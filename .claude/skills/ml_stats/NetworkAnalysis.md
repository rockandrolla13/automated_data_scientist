# NetworkAnalysis

## When to Use
- Analyzing corporate networks, interbank lending, CDS counterparty exposure.
- Centrality measures: which node is most systemically important?
- Community detection: natural clusters in relationship graphs.

## Packages
```python
import networkx as nx
```

## Corresponding Script
`/scripts/ml_stats/network_analysis.py`
- `build_graph(edges_df, source, target, weight) -> nx.Graph`
- `centrality_report(G) -> pd.DataFrame` — degree, betweenness, eigenvector, PageRank
- `detect_communities(G) -> dict` — Louvain or Girvan-Newman
- `contagion_simulation(G, seed_nodes, p_spread) -> pd.DataFrame`

## Gotchas
1. **Directed vs undirected.** Lending networks are directed. Correlation networks are undirected.
2. **Edge weights.** Normalize before centrality computation. Large weights can dominate.
3. **Disconnected components.** Check `nx.is_connected(G)` first. Some metrics fail on disconnected graphs.
4. **Scale.** networkx is fine for < 100k nodes. Use graph-tool or igraph for larger.

## References
- Newman (2010). Networks: An Introduction.
- networkx: https://networkx.org/
