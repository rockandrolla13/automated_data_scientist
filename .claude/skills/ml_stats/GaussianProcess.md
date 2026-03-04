# GaussianProcess

## When to Use
- Regression with full predictive uncertainty (mean + variance at every point).
- Small-to-medium data (n < 5000). GP scales O(n³).
- Bayesian optimization: surrogate model for hyperparameter tuning.

## Packages
```python
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel, ConstantKernel
```

## Mathematical Background
$f(x) \sim \mathcal{GP}(m(x), k(x,x'))$. Posterior: condition on data.
Key kernels: RBF (smooth), Matérn (tunable smoothness, ν=1.5 or 2.5), Periodic.
Marginal likelihood optimized to select kernel hyperparameters.

## Corresponding Script
`/scripts/ml_stats/gaussian_process.py`
- `fit_gp(X, y, kernel) -> GPResult`
- `predict_with_uncertainty(result, X_new) -> pd.DataFrame`
- `optimize_acquisition(result, bounds, acq_fn) -> np.ndarray` — Bayesian optimization step

## Gotchas
1. **O(n³) scaling.** For n > 5000, use sparse GP (inducing points) or switch to neural net.
2. **Kernel choice matters.** RBF assumes infinite smoothness — unrealistic for financial data. Try Matérn(ν=1.5).
3. **Normalize inputs and outputs.** GP is sensitive to scale.
4. **Lengthscale interpretation.** Short = wiggly. Long = smooth. If learned l → 0, model is overfitting.

## Interpretation Guide
| Output | Meaning |
|--------|---------|
| Predictive mean | Best estimate |
| Predictive std | Uncertainty. Wide = little data nearby |
| Marginal likelihood | Model fit quality. Higher = better kernel |

## References
- Rasmussen & Williams (2006). Gaussian Processes for Machine Learning.
