"""graph_neural_network — GNN building blocks via PyTorch Geometric."""

from dataclasses import dataclass
import numpy as np
import pandas as pd

# torch_geometric is heavy — imported inside functions


@dataclass
class GNNResult:
    train_losses: list[float]
    val_accuracy: float | None
    node_embeddings: np.ndarray | None
    best_epoch: int


def create_graph_data(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str | None = None,
    source_col: str = "source",
    target_node_col: str = "target",
):
    """Create PyG Data object from DataFrames."""
    import torch
    from torch_geometric.data import Data

    x = torch.tensor(nodes_df[feature_cols].values, dtype=torch.float)

    # Node name -> index mapping
    node_ids = {name: i for i, name in enumerate(nodes_df.index)}
    src = edges_df[source_col].map(node_ids).values
    dst = edges_df[target_node_col].map(node_ids).values
    edge_index = torch.tensor(np.array([src, dst]), dtype=torch.long)

    y = None
    if target_col and target_col in nodes_df.columns:
        y = torch.tensor(nodes_df[target_col].values, dtype=torch.long)

    return Data(x=x, edge_index=edge_index, y=y, num_nodes=len(nodes_df))


def build_gcn(in_channels: int, hidden: int = 64, out_channels: int = 2, dropout: float = 0.2):
    """2-layer GCN classifier."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch_geometric.nn import GCNConv

    class GCN(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = GCNConv(in_channels, hidden)
            self.conv2 = GCNConv(hidden, out_channels)
            self.dropout = dropout

        def forward(self, data):
            x, edge_index = data.x, data.edge_index
            x = self.conv1(x, edge_index)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
            x = self.conv2(x, edge_index)
            return x

        def embed(self, data):
            x, edge_index = data.x, data.edge_index
            x = self.conv1(x, edge_index)
            return F.relu(x)

    return GCN()


def train_gnn(model, data, epochs: int = 200, lr: float = 0.01, train_mask=None) -> GNNResult:
    """Train GNN on node classification task."""
    import torch
    import torch.nn.functional as F

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=5e-4)
    if train_mask is None:
        n = data.num_nodes
        train_mask = torch.zeros(n, dtype=torch.bool)
        train_mask[:int(n * 0.6)] = True

    losses = []
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        out = model(data)
        loss = F.cross_entropy(out[train_mask], data.y[train_mask])
        loss.backward()
        optimizer.step()
        losses.append(loss.item())

    model.eval()
    with torch.no_grad():
        pred = model(data).argmax(dim=1)
        val_mask = ~train_mask
        if val_mask.sum() > 0 and data.y is not None:
            val_acc = float((pred[val_mask] == data.y[val_mask]).float().mean())
        else:
            val_acc = None

        embeddings = model.embed(data).numpy()

    return GNNResult(train_losses=losses, val_accuracy=val_acc,
                     node_embeddings=embeddings, best_epoch=epochs)


if __name__ == "__main__":
    print("GraphNeuralNetwork requires torch-geometric. Install on demand.")
    print("Usage: create_graph_data(nodes_df, edges_df, features, target)")
