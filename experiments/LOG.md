# Experiment Log

Audit trail for all experiments. Every hypothesis execution must add a row.

## Schema

| ID | Parent | Date | Hypothesis | Scripts | Metrics | Result | Folder |
|----|--------|------|------------|---------|---------|--------|--------|

## Legend

- **ID**: `HYP-NNN` format. Sub-experiments: `HYP-001a`, `HYP-001b`. Max depth 3.
- **Parent**: Parent hypothesis ID or `—` for root.
- **Date**: YYYY-MM-DD
- **Hypothesis**: Brief statement of H₀/H₁
- **Scripts**: Comma-separated list of scripts called
- **Metrics**: `SR=X.X t=X.X MDD=-X.X% IR=X.X` + optional task-specific
- **Result**: `CONFIRMED` | `REFUTED` | `PARTIAL` | `INCONCLUSIVE`
- **Folder**: Relative path under `/experiments/`

## Entries

| ID | Parent | Date | Hypothesis | Scripts | Metrics | Result | Folder |
|----|--------|------|------------|---------|---------|--------|--------|
<!-- Add entries below this line -->
