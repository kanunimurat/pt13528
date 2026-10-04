# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Golden-master tests: the worked examples of ISO 13528:2022 Annex E (E.14 is not covered).

Tolerance is half a unit of the last printed digit unless a comment says otherwise.
"""
import math

import numpy as np
import pytest

from pt13528 import assigned_value as av
from pt13528 import graphics, homogeneity as hom, robust, scores, sigma_pt

import annex_e_data as E


def half_unit(printed_decimals):
    return 0.5 * 10 ** (-printed_decimals) + 1e-12


# ---------------------------------------------------------------- E.1
@pytest.mark.parametrize("case", ["ignored", "deleted"])
def test_e1_algorithm_a(case):
    data, x_star, s_star = E.E1[case]
    r = robust.algorithm_a(data)
    assert r.location == pytest.approx(x_star, abs=half_unit(2))
    assert r.scale == pytest.approx(s_star, abs=half_unit(2))


def test_e1_half_value_depends_on_stopping_rule():
    """Table E.1 prints 23,95 / 8,60. Full convergence gives 23,9585 / 8,5960: the printed s* is
    the converged value and the printed x* is the converged value truncated, not rounded. The
    third-significant-figure rule of C.3.1 stops earlier, at 23,96 / 8,59."""
    data, x_star, s_star = E.E1["half"]
    for tol in ("sig3", 1e-12):
        r = robust.algorithm_a(data, tol=tol)
        assert r.location == pytest.approx(x_star, abs=0.011)
        assert r.scale == pytest.approx(s_star, abs=0.011)
    full = robust.algorithm_a(data, tol=1e-12)
    assert full.location == pytest.approx(23.9585, abs=1e-4)
    assert full.scale == pytest.approx(8.5960, abs=1e-4)


# ---------------------------------------------------------------- E.2
def test_e2_homogeneity_and_stability():
    h = hom.homogeneity(E.E2_HOMOGENEITY)
    assert h.mean == pytest.approx(0.18715, abs=half_unit(5))
    assert h.s_x == pytest.approx(0.00398, abs=half_unit(5))
    assert h.s_w == pytest.approx(0.00556, abs=half_unit(5))
    assert h.s_s == pytest.approx(0.00060, abs=half_unit(5))
    sigma = 0.15 * h.mean
    assert sigma == pytest.approx(0.02807, abs=half_unit(5))
    h = hom.homogeneity(E.E2_HOMOGENEITY, sigma_pt=sigma)
    assert h.criterion == pytest.approx(0.00842, abs=half_unit(5))
    assert h.sufficient is True
    flat = [v for pair in E.E2_HOMOGENEITY for v in pair]
    s = hom.stability(flat, [v for pair in E.E2_STABILITY for v in pair], sigma_pt=sigma)
    assert s.mean_2 == pytest.approx(0.19375, abs=half_unit(5))
    assert s.difference == pytest.approx(0.00660, abs=half_unit(5))
    assert s.stable is True


@pytest.mark.parametrize("g", sorted(E.TABLE_B1))
def test_table_b1_factors(g):
    f1, f2 = hom.expanded_criterion_factors(g)
    assert f1 == pytest.approx(E.TABLE_B1[g][0], abs=half_unit(2))
    assert f2 == pytest.approx(E.TABLE_B1[g][1], abs=half_unit(2))


# ---------------------------------------------------------------- E.3
def test_e3_table_e4_iterations():
    r = robust.algorithm_a(E.E3)
    assert r.iterations == 6 and r.converged


def test_e3_table_e5():
    p = len(E.E3)
    med = av.consensus(E.E3, "median")
    assert med.x_pt == pytest.approx(0.2620, abs=half_unit(4))
    assert robust.niqr(E.E3) == pytest.approx(0.0402, abs=half_unit(4))
    assert robust.made(E.E3) == pytest.approx(0.0386, abs=half_unit(4))
    assert med.u_x_pt == pytest.approx(0.0086, abs=half_unit(4))          # from nIQR
    a = av.consensus(E.E3, "algorithm_a")
    assert (a.x_pt, a.scale, a.u_x_pt) == pytest.approx((0.2570, 0.0395, 0.0085), abs=half_unit(4))
    qh = av.consensus(E.E3, "q_hampel")
    assert (qh.x_pt, qh.scale, qh.u_x_pt) == pytest.approx((0.2600, 0.0426, 0.0091), abs=half_unit(4))
    m = av.consensus(E.E3, "mean")
    assert (m.x_pt, m.scale, m.u_x_pt) == pytest.approx((0.2512, 0.0672, 0.0115), abs=half_unit(4))
    trimmed = [v for v in E.E3 if 0.06 < v < 0.42]                        # three outliers removed
    t = av.consensus(trimmed, "mean")
    assert len(trimmed) == p - 3
    assert (t.x_pt, t.scale, t.u_x_pt) == pytest.approx((0.2588, 0.0337, 0.0061), abs=half_unit(4))


def test_e3_bootstrap_for_mean_within_monte_carlo_error():
    """Table E.5: 0,2503 / 0,0667 / 0,0113 from R; a different generator agrees only statistically."""
    b = av.bootstrap(E.E3, np.mean, replicates=4000, seed=1)
    assert b.scale == pytest.approx(0.2503, abs=0.002)        # mean of the bootstrap replicates
    assert b.u_x_pt == pytest.approx(0.0113, abs=0.001)


def test_hampel_iterative_agrees_with_finite_step():
    s = robust.q_method(E.E3)
    assert robust.hampel(E.E3, s, "iterative") == pytest.approx(robust.hampel(E.E3, s, "finite"), abs=1e-4)


# ---------------------------------------------------------------- E.4
def test_e4_table_e7_scores():
    u_pt = E.E4_BIG_U / 2
    delta_e = 3 * E.E4_SIGMA                      # PA column corresponds to delta_E = 3 sigma_pt
    for code, x, big_u, k, _flag, d_pct, pa, z, zp, zeta, en in E.E4:
        assert scores.percent_difference(x, E.E4_XPT) == pytest.approx(d_pct, abs=half_unit(1)), code
        # PA is printed from D% rounded to one decimal; allow that rounding to propagate
        assert scores.percent_allowed(x, E.E4_XPT, delta_e) == pytest.approx(pa, abs=0.2), code
        assert scores.z_score(x, E.E4_XPT, E.E4_SIGMA) == pytest.approx(z, abs=half_unit(2)), code
        assert scores.z_prime_score(x, E.E4_XPT, E.E4_SIGMA, u_pt) == pytest.approx(zp, abs=half_unit(2)), code
        assert scores.zeta_score(x, E.E4_XPT, big_u / k, u_pt) == pytest.approx(zeta, abs=half_unit(2)), code
        assert scores.en_score(x, E.E4_XPT, big_u, E.E4_BIG_U) == pytest.approx(en, abs=half_unit(2)), code


def test_e4_uncertainty_flags_are_not_derivable_from_the_printed_data():
    """Table E.6 flags reported uncertainties a/b/c "following criteria discussed in 9.8", but the
    limits of 9.8.3 and 9.8.4 (u_min = u(x_pt) = 0,0041 and u_max = 1,5 s* = 0,0247) do not
    reproduce the printed flags. They are reproduced with u_max = sigma_pt and any u_min in
    (0,002; 0,0025], i.e. a characterisation uncertainty that the example does not state."""
    s_star = robust.algorithm_a([r[1] for r in E.E4]).scale
    by_9_8 = [scores.uncertainty_flag(r[2] / r[3], E.E4_BIG_U / 2, 1.5 * s_star) for r in E.E4]
    printed = [r[4] for r in E.E4]
    assert by_9_8 != printed
    for u_min in (0.0021, 0.0023, 0.0025):
        assert [scores.uncertainty_flag(r[2] / r[3], u_min, E.E4_SIGMA) for r in E.E4] == printed


# ---------------------------------------------------------------- E.5
def test_e5_single_laboratory_against_crm():
    d = np.array(E.E5_D)
    assert d.mean() == pytest.approx(1.73, abs=half_unit(2))
    assert d.std(ddof=1) == pytest.approx(1.07, abs=half_unit(2))
    a = av.from_crm_comparison(E.E5_XCRM, E.E5_UCRM, E.E5_D)
    assert a.scale == pytest.approx(0.24, abs=half_unit(2))
    assert a.x_pt == pytest.approx(23.35, abs=half_unit(2))
    assert a.u_x_pt == pytest.approx(0.35, abs=half_unit(2))


# ---------------------------------------------------------------- E.6
def test_e6_kernel_mode_and_bootstrap():
    bw = 0.75 * 0.25
    assert av.kernel_mode(E.E6, bw) == pytest.approx(3.79, abs=half_unit(2))
    b = av.bootstrap(E.E6, lambda s: av.kernel_mode(s, bw, grid=512), replicates=1000, seed=220)
    assert b.u_x_pt == pytest.approx(0.0922, abs=0.02)        # Monte Carlo; R used another generator
    assert not scores.uncertainty_negligible(0.0922, sigma_pt=0.25)


# ---------------------------------------------------------------- E.7
def test_e7_comparison_with_reference():
    values = [r[1] for r in E.E4]
    r = robust.algorithm_a(values)
    assert r.location == pytest.approx(0.03161, abs=half_unit(5))
    assert r.scale == pytest.approx(0.0164, abs=half_unit(4))
    u = av.u_robust(r.scale, len(values))
    assert u == pytest.approx(0.0045, abs=half_unit(4))
    c = av.compare_with_reference(E.E4_XPT, E.E4_BIG_U / 2, r.location, u)
    assert c.u_diff == pytest.approx(0.0061, abs=half_unit(4))
    assert c.x_diff == pytest.approx(0.012, abs=half_unit(3))
    assert c.ratio == pytest.approx(2.0, abs=0.05)


# ---------------------------------------------------------------- E.8 to E.10
def test_e8_regression_on_previous_rounds():
    fit = sigma_pt.fit_previous_rounds(E.E8_AV, E.E8_SD)
    # The standard prints 0,82. The data of Table E.9 give 0,8264, which rounds to 0,83: the printed
    # value is the truncated one (docs/coverage.md, case 2).
    assert fit.r_squared == pytest.approx(0.8264, abs=5e-5)


def test_e9_horwitz():
    assert sigma_pt.horwitz(1.195e-6) * 1e6 == pytest.approx(0.186, abs=half_unit(3))
    assert sigma_pt.horwitz(2.565e-6) * 1e6 == pytest.approx(0.356, abs=half_unit(3))
    assert sigma_pt.horwitz(1.195e-6) / 1.195e-6 * 100 == pytest.approx(15.6, abs=half_unit(1))
    assert sigma_pt.horwitz(2.565e-6) / 2.565e-6 * 100 == pytest.approx(13.9, abs=half_unit(1))


def test_e10_precision_experiment():
    assert sigma_pt.from_precision(23.2, 14.3, 2) == pytest.approx(20.9, abs=half_unit(1))
    assert math.sqrt(23.2 ** 2 - 14.3 ** 2) == pytest.approx(18.3, abs=half_unit(1))


# ---------------------------------------------------------------- E.12
def test_e12_table_e10_uses_arithmetic_statistics():
    """The text of E.12 says the z scores use Algorithm A, but Table E.10 is reproduced only by
    the arithmetic mean and standard deviation printed at its foot (11,54 / 3,29 and 7,66 / 2,90)."""
    for data, z_printed, mean, sd in ((E.E12_A, E.E12_ZA, 11.54, 3.29), (E.E12_B, E.E12_ZB, 7.66, 2.90)):
        a = np.array(data)
        assert a.mean() == pytest.approx(mean, abs=half_unit(2))
        assert a.std(ddof=1) == pytest.approx(sd, abs=half_unit(2))
        z = (a - a.mean()) / a.std(ddof=1)
        assert np.max(np.abs(z - np.array(z_printed))) < 0.0015
        r = robust.algorithm_a(data)
        assert abs(r.location - mean) > 0.3 and abs(r.scale - sd) > 0.5
    assert np.corrcoef(E.E12_A, E.E12_B)[0, 1] == pytest.approx(0.706, abs=half_unit(3))


# ---------------------------------------------------------------- E.13
def test_e13_algorithm_a_and_s():
    assert robust.algorithm_a(E.E13_AVG).location == pytest.approx(1.57, abs=half_unit(2))
    w = robust.algorithm_s(E.E13_SD, nu=3)
    assert w.location == pytest.approx(0.34, abs=half_unit(2))
    x, lo, hi = graphics.repeatability_region(1.57, 0.34, m=4)
    assert np.all(lo > 0) and np.all(hi >= lo)
    stat = graphics.repeatability_statistic(1.13, 0.72, 1.57, 0.34, 4)
    assert stat > 9.21                              # laboratory 13 lies outside the 1 % region


# ---------------------------------------------------------------- E.15
def test_e15_ordinal():
    assert graphics.ordinal_summary({1: 20, 2: 18, 3: 10, 4: 2}) == {"mode": 1, "median": 2, "n": 50}
    assert graphics.ordinal_summary({1: 8, 2: 12, 3: 20, 4: 10}) == {"mode": 3, "median": 3, "n": 50}
