"""hypothesis_testing — Statistical tests with effect sizes and multiple comparison correction."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class TestResult:
    test_name: str
    statistic: float
    p_value: float
    effect_size: float | None
    n_a: int
    n_b: int
    significant_at_05: bool
    alternative: str


@dataclass
class CorrectedResult:
    original_pvalues: np.ndarray
    corrected_pvalues: np.ndarray
    reject: np.ndarray
    method: str
    alpha: float


def two_sample_test(
    a: np.ndarray | pd.Series,
    b: np.ndarray | pd.Series,
    test: str = "auto",
    alternative: str = "two-sided",
) -> TestResult:
    """Two-sample test. Auto selects t-test or Mann-Whitney based on normality."""
    a, b = np.asarray(a).ravel(), np.asarray(b).ravel()
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]

    if test == "auto":
        # Shapiro-Wilk on smaller sample
        n_check = min(len(a), len(b), 5000)
        _, p_norm = stats.shapiro(a[:n_check])
        test = "ttest" if p_norm > 0.05 else "mannwhitney"

    if test == "ttest":
        stat, p = stats.ttest_ind(a, b, alternative=alternative)
        name = "Welch t-test"
    elif test == "mannwhitney":
        stat, p = stats.mannwhitneyu(a, b, alternative=alternative)
        name = "Mann-Whitney U"
    elif test == "ks":
        stat, p = stats.ks_2samp(a, b)
        name = "Kolmogorov-Smirnov"
    else:
        raise ValueError(f"Unknown test: {test}")

    # Cohen's d
    pooled_std = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    cohens_d = (np.mean(a) - np.mean(b)) / pooled_std if pooled_std > 0 else None

    return TestResult(
        test_name=name, statistic=stat, p_value=p,
        effect_size=cohens_d, n_a=len(a), n_b=len(b),
        significant_at_05=p < 0.05, alternative=alternative,
    )


def paired_test(
    a: np.ndarray | pd.Series,
    b: np.ndarray | pd.Series,
    test: str = "auto",
) -> TestResult:
    """Paired test (e.g., comparing model A vs B on same folds)."""
    a, b = np.asarray(a).ravel(), np.asarray(b).ravel()
    diff = a - b
    diff = diff[~np.isnan(diff)]

    if test == "auto":
        _, p_norm = stats.shapiro(diff[:5000])
        test = "ttest" if p_norm > 0.05 else "wilcoxon"

    if test == "ttest":
        stat, p = stats.ttest_rel(a[:len(diff)], b[:len(diff)])
        name = "Paired t-test"
    else:
        stat, p = stats.wilcoxon(diff)
        name = "Wilcoxon signed-rank"

    d = np.mean(diff) / np.std(diff, ddof=1) if np.std(diff) > 0 else None

    return TestResult(
        test_name=name, statistic=stat, p_value=p,
        effect_size=d, n_a=len(diff), n_b=len(diff),
        significant_at_05=p < 0.05, alternative="two-sided",
    )


def multiple_test_correction(
    pvalues: np.ndarray | list[float],
    method: str = "fdr_bh",
    alpha: float = 0.05,
) -> CorrectedResult:
    """Correct for multiple comparisons. Methods: bonferroni, fdr_bh, holm."""
    from statsmodels.stats.multitest import multipletests

    pvals = np.asarray(pvalues)
    reject, corrected, _, _ = multipletests(pvals, alpha=alpha, method=method)

    return CorrectedResult(
        original_pvalues=pvals, corrected_pvalues=corrected,
        reject=reject, method=method, alpha=alpha,
    )


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    a = rng.normal(0.001, 0.02, 500)
    b = rng.normal(0.0005, 0.02, 500)
    result = two_sample_test(a, b)
    print(f"{result.test_name}: stat={result.statistic:.3f}, p={result.p_value:.4f}, d={result.effect_size:.3f}")
