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
