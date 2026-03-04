# LargeScaleProcessing

## When to Use
- Dataset > 1GB or > 10M rows. Pandas runs out of memory.
- Lazy evaluation needed (compute only what's accessed).
- Parallelized groupby, rolling, or join operations.

## Packages
```python
import dask.dataframe as dd
import polars as pl
```

## Corresponding Script
`/scripts/infrastructure/large_scale_processing.py`
- `load_lazy(path) -> dd.DataFrame | pl.LazyFrame` — lazy load
- `rolling_stats_dask(ddf, col, window) -> dd.DataFrame` — parallel rolling
- `partition_by_date(ddf, date_col, freq) -> dict` — split into temporal chunks

## Gotchas
1. **Dask is lazy.** Nothing computes until `.compute()`. Chain operations, compute once.
2. **Polars is faster for single-machine.** Use polars for <100GB, Dask for distributed.
3. **Don't call `.compute()` on full dataset.** Always filter/aggregate first.
4. **Parquet is mandatory** for large data. Never use CSV at scale.
5. **Shuffle operations are expensive** in Dask (groupby on non-index, joins). Repartition first.

## Interpretation Guide
N/A — infrastructure skill. Success = computation completes without OOM.

## References
- Dask: https://docs.dask.org/
- Polars: https://pola.rs/
