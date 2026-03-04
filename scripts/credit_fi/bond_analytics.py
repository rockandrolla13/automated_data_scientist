"""bond_analytics — Bond pricing, yield, duration, convexity, scenario analysis."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.optimize import brentq


@dataclass
class BondMetrics:
    price: float
    ytm: float
    macaulay_duration: float
    modified_duration: float
    convexity: float
    dv01: float  # dollar value of 1bp


def price_bond(
    face: float,
    coupon_rate: float,
    maturity: float,
    ytm: float,
    freq: int = 2,
) -> float:
    """Price a fixed-rate bond."""
    n_periods = int(maturity * freq)
    c = face * coupon_rate / freq
    y = ytm / freq
    if y == 0:
        return c * n_periods + face

    pv_coupons = c * (1 - (1 + y)**(-n_periods)) / y
    pv_face = face / (1 + y)**n_periods
    return pv_coupons + pv_face


def ytm_from_price(
    price: float,
    face: float,
    coupon_rate: float,
    maturity: float,
    freq: int = 2,
) -> float:
    """Solve for yield-to-maturity given price."""
    def obj(y):
        return price_bond(face, coupon_rate, maturity, y, freq) - price
    return brentq(obj, -0.05, 1.0)


def duration_convexity(
    face: float,
    coupon_rate: float,
    maturity: float,
    ytm: float,
    freq: int = 2,
) -> BondMetrics:
    """Compute Macaulay duration, modified duration, convexity, DV01."""
    n = int(maturity * freq)
    c = face * coupon_rate / freq
    y = ytm / freq
    P = price_bond(face, coupon_rate, maturity, ytm, freq)

    # Macaulay duration
    mac_dur = 0
    conv = 0
    for i in range(1, n + 1):
        t = i / freq
        cf = c if i < n else c + face
        df = (1 + y)**(-i)
        mac_dur += t * cf * df
        conv += cf * i * (i + 1) * df

    mac_dur /= P
    mod_dur = mac_dur / (1 + y)
    conv = conv / (P * freq**2 * (1 + y)**2)
    dv01 = mod_dur * P / 10000

    return BondMetrics(
        price=P, ytm=ytm, macaulay_duration=mac_dur,
        modified_duration=mod_dur, convexity=conv, dv01=dv01,
    )


def scenario_analysis(
    face: float,
    coupon_rate: float,
    maturity: float,
    ytm: float,
    yield_shocks_bps: list[int] | None = None,
    freq: int = 2,
) -> pd.DataFrame:
    """Price impact under parallel yield shocks."""
    if yield_shocks_bps is None:
        yield_shocks_bps = [-100, -50, -25, -10, 0, 10, 25, 50, 100]

    base = price_bond(face, coupon_rate, maturity, ytm, freq)
    metrics = duration_convexity(face, coupon_rate, maturity, ytm, freq)

    rows = []
    for shock in yield_shocks_bps:
        dy = shock / 10000
        new_ytm = ytm + dy
        exact_price = price_bond(face, coupon_rate, maturity, new_ytm, freq)
        approx_price = base * (1 - metrics.modified_duration * dy + 0.5 * metrics.convexity * dy**2)
        rows.append({
            "shock_bps": shock,
            "new_ytm_pct": new_ytm * 100,
            "exact_price": exact_price,
            "approx_price": approx_price,
            "pnl": exact_price - base,
            "pnl_pct": (exact_price - base) / base * 100,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    metrics = duration_convexity(100, 0.05, 10, 0.04)
    print(f"Price: {metrics.price:.4f}")
    print(f"Mac Duration: {metrics.macaulay_duration:.3f}")
    print(f"Mod Duration: {metrics.modified_duration:.3f}")
    print(f"Convexity: {metrics.convexity:.3f}")
    print(f"DV01: {metrics.dv01:.4f}")

    scenario = scenario_analysis(100, 0.05, 10, 0.04)
    print(scenario.to_string(index=False))
