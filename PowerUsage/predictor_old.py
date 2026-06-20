"""
predictor.py — 전력 피크 예측 추론 모듈
────────────────────────────────────────────────────────────────
올라운더팀 Project 2 | 팀원 연동용

[사용법]
    from predictor import predict
    result = predict(df)

[입력 df 컬럼]  (DB 기준 컬럼명)
    Date        : str   'YYYY-MM-DD'
    hour        : int   0~23
    temperature : float 기온(°C)
    humidity    : float 습도(%)
    windspeed   : float 풍속(m/s)
    rainfall    : float 강수량(mm)
    op_code     : int   생산구분 (0=비가동, 1~4=생산그룹)
    output      : int   생산량 (개)
    weekday     : int   요일 (1=월 ~ 7=일)
    weekend     : int   주말여부 0/1
    holiday     : int   공휴일여부 0/1

[출력 dict]
    {
      'Set_A': [{'y1': float, 'y2': float, 'y3': float, 'y4': float}, ...],
      'Set_B': [...],
      'Set_C': [...],
    }
    y1=15분, y2=30분, y3=45분, y4=60분  (단위: kW)
    리스트 인덱스 = 입력 df 행 순서와 동일

[필요 파일 — 같은 폴더에 있어야 함]
    energy_pipeline_v3.pkl  : 학습된 모델 (15/30/45/60분 × Set_A/B/C)
    PowerMgt.db             : DB (predict_from_db 사용 시)

[팀원 전달 정보]
    - 파일명        : predictor.py
    - 예측함수      : predict(df)
    - pkl 파일      : energy_pipeline_v3.pkl
    - 입력 df 컬럼  : Date, hour, temperature, humidity, windspeed,
                      rainfall, op_code, output, weekday, weekend, holiday
    - 출력 컬럼     : y1=15분, y2=30분, y3=45분, y4=60분 (단위: kW)
────────────────────────────────────────────────────────────────
"""

import os
import warnings
import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# ── 모델 로드 (임포트 시 1회만 실행) ─────────────────────────────
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_PKL_PATH = os.path.join(_BASE_DIR, 'energy_pipeline_v3.pkl')

_PKL          = joblib.load(_PKL_PATH)
_MODELS       = _PKL['models']        # {타겟: {Set_name: XGBRegressor}}
_SCALERS      = _PKL['scalers']       # {Set_name: StandardScaler}
_FEATURE_SETS = _PKL['feature_sets']  # {Set_name: [feat_col, ...]}
_TARGETS      = _PKL['targets']       # ['15분','30분','45분','60분']

# ── 상수 ─────────────────────────────────────────────────────────

_SMP = {
    1: 70.47,  2: 75.25,  3: 83.78,  4: 75.97,
    5: 78.93,  6: 82.72,  7: 87.04,  8: 93.41,
    9: 98.21, 10:107.53, 11:126.83, 12:142.46,
}

_MANPOWER = {0: 0.0, 1: 0.72, 2: 0.69, 3: 1.81, 4: 6.34}


def _tariff(month):
    if month in [6, 7, 8]:        return 191.6
    if month in [11, 12, 1, 2]:   return 109.8
    return 167.2


def _tou(month, hour):
    if hour >= 22 or hour <= 7:
        return 0, 95.7
    if month in [6, 7, 8]:
        return (2, 155.0) if hour in range(11, 18) else (1, 121.5)
    if month in [11, 12, 1, 2]:
        return (2, 155.0) if hour in [10, 17, 18, 19, 20] else (1, 121.5)
    return 1, 121.5


# ── 파생변수 자동 생성 ────────────────────────────────────────────
def _build_features(df_input):
    df = df_input.copy()

    dt       = pd.to_datetime(df['Date'])
    df['m']  = dt.dt.month
    df['d']  = dt.dt.day
    df['day']= df['weekday'].astype(int)
    df['시간'] = df['hour'].astype(int)

    df['기온']   = df['temperature']
    df['습도']   = df['humidity']
    df['풍속']   = df['windspeed']
    df['강수량'] = df['rainfall'].fillna(0)

    df['is_weekend'] = df['weekend'].astype(int)
    df['is_holiday'] = df['holiday'].astype(int)
    df['weekday']    = df['weekday'].astype(int)
    df['주간여부']   = df['시간'].between(9, 18).astype(int)

    df['GMM생산구분'] = df['op_code'].astype(int)
    df['생산량']      = df['output'].astype(int)
    df['가동여부']    = (df['생산량'] > 0).astype(int)
    df['공장인원']    = df['GMM생산구분'].map(_MANPOWER).fillna(0)
    df['furnace_on']  = (
        df['GMM생산구분'].isin([1, 2, 3]) | (df['생산량'] > 0)
    ).astype(int)
    df['인건비'] = df['시간'].apply(lambda h: 1.0 if 9 <= h <= 18 else 1.5)

    df['전기요금(계절)'] = df['m'].apply(_tariff)
    tou = df.apply(lambda r: _tou(r['m'], r['시간']), axis=1)
    df['tou_bucket'] = tou.apply(lambda x: x[0])
    df['tou_price']  = tou.apply(lambda x: x[1])
    df['smp_land']   = df['m'].map(_SMP).fillna(90.0)

    return df


