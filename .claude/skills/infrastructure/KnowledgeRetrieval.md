---
name: knowledge-retrieval
description: Use before writing plan.md to retrieve relevant research papers and methods for the current hypothesis. Searches arXiv and semantic scholar for applicable techniques.
---

# Knowledge Retrieval — Research-Informed Planning

## Purpose
Before committing to a method, check what the literature says. This skill retrieves relevant papers to inform the experiment plan, preventing the agent from defaulting to the same 2-3 methods for every problem.

## When to Use
- Before writing plan.md for any hypothesis
- When the user asks "what's the best method for X?"
- When a hypothesis involves a technique the agent is uncertain about
- After CaseBank returns no matches (new territory)

## Functions (scripts/infrastructure/knowledge_retrieval.py)

### `search_papers(query, max_results=5)`
Searches arXiv API for papers matching the query. Returns title, authors, abstract, date, URL.

### `extract_method_summary(abstract)`
Extracts the key method/technique from an abstract in 1-2 sentences.

### `recommend_methods(hypothesis_text, max_results=3)`
Combines search + extraction. Returns a ranked list of relevant methods with paper references.

## Protocol
1. Write H₀/H₁.
2. Call `recommend_methods(hypothesis_text)`.
3. Review returned methods. Pick 1-2 that match the data and constraints.
4. Reference the papers in plan.md.
5. If no relevant papers found: proceed with domain knowledge from skills.

## Gotchas
- Papers propose methods. They don't validate them on YOUR data. Always run the full §4 workflow.
- Prefer methods with open-source implementations over theoretical novelties.
- Recency matters: weight papers from 2022+ higher for ML methods.
- For credit/FI-specific methods, arXiv coverage is thin. SSRN or NBER working papers may be more relevant but are not searchable via this script. Note this gap in plan.md.
