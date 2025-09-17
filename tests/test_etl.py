# src/data/run_etl.py

from src.data import ingestion, quality_checks, transformations

def run_etl(billing_csv: str, resources_csv: str, db_path: str):
    """
    Run the ETL process using given CSV files and store in SQLite db_path.
    """
    # Load dataframes
    df_billing = ingestion.get_dataframe(billing_csv)
    df_resources = ingestion.get_dataframe(resources_csv)

    # Quality checks & transformations
    billing_issues = quality_checks.run_quality_checks(df_billing)
    if billing_issues:
        df_billing = transformations.transform_data(df_billing)

    resource_issues = quality_checks.run_quality_checks(df_resources)
    if resource_issues:
        df_resources = transformations.transform_data(df_resources)

    # Load to SQLite
    ingestion.load(df_billing, "billing", db_path)
    ingestion.load(df_resources, "resources", db_path)

    return df_billing, df_resources
