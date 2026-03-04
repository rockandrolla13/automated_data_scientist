# Automated Data Scientist

A hypothesis-driven research framework with a two-layer architecture separating reasoning from execution.

## Architecture

```
REASONING (Brain)                    EXECUTION (Muscle)
/.claude/skills/*.md                 /scripts/*.py
────────────────────                 ────────────────────
• When to use                        • Typed functions
• Math background                    • Dataclass outputs
• Gotchas                            • Unit-testable
• Interpretation                     • Script wrapper + CONFIG
• References                         • Writes results.json
```

**54 skills** across 4 domains paired with **61 scripts**.

## Domains

| Category | Skills | Examples |
|----------|--------|----------|
| `credit_fi/` | 8 | Merton model, hazard rates, spread decomposition, OAS |
| `quant_finance/` | 9 | Backtesting, portfolio optimization, Black-Litterman |
| `ml_stats/` | 23 | GARCH, Bayesian regression, causal inference, transformers |
| `infrastructure/` | 14 | EDA, dashboards, PDF reports, slides |

## Setup

```bash
# Create conda environment
conda create -n automated-data-science python=3.12 -y
conda activate automated-data-science

# Install dependencies
pip install -r requirements.txt
```

## Research Workflow

```
EDA → HYPOTHESIZE → SPLIT → EXECUTE → LEAKAGE CHECK → EVALUATE → LOG → PROMOTE
```

Every experiment requires:
1. Written hypothesis (H₀/H₁) before any code
2. Temporal 60/20/20 split (train/val/test)
3. Mandatory leakage check before evaluation
4. Single-touch holdout policy
5. Verdict on 4 canonical metrics: OOS Sharpe, t-stat, Max Drawdown, Info Ratio

## Directory Structure

```
.
├── CLAUDE.md                    # Master instructions
├── .claude/skills/              # Reasoning layer (54 .md files)
├── scripts/                     # Execution layer (61 .py files)
├── data/                        # Datasets
├── experiments/                 # Hypothesis folders + LOG.md
├── notebooks/                   # Promoted polished notebooks
├── artifacts/                   # Reports + figures
└── docs/                        # Documentation + plans
```

## Usage

See [HOW_TO_USE.md](HOW_TO_USE.md) for detailed examples.

## Key Invariants

1. No code without falsifiable H₀/H₁
2. Every experiment updates `/experiments/LOG.md`
3. Test set touched once (violations logged)
4. Expect 40-60% OOS decay from IS Sharpe
5. n < 30 → stop and say so

## License

MIT
