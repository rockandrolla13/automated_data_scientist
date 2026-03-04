"""
Kernel Methods — compute and analyze kernel matrices.

Usage:
    from scripts.ml_stats.kernel_methods import compute_kernel_matrix, recommend_kernel

    K = compute_kernel_matrix(X, kernel="rbf", gamma=1.0)
    K_centered = center_kernel(K)
    recommendation = recommend_kernel(X, task_type="clustering")
"""
from dataclasses import dataclass
from typing import Literal, Optional, Union

import numpy as np
from scipy.spatial.distance import cdist, pdist, squareform


@dataclass
class KernelRecommendation:
    """Kernel recommendation result."""
    kernel: str
    params: dict
    reasoning: str


def compute_kernel_matrix(
    X: np.ndarray,
    kernel: Literal["rbf", "matern32", "matern52", "polynomial", "linear"] = "rbf",
    Y: Optional[np.ndarray] = None,
    **params,
) -> np.ndarray:
    """Compute kernel matrix K where K[i,j] = k(X[i], Y[j]).

    Args:
        X: Input data, shape (n_samples, n_features)
        kernel: Kernel type
        Y: Optional second input (default: Y=X for square kernel)
        **params: Kernel parameters (gamma, degree, coef0, length_scale)

    Returns:
        Kernel matrix, shape (n_X, n_Y)
    """
    if Y is None:
        Y = X

    if kernel == "linear":
        return X @ Y.T

    elif kernel == "rbf":
        gamma = params.get("gamma", 1.0 / X.shape[1])
        D = cdist(X, Y, metric="sqeuclidean")
        return np.exp(-gamma * D)

    elif kernel == "matern32":
        length_scale = params.get("length_scale", 1.0)
        D = cdist(X, Y, metric="euclidean") / length_scale
        return (1 + np.sqrt(3) * D) * np.exp(-np.sqrt(3) * D)

    elif kernel == "matern52":
        length_scale = params.get("length_scale", 1.0)
        D = cdist(X, Y, metric="euclidean") / length_scale
        return (1 + np.sqrt(5) * D + 5/3 * D**2) * np.exp(-np.sqrt(5) * D)

    elif kernel == "polynomial":
        degree = params.get("degree", 3)
        gamma = params.get("gamma", 1.0 / X.shape[1])
        coef0 = params.get("coef0", 1.0)
        return (gamma * (X @ Y.T) + coef0) ** degree

    else:
        raise ValueError(f"Unknown kernel: {kernel}")


def center_kernel(K: np.ndarray) -> np.ndarray:
    """Center kernel matrix in feature space.

    K_centered = H @ K @ H where H = I - 1/n

    Args:
        K: Kernel matrix, shape (n, n)

    Returns:
        Centered kernel matrix
    """
    n = K.shape[0]
    one_n = np.ones((n, n)) / n

    # K_centered = K - 1_n @ K - K @ 1_n + 1_n @ K @ 1_n
    K_centered = K - one_n @ K - K @ one_n + one_n @ K @ one_n

    return K_centered


