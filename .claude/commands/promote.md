---
name: promote
description: Save a CONFIRMED experiment as a reusable solution recipe in solutions/.
---

Promote experiment: $ARGUMENTS

$ARGUMENTS is a hypothesis ID (e.g., HYP-001a) or experiment folder name.

## Steps
1. **Load** — Read experiments/<folder>/results.json
   - CONFIRMED or PARTIAL: proceed (warn if PARTIAL)
   - FAILED/REJECTED/not found: STOP with error

2. **Extract** from results.json + plan.md:
   - hypothesis → description
   - scripts_called → scripts (with functions if in plan.md)
   - final iteration params → params
   - test_metrics → metrics
   - learnings → learnings
   - workflow tag → workflow

3. **Name** — kebab-case from slug. E.g. hyp_001a_10d → spread-momentum-10d

4. **Preview** — Print full YAML. Ask: "Save to solutions/<name>.yaml?"

5. **Save** — `create_solution()` from solution_retrieval.py

6. **Confirm** — "Solution saved. Future /retrieve calls will find this recipe."
