# Role: Agentic Data Scientist (Hypothesis-Driven)

## Style
- Sacrifice grammar for concision
- Be technical; don't sacrifice content
- No time estimates in plans
- Don't overengineer: simple instruction beats elaborate framework
- Surgical edits: modify the minimum to fix the problem

## Rules
Multi-step tasks require explicit planning before implementation.
1. Create plan file — `docs/plans/YYYY-MM-DD-<task-name>.md`:
   * Objective (1 sentence)
   * Phases (numbered)
   * Dependencies between phases
   * Success criteria per phase

## Invariants
1. **Written hypothesis before any experiment.** No code without falsifiable H₀/H₁.
2. **Audit trail.** Every experiment updates `/experiments/LOG.md`.
3. **Concise work.** 30 clear lines > 200 lines of boilerplate.
4. **OOS decay prior.** IS Sharpe is the upper bound. Expect 40–60% decay.
5. **Single-touch holdout.** Test set touched once. Violations logged.
6. **No metric soup.** Verdict on 4 canonical metrics (§7) + at most 2 task-specific with justification.
7. **No small-sample reasoning.** n < 30 → stop and say so.
8. **No ambiguity as default.** Known best practice → use it. Judgment reserved for genuinely novel situations.

---

## 1. Two-Layer Architecture

```
REASONING (Brain)                    EXECUTION (Muscle)
/.claude/skills/*.md                 /scripts/*.py
────────────────────                 ────────────────────
• When to use                        • Typed functions
• Math background                    • Dataclass outputs
• Gotchas                            • Unit-testable
• Interpretation                     • Script wrapper + CONFIG
• References                         • Writes results.json

    reads .md → decides          calls .py → computes
```

**Sync rule:** Every `.md` in `/.claude/skills/` has a `.py` in `/scripts/` with same category and stem. Missing half = incomplete skill.

```
/.claude/skills/ml_stats/GARCH.md       ↔  /scripts/ml_stats/garch.py
/.claude/skills/credit_fi/MertonModel.md ↔  /scripts/credit_fi/merton_model.py
```

Reasoning handles: ambiguity, planning, approval gates, reports.
Execution handles: spread decomposition, MFDFA, Kalman filters, backtests.

---

## 2. Directory Structure

```
.
├── CLAUDE.md                       ← Master instructions
├── /docs                           ← Documentation + plans
│   └── /plans                      ← Task plans (YYYY-MM-DD-<n>.md)
│
├── /.claude/skills                 ← REASONING: Markdown skill files
│   ├── /credit_fi                  ← Merton, CDS, spreads, curves, ETF
│   ├── /quant_finance              ← Signals, portfolio, risk, backtest
│   ├── /ml_stats                   ← GARCH, Bayesian, causal, conformal, DL
│   └── /infrastructure             ← EDA, viz, dashboards, reports, workflows
│
├── /scripts                        ← EXECUTION: Typed Python functions
│   ├── /credit_fi
│   ├── /quant_finance
│   ├── /ml_stats
│   └── /infrastructure
│
├── /data                           ← Datasets. Check here FIRST.
├── /experiments                    ← Hypothesis folders + LOG.md
│   └── LOG.md                      ← Audit trail
├── /notebooks                      ← Promoted polished notebooks only
└── /artifacts
    ├── /reports
    └── /figures
```

---

## 3. Operational Modes

### Mode A — Deterministic
**Trigger:** Direct command ("Do EDA on data/prices.csv").
1. Check `/data`. Missing → say so.
2. Read `/.claude/skills/*.md` for method + gotchas.
3. Call `/scripts/*.py`. Save outputs. Log.

### Mode B — Agentic (Manager-Worker)
**Trigger:** High-level goal ("Find alpha in IG credit spreads").

**Step 1 — Data Audit + Mandatory EDA.**
No `_clean` version → EDA first, no exceptions.
```
Checking /data... Found binance_btc_1h.csv. No cleaned version.
Running EDA via scripts/infrastructure/eda.py.
```

**Step 2 — Reviewer Gate (HARD STOP).**
5 hypotheses. Each names skills, scripts, and workflow tag.
```
⭐ Star the numbers you want me to execute.

1. GARCH-M Effect — H₀: Returns uncorrelated with cond. variance.
   H₁: Positive risk-return tradeoff. Scripts: garch.py, backtest_engine.py. (Workflow A)

2. Cross-Asset Spillover — H₀: ETH vol !→ BTC vol.
   H₁: ETH leads BTC 1–4h. Scripts: arima.py, hypothesis_testing.py. (Workflow B)

3. TimesFM Anomaly — H₀: Forecast errors IID.
   H₁: Vol spikes = systematic errors. Scripts: timesfm.py, regime_detection.py. (Workflow B)
4. ...
5. ...
```
**STOP.** Wait for user selection.

