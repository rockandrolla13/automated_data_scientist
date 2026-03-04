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


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    X = np.vstack([rng.normal(loc=i, size=(50, 3)) for i in range(3)])
    result = fit_kmeans(X, n_clusters=3)
    print(f"Silhouette: {result.silhouette:.3f}, Calinski: {result.calinski:.1f}")
