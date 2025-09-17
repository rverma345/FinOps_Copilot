import pandas as pd
import sqlite3
from pathlib import Path

# Define warehouse path
DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "processed/warehouse.db"

# Extract

def get_dataframe(file_path: str) -> pd.DataFrame:
    """
    Reads a CSV file into a pandas DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to read {file_path}: {e}")


# Load
def load(df: pd.DataFrame, table_name: str, db_path: str = DB_PATH):
    """
    Loads a DataFrame into the SQLite warehouse.
    Overwrites the table if it already exists.
    """
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()
        print(f"Loaded {len(df)} rows into table '{table_name}' in {db_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to load data into {table_name}: {e}")

