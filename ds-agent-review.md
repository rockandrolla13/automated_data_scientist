# Critical Review: DS-Agent (ICML'24) vs Our Framework

## What DS-Agent Actually Is

DS-Agent (Guo et al., ICML 2024) is not a skill library or a prompt template. It's a **feedback-driven iteration system** built on Case-Based Reasoning (CBR) — a classical AI paradigm from the 1990s applied to LLM-driven data science.

The architecture has two stages:

### Development Stage (iterative)
```
RETRIEVE relevant cases from Kaggle case bank
    → REUSE: adapt case into experiment plan
    → EXECUTE: run plan, get metrics
    → REVISE: if metrics bad, adjust plan using feedback
    → RETAIN: if metrics good, store solution in agent case bank
    → LOOP until convergence or budget exhausted
```

### Deployment Stage (one-shot)
```
RETRIEVE similar solved case from agent case bank
    → ADAPT: minor modifications for new task
    → GENERATE: output code directly
    → DONE (no iteration, cheap)
```

Key insight: the system **learns from its own successes**. Solved tasks become retrievable cases for future tasks.

---

## Honest Comparison: What They Have That We Don't

### 1. FEEDBACK LOOP — The Biggest Gap

**DS-Agent:** Execute → measure → revise → re-execute. Automatic. Up to N iterations. The agent sees its own metrics and adjusts.

**Our framework:** Execute → log → stop. We log the result and wait for the user to decide what to do next. There's no automated "that Sharpe was 0.3, let me try a different lookback window" cycle.

**Why this matters:** Their 100% success rate on development tasks comes from iteration, not from getting it right the first time. Most of their successful solutions required 2-5 revision cycles. Our system gives up after one shot unless the user manually types "try again with different parameters."

### 2. CASE BANK — Searchable Memory of What Worked

**DS-Agent:** Two case banks:
- **Human insight bank** — curated Kaggle competition solutions (the "textbook")
- **Agent case bank** — solutions that worked during development (the "experience")

Both are retrievable by similarity to the current task description.

**Our framework:** We have LOG.md (flat audit trail) and results.json per experiment. But there's no retrieval mechanism. If I solved "IG spread momentum" 3 months ago and now face "HY spread momentum", our system doesn't know to look up the previous solution. The user has to remember.

### 3. PLAN-THEN-CODE — Structured Experiment Plans

**DS-Agent:** Before writing any code, the agent generates an explicit experiment plan as text: "1. Load data, 2. Feature engineering with rolling windows, 3. Train XGBoost with early stopping, 4. Evaluate with RMSE." The plan is a first-class object that gets revised.

**Our framework:** We have hypotheses (H₀/H₁) and workflow templates, but no structured experiment plan between "hypothesis" and "code." The agent jumps from hypothesis to calling scripts. There's no reviewable plan artifact.

### 4. AUTOMATIC PARAMETER REVISION

**DS-Agent:** When iteration N produces RMSE=0.45 and the agent knows the Kaggle winner got 0.38, it revises: "increase epochs, add feature interaction terms, try ensemble." This is driven by the gap between current performance and the retrieved case's performance.

**Our framework:** We have the decay prior (§4: "expect 40-60% OOS decay") but no mechanism to automatically adjust when performance is below expectations. The user sees "SR=0.3" and decides manually.

---

## What They DON'T Have (That We Do)

| Our Advantage | Why It Matters |
|---------------|----------------|
| Hypothesis discipline (H₀/H₁) | They have no scientific method. Just "build best model." |
| Bias/leakage checklist | They don't check for look-ahead bias, survivorship, etc. |
| Temporal split enforcement | Their benchmarks use random train/test splits. |
| Domain-specific skills (credit, FI) | They cover generic tabular/text/timeseries. No finance. |
| Typed scripts with dataclass outputs | Their code generation is ad-hoc per task. |
| Audit trail with experiment branching | They track iterations but not hypothesis genealogy. |
| Canonical metrics (SR, t-stat, MDD, IR) | They use task-specific metrics only. |
| Transaction cost modeling | Not applicable to their Kaggle benchmarks. |

Their system would happily overfit a backtest with no slippage, no leakage check, and no OOS decay prior. Ours wouldn't.

---

## 5 Concrete Improvements to Our Framework

### Improvement 1: Iteration Loop (steal from DS-Agent)

Add an automatic revision cycle to Mode B. Currently:

```
Current:   Hypothesize → Execute → Log → STOP
Proposed:  Hypothesize → Plan → Execute → Evaluate → Revise? → Re-execute → Log
```

Implementation: Add to CLAUDE.md §4 a revision protocol:

```
REVISION PROTOCOL (max 3 iterations on validation set):
After evaluation, if metrics are below "Moderate" thresholds (§7):
  1. Diagnose: Which metric failed? Why?
  2. Propose 1-2 specific changes (not "try everything")
  3. Re-execute with changes. Log as HYP-001-iter2, HYP-001-iter3.
  4. If 3 iterations don't reach Moderate: STOP, log as FAILED, document why.
  
Test set is STILL single-touch. Iteration happens on validation only.
```

This is ~15 lines added to CLAUDE.md. No new files needed.

**What changes:** Add a `RevisionLoop` section to the Workflows skill, and add `iteration` field to results.json.


### Improvement 2: Case Bank (steal core idea, adapt for finance)

Create a searchable case bank from our own experiments. Not Kaggle — our LOG.md and results.json files ARE the case bank. They just need to be retrievable.

New skill + script pair:

