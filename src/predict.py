"""Single-transaction fraud prediction logic."""

from __future__ import annotations

from pathlib import Path

import joblib
import networkx as nx
import pandas as pd

try:
    from .feature_engineering import compute_graph_features
    from .graph_builder import build_transaction_graph, update_transaction_graph
    from .model import FEATURE_COLUMNS_PATH, MODEL_PATH
    from .preprocessing import DEFAULT_DATASET_PATH, preprocess_dataset
except ImportError:
    from feature_engineering import compute_graph_features
    from graph_builder import build_transaction_graph, update_transaction_graph
    from model import FEATURE_COLUMNS_PATH, MODEL_PATH
    from preprocessing import DEFAULT_DATASET_PATH, preprocess_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_prediction_artifacts() -> tuple[object, list[str]]:
    """Load the trained model and saved feature column order."""
    if not MODEL_PATH.exists() or not FEATURE_COLUMNS_PATH.exists():
        raise FileNotFoundError("Model artifacts not found. Run `python src/model.py` first.")

    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
    return model, feature_columns


def initialize_graph(dataset_path: str | Path = DEFAULT_DATASET_PATH, nrows: int = 100000) -> nx.DiGraph:
    """Create the starting transaction graph from the cleaned dataset."""
    transactions, _ = preprocess_dataset(dataset_path=dataset_path, nrows=nrows)
    return build_transaction_graph(transactions)


def _build_prediction_row(
    sender: str,
    receiver: str,
    amount: float,
    graph: nx.DiGraph,
    feature_columns: list[str],
) -> pd.DataFrame:
    """Create a model-ready dataframe for one transaction."""
    graph_features = compute_graph_features(graph)

    row = {column: 0 for column in feature_columns}
    row["step"] = 1
    row["amount"] = float(amount)
    row["oldbalanceOrg"] = 0.0
    row["newbalanceOrig"] = 0.0
    row["oldbalanceDest"] = 0.0
    row["newbalanceDest"] = 0.0
    row["isFlaggedFraud"] = 0

    row["sender_degree"] = graph_features["degree"].get(sender, 0)
    row["receiver_degree"] = graph_features["degree"].get(receiver, 0)
    row["sender_pagerank"] = graph_features["pagerank"].get(sender, 0.0)
    row["receiver_pagerank"] = graph_features["pagerank"].get(receiver, 0.0)
    row["sender_clustering"] = graph_features["clustering"].get(sender, 0.0)
    row["receiver_clustering"] = graph_features["clustering"].get(receiver, 0.0)

    # A standalone prediction does not receive transaction type yet, so type columns remain 0.
    return pd.DataFrame([row], columns=feature_columns)


def predict_transaction(
    sender: str,
    receiver: str,
    amount: float,
    graph: nx.DiGraph | None = None,
) -> dict[str, float | int]:
    """Update the graph, run fraud prediction, and return label plus probability."""
    model, feature_columns = load_prediction_artifacts()

    if graph is None:
        graph = initialize_graph()

    update_transaction_graph(graph, sender, receiver, float(amount))
    prediction_row = _build_prediction_row(sender, receiver, float(amount), graph, feature_columns)

    prediction = int(model.predict(prediction_row)[0])
    probability = float(model.predict_proba(prediction_row)[0][1])

    return {
        "fraud_prediction": prediction,
        "fraud_probability": probability,
    }


if __name__ == "__main__":
    result = predict_transaction("C1231006815", "M1979787155", 9839.64)
    print(result)
