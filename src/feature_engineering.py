"""Graph feature engineering for transaction-level model inputs."""

from __future__ import annotations

import networkx as nx
import pandas as pd

try:
    from .graph_builder import build_transaction_graph
except ImportError:
    from graph_builder import build_transaction_graph


GRAPH_FEATURE_COLUMNS = [
    "sender_degree",
    "receiver_degree",
    "sender_pagerank",
    "receiver_pagerank",
    "sender_clustering",
    "receiver_clustering",
]


def compute_graph_features(graph: nx.DiGraph) -> dict[str, dict[str, float]]:
    """Compute degree, PageRank, and clustering coefficient per account."""
    if graph.number_of_nodes() == 0:
        return {"degree": {}, "pagerank": {}, "clustering": {}}

    degree = dict(graph.degree())
    pagerank = nx.pagerank(graph, weight="weight", max_iter=100, tol=1e-04)
    clustering = nx.clustering(graph.to_undirected(), weight="weight")

    return {
        "degree": degree,
        "pagerank": pagerank,
        "clustering": clustering,
    }


def map_graph_features_to_transactions(
    df: pd.DataFrame,
    graph_features: dict[str, dict[str, float]],
    sender_col: str = "nameOrig",
    receiver_col: str = "nameDest",
) -> pd.DataFrame:
    """Attach sender and receiver graph features to every transaction row."""
    featured_df = df.copy()

    degree = graph_features["degree"]
    pagerank = graph_features["pagerank"]
    clustering = graph_features["clustering"]

    featured_df["sender_degree"] = featured_df[sender_col].map(degree).fillna(0)
    featured_df["receiver_degree"] = featured_df[receiver_col].map(degree).fillna(0)
    featured_df["sender_pagerank"] = featured_df[sender_col].map(pagerank).fillna(0.0)
    featured_df["receiver_pagerank"] = featured_df[receiver_col].map(pagerank).fillna(0.0)
    featured_df["sender_clustering"] = featured_df[sender_col].map(clustering).fillna(0.0)
    featured_df["receiver_clustering"] = featured_df[receiver_col].map(clustering).fillna(0.0)

    return featured_df


def add_graph_features(df: pd.DataFrame, graph: nx.DiGraph | None = None) -> pd.DataFrame:
    """Build graph features and map them back to the transaction dataframe."""
    if graph is None:
        graph = build_transaction_graph(df)

    graph_features = compute_graph_features(graph)
    return map_graph_features_to_transactions(df, graph_features)


if __name__ == "__main__":
    from preprocessing import preprocess_dataset

    transactions, _ = preprocess_dataset()
    featured_transactions = add_graph_features(transactions)
    print(featured_transactions[GRAPH_FEATURE_COLUMNS].head())
