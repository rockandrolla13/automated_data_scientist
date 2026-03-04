"""
Brownian Bridge — Monte Carlo simulation with pinned endpoints.

Usage:
    from scripts.quant_finance.brownian_bridge import sample_bridge, default_time_simulation

    # Simple Brownian bridge from 0 to 1
    paths = sample_bridge(0, 1, 0.0, 1.0, n_steps=100, n_paths=1000)

    # Default time simulation for Merton model
    result = default_time_simulation(V0=100, D=80, sigma=0.2, r=0.05, T=5, n_paths=10000)
"""
from dataclasses import dataclass

import numpy as np


@dataclass
class DefaultTimeResult:
    """Result from default time simulation."""
    default_times: np.ndarray  # Time of default (inf if no default)
    default_probability: float
    expected_default_time: float  # Conditional on default
    survival_probability: float
    paths: np.ndarray  # Asset value paths


@dataclass
class BondPathResult:
    """Result from bond path simulation."""
    paths: np.ndarray  # Shape (n_paths, n_steps+1)
    times: np.ndarray  # Time grid
    mean_path: np.ndarray
    quantiles: dict[str, np.ndarray]  # 5%, 25%, 50%, 75%, 95%


def sample_bridge(
    t_start: float,
    t_end: float,
    x_start: float,
    x_end: float,
    n_steps: int,
    n_paths: int,
    seed: int = 42,
) -> np.ndarray:
    """Sample Brownian bridge paths from x_start to x_end.

    Args:
        t_start: Start time
        t_end: End time
        x_start: Value at t_start
        x_end: Value at t_end
        n_steps: Number of time steps
        n_paths: Number of paths to simulate

    Returns:
        Array of shape (n_paths, n_steps+1)
    """
    np.random.seed(seed)

    T = t_end - t_start
    dt = T / n_steps
    times = np.linspace(t_start, t_end, n_steps + 1)

    # Initialize paths
    paths = np.zeros((n_paths, n_steps + 1))
    paths[:, 0] = x_start
    paths[:, -1] = x_end

    # Build bridge recursively (bisection method for efficiency)
    # For simplicity, use sequential construction here
    sqrt_dt = np.sqrt(dt)

    # Generate increments for unconditioned Brownian motion
    dW = np.random.normal(0, sqrt_dt, (n_paths, n_steps))
    W = np.cumsum(dW, axis=1)
    W = np.hstack([np.zeros((n_paths, 1)), W])  # W(0) = 0

    # Transform to bridge: B(t) = W(t) - (t/T) * W(T) + (t/T) * (x_end - x_start)
    for i in range(n_steps + 1):
        t = times[i] - t_start
        paths[:, i] = x_start + W[:, i] - (t / T) * W[:, -1] + (t / T) * (x_end - x_start)

    return paths


def sample_gbm_bridge(
    S0: float,
    ST: float,
    T: float,
    r: float,
    sigma: float,
    n_steps: int,
    n_paths: int,
    seed: int = 42,
) -> np.ndarray:
    """Sample GBM bridge paths — asset prices pinned to S0 and ST.

    Uses log-space bridge: log(S) follows Brownian bridge.

    Args:
        S0: Initial asset price
        ST: Terminal asset price
        T: Time to maturity
        r: Risk-free rate (not used in bridge, but kept for interface)
        sigma: Volatility
        n_steps: Number of time steps
        n_paths: Number of paths

    Returns:
        Array of shape (n_paths, n_steps+1) with price paths
    """
    # Bridge in log-space
    log_S0 = np.log(S0)
    log_ST = np.log(ST)

    log_paths = sample_bridge(0, T, log_S0, log_ST, n_steps, n_paths, seed)

    # Scale by volatility (bridge has unit variance)
    dt = T / n_steps
    times = np.linspace(0, T, n_steps + 1)

    # The raw bridge has variance t(T-t)/T at time t
    # Scale to have GBM-like variance: sigma^2 * t(T-t)/T
    # This is already approximately right for unit variance bridge
    # For GBM bridge, we need to scale the deviations from the linear interpolation

    linear_interp = log_S0 + (times / T) * (log_ST - log_S0)
    deviations = log_paths - linear_interp
    scaled_deviations = deviations * sigma

    log_paths = linear_interp + scaled_deviations

    return np.exp(log_paths)


