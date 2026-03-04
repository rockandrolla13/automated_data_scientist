"""transition_matrix — Rating migration estimation, multi-period, stress testing."""

from dataclasses import dataclass
import numpy as np
from scipy.linalg import expm, logm


STANDARD_STATES = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D"]


@dataclass
class TransitionResult:
    matrix: np.ndarray
    states: list[str]
    n_observations: int


def estimate_cohort(
    ratings_start: np.ndarray,
    ratings_end: np.ndarray,
    states: list[str] | None = None,
) -> TransitionResult:
    """Cohort method: count transitions over one period."""
    states = states or STANDARD_STATES
    n_states = len(states)
    state_idx = {s: i for i, s in enumerate(states)}

    P = np.zeros((n_states, n_states))
    counts = np.zeros(n_states)

    for s, e in zip(ratings_start, ratings_end):
        if s in state_idx and e in state_idx:
            i, j = state_idx[s], state_idx[e]
            P[i, j] += 1
            counts[i] += 1

    # Normalize rows
    for i in range(n_states):
        if counts[i] > 0:
            P[i] /= counts[i]
        else:
            P[i, i] = 1.0  # no observations → assume no transition

    # Enforce absorbing default state
    default_idx = state_idx.get("D", n_states - 1)
    P[default_idx] = 0
    P[default_idx, default_idx] = 1

    return TransitionResult(matrix=P, states=states, n_observations=int(counts.sum()))


def multi_period(P: np.ndarray, years: int) -> np.ndarray:
    """Compute multi-year transition matrix via eigendecomposition."""
    return np.linalg.matrix_power(P, years)


def generator_from_transition(P: np.ndarray) -> np.ndarray:
    """Extract generator matrix Q from 1-year transition matrix P."""
    Q = logm(P).real
    # Fix: off-diagonal should be non-negative, diagonal negative
    n = Q.shape[0]
    for i in range(n):
        for j in range(n):
            if i != j:
                Q[i, j] = max(Q[i, j], 0)
        Q[i, i] = -np.sum(Q[i, [k for k in range(n) if k != i]])
    return Q


def stressed_matrix(P: np.ndarray, stress_factor: float = 2.0) -> np.ndarray:
    """Scale off-diagonal migration probabilities by stress_factor."""
    n = P.shape[0]
    P_stressed = P.copy()
    for i in range(n):
        off_diag = np.sum(P[i]) - P[i, i]
        if off_diag > 0 and off_diag * stress_factor < 1:
            scale = stress_factor
        else:
            scale = min(stress_factor, 0.99 / off_diag) if off_diag > 0 else 1

        for j in range(n):
            if i != j:
                P_stressed[i, j] = P[i, j] * scale
        P_stressed[i, i] = 1 - np.sum(P_stressed[i, [k for k in range(n) if k != i]])

    return P_stressed


def default_probability(P: np.ndarray, rating: str, horizon: int, states: list[str] | None = None) -> float:
    """Cumulative default probability over horizon years."""
    states = states or STANDARD_STATES
    idx = states.index(rating)
    default_idx = states.index("D")
    P_h = multi_period(P, horizon)
    return P_h[idx, default_idx]


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    n = 5000
    states = STANDARD_STATES
    starts = rng.choice(states[:7], size=n, p=[0.05, 0.1, 0.2, 0.3, 0.2, 0.1, 0.05])
    ends = starts.copy()
    # Simulate some transitions
    for i in range(n):
        if rng.random() < 0.1:
            idx = states.index(starts[i])
            new_idx = min(max(idx + rng.choice([-1, 1]), 0), 7)
            ends[i] = states[new_idx]

    result = estimate_cohort(starts, ends, states)
    print(f"Transition matrix ({result.n_observations} obs):")
    print(np.round(result.matrix, 3))
    print(f"\n5Y default prob for BBB: {default_probability(result.matrix, 'BBB', 5):.4%}")
