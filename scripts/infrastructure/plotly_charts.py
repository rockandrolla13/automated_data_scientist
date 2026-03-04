"""plotly_charts — Interactive Plotly visualizations."""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path


def interactive_time_series(
    df: pd.DataFrame,
    cols: list[str] | None = None,
    title: str = "",
) -> go.Figure:
    """Multi-line interactive time series with range slider."""
    cols = cols or list(df.select_dtypes(include=[np.number]).columns)
    fig = go.Figure()
    for col in cols:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, mode="lines"))
    fig.update_layout(
        title=title, xaxis=dict(rangeslider=dict(visible=True)),
        template="plotly_white", height=500,
    )
    return fig


def candlestick_chart(
    df: pd.DataFrame,
    open_col: str = "open", high_col: str = "high",
    low_col: str = "low", close_col: str = "close",
    volume_col: str | None = "volume",
    title: str = "",
) -> go.Figure:
    """OHLC candlestick with optional volume subplot."""
    rows = 2 if volume_col and volume_col in df.columns else 1
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3] if rows == 2 else [1],
                        vertical_spacing=0.05)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df[open_col], high=df[high_col],
        low=df[low_col], close=df[close_col], name="OHLC",
    ), row=1, col=1)

    if rows == 2:
        fig.add_trace(go.Bar(x=df.index, y=df[volume_col], name="Volume",
                             marker_color="steelblue", opacity=0.5), row=2, col=1)

    fig.update_layout(title=title, template="plotly_white",
                      xaxis_rangeslider_visible=False, height=600)
    return fig


def heatmap_chart(
    matrix: pd.DataFrame,
    title: str = "",
    colorscale: str = "RdBu_r",
) -> go.Figure:
    """Interactive heatmap (correlation, transition, etc.)."""
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values, x=matrix.columns, y=matrix.index,
        colorscale=colorscale, zmid=0,
        text=np.round(matrix.values, 2), texttemplate="%{text}",
    ))
    fig.update_layout(title=title, template="plotly_white", height=600, width=700)
    return fig


def save_plotly(fig: go.Figure, path: str, as_html: bool = True) -> None:
    """Save as HTML (default) or static image (needs kaleido)."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if as_html or path.endswith(".html"):
        fig.write_html(path, include_plotlyjs="cdn")
    else:
        fig.write_image(path)


if __name__ == "__main__":
    df = pd.read_parquet("../../data/returns_clean.parquet")
    fig = interactive_time_series(df, title="Returns")
    save_plotly(fig, "figures/interactive_returns.html")