def default_time_simulation(
    V0: float,
    D: float,
    sigma: float,
    r: float,
    T: float,
    n_paths: int,
    n_steps_per_year: int = 252,
    seed: int = 42,
) -> DefaultTimeResult:
    """Simulate first-passage default times for Merton model.

    Default occurs when asset value V(t) first crosses debt threshold D.

    Args:
        V0: Initial asset value
        D: Debt (default threshold)
        sigma: Asset volatility
        r: Risk-free rate (drift)
        T: Time horizon
        n_paths: Number of simulation paths
        n_steps_per_year: Time steps per year (252 for daily)
        seed: Random seed

    Returns:
        DefaultTimeResult with default times and probabilities
    """
    np.random.seed(seed)

    n_steps = int(T * n_steps_per_year)
    dt = T / n_steps
    sqrt_dt = np.sqrt(dt)

    # Simulate GBM paths (not bridge — we don't know terminal value)
    drift = (r - 0.5 * sigma**2) * dt
    diffusion = sigma * sqrt_dt

    log_V = np.zeros((n_paths, n_steps + 1))
    log_V[:, 0] = np.log(V0)

    dW = np.random.normal(0, 1, (n_paths, n_steps))

    for i in range(n_steps):
        log_V[:, i + 1] = log_V[:, i] + drift + diffusion * dW[:, i]

    V = np.exp(log_V)

    # Find first-passage times
    times = np.linspace(0, T, n_steps + 1)
    default_times = np.full(n_paths, np.inf)

    for path_idx in range(n_paths):
        crossings = np.where(V[path_idx, :] <= D)[0]
        if len(crossings) > 0:
            default_times[path_idx] = times[crossings[0]]

    # Statistics
    defaulted = default_times < np.inf
    default_prob = np.mean(defaulted)
    survival_prob = 1 - default_prob

    if np.any(defaulted):
        expected_default_time = np.mean(default_times[defaulted])
    else:
        expected_default_time = np.inf

    return DefaultTimeResult(
        default_times=default_times,
        default_probability=default_prob,
        expected_default_time=expected_default_time,
        survival_probability=survival_prob,
        paths=V,
    )


def bond_path_simulation(
    P0: float,
    par: float,
    T: float,
    r: float,
    sigma: float,
    n_steps: int,
    n_paths: int,
    seed: int = 42,
) -> BondPathResult:
    """Simulate bond price paths pinned to par at maturity.

    Args:
        P0: Initial bond price
        par: Par value at maturity
        T: Time to maturity
        r: Risk-free rate (for drift adjustment)
        sigma: Price volatility
        n_steps: Number of time steps
        n_paths: Number of paths

    Returns:
        BondPathResult with paths and statistics
    """
    # Use GBM bridge
    paths = sample_gbm_bridge(P0, par, T, r, sigma, n_steps, n_paths, seed)
    times = np.linspace(0, T, n_steps + 1)

    # Compute statistics
    mean_path = np.mean(paths, axis=0)
    quantiles = {
        "5%": np.percentile(paths, 5, axis=0),
        "25%": np.percentile(paths, 25, axis=0),
        "50%": np.percentile(paths, 50, axis=0),
        "75%": np.percentile(paths, 75, axis=0),
        "95%": np.percentile(paths, 95, axis=0),
    }

    return BondPathResult(
        paths=paths,
        times=times,
        mean_path=mean_path,
        quantiles=quantiles,
    )


def plot_paths(
    paths: np.ndarray,
    times: np.ndarray,
    n_show: int = 50,
    title: str = "Simulated Paths",
) -> None:
    """Plot sample paths with mean and quantiles."""
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))

    # Plot sample paths
    for i in range(min(n_show, len(paths))):
        plt.plot(times, paths[i], "b-", alpha=0.1, linewidth=0.5)

    # Plot mean
    mean_path = np.mean(paths, axis=0)
    plt.plot(times, mean_path, "r-", linewidth=2, label="Mean")

    # Plot quantiles
    q05 = np.percentile(paths, 5, axis=0)
    q95 = np.percentile(paths, 95, axis=0)
    plt.fill_between(times, q05, q95, alpha=0.2, color="red", label="90% CI")

    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()


if __name__ == "__main__":
    # Example: Default time simulation
    result = default_time_simulation(
        V0=100,
        D=80,
        sigma=0.25,
        r=0.05,
        T=5,
        n_paths=10000,
    )

    print("=== Default Time Simulation ===")
    print(f"Initial asset value: 100, Debt threshold: 80")
    print(f"Volatility: 25%, Rate: 5%, Horizon: 5 years")
    print(f"Default probability: {result.default_probability:.2%}")
    print(f"Survival probability: {result.survival_probability:.2%}")
    if result.expected_default_time < np.inf:
        print(f"Expected default time (if default): {result.expected_default_time:.2f} years")

    # Example: Bond path simulation
    bond_result = bond_path_simulation(
        P0=95,
        par=100,
        T=5,
        r=0.05,
        sigma=0.1,
        n_steps=252 * 5,
        n_paths=1000,
    )

    print("\n=== Bond Path Simulation ===")
    print(f"Initial price: 95, Par: 100, Maturity: 5 years")
    print(f"Mean path at T/2: {bond_result.mean_path[len(bond_result.mean_path)//2]:.2f}")
    print(f"90% CI at T/2: [{bond_result.quantiles['5%'][len(bond_result.mean_path)//2]:.2f}, "
          f"{bond_result.quantiles['95%'][len(bond_result.mean_path)//2]:.2f}]")
