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


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    X = rng.normal(size=(200, 10))
    X[:, 1] = X[:, 0] * 0.8 + rng.normal(scale=0.3, size=200)  # correlated
    result = fit_pca(X, n_components=0.95)
    print(f"Components: {result.n_components}, Variance: {result.cumulative_variance[-1]:.3f}")
    print(result.loadings.head())
