---
name: kernel-methods
description: Reference skill for choosing and computing kernels across GP, kernel PCA, spectral clustering. When to use RBF vs Matérn vs polynomial.
---

# Kernel Methods — Foundation for Non-Linear Learning

## When to Use
- Features have non-linear relationships (GP, kernel PCA, spectral clustering)
- Need to choose between kernel functions
- Computing or analyzing kernel matrices
- Feature engineering via kernel embeddings

## Packages
- `sklearn.metrics.pairwise` — kernel computations
- `sklearn.gaussian_process.kernels` — GP kernel objects
- `scipy.spatial.distance` — distance matrices

## Functions (scripts/ml_stats/kernel_methods.py)

### `compute_kernel_matrix(X, kernel_fn, **params)`
Compute n×n kernel matrix K where K[i,j] = k(xᵢ, xⱼ).

### `center_kernel(K)`
Center kernel matrix in feature space: K_c = HKH where H = I - 1/n.

### `kernel_alignment(K1, K2)`
Measure similarity between kernels (0-1 scale). High alignment → similar feature spaces.

### `recommend_kernel(X, task_type)`
Heuristic kernel recommendation based on data characteristics.

## Common Kernels

| Kernel | Formula | When to Use |
|--------|---------|-------------|
| **RBF (Gaussian)** | exp(-γ‖x-y‖²) | Default choice, smooth functions |
| **Matérn 3/2** | (1+√3d)exp(-√3d) | Rough but continuous (spreads) |
| **Matérn 5/2** | (1+√5d+5d²/3)exp(-√5d) | Twice differentiable, good default for GP |
| **Polynomial** | (γx·y + c)^d | Interactions (spread × vol) |
| **Linear** | x·y | Baseline, equivalent to linear model |
| **Periodic** | exp(-2sin²(π|x-y|/p)/l²) | Seasonal patterns |

## Finance Use Cases
1. **GP on spreads** — Matérn 5/2 for smooth spread surfaces, Matérn 3/2 for regime jumps
2. **Kernel PCA on factors** — RBF to capture non-linear factor loadings
3. **Spectral clustering** — RBF to find non-linear regimes in spread-vol space
4. **Credit surface interpolation** — Polynomial for rating × maturity interactions

## Kernel Selection Guide

```
Is the function smooth?
├─ Yes → RBF or Matérn 5/2
│   └─ Need uncertainty? → GP with Matérn 5/2
│   └─ Just similarity? → RBF (sklearn default)
├─ No, has jumps → Matérn 1/2 or 3/2
└─ Has interactions? → Polynomial (degree 2-3)

Is there periodicity?
├─ Yes → Periodic or Periodic × RBF
└─ No → Use above

Large dataset (n > 5000)?
├─ Yes → Consider Nyström approximation
└─ No → Full kernel OK
```

## Hyperparameters

| Kernel | Key Param | Effect |
|--------|-----------|--------|
| RBF | γ (length_scale⁻²) | Small γ → wide, smooth. Large γ → local, wiggly. |
| Matérn | ν | 1/2 → rough. 3/2 → once diff. 5/2 → twice diff. |
| Polynomial | degree | 2-3 typical. Higher → overfit risk. |

## Gotchas
- **Kernel matrix size** — O(n²) memory. Nyström for n > 5000.
- **Centering** — Required for kernel PCA. Not for GP.
- **Length scale** — Cross-validate or use median heuristic (γ = 1/median(‖xᵢ-xⱼ‖²)).
- **Mixed scales** — Standardize features before kernel computation.

## References
- Rasmussen & Williams "Gaussian Processes for Machine Learning" Ch. 4
- Schölkopf & Smola "Learning with Kernels"