# ── 메인 예측 함수 ────────────────────────────────────────────────
def predict(df):
    """
    전력 피크 예측 — Set_A / Set_B / Set_C 동시 실행

    Parameters
    ----------
    df : pd.DataFrame
        Date, hour, temperature, humidity, windspeed,
        rainfall, op_code, output, weekday, weekend, holiday

    Returns
    -------
    dict
        {
          'Set_A': [{'y1':float,'y2':float,'y3':float,'y4':float}, ...],
          'Set_B': [...],
          'Set_C': [...],
        }
        y1=15분, y2=30분, y3=45분, y4=60분  (단위: kW)
    """
    df_feat   = _build_features(df)
    target_key = {'15분': 'y1', '30분': 'y2', '45분': 'y3', '60분': 'y4'}
    n_rows    = len(df)

    results = {
        sn: [{'y1': 0., 'y2': 0., 'y3': 0., 'y4': 0.} for _ in range(n_rows)]
        for sn in _FEATURE_SETS
    }

    for set_name, feat_cols in _FEATURE_SETS.items():
        for c in feat_cols:
            if c not in df_feat.columns:
                df_feat[c] = 0

        X        = df_feat[feat_cols].fillna(0)
        X_scaled = _SCALERS[set_name].transform(X)

        for target in _TARGETS:
            y_key  = target_key[target]
            model  = _MODELS[target][set_name]
            y_pred = model.predict(X_scaled).clip(0, 250)
            for i, val in enumerate(y_pred):
                results[set_name][i][y_key] = round(float(val), 2)

    return results


# ── DB 연동 편의 함수 ─────────────────────────────────────────────
def predict_from_db(db_path, date):
    """
    DB에서 특정 날짜 데이터를 가져와 predict() 실행

    Parameters
    ----------
    db_path : str  PowerMgt.db 경로
    date    : str  'YYYY-MM-DD'
    """
    import sqlite3
    conn = sqlite3.connect(db_path)
    sql = """
        SELECT
            w.date        AS Date,
            w.hour,
            w.temperature,
            w.humidity,
            w.windspeed,
            w.rainfall,
            COALESCE(o.op_code, 0)  AS op_code,
            COALESCE(o.output,  0)  AS output,
            c.weekday,
            c.weekend,
            c.holiday
        FROM WeatherForecast w
        LEFT JOIN Calendar c
               ON w.date = c.date
        LEFT JOIN OperationForecast o
               ON w.date = o.date AND w.hour = o.hour
        WHERE w.date = ?
        ORDER BY w.hour
    """
    df_db = pd.read_sql(sql, conn, params=(date,))
    conn.close()

    if df_db.empty:
        print(f"[predictor] {date} — DB에 날씨 데이터 없음")
        return {}

    return predict(df_db)


# ── 단독 실행 테스트 ──────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("  predictor.py 단독 테스트")
    print("=" * 60)

    sample = pd.DataFrame({
        'Date'       : ['2021-07-05'] * 5,
        'hour'       : [8, 10, 13, 17, 22],
        'temperature': [27.0, 31.0, 33.0, 29.0, 24.0],
        'humidity'   : [60.0, 65.0, 70.0, 72.0, 75.0],
        'windspeed'  : [2.0, 1.5, 1.0, 2.5, 3.0],
        'rainfall'   : [0.0, 0.0, 0.0, 0.0, 0.0],
        'op_code'    : [1, 1, 1, 0, 0],
        'output'     : [1200, 1800, 2000, 0, 0],
        'weekday'    : [1, 1, 1, 1, 1],
        'weekend'    : [0, 0, 0, 0, 0],
        'holiday'    : [0, 0, 0, 0, 0],
    })

    print("\n[입력]")
    print(sample[['Date','hour','op_code','output']].to_string(index=False))

    result = predict(sample)

    print("\n[예측 결과]")
    for set_name, rows in result.items():
        print(f"\n  ▶ {set_name}")
        print(f"  {'hour':>4}  {'y1(15분)':>9} {'y2(30분)':>9} {'y3(45분)':>9} {'y4(60분)':>9}")
        print("  " + "-" * 48)
        for i, r in enumerate(rows):
            h = sample.iloc[i]['hour']
            print(f"  {h:>4}  {r['y1']:>9.1f} {r['y2']:>9.1f} {r['y3']:>9.1f} {r['y4']:>9.1f}")