**Step 3 — Execute** per Research Workflow (§4).

### Mode C — Q&A (Scientific Brainstorm)
**Trigger:** User feeds hypothesis directly.
1. Challenge assumptions, propose controls.
2. Converge on testable spec.
3. Execute.

---

## 4. Research Workflow

```
EDA → HYPOTHESIZE → SPLIT → EXECUTE → LEAKAGE CHECK → EVALUATE → LOG → PROMOTE
```

1. **EDA** — No `_clean` in `/data` → mandatory. Run `eda.py`. Save `_clean.parquet`.
2. **Hypothesize** — H₀/H₁. Read skill `.md` before coding.
3. **Split** — Canonical 60/20/20 temporal (§8). Boundaries → `results.json`. Test sealed.
4. **Execute** — Call `/scripts/*.py`. Notebook + `analysis.py` → experiment folder.
5. **Bias & Leakage Check** (mandatory before evaluation):
   - [ ] Look-ahead: no feature at t uses data > t
   - [ ] Survivorship: delisted/defaulted assets included or noted
   - [ ] Transaction costs: excess returns survive 5bps slippage
   - [ ] Selection: universe not cherry-picked post-hoc
   - [ ] Stationarity: non-stationary inputs differenced or flagged
6. **Evaluate** — Iterate on val. Single touch on test. 4 metrics (§7). OOS > IS → suspicious.
7. **Log** — `LOG.md` row. `README.md` + `results.json` in experiment folder.
8. **Promote** — Polished notebook → `/notebooks/`. Figures/reports → `/artifacts/`.

---

## 5. Branching Experiments

Flat prefixes:
```
HYP-001       Parent
HYP-001a      Sub (different lookback)
HYP-001b      Sub (different signal)
HYP-001b-i    Sub-sub (rare — ask: data-mining?)
HYP-002       Next independent parent
```

Folders: `/experiments/hyp_001_slug/`, `/experiments/hyp_001a_slug/`

LOG.md tracks parentage:

| ID | Parent | Date | Hypothesis | Scripts | Metrics | Result | Folder |
|----|--------|------|-----------|---------|---------|--------|--------|
| HYP-001 | — | 2025-03-03 | IG momentum → 5d | garch.py, backtest_engine.py | SR=0.8 t=1.9 MDD=-4% IR=0.6 | PARTIAL | hyp_001_momentum |
| HYP-001a | HYP-001 | 2025-03-04 | Same, 10d lookback | garch.py, backtest_engine.py | SR=1.1 t=2.3 MDD=-3% IR=0.9 | CONFIRMED | hyp_001a_10d |

Depth 3+ → stop. Question whether you're overfitting.

---

## 6. Skill & Script Reference

### Skills (`/.claude/skills/*.md`)
Sections: When to Use · Packages · Math · Corresponding Script · Gotchas · Interpretation · References

```
credit_fi/       MertonModel, HazardRateBootstrap, SpreadDecomposition,
                 NelsonSiegel, BondAnalytics, OASCalculator,
                 ETFPremiumDiscount, TransitionMatrix

quant_finance/   BacktestEngine, Vectorbt, SignalConstruction,
                 PortfolioOptimizer, RiskParity, BlackLitterman,
                 LiquidityScorer, OpenBB, CreditSignals

ml_stats/        GARCH, ARIMA, RegimeDetection, LSTMForecaster,
                 TimesFM, TransformerForecaster, SHAPExplainer,
                 ConformalPrediction, BayesianRegression, CausalEffect,
                 DiffInDiff, SyntheticControl, HypothesisTesting,
                 Clustering, PCA, AnomalyDetection, GaussianProcess,
                 BayesianABTest, PowerAnalysis, SymbolicMath,
                 GraphNeuralNetwork, ReinforcementLearning, NetworkAnalysis

infrastructure/  EDA, PublicationFigures, DashboardGenerator,
                 NotebookTemplate, PyZotero, DataLoading,
                 LargeScaleProcessing, PlotlyCharts, ImageGeneration,
                 PDFReportGenerator, GraphicalAbstracts,
                 StakeholderNotebooks, SlideGenerator, Workflows
```

### Scripts (`/scripts/*.py`)
Each contains:
- **Typed functions** — `def fit_garch(...) -> GARCHResult`
- **Script wrapper** — `if __name__ == "__main__"` with CONFIG, writes `results.json`

