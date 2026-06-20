import sqlite3
import pandas as pd

DB_PATH = "db/credit_default.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def search_customers(query):

    conn = get_connection()

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def get_customer(customer_id):

    conn = get_connection()

    df = pd.read_sql_query(
        f"SELECT * FROM customer_credit_data WHERE customer_id={customer_id}",
        conn
    )

    conn.close()

    return df


def save_prediction(data):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO default_prediction
        (customer_id, model_name, model_version, threshold,
        default_probability, predicted_label, prediction_time)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, data)

    conn.commit()

    conn.close()
    