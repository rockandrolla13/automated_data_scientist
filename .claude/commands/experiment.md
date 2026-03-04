---
name: experiment
description: Execute a hypothesis end-to-end per §4 workflow. Creates folder, runs plan, iterates, logs.
---

Execute experiment: $ARGUMENTS

$ARGUMENTS is a hypothesis ID (e.g., HYP-001) or a short description for a new hypothesis.

## Steps
1. **Folder** — Create /experiments/<hyp_id>_<slug>/

2. **Retrieve** — Per §4 step 2b:
   - Case bank → adapt if match found
   - Solutions → load recipe if pattern matches
   - Literature → surface relevant methods

3. **Plan** — Write plan.md per §9 template:
   - H₀/H₁, numbered steps, scripts, skill references, expected outcome
   - Print plan. **STOP.** Wait for user approval.

4. **Split** — Per §8: 60/20/20 temporal. Log boundaries to results.json. Test sealed.

5. **Execute** — Call scripts per plan. Save outputs to experiment folder.

6. **Check** — Run bias/leakage checklist (§4 step 5). All 5 items. Print PASS/FAIL per item.
   - If any FAIL: STOP. Report which item failed and why. Ask user whether to proceed.

7. **Evaluate** — 4 canonical metrics on validation (§7).

8. **Revise** — Per §4 step 6b (max 3 iterations on validation):
   - If below Moderate: diagnose, propose changes, re-execute
   - Log each iteration in results.json

9. **Test** — Single touch. Compute 4 metrics. Calculate val-to-test decay.

10. **Log** — Write results.json (full iteration history), README.md, update LOG.md.

11. **Classify** — CONFIRMED / PARTIAL / REJECTED / FAILED per §7 thresholds.
    - If CONFIRMED: suggest /promote
