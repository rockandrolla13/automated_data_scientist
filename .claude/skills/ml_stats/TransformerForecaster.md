# TransformerForecaster

## When to Use
- Multi-variate time series forecasting with attention mechanisms.
- When you need interpretable attention weights (which lags matter).
- Temporal Fusion Transformer (TFT) for mixed static + temporal features.

## Packages
```python
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
# or custom transformer via torch
```

## Corresponding Script
`/scripts/ml_stats/transformer_forecaster.py`
- `build_tft(dataset_params) -> TemporalFusionTransformer`
- `train_tft(model, train_dl, val_dl, epochs) -> TransformerResult`
- `interpret_attention(model, dataloader) -> pd.DataFrame`

## Gotchas
1. **Data format is strict.** pytorch_forecasting requires specific DataFrame structure with time_idx, group_ids.
2. **Slow to train.** Use GPU. Reduce hidden_size for prototyping.
3. **Overfits easily on small data.** Need >1000 time steps per group.
4. **Attention ≠ importance.** Attention weights are descriptive, not causal.

## References
- Lim et al. (2021). Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting.
