# Clustering

## When to Use
- Grouping assets/issuers by behavior (spread dynamics, return patterns).
- Regime analysis alternative: cluster time windows by feature similarity.
- Dimensionality reduction for visualization (with PCA/UMAP first).

## Packages
```python
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score
```

## Corresponding Script
`/scripts/ml_stats/clustering.py`
- `fit_kmeans(X, n_clusters, random_state) -> ClusterResult`
- `fit_dbscan(X, eps, min_samples) -> ClusterResult`
- `select_k(X, k_range) -> pd.DataFrame` — elbow + silhouette for each k
- `cluster_stability(X, n_clusters, n_boots) -> float` — bootstrap stability

## Gotchas
1. **Scale features first.** KMeans uses Euclidean distance. Unscaled → dominated by largest feature.
2. **Silhouette score.** >0.5 = good, 0.25–0.5 = OK, <0.25 = weak structure.
3. **DBSCAN eps is critical.** Use k-distance plot to choose. Too small → all noise. Too large → one cluster.
4. **Clusters ≠ regimes.** Clusters are static groupings. For temporal regimes, use RegimeDetection.

## References
- Jain (2010). Data clustering: 50 years beyond K-means.
