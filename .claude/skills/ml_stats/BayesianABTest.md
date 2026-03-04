---
name: bayesian-ab-test
description: Use when running A/B tests with Bayesian framework to get posterior probabilities instead of p-values.
---

# BayesianABTest

## When to Use
- A/B testing with Bayesian framework (posterior on effect size).
- When you want P(A > B) instead of just p-values.
- Continuous monitoring without multiple-testing penalty.

## Packages
```python
import pymc as pm
import arviz as az
from scipy import stats
```

## Mathematical Background
Beta-Binomial model (conversion): $\theta_A \sim \text{Beta}(\alpha_A, \beta_A)$, posterior updated with observed successes/failures.
Normal model (revenue): $\mu_A \sim N(m, s^2)$, posterior via conjugacy or MCMC.
Decision: P(θ_A > θ_B | data) — the "probability of being best."

## Corresponding Script
`/scripts/ml_stats/bayesian_ab_test.py`
- `beta_binomial_test(successes_a, n_a, successes_b, n_b) -> ABTestResult`
- `normal_test(samples_a, samples_b) -> ABTestResult`
- `expected_loss(result) -> float` — expected loss of choosing A if B is actually better

## Gotchas
1. **Priors matter with small n.** Use Beta(1,1) (uniform) as default. Informative priors only if justified.
2. **P(A > B) = 0.95 is NOT the same as p < 0.05.** Don't conflate frequentist and Bayesian thresholds.
3. **Expected loss > probability of winning.** Use loss to decide, not just P(A>B).
4. **Early stopping is allowed** in Bayesian framework, unlike frequentist tests.

## References
- Kruschke (2013). Bayesian estimation supersedes the t-test.
