import pandas as pd


def transform_data(df):
    """
    Cleans dataframe depending on available columns.
    - Drops nulls
    - Fixes negative costs (if cost exists)
    - Removes duplicates (resource_id + invoice_month if both exist, else resource_id only)
    """
    # Drop nulls
    df = df.dropna()

    # Fix negative costs if 'cost' column exists
    if "cost" in df.columns:
        df.loc[df["cost"] < 0, "cost"] = 0

    # Handle duplicates
    if {"resource_id", "invoice_month"}.issubset(df.columns):
        df = df.drop_duplicates(subset=["resource_id", "invoice_month"])
    elif "resource_id" in df.columns:
        df = df.drop_duplicates(subset=["resource_id"])

    return df


