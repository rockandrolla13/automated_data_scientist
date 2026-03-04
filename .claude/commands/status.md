---
name: status
description: Print experiment dashboard — all experiments, status, metrics, pending next steps.
---

Print experiment status dashboard.

## Steps
1. **Scan** — `index_experiments()` from case_bank.py. Read all experiments/*/results.json.

2. **Dashboard**
   | ID | Hypothesis | Wkfl | Iters | Result | OOS SR | t-stat | Folder |
   |---|---|---|---|---|---|---|---|

3. **Stats**
   - Total: N | CONFIRMED: N | PARTIAL: N | FAILED: N | REJECTED: N
   - Solutions saved: N (from solutions/)
   - Avg iterations: N

4. **Pending** — For each experiment with next_steps:
   - HYP-XXX: "<next step text>"

5. **Recommendations**
   - PARTIAL with next_steps → "Consider /experiment"
   - CONFIRMED not promoted → "Consider /promote"
   - No experiments → "Start with /eda then /hypothesize"
