# TimesFM

## When to Use
- Zero-shot time series forecasting (no training needed).
- Quick baseline: does a foundation model beat your hand-tuned model?
- When limited training data makes supervised approaches unreliable.

## Packages
```python
# google-research timesfm or huggingface
# pip install timesfm  (if available)
```

## Corresponding Script
`/scripts/ml_stats/timesfm.py`
- `forecast_timesfm(series, horizon) -> TimesFMResult`
- `compare_with_baseline(series, horizon, baseline_fn) -> pd.DataFrame`

## Gotchas
1. **Requires GPU for reasonable speed.** CPU inference is very slow.
2. **Context length.** TimesFM expects 512 time steps. Pad or truncate.
3. **Returns point forecasts.** No native uncertainty. Wrap with conformal prediction for intervals.
4. **Model updates.** Foundation model versions change. Pin the version.

## References
- Das et al. (2024). A decoder-only foundation model for time-series forecasting.
