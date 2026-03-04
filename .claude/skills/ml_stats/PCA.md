# PCA

## When to Use
- Dimensionality reduction before modeling.
- Identifying latent factors in credit spreads (level, slope, curvature).
- Multicollinearity: replace correlated features with orthogonal components.

## Packages
```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
```

## Mathematical Background
$X = U\Sigma V^T$. PCs are columns of $V$. Variance explained = $\sigma_i^2 / \sum \sigma_j^2$.
In credit: PC1 ≈ level, PC2 ≈ slope, PC3 ≈ curvature (typically >90% variance in 3 PCs).

## Corresponding Script
`/scripts/ml_stats/pca.py`
- `fit_pca(X, n_components) -> PCAResult`
- `scree_plot(result, path)` — variance explained plot
- `interpret_loadings(result, feature_names) -> pd.DataFrame`

## Gotchas
1. **Scale first.** PCA on unscaled data → dominated by high-variance features.
2. **n_components = 0.95** to auto-select based on variance explained.
3. **Signs are arbitrary.** PC1 loadings might be all negative — flip for interpretation.
4. **Non-linear structure → use UMAP/t-SNE** instead.

## References
- Jolliffe (2002). Principal Component Analysis.
