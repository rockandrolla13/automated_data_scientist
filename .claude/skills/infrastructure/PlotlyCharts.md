# PlotlyCharts

## When to Use
- Interactive charts for notebooks or dashboards.
- Candlestick charts, 3D surfaces, animated time series.
- When static matplotlib isn't sufficient (hover, zoom, drill-down).

## Packages
```python
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
```

## Corresponding Script
`/scripts/infrastructure/plotly_charts.py`
- `candlestick_chart(df, title) -> go.Figure` — OHLC with volume subplot
- `interactive_time_series(df, cols, title) -> go.Figure` — multi-line with range slider
- `heatmap_animated(data_dict, title) -> go.Figure` — animated heatmap over time
- `save_plotly(fig, path)` — save as HTML or static image

## Gotchas
1. **Plotly figures are large.** HTML exports can be 5MB+. Use `include_plotlyjs="cdn"` to reduce.
2. **Static export needs kaleido.** `pip install kaleido` for PNG/PDF export.
3. **Don't mix plotly and matplotlib** in the same notebook cell.

## Interpretation Guide
N/A — visualization utility.

## References
- Plotly: https://plotly.com/python/
