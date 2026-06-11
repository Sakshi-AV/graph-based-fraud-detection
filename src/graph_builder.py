"""Build and update account transaction graphs."""

from __future__ import annotations

import networkx as nx
import pandas as pd


def build_transaction_graph(
    df: pd.DataFrame,
    sender_col: str = "nameOrig",
    receiver_col: str = "nameDest",
    amount_col: str = "amount",
) -> nx.DiGraph:
    """Build a directed account graph where edge weight is transaction amount."""
    required_columns = {sender_col, receiver_col, amount_col}
    missing = required_columns.difference(df.columns)
    if missing:
        raise KeyError(f"Missing graph builder columns: {sorted(missing)}")

    graph = nx.DiGraph()

    for row in df[[sender_col, receiver_col, amount_col]].itertuples(index=False):
        sender, receiver, amount = row
        amount = float(amount)

        if graph.has_edge(sender, receiver):
            graph[sender][receiver]["weight"] += amount
            graph[sender][receiver]["transaction_count"] += 1
        else:
            graph.add_edge(sender, receiver, weight=amount, transaction_count=1)

    return graph


def update_transaction_graph(
    graph: nx.DiGraph,
    sender: str,
    receiver: str,
    amount: float,
) -> nx.DiGraph:
    """Add a new transaction to an existing graph and return the graph."""
    amount = float(amount)

    if graph.has_edge(sender, receiver):
        graph[sender][receiver]["weight"] += amount
        graph[sender][receiver]["transaction_count"] += 1
    else:
        graph.add_edge(sender, receiver, weight=amount, transaction_count=1)

    return graph


if __name__ == "__main__":
    from preprocessing import preprocess_dataset

    transactions, _ = preprocess_dataset()
    transaction_graph = build_transaction_graph(transactions)
    print(f"Nodes: {transaction_graph.number_of_nodes()}")
    print(f"Edges: {transaction_graph.number_of_edges()}")

