
'''
파이선으로 스트림릿 대시보드 프로그램 작성해줘

1. 전체 레이아웃
   - 화면 윗부분을 Header 영역으로 하고 "Walmart Sales Analysis"라고 제목을 표시
   - 화면 아랫부분은
     : 화면 왼쪽을 사이드바로 메뉴이동 라디오버튼 배치 : '개요', '분석내용', '결과'
     

2. '개요' 페이지 구성

아래 내용을 표시

# Wallmart 데이터 분석

## 프로젝트 개요
[Kaggle의 Wallmart 데이터 셋](https://www.kaggle.com/datasets/harshalpanchal/walmart-black-friday-sales) 분석 프로젝트입니다. 
데이터 전처리, 탐색적 데이터 분석(EDA)을 통한 데이터의 분포를 확인하고, VIP 고객 도출 및 지역별 구매 고객 특징을 파악하여 마케팅 전략을 도출합니다.
이 프로젝트의 목표는 주어진 데이터의 분포를 분석하여 주요 특징을 도출하고, 이를 바탕으로 마케팅 전략을 제시하는 것입니다.

2. '분석내용' 페이지 구성
 - 탭으로 구성 - "1. 데이터 살펴보기", "2. 고객 중심 분석", "3. 제품 카테고리 중심 분석"
 - walmart_sales_analysis.ipynb 파일에서 각 "1. 데이터 살펴보기", "2. 고객 중심 분석", "3. 제품 카테고리 중심 분석"에 맞게 텝 데이타를 구성
 
'''

# app.py
# 실행: streamlit run app.py
# 로컬 파일 사용:
# - ./Walmart_Salse_Analysis.ipynb
# - ./data/walmart_data.csv

