import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

from xgboost import XGBClassifier


# -----------------------------------
# 0. 경로 설정
# -----------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "UCI_Credit_Card.csv"
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "xgb_default_model.pkl"
META_PATH = MODEL_DIR / "model_meta.json"

# utils import를 위한 path 보정
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


# -----------------------------------
# 1. 데이터 로드
# -----------------------------------
df = pd.read_csv(DATA_PATH)

print(f"[INFO] Loaded data shape: {df.shape}")
print(f"[INFO] Columns: {df.columns.tolist()}")


# -----------------------------------
# 2. 타깃 컬럼 정리
# -----------------------------------
if "default payment next month" in df.columns:
    df = df.rename(columns={"default payment next month": "default"})
elif "default.payment.next.month" in df.columns:
    df = df.rename(columns={"default.payment.next.month": "default"})
elif "default_flag" in df.columns:
    df = df.rename(columns={"default_flag": "default"})
elif "default" not in df.columns:
    raise ValueError(
        "타깃 컬럼이 없습니다. "
        "'default payment next month' 또는 "
        "'default.payment.next.month' 또는 "
        "'default' 또는 'default_flag' 컬럼이 필요합니다."
    )

print("[INFO] Target column: default")


# -----------------------------------
# 3. X / y 분리
# -----------------------------------
drop_cols = ["default"]
if "ID" in df.columns:
    drop_cols.append("ID")
if "customer_id" in df.columns:
    drop_cols.append("customer_id")

y = df["default"]
X = df.drop(columns=drop_cols)

print(f"[INFO] X shape: {X.shape}")
print(f"[INFO] y distribution:\n{y.value_counts(dropna=False)}")


# -----------------------------------
# 4. categorical column 정의
# -----------------------------------
cat_cols = [
    "SEX", "EDUCATION", "MARRIAGE",
    "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"
]


# -----------------------------------
# 5. Train / Test Split
# -----------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"[INFO] X_train shape: {X_train.shape}")
print(f"[INFO] X_test shape: {X_test.shape}")


# -----------------------------------
# 6. Feature Engineering
#    - credit_utilization
#    - payment_ratio
#    - late_payment_count
# -----------------------------------
X_train_fe = X_train.copy()
X_test_fe = X_test.copy()

# 1) credit_utilization = 최근 청구금액 / 한도
X_train_fe["credit_utilization"] = (
    X_train_fe["BILL_AMT1"] / (X_train_fe["LIMIT_BAL"] + 1e-6)
)
X_test_fe["credit_utilization"] = (
    X_test_fe["BILL_AMT1"] / (X_test_fe["LIMIT_BAL"] + 1e-6)
)

# 2) payment_ratio = 최근 결제금액 / 최근 청구금액
#    음수/0 대비를 위해 abs + epsilon 사용
X_train_fe["payment_ratio"] = (
    X_train_fe["PAY_AMT1"] / (np.abs(X_train_fe["BILL_AMT1"]) + 1e-6)
)
X_test_fe["payment_ratio"] = (
    X_test_fe["PAY_AMT1"] / (np.abs(X_test_fe["BILL_AMT1"]) + 1e-6)
)

# 3) late_payment_count = 연체 발생 횟수
pay_cols = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]

X_train_fe["late_payment_count"] = (X_train_fe[pay_cols] > 0).sum(axis=1)
X_test_fe["late_payment_count"] = (X_test_fe[pay_cols] > 0).sum(axis=1)

print("[INFO] Feature engineering applied")


# -----------------------------------
# 7. num_cols 정의
# -----------------------------------
num_cols = [col for col in X_train_fe.columns if col not in cat_cols]

print(f"[INFO] cat_cols: {cat_cols}")
print(f"[INFO] num_cols count before log: {len(num_cols)}")
print(f"[INFO] num_cols[11:]: {num_cols[11:]}")


# -----------------------------------
# 8. Long-tail 완화용 log feature 추가
#    - num_cols[11:] 기준
#    - AGE 제외
#    - 음수값 있는 컬럼 제외 (NaN 방지)
# -----------------------------------
long_tail_cols = [col for col in num_cols[11:] if col != "AGE"]

log_safe_cols = []
excluded_cols = []

for col in long_tail_cols:
    if X_train_fe[col].min() > -1 and X_test_fe[col].min() > -1:
        log_safe_cols.append(col)
    else:
        excluded_cols.append(col)

for col in log_safe_cols:
    X_train_fe[col + "_log"] = np.log1p(X_train_fe[col])
    X_test_fe[col + "_log"] = np.log1p(X_test_fe[col])

print("[INFO] long_tail_cols:", long_tail_cols)
print("[INFO] log_safe_cols:", log_safe_cols)
print("[INFO] excluded_cols (negative values exist):", excluded_cols)


# -----------------------------------
# 9. num_cols 재정의
# -----------------------------------
num_cols = [col for col in X_train_fe.columns if col not in cat_cols]

print(f"[INFO] num_cols count after log: {len(num_cols)}")


# -----------------------------------
# 10. scale_pos_weight 계산
# -----------------------------------
neg_count = (y_train == 0).sum()
pos_count = (y_train == 1).sum()
scale_pos_weight = neg_count / max(pos_count, 1)

print(f"[INFO] scale_pos_weight: {scale_pos_weight:.4f}")


# -----------------------------------
# 11. 전처리 + XGBoost Pipeline
# -----------------------------------
preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
    ]
)

model = Pipeline(steps=[
    ("preprocess", preprocessor),
    ("classifier", XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight
    ))
])


# -----------------------------------
# 12. 학습
# -----------------------------------
model.fit(X_train_fe, y_train)


# -----------------------------------
# 13. 예측
# -----------------------------------
threshold = 0.42

y_prob = model.predict_proba(X_test_fe)[:, 1]
y_pred = (y_prob >= threshold).astype(int)


# -----------------------------------
# 14. 평가
# -----------------------------------
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
auc = roc_auc_score(y_test, y_prob)
cm = confusion_matrix(y_test, y_pred)

print("\n[RESULT] Evaluation")
print(f"Threshold  : {threshold}")
print(f"Accuracy   : {acc:.4f}")
print(f"Precision  : {prec:.4f}")
print(f"Recall     : {rec:.4f}")
print(f"F1 Score   : {f1:.4f}")
print(f"ROC-AUC    : {auc:.4f}")
print("\nConfusion Matrix")
print(cm)


# -----------------------------------
# 15. 모델 저장
# -----------------------------------
MODEL_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(model, MODEL_PATH)

print(f"\n[INFO] Model saved to: {MODEL_PATH}")


# -----------------------------------
# 16. 메타 정보 저장
# -----------------------------------
meta = {
    "model_name": "XGBoost",
    "model_version": "v1.0",
    "threshold": threshold,
    "target_name": "default",
    "description": "XGBoost credit default prediction model with feature engineering and log features",
    "train_data_path": str(DATA_PATH),
    "cat_cols": cat_cols,
    "num_cols": num_cols,
    "feature_engineering": [
        "credit_utilization",
        "payment_ratio",
        "late_payment_count"
    ],
    "long_tail_cols": long_tail_cols,
    "log_safe_cols": log_safe_cols,
    "excluded_cols": excluded_cols,
    "metrics": {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(auc), 4)
    }
}

with open(META_PATH, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print(f"[INFO] Meta saved to: {META_PATH}")
