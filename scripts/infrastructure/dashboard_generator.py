"""dashboard_generator — Generate Plotly Dash applications from specs."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PanelSpec:
    title: str
    chart_type: str  # "line", "bar", "scatter", "heatmap", "table", "metric", "candlestick"
    data_col: str | list[str] = ""
    width: int = 6  # Bootstrap grid: 1-12


@dataclass
class DashboardSpec:
    title: str
    panels: list[PanelSpec]
    data_source: str
    refresh_seconds: int = 0  # 0 = no auto-refresh
    theme: str = "plotly_white"


CHART_TEMPLATES = {
    "line": """
        dcc.Graph(figure=px.line(df, y={cols}, title="{title}").update_layout(template="{theme}"))
    """,
    "bar": """
        dcc.Graph(figure=px.bar(df, y={cols}, title="{title}").update_layout(template="{theme}"))
    """,
    "scatter": """
        dcc.Graph(figure=px.scatter(df, x={cols}[0], y={cols}[1], title="{title}").update_layout(template="{theme}"))
    """,
    "heatmap": """
        dcc.Graph(figure=px.imshow(df[{cols}].corr(), title="{title}", color_continuous_scale="RdBu_r"))
    """,
    "table": """
        dash.dash_table.DataTable(data=df[{cols}].tail(20).to_dict("records"), page_size=20)
    """,
    "metric": """
        html.Div([
            html.H3("{title}"),
            html.H1(f"{{df[{cols}[0]].iloc[-1]:.4f}}")
        ], style={{"textAlign": "center", "padding": "20px"}})
    """,
}


def generate_dash_app(spec: DashboardSpec, output_path: str = "dashboard.py") -> str:
    """Generate a complete Dash app .py file from DashboardSpec."""
    panels_code = []
    for p in spec.panels:
        cols = p.data_col if isinstance(p.data_col, list) else [p.data_col]
        cols_str = str(cols)
        tmpl = CHART_TEMPLATES.get(p.chart_type, CHART_TEMPLATES["line"])
        code = tmpl.format(cols=cols_str, title=p.title, theme=spec.theme)
        panels_code.append(
            f'    html.Div([{code.strip()}], '
            f'style={{"width": "{int(p.width/12*100)}%", "display": "inline-block", "verticalAlign": "top"}})'
        )

    panels_joined = ",\n".join(panels_code)

    refresh_code = ""
    if spec.refresh_seconds > 0:
        refresh_code = f"    dcc.Interval(id='interval', interval={spec.refresh_seconds * 1000}),"

    app_code = f'''"""Auto-generated dashboard: {spec.title}"""
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

df = pd.read_parquet("{spec.data_source}")

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("{spec.title}"),
{refresh_code}
{panels_joined}
])

if __name__ == "__main__":
    app.run(debug=True, port=8050)
'''

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(app_code)
    return app_code


if __name__ == "__main__":
    spec = DashboardSpec(
        title="Example Dashboard",
        panels=[
            PanelSpec(title="Returns", chart_type="line", data_col=["close"], width=8),
            PanelSpec(title="Latest", chart_type="metric", data_col=["close"], width=4),
        ],
        data_source="../../data/prices_clean.parquet",
    )
    generate_dash_app(spec, "dashboard_output.py")
    print("Dashboard generated: dashboard_output.py")
