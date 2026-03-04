"""lstm_forecaster — LSTM time series forecasting via PyTorch."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
import torch
import torch.nn as nn


@dataclass
class LSTMResult:
    train_losses: list[float]
    val_losses: list[float]
    best_epoch: int
    predictions: np.ndarray | None


class LSTMModel(nn.Module):
    def __init__(self, input_dim: int = 1, hidden_dim: int = 64, n_layers: int = 2,
                 output_dim: int = 1, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, n_layers, batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


def create_sequences(data: np.ndarray, lookback: int = 30) -> tuple[np.ndarray, np.ndarray]:
    """Create (X, y) pairs from sequential data. X shape: (n, lookback, features)."""
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    X, y = [], []
    for i in range(lookback, len(data)):
        X.append(data[i - lookback:i])
        y.append(data[i, 0])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def train_lstm(
    model: nn.Module,
    X_train: np.ndarray, y_train: np.ndarray,
    X_val: np.ndarray, y_val: np.ndarray,
    epochs: int = 100, lr: float = 1e-3, batch_size: int = 64,
    patience: int = 10,
) -> LSTMResult:
    """Train LSTM with early stopping."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    train_ds = torch.utils.data.TensorDataset(
        torch.tensor(X_train), torch.tensor(y_train))
    train_dl = torch.utils.data.DataLoader(train_ds, batch_size=batch_size, shuffle=False)

    X_val_t = torch.tensor(X_val).to(device)
    y_val_t = torch.tensor(y_val).to(device)

    train_losses, val_losses = [], []
    best_val, best_epoch, wait = float("inf"), 0, 0
    best_state = None

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for xb, yb in train_dl:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            pred = model(xb).squeeze()
            loss = criterion(pred, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_loss += loss.item() * len(xb)

        train_losses.append(epoch_loss / len(X_train))

        model.eval()
        with torch.no_grad():
            val_pred = model(X_val_t).squeeze()
            val_loss = criterion(val_pred, y_val_t).item()
        val_losses.append(val_loss)

        if val_loss < best_val:
            best_val = val_loss
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            wait = 0
        else:
            wait += 1
            if wait >= patience:
                break

    if best_state:
        model.load_state_dict(best_state)

    return LSTMResult(train_losses=train_losses, val_losses=val_losses,
                      best_epoch=best_epoch, predictions=None)


def forecast(model: nn.Module, last_sequence: np.ndarray, horizon: int = 10) -> np.ndarray:
    """Autoregressive multi-step forecast."""
    device = next(model.parameters()).device
    model.eval()
    seq = torch.tensor(last_sequence, dtype=torch.float32).unsqueeze(0).to(device)
    preds = []
    with torch.no_grad():
        for _ in range(horizon):
            pred = model(seq).item()
            preds.append(pred)
            new = torch.tensor([[[pred]]]).to(device)
            seq = torch.cat([seq[:, 1:, :], new], dim=1)
    return np.array(preds)


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    data = np.cumsum(rng.normal(0.001, 0.02, 500))
    X, y = create_sequences(data, lookback=30)
    split = int(len(X) * 0.8)
    model = LSTMModel(input_dim=1, hidden_dim=32, n_layers=2)
    result = train_lstm(model, X[:split], y[:split], X[split:], y[split:], epochs=50)
    print(f"Best epoch: {result.best_epoch}, Val loss: {result.val_losses[result.best_epoch]:.6f}")
