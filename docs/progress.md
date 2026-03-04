# Project Setup Progress

**Date:** 2026-03-03
**Repo:** https://github.com/rockandrolla13/automated_data_scientist

---

## Completed Tasks

### 1. Directory Structure Created (per CLAUDE.md §2)

```
.
├── CLAUDE.md                       # Master instructions
├── .gitignore                      # Python/Jupyter/IDE exclusions
├── requirements.txt                # Categorized dependencies
├── auto-data-science/              # Python 3.12.7 virtual environment
│
├── docs/
│   └── plans/                      # Task plans (YYYY-MM-DD-<n>.md)
│
├── .claude/skills/                 # REASONING layer (54 .md files)
│   ├── credit_fi/                  # 8 skills
│   ├── quant_finance/              # 9 skills
│   ├── ml_stats/                   # 23 skills
│   └── infrastructure/             # 14 skills
│
├── scripts/                        # EXECUTION layer (54 .py files)
│   ├── credit_fi/                  # 8 scripts
│   ├── quant_finance/              # 9 scripts
│   ├── ml_stats/                   # 23 scripts
│   └── infrastructure/             # 14 scripts
│
├── data/                           # Datasets
├── experiments/
│   └── LOG.md                      # Audit trail
├── notebooks/                      # Polished notebooks only
└── artifacts/
    ├── reports/
    └── figures/
```

### 2. Skills & Scripts Created (54 pairs)

| Category | Skills |
|----------|--------|
| **credit_fi** | MertonModel, HazardRateBootstrap, SpreadDecomposition, NelsonSiegel, BondAnalytics, OASCalculator, ETFPremiumDiscount, TransitionMatrix |
| **quant_finance** | BacktestEngine, Vectorbt, SignalConstruction, PortfolioOptimizer, RiskParity, BlackLitterman, LiquidityScorer, OpenBB, CreditSignals |
| **ml_stats** | GARCH, ARIMA, RegimeDetection, LSTMForecaster, TimesFM, TransformerForecaster, SHAPExplainer, ConformalPrediction, BayesianRegression, CausalEffect, DiffInDiff, SyntheticControl, HypothesisTesting, Clustering, PCA, AnomalyDetection, GaussianProcess, BayesianABTest, PowerAnalysis, SymbolicMath, GraphNeuralNetwork, ReinforcementLearning, NetworkAnalysis |
| **infrastructure** | EDA, PublicationFigures, DashboardGenerator, NotebookTemplate, PyZotero, DataLoading, LargeScaleProcessing, PlotlyCharts, ImageGeneration, PDFReportGenerator, GraphicalAbstracts, StakeholderNotebooks, SlideGenerator, Workflows |

Each `.md` skill has template sections: When to Use, Packages, Math, Corresponding Script, Gotchas, Interpretation, References.

Each `.py` script has: typed dataclass result, main function stub, CONFIG dict, `if __name__` wrapper writing `results.json`.

### 3. Experiment Log Created

`experiments/LOG.md` with schema:

| ID | Parent | Date | Hypothesis | Scripts | Metrics | Result | Folder |
|----|--------|------|------------|---------|---------|--------|--------|

### 4. Virtual Environment & Dependencies

- **Python:** 3.12.7
- **Location:** `auto-data-science/`
- **Activation:** `source auto-data-science/bin/activate`
- **Packages:** 308 installed

#### requirements.txt Structure

| Section | Key Packages |
|---------|--------------|
| Core | numpy, pandas, scipy, pydantic |
| credit_fi | *(uses core)* |
| quant_finance | vectorbt, cvxpy, pyportfolioopt, empyrical-reloaded |
| ml_stats - Classical | arch, statsmodels, sklearn, hmmlearn, pingouin |
| ml_stats - Conformal | mapie |
| ml_stats - Bayesian | pymc, arviz, bambi |
| ml_stats - Causal | dowhy, econml |
| ml_stats - DL | torch, pytorch-forecasting, lightning, darts |
| ml_stats - Graph | networkx, torch-geometric |
| ml_stats - RL | stable-baselines3, gymnasium |
| ml_stats - Symbolic | sympy |
| infrastructure | matplotlib, seaborn, plotly, dash, pyzotero, nbformat, python-pptx, pdfplumber |
| dev | pytest, mypy, ruff, jupyterlab |

#### Package Fixes for Python 3.12

- `pypfopt` → `pyportfolioopt` (correct PyPI name)
- `empyrical` → `empyrical-reloaded` (Py3.12 compatible fork)

---

## Git Commits

1. `93851ee` - Initialize hypothesis-driven data science framework
2. `3237f22` - Add requirements.txt and .gitignore
3. `fc189f8` - Fix package names for Python 3.12 compatibility

---

## Next Steps

- [ ] Flesh out individual skill `.md` files with actual content
- [ ] Implement script `.py` stubs with working code
- [ ] Add sample data to `/data/`
- [ ] Run first hypothesis experiment
