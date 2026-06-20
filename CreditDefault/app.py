import streamlit as st
import pandas as pd
import sqlite3

from pathlib import Path

from utils.features import add_features
from utils.predict import (
    predict_default,
    get_top_features,
    get_grouped_feature_importance,
    THRESHOLD,
    model_meta
)


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "credit_default.db"


# -----------------------------------
# DB Helper
# -----------------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)


def search_customers(
    sex,
    education,
    marriage,
    age_min,
    age_max,
    late_min,
    late_max,
    pay0_values,
    limit_min,
    limit_max,
    bill_avg_min,
    bill_avg_max
):
    conn = get_connection()

    base_query = """
    SELECT
        *,
        (
            CASE WHEN PAY_0 > 0 THEN 1 ELSE 0 END +
            CASE WHEN PAY_2 > 0 THEN 1 ELSE 0 END +
            CASE WHEN PAY_3 > 0 THEN 1 ELSE 0 END +
            CASE WHEN PAY_4 > 0 THEN 1 ELSE 0 END +
            CASE WHEN PAY_5 > 0 THEN 1 ELSE 0 END +
            CASE WHEN PAY_6 > 0 THEN 1 ELSE 0 END
        ) AS late_payment_count,
        (BILL_AMT1 + BILL_AMT2 + BILL_AMT3) / 3.0 AS recent_3m_bill_avg
    FROM customer_credit_data
    WHERE 1=1
    """

    params = []

    if sex:
        placeholders = ",".join(["?"] * len(sex))
        base_query += f" AND SEX IN ({placeholders})"
        params.extend(sex)

    if education:
        placeholders = ",".join(["?"] * len(education))
        base_query += f" AND EDUCATION IN ({placeholders})"
        params.extend(education)

    if marriage:
        placeholders = ",".join(["?"] * len(marriage))
        base_query += f" AND MARRIAGE IN ({placeholders})"
        params.extend(marriage)

    base_query += " AND AGE BETWEEN ? AND ?"
    params.extend([age_min, age_max])

    base_query += " AND LIMIT_BAL BETWEEN ? AND ?"
    params.extend([limit_min, limit_max])

    if pay0_values:
        placeholders = ",".join(["?"] * len(pay0_values))
        base_query += f" AND PAY_0 IN ({placeholders})"
        params.extend(pay0_values)

    # late_payment_count 조건
    base_query += """
    AND (
        (CASE WHEN PAY_0 > 0 THEN 1 ELSE 0 END +
         CASE WHEN PAY_2 > 0 THEN 1 ELSE 0 END +
         CASE WHEN PAY_3 > 0 THEN 1 ELSE 0 END +
         CASE WHEN PAY_4 > 0 THEN 1 ELSE 0 END +
         CASE WHEN PAY_5 > 0 THEN 1 ELSE 0 END +
         CASE WHEN PAY_6 > 0 THEN 1 ELSE 0 END)
    ) BETWEEN ? AND ?
    """
    params.extend([late_min, late_max])

    # 최근 3개월 bill 평균 조건
    base_query += " AND ((BILL_AMT1 + BILL_AMT2 + BILL_AMT3) / 3.0) BETWEEN ? AND ?"
    params.extend([bill_avg_min, bill_avg_max])

    df = pd.read_sql_query(base_query, conn, params=params)
    conn.close()

    return df


def get_customer_by_id(customer_id: int) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM customer_credit_data WHERE customer_id = ?",
        conn,
        params=[customer_id]
    )
    conn.close()
    return df


def save_prediction_history(
    customer_id: int,
    default_probability: float,
    predicted_label: int,
    top_features: list[str]
):
    conn = get_connection()
    cur = conn.cursor()

    top1 = top_features[0] if len(top_features) > 0 else None
    top2 = top_features[1] if len(top_features) > 1 else None
    top3 = top_features[2] if len(top_features) > 2 else None

    cur.execute("""
        INSERT INTO default_prediction (
            customer_id,
            model_name,
            model_version,
            threshold,
            default_probability,
            predicted_label,
            top_feature_1,
            top_feature_2,
            top_feature_3,
            prediction_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        customer_id,
        model_meta.get("model_name", "XGBoost"),
        model_meta.get("model_version", "v1.0"),
        THRESHOLD,
        default_probability,
        predicted_label,
        top1,
        top2,
        top3
    ))

    conn.commit()
    conn.close()


def load_prediction_history(customer_id: int) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            prediction_id,
            customer_id,
            model_name,
            model_version,
            threshold,
            default_probability,
            predicted_label,
            top_feature_1,
            top_feature_2,
            top_feature_3,
            prediction_time
        FROM default_prediction
        WHERE customer_id = ?
        ORDER BY prediction_time DESC
    """, conn, params=[customer_id])
    conn.close()
    return df


