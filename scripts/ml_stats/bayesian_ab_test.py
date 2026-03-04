"""bayesian_ab_test — Bayesian A/B testing with Beta-Binomial and Normal models."""

from dataclasses import dataclass
import numpy as np


@dataclass
class ABTestResult:
    prob_a_better: float
    prob_b_better: float
    expected_loss_a: float  # expected loss if we pick A but B is better
    expected_loss_b: float
    effect_size: float
    ci_95: tuple[float, float]
    n_simulations: int


def beta_binomial_test(
    successes_a: int, n_a: int,
    successes_b: int, n_b: int,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
    n_sim: int = 100_000,
    random_state: int = 42,
) -> ABTestResult:
    """Bayesian A/B test for conversion rates (Beta-Binomial model)."""
    rng = np.random.default_rng(random_state)

    post_a = rng.beta(prior_alpha + successes_a, prior_beta + n_a - successes_a, n_sim)
    post_b = rng.beta(prior_alpha + successes_b, prior_beta + n_b - successes_b, n_sim)

    diff = post_a - post_b
    prob_a = float(np.mean(diff > 0))
    prob_b = float(np.mean(diff < 0))

    # Expected loss: E[max(θ_B - θ_A, 0)] if we pick A
    loss_a = float(np.mean(np.maximum(post_b - post_a, 0)))
    loss_b = float(np.mean(np.maximum(post_a - post_b, 0)))

    ci = (float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5)))

    return ABTestResult(
        prob_a_better=prob_a, prob_b_better=prob_b,
        expected_loss_a=loss_a, expected_loss_b=loss_b,
        effect_size=float(np.mean(diff)), ci_95=ci, n_simulations=n_sim,
    )


def normal_test(
    samples_a: np.ndarray,
    samples_b: np.ndarray,
    n_sim: int = 100_000,
    random_state: int = 42,
) -> ABTestResult:
    """Bayesian A/B test for continuous metrics (Normal model with conjugate prior)."""
    rng = np.random.default_rng(random_state)

    # Posterior parameters (uninformative prior)
    n_a, n_b = len(samples_a), len(samples_b)
    mean_a, mean_b = np.mean(samples_a), np.mean(samples_b)
    var_a, var_b = np.var(samples_a, ddof=1), np.var(samples_b, ddof=1)

    # Posterior draws (Normal approximation)
    post_a = rng.normal(mean_a, np.sqrt(var_a / n_a), n_sim)
    post_b = rng.normal(mean_b, np.sqrt(var_b / n_b), n_sim)

    diff = post_a - post_b
    prob_a = float(np.mean(diff > 0))
    prob_b = float(np.mean(diff < 0))
    loss_a = float(np.mean(np.maximum(post_b - post_a, 0)))
    loss_b = float(np.mean(np.maximum(post_a - post_b, 0)))
    ci = (float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5)))

    return ABTestResult(
        prob_a_better=prob_a, prob_b_better=prob_b,
        expected_loss_a=loss_a, expected_loss_b=loss_b,
        effect_size=float(np.mean(diff)), ci_95=ci, n_simulations=n_sim,
    )


if __name__ == "__main__":
    # Conversion test
    result = beta_binomial_test(successes_a=120, n_a=1000, successes_b=105, n_b=1000)
    print(f"P(A>B)={result.prob_a_better:.3f}, Effect={result.effect_size:.4f}")
    print(f"Expected loss A: {result.expected_loss_a:.5f}, B: {result.expected_loss_b:.5f}")
