import pandas as pd
from loguru import logger

def read_file(file_path):
    """
    Reads a JSON, Excel, CSV, Parquet, Feather, or TSV file into a Pandas DataFrame.

    Parameters:
        file_path (str): Path to the file.

    Returns:
        pd.DataFrame: DataFrame containing the file data.
    """
    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.endswith(".json"):
            return pd.read_json(file_path)
        elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            return pd.read_excel(file_path)
        elif file_path.endswith(".parquet"):
            return pd.read_parquet(file_path)
        elif file_path.endswith(".feather"):
            return pd.read_feather(file_path)
        elif file_path.endswith(".tsv"):
            return pd.read_csv(file_path, sep="\t")
        else:
            raise ValueError("Unsupported file format. Please use JSON, Excel, CSV, Parquet, Feather, or TSV.")
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return None
