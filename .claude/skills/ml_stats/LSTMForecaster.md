# LSTMForecaster

## When to Use
- Sequence-to-one or sequence-to-sequence time series forecasting.
- When temporal dependencies span many lags (>20).
- Baseline deep learning model before trying transformers.

## Packages
```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
```

## Corresponding Script
`/scripts/ml_stats/lstm_forecaster.py`
- `build_lstm(input_dim, hidden_dim, n_layers, output_dim) -> nn.Module`
- `create_sequences(data, lookback) -> tuple[np.ndarray, np.ndarray]`
- `train_lstm(model, train_loader, val_loader, epochs, lr) -> LSTMResult`
- `forecast(model, last_sequence, horizon) -> np.ndarray`

## Gotchas
1. **Normalize inputs.** LSTM is sensitive to scale. StandardScaler on train, apply to val/test.
2. **Lookback window matters.** Too short = underfitting. Too long = slow + overfitting. Try 20–60.
3. **Gradient clipping.** Use `clip_grad_norm_(model.parameters(), 1.0)` to prevent explosion.
4. **Don't shuffle time series.** Use sequential batches or walk-forward.
5. **Overfit risk.** Use dropout (0.2) and early stopping on validation loss.

## References
- Hochreiter & Schmidhuber (1997). Long Short-Term Memory.
