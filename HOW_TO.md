# HOW_TO.md

## Setup

```bash
cd /media/ak/10E1026C4FA6006E/GitRepos/automated_data_scientist
source auto-data-science/bin/activate
claude
```

That's it. Claude Code reads `CLAUDE.md` automatically, discovers all skills via frontmatter, and makes agents + commands available.

---

## Slash Commands

Type these directly in Claude Code. They're the fastest way to work.

```
/eda data/prices.csv
```
Runs full EDA. Outputs cleaned parquet + summary stats + figures.

```
/hypothesize alpha in IG credit spreads
```
Generates 5 testable hypotheses with H₀/H₁, names the scripts, tags the workflow. Stops and waits for you to pick which ones to run.

```
/experiment HYP-001
```
Executes a hypothesis end-to-end: creates experiment folder, runs the analysis, applies bias/leakage checklist, reports 4 canonical metrics, writes results.json, updates LOG.md.

```
/report HYP-001
```
Generates stakeholder deliverables from a completed experiment: figures, PDF/markdown report, optional slides. Saves to `/artifacts/`.

```
/review HYP-001
```
Runs the 8-point bias/leakage checklist on an experiment. Reports PASS/FAIL per item with evidence.

---

## Agents

Agents are specialized subagents that run in their own context window. You don't call them directly — the main Claude Code session dispatches them when the task fits, or you can request it explicitly.

### Automatic dispatch

Just describe what you want. Claude Code routes to the right agent:

```
> Clean and explore the dataset in data/bond_returns.csv
```
→ Dispatches `data-engineer`

```
> Test whether IG spread momentum predicts 5-day excess returns
```
→ Dispatches `quant-researcher`

```
> Price this 10Y 5% coupon bond at a 4.2% yield and compute duration
```
→ Dispatches `credit-analyst`

```
> Make a slide deck summarizing the HYP-003 results for the PM
```
→ Dispatches `report-writer`

### Explicit dispatch

If you want to force a specific agent:

```
> Use the quant-researcher agent to run a GARCH(1,1) on data/vol_series.csv
```

```
> Dispatch credit-analyst to bootstrap hazard rates from these CDS spreads: 1Y=50, 3Y=80, 5Y=100, 7Y=115, 10Y=130
```

### Parallel dispatch

For complex tasks, Claude Code can run multiple agents simultaneously:

```
> Analyze the IG ETF dataset: have data-engineer clean it, quant-researcher test spread momentum, and credit-analyst decompose the spreads. Then report-writer summarizes everything.
```

This runs the first three in parallel, then report-writer runs after they finish.

---

## Typical Workflows

### Workflow A — Signal Research (most common)

```
/eda data/ig_spreads.csv
/hypothesize momentum signal in IG spreads
```
Pick a hypothesis (e.g. star #2), then:
```
/experiment HYP-001
/review HYP-001
/report HYP-001
```

### Workflow B — Model Comparison

```
> Compare GARCH, EGARCH, and GJR-GARCH on data/vol_series.csv.
  Use the quant-researcher agent. Evaluate all three on the validation set,
  pick the best, then single-touch the test set.
```

### Workflow C — Causal Investigation

```
> Did the March 2020 Fed intervention cause IG spreads to tighten
  beyond what fundamentals would predict? Use DiffInDiff or SyntheticControl.
```

### Workflow D — Stakeholder Deliverable

```
/report HYP-003
> Also make a 5-slide deck and a one-page PDF summary.
```

### Workflow E — External Dataset

You stay in this repo. Pass the path:

```
/eda /home/ak/Downloads/new_dataset.csv
```

Or copy data in first:
```
> Copy /home/ak/Downloads/new_dataset.csv to data/ and run EDA on it.
```

---

## What Lives Where

| You want to... | Look in |
|----------------|---------|
| Understand a method before using it | `.claude/skills/<category>/<Method>.md` |
| Call a function | `scripts/<category>/<method>.py` |
| See experiment results | `experiments/<hyp_id>_<slug>/results.json` |
| See the audit trail | `experiments/LOG.md` |
| See polished notebooks | `notebooks/` |
| See figures and reports | `artifacts/figures/` and `artifacts/reports/` |
| See raw data | `data/` |
| See the master rules | `CLAUDE.md` |

---

## The 54 Skills (Quick Reference)

**Credit & Fixed Income** — MertonModel, HazardRateBootstrap, SpreadDecomposition, NelsonSiegel, BondAnalytics, OASCalculator, ETFPremiumDiscount, TransitionMatrix

**Quant Finance** — BacktestEngine, Vectorbt, SignalConstruction, PortfolioOptimizer, RiskParity, BlackLitterman, LiquidityScorer, OpenBB, CreditSignals

**ML & Statistics** — GARCH, ARIMA, RegimeDetection, LSTMForecaster, TimesFM, TransformerForecaster, SHAPExplainer, ConformalPrediction, BayesianRegression, CausalEffect, DiffInDiff, SyntheticControl, HypothesisTesting, Clustering, PCA, AnomalyDetection, GaussianProcess, BayesianABTest, PowerAnalysis, SymbolicMath, GraphNeuralNetwork, ReinforcementLearning, NetworkAnalysis

**Infrastructure** — EDA, PublicationFigures, DashboardGenerator, NotebookTemplate, PyZotero, DataLoading, LargeScaleProcessing, PlotlyCharts, ImageGeneration, PDFReportGenerator, GraphicalAbstracts, StakeholderNotebooks, SlideGenerator, Workflows

You don't need to memorize these. Claude Code reads the frontmatter and auto-selects the right one based on what you ask.

---

## Tips

**Start every session with data.** Drop a CSV in `data/` or point to one. `/eda` first, always.

**Let Claude Code pick the agent.** Just describe the task in natural language. Explicit dispatch is for when you want to override.

**Don't write code yourself.** The 54 scripts exist for a reason. Say "use the backtest_engine.py" not "write me a backtester."

**Check LOG.md regularly.** It's your audit trail. If an experiment isn't logged, it didn't happen.

**Branch hypotheses, don't multiply.** HYP-001 → HYP-001a → HYP-001b. If you hit depth 3, you're probably overfitting.

**Single-touch the test set.** Iterate on validation. Test set gets touched once. Violations get logged.
