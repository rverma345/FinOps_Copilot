import pandas as pd


def extract_from_csv(path: str)-> pd.Dataframe:
    """Extract Cloud billing data from CSV"""
    return pd.read_csv(path)
