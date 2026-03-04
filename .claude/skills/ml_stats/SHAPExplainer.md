# SHAPExplainer

## When to Use
- Explaining black-box model predictions (tree models, neural nets, any sklearn model).
- Feature importance with theoretical guarantees (Shapley values).
- Debugging: why did the model predict X for this observation?

## Packages
```python
import shap
```

## Corresponding Script
`/scripts/ml_stats/shap_explainer.py`
- `explain_model(model, X, feature_names) -> SHAPResult`
- `plot_summary(result, path)` — beeswarm plot
- `plot_dependence(result, feature, path)` — partial dependence

## Gotchas
1. **TreeExplainer is fast** for tree models. KernelExplainer is slow but model-agnostic.
2. **Background data for KernelExplainer.** Use `shap.kmeans(X, 50)` for large datasets.
3. **SHAP values are additive.** sum(SHAP values) + base_value = prediction.
4. **Don't confuse global vs local.** Summary plot = global. Force plot = local.

## References
- Lundberg & Lee (2017). A Unified Approach to Interpreting Model Predictions.
- SHAP: https://shap.readthedocs.io/
