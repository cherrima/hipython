import json
import joblib
import pandas as pd

from pathlib import Path

from utils.features import make_model_input


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "xgb_default_model.pkl"
META_PATH = BASE_DIR / "model" / "model_meta.json"

model = joblib.load(MODEL_PATH)

with open(META_PATH, "r", encoding="utf-8") as f:
    model_meta = json.load(f)

THRESHOLD = model_meta.get("threshold", 0.42)
CAT_COLS = model_meta.get(
    "cat_cols",
    ["SEX", "EDUCATION", "MARRIAGE", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
)
LOG_SAFE_COLS = model_meta.get("log_safe_cols", [])


def preprocess_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """
    예측 전처리:
    학습 시점과 동일한 FE + log feature 생성
    """
    return make_model_input(
        df=df,
        cat_cols=CAT_COLS,
        log_safe_cols=LOG_SAFE_COLS
    )


def predict_default(df: pd.DataFrame, threshold: float | None = None) -> tuple[float, int]:
    """
    1건 예측 기준
    return: (default_probability, predicted_label)
    """
    if threshold is None:
        threshold = THRESHOLD

    model_input = preprocess_for_prediction(df)
    prob = model.predict_proba(model_input)[:, 1]
    pred = (prob >= threshold).astype(int)

    return float(prob[0]), int(pred[0])


def get_grouped_feature_importance(top_n: int = 10) -> pd.DataFrame:
    """
    Pipeline 내부 XGBoost의 feature importance를 원래 컬럼 기준으로 집계
    """
    preprocessor = model.named_steps["preprocess"]
    classifier = model.named_steps["classifier"]

    feature_names = preprocessor.get_feature_names_out()
    importances = classifier.feature_importances_

    fi_detail = pd.DataFrame({
        "feature_transformed": feature_names,
        "importance": importances
    })

    def to_original_feature_name(transformed_name: str) -> str:
        if transformed_name.startswith("num__"):
            return transformed_name.replace("num__", "")

        if transformed_name.startswith("cat__"):
            col = transformed_name.replace("cat__", "")
            for c in sorted(CAT_COLS, key=len, reverse=True):
                if col == c or col.startswith(c + "_"):
                    return c
            return col.split("_")[0]

        return transformed_name

    fi_detail["feature_original"] = fi_detail["feature_transformed"].apply(to_original_feature_name)

    fi_grouped = (
        fi_detail
        .groupby("feature_original", as_index=False)["importance"]
        .sum()
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    fi_grouped["importance_pct"] = fi_grouped["importance"] / fi_grouped["importance"].sum() * 100
    fi_grouped["importance"] = fi_grouped["importance"].round(6)
    fi_grouped["importance_pct"] = fi_grouped["importance_pct"].round(2)

    return fi_grouped.head(top_n)


def get_top_features(top_n: int = 3) -> list[str]:
    fi = get_grouped_feature_importance(top_n=top_n)
    return fi["feature_original"].tolist()
