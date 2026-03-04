---
name: simulate
description: Run Monte Carlo simulation for pricing or risk. Supports Brownian bridge, GBM, default time simulation.
---

Run Monte Carlo simulation for: $ARGUMENTS

## Pipeline
1. **Identify simulation type**:
   - Default time / first-passage → BrownianBridge.default_time_simulation
   - Bond price paths (pinned to par) → BrownianBridge.bond_path_simulation
   - Asset price paths → BrownianBridge.sample_gbm_bridge
   - Generic paths with endpoints → BrownianBridge.sample_bridge

2. **Read skill** — .claude/skills/quant_finance/BrownianBridge.md

3. **Set parameters**:
   - n_paths: 1000-10000 (more for tails)
   - n_steps: 252 per year (daily) typical
   - seed: 42 (reproducibility)
   - Model-specific: V0, D, sigma, r, T

4. **Run simulation** via scripts/quant_finance/brownian_bridge.py

5. **Compute statistics**:
   - Mean, std across paths
   - Quantiles: 5th, 25th, 50th, 75th, 95th
   - For default: probability, expected time conditional on default

6. **Visualize**:
   - Path fan chart (sample paths + mean + 90% CI)
   - Terminal distribution histogram
   - For default: survival curve

7. **Report**:
   | Statistic | Value |
   |-----------|-------|
   | Mean | ... |
   | Std | ... |
   | 5th percentile | ... |
   | 95th percentile | ... |
   | (For default) P(default) | ... |

8. **Save**:
   - Paths to experiment folder (parquet for large)
   - Figures to figures/
   - Statistics to results.json

Example: /simulate "1000 default time paths for BBB issuer, Merton model, V0=100, D=80, sigma=0.25, T=5"
