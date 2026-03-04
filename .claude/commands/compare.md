---
name: compare
description: Run Workflow B — fit multiple models on the same data, select best on validation, single-touch test.
---

Execute Workflow B (Model Comparison) for: $ARGUMENTS

## Pipeline
1. **Retrieve** — Case bank, solutions, literature.

2. **Plan** — Write plan.md:
   - H₀: No model outperforms baseline.
   - H₁: Model X outperforms on val metrics.
   - List 3-5 candidate models. For each: skill .md and script .py.
   - Shared split (§8), shared features, shared evaluation metric.

3. **STOP** — Print plan with model list. Wait for user to confirm or drop models.

4. **Execute** — For each model: read skill, call script, record 4 metrics on validation.

5. **Select** — Rank by primary metric. Print comparison table:
   | Model | Val Sharpe | Val t-stat | Val MDD | Val IR |
   Flag if top 2 within noise.

6. **Test** — Single touch with BEST validation model only.

7. **Check** — Bias/leakage checklist on winning model.

8. **Log** — results.json with all model results. README.md explains comparison.
