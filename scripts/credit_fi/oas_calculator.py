"""oas_calculator — Z-spread and OAS computation."""

from dataclasses import dataclass
import numpy as np
from scipy.optimize import brentq


@dataclass
class OASResult:
    spread_bps: float
    model_price: float
    market_price: float


def z_spread(
    market_price: float,
    cash_flows: np.ndarray,
    cash_flow_times: np.ndarray,
    spot_rates: np.ndarray,
) -> float:
    """Compute Z-spread (bps). Constant spread over spot curve matching market price."""
    def price_at_spread(z):
        z_dec = z / 10000
        pv = sum(cf / (1 + r + z_dec)**(t) for cf, t, r in zip(cash_flows, cash_flow_times, spot_rates))
        return pv - market_price

    spread = brentq(price_at_spread, -500, 5000)
    return spread


def z_spread_continuous(
    market_price: float,
    cash_flows: np.ndarray,
    cash_flow_times: np.ndarray,
    spot_rates: np.ndarray,
) -> float:
    """Z-spread with continuous compounding."""
    def price_at_spread(z):
        z_dec = z / 10000
        pv = sum(cf * np.exp(-(r + z_dec) * t) for cf, t, r in zip(cash_flows, cash_flow_times, spot_rates))
        return pv - market_price

    return brentq(price_at_spread, -500, 5000)


def spread_duration(
    cash_flows: np.ndarray,
    cash_flow_times: np.ndarray,
    spot_rates: np.ndarray,
    oas_bps: float,
    bump_bps: float = 1.0,
) -> float:
    """Spread duration: price sensitivity to 1bp spread change."""
    z = oas_bps / 10000

    def price(s):
        return sum(cf * np.exp(-(r + s) * t) for cf, t, r in zip(cash_flows, cash_flow_times, spot_rates))

    p_up = price(z + bump_bps / 10000)
    p_dn = price(z - bump_bps / 10000)
    p_mid = price(z)

    return -(p_up - p_dn) / (2 * bump_bps / 10000 * p_mid)


if __name__ == "__main__":
    # 5-year 5% coupon bond, semi-annual
    cfs = np.array([2.5]*9 + [102.5])
    times = np.arange(0.5, 5.5, 0.5)
    spots = np.full(10, 0.04)  # flat 4% spot curve

    market_px = 98.0
    z = z_spread(market_px, cfs, times, spots)
    print(f"Z-spread: {z:.1f} bps")
    sd = spread_duration(cfs, times, spots, z)
    print(f"Spread duration: {sd:.3f}")
