"""power_analysis — Sample size calculation and power curves."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class PowerResult:
    required_n: int
    effect_size: float
    alpha: float
    power: float
    test_type: str


def required_sample_size(
    effect_size: float,
    alpha: float = 0.05,
    power: float = 0.80,
    test_type: str = "two-sample",
    ratio: float = 1.0,
) -> int:
    """Compute required sample size per group."""
    from statsmodels.stats.power import TTestIndPower, TTestPower

    if test_type == "two-sample":
        analysis = TTestIndPower()
        n = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power,
                                  ratio=ratio, alternative="two-sided")
    elif test_type == "paired":
        analysis = TTestPower()
        n = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power,
                                  alternative="two-sided")
    else:
        raise ValueError(f"Unknown test_type: {test_type}")

    return int(np.ceil(n))


def achieved_power(
    effect_size: float,
    n: int,
    alpha: float = 0.05,
    test_type: str = "two-sample",
) -> float:
    """Compute achieved power given effect size and sample size."""
    from statsmodels.stats.power import TTestIndPower, TTestPower

    if test_type == "two-sample":
        return TTestIndPower().power(effect_size=effect_size, nobs1=n, alpha=alpha, alternative="two-sided")
    else:
        return TTestPower().power(effect_size=effect_size, nobs=n, alpha=alpha, alternative="two-sided")


def power_curve(
    effect_sizes: np.ndarray | None = None,
    n: int = 100,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Power across a range of effect sizes."""
    if effect_sizes is None:
        effect_sizes = np.arange(0.1, 1.5, 0.05)

    rows = []
    for d in effect_sizes:
        pwr = achieved_power(d, n, alpha)
        rows.append({"effect_size": d, "power": pwr, "n": n, "alpha": alpha})
    return pd.DataFrame(rows)


def sharpe_to_sample_size(
    target_sharpe: float,
    alpha: float = 0.05,
    power: float = 0.80,
    freq: str = "daily",
) -> int:
    """How many observations to detect a given Sharpe ratio.
    SR ≈ d * sqrt(n) → d = SR / sqrt(annualization).
    """
    ann = {"daily": 252, "weekly": 52, "monthly": 12}[freq]
    d = target_sharpe / np.sqrt(ann)
    return required_sample_size(d, alpha, power, test_type="paired")


if __name__ == "__main__":
    n = required_sample_size(effect_size=0.3, alpha=0.05, power=0.80)
    print(f"Required n per group: {n}")

    n_sharpe = sharpe_to_sample_size(target_sharpe=0.5)
    print(f"Days to detect SR=0.5: {n_sharpe}")
