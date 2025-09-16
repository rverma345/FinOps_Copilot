import pandas as pd
import sqlite3
import logging
from typing import Dict, List, Any

# Database path
DB_PATH = "data/warehouse.db"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


# ----------------------------
# Data Quality Checks
# ----------------------------
def run_quality_checks(billing: pd.DataFrame, resources: pd.DataFrame) -> List[str]:
    """
    Run quality checks on billing and resources data.
    """
    issues = []

    if billing["resource_id"].isnull().any():
        issues.append("❌ Null resource_id found in billing")

    if (billing["cost"] < 0).any():
        issues.append("❌ Negative cost found in billing")

    if resources["resource_id"].duplicated().any():
        issues.append("❌ Duplicate resource_id found in resources")

    return issues or ["✅ All checks passed"]


# ----------------------------
# Load Data into SQLite
# ----------------------------
def load_to_db(billing: pd.DataFrame, resources: pd.DataFrame) -> None:
    """
    Load billing and resources data into SQLite database.
    """
    with sqlite3.connect(DB_PATH) as conn:
        billing.to_sql("billing", conn, if_exists="replace", index=False)
        resources.to_sql("resources", conn, if_exists="replace", index=False)

    logging.info("✅ Data successfully loaded into SQLite: %s", DB_PATH)


# ----------------------------
# KPI Queries
# ----------------------------
def monthly_cost_by_service(month: str) -> List[Dict[str, Any]]:
    """
    Get total cost by service for a given month.
    """
    query = """
    SELECT service, SUM(cost) as total_cost
    FROM billing
    WHERE invoice_month = ?
    GROUP BY service
    ORDER BY total_cost DESC;
    """
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(query, conn, params=[month])
    return df.to_dict(orient="records")


def monthly_cost_by_rg(month: str) -> List[Dict[str, Any]]:
    """
    Get total cost by resource group for a given month.
    """
    query = """
    SELECT resource_group, SUM(cost) as total_cost
    FROM billing
    WHERE invoice_month = ?
    GROUP BY resource_group
    ORDER BY total_cost DESC;
    """
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(query, conn, params=[month])
    return df.to_dict(orient="records")


def six_month_trend() -> List[Dict[str, Any]]:
    """
    Get spend trend for the last 6 months.
    """
    query = """
    SELECT invoice_month, SUM(cost) as total_cost
    FROM billing
    GROUP BY invoice_month
    ORDER BY invoice_month;
    """
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(query, conn)
    return df.to_dict(orient="records")


def monthly_cost_kpis(month: str) -> Dict[str, Any]:
    """
    Bundle monthly KPIs by service and resource group.
    """
    return {
        "month": month,
        "by_service": monthly_cost_by_service(month),
        "by_resource_group": monthly_cost_by_rg(month),
    }


def idle_resources() -> List[Dict[str, Any]]:
    """
    Identify idle resources with low usage but cost > 0.
    """
    query = """
    SELECT resource_id, AVG(usage_qty) as avg_usage, SUM(cost) as total_cost
    FROM billing
    GROUP BY resource_id
    HAVING avg_usage < 1;
    """
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(query, conn)
    return df.to_dict(orient="records")


# ----------------------------
# Standalone Testing
# ----------------------------
def main():
    #Step1: Extracting the data
    billing = pd.read_csv('data/billing.csv')
    resource= pd.read_csv('data/resource_metadata.csv')

    # Step 2: Transform (Quality Checks)
    issues= run_quality_checks(billing,resource)
    for issue in issues:
        logging.warning(issue)
    
    # Step 3: load

    load_to_db(billing,resource)


    # query kpis
    month = "2025-03"
    logging.info("📊 Monthly Cost by Service (%s): %s", month, monthly_cost_by_service(month))
    logging.info("📊 Monthly Cost by Resource Group (%s): %s", month, monthly_cost_by_rg(month))
    logging.info("📊 6-Month Trend: %s", six_month_trend())
    logging.info("📊 Idle Resources: %s", idle_resources())

if __name__=='__main__':
    main()