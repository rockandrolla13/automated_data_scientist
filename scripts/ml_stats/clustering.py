"""clustering — KMeans, DBSCAN, hierarchical clustering with selection diagnostics."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


@dataclass
class ClusterResult:
    labels: np.ndarray
    n_clusters: int
    silhouette: float
    calinski: float
    centers: np.ndarray | None


def fit_kmeans(
    X: np.ndarray | pd.DataFrame,
    n_clusters: int = 3,
    scale: bool = True,
    random_state: int = 42,
) -> ClusterResult:
    """KMeans with optional scaling."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score, calinski_harabasz_score

    X_arr = np.asarray(X)
    if scale:
        X_arr = StandardScaler().fit_transform(X_arr)

    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = km.fit_predict(X_arr)

    return ClusterResult(
        labels=labels, n_clusters=n_clusters,
        silhouette=silhouette_score(X_arr, labels),
        calinski=calinski_harabasz_score(X_arr, labels),
        centers=km.cluster_centers_,
    )


def fit_dbscan(
    X: np.ndarray | pd.DataFrame,
    eps: float = 0.5,
    min_samples: int = 5,
    scale: bool = True,
) -> ClusterResult:
    """DBSCAN clustering."""
    from sklearn.cluster import DBSCAN
    from sklearn.metrics import silhouette_score, calinski_harabasz_score

    X_arr = np.asarray(X)
    if scale:
        X_arr = StandardScaler().fit_transform(X_arr)

    db = DBSCAN(eps=eps, min_samples=min_samples)
    labels = db.fit_predict(X_arr)
    n_clusters = len(set(labels) - {-1})

    sil = silhouette_score(X_arr, labels) if n_clusters > 1 else -1
    cal = calinski_harabasz_score(X_arr, labels) if n_clusters > 1 else 0

    return ClusterResult(labels=labels, n_clusters=n_clusters, silhouette=sil,
                         calinski=cal, centers=None)


def select_k(X: np.ndarray | pd.DataFrame, k_range: range = range(2, 11)) -> pd.DataFrame:
    """Evaluate silhouette and inertia for k in range."""
    rows = []
    for k in k_range:
        result = fit_kmeans(X, n_clusters=k)
        rows.append({"k": k, "silhouette": result.silhouette, "calinski": result.calinski})
    return pd.DataFrame(rows)


def fit_spectral(
    X: np.ndarray | pd.DataFrame,
    n_clusters: int = 3,
    kernel: str = "rbf",
    scale: bool = True,
    random_state: int = 42,
    **kernel_params,
) -> ClusterResult:
    """Spectral clustering for non-linearly separable clusters.

    Args:
        X: Input data
        n_clusters: Number of clusters
        kernel: 'rbf', 'poly', 'sigmoid', 'nearest_neighbors'
        scale: Whether to standardize features
        random_state: Random seed
        **kernel_params: gamma, degree, n_neighbors depending on kernel

    Returns:
        ClusterResult with labels and metrics
    """
    from sklearn.cluster import SpectralClustering
    from sklearn.metrics import silhouette_score, calinski_harabasz_score

    X_arr = np.asarray(X)
    if scale:
        X_arr = StandardScaler().fit_transform(X_arr)

    # Set default gamma (median heuristic)
    if "gamma" not in kernel_params and kernel in ["rbf", "poly", "sigmoid"]:
        from scipy.spatial.distance import pdist
        D_sq = pdist(X_arr, metric="sqeuclidean")
        kernel_params["gamma"] = 1.0 / np.median(D_sq) if np.median(D_sq) > 0 else 1.0

    affinity = kernel if kernel != "poly" else "polynomial"

    sc = SpectralClustering(
        n_clusters=n_clusters,
        affinity=affinity,
        random_state=random_state,
        **kernel_params,
    )
    labels = sc.fit_predict(X_arr)

    sil = silhouette_score(X_arr, labels) if len(set(labels)) > 1 else -1
    cal = calinski_harabasz_score(X_arr, labels) if len(set(labels)) > 1 else 0

    return ClusterResult(
        labels=labels,
        n_clusters=n_clusters,
        silhouette=sil,
        calinski=cal,
        centers=None,  # Spectral doesn't have explicit centers
    )


