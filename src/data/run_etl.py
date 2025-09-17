from src.data import ingestion, quality_checks, transformations

def main():
    """
    Run the full ETL process:
    1. Load CSVs
    2. Run quality checks
    3. Transform (if needed)
    4. Load to SQLite warehouse
    """

    # loading dataframes from raw csv files
    
    df_billing = ingestion.get_dataframe("data/raw/billing_data.csv")
    df_resources = ingestion.get_dataframe("data/raw/resources_data.csv")

    
    billing_issues = quality_checks.run_quality_checks(df_billing)
    
    #checking the quality of the dataframes loaded and if found any quality issue then performing required transformation

    if billing_issues:
        print("Billing data quality issues:", billing_issues)
        df_billing = transformations.transform_data(df_billing)

    resource_issues = quality_checks.run_quality_checks(df_resources)
    if resource_issues:
        print("Resources data quality issues:", resource_issues)
        df_resources = transformations.transform_data(df_resources)

    # Loading the dataframes to Sqlite warehouse
    ingestion.load(df_billing, "billing")
    ingestion.load(df_resources, "resources")

    print("ETL completed successfully!")

if __name__ == "__main__":
    main()
