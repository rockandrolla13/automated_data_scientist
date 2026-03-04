---
name: retrieve
description: Run pre-planning retrieval — case bank, solution recipes, and literature. Planning only, no execution.
---

Run pre-planning retrieval for: $ARGUMENTS

## Steps
1. **Case Bank** — `retrieve_similar("$ARGUMENTS", top_k=3)` from case_bank.py
   - For each match: hypothesis, result, metrics, learnings, folder
   - If similarity > 0.3 and CONFIRMED/PARTIAL: recommend adapting

2. **Solutions** — `match_solution("$ARGUMENTS")` from solution_retrieval.py
   - If match: print full recipe (scripts, params, metrics, learnings)

3. **Literature** — `recommend_methods("$ARGUMENTS", max_results=3)` from knowledge_retrieval.py
   - For each paper: title, date, method summary, URL

4. **Summary**
   | Source | Found? | Recommendation |
   |--------|--------|---------------|
   | Case Bank | X matches | Adapt HYP-XXX / Start fresh |
   | Solutions | Yes/No | Use recipe X / No match |
   | Literature | X papers | Consider method Y / Nothing new |

5. **STOP** — Do not execute anything. Print: "Run /signal, /compare, /causal, or /experiment to proceed."
