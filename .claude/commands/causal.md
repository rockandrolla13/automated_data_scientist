---
name: causal
description: Run Workflow C — causal investigation with effect estimation, refutation, sensitivity.
---

Execute Workflow C (Causal Investigation) for: $ARGUMENTS

## Pipeline
1. **Retrieve** — Case bank, solutions, literature for causal methods.

2. **Plan** — Write plan.md:
   - Treatment, outcome, mechanism
   - H₀: No causal effect. H₁: Measurable change.
   - Method: DiffInDiff, SyntheticControl, CausalEffect, or other
   - Confounders and instruments
   - Skills: CausalEffect.md, DiffInDiff.md, SyntheticControl.md

3. **STOP** — Print plan with DAG sketch. Wait for approval.

4. **Execute** — Estimate effect (ATE, ATT, or CATE). Report point estimate + CI.

5. **Refute** — At least 2 refutation tests:
   - Placebo treatment (random assignment)
   - Subset removal (drop 10%)
   - If DiffInDiff: parallel trends pre-treatment
   Report: does the effect survive?

6. **Sensitivity** — How large must unmeasured confounding be to nullify the effect?

7. **Check** — Bias/leakage checklist. Extra attention to treatment endogeneity, post-treatment controls, selection into treatment.

8. **Log** — results.json with effect, CI, refutation results, sensitivity bound.
