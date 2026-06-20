import numpy as np
import pandas as pd


PAY_COLS = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    학습/예측 공통 Feature Engineering
    - credit_utilization
    - payment_ratio
    - late_payment_count
    - recent_3m_bill_avg (검색/표시용)
    """
    df = df.copy()

    # 1) credit_utilization = 최근 청구금액 / 한도
    df["credit_utilization"] = df["BILL_AMT1"] / (df["LIMIT_BAL"] + 1e-6)

    # 2) payment_ratio = 최근 결제금액 / 최근 청구금액
    # 음수 / 0 대응 위해 abs + epsilon
    df["payment_ratio"] = df["PAY_AMT1"] / (np.abs(df["BILL_AMT1"]) + 1e-6)

    # 3) late_payment_count = 연체 발생 횟수
    df["late_payment_count"] = (df[PAY_COLS] > 0).sum(axis=1)

    # 4) 최근 3개월 청구금액 평균
    df["recent_3m_bill_avg"] = (
        df["BILL_AMT1"] + df["BILL_AMT2"] + df["BILL_AMT3"]
    ) / 3.0

    return df


def add_log_features(
    df: pd.DataFrame,
    num_cols: list[str],
    log_safe_cols: list[str] | None = None
) -> pd.DataFrame:
    """
    학습 시와 동일한 log feature 생성
    - log_safe_cols가 주어지면 해당 컬럼만 생성
    - 없으면 num_cols[11:] 중 AGE 제외 + 음수 없는 컬럼만 자동 선택
    """
    df = df.copy()

    if log_safe_cols is None:
        long_tail_cols = [col for col in num_cols[11:] if col != "AGE"]
        log_safe_cols = []

        for col in long_tail_cols:
            if col in df.columns and df[col].min() > -1:
                log_safe_cols.append(col)

    for col in log_safe_cols:
        if col in df.columns:
            df[col + "_log"] = np.log1p(df[col])

    return df


def make_model_input(
    df: pd.DataFrame,
    cat_cols: list[str],
    log_safe_cols: list[str] | None = None
) -> pd.DataFrame:
    """
    웹 입력 / DB 조회 데이터를 학습 시점과 동일한 모델 입력 형태로 변환
    """
    df = add_features(df)

    num_cols = [col for col in df.columns if col not in cat_cols]
    df = add_log_features(df, num_cols=num_cols, log_safe_cols=log_safe_cols)

    return df