def fit_kernel_kmeans(
    X: np.ndarray | pd.DataFrame,
    n_clusters: int = 3,
    kernel: str = "rbf",
    scale: bool = True,
    random_state: int = 42,
    **kernel_params,
) -> ClusterResult:
    """Kernel K-means via kernel PCA + K-means.

    Projects to kernel space via kernel PCA, then runs standard K-means.

    Args:
        X: Input data
        n_clusters: Number of clusters
        kernel: Kernel type for embedding
        scale: Whether to standardize
        random_state: Random seed
        **kernel_params: Kernel parameters

    Returns:
        ClusterResult with labels and metrics
    """
    from sklearn.cluster import KMeans
    from sklearn.decomposition import KernelPCA
    from sklearn.metrics import silhouette_score, calinski_harabasz_score

    X_arr = np.asarray(X)
    if scale:
        X_arr = StandardScaler().fit_transform(X_arr)

    # Set default gamma
    if "gamma" not in kernel_params and kernel in ["rbf", "poly", "sigmoid"]:
        from scipy.spatial.distance import pdist
        D_sq = pdist(X_arr, metric="sqeuclidean")
        kernel_params["gamma"] = 1.0 / np.median(D_sq) if np.median(D_sq) > 0 else 1.0

    # Project to kernel space
    n_components = min(n_clusters * 2, X_arr.shape[1], X_arr.shape[0] // 2)
    kpca = KernelPCA(n_components=n_components, kernel=kernel, **kernel_params)
    X_kpca = kpca.fit_transform(X_arr)

    # Run K-means in kernel space
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = km.fit_predict(X_kpca)

    # Compute metrics in original space
    sil = silhouette_score(X_arr, labels) if len(set(labels)) > 1 else -1
    cal = calinski_harabasz_score(X_arr, labels) if len(set(labels)) > 1 else 0

    return ClusterResult(
        labels=labels,
        n_clusters=n_clusters,
        silhouette=sil,
        calinski=cal,
        centers=km.cluster_centers_,  # Centers in kernel space
    )


def cluster_stability(
    X: np.ndarray | pd.DataFrame,
    n_clusters: int = 3,
    n_boots: int = 100,
    method: str = "kmeans",
    random_state: int = 42,
) -> float:
    """Assess cluster stability via bootstrap resampling.

    Args:
        X: Input data
        n_clusters: Number of clusters
        n_boots: Number of bootstrap iterations
        method: 'kmeans' or 'spectral'
        random_state: Random seed

    Returns:
        Mean adjusted Rand index across bootstrap pairs (0-1, higher = more stable)
    """
    from sklearn.metrics import adjusted_rand_score

    rng = np.random.default_rng(random_state)
    X_arr = np.asarray(X)
    n = len(X_arr)

    all_labels = []

    for i in range(n_boots):
        # Bootstrap sample
        idx = rng.choice(n, size=n, replace=True)
        X_boot = X_arr[idx]

        if method == "kmeans":
            result = fit_kmeans(X_boot, n_clusters=n_clusters, random_state=random_state + i)
        else:
            result = fit_spectral(X_boot, n_clusters=n_clusters, random_state=random_state + i)

        all_labels.append((idx, result.labels))

    # Compute pairwise ARI for overlapping samples
    ari_scores = []
    for i in range(len(all_labels)):
        for j in range(i + 1, min(i + 10, len(all_labels))):  # Compare with next 10
            idx_i, labels_i = all_labels[i]
            idx_j, labels_j = all_labels[j]

            # Find overlapping indices
            common = np.intersect1d(idx_i, idx_j)
            if len(common) > n_clusters:
                # Get labels for common samples
                mask_i = np.isin(idx_i, common)
                mask_j = np.isin(idx_j, common)
                ari = adjusted_rand_score(labels_i[mask_i], labels_j[mask_j])
                ari_scores.append(ari)

    return float(np.mean(ari_scores)) if ari_scores else 0.0


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    X = np.vstack([rng.normal(loc=i, size=(50, 3)) for i in range(3)])
    result = fit_kmeans(X, n_clusters=3)
    print(f"KMeans - Silhouette: {result.silhouette:.3f}, Calinski: {result.calinski:.1f}")

    # Spectral clustering example
    spectral_result = fit_spectral(X, n_clusters=3)
    print(f"Spectral - Silhouette: {spectral_result.silhouette:.3f}")

    # Kernel K-means example
    kernel_result = fit_kernel_kmeans(X, n_clusters=3, kernel="rbf")
    print(f"Kernel KMeans - Silhouette: {kernel_result.silhouette:.3f}")
