# How to Use

## Quick Start

### 1. Activate Environment
```bash
conda activate automated-data-science
```

### 2. Add Data
Place your dataset in `/data/`. The framework checks here first.

### 3. Run EDA (Mandatory)
```bash
python scripts/infrastructure/eda.py --input data/your_data.csv
```
Outputs: `data/your_data_clean.parquet` + EDA report.

---

## Operational Modes

### Mode A — Direct Command
You know exactly what you want.

```bash
# Fit GARCH model
python scripts/ml_stats/garch.py --input data/returns.csv

# Run backtest
python scripts/quant_finance/backtest_engine.py --signal signals.csv --prices prices.csv
```

### Mode B — Hypothesis-Driven Research
You have a high-level goal. The framework generates testable hypotheses.

1. **State goal**: "Find alpha in credit spreads"
2. **Framework proposes 5 hypotheses** with H₀/H₁, scripts, workflow tags
3. **You select** which to execute
4. **Execute** via Research Workflow

### Mode C — Scientific Brainstorm
You have a hypothesis but need refinement.

1. State hypothesis
2. Framework challenges assumptions, proposes controls
3. Converge on testable spec
4. Execute

---

## Research Workflow

```
EDA → HYPOTHESIZE → SPLIT → EXECUTE → LEAKAGE CHECK → EVALUATE → LOG → PROMOTE
```

### Step 1: EDA
```python
from scripts.infrastructure.eda import run_eda

report = run_eda("data/prices.csv")
# Creates data/prices_clean.parquet
```

### Step 2: Hypothesize
Write H₀/H₁ before any modeling code.

```
H₀: 5-day momentum in IG spreads has zero predictive power
H₁: 5-day momentum predicts 1-week excess returns (β > 0)
```

### Step 3: Split (60/20/20 temporal)
```python
T = len(df)
t1, t2 = int(T * 0.60), int(T * 0.80)
train, val, test = df.iloc[:t1], df.iloc[t1:t2], df.iloc[t2:]
```

### Step 4: Execute
```python
from scripts.ml_stats.garch import fit_garch
from scripts.quant_finance.backtest_engine import run_backtest

# Fit on train
model = fit_garch(train_returns)

# Generate signals, backtest on val
signals = generate_signals(model, val)
val_results = run_backtest(signals, val_prices)
```

### Step 5: Leakage Check (Mandatory)
- [ ] Look-ahead: no feature at t uses data > t
- [ ] Survivorship: delisted/defaulted assets included
- [ ] Transaction costs: returns survive 5bps slippage
- [ ] Selection: universe not cherry-picked post-hoc
- [ ] Stationarity: non-stationary inputs differenced

### Step 6: Evaluate (Test Set — Single Touch)
```python
# Only after val iteration is complete
test_results = run_backtest(final_signals, test_prices)
```

Report 4 canonical metrics:
```
SR=1.1 t=2.3 MDD=-3.2% IR=0.9
```

### Step 7: Log
Update `/experiments/LOG.md`:

| ID | Parent | Date | Hypothesis | Scripts | Metrics | Result | Folder |
|----|--------|------|------------|---------|---------|--------|--------|
| HYP-001 | — | 2025-03-04 | IG momentum 5d | garch.py, backtest_engine.py | SR=0.8 t=1.9 MDD=-4% IR=0.6 | PARTIAL | hyp_001_momentum |

### Step 8: Promote
- Polished notebook → `/notebooks/`
- Figures → `/artifacts/figures/`
- Reports → `/artifacts/reports/`

---

## Using Skills + Scripts

### Pattern: Read Skill, Then Call Script

1. **Read the skill** (`.claude/skills/<domain>/<Skill>.md`)
   - Understand when to use, math, gotchas

2. **Call the script** (`scripts/<domain>/<skill>.py`)
   - Typed functions with dataclass outputs
   - Script wrapper with CONFIG for CLI usage

### Example: GARCH Modeling

**Skill**: `.claude/skills/ml_stats/GARCH.md`
```markdown
## When to Use
- Volatility clustering in returns
- Risk forecasting, VaR estimation
- Conditional heteroskedasticity modeling

## Gotchas
- Returns must be ×100 for arch package
- Check Ljung-Box on squared residuals
- GARCH(1,1) often sufficient
```

**Script**: `scripts/ml_stats/garch.py`
```python
from scripts.ml_stats.garch import fit_garch, GARCHResult

result: GARCHResult = fit_garch(
    returns=df["returns"] * 100,  # ×100 per gotcha
    p=1, q=1
)
print(result.aic, result.conditional_volatility)
```

---

## Experiment Folder Structure

```
/experiments/hyp_001_spread_momentum/
├── README.md        # Hypothesis, method, results, learnings
├── notebook.ipynb   # Working notebook
├── analysis.py      # Clean script (calls /scripts/*.py)
├── results.json     # Metrics, split, parameters
├── figures/
└── notes.md         # Optional lab notes
```

### results.json
```json
{
  "hypothesis_id": "HYP-001",
  "parent": null,
  "date": "2025-03-04",
  "hypothesis": "IG spread 5d momentum predicts excess returns",
  "scripts_called": ["garch.py", "backtest_engine.py"],
  "split": {"t1": "2020-01-02", "t2": "2022-06-30"},
  "metrics": {
    "oos_sharpe": 0.82,
    "t_stat": 1.91,
    "max_drawdown": -0.043,
    "information_ratio": 0.61
  },
  "result": "PARTIAL",
  "learnings": "Works in low-vol regimes, reverses in high-vol.",
  "next_steps": ["HYP-001a: condition on vol regime"]
}
```

---

## Workflow Templates

Tag hypotheses with workflow type:

| Workflow | Pipeline | Use Case |
|----------|----------|----------|
| **A** | EDA → Features → Signal → Backtest → Evaluate → Log | Signal research |
| **B** | EDA → Fit N Models → Val Select → Test Eval → Log | Model comparison |
| **C** | EDA → DAG → Effect → Refutation → Sensitivity → Log | Causal investigation |
| **D** | Results → Figures → Report/Slides → /artifacts | Stakeholder deliverable |
| **E** | EDA → Clean → Features → Model → Diagnostics → Viz → Report | Full pipeline |

---

## Conventions

| Item | Convention |
|------|-----------|
| Seed | `42` unless testing sensitivity |
| Index | `pd.DatetimeIndex`, tz-naive, bday |
| Returns | Decimal (0.01 = 1%); ×100 for `arch` |
| Spreads | Basis points |
| Annualize | √252 |
| Figures | mpl + seaborn, PNG ≥150dpi |
| Min sample | n ≥ 30 |

---

## Common Commands

```bash
# EDA
python scripts/infrastructure/eda.py --input data/prices.csv

# GARCH
python scripts/ml_stats/garch.py --input data/returns.csv --p 1 --q 1

# Backtest
python scripts/quant_finance/backtest_engine.py \
    --signals signals.csv \
    --prices prices.csv \
    --output experiments/hyp_001/results.json

# Generate report
python scripts/infrastructure/pdf_report_generator.py \
    --experiment experiments/hyp_001/ \
    --output artifacts/reports/hyp_001_report.pdf
```
