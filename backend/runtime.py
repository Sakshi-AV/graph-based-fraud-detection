"""Runtime model, graph, and anomaly detector state."""

from __future__ import annotations

import networkx as nx

from backend.config import DATASET_PATH
from backend.services.anomaly import TransactionAnomalyDetector
from backend.services.database import init_db
from src.predict import initialize_graph, load_prediction_artifacts


MODEL = None
FEATURE_COLUMNS = None
FRAUD_THRESHOLD = None
TRANSACTION_GRAPH = None
ANOMALY_DETECTOR = TransactionAnomalyDetector()


def load_runtime_artifacts() -> None:
    """Load ML artifacts and graph state once for the Flask process."""
    global MODEL, FEATURE_COLUMNS, FRAUD_THRESHOLD, TRANSACTION_GRAPH

    if MODEL is None or FEATURE_COLUMNS is None or FRAUD_THRESHOLD is None:
        MODEL, FEATURE_COLUMNS, FRAUD_THRESHOLD = load_prediction_artifacts()

    if TRANSACTION_GRAPH is None:
        try:
            TRANSACTION_GRAPH = initialize_graph(dataset_path=DATASET_PATH)
        except FileNotFoundError:
            TRANSACTION_GRAPH = nx.DiGraph()

    init_db()

