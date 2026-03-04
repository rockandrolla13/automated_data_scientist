---
name: clustering
description: Use when grouping assets or issuers by behavior patterns or identifying regime clusters in time windows. Includes spectral clustering for non-linear separation.
---

# Clustering

## When to Use
- Grouping assets/issuers by behavior (spread dynamics, return patterns).
- Regime analysis alternative: cluster time windows by feature similarity.
- Dimensionality reduction for visualization (with PCA/UMAP first).
- **Spectral clustering**: when clusters are non-linearly separable.

## Packages
```python
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, SpectralClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score
```

## Corresponding Script
`/scripts/ml_stats/clustering.py`
- `fit_kmeans(X, n_clusters, random_state) -> ClusterResult`
- `fit_dbscan(X, eps, min_samples) -> ClusterResult`
- `select_k(X, k_range) -> pd.DataFrame` — elbow + silhouette for each k
- `cluster_stability(X, n_clusters, n_boots) -> float` — bootstrap stability
- `fit_spectral(X, n_clusters, kernel, **kernel_params) -> ClusterResult`
- `fit_kernel_kmeans(X, n_clusters, kernel, **kernel_params) -> ClusterResult`

## Spectral Clustering
When clusters are non-linearly separable (e.g., credit regimes that overlap in spread-vol space but separate in kernel space). Builds kernel matrix → eigendecompose → k-means on top eigenvectors.

**Use case**: Stress vs normal regimes may form concentric rings in spread-vol space. KMeans fails; spectral with RBF kernel finds them.

**Gotcha**: O(n³) from eigendecomposition. Use Nyström approximation for n > 5000.

## Kernel Selection for Spectral
- **RBF**: default, good for compact clusters
- **Polynomial**: when interactions matter (spread × vol)
- Tune gamma via grid search on silhouette or known label subset

## Gotchas
1. **Scale features first.** KMeans uses Euclidean distance. Unscaled → dominated by largest feature.
2. **Silhouette score.** >0.5 = good, 0.25–0.5 = OK, <0.25 = weak structure.
3. **DBSCAN eps is critical.** Use k-distance plot to choose. Too small → all noise. Too large → one cluster.
4. **Clusters ≠ regimes.** Clusters are static groupings. For temporal regimes, use RegimeDetection.
5. **Spectral clustering**: sensitive to gamma. Start with median heuristic, tune if needed.

## References
- Jain (2010). Data clustering: 50 years beyond K-means.
- Von Luxburg (2007). A tutorial on spectral clustering.
