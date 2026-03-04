"""notebook_template — Generate Jupyter notebooks from specs."""

from dataclasses import dataclass, field
from pathlib import Path
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell


@dataclass
class NotebookSpec:
    title: str
    hypothesis_id: str
    skills: list[str]
    data_source: str
    parameters: dict = field(default_factory=dict)


def generate_notebook(spec: NotebookSpec) -> nbformat.NotebookNode:
    """Build executable notebook from spec."""
    nb = new_notebook()
    cells = []

    # Title
    cells.append(new_markdown_cell(
        f"# {spec.title}\n\n"
        f"**Hypothesis:** {spec.hypothesis_id}\n\n"
        f"**Skills:** {', '.join(spec.skills)}\n\n"
        f"**Data:** `{spec.data_source}`"
    ))

    # Imports
    imports = [
        "import numpy as np",
        "import pandas as pd",
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        "import sys; sys.path.insert(0, '../../scripts')",
    ]
    cells.append(new_code_cell("\n".join(imports)))

    # Config
    config_code = (
        f"CONFIG = {{\n"
        f'    "hypothesis_id": "{spec.hypothesis_id}",\n'
        f'    "data_source": "{spec.data_source}",\n'
        f'    "random_seed": 42,\n'
        f"}}\nnp.random.seed(CONFIG['random_seed'])"
    )
    cells.append(new_code_cell(config_code))

    # Data loading
    cells.append(new_markdown_cell("## Data Loading"))
    ext = Path(spec.data_source).suffix
    if ext == ".parquet":
        cells.append(new_code_cell(f'df = pd.read_parquet(CONFIG["data_source"])\ndf.head()'))
    else:
        cells.append(new_code_cell(f'df = pd.read_csv(CONFIG["data_source"], index_col=0, parse_dates=True)\ndf.head()'))

    # Canonical split
    cells.append(new_markdown_cell("## Train / Val / Test Split (60/20/20)"))
    cells.append(new_code_cell(
        "T = len(df)\n"
        "t1, t2 = int(T * 0.60), int(T * 0.80)\n"
        "train, val, test = df.iloc[:t1], df.iloc[t1:t2], df.iloc[t2:]\n"
        'print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")'
    ))

    # Skill sections
    for skill in spec.skills:
        cells.append(new_markdown_cell(f"## {skill}"))
        cells.append(new_code_cell(f"# TODO: apply {skill} — see /.claude/skills/ for template"))

    # Results
    cells.append(new_markdown_cell("## Results & Metrics"))
    cells.append(new_code_cell(
        "results = {\n"
        f'    "hypothesis_id": "{spec.hypothesis_id}",\n'
        '    "metrics": {\n'
        '        "oos_sharpe": None,\n'
        '        "t_stat": None,\n'
        '        "max_drawdown": None,\n'
        '        "information_ratio": None,\n'
        "    },\n"
        '    "result": "IN PROGRESS",\n'
        "}\nresults"
    ))

    nb.cells = cells
    nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    return nb


def save_notebook(nb: nbformat.NotebookNode, path: str) -> None:
    """Write notebook to disk."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        nbformat.write(nb, f)


if __name__ == "__main__":
    spec = NotebookSpec(
        title="IG Spread Momentum",
        hypothesis_id="HYP-001",
        skills=["EDA", "GARCH", "BacktestEngine"],
        data_source="../../data/ig_spreads_clean.parquet",
    )
    nb = generate_notebook(spec)
    save_notebook(nb, "../../notebooks/hyp_001_momentum.ipynb")
    print("Notebook generated.")
