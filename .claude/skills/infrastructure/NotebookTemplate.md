# NotebookTemplate

## When to Use
- Generating executable Jupyter notebooks from experiment specs.
- Promoting working notebooks to polished `/notebooks/` versions.
- Creating stakeholder-friendly notebooks with narrative between code.

## Packages
```python
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
```

## Corresponding Script
`/scripts/infrastructure/notebook_template.py`
- `generate_notebook(spec) -> nbformat.NotebookNode` — build notebook from spec
- `NotebookSpec` — dataclass: title, hypothesis_id, skills, data_source, sections
- `save_notebook(nb, path)` — write `.ipynb`

## Gotchas
1. **Notebooks are JSON.** Don't manually edit `.ipynb` — use `nbformat`.
2. **Kernel name matters.** Set `kernelspec` metadata to match the venv.
3. **Markdown cells between code** are critical for readability. Always alternate.
4. **Don't embed large outputs.** Clear outputs before committing notebooks.

## Interpretation Guide
N/A — generator. Success = notebook opens and runs cleanly in Jupyter.

## References
- nbformat: https://nbformat.readthedocs.io/
