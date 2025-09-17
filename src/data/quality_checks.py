import pandas as pd

def run_quality_checks(df: pd.DataFrame):
    """
    This functions is responsible for the quality checks on 
    the raw dataframe (null values, duplicate resource_ids,negative_costs)

    """
    issues=[]
    # checking for null values
    if df.isnull().values.any():
        issues.append("NULL values found")



    if df['resource_id'].duplicated().any():
        issues.append("Duplicate resource IDs found")

    if "cost" in df.columns and (df["cost"] < 0).any():
        issues.append("Negative costs detected")

    return issues