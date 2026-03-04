---
name: eda
description: Run exploratory data analysis on a dataset. Cleans data, reports stats, saves figures.
---

Run EDA on: $ARGUMENTS

## Steps
1. Read skill: .claude/skills/infrastructure/EDA.md
2. Call `scripts/infrastructure/eda.py` on the target file
3. Save cleaned output as <name>_clean.parquet in /data/
4. Report: shape, dtypes, missing%, nulls treatment, key distributions, correlation matrix
5. Save figures to experiment folder if one exists, otherwise to /artifacts/figures/
6. If data has < 30 rows: WARN insufficient sample size for most statistical tests

$ARGUMENTS is a file path (absolute or relative to repo root).
Example: /eda data/ig_spreads.csv
