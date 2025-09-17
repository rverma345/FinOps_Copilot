import sqlite3
import pandas as pd

DB_PATH= 'data/processed/warehouse.db'

def find_idle_resources(threshold_usage=5.0, month=None):
    """
    Simple heuristic: resources with usage_qty < threshold for the selected month.
    Returns rows with estimated monthly saving if we shut them off (cost).
    """
    con = sqlite3.connect(DB_PATH)

    if month:
        where_clause = "WHERE invoice_month = ?"
        params = (month, threshold_usage)
    else:
        where_clause = ""
        params = (threshold_usage,)

    q = f"""
    SELECT resource_id, service, resource_group, SUM(usage_qty) as usage_qty, SUM(cost) as total_cost
    FROM billing
    {where_clause}
    GROUP BY resource_id, service, resource_group
    HAVING usage_qty < ?
    ORDER BY total_cost DESC
    LIMIT 200
    """

    df = pd.read_sql(q, con, params=params)
    con.close()

    # Estimated saving if we remove them is their cost
    df["estimated_monthly_saving"] = df["total_cost"].round(2)
    return df
