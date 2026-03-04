---
name: review
description: Run the 8-point bias and leakage checklist on an experiment. Reports PASS/FAIL with evidence.
---

Review experiment: $ARGUMENTS

$ARGUMENTS is a hypothesis ID or experiment folder name. If omitted, review the most recent experiment.

## Checklist
Read the experiment's results.json, plan.md, and analysis.py. Evaluate each item:

1. **Look-ahead bias** — No feature at time t uses data from time > t.
   Check: inspect feature construction code for future values, joins on future dates, or unstacked pivots.

2. **Survivorship bias** — Delisted, defaulted, or downgraded assets included or explicitly noted.
   Check: does the universe include dead names? Is there a note about survivorship?

3. **Transaction costs** — Returns survive ≥ 5bps slippage per trade.
   Check: is costs_bps set in backtest config? What's the net Sharpe vs gross?

4. **Selection bias** — Universe not cherry-picked post-hoc.
   Check: was the asset universe defined before seeing results?

5. **Stationarity** — Non-stationary inputs differenced or flagged.
   Check: are raw price levels used as features? Any ADF/KPSS tests run?

6. **Temporal split** — 60/20/20 temporal, no shuffling, boundaries logged.
   Check: split boundaries in results.json. Any random_state in split code?

7. **OOS decay** — Test performance within expected 40-60% decay of validation.
   Check: compare val_metrics to test_metrics. Flag if test > val (suspicious).

8. **Iteration discipline** — Max 3 validation iterations. Test touched exactly once.
   Check: iterations array length ≤ 3. test_metrics populated exactly once.

## Output
Print a table:

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Look-ahead | PASS/FAIL | <one line> |
| ... | ... | ... | ... |

Score: X/8 passed.
If any FAIL: explain what's wrong and suggest the fix.
