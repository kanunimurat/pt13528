# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Boundaries, signal limits, branches and result fields (added in 0.1.9).

Mutation testing of 0.1.8 (mutmut 3.8.0), carried out in response to the
reviewers of the article, showed that the tests did not check some branches
(the delta_E criteria, the stability criterion, the 2022 order statistic of
Qn for odd p), the zero limits of the input checks, the results returned for
degenerate data and the exact signal limits of Clause 9. The tests below
cover them. Expected values are written out from the formulae of the standard,
not taken from the library.
"""
import math

import numpy as np
import pytest

from pt13528 import assigned_value as av
from pt13528 import graphics, homogeneity as hm, outliers, record, robust, scores
from pt13528 import sigma_pt as sp


# --- signal limits of 9.3.2, 9.4.2 and 9.7.2 -------------------------------------------

@pytest.mark.parametrize("z, signal", [(0.0, "acceptable"), (2.0, "acceptable"), (-2.0, "acceptable"),
                                       (2.0 + 1e-12, "warning"), (-2.5, "warning"), (3.0 - 1e-12, "warning"),
                                       (3.0, "action"), (-3.0, "action"), (7.1, "action")])
def test_z_signal_limits(z, signal):
    # 9.4.2: |z| <= 2,0 acceptable; 2,0 < |z| < 3,0 warning; |z| >= 3,0 action
    assert scores.classify_z(z) == signal


@pytest.mark.parametrize("z, signal", [(2.0, "acceptable"), (2.0 + 1e-12, "action"), (-2.0 - 1e-12, "action")])
def test_z_two_band_rule(z, signal):
    # 9.4.2 NOTE 1: a single limit at 2,0
    assert scores.classify_z(z, action=2.0, warning=None) == signal


@pytest.mark.parametrize("en, signal", [(0.0, "acceptable"), (1.0 - 1e-12, "acceptable"), (-1.0 + 1e-12, "acceptable"),
                                        (1.0, "action"), (-1.0, "action"), (1.0 + 1e-12, "action")])
def test_en_signal_limits(en, signal):
    # 9.7.2: |En| >= 1,0 is a signal
    assert scores.classify_en(en) == signal


@pytest.mark.parametrize("d, signal", [(0.4999, "acceptable"), (0.5, "action"), (-0.5, "action")])
def test_d_signal_limits(d, signal):
    # 9.3.2: acceptable when -delta_E < D < delta_E
    assert scores.classify_d(d, 0.5) == signal


def test_scores_near_limits_round_trip():
    # a result exactly 2 sigma_pt and 3 sigma_pt from x_pt (binary-exact values)
    assert scores.classify_z(scores.z_score(12.0, 10.0, 1.0)) == "acceptable"
    assert scores.classify_z(scores.z_score(13.0, 10.0, 1.0)) == "action"
    assert scores.classify_en(scores.en_score(11.0, 10.0, 0.6, 0.8)) == "action"      # hypot = 1,0 exactly
    assert scores.classify_en(scores.en_score(10.5, 10.0, 0.3, 0.4)) == "action"      # En = 1,0 exactly
    assert scores.classify_en(scores.en_score(10.25, 10.0, 0.3, 0.4)) == "acceptable"  # En = 0,5


# --- zero limits of the input checks of the scores ---------------------------------------

def test_score_zero_limits():
    with pytest.raises(ValueError):
        scores.z_score(1.0, 0.0, 0.0)
    assert scores.z_prime_score(1.0, 0.0, 0.0, 0.5) == 2.0          # sigma_pt = 0 with u(x_pt) > 0 is accepted
    assert scores.z_prime_score(1.0, 0.0, 0.5, 0.0) == 2.0
    with pytest.raises(ValueError):
        scores.z_prime_score(1.0, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError):
        scores.z_prime_score(1.0, 0.0, -0.5, 0.5)
    with pytest.raises(ValueError):
        scores.z_prime_score(1.0, 0.0, 0.5, -0.5)
    assert scores.zeta_score(1.0, 0.0, 0.5, 0.0) == 2.0
    assert scores.zeta_score(1.0, 0.0, 0.0, 0.5) == 2.0
    for args in ((0.0, 0.0), (-0.5, 0.5), (0.5, -0.5)):
        with pytest.raises(ValueError):
            scores.zeta_score(1.0, 0.0, *args)
    assert scores.en_score(1.0, 0.0, 0.5, 0.0) == 2.0
    assert scores.en_score(1.0, 0.0, 0.0, 0.5) == 2.0
    for args in ((0.0, 0.0), (-0.5, 0.5), (0.5, -0.5)):
        with pytest.raises(ValueError):
            scores.en_score(1.0, 0.0, *args)
    with pytest.raises(ValueError):
        scores.percent_allowed(1.0, 0.0, 0.0)
    with pytest.raises(ZeroDivisionError):
        scores.percent_difference(1.0, 0.0)
    assert scores.percent_difference(2.0, 1.0) == 100.0


def test_uncertainty_negligible_both_branches():
    # Formula (10): u(x_pt) < 0,3 sigma_pt, or u(x_pt) < 0,1 delta_E
    assert scores.uncertainty_negligible(0.29, sigma_pt=1.0)
    assert not scores.uncertainty_negligible(0.3, sigma_pt=1.0)
    assert scores.uncertainty_negligible(0.74, delta_e=7.5)
    assert not scores.uncertainty_negligible(0.75, delta_e=7.5)
    assert not scores.uncertainty_negligible(0.76, delta_e=7.5)


# --- homogeneity and stability, Annex B ------------------------------------------------

def test_stability_criteria():
    st = hm.stability([1.0, 1.0], [1.75, 1.75], sigma_pt=2.5)
    assert st.criterion == 0.75 and st.difference == 0.75 and st.stable          # B.17, equality is stable
    st = hm.stability([1.0], [1.75], delta_e=7.5)
    assert st.criterion == 0.75 and st.stable                                    # 0,1 delta_E
    st = hm.stability([1.0], [2.0], sigma_pt=2.5, u_y1=0.3, u_y2=0.4)
    assert st.expanded_criterion == pytest.approx(0.75 + 2 * 0.5) and st.stable_expanded   # B.18
    st = hm.stability([1.0], [2.0], sigma_pt=2.5, u_y1=0.3)                      # one uncertainty only
    assert st.expanded_criterion is None and st.stable_expanded is None
    st = hm.stability([1.0], [2.0], sigma_pt=2.5, u_y1=0.0, u_y2=0.0)            # zero uncertainties allowed
    assert st.expanded_criterion == 0.75
    with pytest.raises(ValueError):
        hm.stability([1.0], [2.0], sigma_pt=0.0)


def test_homogeneity_checks_and_fields():
    data = [[1.0, 1.1], [1.2, 1.1], [0.9, 1.0], [1.05, 1.0]]
    for kw in ({"alpha": 0.0}, {"alpha": 1.0}, {"sigma_pt": 0.0}, {"sigma_pt": -1.0}, {"delta_e": 0.0}):
        with pytest.raises(ValueError):
            hm.homogeneity(data, **kw)
    h = hm.homogeneity(data, delta_e=2.0)
    assert h.criterion == pytest.approx(0.2)                                       # B.2: 0,1 delta_E
    same = hm.homogeneity([[1.0, 1.0], [2.0, 2.0], [1.5, 1.5]])                  # no within-item variation
    assert same.s_w == 0.0 and same.f_statistic is None and same.f_significant is None


def test_homogeneity_single_fields():
    h = hm.homogeneity_single([1.0, 2.0, 3.0], delta_e=10.0)
    assert (h.g, h.m, h.mean, h.s_x, h.s_w, h.s_s) == (3, 1, 2.0, 1.0, None, 1.0)
    assert h.criterion == 1.0 and h.sufficient is True                           # s = criterion: sufficient
    h = hm.homogeneity_single([1.0, 2.0, 3.0])
    assert h.criterion is None and h.sufficient is None


# --- robust estimators, Annex C --------------------------------------------------------

def _qn_by_hand(x, h, factor, bp):
    d = sorted(abs(a - b) for i, a in enumerate(x) for b in x[i + 1:])
    k = h * (h - 1) // 2
    return factor * d[k - 1] * bp


def test_qn_2022_order_statistic_odd_and_even():
    # 2022 text: h = p/2 (p even) or (p - 1)/2 (p odd), factor 2,221 9; b_p from Table C.2.
    # For odd p, floor(p/2) equals (p - 1)/2, so the two cases coincide in integer arithmetic.
    x7 = [0.0, 1.0, 3.0, 7.0, 15.0, 31.0, 63.0]           # all pairwise differences distinct
    x8 = x7 + [127.0]
    assert robust.qn(x7, h_rule="iso-literal") == pytest.approx(_qn_by_hand(x7, 3, 2.2219, 0.8588), rel=1e-12)
    assert robust.qn(x8, h_rule="iso-literal") == pytest.approx(_qn_by_hand(x8, 4, 2.2219, 0.6699), rel=1e-12)
    assert robust.qn(x7) == pytest.approx(_qn_by_hand(x7, 4, 2.2191, 0.8588), rel=1e-12)


def test_degenerate_results_are_complete():
    r = robust.algorithm_a([5.0] * 5)
    assert (r.location, r.scale, r.iterations, r.converged, r.degenerate) == (5.0, 0.0, 0, True, True)
    for tol in (robust.DEFAULT_TOL if hasattr(robust, "DEFAULT_TOL") else 1e-10, "iso2022"):
        r = robust.algorithm_a([10.0] * 8 + [11.0, 12.0], tol=tol)
        assert r.location == 10.0 and r.scale == 0.0 and r.converged and r.degenerate and r.iterations > 0
    r = robust.algorithm_s([0.0, 0.0, 0.0], nu=2)
    assert (r.location, r.scale, r.iterations, r.converged, r.degenerate) == (0.0, 0.0, 0, True, True)
    r = robust.algorithm_a([9.0, 10.0, 11.0, 10.5, 9.5])
    assert r.degenerate is False and r.converged is True
    c = av.consensus([5.0] * 4, "median")
    assert (c.x_pt, c.u_x_pt, c.method, c.scale, c.p, c.degenerate) == (5.0, 0.0, "median", 0.0, 4, True)
    for m in ("algorithm_a", "median", "q_hampel"):
        c = av.consensus([0.10, 0.12, 0.11, 0.13, 0.09, 0.115], m)           # scale well below 1
        assert c.method == m and c.p == 6 and c.degenerate is False and 0 < c.scale < 1
    c = av.consensus([1.0, 2.0, 3.0], "mean")
    assert (c.method, c.scale, c.p) == ("mean", 1.0, 3)


def test_q_hampel_result_fields():
    r = robust.q_hampel([10.1, 10.4, 9.8, 10.0, 11.2, 9.9, 10.3])
    assert r.iterations == 0 and r.converged is True and r.degenerate is False
    assert r.location == robust.hampel([10.1, 10.4, 9.8, 10.0, 11.2, 9.9, 10.3], r.scale, "finite")


def test_hampel_iterative_within_its_stopping_limit():
    # C.5.3.2 stops when the change is below 0,01 s*/sqrt(p); the finite-step result is the exact root
    x = [10.1, 10.4, 9.8, 10.0, 11.2, 9.9, 10.3, 12.5, 10.2]
    s = robust.q_method(x)
    assert abs(robust.hampel(x, s, "iterative") - robust.hampel(x, s, "finite")) < 0.01 * s / math.sqrt(len(x))


# --- assigned value, sigma_pt, outliers, graphics ---------------------------------------

def test_assigned_value_edges():
    c = av.compare_with_reference(10.0, 0.0, 9.0, 0.0)
    assert c.ratio == math.inf and c.investigate
    c = av.compare_with_reference(10.0, 0.0, 10.0, 0.0)
    assert c.ratio == math.inf
    assert av.u_robust(2.0, 1) == 2.5                                              # Formula (6) with p = 1
    r = av.from_crm_comparison(20.0, 0.3, [1.0, 2.0, 3.0])
    assert r.p == 3 and r.method == "crm-comparison"
    for kw in ({"u_hom": -0.1}, {"u_trans": -0.1}, {"u_stab": -0.1}):
        with pytest.raises(ValueError):
            av.combine_uncertainty(0.1, **kw)
    with pytest.raises(ValueError):
        av.kernel_mode([1.0, 2.0], 0.0)
    assert av.kernel_mode([10.0], 2.0, grid=4097) == pytest.approx(10.0)


def test_sigma_pt_edges():
    assert sp.horwitz(0.0) == 0.0
    assert sp.from_precision(0.0, 0.0, 2) == 0.0
    with pytest.raises(ValueError):
        sp.fit_previous_rounds([1.0, 2.0, 3.0, 4.0], [0.1, 0.2, 0.3])
    assert sp.limit_sigma(1.0, lower=2.0, upper=2.0) == 2.0


def test_outlier_tests_edges():
    gh, gl, crit = outliers.grubbs([1.0, 2.0, 4.0], alpha=0.05)
    m, s = 7.0 / 3.0, float(np.std([1.0, 2.0, 4.0], ddof=1))
    assert gh == pytest.approx((4.0 - m) / s) and gl == pytest.approx((m - 1.0) / s)
    assert crit == outliers.grubbs_critical(3, 0.05)
    for bad in ([1.0, 2.0], [3.0, 3.0, 3.0]):
        with pytest.raises(ValueError):
            outliers.grubbs(bad)
    c, crit, i = outliers.cochran([0.0, 0.5, 1.5], 2, alpha=0.05)
    assert c == 0.75 and i == 2 and crit == outliers.cochran_critical(3, 2, 0.05)
    for bad in ([0.0, 0.0], [-0.1, 0.5], [float("nan"), 0.5]):
        with pytest.raises(ValueError):
            outliers.cochran(bad, 2)
    for a in (0.0, 1.0):
        with pytest.raises(ValueError):
            outliers.grubbs_critical(5, a)
        with pytest.raises(ValueError):
            outliers.cochran_critical(3, 2, a)


def test_graphics_edges():
    assert graphics.bandwidth(10, robust_sd=1.0) == pytest.approx(0.9 / 10 ** 0.2)
    assert graphics.bandwidth(10, robust_sd=1.0, sigma_pt=0.0) == pytest.approx(0.9 / 10 ** 0.2)
    with pytest.raises(ValueError):
        graphics.bandwidth(10, robust_sd=0.0)
    g, d = graphics.kernel_density([1.0, 2.0, 4.0], 0.5, grid=2001, cut=3.0)
    assert g[0] == pytest.approx(1.0 - 1.5) and g[-1] == pytest.approx(4.0 + 1.5) and g.size == 2001
    assert np.trapezoid(d, g) == pytest.approx(1.0, abs=2e-3)                    # unit area (10.3.1)
    assert graphics.repeatability_statistic(10.0, 1.0, 10.0, 1.0, 4) == 0.0
    assert graphics.repeatability_statistic(11.0, 1.0, 10.0, 1.0, 4) == 4.0
    for sd_i, w in ((0.0, 1.0), (1.0, 0.0)):
        with pytest.raises(ValueError):
            graphics.repeatability_statistic(10.0, sd_i, 10.0, w, 4)
    assert graphics.ordinal_summary({1: 2, 2: 2})["median"] == 1                   # cumulative share reaches 1/2
    assert graphics.ordinal_summary({1: 1, 2: 2, 3: 1})["median"] == 2
    with pytest.raises(ValueError):
        graphics.ordinal_summary({1: 1, 2: 1}, order=[1, 1, 2])


# --- the round record --------------------------------------------------------------------

def test_round_record_limits_and_clauses():
    x = [10.0, 10.2, 9.9, 10.1, 9.8, 10.05, 13.0, 10.15, 9.95, 10.1]
    two = record.round_record(x, sigma_pt=1.0, warning=None, action=2.0, u_x=[0.1] * 10)
    assert "warning" not in two.counts and all(r.signal in ("acceptable", "action") for r in two.participants)
    assert all(r.zeta_signal in ("acceptable", "action") for r in two.participants)
    assert two.clauses["sigma_pt"] == "8.2 to 8.5" and two.clauses["x_pt"] == "7.7, C.3.1"
    med = record.round_record(x, method="median", sigma_pt=1.0)
    assert med.method == "median" and med.clauses["x_pt"] == "7.7, C.2" and med.clauses["u_x_pt"] == "7.7.7, Formula (6)"
    assert med.x_pt == av.consensus(x, "median").x_pt
    mean = record.round_record(x, method="mean", sigma_pt=1.0)
    assert mean.clauses["x_pt"] == "7.7" and mean.clauses["u_x_pt"] == "7.2"
    own = record.round_record(x, sigma_pt=None)
    assert own.clauses["sigma_pt"] == "8.6"
    given = record.round_record(x, x_pt=10.0, u_x_pt=0.5, sigma_pt=1.0, statistic="z")
    assert given.clauses["x_pt"] == "7.3 to 7.6" and given.clauses["statistic"] == "9.4.1, Formula (14)"
    zp = record.round_record(x, x_pt=10.0, u_x_pt=0.5, sigma_pt=1.0, statistic="z_prime")
    assert zp.clauses["statistic"] == "9.5.1, Formula (15)"
    for bad in ([], [1.0, float("nan")]):
        with pytest.raises(ValueError):
            record.round_record(bad, sigma_pt=1.0)