```
.claude/skills/infrastructure/CaseBank.md
scripts/infrastructure/case_bank.py
```

What it does:
- `index_experiments()` — reads all experiments/*/results.json, builds an index
- `retrieve_similar(task_description, top_k=3)` — TF-IDF or embedding similarity against hypothesis text
- `adapt_case(case, new_task)` — returns the previous experiment's scripts, params, and learnings

When the agent starts a new hypothesis, it first checks: "have I solved something like this before?" If yes, it starts from that solution instead of from scratch.

This is our LOG.md becoming a first-class retrieval system instead of a flat file.


### Improvement 3: Experiment Plan as First-Class Artifact

Before executing, the agent writes a plan. Not just H₀/H₁, but the specific steps:

```
experiments/hyp_005_carry/plan.md:

## Hypothesis
H₀: Credit carry (spread - funding) does not predict 5d excess returns.
H₁: Top-quintile carry → positive excess returns.

## Plan
1. Load: data/ig_spreads.csv via data_loading.py
2. Features: carry_signal() from credit_signals.py, window=20
3. Signal: zscore_normalize() from signal_construction.py
4. Backtest: backtest() from backtest_engine.py, costs_bps=5
5. Evaluate: 4 canonical metrics on validation
6. If SR < 0.5: try window=[10, 40], re-evaluate
7. Single touch test set with best validation config

## Expected Duration: 1 iteration if signal is clean, 2-3 if noisy
## Scripts: credit_signals.py, signal_construction.py, backtest_engine.py
## Skill References: CreditSignals.md, SignalConstruction.md, BacktestEngine.md
```

This is reviewable before execution, reusable as a case, and auditable.

Implementation: Add `plan.md` to §9 experiment folder template. Update the `/experiment` slash command to generate plan first, then pause for approval, then execute.


### Improvement 4: Retain Successful Solutions (the "deployment" idea)

DS-Agent's deployment stage = reuse past solutions with minimal adaptation. We can do this without building a separate system:

Add a `solutions/` directory:

```
solutions/
├── spread_momentum.yaml    ← "when asked about spread momentum, start here"
├── carry_signal.yaml       ← "when asked about carry, start here"
└── vol_regime.yaml         ← "when asked about vol regimes, start here"
```

Each YAML is a lightweight recipe:
```yaml
name: spread_momentum
description: Cross-sectional spread momentum signal for IG bonds
origin: HYP-001a (experiments/hyp_001a_10d/)
scripts:
  - credit_signals.py::spread_momentum(lookback=10)
  - signal_construction.py::zscore_normalize(window=60)
  - backtest_engine.py::backtest(costs_bps=5)
params:
  lookback: 10
  z_window: 60
  costs_bps: 5
metrics:
  oos_sharpe: 1.1
  t_stat: 2.3
learnings: "Works in low-vol regimes. Condition on VIX < 20 for best results."
```

The agent reads `solutions/` before generating a new plan. If a matching recipe exists, it adapts rather than starting from scratch.

New skill: `.claude/skills/infrastructure/SolutionRetrieval.md`
New script: `scripts/infrastructure/solution_retrieval.py`


### Improvement 5: Execution Feedback in results.json

DS-Agent captures execution feedback (errors, warnings, metric progression across iterations). Our results.json only captures final metrics.

Extend the schema:

```json
{
  "hypothesis_id": "HYP-005",
  "iterations": [
    {
      "iter": 1,
      "params": {"lookback": 20},
      "val_metrics": {"sharpe": 0.31, "t_stat": 1.2},
      "diagnosis": "Sharpe below Moderate threshold. Lookback too short.",
      "action": "Increase lookback to 40"
    },
    {
      "iter": 2,
      "params": {"lookback": 40},
      "val_metrics": {"sharpe": 0.72, "t_stat": 2.1},
      "diagnosis": "Sharpe now Moderate. Proceed to test.",
      "action": "Touch test set"
    }
  ],
  "test_metrics": {"sharpe": 0.58, "t_stat": 1.8, "mdd": -0.032, "ir": 0.45},
  "result": "PARTIAL",
  "decay": "20% from val to test (within expected 40-60% range)"
}
```

This makes every experiment a retrievable case with full iteration history.

---

## Summary: Priority-Ranked Changes

| # | Change | Effort | Impact | What Changes |
|---|--------|--------|--------|-------------|
| 1 | Iteration loop in §4 | ~15 lines in CLAUDE.md | HIGH — goes from 1-shot to multi-shot | CLAUDE.md edit |
| 2 | plan.md in experiment template | ~10 lines in CLAUDE.md, update /experiment command | HIGH — reviewable before execution | CLAUDE.md + 1 command edit |
| 3 | Extended results.json schema | ~5 lines in CLAUDE.md §9 | MEDIUM — enables case retrieval later | CLAUDE.md edit |
| 4 | CaseBank skill + script | 1 new skill, 1 new script (~150 lines) | MEDIUM — "have I seen this before?" | 2 new files |
| 5 | Solutions directory | 1 new skill, 1 new script, solutions/ dir (~100 lines) | MEDIUM — fast-start from proven recipes | 2 new files + new dir |

Changes 1-3 are edits to existing files. ~30 lines total. No new architecture.
Changes 4-5 add 4 new files. They're optional but become powerful once you have 10+ experiments logged.

The fundamental insight from DS-Agent: **iteration beats single-shot, and memory beats amnesia.** Our framework has the scientific rigor they lack. Adding their feedback loop and retrieval mechanism to our hypothesis discipline would be genuinely powerful.