# -----------------------------------
# Streamlit UI
# -----------------------------------
st.set_page_config(page_title="Credit Default Prediction", layout="wide")

st.title("Credit Default Prediction")
st.caption(f"Model: {model_meta.get('model_name', 'XGBoost')} / Threshold: {THRESHOLD}")


# 검색 조건
st.subheader("1. 대상 사용자 검색 및 선택")

col1, col2, col3, col4 = st.columns(4)

with col1:
    sex = st.multiselect("SEX", options=[1, 2], default=[1, 2])
with col2:
    education = st.multiselect("EDUCATION", options=[1, 2, 3, 4], default=[1, 2, 3, 4])
with col3:
    marriage = st.multiselect("MARRIAGE", options=[1, 2, 3], default=[1, 2, 3])
with col4:
    pay0_values = st.multiselect(
        "PAY_0",
        options=[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8],
        default=[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    )

col5, col6, col7, col8 = st.columns(4)

with col5:
    age_min, age_max = st.slider("AGE", min_value=20, max_value=80, value=(20, 80))
with col6:
    late_min, late_max = st.slider("연체회수", min_value=0, max_value=6, value=(0, 6))
with col7:
    limit_min, limit_max = st.slider("LIMIT_BAL", min_value=0, max_value=1000000, value=(0, 1000000))
with col8:
    bill_avg_min, bill_avg_max = st.slider(
        "최근 3개월 BILL_AMT 평균",
        min_value=-200000,
        max_value=1000000,
        value=(-200000, 1000000)
    )

if st.button("검색 실행"):
    result_df = search_customers(
        sex=sex,
        education=education,
        marriage=marriage,
        age_min=age_min,
        age_max=age_max,
        late_min=late_min,
        late_max=late_max,
        pay0_values=pay0_values,
        limit_min=limit_min,
        limit_max=limit_max,
        bill_avg_min=bill_avg_min,
        bill_avg_max=bill_avg_max
    )

    st.session_state["search_result_df"] = result_df

if "search_result_df" in st.session_state:
    result_df = st.session_state["search_result_df"]

    st.write(f"검색 결과: {len(result_df)}건")

    display_cols = [
        col for col in [
            "customer_id", "SEX", "EDUCATION", "MARRIAGE", "AGE",
            "LIMIT_BAL", "PAY_0", "late_payment_count", "recent_3m_bill_avg"
        ] if col in result_df.columns
    ]

    st.dataframe(result_df[display_cols], use_container_width=True)

    if not result_df.empty:
        selected_customer_id = st.selectbox(
            "고객 1명 선택",
            options=result_df["customer_id"].tolist()
        )

        st.subheader("2. 예측 결과")

        customer_df = get_customer_by_id(int(selected_customer_id))

        if not customer_df.empty:
            customer_display = add_features(customer_df.copy())

            with st.expander("기반 데이터 보기", expanded=True):
                st.dataframe(customer_display, use_container_width=True)

            if st.button("예측 실행"):
                default_probability, predicted_label = predict_default(customer_df.copy(), threshold=THRESHOLD)
                top_features = get_top_features(3)

                save_prediction_history(
                    customer_id=int(selected_customer_id),
                    default_probability=default_probability,
                    predicted_label=predicted_label,
                    top_features=top_features
                )

                metric_col1, metric_col2, metric_col3 = st.columns(3)

                with metric_col1:
                    st.metric("부도 확률", f"{default_probability:.4f}")

                with metric_col2:
                    label_text = "부도 위험" if predicted_label == 1 else "정상"
                    st.metric("예측 결과", label_text)

                with metric_col3:
                    st.metric("Threshold", f"{THRESHOLD:.2f}")

                st.markdown("### 설명")
                if predicted_label == 1:
                    st.write("선택 고객은 threshold 기준을 초과하여 **부도 위험**으로 분류되었습니다.")
                else:
                    st.write("선택 고객은 threshold 기준 미만으로 **정상**으로 분류되었습니다.")

                st.markdown("### 주요 영향 변수 Top 3")
                for i, feat in enumerate(top_features, start=1):
                    st.write(f"{i}. {feat}")

                st.markdown("### 전체 중요 변수")
                fi_df = get_grouped_feature_importance(15)
                st.dataframe(fi_df, use_container_width=True)

            st.markdown("### 예측 이력")
            history_df = load_prediction_history(int(selected_customer_id))
            st.dataframe(history_df, use_container_width=True)