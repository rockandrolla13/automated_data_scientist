"""hazard_rate_bootstrap — Bootstrap hazard rates from CDS spreads."""

from dataclasses import dataclass
import numpy as np
from scipy.optimize import brentq


@dataclass
class HazardResult:
    tenors: np.ndarray
    hazard_rates: np.ndarray  # piecewise-constant between tenors
    survival_probs: np.ndarray  # at each tenor
    recovery: float


def bootstrap_hazard_rates(
    tenors: np.ndarray,
    spreads_bps: np.ndarray,
    recovery: float = 0.40,
    discount_rates: np.ndarray | None = None,
) -> HazardResult:
    """Bootstrap piecewise-constant hazard rates from CDS spreads.

    Args:
        tenors: CDS maturities in years [1, 3, 5, 7, 10]
        spreads_bps: CDS spreads in basis points
        recovery: Recovery rate (decimal)
        discount_rates: Continuous discount rates per tenor. Default: flat 4%.
    """
    n = len(tenors)
    spreads = spreads_bps / 10000
    if discount_rates is None:
        discount_rates = np.full(n, 0.04)

    lambdas = np.zeros(n)
    surv = np.ones(n + 1)  # surv[0] = 1 at t=0

    for i in range(n):
        s = spreads[i]
        t_start = 0 if i == 0 else tenors[i - 1]
        t_end = tenors[i]
        dt = t_end - t_start
        r = discount_rates[i]

        # Accumulated PV of protection and premium legs from prior intervals
        prot_pv_prior = 0
        prem_pv_prior = 0
        for j in range(i):
            tj0 = 0 if j == 0 else tenors[j - 1]
            tj1 = tenors[j]
            dtj = tj1 - tj0
            df_j = np.exp(-discount_rates[j] * tj1)
            lam_j = lambdas[j]
            # Protection: (1-R) * lambda * integral of surv * df
            prot_pv_prior += (1 - recovery) * lam_j * surv[j] * (1 - np.exp(-lam_j * dtj)) / lam_j * df_j if lam_j > 0 else 0
            # Premium: s * integral of surv * df
            prem_pv_prior += s * surv[j + 1] * dtj * df_j

        def objective(lam):
            if lam < 0:
                return 1e10
            surv_end = surv[i] * np.exp(-lam * dt)
            df = np.exp(-r * t_end)
            # Protection leg for this interval
            prot = (1 - recovery) * surv[i] * (1 - np.exp(-lam * dt)) * df
            # Premium leg for this interval
            prem = s * surv_end * dt * df
            total_prot = prot_pv_prior + prot
            total_prem = prem_pv_prior + prem
            return total_prot - total_prem

        try:
            lam = brentq(objective, 1e-8, 5.0)
        except ValueError:
            lam = spreads[i] / (1 - recovery)  # approximate fallback

        lambdas[i] = max(lam, 0)
        surv[i + 1] = surv[i] * np.exp(-lambdas[i] * dt)

    return HazardResult(
        tenors=tenors, hazard_rates=lambdas,
        survival_probs=surv[1:], recovery=recovery,
    )


def survival_probability(result: HazardResult, t: float) -> float:
    """Interpolate survival probability at arbitrary time t."""
    if t <= 0:
        return 1.0
    cum_hazard = 0
    prev_t = 0
    for i, tenor in enumerate(result.tenors):
        if t <= tenor:
            cum_hazard += result.hazard_rates[i] * (t - prev_t)
            break
        cum_hazard += result.hazard_rates[i] * (tenor - prev_t)
        prev_t = tenor
    else:
        # Extrapolate flat
        cum_hazard += result.hazard_rates[-1] * (t - result.tenors[-1])
    return np.exp(-cum_hazard)


def fair_spread(result: HazardResult, tenor: float, recovery: float | None = None) -> float:
    """Compute fair CDS spread (bps) for a given tenor from bootstrapped curve."""
    R = recovery if recovery is not None else result.recovery
    # Approximate: s ≈ (1-R) × cumulative hazard / tenor
    cum = 0
    prev = 0
    for i, t in enumerate(result.tenors):
        if tenor <= t:
            cum += result.hazard_rates[i] * (tenor - prev)
            break
        cum += result.hazard_rates[i] * (t - prev)
        prev = t
    return cum * (1 - R) * 10000 / max(tenor, 0.01)


if __name__ == "__main__":
    tenors = np.array([1, 3, 5, 7, 10], dtype=float)
    spreads = np.array([50, 80, 100, 115, 130], dtype=float)
    result = bootstrap_hazard_rates(tenors, spreads)
    print("Tenor | Hazard | Survival")
    for i in range(len(tenors)):
        print(f"  {tenors[i]:.0f}Y  | {result.hazard_rates[i]:.4f} | {result.survival_probs[i]:.4f}")
