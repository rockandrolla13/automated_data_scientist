# StakeholderNotebooks

## When to Use
- Non-technical audience needs to see results.
- Executive summaries with charts but minimal code.
- Databricks/Jupyter notebooks optimized for presentation (hide code, show outputs).

## Packages
```python
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
```

## Corresponding Script
`/scripts/infrastructure/stakeholder_notebooks.py`
- `generate_stakeholder_notebook(spec) -> nbformat.NotebookNode` — narrative-heavy, code-light
- Inherits from NotebookTemplate but: hides code cells, adds executive summary, simplifies metrics

## Gotchas
1. **Hide code in Jupyter.** Add `"tags": ["hide-input"]` to cell metadata, use `nbconvert` with `--TagRemovePreprocessor.remove_input_tags=hide-input`.
2. **Charts > tables.** Stakeholders read charts. Convert tabular results to plots.
3. **No jargon.** Replace "OOS Sharpe" with "risk-adjusted return" in markdown cells.
4. **One key takeaway per section.** Bold it.

## Interpretation Guide
N/A — communication output.

## References
- nbconvert tags: https://nbconvert.readthedocs.io/
