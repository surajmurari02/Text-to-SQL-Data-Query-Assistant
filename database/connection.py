import sqlite3
from contextlib import contextmanager

import pandas as pd

from config import DATABASE_PATH, MAX_RESULT_ROWS, QUERY_TIMEOUT_SECONDS


@contextmanager
def get_connection():
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH), timeout=QUERY_TIMEOUT_SECONDS)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn:
            conn.close()


def execute_query(sql, limit=None):
    if not sql or not sql.strip():
        raise ValueError("SQL query cannot be empty")

    effective_limit = limit or MAX_RESULT_ROWS
    sql_upper = sql.upper().strip()

    if sql_upper.startswith("SELECT") and "LIMIT" not in sql_upper:
        sql = f"{sql.rstrip().rstrip(';')} LIMIT {effective_limit}"

    with get_connection() as conn:
        try:
            return pd.read_sql_query(sql, conn)
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Query execution failed: {str(e)}")