def kernel_alignment(K1: np.ndarray, K2: np.ndarray) -> float:
    """Compute kernel alignment (similarity between two kernels).

    Alignment = <K1, K2>_F / (||K1||_F ||K2||_F)

    Args:
        K1: First kernel matrix
        K2: Second kernel matrix

    Returns:
        Alignment score in [0, 1]
    """
    # Frobenius inner product
    numerator = np.sum(K1 * K2)

    # Frobenius norms
    norm1 = np.sqrt(np.sum(K1**2))
    norm2 = np.sqrt(np.sum(K2**2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(numerator / (norm1 * norm2))


def median_heuristic_gamma(X: np.ndarray) -> float:
    """Compute gamma for RBF kernel using median heuristic.

    gamma = 1 / median(||x_i - x_j||^2)

    Args:
        X: Input data

    Returns:
        Recommended gamma value
    """
    # Compute pairwise squared distances
    D_sq = pdist(X, metric="sqeuclidean")

    median_dist_sq = np.median(D_sq)

    if median_dist_sq == 0:
        return 1.0

    return 1.0 / median_dist_sq


def recommend_kernel(
    X: np.ndarray,
    task_type: Literal["gp", "pca", "clustering", "regression"] = "gp",
) -> KernelRecommendation:
    """Recommend kernel based on data characteristics and task.

    Args:
        X: Input data
        task_type: Type of task

    Returns:
        KernelRecommendation with kernel name, params, and reasoning
    """
    n_samples, n_features = X.shape

    # Compute basic statistics
    gamma = median_heuristic_gamma(X)

    # Check for potential periodicity (crude heuristic)
    has_periodicity = False
    if n_features == 1 and n_samples > 50:
        from scipy import signal
        # Check for peaks in FFT
        fft = np.abs(np.fft.fft(X.flatten()))
        peaks, _ = signal.find_peaks(fft[:len(fft)//2], height=np.max(fft) * 0.3)
        has_periodicity = len(peaks) > 1

    # Task-specific recommendations
    if task_type == "gp":
        # GP: prefer Matérn 5/2 for smooth, well-behaved posteriors
        return KernelRecommendation(
            kernel="matern52",
            params={"length_scale": 1.0 / np.sqrt(gamma)},
            reasoning="Matérn 5/2 is twice-differentiable, good default for GP regression. "
                     "Provides smooth but flexible posterior. Adjust length_scale via MLE."
        )

    elif task_type == "pca":
        # Kernel PCA: RBF is standard
        return KernelRecommendation(
            kernel="rbf",
            params={"gamma": gamma},
            reasoning=f"RBF with median heuristic gamma={gamma:.4f}. "
                     "Standard choice for kernel PCA. Will capture non-linear structure."
        )

    elif task_type == "clustering":
        # Spectral clustering: RBF
        return KernelRecommendation(
            kernel="rbf",
            params={"gamma": gamma},
            reasoning=f"RBF with gamma={gamma:.4f} (median heuristic). "
                     "Standard for spectral clustering. Adjust if clusters too connected/disconnected."
        )

    elif task_type == "regression":
        # Check if interactions likely (multiple features)
        if n_features > 3:
            return KernelRecommendation(
                kernel="polynomial",
                params={"degree": 2, "gamma": 1.0/n_features, "coef0": 1.0},
                reasoning="Polynomial degree 2 to capture feature interactions. "
                         "Consider RBF if non-linearities are more complex."
            )
        else:
            return KernelRecommendation(
                kernel="rbf",
                params={"gamma": gamma},
                reasoning=f"RBF with gamma={gamma:.4f}. "
                         "Good general-purpose kernel for non-linear regression."
            )

    # Default fallback
    return KernelRecommendation(
        kernel="rbf",
        params={"gamma": gamma},
        reasoning="Default RBF kernel with median heuristic."
    )


def nystrom_approximation(
    X: np.ndarray,
    kernel: str = "rbf",
    n_components: int = 100,
    random_state: int = 42,
    **kernel_params,
) -> tuple[np.ndarray, np.ndarray]:
    """Nyström low-rank approximation of kernel matrix.

    For large datasets where full kernel matrix is infeasible.
    K ≈ C @ W^{-1} @ C.T

    Args:
        X: Input data
        kernel: Kernel type
        n_components: Number of landmark points
        random_state: Random seed
        **kernel_params: Kernel parameters

    Returns:
        (embedding, landmarks): Low-rank embedding and landmark indices
    """
    np.random.seed(random_state)

    n = len(X)
    n_components = min(n_components, n)

    # Sample landmark points
    landmarks = np.random.choice(n, size=n_components, replace=False)
    X_landmarks = X[landmarks]

    # Compute kernel between all points and landmarks
    C = compute_kernel_matrix(X, kernel=kernel, Y=X_landmarks, **kernel_params)

    # Compute kernel between landmarks
    W = compute_kernel_matrix(X_landmarks, kernel=kernel, **kernel_params)

    # Regularize W for numerical stability
    W += 1e-8 * np.eye(n_components)

    # Compute W^{-1/2}
    eigvals, eigvecs = np.linalg.eigh(W)
    eigvals = np.maximum(eigvals, 1e-10)
    W_sqrt_inv = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T

    # Embedding: each row is the approximate kernel feature for that point
    embedding = C @ W_sqrt_inv

    return embedding, landmarks


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)

    # Generate sample data
    X = np.random.randn(100, 5)

    # Compute different kernels
    K_rbf = compute_kernel_matrix(X, kernel="rbf", gamma=0.1)
    K_matern = compute_kernel_matrix(X, kernel="matern52", length_scale=1.0)
    K_poly = compute_kernel_matrix(X, kernel="polynomial", degree=2)

    print("=== Kernel Methods Demo ===")
    print(f"Data shape: {X.shape}")
    print(f"RBF kernel shape: {K_rbf.shape}")
    print(f"Kernel alignment (RBF vs Matern): {kernel_alignment(K_rbf, K_matern):.3f}")
    print(f"Kernel alignment (RBF vs Poly): {kernel_alignment(K_rbf, K_poly):.3f}")

    # Get recommendation
    rec = recommend_kernel(X, task_type="gp")
    print(f"\nRecommendation for GP: {rec.kernel}")
    print(f"Params: {rec.params}")
    print(f"Reasoning: {rec.reasoning}")

    # Nyström approximation
    embedding, landmarks = nystrom_approximation(X, kernel="rbf", n_components=20)
    print(f"\nNyström embedding shape: {embedding.shape}")
    print(f"Number of landmarks: {len(landmarks)}")
