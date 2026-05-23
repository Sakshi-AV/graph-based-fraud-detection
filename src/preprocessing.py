"""Dataset loading and preprocessing helpers for the fraud pipeline."""

from pathlib import Path
from typing import Tuple

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "PS_20174392719_1491204439457_log.csv"
GRAPH_COLUMNS = ["nameOrig", "nameDest"]


def load_dataset(dataset_path: str | Path = DEFAULT_DATASET_PATH, nrows: int = 100000) -> pd.DataFrame:
    """Load a limited number of rows from the transaction dataset."""
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    return pd.read_csv(dataset_path, nrows=nrows)


def inspect_columns(df: pd.DataFrame) -> list[str]:
    """Return the dataset column names for quick inspection/debugging."""
    return list(df.columns)


def drop_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing values and reset the index."""
    return df.dropna().reset_index(drop=True)


def separate_graph_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return sender/receiver account columns used to build the graph."""
    missing = [column for column in GRAPH_COLUMNS if column not in df.columns]
    if missing:
        raise KeyError(f"Missing graph columns: {missing}")

    return df[GRAPH_COLUMNS].copy()


def one_hot_encode_transaction_type(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode the transaction type column."""
    if "type" not in df.columns:
        raise KeyError("Missing required column: type")

    return pd.get_dummies(df, columns=["type"], prefix="type", dtype=int)


def preprocess_dataset(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
    nrows: int = 100000,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load, clean, encode, and return the cleaned data plus graph columns."""
    raw_df = load_dataset(dataset_path=dataset_path, nrows=nrows)
    cleaned_df = drop_nulls(raw_df)
    graph_columns = separate_graph_columns(cleaned_df)
    encoded_df = one_hot_encode_transaction_type(cleaned_df)

    return encoded_df, graph_columns


if __name__ == "__main__":
    transactions = load_dataset()
    print("Columns:", inspect_columns(transactions))
    cleaned_transactions, graph_data = preprocess_dataset()
    print(f"Cleaned shape: {cleaned_transactions.shape}")
    print(f"Graph columns shape: {graph_data.shape}")

