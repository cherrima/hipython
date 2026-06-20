import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "credit_default.db"
DATA_PATH = BASE_DIR / "data" / "UCI_Credit_Card.csv"

DB_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------
# 1. 원본 CSV 로드
# -----------------------------------
df = pd.read_csv(DATA_PATH)

print(f"[INFO] Loaded source data: {DATA_PATH}")
print(f"[INFO] Source shape: {df.shape}")

# -----------------------------------
# 2. 컬럼명 정리
# -----------------------------------
rename_map = {}

if "default.payment.next.month" in df.columns:
    rename_map["default.payment.next.month"] = "default"

if "default payment next month" in df.columns:
    rename_map["default payment next month"] = "default"

if "ID" in df.columns:
    rename_map["ID"] = "customer_id"

df = df.rename(columns=rename_map)

# customer_id가 없으면 생성
if "customer_id" not in df.columns:
    df.insert(0, "customer_id", range(1, len(df) + 1))

print(f"[INFO] Columns after rename: {df.columns.tolist()}")

# -----------------------------------
# 3. DB 연결
# -----------------------------------
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# -----------------------------------
# 4. 기존 테이블 삭제
# -----------------------------------
cur.execute("DROP TABLE IF EXISTS default_prediction")
cur.execute("DROP TABLE IF EXISTS customer_credit_data")

# -----------------------------------
# 5. customer_credit_data 생성/적재
# -----------------------------------
df.to_sql("customer_credit_data", conn, if_exists="replace", index=False)

# -----------------------------------
# 6. default_prediction 생성
# -----------------------------------
cur.execute("""
CREATE TABLE default_prediction (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    model_version TEXT,
    threshold REAL NOT NULL,
    default_probability REAL NOT NULL,
    predicted_label INTEGER NOT NULL,
    top_feature_1 TEXT,
    top_feature_2 TEXT,
    top_feature_3 TEXT,
    prediction_time TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print(f"[INFO] Database initialized: {DB_PATH}")
print(f"[INFO] customer_credit_data rows loaded: {len(df)}")
print("[INFO] Tables recreated: customer_credit_data, default_prediction")
