"""PyVis graph export helpers."""

from __future__ import annotations

from pathlib import Path

import networkx as nx
from pyvis.network import Network


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GRAPH_DIR = PROJECT_ROOT / "graph"
GRAPH_PATH = GRAPH_DIR / "graph.html"


def export_graph_html(graph: nx.DiGraph, risky_accounts: set[str] | None = None, max_nodes: int = 150) -> Path:
    """Export the runtime NetworkX graph to graph/graph.html."""
    risky_accounts = risky_accounts or set()
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    display_graph = _build_display_subgraph(graph, risky_accounts, max_nodes=max_nodes)

    network = Network(height="720px", width="100%", bgcolor="#101317", font_color="#edf2f6", directed=True)
    network.barnes_hut()

    for node in display_graph.nodes:
        degree = display_graph.degree(node)
        color = "#ff6b6b" if node in risky_accounts else ("#5eb1ff" if degree > 2 else "#44d19d")
        network.add_node(node, label=node, color=color, size=12 + min(degree * 3, 28))

    for source, target, data in display_graph.edges(data=True):
        weight = float(data.get("weight", 1.0))
        network.add_edge(source, target, value=max(1, min(weight / 10000, 12)), title=f"Amount: {weight:.2f}")

    network.write_html(str(GRAPH_PATH), notebook=False, open_browser=False)
    return GRAPH_PATH


def _build_display_subgraph(graph: nx.DiGraph, risky_accounts: set[str], max_nodes: int) -> nx.DiGraph:
    """Keep PyVis export responsive by showing risky and high-degree accounts."""
    selected_nodes = set(risky_accounts)
    high_degree_nodes = sorted(graph.degree, key=lambda item: item[1], reverse=True)

    for node, _ in high_degree_nodes:
        selected_nodes.add(node)
        if len(selected_nodes) >= max_nodes:
            break

    return graph.subgraph(selected_nodes).copy()
