---
name: solution-retrieval
description: Use when a known strategy pattern (momentum, carry, mean-reversion, vol regime) matches the current task. Retrieves proven recipes from solutions/ for fast-start execution.
---

# Solution Retrieval — Reuse Proven Recipes

## Purpose
When a new hypothesis matches a known pattern, skip the cold-start. Load the proven recipe from solutions/ and adapt parameters for the new asset/universe.

## When to Use
- After CaseBank retrieval finds a CONFIRMED experiment
- When the user says "do the same thing but for <new asset>"
- When /hypothesize generates a hypothesis matching a known pattern

## Functions (scripts/infrastructure/solution_retrieval.py)

### `list_solutions(solutions_dir="solutions/")`
Lists all .yaml files in solutions/.

### `load_solution(name, solutions_dir="solutions/")`
Loads a specific solution recipe by name (without .yaml extension).

### `match_solution(hypothesis_text, solutions_dir="solutions/")`
Keyword-matches hypothesis text against solution descriptions. Returns best match or None.

## Protocol
1. After writing H₀/H₁, call `match_solution(hypothesis_text)`.
2. If match found: load recipe, adapt params for new data, note "Based on solution: <name>" in plan.md.
3. If no match: proceed normally via CaseBank or from scratch.
4. After a CONFIRMED experiment: create a new solution recipe via `create_solution()`.

## Solution YAML Format
```yaml
name: spread-momentum
description: Cross-sectional spread momentum signal
origin: HYP-001a (experiments/hyp_001a_10d/)
workflow: A
scripts:
  - credit_signals.py::spread_momentum
  - signal_construction.py::zscore_normalize
  - backtest_engine.py::backtest
params:
  lookback: 10
  z_window: 60
  costs_bps: 5
metrics:
  oos_sharpe: 1.1
  t_stat: 2.3
  max_drawdown: -0.03
  information_ratio: 0.9
learnings: "Works in low-vol regimes. Condition on VIX < 20."
```

## Gotchas
- Recipes are starting points, not gospel. Always re-validate on current data.
- Params may need re-tuning if the universe or time period changed.
- Never skip the bias/leakage checklist just because the recipe was previously confirmed.
