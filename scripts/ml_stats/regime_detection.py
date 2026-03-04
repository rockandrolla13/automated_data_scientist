"""regime_detection — HMM and GMM regime identification."""

from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class RegimeResult:
    n_states: int
    states: pd.Series
    state_means: np.ndarray
    state_vars: np.ndarray
    transition_matrix: np.ndarray | None
    state_probs: np.ndarray
    log_likelihood: float
    labels: dict  # state_id -> label string


def fit_hmm(
    returns: pd.Series,
    n_states: int = 2,
    n_init: int = 10,
    n_iter: int = 100,
    random_state: int = 42,
) -> RegimeResult:
    """Fit Gaussian HMM. States sorted by ascending variance."""
    from hmmlearn.hmm import GaussianHMM

    r = returns.dropna().values.reshape(-1, 1)
    model = GaussianHMM(
        n_components=n_states, covariance_type="full",
        n_iter=n_iter, random_state=random_state, init_params="stmc",
    )

    best_ll = -np.inf
    best_model = None
    for _ in range(n_init):
        model.random_state = np.random.randint(0, 10000)
        try:
            model.fit(r)
            ll = model.score(r)
            if ll > best_ll:
                best_ll = ll
                best_model = model
        except Exception:
            continue

    if best_model is None:
        raise RuntimeError("HMM failed to converge in any initialization")

    states = best_model.predict(r)
    probs = best_model.predict_proba(r)

    # Sort states by variance (ascending)
    variances = best_model.covars_.flatten() if n_states == 2 else np.array([best_model.covars_[i][0][0] for i in range(n_states)])
    sort_idx = np.argsort(variances)
    state_map = {old: new for new, old in enumerate(sort_idx)}
    states = np.array([state_map[s] for s in states])

    means = best_model.means_.flatten()[sort_idx]
    vars_ = variances[sort_idx]

    labels = {}
    if n_states == 2:
        labels = {0: "low_vol", 1: "high_vol"}
    elif n_states == 3:
        labels = {0: "low_vol", 1: "mid_vol", 2: "high_vol"}

    return RegimeResult(
        n_states=n_states,
        states=pd.Series(states, index=returns.dropna().index, name="regime"),
        state_means=means,
        state_vars=vars_,
        transition_matrix=best_model.transmat_,
        state_probs=probs,
        log_likelihood=best_ll,
        labels=labels,
    )


def fit_gmm(
    returns: pd.Series,
    n_states: int = 2,
    random_state: int = 42,
) -> RegimeResult:
    """Fit Gaussian Mixture (no temporal dependence)."""
    from sklearn.mixture import GaussianMixture

    r = returns.dropna().values.reshape(-1, 1)
    gmm = GaussianMixture(n_components=n_states, random_state=random_state, n_init=5)
    gmm.fit(r)

    states = gmm.predict(r)
    probs = gmm.predict_proba(r)
    means = gmm.means_.flatten()
    vars_ = gmm.covariances_.flatten()

    sort_idx = np.argsort(vars_)
    state_map = {old: new for new, old in enumerate(sort_idx)}
    states = np.array([state_map[s] for s in states])

    return RegimeResult(
        n_states=n_states,
        states=pd.Series(states, index=returns.dropna().index, name="regime"),
        state_means=means[sort_idx],
        state_vars=vars_[sort_idx],
        transition_matrix=None,
        state_probs=probs,
        log_likelihood=gmm.score(r) * len(r),
        labels={0: "low_vol", 1: "high_vol"} if n_states == 2 else {},
    )


def label_regimes(result: RegimeResult) -> pd.Series:
    """Map numeric states to interpretable labels."""
    return result.states.map(result.labels)


if __name__ == "__main__":
    import json
    df = pd.read_parquet("../../data/returns_clean.parquet")
    result = fit_hmm(df.iloc[:, 0], n_states=2)
    print(f"State means: {result.state_means}")
    print(f"State vols: {np.sqrt(result.state_vars)}")
    print(f"Transition matrix:\n{result.transition_matrix}")

    with open("results.json", "w") as f:
        json.dump({
            "state_means": result.state_means.tolist(),
            "state_vols": np.sqrt(result.state_vars).tolist(),
            "log_likelihood": result.log_likelihood,
        }, f, indent=2)
