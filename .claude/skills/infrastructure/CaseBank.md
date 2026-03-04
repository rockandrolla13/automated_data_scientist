---
name: case-bank
description: Use before planning a new experiment to retrieve similar past experiments. Surfaces prior successes, failures, and learnings to avoid repeating mistakes.
---

# CaseBank — Learn from Past Experiments

## Purpose
Before starting a new hypothesis, check what you've already tried. CaseBank indexes all experiments in `/experiments/` and retrieves the most similar ones based on hypothesis text, scripts used, and learnings.

## When to Use
- Before writing plan.md for any hypothesis (step 2b in §4)
- When the user asks "have we tried X before?"
- After a FAILED experiment to find similar past failures and their diagnoses
- When looking for prior art to adapt rather than starting from scratch

## Functions (scripts/infrastructure/case_bank.py)

### `index_experiments(experiments_dir="experiments/")`
Scans all experiment folders and builds an index from their results.json files. Returns a list of ExperimentCase dataclasses.

### `retrieve_similar(hypothesis_text, experiments_dir="experiments/", top_k=3, min_score=0.3)`
Finds the top-k most similar past experiments using TF-IDF similarity on hypothesis text + learnings. Returns matches with similarity scores.

### `format_case(case)`
Formats an ExperimentCase for display: hypothesis, result, metrics, learnings.

## Protocol
1. After writing H₀/H₁, call `retrieve_similar(hypothesis_text)`.
2. If matches found with score ≥ 0.3:
   - Review their results (CONFIRMED/PARTIAL/FAILED)
   - Adapt their approach if CONFIRMED
   - Avoid their mistakes if FAILED
   - Note "Based on: HYP-XXX" in plan.md
3. If no matches or all below threshold: note "No prior art" and proceed.

## ExperimentCase Fields
```python
@dataclass
class ExperimentCase:
    hypothesis_id: str
    hypothesis: str
    scripts: list[str]
    result: str  # CONFIRMED, PARTIAL, FAILED
    metrics: dict
    learnings: str
    folder: str
```

## Gotchas
- CaseBank only indexes experiments with valid results.json files.
- Similarity is text-based. Two experiments using different words for the same concept may not match.
- A high match score doesn't mean the prior approach is correct—it was just similar.
- Always verify that prior learnings still apply to current data/universe.
