# Testable Invariants for Time Series Code

Reference catalogue for the `hypothesis-testing` skill. Each section describes
a class of mathematical or structural property that should hold for time series
code, along with the Hypothesis strategy shape that exposes violations.

The organising principle: **every transform on a time series implies a contract**.
Property-based testing encodes that contract and searches the input space for
counterexamples. The catalogue is ordered from low-level numerical properties
(where violations are silent and dangerous) to high-level pipeline properties
(where violations are visible but expensive to debug).

**Notation.** Throughout, `ts` denotes a 1-d time series (numpy array or pandas
Series with a monotonic temporal index), `X` a multivariate series (n × d),
and `assert_close` means `np.testing.assert_allclose` with stated tolerance.

---

## Table of Contents

1. [Index Integrity](#1-index-integrity) — monotonicity, alignment
2. [Causal Integrity (No-Lookahead)](#2-causal-integrity-no-lookahead) — the master section
   - 2.1 Core property: future-perturbation invariance (reusable template)
   - 2.2 Rolling/expanding window lookahead
   - 2.3 Normalisation and standardisation leakage
   - 2.4 Cross-validation split leakage
   - 2.5 Signal construction leakage (cross-sectional)
   - 2.6 Model fitting and prediction leakage (Kalman, online models)
   - 2.7 Aggregation leakage in resampling
3. [Numerical Stability](#3-numerical-stability) — finite output, scale/translation invariance, PSD
4. [Transform Contracts](#4-transform-contracts) — roundtrip, idempotence, decomposition, dimensions
5. [Statistical Estimator Properties](#5-statistical-estimator-properties) — model-specific
   - 5.1.1 AR / ARMA / ARIMA
   - 5.1.2 GARCH / Stochastic Volatility
   - 5.1.3 Fractional Processes (fBM, MFDFA) — including multifractal spectrum
     - P1: h(q) monotonicity, P2: f(α) concavity, P3: spectrum peak
     - P4: F(q,s) power-law scaling, P5: Δα width recovery
     - P6: Legendre roundtrip (h(q) ↔ f(α)), P7: monofractal limit, P8: scale robustness
   - 5.1.4 State-Space / Kalman Filter
   - 5.2 Permutation invariance
   - 5.3 Sufficient statistic reduction (streaming vs batch)
6. [Rolling / Windowed Computation Properties](#6-rolling--windowed-computation-properties)
7. [Resampling and Frequency Conversion](#7-resampling-and-frequency-conversion)
8. [Pipeline-Level Properties](#8-pipeline-level-properties) — determinism, NaN, dtype, degenerate inputs
9. [Strategy Design Principles](#9-strategy-design-principles) — encode constraints, composite strategies, regime switching

**Appendices**
- [A: Property Checklist by Function Type](#appendix-a-property-checklist-by-function-type)
- [B: Failure-Mode Routing](#appendix-b-failure-mode-routing) — maps suspected issues → test sections
- [C: Lazy Evaluation Gotchas](#appendix-c-lazy-evaluation-gotchas-duckdb--parquet--polars)

---

## 1. Index Integrity

Time series code lives or dies by the index. These properties should be tested
on every function that accepts or returns indexed data.

### 1.1 Monotonicity preservation

If the input index is strictly monotonic, the output index must be strictly
monotonic (or explicitly documented as not preserving order). This catches
silent reindexing, accidental sorts, and off-by-one resampling boundaries.

**Strategy shape:**
```python
sorted_timestamps = st.lists(
    st.datetimes(min_value=dt(2000,1,1), max_value=dt(2030,1,1)),
    min_size=2, unique=True
).map(sorted)
```

**What breaks:** resampling with `closed='left'` vs `closed='right'`, merge
operations that introduce duplicate timestamps, rolling windows that shift
the index.

### 1.2 Alignment invariance

When two time series are aligned (joined, merged, combined), the result must
respect the semantics of the join type. For an inner join: the output index
is the intersection of input indices. For a left join: the output index equals
the left index exactly.

**Strategy shape:**
```python
index_a = draw(sorted_unique_timestamps)
index_b = draw(sorted_unique_timestamps)
# Ensure partial overlap
overlap = set(index_a) & set(index_b)
assume(len(overlap) > 0)
```

---

## 2. Causal Integrity (No-Lookahead)

This is the single most important invariant class in quantitative finance.
Every function, feature, model, and pipeline stage must be testable for
information leakage from the future. Lookahead bugs are uniquely dangerous
because they inflate backtested performance without producing errors, making
them invisible to conventional testing. This section provides a systematic
decomposition of the ways lookahead enters code, with a reusable strategy
template.

### 2.1 The core property: future-perturbation invariance

For any function `f(ts, t) → value`, the output at time `t` must depend only
on `ts[:t+1]` (observations up to and including `t`). Test this by perturbing
`ts[t+1:]` and asserting the output is unchanged.

**Reusable strategy template:**
```python
@st.composite
def causal_test_data(draw, ts_strategy, min_history=10):
    """Generate a time series and a valid split point for causal testing.
    
    Returns (ts_original, ts_perturbed, split_index) where ts_perturbed
    differs from ts_original only at indices > split_index.
    """
    ts = draw(ts_strategy)
    n = len(ts)
    assume(n >= min_history + 2)
    split = draw(st.integers(min_value=min_history, max_value=n - 2))
    
    # Perturb the future — draw entirely fresh values
    future_len = n - split - 1
    future_values = draw(
        arrays(dtype=np.float64, shape=(future_len,),
               elements=st.floats(-1e6, 1e6, allow_nan=False, allow_infinity=False))
    )
    ts_perturbed = ts.copy()
    ts_perturbed[split + 1:] = future_values
    
    return ts, ts_perturbed, split


@given(data=causal_test_data(ar1_series()))
def test_no_lookahead(data):
    ts_orig, ts_pert, t = data
    assert_close(f(ts_orig, t), f(ts_pert, t))
```

This template is the universal starting point. The subsections below identify
specific patterns where lookahead enters code, each requiring a targeted
variant of this test.

### 2.2 Rolling and expanding window lookhead

Centered rolling windows (the pandas default for some operations) use future
observations. This is correct for smoothing in retrospective analysis but
catastrophic in signal construction for trading.

**Specific test:** compare the output of a rolling computation against an
explicit trailing-window slice-and-compute. Any discrepancy at position `t`
that correlates with values at `t+1, ..., t+w//2` indicates a centered window.

```python
@given(
    n=st.integers(min_value=50, max_value=500),
    w=st.integers(min_value=3, max_value=25),
    data=st.data()
)
def test_rolling_is_trailing(n, w, data):
    ts = data.draw(arrays(dtype=float, shape=(n,), elements=finite_floats))
    result = rolling_feature(ts, window=w)
    for i in range(w - 1, n):
        trailing_slice = ts[i - w + 1 : i + 1]
        expected = compute_feature(trailing_slice)
        assert_close(result[i], expected,
                     err_msg=f"Position {i}: rolling != trailing window")
```

**What breaks:** `pd.Series.rolling(w, center=True)`, using `.rolling(w).mean()`
without verifying `center=False`, ewm with `adjust=True` on short windows
where the implicit initialisation reaches into the future via the normalisation.

### 2.3 Normalisation and standardisation leakage

Z-scoring, min-max scaling, or rank transforms computed over the full dataset
leak future distributional information. This is the most common lookahead bug
in feature engineering pipelines.

**Specific test:** fit the scaler on `ts[:t]`, transform `ts[t]`, and compare
against the pipeline's output at `t`. Disagreement means the pipeline fitted
on a larger window.

```python
@given(data=causal_test_data(time_series_strategy()))
def test_normalisation_causal(data):
    ts_orig, ts_pert, t = data
    # Pipeline should produce identical z-score at t regardless of future
    z_orig = pipeline_zscore(ts_orig, at=t)
    z_pert = pipeline_zscore(ts_pert, at=t)
    assert_close(z_orig, z_pert)
```

**What breaks:** `sklearn.preprocessing.StandardScaler` fitted on the full
training set in a walk-forward context, pandas `rank(pct=True)` computed
column-wise over the full DataFrame, quantile binning over the full sample.

### 2.4 Cross-validation split leakage

In time series cross-validation, the test fold must be strictly after the
training fold. No shuffling. The gap between train and test must be at least
as large as the maximum lookahead of any feature (e.g., if a feature uses a
20-day rolling window, the gap must be ≥ 20 days to avoid the window reaching
into the test set).

**Specific test:** for each CV split, verify that `max(train_index) < min(test_index)`
and that the gap satisfies the feature horizon.

```python
@given(
    n=st.integers(min_value=100, max_value=1000),
    n_splits=st.integers(min_value=2, max_value=10),
    max_feature_horizon=st.integers(min_value=1, max_value=30)
)
def test_cv_splits_causal(n, n_splits, max_feature_horizon):
    splits = walk_forward_split(n, n_splits=n_splits)
    for train_idx, test_idx in splits:
        assert train_idx.max() < test_idx.min(), "Train/test overlap"
        gap = test_idx.min() - train_idx.max()
        assert gap >= max_feature_horizon, (
            f"Gap {gap} < feature horizon {max_feature_horizon}: "
            f"features in test set can see training-period data"
        )
```

### 2.5 Signal construction leakage

Trading signals that incorporate information from the full cross-section at
time `t` (e.g., cross-sectional rank, percentile, z-score across assets) are
legitimate — they use only time-`t` data. But signals that use future
cross-sectional snapshots, or that are constructed from a panel with
forward-filled stale data, leak information.

**Specific test:** construct the signal at time `t` using only the panel up to
and including `t`. Compare against the pipeline's output. This is the
multivariate extension of §2.1.

```python
@given(data=st.data())
def test_cross_sectional_signal_causal(data):
    panel = data.draw(panel_strategy)  # n_times × n_assets
    t = data.draw(st.integers(min_value=0, max_value=panel.shape[0] - 2))
    
    signal_full = compute_signal(panel, at=t)
    panel_truncated = panel[:t + 1, :]
    signal_truncated = compute_signal(panel_truncated, at=t)
    assert_close(signal_full, signal_truncated)
```

### 2.6 Model fitting and prediction leakage

The prediction at time `t` must use only a model fitted on data up to `t - h`
where `h` is the prediction horizon. Online/recursive models (Kalman filter,
EWMA, online SGD) must not condition on future observations.

**Specific test:** for a recursive model, the state at time `t` must be
deterministically a function of observations `0, ..., t`. Perturb observation
at `t + 1` and verify the state at `t` is identical.

```python
@given(data=causal_test_data(time_series_strategy()))
def test_kalman_state_causal(data):
    ts_orig, ts_pert, t = data
    # Run filter on both, compare state at split point
    states_orig = kalman_filter(ts_orig)
    states_pert = kalman_filter(ts_pert)
    assert_close(states_orig[t], states_pert[t])
```

**What breaks:** Kalman smoothers (which are intentionally non-causal — make
sure the code uses the filter, not the smoother, when causal output is needed),
models that call `.fit()` then `.predict()` on the same array without temporal
splitting, `statsmodels` functions that default to full-sample estimation.

### 2.7 Aggregation leakage in resampling

When downsampling (e.g., tick → bar, 1min → daily), the aggregation boundary
must be causal. A daily bar at date `d` must aggregate only observations from
`d`, not from `d + 1`. This is particularly treacherous with timezone-aware
data where "end of day" depends on the exchange timezone.

**Specific test:** perturb observations after the boundary timestamp and verify
the aggregated bar is unchanged.

---

## 3. Numerical Stability

### 3.1 Finite output on finite input

Any function that accepts finite floats must return finite floats (no NaN, no
±inf) unless explicitly documented otherwise. This is the baseline sanity
property. Test with the full `st.floats(allow_nan=False, allow_infinity=False)`
range — the extremes (subnormals, large magnitudes) are where instability hides.

**Strategy shape:**
```python
finite_floats = st.floats(
    min_value=-1e15, max_value=1e15,
    allow_nan=False, allow_infinity=False,
    allow_subnormal=True  # deliberate — subnormals expose cancellation bugs
)
```

**What breaks:** log-returns on near-zero prices, variance calculations on
constant series (0/0), normalisation of series with range ≈ machine epsilon.

### 3.2 Scale invariance / equivariance

Many time series statistics should be either scale-invariant (correlation,
Hurst exponent, autocorrelation) or scale-equivariant (mean, standard
deviation). For invariant statistics: `f(c * x) == f(x)` for any `c > 0`.
For equivariant: `f(c * x) == g(c) * f(x)` where `g` is known (e.g., linear).

**Strategy shape:**
```python
scale = draw(st.floats(min_value=1e-6, max_value=1e6))
ts = draw(time_series_strategy)
assert_close(f(scale * ts), f(ts))  # invariant case
```

**What breaks:** implementations that use absolute thresholds internally,
hard-coded epsilon values that assume unit-scale data, estimators that
mix raw and normalised quantities.

### 3.3 Translation invariance / equivariance

Statistics that depend on differences (volatility, returns, autocorrelation)
should be translation-invariant: `f(x + c) == f(x)`. Mean-dependent statistics
should be equivariant: `f(x + c) == f(x) + c`.

**Strategy shape:**
```python
shift = draw(st.floats(min_value=-1e6, max_value=1e6))
```

**What breaks:** implementations that compute `E[X²] - E[X]²` for variance
(catastrophic cancellation at large shift), price-level dependent volatility
estimators applied to shifted series.

### 3.4 Positive semi-definiteness (PSD) preservation

Any function that produces a covariance matrix, correlation matrix, or kernel
matrix must produce a PSD output. Test by checking all eigenvalues ≥ −ε (with
ε a small numerical tolerance). Applies to rolling covariance, shrinkage
estimators, GARCH conditional covariance, Kalman filter state covariance
propagation, and kernel evaluations.

**Strategy shape:**
```python
# Generate a multivariate time series with d assets and n observations
d = draw(st.integers(min_value=2, max_value=20))
n = draw(st.integers(min_value=d+1, max_value=500))
data = draw(arrays(dtype=np.float64, shape=(n, d), elements=finite_floats))
result = covariance_estimator(data)
eigenvalues = np.linalg.eigvalsh(result)
assert np.all(eigenvalues >= -1e-10)
```

**What breaks:** online/streaming covariance updates with numerical drift,
shrinkage estimators that don't enforce PSD on the target, kernel matrices
at very small or very large length scales.

---

## 4. Transform Contracts

### 4.1 Roundtrip / invertibility

If a transform has a documented inverse, the roundtrip must recover the
original within numerical tolerance: `inverse(forward(x)) ≈ x`.

Common pairs in time series: log/exp, diff/cumsum, returns/prices,
z-score/unscale, FFT/IFFT, wavelet decompose/reconstruct.

**Strategy shape:**
```python
ts = draw(time_series_strategy)
reconstructed = inverse(forward(ts))
assert_allclose(reconstructed, ts, atol=1e-10)
```

**What breaks:** `cumsum` after `diff` loses the initial value (off-by-one),
log-return to price reconstruction drifts due to floating-point accumulation,
wavelet reconstruction with truncated coefficients.

### 4.2 Idempotence

Operations that should be idempotent: `f(f(x)) == f(x)`. Applies to
cleaning/preprocessing functions (deduplication, fill missing values, sort
index, clip outliers, resample to regular frequency).

**What breaks:** forward-fill that propagates NaNs differently on a second
pass (because the first pass introduced new non-NaN values at boundaries),
outlier clipping that recomputes quantile thresholds on the clipped data.

### 4.3 Composition / decomposition additivity

Additive decompositions must satisfy `trend + seasonal + residual == original`.
Multiplicative decompositions: `trend * seasonal * residual == original`.
This applies to STL, X-13, Fourier decomposition, EMD, and any custom
decomposition.

**Strategy shape:**
```python
ts = draw(time_series_strategy(min_size=2*period))
trend, seasonal, residual = decompose(ts)
assert_allclose(trend + seasonal + residual, ts)
```

**What breaks:** decompositions that drop boundary observations, seasonal
components that don't exactly sum to zero over a full period (leaking into
trend), edge effects in moving-average trend extraction.

### 4.4 Dimensional consistency

Returns must have length `n-1` (or `n` with NaN/0 at index 0). Rolling
statistics with window `w` must have `w-1` NaN lead-in or length `n-w+1`.
Resampled output must have the correct number of periods. This catches
off-by-one errors that silently misalign signals.

**Strategy shape:**
```python
n = draw(st.integers(min_value=10, max_value=1000))
window = draw(st.integers(min_value=2, max_value=n))
ts = draw(arrays(dtype=float, shape=(n,), elements=finite_floats))
result = rolling_stat(ts, window)
assert len(result) == n  # or n - window + 1, depending on convention
assert np.isnan(result[:window-1]).all()  # if NaN-padded convention
```

---

## 5. Statistical Estimator Properties

### 5.1 Consistency under known DGP — model-specific strategies

When the data-generating process is known, estimators must converge.
Generate synthetic series from a known model and verify estimated parameters
lie within tolerance. Each model family requires a dedicated composite strategy.

**Caution for all consistency tests:** these are probabilistic properties. Use
generous bounds (5σ), `@settings(max_examples=50)`, and `@seed(...)` for
reproducibility. False positives from repeated trials are the main risk.

#### 5.1.1 AR / ARMA / ARIMA

The canonical linear models. Key properties: estimated AR coefficients converge
to true values; MA coefficients are harder (invertibility boundary near
|θ| = 1 causes estimation instability); integrated series require correct
differencing order.

```python
@st.composite
def arma_series(draw, min_size=200, max_size=2000):
    """Generate ARMA(p,q) with known coefficients."""
    p = draw(st.integers(min_value=1, max_value=3))
    q = draw(st.integers(min_value=0, max_value=2))
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    
    # AR coefficients: ensure stationarity (roots outside unit circle)
    # Simple sufficient condition: sum of absolute values < 1
    ar_raw = draw(arrays(dtype=float, shape=(p,),
                         elements=st.floats(-0.4, 0.4)))
    assume(np.sum(np.abs(ar_raw)) < 0.95)
    
    # MA coefficients: ensure invertibility
    ma_raw = draw(arrays(dtype=float, shape=(q,),
                         elements=st.floats(-0.4, 0.4)))
    
    sigma = draw(st.floats(min_value=0.1, max_value=5.0))
    innovations = np.random.default_rng(
        draw(st.integers(0, 2**32 - 1))
    ).normal(0, sigma, size=n + 100)  # burn-in
    
    ts = simulate_arma(ar_raw, ma_raw, innovations)[-n:]
    return ts, {"ar": ar_raw, "ma": ma_raw, "sigma": sigma}
```

**Properties beyond consistency:**
- Stationarity: if `sum(|ar_i|) < 1`, the output process variance should be
  bounded. Test that `np.var(ts)` < an analytical upper bound.
- Residual whiteness: after fitting, residuals should be approximately
  uncorrelated. Test `|acf(residuals, lag)| < 2/sqrt(n)` for lags 1..10.

#### 5.1.2 GARCH / Stochastic Volatility

The key property is that conditional variance is always positive. This is the
GARCH analogue of PSD preservation and is the first thing to test.

```python
@st.composite
def garch_series(draw, min_size=500, max_size=3000):
    """Generate GARCH(1,1) with known parameters."""
    omega = draw(st.floats(min_value=1e-6, max_value=0.1))
    alpha = draw(st.floats(min_value=0.01, max_value=0.3))
    beta = draw(st.floats(min_value=0.3, max_value=0.95))
    assume(alpha + beta < 0.999)  # stationarity
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    
    rng = np.random.default_rng(draw(st.integers(0, 2**32 - 1)))
    z = rng.normal(size=n + 200)
    sigma2 = np.zeros(n + 200)
    sigma2[0] = omega / (1 - alpha - beta)  # unconditional variance
    eps = np.zeros(n + 200)
    for t in range(1, n + 200):
        sigma2[t] = omega + alpha * eps[t-1]**2 + beta * sigma2[t-1]
        eps[t] = z[t] * np.sqrt(sigma2[t])
    
    return eps[-n:], sigma2[-n:], {"omega": omega, "alpha": alpha, "beta": beta}
```

**Properties:**
- Conditional variance positivity: `sigma2_hat[t] > 0` for all `t`.
- Persistence ordering: if `alpha + beta` is high, estimated persistence
  should be high. Not an exact test, but `|estimated_persistence - true| < tol`.
- Leverage asymmetry (if GJR-GARCH): negative returns should produce higher
  next-period variance than equal-magnitude positive returns.
- Unconditional variance: `mean(sigma2) ≈ omega / (1 - alpha - beta)` for
  long samples.

#### 5.1.3 Fractional Processes (fBM, MFDFA)

The Hurst exponent `H` controls the memory structure: `H = 0.5` is Brownian
motion (no memory), `H > 0.5` is persistent, `H < 0.5` is anti-persistent.

**fBM strategy:**
```python
@st.composite
def fbm_series(draw, min_size=500, max_size=5000):
    """Generate fractional Brownian motion with known Hurst exponent."""
    H = draw(st.floats(min_value=0.1, max_value=0.9))
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    seed = draw(st.integers(0, 2**32 - 1))
    
    # Hosking or Cholesky method for exact fBM generation
    ts = simulate_fbm(H, n, seed=seed)
    return ts, {"H": H}
```

**Monofractal (DFA) properties:**
- Hurst exponent recovery: `|H_hat - H_true| < tol(n)` where `tol` decreases
  with sample size. For DFA/MFDFA, the tolerance is wider than for Whittle
  estimation — use `tol ≈ 0.15` at `n = 1000`.
- Self-similarity: for fBM, `f(c^H * B(t/c)) =_d f(B(t))`. In practice, test
  that the estimated Hurst exponent is approximately the same for the series
  and a time-rescaled version.
- Scale invariance of the Hurst estimator itself (§3.2): `H_hat(c * ts) ≈ H_hat(ts)`.
- Increment stationarity: increments of fBM are stationary. Test that
  `mean(increments[:n//2]) ≈ mean(increments[n//2:])` and similarly for
  variance.

##### MFDFA-Specific Spectrum Properties

MFDFA extends DFA by computing a family of fluctuation functions
`F(q, s)` across moment orders `q` and scale `s`, yielding a generalised
Hurst exponent `h(q)` and a singularity spectrum `f(α)` via Legendre
transform. The following properties are algebraic consequences of the
multifractal formalism and must hold for any correct implementation.

**Multifractal cascade strategy:**

For testing MFDFA, monofractal fBM is insufficient — `h(q)` is constant
for fBM, so spectrum-shape properties become trivial. Use a synthetic
multifractal process (binomial cascade, random wavelet cascade, or
multifractal random walk) with known theoretical spectrum.

```python
@st.composite
def binomial_cascade(draw, n_levels=None):
    """Generate a binomial multiplicative cascade with known multifractal width.
    
    The theoretical h(q) for a binomial cascade with parameter m is:
        h(q) = (1/q) * log2(m^q + (1-m)^q) + 1  (for the integrated process)
    The width Δα = |log2(m) - log2(1-m)| controls the degree of multifractality.
    """
    levels = n_levels or draw(st.integers(min_value=10, max_value=16))
    m = draw(st.floats(min_value=0.55, max_value=0.95))  # asymmetry parameter
    seed = draw(st.integers(0, 2**32 - 1))
    
    rng = np.random.default_rng(seed)
    n = 2 ** levels
    measure = np.ones(n)
    for k in range(levels):
        step = n // (2 ** (k + 1))
        for i in range(0, n, 2 * step):
            weight = m if rng.random() < 0.5 else (1 - m)
            measure[i:i+step] *= weight
            measure[i+step:i+2*step] *= (1 - weight)
    
    # Integrate to get a "walk" — MFDFA operates on profiles
    profile = np.cumsum(measure - measure.mean())
    
    params = {"m": m, "n_levels": levels, "delta_alpha": abs(np.log2(m) - np.log2(1-m))}
    return profile, params


@st.composite
def multifractal_random_walk(draw, min_size=2000, max_size=10000):
    """Generate a multifractal random walk (MRW) with known intermittency λ².
    
    The MRW has h(q) = qH - λ²q(q-1)/2 for q < q_crit, giving a parabolic
    spectrum. λ² = 0 recovers monofractal fBM.
    """
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    H = draw(st.floats(min_value=0.3, max_value=0.7))
    lambda_sq = draw(st.floats(min_value=0.01, max_value=0.08))  # intermittency
    integral_scale = draw(st.integers(min_value=n//4, max_value=n//2))
    seed = draw(st.integers(0, 2**32 - 1))
    
    ts = simulate_mrw(H, lambda_sq, integral_scale, n, seed=seed)
    params = {"H": H, "lambda_sq": lambda_sq, "integral_scale": integral_scale}
    return ts, params
```

**P1 — Generalised Hurst exponent h(q) is non-increasing in q:**

For any multifractal process, `h(q)` is a non-increasing function of `q`.
This follows from Jensen's inequality applied to the fluctuation function.
For monofractal processes, `h(q) = const` (the classical Hurst exponent).

```python
@given(data=binomial_cascade())
def test_hq_monotonicity(data):
    ts, params = data
    q_range = np.arange(-5, 6, 0.5)  # avoid q=0
    q_range = q_range[q_range != 0]
    hq = mfdfa(ts, q_range, scales=...)
    
    # h(q) should be non-increasing: h(q_i) >= h(q_{i+1}) for q_i < q_{i+1}
    for i in range(len(q_range) - 1):
        assert hq[i] >= hq[i+1] - 0.05, (  # tolerance for estimation noise
            f"h(q) not monotone: h({q_range[i]:.1f})={hq[i]:.3f} "
            f"< h({q_range[i+1]:.1f})={hq[i+1]:.3f}"
        )
```

**What breaks:** incorrect detrending polynomial order, scale ranges that
include scales too small (< 10 points) or too large (> n/4) where boundary
effects dominate, bugs in the q-weighted averaging of segment fluctuations.

**P2 — Singularity spectrum f(α) is concave:**

The singularity spectrum `f(α)`, obtained from `h(q)` via Legendre transform,
must be a concave function. This is a fundamental property of the multifractal
formalism — `f(α)` is the Legendre transform of `τ(q) = qh(q) - 1`, and
Legendre transforms of convex functions are concave.

```python
@given(data=binomial_cascade())
def test_spectrum_concavity(data):
    ts, params = data
    q_range = np.linspace(-5, 5, 41)
    q_range = q_range[q_range != 0]
    
    alpha, f_alpha = mfdfa_spectrum(ts, q_range, scales=...)
    
    # Sort by α for concavity check
    order = np.argsort(alpha)
    alpha_sorted = alpha[order]
    f_sorted = f_alpha[order]
    
    # Concavity: second differences must be non-positive
    if len(alpha_sorted) >= 3:
        second_diff = np.diff(f_sorted, n=2)
        # Tolerance for numerical estimation noise
        assert np.all(second_diff <= 0.1), (
            f"f(α) not concave: max second difference = {second_diff.max():.4f}"
        )
```

**P3 — Spectrum peak f(α₀) = 1:**

The maximum of the singularity spectrum satisfies `max(f(α)) = 1` (or
equivalently, `f(α₀) = dim_H(support)` which is 1 for a time series on ℝ).
This is the normalisation condition — the most frequent singularity exponent
carries the full measure.

```python
@given(data=binomial_cascade())
def test_spectrum_peak(data):
    ts, params = data
    alpha, f_alpha = mfdfa_spectrum(ts, ...)
    assert abs(np.max(f_alpha) - 1.0) < 0.15, (
        f"Spectrum peak f(α₀) = {np.max(f_alpha):.3f}, expected ≈ 1.0"
    )
```

**What breaks:** incorrect normalisation in the partition function,
using `log` instead of `log2` (or vice versa) in the fluctuation function
computation, wrong sign convention in the Legendre transform.

**P4 — Fluctuation function F(q,s) power-law scaling:**

The fluctuation function `F(q, s)` should scale as `s^h(q)` in the scaling
regime. On a log-log plot of `F(q, s)` vs `s`, the relationship should be
approximately linear. Test that the R² of the linear fit in log-log space
exceeds a threshold (e.g., 0.95) for each `q` in the scaling regime.

```python
@given(data=binomial_cascade())
def test_fluctuation_scaling(data):
    ts, params = data
    q_values = [-3, -1, 1, 3, 5]
    scales = np.logspace(np.log10(10), np.log10(len(ts)//4), 20).astype(int)
    scales = np.unique(scales)
    
    for q in q_values:
        Fq = fluctuation_function(ts, q, scales)
        # Log-log linear fit
        log_s = np.log(scales)
        log_F = np.log(Fq[Fq > 0])  # drop zeros
        if len(log_F) < 5:
            continue
        coeffs = np.polyfit(log_s[:len(log_F)], log_F, 1)
        residuals = log_F - np.polyval(coeffs, log_s[:len(log_F)])
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((log_F - log_F.mean())**2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        assert r_squared > 0.90, (
            f"Poor scaling for q={q}: R²={r_squared:.3f}"
        )
```

**P5 — Multifractal width Δα recovers known cascade parameter:**

For a binomial cascade with parameter `m`, the theoretical spectrum width
`Δα = |log₂(m) - log₂(1−m)|` is known. The estimated width should converge
to this value. This is the multifractal analogue of Hurst exponent recovery.

```python
@given(data=binomial_cascade())
def test_spectrum_width_recovery(data):
    ts, params = data
    alpha, f_alpha = mfdfa_spectrum(ts, ...)
    
    estimated_width = alpha.max() - alpha.min()
    true_width = params["delta_alpha"]
    
    # Wide tolerance — MFDFA spectrum width estimation is noisy
    assert abs(estimated_width - true_width) < 0.3 * true_width + 0.1, (
        f"Δα estimated={estimated_width:.3f}, true={true_width:.3f}"
    )
```

**P6 — Legendre transform consistency (h(q) ↔ f(α) roundtrip):**

The singularity spectrum `f(α)` and the scaling exponent `τ(q) = qh(q) - 1`
are related by Legendre transform. Computing `h(q) → τ(q) → f(α)` and then
inverting via `f(α) → τ(q) → h(q)` should recover the original `h(q)`.

```python
@given(data=binomial_cascade())
def test_legendre_roundtrip(data):
    ts, params = data
    q_range = np.linspace(-5, 5, 41)
    q_range = q_range[q_range != 0]
    
    # Forward: h(q) → τ(q) → (α, f(α))
    hq = mfdfa(ts, q_range, scales=...)
    tau_q = q_range * hq - 1
    alpha_forward = np.gradient(tau_q, q_range)
    f_forward = q_range * alpha_forward - tau_q
    
    # Inverse: (α, f(α)) → τ(q) → h(q)
    # τ(q) = q·α - f(α) where α satisfies f'(α) = q
    # Numerically: for each q, find α that maximises q·α - f(α)
    tau_recovered = np.array([
        np.max(q * alpha_forward - f_forward) for q in q_range
    ])
    hq_recovered = (tau_recovered + 1) / q_range
    
    assert_close(hq, hq_recovered, atol=0.05,
                 err_msg="Legendre roundtrip failed: h(q) not recovered")
```

**What breaks:** numerical differentiation of `τ(q)` using too-coarse `q`
grid, incorrect sign convention (`τ(q) = qh(q) - 1` vs `τ(q) = qH(q)` —
the `−1` is the DFA convention for profiles vs. increments), boundary
effects in the Legendre inversion when `f(α)` is estimated at too few points.

**P7 — Monofractal limit: h(q) = const when λ² = 0:**

When the intermittency parameter is zero, the process is monofractal and
`h(q)` should be constant across all `q`. This is the degenerate-case
sanity check for MFDFA — it should correctly identify a monofractal process
as having zero spectrum width.

```python
@given(data=fbm_series())
def test_monofractal_constant_hq(data):
    ts, params = data
    q_range = np.array([-3, -1, 1, 3, 5])
    hq = mfdfa(ts, q_range, scales=...)
    
    # For fBM, h(q) should be approximately constant
    assert np.std(hq) < 0.1, (
        f"h(q) varies too much for monofractal input: "
        f"std={np.std(hq):.3f}, values={hq}"
    )
```

**P8 — Scale range sensitivity:**

The estimated `h(q)` should be robust to small changes in the scale range
used for the log-log fit. If removing the smallest or largest scale changes
`h(q)` by more than a threshold, the scaling regime is poorly identified.
This is not a pass/fail property but a diagnostic — the skill should flag
fragile scale ranges.

```python
@given(data=binomial_cascade())
def test_scale_range_robustness(data):
    ts, params = data
    scales_full = default_scales(len(ts))
    q_test = np.array([2.0])
    
    hq_full = mfdfa(ts, q_test, scales=scales_full)
    hq_trimmed_low = mfdfa(ts, q_test, scales=scales_full[1:])  # drop smallest
    hq_trimmed_high = mfdfa(ts, q_test, scales=scales_full[:-1])  # drop largest
    
    assert abs(hq_full[0] - hq_trimmed_low[0]) < 0.1, "Sensitive to smallest scale"
    assert abs(hq_full[0] - hq_trimmed_high[0]) < 0.1, "Sensitive to largest scale"
```

#### 5.1.4 State-Space / Kalman Filter

The Kalman filter has rich algebraic structure that produces many testable
properties.

```python
@st.composite
def linear_state_space(draw, dim_state=None, dim_obs=None, n_obs=None):
    """Generate a linear Gaussian state-space model with known parameters."""
    dx = dim_state or draw(st.integers(min_value=1, max_value=5))
    dy = dim_obs or draw(st.integers(min_value=1, max_value=dx))
    n = n_obs or draw(st.integers(min_value=50, max_value=500))
    
    # Transition matrix: stable (spectral radius < 1)
    A_raw = draw(arrays(dtype=float, shape=(dx, dx),
                        elements=st.floats(-0.5, 0.5)))
    # Enforce stability via scaling
    spectral_radius = np.max(np.abs(np.linalg.eigvals(A_raw)))
    if spectral_radius >= 0.99:
        A_raw *= 0.95 / spectral_radius
    
    # Observation matrix
    C = draw(arrays(dtype=float, shape=(dy, dx),
                    elements=st.floats(-2, 2)))
    
    # Noise covariances (must be PSD)
    Q_half = draw(arrays(dtype=float, shape=(dx, dx),
                         elements=st.floats(-1, 1)))
    Q = Q_half @ Q_half.T + 1e-6 * np.eye(dx)
    
    R_half = draw(arrays(dtype=float, shape=(dy, dy),
                         elements=st.floats(-1, 1)))
    R = R_half @ R_half.T + 1e-6 * np.eye(dy)
    
    # Simulate
    rng = np.random.default_rng(draw(st.integers(0, 2**32 - 1)))
    states = np.zeros((n, dx))
    obs = np.zeros((n, dy))
    states[0] = rng.multivariate_normal(np.zeros(dx), Q)
    obs[0] = C @ states[0] + rng.multivariate_normal(np.zeros(dy), R)
    for t in range(1, n):
        states[t] = A_raw @ states[t-1] + rng.multivariate_normal(np.zeros(dx), Q)
        obs[t] = C @ states[t] + rng.multivariate_normal(np.zeros(dy), R)
    
    params = {"A": A_raw, "C": C, "Q": Q, "R": R}
    return obs, states, params
```

**Properties:**
- **PSD of state covariance**: `P_t|t` and `P_t|t-1` must be PSD at every
  time step. This is the most critical numerical property (§3.4 specialised
  to Kalman). Use the Joseph form update `P = (I - KH)P(I - KH)' + KRK'`
  rather than the textbook `P = (I - KH)P` to maintain PSD numerically.
- **Causal state** (§2.6): the filtered state at `t` must not depend on
  observations after `t`. The smoother state intentionally violates this.
- **Innovation whiteness**: the innovations `v_t = y_t - C x_t|t-1` should
  be approximately white noise with covariance `S_t = C P_t|t-1 C' + R`.
  Test `|acf(innovations, lag)| < 2/sqrt(n)`.
- **Steady-state convergence**: for a time-invariant system, `P_t|t → P_∞`
  as `t → ∞`. Test that `||P_t - P_{t-1}|| < ε` after sufficient burn-in.
- **Log-likelihood consistency**: the sum of log-likelihood contributions
  should be a proper probability. Test that it's finite and that increasing
  noise variance decreases the log-likelihood.
- **Filter-smoother ordering**: `trace(P_t|t) ≥ trace(P_t|T)` — the smoother
  must have lower uncertainty than the filter.

### 5.2 Permutation invariance (or non-invariance)

Statistics that should NOT depend on temporal ordering (mean, variance,
histogram) must be permutation-invariant. Statistics that SHOULD depend
on ordering (autocorrelation, Hurst exponent, run tests) must NOT be
permutation-invariant — test that shuffling the series changes the output.

**Strategy shape:**
```python
ts = draw(time_series_strategy)
perm = draw(st.permutations(range(len(ts))))
shuffled = ts[perm]

# For order-independent stats:
assert_close(stat(ts), stat(shuffled))

# For order-dependent stats:
# (use assume to skip pathological cases like constant series)
assume(not np.allclose(ts, ts[0]))
assert not np.isclose(stat(ts), stat(shuffled))
```

### 5.3 Sufficient statistic reduction

If a function computes an online/streaming estimate, it must produce the
same result as the batch computation. This tests that the streaming state
captures the sufficient statistics correctly.

**Strategy shape:**
```python
ts = draw(time_series_strategy(min_size=20))
split = draw(st.integers(min_value=5, max_value=len(ts)-5))
# Batch
batch_result = estimator(ts)
# Streaming: process first chunk, then second
state = estimator_init()
state = estimator_update(state, ts[:split])
state = estimator_update(state, ts[split:])
stream_result = estimator_finalise(state)
assert_close(batch_result, stream_result)
```

---

## 6. Rolling / Windowed Computation Properties

### 6.1 Window boundary correctness

A rolling computation with window size `w` at position `i` must use exactly
observations `[i-w+1, ..., i]` (or the documented convention). Test by
comparing rolling output at each position against an explicit slice-and-compute.

**Strategy shape:**
```python
n = draw(st.integers(min_value=20, max_value=200))
w = draw(st.integers(min_value=2, max_value=n//2))
ts = draw(arrays(dtype=float, shape=(n,), elements=finite_floats))
result = rolling_f(ts, w)
for i in range(w-1, n):
    expected = f(ts[i-w+1:i+1])
    assert_close(result[i], expected)
```

### 6.2 Expanding window monotonicity

For expanding-window computations where the statistic is monotone in sample
size (e.g., expanding max, expanding count of events), the output sequence
must be monotonically non-decreasing.

### 6.3 Rolling vs. batch equivalence at full window

When the window size equals the series length, the rolling output at the
final position must equal the batch statistic over the full series. This
is a degenerate-case sanity check that catches initialisation bugs.

---

## 7. Resampling and Frequency Conversion

### 7.1 Conservation laws

Downsampling with `sum` aggregation must preserve the total:
`resampled.sum() == original.sum()` (up to float tolerance). Analogous
conservation for `count`, and for `mean` weighted by group size.

### 7.2 Frequency relationship

If resampling from frequency `f_high` to `f_low`, the output length must
satisfy `len(output) ≈ len(input) * (f_low / f_high)` within ±1 for
boundary effects.

### 7.3 Upsample-then-downsample roundtrip

Upsampling (with interpolation) then downsampling back to the original
frequency must recover the original values at the original timestamps.
This catches interpolation methods that don't pass through the knot points.

---

## 8. Pipeline-Level Properties

### 8.1 Determinism

`pipeline(data, seed=s) == pipeline(data, seed=s)` for all inputs and seeds.
Non-determinism typically hides in: hash-dependent dict/set iteration order,
uncontrolled random state in cross-validation splits, concurrent data loading
with non-deterministic ordering, GPU non-determinism in cuDNN.

### 8.2 Null propagation contract

Define explicitly how NaN/None flows through the pipeline. Either:
- **Strict:** any NaN in input → NaN in output (or exception). Test by
  injecting a single NaN at a random position and verifying the contract.
- **Tolerant:** NaN is ignored/interpolated. Test that the output is
  finite when the input has scattered NaNs.

**Strategy shape:**
```python
ts = draw(time_series_strategy)
nan_positions = draw(
    st.lists(st.integers(0, len(ts)-1), min_size=1, max_size=len(ts)//4, unique=True)
)
ts_with_nans = ts.copy()
ts_with_nans[nan_positions] = np.nan
result = pipeline(ts_with_nans)
# Assert contract (strict or tolerant, per documentation)
```

### 8.3 Dtype preservation / promotion

If the input is `float64`, the output should be `float64` (not silently
downcast to `float32`). If the input is a pandas Series with a
DatetimeIndex, the output should preserve the index type. Dtype bugs are
silent precision killers.

### 8.4 Empty and degenerate inputs

The pipeline must handle gracefully: empty series, single-observation
series, constant series, series shorter than the minimum window size.
The correct behaviour for each case should be documented and tested —
either a clean exception or a documented default output.

**Strategy shape:**
```python
# Degenerate case: constant series
n = draw(st.integers(min_value=1, max_value=100))
constant = draw(finite_floats)
ts = np.full(n, constant)
# Should not raise, or should raise a documented exception
```

---

## 9. Strategy Design Principles

These are not properties to test but guidelines for writing strategies that
effectively explore the time series input space.

### 9.1 Encode constraints, don't filter

Build strategies that generate valid inputs by construction rather than
filtering invalid ones. Filtering wastes samples and can make Hypothesis
give up.

```python
# BAD — filters most generated values
st.floats().filter(lambda x: 0 < x < 1)

# GOOD — generates in-range by construction
st.floats(min_value=1e-10, max_value=1.0 - 1e-10)
```

### 9.2 Composite strategies for realistic time series

Build time series strategies that reflect the structure of real data:
autocorrelation, heteroscedasticity, regime changes, fat tails. A pure
i.i.d. Gaussian strategy will miss bugs that only manifest under realistic
dependence structure. See §5.1 for model-specific strategies. Below is a
meta-strategy that mixes across model families:

```python
@st.composite
def realistic_time_series(draw, min_size=100, max_size=2000):
    """Draw from a mixture of DGPs to cover diverse dependence structures."""
    model = draw(st.sampled_from(["ar", "garch", "fbm", "regime_switch"]))
    if model == "ar":
        return draw(arma_series(min_size=min_size, max_size=max_size))
    elif model == "garch":
        ts, sigma2, params = draw(garch_series(min_size=min_size, max_size=max_size))
        return ts, params
    elif model == "fbm":
        return draw(fbm_series(min_size=min_size, max_size=max_size))
    elif model == "regime_switch":
        return draw(regime_switching_series(min_size=min_size, max_size=max_size))
```

### 9.3 Regime-switching strategy

Many time series bugs only appear at regime boundaries — a function that
works in calm markets breaks during a volatility spike. This strategy
generates series with abrupt parameter changes.

```python
@st.composite
def regime_switching_series(draw, min_size=200, max_size=2000):
    """AR(1) with regime-switching coefficient and noise scale."""
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    n_regimes = draw(st.integers(min_value=2, max_value=5))
    
    # Draw regime parameters
    phis = draw(arrays(dtype=float, shape=(n_regimes,),
                       elements=st.floats(-0.95, 0.95)))
    sigmas = draw(arrays(dtype=float, shape=(n_regimes,),
                         elements=st.floats(0.1, 10.0)))
    
    # Draw regime durations (Poisson-like)
    breakpoints = sorted(draw(
        st.lists(st.integers(20, n - 20),
                 min_size=n_regimes - 1, max_size=n_regimes - 1, unique=True)
    ))
    segments = [0] + breakpoints + [n]
    
    # Simulate
    rng = np.random.default_rng(draw(st.integers(0, 2**32 - 1)))
    ts = np.zeros(n)
    for r in range(n_regimes):
        start, end = segments[r], segments[r + 1]
        for t in range(max(start, 1), end):
            ts[t] = phis[r] * ts[t-1] + sigmas[r] * rng.normal()
    
    params = {"phis": phis, "sigmas": sigmas, "breakpoints": breakpoints}
    return ts, params
```

### 9.4 Edge case amplification

Explicitly test the boundaries: series of length 1, window equal to series
length, all-NaN series, series with identical values, timestamps with
sub-millisecond resolution, series spanning DST transitions, Feb 29 dates.

### 9.5 Shrinking considerations

Hypothesis shrinks failing examples to minimal reproducers. Time series
strategies should be designed so that shrinking produces interpretable
examples. Use `st.lists(...).map(np.array)` rather than
`arrays(dtype=float, shape=(n,))` when shrinkability matters more than
generation speed.

---

## Appendix A: Property Checklist by Function Type

Quick lookup for which properties to test given the function signature.

| Function type | Properties to test |
|---|---|
| `ts → scalar` (estimator) | Scale invariance/equivariance (§3.2), translation invariance (§3.3), permutation (non-)invariance (§5.2), consistency under known DGP (§5.1), finite output (§3.1), degenerate inputs (§8.4) |
| `ts → ts` (transform) | Roundtrip (§4.1), idempotence (§4.2), dimensional consistency (§4.4), index monotonicity (§1.1), causal integrity (§2.1), NaN propagation (§8.2), dtype preservation (§8.3) |
| `ts → matrix` (covariance etc.) | PSD (§3.4), symmetry, scale equivariance (§3.2), consistency with pairwise computation |
| `(ts, ts) → ts` (combine) | Alignment invariance (§1.2), commutativity (if applicable), identity element |
| `ts, window → ts` (rolling) | Boundary correctness (§6.1), no centered-window lookahead (§2.2), batch equivalence at full window (§6.3), expanding monotonicity (§6.2), dimensional consistency (§4.4) |
| `ts → components` (decompose) | Additivity/multiplicativity (§4.3), completeness, residual orthogonality |
| `ts_high → ts_low` (resample) | Conservation (§7.1), frequency relationship (§7.2), causal aggregation boundary (§2.7), roundtrip (§7.3) |
| `ts → ts` (pipeline) | Determinism (§8.1), causal integrity (§2.1–2.7), NaN contract (§8.2), dtype preservation (§8.3), empty/degenerate handling (§8.4) |
| `(ts, model) → forecast` | Causal state (§2.6), CV split integrity (§2.4), no normalisation leakage (§2.3) |
| `ts → (h(q), f(α))` (MFDFA) | h(q) monotonicity (§5.1.3 P1), f(α) concavity (P2), peak normalisation (P3), power-law scaling (P4), width recovery (P5), Legendre roundtrip (P6), monofractal limit (P7), scale robustness (P8) |

## Appendix B: Failure-Mode Routing

When the `code-review` skill or manual inspection flags a suspected issue,
use this table to select which properties to test. This enables the
`hypothesis-testing` skill to consume findings from the findings registry
and automatically route to the right test section.

| Suspected failure mode | Test sections | Priority |
|---|---|---|
| Lookahead / data snooping | §2.1–2.7 (full causal suite) | 🔴 Critical |
| Numerical instability / NaN | §3.1–3.3 (finite output, scale, translation) | 🔴 Critical |
| Covariance matrix not PSD | §3.4, §5.1.4 (PSD + Kalman properties) | 🔴 Critical |
| MFDFA spectrum shape wrong | §5.1.3 P1–P3 (h(q) monotone, f(α) concave, peak=1) | 🔴 Critical |
| Hurst exponent estimate biased | §5.1.3 monofractal properties + P5 (width recovery) | 🟠 Major |
| Legendre transform inconsistency | §5.1.3 P6 (h(q) ↔ f(α) roundtrip) | 🟠 Major |
| Scaling regime fragile | §5.1.3 P4 (R² check), P8 (scale range sensitivity) | 🟡 Minor |
| Off-by-one in rolling window | §6.1 (boundary correctness), §4.4 (dimensions) | 🟠 Major |
| Wrong differencing / cumsum | §4.1 (roundtrip), §4.4 (dimensions) | 🟠 Major |
| Estimator bias suspected | §5.1 (consistency under known DGP) | 🟠 Major |
| Streaming ≠ batch results | §5.3 (sufficient statistic reduction) | 🟠 Major |
| Resampling drops data | §7.1 (conservation), §7.2 (frequency) | 🟠 Major |
| Regime-boundary crash | §9.3 (regime strategy), §8.4 (degenerate inputs) | 🟡 Minor |
| Pipeline non-deterministic | §8.1 (determinism) | 🟡 Minor |
| Silent dtype downcast | §8.3 (dtype preservation) | 🟡 Minor |

## Appendix C: Lazy Evaluation Gotchas (DuckDB / Parquet / Polars)

When time series code operates on lazily-evaluated backends (DuckDB queries
over Parquet, Polars lazy frames), additional properties must hold that are
trivially satisfied by eager numpy/pandas code.

### C.1 Materialisation equivalence

The result of a lazy pipeline materialised at the end must be identical to
the same operations applied eagerly. This catches: predicate pushdown that
changes filter semantics, column pruning that drops a column used in a
downstream computation, and query optimiser reordering that changes the
result of non-commutative operations (e.g., a limit before vs. after a sort).

```python
@given(data=st.data())
def test_lazy_equals_eager(data):
    ts_eager = data.draw(time_series_strategy)
    ts_lazy = to_lazy(ts_eager)  # e.g., duckdb.from_df() or pl.LazyFrame
    result_eager = pipeline_eager(ts_eager)
    result_lazy = pipeline_lazy(ts_lazy).collect()
    assert_frame_equal(result_eager, result_lazy)
```

### C.2 Partition-boundary correctness

When data is stored across multiple Parquet files (e.g., partitioned by date),
computations that span partition boundaries must produce the same result as
computation on a single contiguous file. This catches: rolling windows that
restart at partition boundaries, GROUP BY aggregations that don't merge
across partitions, and sorts that are only partition-local.

**Strategy shape:** generate a single series, split it at random points into
multiple Parquet files, run the pipeline, and compare against the single-file
result.

### C.3 Row-group and predicate pushdown interaction

DuckDB and Parquet readers use row-group statistics (min/max) for predicate
pushdown. If statistics are stale, missing, or the pushdown logic has an
off-by-one on the boundary, data can be silently dropped. Test by comparing
a filtered scan against a full scan followed by in-memory filter.

### C.4 Timestamp precision across serialisation

Parquet stores timestamps as int64 with a resolution unit (microseconds or
nanoseconds). Roundtripping through Parquet can truncate or shift timestamps
if the resolution doesn't match the source. Test that
`read_parquet(write_parquet(ts)).index == ts.index` exactly.

### C.5 Null semantics mismatch

DuckDB NULL, pandas NaN, numpy NaN, and Polars null have different
propagation semantics in edge cases (e.g., `NULL == NULL` is NULL in SQL
but `np.nan == np.nan` is False in numpy). When a pipeline crosses these
boundaries, null handling must be tested explicitly at the boundary.