# GraphNeuralNetwork

## When to Use
- Data has graph structure: corporate networks, supply chains, CDS counterparty graphs.
- Node classification (issuer risk), link prediction (default contagion).
- When features of neighbors carry signal.

## Packages
```python
import torch
from torch_geometric.nn import GCNConv, GATConv, SAGEConv
from torch_geometric.data import Data
```
**Install:** `pip install torch-geometric` (heavy, install on demand)

## Corresponding Script
`/scripts/ml_stats/graph_neural_network.py`
- `build_gcn(in_channels, hidden, out_channels) -> nn.Module`
- `create_graph_data(nodes_df, edges_df, target_col) -> Data`
- `train_gnn(model, data, epochs, lr) -> GNNResult`

## Gotchas
1. **torch-geometric install is complex.** Depends on torch version. Follow official install guide.
2. **Over-smoothing.** >3 GCN layers → all node embeddings converge. Use 2 layers.
3. **Graph construction is the real task.** Bad edges → bad model. Think hard about what connects nodes.
4. **Transductive vs inductive.** GCN is transductive (needs full graph at inference). GraphSAGE is inductive.

## References
- Kipf & Welling (2017). Semi-Supervised Classification with Graph Convolutional Networks.
