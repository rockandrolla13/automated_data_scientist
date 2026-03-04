# DashboardGenerator

## When to Use
- Interactive multi-panel dashboards for monitoring or exploration.
- Combining multiple skill outputs (regime detection + PnL + risk) in one view.
- Stakeholder-facing live apps.

## Packages
```python
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
```
Alternative: `panel` for Jupyter-native dashboards.

## Corresponding Script
`/scripts/infrastructure/dashboard_generator.py`
- `generate_dash_app(spec) -> str` — generates a complete Dash `.py` file from a DashboardSpec
- `DashboardSpec` — dataclass: title, panels list, data_source, refresh_seconds
- `PanelSpec` — dataclass: title, chart_type, data_col, width

## Gotchas
1. **Dash runs a Flask server.** Port conflicts if running multiple. Use `port=` param.
2. **Callbacks are server-side.** Heavy computation in callbacks will block. Pre-compute and cache.
3. **Panel is lighter** for quick Jupyter prototyping. Use Dash for production.
4. **Don't put model fitting inside callbacks.** Load pre-computed results from `/experiments/`.

## Interpretation Guide
N/A — generator skill. Success = runnable `python dashboard.py` that opens in browser.

## References
- Dash: https://dash.plotly.com/
- Panel: https://panel.holoviz.org/
