# app.py
# 실행: streamlit run app.py
'''
파이선으로 스트림릿 대시보드 프로그램 작성해줘

기본 구성
 - 페이지 제목 표시, 이미지 한장 넣기
 - 사이드바에 메뉴이동 라디오버튼 : 메인페이지, 분석보고서, 설정 
 - 메인페이지 구성
   : 2개의 컬럼으로 KPI 대시보드 구성
   : 방문자수, 활성사용자수를 메트릭 카드로 구성
 - 분석보고서 구성
   : 탭으로 구성 - 차트, 데이터, 설정
   : 차트 탭 - 간단한 사용자 방문형황 그래프 
   : 데이터 탭 - 데이터 테이블 출력
   : 설정 탭 - 연결시 옵션 체크박스
- 설정 구성
  : 화면 색상
   : 데이터 소스 선택
   : ** 그외 필요한 설정이 있으면 구성해줘
'''

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="✨ Streamlit KPI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Light Styling (예쁘게)
# =========================
st.markdown(
    """
<style>
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

div[data-testid="stMetric"]{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.10);
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# Utils / Data
# =========================
@st.cache_data(show_spinner=False)
def make_dummy_data(n_days: int = 30, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n_days, freq="D")
    base = np.linspace(1200, 1700, n_days)
    noise = rng.normal(0, 120, n_days)
    visitors = np.maximum(200, (base + noise).astype(int))
    active_users = np.maximum(50, (visitors * rng.uniform(0.25, 0.45, n_days)).astype(int))
    return pd.DataFrame({"date": dates, "visitors": visitors, "active_users": active_users})


@st.cache_data(show_spinner=False)
def make_seasonal_data(n_days: int = 30, seed: int = 21) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n_days, freq="D")
    t = np.arange(n_days)
    visitors = (1300 + 250 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 90, n_days)).astype(int)
    visitors = np.maximum(150, visitors)
    active_users = (visitors * (0.32 + 0.06 * np.cos(2 * np.pi * t / 10)) + rng.normal(0, 25, n_days)).astype(int)
    active_users = np.maximum(40, active_users)
    return pd.DataFrame({"date": dates, "visitors": visitors, "active_users": active_users})


def load_data(source: str, n_days: int, seed: int) -> pd.DataFrame:
    if source == "더미(기본)":
        return make_dummy_data(n_days=n_days, seed=seed)
    if source == "더미(시즌성)":
        return make_seasonal_data(n_days=n_days, seed=seed)
    # 확장 포인트: CSV/DB/API 연동
    return make_dummy_data(n_days=n_days, seed=seed)


def inject_accent(accent_hex: str) -> None:
    # 버튼/링크 등 약간의 포인트 컬러
    st.markdown(
        f"""
<style>
/* Streamlit 일부 요소에 포인트 컬러 적용 */
a, a:visited {{ color: {accent_hex}; }}
div.stButton > button {{
    border-radius: 14px;
}}
/* expander/checkbox 라벨 hover 느낌 */
label:hover {{ opacity: 0.92; }}
</style>
""",
        unsafe_allow_html=True,
    )


# =========================
# Session Defaults
# =========================
if "days" not in st.session_state:
    st.session_state.days = 30
if "seed" not in st.session_state:
    st.session_state.seed = 7
if "data_source" not in st.session_state:
    st.session_state.data_source = "더미(기본)"
if "accent" not in st.session_state:
    st.session_state.accent = "#7C3AED"  # 보라 포인트
if "show_help" not in st.session_state:
    st.session_state.show_help = True

inject_accent(st.session_state.accent)

# =========================
# Header (제목 + 이미지)
# =========================
st.title("📊 KPI 대시보드")
st.caption("메인 KPI 요약부터 분석 리포트까지. 설정에서 화면/데이터 소스를 바꿔보세요.")

st.image(
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1600&q=80",
    caption="Dashboard vibes ✨",
    use_container_width=True,
)

st.divider()

# =========================
# Sidebar (메뉴 + 공통 설정 일부)
# =========================
with st.sidebar:
    st.header("🧭 메뉴")
    page = st.radio(
        "이동",
        ["메인페이지", "분석보고서", "설정"],
        index=0,
        label_visibility="collapsed",
    )

    st.divider()

    st.subheader("🎛️ 빠른 설정(공통)")
    st.session_state.days = st.slider("표시 기간(일)", 7, 120, st.session_state.days)
    st.session_state.seed = st.number_input("랜덤 시드(seed)", min_value=0, max_value=9999, value=st.session_state.seed, step=1)

    if st.session_state.show_help:
        st.info("설정 페이지에서 화면 색상/데이터 소스를 바꿀 수 있어요.", icon="💡")

# 데이터 로드
df = load_data(st.session_state.data_source, n_days=st.session_state.days, seed=st.session_state.seed)
df_view = df.copy()

# KPI (최신 하루)
today_row = df_view.iloc[-1]
visitors_today = int(today_row["visitors"])
active_today = int(today_row["active_users"])
if len(df_view) >= 2:
    prev_row = df_view.iloc[-2]
    visitors_delta = visitors_today - int(prev_row["visitors"])
    active_delta = active_today - int(prev_row["active_users"])
else:
    visitors_delta = 0
    active_delta = 0

# =========================
# Pages
# =========================
if page == "메인페이지":
    st.subheader("🏠 메인페이지")
    st.write("2개의 컬럼으로 KPI 메트릭 카드를 구성합니다.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.metric(
            label="방문자수 (Today)",
            value=f"{visitors_today:,}",
            delta=f"{visitors_delta:+,}",
            help="전일 대비 증감(데모 데이터)",
        )
        with st.expander("🔎 방문자수 인사이트", expanded=True):
            st.progress(min(1.0, visitors_today / (df_view["visitors"].max() + 1)))
            st.caption("최대치 대비 오늘 방문자수 비율(예시)")

    with col2:
        st.metric(
            label="활성 사용자수 (Today)",
            value=f"{active_today:,}",
            delta=f"{active_delta:+,}",
            help="전일 대비 증감(데모 데이터)",
        )
        with st.expander("⚡ 활성 사용자 인사이트", expanded=True):
            ratio = active_today / max(1, visitors_today)
            st.write(f"활성/방문 비율: **{ratio:.1%}**")
            st.caption("활성 사용자수 / 방문자수 (예시)")

    st.divider()

    with st.container(border=True):
        st.subheader("🪄 상태 요약")
        if visitors_delta >= 0 and active_delta >= 0:
            st.success("지표가 전일 대비 상승 중입니다!", icon="✅")
        elif visitors_delta < 0 and active_delta < 0:
            st.warning("지표가 전일 대비 하락 중입니다. 원인 분석이 필요해요.", icon="⚠️")
        else:
            st.info("지표가 혼합 상태입니다. 그래프에서 추이를 확인해보세요.", icon="ℹ️")

        st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

elif page == "분석보고서":
    st.subheader("📑 분석보고서")

    tab_chart, tab_data, tab_settings = st.tabs(["📈 차트", "🧾 데이터", "⚙️ 설정"])

    with tab_chart:
        st.write("간단한 사용자 방문 현황 그래프입니다.")

        chart_df = df_view.melt(
            "date", value_vars=["visitors", "active_users"], var_name="metric", value_name="value"
        )
        chart = (
            alt.Chart(chart_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("value:Q", title="Count"),
                color=alt.Color("metric:N", title="Metric"),
                tooltip=[alt.Tooltip("date:T"), alt.Tooltip("metric:N"), alt.Tooltip("value:Q")],
            )
            .properties(height=360)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

        with st.popover("🧠 해석 가이드"):
            st.write(
                "- **visitors**: 방문자수\n"
                "- **active_users**: 활성 사용자수\n\n"
                "급증/급감 구간을 확인하고 이벤트/캠페인 영향 등을 점검해보세요."
            )

    with tab_data:
        st.write("데이터 테이블 출력")

        edited = st.data_editor(
            df_view,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
        )

        c1, c2 = st.columns([1, 2])
        with c1:
            st.download_button(
                "⬇️ CSV 다운로드",
                data=edited.to_csv(index=False).encode("utf-8-sig"),
                file_name="dashboard_data.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with c2:
            st.caption("데모: 표 수정은 화면용이며, 원본 데이터는 캐시/재생성될 수 있습니다.")

    with tab_settings:
        st.write("연결 시 옵션 체크박스")

        with st.container(border=True):
            opt_auto_connect = st.checkbox("앱 실행 시 자동 연결", value=True)
            opt_use_cache = st.checkbox("캐시 사용(성능 향상)", value=True)
            opt_readonly = st.checkbox("읽기 전용 모드(편집 비활성)", value=False)
            opt_send_telemetry = st.checkbox("사용 통계 전송(익명)", value=False)

            st.divider()

            if st.button("연결 테스트", use_container_width=True):
                with st.status("연결 확인 중...", expanded=True) as status:
                    st.write("옵션 적용 중…")
                    st.write(f"- 자동 연결: {opt_auto_connect}")
                    st.write(f"- 캐시 사용: {opt_use_cache}")
                    st.write(f"- 읽기 전용: {opt_readonly}")
                    st.write(f"- 사용 통계 전송: {opt_send_telemetry}")
                    st.write("가짜 엔드포인트 ping… ✅")
                    status.update(label="연결 테스트 완료!", state="complete")

else:  # 설정 페이지
    st.subheader("⚙️ 설정")
    st.write("화면 색상 / 데이터 소스 선택 / 기타 필요한 설정을 제공합니다.")

    # 1) 화면 색상
    with st.container(border=True):
        st.write("### 🎨 화면 색상(포인트 컬러)")
        new_accent = st.color_picker("포인트 컬러 선택", value=st.session_state.accent)
        c1, c2 = st.columns([1, 2])
        with c1:
            if st.button("적용", use_container_width=True):
                st.session_state.accent = new_accent
                st.rerun()
        with c2:
            st.caption("이 앱은 포인트 컬러만 가볍게 적용합니다(테마 전체 변경은 Streamlit 테마 설정을 사용).")

    # 2) 데이터 소스 선택
    with st.container(border=True):
        st.write("### 🗄️ 데이터 소스 선택")
        st.session_state.data_source = st.selectbox(
            "데이터 소스",
            ["더미(기본)", "더미(시즌성)", "CSV 업로드(확장)", "DB/API(확장)"],
            index=["더미(기본)", "더미(시즌성)", "CSV 업로드(확장)", "DB/API(확장)"].index(st.session_state.data_source)
            if st.session_state.data_source in ["더미(기본)", "더미(시즌성)", "CSV 업로드(확장)", "DB/API(확장)"]
            else 0,
            help="CSV/DB/API는 확장 포인트입니다.",
        )

        if st.session_state.data_source == "CSV 업로드(확장)":
            uploaded = st.file_uploader("CSV 업로드(date, visitors, active_users 컬럼)", type=["csv"])
            st.caption("현재 코드는 업로드 UI만 제공(실제 로드는 아래 확장 가이드 참고).")

        if st.session_state.data_source == "DB/API(확장)":
            st.text_input("API Endpoint", placeholder="https://api.example.com/metrics")
            st.text_input("API Key", type="password", placeholder="••••••••")
            st.caption("현재 코드는 입력 UI만 제공(실제 호출/인증은 별도 구현).")

    # 3) 기타 필요한 설정
    with st.container(border=True):
        st.write("### 🧩 기타 설정")
        st.session_state.show_help = st.toggle("도움말(가이드) 표시", value=st.session_state.show_help)
        refresh = st.select_slider("자동 새로고침(데모)", options=["OFF", "10s", "30s", "60s"], value="OFF")
        readonly_mode = st.toggle("읽기 전용 모드(데모)", value=False)

        st.caption("자동 새로고침/읽기 전용 모드는 데모 UI입니다. 필요 시 실제 로직에 연결해드릴 수 있어요.")

    with st.container(border=True):
        st.write("### 🧽 캐시/데이터 관리")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("캐시 초기화", use_container_width=True):
                st.cache_data.clear()
                st.success("캐시를 초기화했습니다.")
        with c2:
            if st.button("데모 데이터 재생성", use_container_width=True):
                st.session_state.seed = int(np.random.randint(0, 9999))
                st.rerun()
