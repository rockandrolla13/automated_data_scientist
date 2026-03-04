# ReinforcementLearning

## When to Use
- Sequential decision problems: optimal execution, portfolio rebalancing.
- When actions affect future states (trading impact, inventory management).
- NOT for static prediction tasks (use supervised learning).

## Packages
```python
import gymnasium as gym
from stable_baselines3 import PPO, A2C, SAC
```

## Corresponding Script
`/scripts/ml_stats/reinforcement_learning.py`
- `create_trading_env(df, config) -> gym.Env`
- `train_agent(env, algorithm, timesteps) -> RLResult`
- `evaluate_agent(model, env, n_episodes) -> pd.DataFrame`

## Gotchas
1. **Reward shaping is everything.** Bad reward → agent learns wrong thing. Use risk-adjusted returns.
2. **Sample inefficient.** RL needs millions of steps. Financial data is scarce. Use simulation.
3. **Non-stationarity.** Markets change. Agent trained on 2020 data may fail in 2024.
4. **Overfitting to simulator.** If using synthetic data, agent exploits simulator artifacts.
5. **Start simple.** Tabular Q-learning before deep RL. Bandit before full MDP.

## References
- Sutton & Barto (2018). Reinforcement Learning: An Introduction.
- stable-baselines3: https://stable-baselines3.readthedocs.io/
