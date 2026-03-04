---
name: pca
description: Use for dimensionality reduction, identifying latent factors (level, slope, curvature), or removing multicollinearity. Includes kernel PCA for non-linear structure.
---

# PCA — Principal Component Analysis

## When to Use
- Dimensionality reduction before modeling.
- Identifying latent factors in credit spreads (level, slope, curvature).
- Multicollinearity: replace correlated features with orthogonal components.
- **Kernel PCA**: when relationships are non-linear (e.g., spread surface curvature).

## Packages
```python
from sklearn.decomposition import PCA, KernelPCA
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
- `fit_kernel_pca(X, kernel, n_components, **kernel_params) -> KernelPCAResult`
- `select_kernel_pca_components(X, kernel, max_components) -> pd.DataFrame`

## Kernel PCA
When the relationship between features is non-linear (e.g., credit spread surface curvature vs level). Project through kernel-induced feature space.

**Kernels**:
- Polynomial (degree 2-4) for spread interactions
- RBF for regime surfaces

**Gotcha**: No inverse transform — can't reconstruct original space. Use for visualization or downstream modeling, not interpretation.

**Use case**: Spread-vol surface has curvature that linear PCA misses. Kernel PCA with polynomial kernel captures this.

## Gotchas
1. **Scale first.** PCA on unscaled data → dominated by high-variance features.
2. **n_components = 0.95** to auto-select based on variance explained.
3. **Signs are arbitrary.** PC1 loadings might be all negative — flip for interpretation.
4. **Non-linear structure** → use Kernel PCA or UMAP/t-SNE.
5. **Kernel PCA**: no loadings to interpret — use for embedding, not factor identification.

## References
- Jolliffe (2002). Principal Component Analysis.
- Schölkopf et al. (1998). Nonlinear Component Analysis as a Kernel Eigenvalue Problem.
