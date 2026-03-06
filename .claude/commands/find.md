---
name: find
description: Search skills by keyword, tag, or natural language query. Surfaces relevant skills to prevent reinventing existing capabilities.
---

Search for skills matching: $ARGUMENTS

## How to Search

$ARGUMENTS can be:
- **Keywords**: `volatility`, `credit spreads`, `forecasting`
- **Method names**: `GARCH`, `regression`, `clustering`
- **Task descriptions**: `model time-varying volatility`, `detect anomalies`
- **Domain terms**: `IG bonds`, `crypto`, `risk`

## Steps

1. **Load registry** from `~/.claude/skills/agentds/registry.yaml` (global) or `.claude/skills/registry.yaml` (local)

2. **Search** — Match query against:
   - `tags` (broad categories)
   - `keywords` (specific terms)
   - `use_when` (natural language description)
   - `id` and `category` (boost exact matches)

3. **Rank** — Score by relevance, penalize `not_for` matches

4. **Display** — Show top 5 results:

```
Results for "$ARGUMENTS":

1. GARCH (ml_stats)                           score: 0.89
   → Modeling time-varying volatility
   Related: RegimeDetection, ARIMA, ConformalPrediction
   Matched: tags: volatility, time-series

2. RegimeDetection (ml_stats)                 score: 0.65
   → Detecting market regimes and state changes
   Related: GARCH, HypothesisTesting
```

5. **Suggest next steps**:
   - Read the skill: `Read .claude/skills/<category>/<Skill>.md`
   - See related: `/find <related_skill>`
   - Use in experiment: Add to plan.md under Skill References

## Example Queries

| Query | Finds |
|-------|-------|
| `/find volatility` | GARCH, RegimeDetection, BrownianBridge |
| `/find credit default` | MertonModel, HazardRateBootstrap, TransitionMatrix |
| `/find clustering bonds` | Clustering, PCA |
| `/find backtest signal` | BacktestEngine, SignalConstruction |
| `/find bayesian` | MCMC, BayesianRegression, VariationalInference |

## No Results?

If no skills match:
1. Try broader terms (e.g., "volatility" instead of "GARCH(1,1)")
2. Check `/status` to see all available skills
3. The capability may not exist yet — consider creating a new skill
