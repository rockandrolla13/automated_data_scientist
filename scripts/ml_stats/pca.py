"""pca — Principal Component Analysis with scree plots and loadings interpretation."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


@dataclass
class PCAResult:
    components: np.ndarray  # (n_components, n_features)
    explained_variance_ratio: np.ndarray
    cumulative_variance: np.ndarray
    n_components: int
    loadings: pd.DataFrame
    transformed: np.ndarray


def fit_pca(
    X: np.ndarray | pd.DataFrame,
    n_components: int | float = 0.95,
    scale: bool = True,
    feature_names: list[str] | None = None,
) -> PCAResult:
    """Fit PCA. n_components=float selects by variance explained threshold."""
    if isinstance(X, pd.DataFrame):
        feature_names = feature_names or list(X.columns)
        X_arr = X.values
    else:
        X_arr = np.asarray(X)
        feature_names = feature_names or [f"f{i}" for i in range(X_arr.shape[1])]

    if scale:
        X_arr = StandardScaler().fit_transform(X_arr)

    pca = PCA(n_components=n_components)
    transformed = pca.fit_transform(X_arr)

    pc_names = [f"PC{i+1}" for i in range(pca.n_components_)]
    loadings = pd.DataFrame(pca.components_.T, index=feature_names, columns=pc_names)

    return PCAResult(
        components=pca.components_,
        explained_variance_ratio=pca.explained_variance_ratio_,
        cumulative_variance=np.cumsum(pca.explained_variance_ratio_),
        n_components=pca.n_components_,
        loadings=loadings,
        transformed=transformed,
    )


def scree_plot(result: PCAResult, path: str | None = None):
    """Plot variance explained per component."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(1, result.n_components + 1)
    ax.bar(x, result.explained_variance_ratio, alpha=0.6, label="Individual")
    ax.plot(x, result.cumulative_variance, "ro-", label="Cumulative")
    ax.axhline(0.95, ls="--", color="gray", alpha=0.5)
    ax.set_xlabel("Component")
    ax.set_ylabel("Variance Explained")
    ax.set_title("Scree Plot")
    ax.legend()
    if path:
        from pathlib import Path as P
        P(path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
    return fig


def interpret_loadings(result: PCAResult, top_n: int = 5) -> pd.DataFrame:
    """Top contributors per component."""
    rows = []
    for col in result.loadings.columns:
        top = result.loadings[col].abs().nlargest(top_n)
        for feat, val in top.items():
            rows.append({"component": col, "feature": feat,
                         "loading": result.loadings.loc[feat, col], "abs_loading": val})
    return pd.DataFrame(rows)


@dataclass
class KernelPCAResult:
    transformed: np.ndarray  # (n_samples, n_components)
    n_components: int
    kernel: str
    kernel_params: dict
    eigenvalues: np.ndarray


def fit_kernel_pca(
    X: np.ndarray | pd.DataFrame,
    kernel: str = "rbf",
    n_components: int = 5,
    scale: bool = True,
    **kernel_params,
) -> KernelPCAResult:
    """Fit Kernel PCA for non-linear dimensionality reduction.

    Args:
        X: Input data
        kernel: 'rbf', 'poly', 'sigmoid', 'cosine', 'linear'
        n_components: Number of components
        scale: Whether to standardize features first
        **kernel_params: gamma, degree, coef0 depending on kernel

    Returns:
        KernelPCAResult with transformed data and eigenvalues
    """
    from sklearn.decomposition import KernelPCA

    if isinstance(X, pd.DataFrame):
        X_arr = X.values
    else:
        X_arr = np.asarray(X)

    if scale:
        X_arr = StandardScaler().fit_transform(X_arr)

    # Set default gamma if not provided (median heuristic)
    if "gamma" not in kernel_params and kernel in ["rbf", "poly", "sigmoid"]:
        from scipy.spatial.distance import pdist
        D_sq = pdist(X_arr, metric="sqeuclidean")
        kernel_params["gamma"] = 1.0 / np.median(D_sq) if np.median(D_sq) > 0 else 1.0

    kpca = KernelPCA(n_components=n_components, kernel=kernel, **kernel_params)
    transformed = kpca.fit_transform(X_arr)

    return KernelPCAResult(
        transformed=transformed,
        n_components=n_components,
        kernel=kernel,
        kernel_params=kernel_params,
        eigenvalues=kpca.eigenvalues_ if hasattr(kpca, "eigenvalues_") else np.array([]),
    )


def select_kernel_pca_components(
    X: np.ndarray | pd.DataFrame,
    kernel: str = "rbf",
    max_components: int = 10,
    scale: bool = True,
    **kernel_params,
) -> pd.DataFrame:
    """Analyze eigenvalue spectrum to select number of kernel PCA components.

    Args:
        X: Input data
        kernel: Kernel type
        max_components: Maximum components to compute
        scale: Whether to standardize
        **kernel_params: Kernel parameters

    Returns:
        DataFrame with component, eigenvalue, cumulative proportion
    """
    from sklearn.decomposition import KernelPCA

    if isinstance(X, pd.DataFrame):
        X_arr = X.values
    else:
        X_arr = np.asarray(X)

    if scale:
        X_arr = StandardScaler().fit_transform(X_arr)

    if "gamma" not in kernel_params and kernel in ["rbf", "poly", "sigmoid"]:
        from scipy.spatial.distance import pdist
        D_sq = pdist(X_arr, metric="sqeuclidean")
        kernel_params["gamma"] = 1.0 / np.median(D_sq) if np.median(D_sq) > 0 else 1.0

    kpca = KernelPCA(n_components=max_components, kernel=kernel, **kernel_params)
    kpca.fit(X_arr)

    eigenvalues = kpca.eigenvalues_ if hasattr(kpca, "eigenvalues_") else np.ones(max_components)
    total = np.sum(np.abs(eigenvalues))
    cumulative = np.cumsum(np.abs(eigenvalues)) / total if total > 0 else np.arange(1, max_components + 1) / max_components

    return pd.DataFrame({
        "component": range(1, len(eigenvalues) + 1),
        "eigenvalue": eigenvalues,
        "proportion": np.abs(eigenvalues) / total if total > 0 else np.ones(len(eigenvalues)) / len(eigenvalues),
        "cumulative": cumulative,
    })


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    X = rng.normal(size=(200, 10))
    X[:, 1] = X[:, 0] * 0.8 + rng.normal(scale=0.3, size=200)  # correlated
    result = fit_pca(X, n_components=0.95)
    print(f"PCA - Components: {result.n_components}, Variance: {result.cumulative_variance[-1]:.3f}")
    print(result.loadings.head())

    # Kernel PCA example
    kpca_result = fit_kernel_pca(X, kernel="rbf", n_components=5)
    print(f"\nKernel PCA - Components: {kpca_result.n_components}, Kernel: {kpca_result.kernel}")
    print(f"Transformed shape: {kpca_result.transformed.shape}")
