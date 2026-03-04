---
name: signal
description: Run Workflow A — full signal research pipeline from hypothesis to logged result.
---

Execute Workflow A (Signal Research) for: $ARGUMENTS

## Pipeline
1. **Retrieve** — Run pre-planning retrieval per §4 step 2b:
   - `retrieve_similar("$ARGUMENTS")` from case_bank.py
   - `match_solution("$ARGUMENTS")` from solution_retrieval.py
   - `recommend_methods("$ARGUMENTS")` from knowledge_retrieval.py
   - Summarize findings.

2. **Plan** — Write plan.md:
   - H₀/H₁
   - Steps: data loading → feature construction → signal construction → backtest → evaluate
   - Name specific scripts from scripts/quant_finance/ and scripts/ml_stats/
   - Reference retrieved cases, solutions, or papers
   - Tag: (Workflow A)

3. **STOP** — Print plan. Wait for user approval.

4. **Execute** — Split per §8. Construct features and signal. Backtest via backtest_engine.py with costs ≥ 5bps. Compute 4 canonical metrics on validation.

5. **Revise** — Per §4 step 6b. Max 3 iterations. Diagnose, propose, re-execute.

6. **Test** — Single touch. 4 metrics. Val-to-test decay.

7. **Check** — Bias/leakage checklist (§4 step 5). All 5 items. PASS/FAIL.

8. **Log** — results.json with iteration history. LOG.md. README.md.

9. **Promote** — If CONFIRMED: "Save as reusable solution recipe? Run /promote <id>"