from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="Walmart Sales Analysis",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# ✅ Styling (메트릭 강조 + 상단 잘림 방지)
# =========================
st.markdown(
    """
<style>
/* 상단 잘림 방지 */
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* ✅ 전체 metric 강조 스타일 */
div[data-testid="stMetric"]{
  background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(59,130,246,0.14));
  border: 1px solid rgba(124,58,237,0.35);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
div[data-testid="stMetric"]:hover{
  transform: translateY(-3px);
  box-shadow: 0 14px 34px rgba(0,0,0,0.16);
}
div[data-testid="stMetric"] label{
  font-weight: 700;
  opacity: 0.9;
}
div[data-testid="stMetric"] div{
  font-weight: 900;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# Local Paths
# =========================
NB_PATH = Path("./Walmart_Salse_Analysis.ipynb")
CSV_PATH = Path("./data/walmart_data.csv")

# =========================
# Notebook Comment (고정)
# =========================
CUSTOM_NOTEBOOK_COMMENT = """
1인당 평균 93개 제품을 사지만 중간값은 54개로, 사업등의 이유로 대량구매를 하는 고객들 때문에 평균이 상승함 <br>
26-35세가 가장 구매력이 높게 나타남. 그 뒤로 36-45, 18-25 순 (구매빈도 및 구매금액이 비슷한 분포를 가짐)

18~45세 연령대가 안정적인 고객군으로 판단됩니다.<br>
10대의 경우 보호자 동반 방문으로 직접 방문하는 고객층의 패턴을 확인할 필요가 있습니다.<br>
50대 이상의 경우 구매력에 비해 방문횟수가 적어, 마케팅 강화의 여지를 확인할 필요가 있습니다.<br>
""".strip()

# =========================
# Product Category Comment (고정)
# =========================
CUSTOM_PRODUCT_CATEGORY_COMMENT = """
- 제품 종류는 **3631개** - 카테고리별 **2개**에서 많게는 **1047개** 임  
- 카테고리의 제품이 많을 수록 카테고리 구매액도 증가 (**상관도 0.724**)
""".strip()

# =========================
# Helpers
# =========================
@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "Purchase" in df.columns:
        df["Purchase"] = pd.to_numeric(df["Purchase"], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_notebook_cells(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        nb = json.load(f)
    return nb.get("cells", [])


def kpi_cards(df: pd.DataFrame):
    transactions = len(df)
    unique_users = df["User_ID"].nunique() if "User_ID" in df.columns else 0
    unique_products = df["Product_ID"].nunique() if "Product_ID" in df.columns else 0
    unique_categories = df["Product_Category"].nunique() if "Product_Category" in df.columns else 0
    total_purchase = df["Purchase"].sum() if "Purchase" in df.columns else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Transactions", f"{transactions:,}")
    with c2:
        st.metric("Unique Users", f"{unique_users:,}")
    with c3:
        st.metric("Unique Products", f"{unique_products:,}")
    with c4:
        st.metric("Product Categories", f"{unique_categories:,}")
    with c5:
        st.metric("Total Purchase", f"{total_purchase:,.0f}")


def get_age_order(series: pd.Series) -> list[str] | None:
    known = ["0-17", "18-25", "26-35", "36-45", "46-50", "51-55", "55+"]
    uniq = [str(x) for x in series.dropna().unique().tolist()]
    if set(uniq).issubset(set(known)):
        return [x for x in known if x in set(uniq)]
    return None


# =========================
# Header
# =========================
st.markdown(
    """
<div style="
    margin-top: 0.6rem;
    margin-bottom: 1.0rem;
    padding:18px 22px;
    border-radius:18px;
    background:linear-gradient(135deg, rgba(124,58,237,0.22), rgba(59,130,246,0.16));
    border:1px solid rgba(255,255,255,0.15);
">
  <div style="font-size:30px;font-weight:900;">Walmart Sales Analysis</div>
</div>
""",
    unsafe_allow_html=True,
)
st.markdown("---")

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.header("🧭 메뉴")
    page = st.radio("이동", ["개요", "분석내용", "결과"], index=0)

    st.divider()
    show_nb_notes = st.toggle("노트북 코멘트(요약) 표시", value=True)

# =========================
# Load Data
# =========================
if not CSV_PATH.exists():
    st.error(f"CSV 파일을 찾을 수 없습니다: {CSV_PATH}")
    st.stop()

df = load_csv(CSV_PATH)
cells = load_notebook_cells(NB_PATH)

# =========================
# Tables
# =========================
@st.cache_data(show_spinner=False)
def build_user_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    user_df = df.drop_duplicates(subset=["User_ID"], keep="first").copy()
    drop_cols = [c for c in ["Product_ID", "Product_Category", "Purchase"] if c in user_df.columns]
    if drop_cols:
        user_df = user_df.drop(columns=drop_cols)

    user_purchase_df = (
        df.groupby("User_ID")["Purchase"]
        .aggregate(["count", "sum"])
        .rename(columns={"count": "Product_Kinds", "sum": "Purchase_Amount"})
        .reset_index()
    )

    user_stat_df = user_df.merge(user_purchase_df, on="User_ID", how="left").set_index("User_ID").sort_index()
    return user_df, user_purchase_df, user_stat_df


@st.cache_data(show_spinner=False)
def build_age_agg(user_stat_df: pd.DataFrame) -> pd.DataFrame:
    if "Age" not in user_stat_df.columns:
        return pd.DataFrame()

    age_agg = user_stat_df.groupby("Age").aggregate(
        Product_Kinds_mean=("Product_Kinds", "mean"),
        Purchase_Amount_sum=("Purchase_Amount", "sum"),
        Purchase_Amount_mean=("Purchase_Amount", "mean"),
    )
    age_agg["Product_Kinds_mean"] = age_agg["Product_Kinds_mean"].round(0)
    age_agg["Purchase_Amount_mean"] = age_agg["Purchase_Amount_mean"].round(0)
    return age_agg.reset_index()


@st.cache_data(show_spinner=False)
def build_product_cat_table(df: pd.DataFrame) -> pd.DataFrame:
    if not all(c in df.columns for c in ["Product_Category", "Product_ID", "Purchase"]):
        return pd.DataFrame()

    tmp = df.groupby("Product_Category").agg(
        Product_Kinds=("Product_ID", pd.Series.nunique),
        Total_Purchase=("Purchase", "sum"),
        Avg_Purchase=("Purchase", "mean"),
        Transactions=("Purchase", "size"),
    )
    tmp["Avg_Purchase_per_Product"] = tmp["Total_Purchase"] / tmp["Product_Kinds"].replace({0: np.nan})
    return tmp.reset_index().sort_values("Total_Purchase", ascending=False)


@st.cache_data(show_spinner=False)
def build_stat_cat_age(df: pd.DataFrame, categories: list[int]) -> pd.DataFrame:
    if "Age" not in df.columns or "Product_Category" not in df.columns:
        return pd.DataFrame()

    stat = (df.groupby("Age").size() / len(df)).to_frame(name="All Categories")

    for cat in categories:
        df_cat = df[df["Product_Category"] == cat]
        col = f"Category {cat}"
        if len(df_cat) == 0:
            stat[col] = np.nan
        else:
            stat[col] = (df_cat.groupby("Age").size() / len(df_cat)).reindex(stat.index)

    stat.index = stat.index.astype(str)
    return stat


user_df, user_purchase_df, user_stat_df = build_user_tables(df)
age_agg = build_age_agg(user_stat_df)
product_cat_df = build_product_cat_table(df)

# =========================
# Pages
# =========================
if page == "개요":
    st.markdown(
        """
# Wallmart 데이터 분석

## 프로젝트 개요
[Kaggle의 Wallmart 데이터 셋](https://www.kaggle.com/datasets/harshalpanchal/walmart-black-friday-sales) 분석 프로젝트입니다. 
데이터 전처리, 탐색적 데이터 분석(EDA)을 통한 데이터의 분포를 확인하고, VIP 고객 도출 및 지역별 구매 고객 특징을 파악하여 마케팅 전략을 도출합니다.
이 프로젝트의 목표는 주어진 데이터의 분포를 분석하여 주요 특징을 도출하고, 이를 바탕으로 마케팅 전략을 제시하는 것입니다.
"""
    )

    kpi_cards(df)

    st.subheader("데이터 미리보기")
    st.dataframe(df.head(20), use_container_width=True, hide_index=True)

elif page == "분석내용":
    tabs = st.tabs(["1. 데이터 살펴보기", "2. 고객 중심 분석", "3. 제품 카테고리 중심 분석"])

    # 1) 데이터 살펴보기
    with tabs[0]:
        kpi_cards(df)

        st.subheader("Purchase 분포")
        hist = (
            alt.Chart(df.dropna(subset=["Purchase"]))
            .mark_bar()
            .encode(
                x=alt.X("Purchase:Q", bin=alt.Bin(maxbins=40), title="Purchase (binned)"),
                y=alt.Y("count():Q", title="Count"),
                tooltip=[alt.Tooltip("count():Q", title="Count")],
            )
            .properties(height=350)
        )
        st.altair_chart(hist, use_container_width=True)

    # 2) 고객 중심 분석
    with tabs[1]:
        st.subheader("2. 고객 중심 분석 (Notebook 반영)")

        if show_nb_notes:
            with st.expander("📓 노트북 코멘트(요약)", expanded=True):
                st.markdown(CUSTOM_NOTEBOOK_COMMENT, unsafe_allow_html=True)

        st.markdown("### (1) 고객 통계 테이블(user_stat_df)")
        with st.expander("user_stat_df 미리보기", expanded=False):
            st.dataframe(user_stat_df.head(25), use_container_width=True)

        st.markdown("### (2) 1인당 구매품목 / 구매금액 분포 (boxplot)")

        dist_df = user_stat_df.reset_index()[["User_ID", "Product_Kinds", "Purchase_Amount"]].dropna()
        if len(dist_df) > 150_000:
            dist_df = dist_df.sample(150_000, random_state=7)

        col_left, col_right = st.columns(2, gap="large")

        with col_left:
            st.markdown("#### 1인당 구매품목 분포")
            box_kinds = (
                alt.Chart(dist_df)
                .mark_boxplot()
                .encode(
                    y=alt.Y("Product_Kinds:Q", title="Product Kinds per User"),
                    tooltip=[alt.Tooltip("Product_Kinds:Q")],
                )
                .properties(height=260)
            )
            st.altair_chart(box_kinds, use_container_width=True)

        with col_right:
            st.markdown("#### 1인당 구매금액 분포")
            box_amt = (
                alt.Chart(dist_df)
                .mark_boxplot()
                .encode(
                    y=alt.Y("Purchase_Amount:Q", title="Purchase Amount per User"),
                    tooltip=[alt.Tooltip("Purchase_Amount:Q", format=",.0f")],
                )
                .properties(height=260)
            )
            st.altair_chart(box_amt, use_container_width=True)

        st.markdown("### (3) 연령(Age) 별 구매품목(평균) / 구매금액(평균) / 구매금액(합)")

        if age_agg.empty:
            st.info("Age 컬럼이 없어 연령대 분석을 표시할 수 없습니다.")
        else:
            c1, c2, c3 = st.columns(3, gap="large")

            with c1:
                st.markdown("#### 구매품목(평균)")
                df_kinds = age_agg[["Age", "Product_Kinds_mean"]].copy()
                st.dataframe(df_kinds, use_container_width=True, hide_index=True)

                ch1 = (
                    alt.Chart(df_kinds)
                    .mark_bar()
                    .encode(
                        x=alt.X("Age:N", title="Age"),
                        y=alt.Y("Product_Kinds_mean:Q", title="Avg Product Kinds"),
                        tooltip=["Age:N", alt.Tooltip("Product_Kinds_mean:Q")],
                    )
                    .properties(height=240)
                )
                st.altair_chart(ch1, use_container_width=True)

            with c2:
                st.markdown("#### 구매금액(평균)")
                df_avg = age_agg[["Age", "Purchase_Amount_mean"]].copy()
                st.dataframe(df_avg, use_container_width=True, hide_index=True)

                ch2 = (
                    alt.Chart(df_avg)
                    .mark_bar()
                    .encode(
                        x=alt.X("Age:N", title="Age"),
                        y=alt.Y("Purchase_Amount_mean:Q", title="Avg Purchase Amount"),
                        tooltip=["Age:N", alt.Tooltip("Purchase_Amount_mean:Q", format=",.0f")],
                    )
                    .properties(height=240)
                )
                st.altair_chart(ch2, use_container_width=True)

            with c3:
                st.markdown("#### 구매금액(합)")
                df_sum = age_agg[["Age", "Purchase_Amount_sum"]].copy()
                st.dataframe(df_sum, use_container_width=True, hide_index=True)

                ch3 = (
                    alt.Chart(df_sum)
                    .mark_bar()
                    .encode(
                        x=alt.X("Age:N", title="Age"),
                        y=alt.Y("Purchase_Amount_sum:Q", title="Total Purchase Amount"),
                        tooltip=["Age:N", alt.Tooltip("Purchase_Amount_sum:Q", format=",.0f")],
                    )
                    .properties(height=240)
                )
                st.altair_chart(ch3, use_container_width=True)

    # 3) 제품 카테고리 중심 분석
    with tabs[2]:
        st.subheader("3. 제품 카테고리 중심 분석 (Notebook 반영)")

        if show_nb_notes:
            with st.expander("📓 노트북 코멘트(요약)", expanded=True):
                st.markdown(CUSTOM_PRODUCT_CATEGORY_COMMENT)

        if product_cat_df.empty:
            st.warning("Product_Category / Product_ID / Purchase 컬럼이 없어 제품 카테고리 분석을 표시할 수 없습니다.")
        else:
            # ✅ 추가: 카테고리 수(20) 포함해서 메트릭 4개로 표시
            category_cnt = df["Product_Category"].nunique()
            product_cnt = df["Product_ID"].nunique() if "Product_ID" in df.columns else 0
            min_kinds = int(product_cat_df["Product_Kinds"].min())
            max_kinds = int(product_cat_df["Product_Kinds"].max())
            corr_val = float(product_cat_df[["Product_Kinds", "Total_Purchase"]].corr(numeric_only=True).iloc[0, 1])

            m1, m2, m3, m4 = st.columns(4, gap="large")
            with m1:
                st.metric("카테고리 수", f"{category_cnt:,}")
            with m2:
                st.metric("제품 종류 수(Product_ID unique)", f"{product_cnt:,}")
            with m3:
                st.metric("카테고리별 제품수 범위", f"{min_kinds:,} ~ {max_kinds:,}")
            with m4:
                st.metric("제품수 ↔ 총구매액 상관", f"{corr_val:.3f}")

            st.markdown("### (1) 카테고리별 제품수 / 구매액(합) / 제품당 평균구매액")
            view = product_cat_df[
                ["Product_Category", "Product_Kinds", "Total_Purchase", "Avg_Purchase_per_Product"]
            ].copy()
            view["Total_Purchase"] = view["Total_Purchase"].round(0)
            view["Avg_Purchase_per_Product"] = view["Avg_Purchase_per_Product"].round(0)
            st.dataframe(view, use_container_width=True, hide_index=True)

            # 3개 barplot 1화면 3분할
            b1, b2, b3 = st.columns(3, gap="large")

            with b1:
                st.markdown("#### 카테고리별 제품수")
                chart_kinds = (
                    alt.Chart(product_cat_df)
                    .mark_bar()
                    .encode(
                        x=alt.X("Product_Kinds:Q", title="Product Kinds"),
                        y=alt.Y("Product_Category:N", sort="-x", title="Category"),
                        tooltip=["Product_Category:N", alt.Tooltip("Product_Kinds:Q", format=",.0f")],
                    )
                    .properties(height=480)
                )
                st.altair_chart(chart_kinds, use_container_width=True)

            with b2:
                st.markdown("#### 카테고리별 구매액(합)")
                chart_purchase = (
                    alt.Chart(product_cat_df)
                    .mark_bar()
                    .encode(
                        x=alt.X("Total_Purchase:Q", title="Total Purchase"),
                        y=alt.Y("Product_Category:N", sort="-x", title="Category"),
                        tooltip=["Product_Category:N", alt.Tooltip("Total_Purchase:Q", format=",.0f")],
                    )
                    .properties(height=480)
                )
                st.altair_chart(chart_purchase, use_container_width=True)

            with b3:
                st.markdown("#### 제품당 평균구매액(구매액/제품수)")
                chart_avg_per_product = (
                    alt.Chart(product_cat_df.sort_values("Avg_Purchase_per_Product", ascending=False))
                    .mark_bar()
                    .encode(
                        x=alt.X("Avg_Purchase_per_Product:Q", title="Avg Purchase / Product"),
                        y=alt.Y("Product_Category:N", sort="-x", title="Category"),
                        tooltip=[
                            "Product_Category:N",
                            alt.Tooltip("Avg_Purchase_per_Product:Q", format=",.0f"),
                            alt.Tooltip("Product_Kinds:Q", format=",.0f"),
                            alt.Tooltip("Total_Purchase:Q", format=",.0f"),
                        ],
                    )
                    .properties(height=480)
                )
                st.altair_chart(chart_avg_per_product, use_container_width=True)

            st.markdown("---")
            st.markdown("### (2) 연령(Age) 기준 카테고리 분포 분석 (Notebook: stat_cat_age)")

            high_categories = [10, 12, 17, 18]
            stat_cat_age = build_stat_cat_age(df, high_categories)

            if stat_cat_age.empty:
                st.info("Age/Product_Category 컬럼이 없어 stat_cat_age 분석을 표시할 수 없습니다.")
            else:
                desc = stat_cat_age.describe().loc[["mean", "std"]].T.reset_index().rename(columns={"index": "Metric"})
                desc = desc.rename(columns={"mean": "Mean", "std": "Std"})
                desc["Mean"] = desc["Mean"].astype(float).round(4)
                desc["Std"] = desc["Std"].astype(float).round(4)

                cA, cB = st.columns([1, 1], gap="large")
                with cA:
                    st.markdown("#### stat_cat_age.describe() - 평균 / 표준편차")
                    st.dataframe(desc, use_container_width=True, hide_index=True)

                with cB:
                    st.markdown("#### stat_cat_age (비율 테이블)")
                    st.dataframe(stat_cat_age.reset_index().rename(columns={"index": "Age"}), use_container_width=True, hide_index=True)

                # 제목 변경 반영
                st.markdown("#### 나이별 구매액 분포가 상이한 제품 카테고리")

                age_order = get_age_order(df["Age"])
                sort_age = age_order if age_order else None

                row1 = st.columns(2, gap="large")
                row2 = st.columns(2, gap="large")
                grid_rows = [row1, row2]

                stat_reset = stat_cat_age.reset_index().rename(columns={"index": "Age"})

                for i, cat in enumerate(high_categories):
                    r = i // 2
                    c = i % 2

                    cat_col = f"Category {cat}"
                    if cat_col not in stat_reset.columns:
                        continue

                    plot_df = stat_reset[["Age", "All Categories", cat_col]].melt(
                        id_vars=["Age"], var_name="Series", value_name="Ratio"
                    )

                    ch = (
                        alt.Chart(plot_df)
                        .mark_line(point=True)
                        .encode(
                            x=alt.X("Age:N", sort=sort_age, title="Age"),
                            y=alt.Y("Ratio:Q", title="Ratio", axis=alt.Axis(format=".0%")),
                            color=alt.Color("Series:N", title=""),
                            tooltip=[
                                alt.Tooltip("Age:N"),
                                alt.Tooltip("Series:N"),
                                alt.Tooltip("Ratio:Q", format=".2%"),
                            ],
                        )
                        .properties(height=260, title=f"Category {cat}")
                    )

                    with grid_rows[r][c]:
                        st.altair_chart(ch, use_container_width=True)

else:
    st.subheader("분석 결과 요약")
    kpi_cards(df)

    st.markdown("### 마케팅 전략 제안")
    st.write("- VIP 고객 타겟 프로모션 (상위 고객군 쿠폰/멤버십/번들 제안)")
    st.write("- 연령대(특히 26~35) 중심 캠페인 / 크로스셀 추천 강화")
    st.write("- 카테고리별 제품수·매출 기반 재고/프로모션 최적화")


