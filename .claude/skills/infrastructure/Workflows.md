# Workflows

## When to Use
- Starting any multi-step experiment. Match task to a template before improvising.
- Mode B (Agentic): tag each hypothesis with its workflow letter.
- Novel workflow needed: compose freely but document the new pattern in the experiment README.

## Packages
No packages — this is a pure reasoning skill. It orchestrates calls to other skills/scripts.

## Corresponding Script
`/scripts/infrastructure/workflows.py`
- `get_workflow(name) -> WorkflowSpec` — returns step list for a named workflow
- `validate_workflow(experiment_dir) -> list[str]` — checks experiment folder has all expected artifacts
- `WorkflowSpec` — dataclass: name, steps, required_scripts, required_outputs

## Defined Workflows

### A — Signal Research (most common)
```
EDA → Feature Engineering → Signal Construction → Backtest → Evaluate → Log
```
**Required scripts:** `eda.py`, `signal_construction.py`, `backtest_engine.py`
**Required outputs:** `results.json`, at least 1 figure, `README.md`
**Use when:** Testing whether a quantitative signal (momentum, mean-reversion, carry) has predictive power.

### B — Model Comparison
```
EDA → Fit N Models → Cross-Validate on Val → Select Best → Test-Set Evaluation → Log
```
**Required scripts:** (model-specific), `hypothesis_testing.py`
**Required outputs:** `results.json` with all model results, comparison table figure
**Use when:** Comparing multiple models on the same target (e.g., GARCH vs EGARCH vs GJR).

### C — Causal Investigation
```
EDA → DAG Specification → Estimate Effect → Refutation Tests → Sensitivity Analysis → Log
```
**Required scripts:** `causal_effect.py`, and at least one of `diff_in_diff.py`, `synthetic_control.py`
**Required outputs:** `results.json`, DAG diagram, refutation p-values
**Use when:** Estimating causal impact of a policy change, event, or structural break.

### D — Stakeholder Deliverable
```
Load Results → Generate Figures → Build Report/Slides/Notebook → Promote to /artifacts
```
**Required scripts:** `publication_figures.py`, and at least one of `pdf_report_generator.py`, `slide_generator.py`, `stakeholder_notebooks.py`
**Required outputs:** file in `/artifacts/reports/` or `/artifacts/figures/`
**Use when:** Packaging completed experiment results for a non-technical audience.

### E — Full Pipeline (start-to-finish)
```
EDA → Clean → Features → Model → Diagnostics → Visualization → Report
```
**Required scripts:** `eda.py`, `data_loading.py`, (model-specific), `publication_figures.py`
**Required outputs:** clean data in `/data/`, full experiment folder, promoted notebook
**Use when:** End-to-end analysis from raw data to final report. Combines A + D.

## Gotchas
1. **Don't skip EDA.** Every workflow starts with EDA if no clean data exists.
2. **Don't invent workflows for simple tasks.** Mode A (deterministic) doesn't need a workflow tag.
3. **Novel workflows are fine** — just document the new pattern in the experiment README so it can become a template later.
4. **Workflow ≠ pipeline.** Workflows are decision frameworks, not rigid scripts. Steps can be revisited.

## Interpretation Guide
| Workflow | Typical experiments per project | Complexity |
|----------|-------------------------------|------------|
| A | 5–20 | Medium |
| B | 2–5 | Medium |
| C | 1–3 | High |
| D | 1 per deliverable | Low |
| E | 1–2 | High |

## References
- Internal: see CLAUDE.md §4 (Research Workflow) and §10 (Workflow Templates)
