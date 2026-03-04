"""network_analysis — Graph construction, centrality, community detection, contagion."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
import networkx as nx


@dataclass
class CentralityReport:
    degree: pd.Series
    betweenness: pd.Series
    eigenvector: pd.Series
    pagerank: pd.Series
    top_nodes: pd.DataFrame  # top 10 by each metric


def build_graph(
    edges_df: pd.DataFrame,
    source: str = "source",
    target: str = "target",
    weight: str | None = "weight",
    directed: bool = False,
) -> nx.Graph:
    """Build networkx graph from edge DataFrame."""
    G = nx.DiGraph() if directed else nx.Graph()
    for _, row in edges_df.iterrows():
        kwargs = {}
        if weight and weight in row.index:
            kwargs["weight"] = row[weight]
        G.add_edge(row[source], row[target], **kwargs)
    return G


def centrality_report(G: nx.Graph, top_n: int = 10) -> CentralityReport:
    """Compute degree, betweenness, eigenvector centrality, and PageRank."""
    degree = pd.Series(dict(G.degree()), name="degree").sort_values(ascending=False)
    betweenness = pd.Series(nx.betweenness_centrality(G), name="betweenness").sort_values(ascending=False)

    try:
        eigenvector = pd.Series(nx.eigenvector_centrality(G, max_iter=1000), name="eigenvector").sort_values(ascending=False)
    except nx.PowerIterationFailedConvergence:
        eigenvector = pd.Series(dtype=float, name="eigenvector")

    pagerank = pd.Series(nx.pagerank(G), name="pagerank").sort_values(ascending=False)

    top = pd.DataFrame({
        "degree": degree.head(top_n).index,
        "betweenness": betweenness.head(top_n).index,
        "pagerank": pagerank.head(top_n).index,
    })

    return CentralityReport(degree=degree, betweenness=betweenness,
                            eigenvector=eigenvector, pagerank=pagerank, top_nodes=top)


def detect_communities(G: nx.Graph, method: str = "louvain") -> dict:
    """Community detection. Returns {node: community_id}."""
    if method == "louvain":
        try:
            from networkx.algorithms.community import louvain_communities
            communities = louvain_communities(G, seed=42)
        except ImportError:
            from networkx.algorithms.community import greedy_modularity_communities
            communities = greedy_modularity_communities(G)
    elif method == "girvan_newman":
        from networkx.algorithms.community import girvan_newman
        comp = girvan_newman(G)
        communities = next(comp)
    else:
        raise ValueError(f"Unknown method: {method}")

    mapping = {}
    for i, comm in enumerate(communities):
        for node in comm:
            mapping[node] = i
    return mapping


def contagion_simulation(
    G: nx.Graph,
    seed_nodes: list,
    p_spread: float = 0.3,
    n_steps: int = 10,
    n_simulations: int = 100,
    random_state: int = 42,
) -> pd.DataFrame:
    """Simple SI contagion model. Returns fraction infected over time."""
    rng = np.random.default_rng(random_state)
    nodes = list(G.nodes())
    n = len(nodes)
    node_idx = {node: i for i, node in enumerate(nodes)}

    results = np.zeros((n_simulations, n_steps + 1))

    for sim in range(n_simulations):
        infected = set(seed_nodes)
        results[sim, 0] = len(infected) / n

        for t in range(1, n_steps + 1):
            new_infected = set()
            for node in infected:
                for neighbor in G.neighbors(node):
                    if neighbor not in infected and rng.random() < p_spread:
                        new_infected.add(neighbor)
            infected |= new_infected
            results[sim, t] = len(infected) / n

    return pd.DataFrame({
        "step": range(n_steps + 1),
        "mean_infected": results.mean(axis=0),
        "std_infected": results.std(axis=0),
        "p10": np.percentile(results, 10, axis=0),
        "p90": np.percentile(results, 90, axis=0),
    })


if __name__ == "__main__":
    # Example: random graph
    G = nx.barabasi_albert_graph(100, 3, seed=42)
    report = centrality_report(G)
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print(f"Top by PageRank: {report.pagerank.head(5).index.tolist()}")

    communities = detect_communities(G)
    n_comms = len(set(communities.values()))
    print(f"Communities: {n_comms}")

    contagion = contagion_simulation(G, seed_nodes=[0], p_spread=0.2)
    print(f"Contagion at step 10: {contagion.iloc[-1]['mean_infected']:.2%} infected")
