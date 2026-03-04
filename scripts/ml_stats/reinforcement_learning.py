"""reinforcement_learning — Trading environment and RL agent training via stable-baselines3."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class RLResult:
    total_reward: float
    sharpe: float
    max_drawdown: float
    n_trades: int
    episode_rewards: list[float]


def create_trading_env(
    df: pd.DataFrame,
    price_col: str = "close",
    initial_balance: float = 1_000_000,
    transaction_cost_bps: float = 5.0,
):
    """Create a simple trading Gymnasium environment."""
    import gymnasium as gym
    from gymnasium import spaces

    class TradingEnv(gym.Env):
        metadata = {"render_modes": []}

        def __init__(self):
            super().__init__()
            self.prices = df[price_col].values
            self.n_steps = len(self.prices) - 1
            self.initial_balance = initial_balance
            self.tc = transaction_cost_bps / 10_000

            # Actions: 0=hold, 1=buy, 2=sell
            self.action_space = spaces.Discrete(3)
            # Observation: [position, returns_5d, vol_20d, balance_pct]
            self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32)

        def reset(self, seed=None, options=None):
            super().reset(seed=seed)
            self.step_idx = 20  # skip initial lookback
            self.position = 0  # -1, 0, 1
            self.balance = self.initial_balance
            self.n_trades = 0
            return self._obs(), {}

        def _obs(self):
            rets = np.diff(np.log(self.prices[max(0, self.step_idx-5):self.step_idx+1]))
            ret_5d = rets.sum() if len(rets) > 0 else 0
            vol = np.std(np.diff(np.log(self.prices[max(0, self.step_idx-20):self.step_idx+1]))) if self.step_idx > 20 else 0.01
            bal_pct = self.balance / self.initial_balance
            return np.array([self.position, ret_5d, vol, bal_pct], dtype=np.float32)

        def step(self, action):
            price_now = self.prices[self.step_idx]
            price_next = self.prices[min(self.step_idx + 1, self.n_steps)]
            ret = (price_next - price_now) / price_now

            old_pos = self.position
            if action == 1:
                self.position = 1
            elif action == 2:
                self.position = -1
            else:
                pass

            if old_pos != self.position:
                self.n_trades += 1
                self.balance *= (1 - self.tc)

            pnl = self.position * ret * self.balance
            self.balance += pnl

            # Reward: risk-adjusted return
            reward = float(pnl / self.initial_balance)

            self.step_idx += 1
            terminated = self.step_idx >= self.n_steps
            truncated = False

            return self._obs(), reward, terminated, truncated, {}

    return TradingEnv()


def train_agent(
    env,
    algorithm: str = "PPO",
    total_timesteps: int = 50_000,
    random_state: int = 42,
):
    """Train RL agent. Returns trained model."""
    from stable_baselines3 import PPO, A2C

    algos = {"PPO": PPO, "A2C": A2C}
    cls = algos.get(algorithm, PPO)
    model = cls("MlpPolicy", env, verbose=0, seed=random_state)
    model.learn(total_timesteps=total_timesteps)
    return model


def evaluate_agent(model, env, n_episodes: int = 10) -> RLResult:
    """Evaluate trained agent over multiple episodes."""
    episode_rewards = []
    total_trades = 0

    for _ in range(n_episodes):
        obs, _ = env.reset()
        done = False
        ep_reward = 0
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            ep_reward += reward
            done = terminated or truncated
        episode_rewards.append(ep_reward)
        total_trades += env.n_trades

    rewards = np.array(episode_rewards)
    sharpe = rewards.mean() / (rewards.std() + 1e-10) * np.sqrt(252)

    return RLResult(
        total_reward=float(rewards.sum()),
        sharpe=float(sharpe),
        max_drawdown=float(rewards.min()),
        n_trades=total_trades // n_episodes,
        episode_rewards=episode_rewards,
    )


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    prices = 100 * np.cumprod(1 + rng.normal(0.0002, 0.01, 500))
    df = pd.DataFrame({"close": prices})

    env = create_trading_env(df)
    print(f"Environment created. Action space: {env.action_space}, Obs space: {env.observation_space}")
