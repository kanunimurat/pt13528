# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Functions without a printed example in the standard, against values worked out by hand.

Every expected value below is written as plain arithmetic or as a quantile taken
directly from SciPy, not through the library.
"""
import math

import numpy as np
import pytest
from scipy import stats

from pt13528 import assigned_value, graphics, homogeneity, outliers, record, robust, scores, sigma_pt


# ---------------------------------------------------------------- Clause 8
def test_horwitz_three_branches():
    assert sigma_pt.horwitz(1e-8) == pytest.approx(0.22 * 1e-8, rel=1e-12)
    assert sigma_pt.horwitz(1.19e-7) == pytest.approx(0.22 * 1.19e-7, rel=1e-12)
    assert sigma_pt.horwitz(1.2e-7) == pytest.approx(0.02 * 1.2e-7 ** 0.8495, rel=1e-12)
    assert sigma_pt.horwitz(0.01) == pytest.approx(0.02 * 0.01 ** 0.8495, rel=1e-12)
    assert sigma_pt.horwitz(0.138) == pytest.approx(0.02 * 0.138 ** 0.8495, rel=1e-12)
    assert sigma_pt.horwitz(0.139) == pytest.approx(0.01 * math.sqrt(0.139), rel=1e-12)
    assert sigma_pt.horwitz(0.5) == pytest.approx(0.01 * math.sqrt(0.5), rel=1e-12)


def test_from_precision_with_three_replicates():
    assert sigma_pt.from_precision(5.0, 3.0, 3) == pytest.approx(math.sqrt(25.0 - 9.0 * 2.0 / 3.0), rel=1e-12)
    assert sigma_pt.from_precision(5.0, 3.0, 1) == pytest.approx(5.0, rel=1e-12)


def test_fit_previous_rounds_slope_and_intercept():
    fit = sigma_pt.fit_previous_rounds([1.0, 2.0, 3.0, 4.0], [3.0, 5.0, 7.0, 9.0])     # y = 1 + 2 x
    assert fit.slope == pytest.approx(2.0) and fit.intercept == pytest.approx(1.0)
    assert fit.r_squared == pytest.approx(1.0) and fit.predict(10.0) == pytest.approx(21.0)


def test_limit_sigma():
    assert sigma_pt.limit_sigma(1.0, lower=2.0) == 2.0
    assert sigma_pt.limit_sigma(5.0, upper=3.0) == 3.0
    assert sigma_pt.limit_sigma(2.5, lower=2.0, upper=3.0) == 2.5


# ---------------------------------------------------------------- Clause 7 and 9
def test_compare_with_reference_limit_is_two():
    assert not assigned_value.compare_with_reference(10.0, 3.0, 0.0, 4.0).investigate     # 10 / 5 = 2
    assert assigned_value.compare_with_reference(10.1, 3.0, 0.0, 4.0).investigate


def test_signal_limits():
    assert scores.classify_z(2.0, action=2.0, warning=None) == "acceptable"               # 9.4.2 NOTE 1
    assert scores.classify_z(2.01, action=2.0, warning=None) == "action"
    assert scores.classify_z(2.0) == "acceptable" and scores.classify_z(2.5) == "warning"
    assert scores.classify_z(3.0) == "action" and scores.classify_z(-3.0) == "action"
    assert scores.classify_d(0.99, 1.0) == "acceptable" and scores.classify_d(-1.0, 1.0) == "action"
    assert scores.classify_en(0.99) == "acceptable" and scores.classify_en(-1.0) == "action"


def test_criteria_based_on_delta_e_use_one_tenth():
    assert scores.uncertainty_negligible(0.09, delta_e=1.0) and not scores.uncertainty_negligible(0.11, delta_e=1.0)
    assert scores.uncertainty_negligible(0.29, sigma_pt=1.0) and not scores.uncertainty_negligible(0.31, sigma_pt=1.0)
    h = homogeneity.homogeneity([[1.0, 1.2], [1.1, 1.3], [1.0, 1.2]], delta_e=2.0)
    assert h.criterion == pytest.approx(0.2)
    assert homogeneity.homogeneity_single([1.0, 1.1, 1.2], delta_e=2.0).criterion == pytest.approx(0.2)
    st = homogeneity.stability([1.0, 1.0], [1.15, 1.15], delta_e=2.0)
    assert st.criterion == pytest.approx(0.2) and st.stable
    assert not homogeneity.stability([1.0, 1.0], [1.25, 1.25], delta_e=2.0).stable
    assert graphics.bandwidth(10, delta_e=2.0) == pytest.approx(0.5)
    assert graphics.bandwidth(10, sigma_pt=2.0) == pytest.approx(1.5)
    assert graphics.bandwidth(32, robust_sd=2.0) == pytest.approx(0.9 * 2.0 / 2.0)        # 32 ** 0.2 = 2


def test_record_difference_is_result_minus_assigned_value():
    rec = record.round_record([9.0, 12.0], x_pt=10.0, u_x_pt=0.1, sigma_pt=1.0)
    assert [r.difference for r in rec.participants] == [-1.0, 2.0]
    assert [r.score for r in rec.participants] == [-1.0, 2.0]


# ---------------------------------------------------------------- Annex B
def test_homogeneity_with_three_replicates():
    x = [[2.0, 4.0, 6.0], [4.0, 6.0, 8.0], [8.0, 10.0, 12.0]]    # item means 4, 6, 10; every within-item variance 4
    h = homogeneity.homogeneity(x, sigma_pt=1.0)
    assert h.s_x == pytest.approx(math.sqrt(28.0 / 3.0))
    assert h.s_w == pytest.approx(2.0)
    assert h.s_s == pytest.approx(math.sqrt(28.0 / 3.0 - 4.0 / 3.0))
    g, m = 3, 3
    f1 = stats.chi2.ppf(0.95, g - 1) / (g - 1)
    fm = (stats.f.ppf(0.95, g - 1, g * (m - 1)) - 1.0) / m
    assert homogeneity.expanded_criterion_factors(g, m) == pytest.approx((f1, fm))
    assert h.expanded_criterion == pytest.approx(math.sqrt(f1 * 0.3 ** 2 + fm * 4.0))
    assert h.f_statistic == pytest.approx(3 * (28.0 / 3.0) / 4.0)
    assert h.f_critical == pytest.approx(stats.f.ppf(0.95, 2, 6))


def test_homogeneity_single_uses_the_sample_standard_deviation():
    h = homogeneity.homogeneity_single([1.0, 2.0, 3.0], sigma_pt=4.0)
    assert h.s_s == pytest.approx(1.0) and h.criterion == pytest.approx(1.2) and h.sufficient


def test_expanded_stability_criterion():
    st = homogeneity.stability([10.0, 10.0], [10.9, 10.9], sigma_pt=1.0, u_y1=0.3, u_y2=0.4)
    assert st.difference == pytest.approx(0.9) and not st.stable
    assert st.expanded_criterion == pytest.approx(0.3 + 2 * 0.5) and st.stable_expanded


def test_stability_t_test_is_welch_by_default():
    a, b = [10.0, 10.1, 9.9, 10.0], [10.0, 12.0, 8.0, 10.4]
    t, df, p, sig = homogeneity.stability_t_test(a, b)
    va, vb = np.var(a, ddof=1) / 4, np.var(b, ddof=1) / 4
    assert t == pytest.approx((np.mean(a) - np.mean(b)) / math.sqrt(va + vb))
    assert df == pytest.approx((va + vb) ** 2 / (va ** 2 / 3 + vb ** 2 / 3))
    assert homogeneity.stability_t_test(a, b, equal_var=True)[1] == pytest.approx(6.0)


# ---------------------------------------------------------------- outlier tests of ISO 5725-2
def test_grubbs_and_cochran_statistics():
    hi, lo, crit = outliers.grubbs([1.0, 2.0, 3.0, 4.0, 10.0])   # mean 4, s = sqrt(50 / 4)
    s = math.sqrt(50.0 / 4.0)
    assert hi == pytest.approx(6.0 / s) and lo == pytest.approx(3.0 / s)
    assert crit == pytest.approx(1.764, abs=5e-4)                # ISO 5725-2, n = 5, 1 %
    c, crit_c, idx = outliers.cochran([1.0, 2.0, 3.0, 6.0], n=2)
    assert c == pytest.approx(0.5) and idx == 3
    assert crit_c == pytest.approx(0.968, abs=5e-4)              # ISO 5725-2, p = 4, n = 2, 1 %


# ---------------------------------------------------------------- Clauses 10 and 11
def test_repeatability_region_and_statistic():
    chi = -2.0 * math.log(0.01)                                  # chi-squared, 2 degrees of freedom, 99 %
    x, lo, hi = graphics.repeatability_region(10.0, 2.0, m=4, points=3)
    assert x[0] == pytest.approx(10.0 - 2.0 * math.sqrt(chi / 4)) and x[2] == pytest.approx(10.0 + 2.0 * math.sqrt(chi / 4))
    e = math.sqrt(chi / (2 * 3))
    assert lo[1] == pytest.approx(2.0 * math.exp(-e)) and hi[1] == pytest.approx(2.0 * math.exp(e))
    assert lo[0] == pytest.approx(2.0, rel=1e-6) and hi[2] == pytest.approx(2.0, rel=1e-6)
    assert graphics.repeatability_statistic(11.0, 2.0 * math.e, 10.0, 2.0, 4) == pytest.approx(4 * 0.25 + 2 * 3 * 1.0)


def test_ordinal_summary():
    assert graphics.ordinal_summary({1: 3, 2: 1, 3: 1}) == {"mode": 1, "median": 1, "n": 5}
    assert graphics.ordinal_summary({1: 1, 2: 1, 3: 5}) == {"mode": 3, "median": 3, "n": 7}
    assert graphics.ordinal_summary({1: 2, 2: 3, 3: 2})["median"] == 2


# ---------------------------------------------------------------- Annex C
def test_qn_as_first_printed_in_2022():
    x = [1.0, 2.0, 4.0, 8.0]                                     # differences 1, 2, 3, 4, 6, 7; h = 2, k = 1
    assert robust.qn(x, h_rule="iso-literal") == pytest.approx(2.2219 * 1.0 * 0.5132)
    assert robust.qn(x) == pytest.approx(2.2191 * 3.0 * 0.5132)  # h = 3, k = 3


def test_algorithm_s_one_degree_of_freedom():
    w = np.array([0.2, 0.5, 0.1, 0.4, 0.3, 0.6, 2.0])            # Table C.1, nu = 1: eta 1,645, xi 1,097
    ws = float(np.median(w))
    for _ in range(200):
        ws = 1.097 * math.sqrt(np.mean(np.minimum(w, 1.645 * ws) ** 2))
    assert robust.algorithm_s(w, 1).location == pytest.approx(ws, rel=1e-8)


def test_algorithm_a_starts_from_the_standard_deviation_when_made_is_zero():
    x = [5.0, 5.0, 5.0, 5.0, 6.0, 7.0, 9.0]                      # C.3.1 NOTE 2: MADe = 0
    assert robust.made(x) == 0.0
    r = robust.algorithm_a(x)
    assert not r.degenerate and r.scale > 0
    assert r.scale == pytest.approx(robust.algorithm_a(x, scale=float(np.std(x, ddof=1))).scale, rel=1e-9)
    xs, ss = 5.0, float(np.std(x, ddof=1))                       # the same iteration written out
    a = np.array(x)
    for _ in range(500):
        c = np.clip(a, xs - 1.5 * ss, xs + 1.5 * ss)
        xs, ss = float(c.mean()), 1.134 * float(np.std(c, ddof=1))
    assert r.scale == pytest.approx(ss, rel=1e-8) and r.location == pytest.approx(xs, abs=1e-8)


def test_hampel_iterative_agrees_with_finite_step():
    rng = np.random.default_rng(3)
    for _ in range(50):
        x = rng.normal(10, 1, 25)
        x[:2] += 8
        s = robust.q_method(x)
        assert robust.hampel(x, s, "iterative") == pytest.approx(robust.hampel(x, s), abs=0.01 * s)
    y = [0.0, 1.0, 2.0, 10.0]                                    # weights by hand at x* = 1, s = 1: 1, 1, 1, 0
    assert robust.hampel(y, 1.0, "iterative") == pytest.approx(1.0)


def test_q_method_does_not_merge_distinct_differences():
    rng = np.random.default_rng(8)
    for p in (12, 100):
        x = np.round(rng.normal(0, 0.01, p), 6)
        assert robust.q_method(x + 1000.0) == pytest.approx(robust.q_method(x), rel=1e-6)
    y = [1000.001, 1000.002, 1000.004, 1000.008, 1000.016, 1000.032]
    assert robust.q_method(y) == pytest.approx(robust.q_method([v - 1000.0 for v in y]), rel=1e-9)


def test_result_objects():
    import copy
    r = robust.algorithm_a([1.0, 2.0, 3.0, 9.0])
    assert copy.deepcopy(r) == r and not hasattr(r, "nothing") and getattr(r, "nothing", None) is None
    assert robust.q_hampel([1.0, 2.0, 3.0, 9.0]).degenerate is False
    assert assigned_value.consensus([1, 1, 1, 1, 1, 1, 2]).degenerate
    assert not assigned_value.consensus([1, 2, 3, 4, 5, 6, 9]).degenerate
    for bad in ("12345", b"123", {1: 2, 3: 4, 5: 6}):
        with pytest.raises(TypeError):
            robust.median(bad)


# ---------------------------------------------------------------- added in 0.1.6
def test_repeatability_statistic_with_a_logarithm_other_than_one():
    # Formula (23): 4 (11 - 10)^2 / 2^2 + 2 (4 - 1) ln(3 / 2)^2 = 1 + 6 x 0,164402
    assert graphics.repeatability_statistic(11.0, 3.0, 10.0, 2.0, 4) == pytest.approx(1.0 + 6 * 0.1644019, abs=1e-6)


def test_combine_uncertainty_with_four_terms():
    assert assigned_value.combine_uncertainty(1.0, 2.0, 3.0, 4.0) == pytest.approx(math.sqrt(30.0))   # Formula (3)


def test_table_c1_follows_from_the_chi_squared_distribution():
    """eta = sqrt(chi2_0.9(nu) / nu) and xi = 1 / sqrt(F_{nu+2}(nu eta^2) + 0,1 eta^2), where F is the
    chi-squared distribution function (ISO 5725-5). The printed three decimals agree within one unit
    of the last digit."""
    for nu, (eta, xi) in robust._ALG_S.items():
        e = math.sqrt(stats.chi2.ppf(0.9, nu) / nu)
        x = 1 / math.sqrt(stats.chi2.cdf(nu * e * e, nu + 2) + 0.1 * e * e)
        assert eta == pytest.approx(e, abs=6e-4), nu
        assert xi == pytest.approx(x, abs=1.1e-3), nu
    assert sorted(robust._ALG_S) == list(range(1, 11))


@pytest.mark.parametrize("nu,eta,xi", [(2, 1.517, 1.054), (4, 1.395, 1.032), (5, 1.359, 1.027), (6, 1.332, 1.024),
                                       (7, 1.310, 1.021), (8, 1.292, 1.019), (9, 1.277, 1.018), (10, 1.264, 1.017)])
def test_algorithm_s_other_degrees_of_freedom(nu, eta, xi):
    w = np.array([0.2, 0.5, 0.1, 0.4, 0.3, 0.6, 2.0])            # the last value is limited for every nu
    ws = float(np.median(w))
    for _ in range(300):
        ws = xi * math.sqrt(np.mean(np.minimum(w, eta * ws) ** 2))
    assert robust.algorithm_s(w, nu).location == pytest.approx(ws, rel=1e-8)
    assert 2.0 > eta * ws


def test_algorithm_s_three_figure_rule():
    w = [0.2, 0.5, 0.1, 0.4, 0.3, 0.6, 2.0]
    r, full = robust.algorithm_s(w, 1, tol="sig3"), robust.algorithm_s(w, 1)
    assert 1 < r.iterations < full.iterations
    assert r.scale == pytest.approx(0.5403, abs=5e-5) and full.scale == pytest.approx(0.5409, abs=5e-5)


def test_qn_correction_factor_for_more_than_twelve_results():
    x = [float(v * v) for v in range(1, 15)]                     # p = 14 (even): Formula (C.21)
    d = sorted(b - a for i, a in enumerate(x) for b in x[i + 1:])
    h = 14 // 2 + 1
    r = (1 / 14) * (3.6756 + (1 / 14) * (1.965 + (1 / 14) * (6.987 - 77 / 14)))
    assert robust.qn(x) == pytest.approx(2.2191 * d[h * (h - 1) // 2 - 1] / (r + 1), rel=1e-12)
    x = x[:13]                                                   # p = 13 (odd): Formula (C.20)
    d = sorted(b - a for i, a in enumerate(x) for b in x[i + 1:])
    h = 13 // 2 + 1
    r = (1 / 13) * (1.6019 + (1 / 13) * (-2.128 - 5.172 / 13))
    assert robust.qn(x) == pytest.approx(2.2191 * d[h * (h - 1) // 2 - 1] / (r + 1), rel=1e-12)


def test_hampel_iterative_weights():
    # psi sums to zero at m = 0,25 for (0, 0, 0, 4) and at m = 0,5 for (0, 0, 0, 2), scale 1:
    # -3 m + (4,5 - (4 - m)) = 0 and -3 m + 1,5 = 0. The iteration stops within 0,01 s / sqrt(p).
    assert robust.hampel([0, 0, 0, 4], 1.0) == pytest.approx(0.25, abs=1e-9)
    assert robust.hampel([0, 0, 0, 2], 1.0) == pytest.approx(0.5, abs=1e-9)
    assert robust.hampel([0, 0, 0, 4], 1.0, "iterative") == pytest.approx(0.25, abs=0.004)
    assert robust.hampel([0, 0, 0, 2], 1.0, "iterative") == pytest.approx(0.5, abs=0.004)
    # (0, 0, 0, 2,5): -3 m + 1,5 = 0 again, and the last result has |q| = 2, weight 1,5 / 2
    assert robust.hampel([0, 0, 0, 2.5], 1.0) == pytest.approx(0.5, abs=1e-9)
    assert robust.hampel([0, 0, 0, 2.5], 1.0, "iterative") == pytest.approx(0.5, abs=0.004)


def test_q_hampel_with_identical_results_and_flag_limits():
    r = robust.q_hampel([5.0, 5.0, 5.0, 5.0])
    assert r.degenerate and r.scale == 0.0 and r.location == 5.0
    assert not robust.q_hampel([5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 9.0]).degenerate   # ties shift the quantile (C.24)
    assert scores.uncertainty_flag(0.10, 0.10, 0.30) == "a" and scores.uncertainty_flag(0.30, 0.10, 0.30) == "a"
    assert scores.uncertainty_flag(0.0999, 0.10, 0.30) == "b" and scores.uncertainty_flag(0.3001, 0.10, 0.30) == "c"


def test_small_cases_and_limits():
    r = robust.algorithm_a([1.0, 3.0])                           # two results: x* = 2, MADe = 1,483, nothing is winsorized
    assert not r.degenerate and r.location == pytest.approx(2.0) and r.scale == pytest.approx(1.134 * math.sqrt(2.0))
    assert robust.algorithm_a([4.0]).degenerate and robust.algorithm_a([4.0]).iterations == 0
    assert scores.en_score(1.0, 0.0, 0.0, 2.0) == pytest.approx(0.5)             # one expanded uncertainty may be zero
    assert scores.zeta_score(1.0, 0.0, 0.0, 2.0) == pytest.approx(0.5)
    assert not scores.uncertainty_negligible(0.1, delta_e=1.0)                   # 9.2.1: u < 0,1 delta_E, strictly
    assert scores.uncertainty_negligible(0.0999, delta_e=1.0)
    assert not scores.uncertainty_negligible(0.3, sigma_pt=1.0) and scores.uncertainty_negligible(0.2999, sigma_pt=1.0)
    stat, _crit, idx = outliers.cochran([0.01, 0.02, 0.03, 0.2], n=3)            # variances that sum to less than one
    assert stat == pytest.approx(0.2 / 0.26) and idx == 3
    assert sigma_pt.horwitz(1.0) == pytest.approx(0.01)                           # c = 1: 0,01 c^0,5
    with pytest.raises(ValueError):
        sigma_pt.horwitz(1.5)


def test_result_details():
    r = robust.algorithm_a([7.0, 7.0, 7.0])
    assert r.degenerate and r.iterations == 0 and r.location == 7.0
    r = robust.algorithm_s([1.0, 1.0, 1.0], 1)                   # nothing is limited: w* = 1,097 after the first step
    assert r.scale == pytest.approx(1.097) and r.iterations == 2
    for method in ("mean", "median", "algorithm_a", "q_hampel"):
        assert assigned_value.consensus([2.0, 2.0, 2.0], method).degenerate
    assert not assigned_value.consensus([1.0, 2.0, 3.0], "mean").degenerate
    with pytest.raises(ValueError):
        homogeneity.homogeneity([[1.0, 1.1]], sigma_pt=0.1)      # one item
    with pytest.raises(ValueError):
        homogeneity.homogeneity([[1.0], [1.1], [1.2]], sigma_pt=0.1)   # one replicate
    assert homogeneity.homogeneity([[1.0, 1.1], [1.2, 1.1]], sigma_pt=0.1).s_w > 0


def test_more_values_from_tables_and_by_hand():
    # Cochran's critical values at 1 % and 5 %, as tabulated in ISO 5725-2
    assert outliers.cochran_critical(10, 2, 0.01) == pytest.approx(0.718, abs=6e-4)
    assert outliers.cochran_critical(10, 2, 0.05) == pytest.approx(0.602, abs=6e-4)
    assert outliers.cochran_critical(5, 3, 0.01) == pytest.approx(0.788, abs=6e-4)
    # Formulae (24), (25) at a point inside the region: a quarter of chi is used by the mean
    chi = -2.0 * math.log(0.01)
    x, lo, hi = graphics.repeatability_region(10.0, 2.0, m=4, points=5)
    e = math.sqrt(0.75 * chi / (2 * 3))
    assert x[1] == pytest.approx(10.0 - 0.5 * 2.0 * math.sqrt(chi / 4))
    assert lo[1] == pytest.approx(2.0 * math.exp(-e)) and hi[1] == pytest.approx(2.0 * math.exp(e))
    # Qn with exactly twelve results uses b_12 of Table C.2
    x = [float(v * v) for v in range(1, 13)]
    d = sorted(b - a for i, a in enumerate(x) for b in x[i + 1:])
    assert robust.qn(x) == pytest.approx(2.2191 * d[7 * 6 // 2 - 1] * 0.7574, rel=1e-12)
    # regression on three previous rounds; the mean of two results; a round of one result
    fit = sigma_pt.fit_previous_rounds([1.0, 2.0, 3.0], [0.1, 0.2, 0.3])
    assert fit.slope == pytest.approx(0.1) and fit.intercept == pytest.approx(0.0, abs=1e-12)
    av = assigned_value.consensus([1.0, 3.0], "mean")
    assert av.x_pt == 2.0 and av.u_x_pt == pytest.approx(math.sqrt(2.0) / math.sqrt(2.0))
    rec = record.round_record([3.05], x_pt=0.0, u_x_pt=0.0, sigma_pt=1.0)
    assert rec.participants[0].signal == "action" and rec.action == 3.0 and rec.warning == 2.0
    assert record.round_record([2.95], x_pt=0.0, u_x_pt=0.0, sigma_pt=1.0).participants[0].signal == "warning"
    assert sigma_pt.from_precision(1.0, 2.0, 1) == pytest.approx(1.0)        # m = 1: sigma_r does not enter
    with pytest.raises(ValueError):
        sigma_pt.from_precision(1.0, 2.0, 2)                                   # 1 - 4 x 0,5 < 0
    assert sigma_pt.from_precision(1.0, math.sqrt(1.5), 2) == pytest.approx(0.5)   # 1 - 1,5 x 0,5 = 0,25