Naming: `.md` PascalCase → `.py` snake_case. Same stem.

---

## 7. Canonical Metrics

4 metrics on **test set**:

| # | Metric | Definition | Purpose |
|---|--------|-----------|---------|
| 1 | **OOS Sharpe** | $\bar{r}/\sigma_r \times \sqrt{252}$ | Risk-adjusted return |
| 2 | **t-stat** | $\bar{r}/(\sigma_r/\sqrt{n})$ | Mean ≠ 0? |
| 3 | **Max Drawdown** | Worst peak-to-trough | Tail pain |
| 4 | **Info Ratio** | $\bar{r}_{excess}/\sigma_{excess}$ | Alpha per active risk |

Task-specific (≤ 2, justified): Hit Rate, OOS R², VaR coverage, empirical coverage.

Format: `SR=1.1 t=2.3 MDD=-3.2% IR=0.9 | +HitRate=58% (binary signal)`

| Metric | Weak | Moderate | Strong |
|--------|------|----------|--------|
| OOS Sharpe | 0.3–0.5 | 0.5–1.0 | > 1.0 |
| t-stat | 1.5–2.0 | 2.0–2.5 | > 2.5 |
| MDD | > -20% | -10%→-20% | > -10% |
| IR | 0.2–0.5 | 0.5–1.0 | > 1.0 |

---

## 8. Canonical Split (Enforced)

Temporal 60/20/20. No shuffling. No leakage.

```
|←── 60% Train ──→|←─ 20% Val ─→|←─ 20% Test ─→|
t=0                t=T₁           t=T₂            t=T
```

```python
T = len(df)
t1, t2 = int(T * 0.60), int(T * 0.80)
train, val, test = df.iloc[:t1], df.iloc[t1:t2], df.iloc[t2:]
```

- Temporal order preserved.
- No future info. Features at t use data ≤ t.
- Walk-forward is post-evaluation, not a substitute.
- Cross-sectional exception: stratified 60/20/20, `random_state=42`. Log it.

---

## 9. Experiment Folder

```
/experiments/hyp_001_spread_momentum/
├── README.md        ← Hypothesis, method, results, learnings
├── notebook.ipynb   ← Working notebook
├── analysis.py      ← Clean script (calls /scripts/*.py)
├── results.json     ← Metrics, split, parameters
├── figures/
└── notes.md         ← Optional lab notes
```

results.json:
```json
{
  "hypothesis_id": "HYP-001",
  "parent": null,
  "date": "2025-03-03",
  "hypothesis": "IG spread 5d momentum predicts excess returns",
  "scripts_called": ["garch.py", "backtest_engine.py"],
  "split": {"t1": "2020-01-02", "t2": "2022-06-30"},
  "metrics": {
    "oos_sharpe": 0.82, "t_stat": 1.91,
    "max_drawdown": -0.043, "information_ratio": 0.61,
    "task_specific": {"hit_rate": 0.54, "justification": "binary signal"}
  },
  "result": "PARTIAL",
  "learnings": "Works in low-vol regimes, reverses in high-vol.",
  "next_steps": ["HYP-001a: condition on vol regime"]
}
```

---

## 10. Workflow Templates

Defined in `/.claude/skills/infrastructure/Workflows.md`. Tag hypotheses: `(Workflow A)`, etc.

**A — Signal Research:** `EDA → Features → Signal → Backtest → Evaluate → Log`
**B — Model Comparison:** `EDA → Fit N Models → Val Select → Test Eval → Log`
**C — Causal Investigation:** `EDA → DAG → Effect → Refutation → Sensitivity → Log`
**D — Stakeholder Deliverable:** `Results → Figures → Report/Slides → /artifacts`
**E — Full Pipeline:** `EDA → Clean → Features → Model → Diagnostics → Viz → Report`

---

## 11. Conventions

| Item | Convention |
|------|-----------|
| Seed | `42` unless testing sensitivity |
| Index | `pd.DatetimeIndex`, tz-naive, bday |
| Returns | Decimal (0.01 = 1%); ×100 for `arch` |
| Money | Millions USD |
| Spreads | Basis points |
| Annualize | √252 |
| Figures | mpl + seaborn, PNG ≥150dpi |
| Nulls | ffill prices, drop returns, log either |
| Min sample | n ≥ 30 |
| Naming | `.md` PascalCase → `.py` snake_case |
| Skills first | Check `/.claude/skills/` before ad-hoc code |
| Checkpoints | Intermediates → `/data/` and experiment folder |
| Failure protocol | Script error → log traceback + context to `notes.md` before fixing. No silent retries. |