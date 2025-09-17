# src/analytics/kpis.py
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data") / "processed/warehouse.db"

def _connect():
    return sqlite3.connect(DB_PATH)

def monthly_cost_by_service(month):
    con = _connect()
    q = """
    SELECT service, resource_group, SUM(cost) as total_cost
    FROM billing
    WHERE invoice_month = ?
    GROUP BY service, resource_group
    ORDER BY total_cost DESC
    """
    df = pd.read_sql(q, con, params=(month,))
    con.close()
    return df

def monthy_cost_by_resource(month):
    con = _connect()
    q = """
    SELECT resource_id, SUM(cost) as total_cost
    FROM billing
    WHERE invoice_month = ?
    GROUP BY resource_id
    ORDER BY total_cost DESC
    """
    df = pd.read_sql(q, con, params=(month,))
    con.close()
    return df

def six_month_trend():
    con = _connect()
    q = """
    SELECT invoice_month, SUM(cost) as total_cost
    FROM billing
    GROUP BY invoice_month
    ORDER BY invoice_month
    """
    df = pd.read_sql(q, con)
    con.close()
    return df

def top_n_cost_drivers(month, n=5):
    con = _connect()
    q = """
    SELECT resource_id, service, resource_group, SUM(cost) as total_cost
    FROM billing
    WHERE invoice_month = ?
    GROUP BY resource_id, service, resource_group
    ORDER BY total_cost DESC
    LIMIT ?
    """
    df = pd.read_sql(q, con, params=(month, n))
    con.close()
    return df
