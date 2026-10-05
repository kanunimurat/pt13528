# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Degenerate and invalid input, and independence of the unit of the data."""
import math

import numpy as np
import pytest

from pt13528 import assigned_value, homogeneity, outliers, record, robust, scores

NAN = float("nan")
DEFAULT = robust.DEFAULT_TOL


def test_convergence_does_not_depend_on_the_unit():
    rng = np.random.default_rng(5)
    x = rng.normal(10, 1, 20)
    ref = robust.algorithm_a(x, tol=1e-10)
    for unit in (1e-9, 1e-6, 1e3, 1e9):
        r = robust.algorithm_a(x * unit, tol=1e-10)
        assert r.converged and r.iterations == ref.iterations
        assert r.scale / unit == pytest.approx(ref.scale, rel=1e-12)
        assert r.location / unit == pytest.approx(ref.location, rel=1e-12)
    w = np.abs(rng.normal(0, 1, 15)) + 0.1
    assert robust.algorithm_s(w * 1e-9, 1, tol=1e-10).location / 1e-9 == pytest.approx(
        robust.algorithm_s(w, 1, tol=1e-10).location, rel=1e-12)


def test_default_depends_neither_on_the_unit_nor_on_the_origin():
    rng = np.random.default_rng(6)
    for _ in range(200):
        p = int(rng.integers(6, 41))
        x = np.round(rng.normal(rng.uniform(1, 100), rng.uniform(0.1, 5), p), 1)
        a = robust.algorithm_a(x)
        if a.degenerate:
            continue
        for unit in (25.4, 1e-6, 3.7):
            b = robust.algorithm_a(x * unit)
            assert b.scale / unit == pytest.approx(a.scale, rel=1e-8)
            assert b.location / unit == pytest.approx(a.location, abs=1e-8 * a.scale)
        c = robust.algorithm_a(x + 273.15)
        assert c.scale == pytest.approx(a.scale, rel=1e-8)
        assert c.location - 273.15 == pytest.approx(a.location, abs=1e-8 * a.scale)
        r1, r2 = record.round_record(list(x)), record.round_record(list(x + 273.15))
        assert [q.signal for q in r1.participants] == [q.signal for q in r2.participants]


X11 = [18.2, 18.2, 18.4, 18.4, 18.4, 18.4, 18.6, 19.8, 20.5, 20.9, 22.3]


def test_stopping_criterion_of_the_2022_edition_and_its_variants():
    """ISO 13528:2022, C.3.1: no change "from one iteration to the next" in the third significant
    figures of x* and s* ("iso2022"). The starting values are not an iteration, so the first update is
    not compared with them. An implementation that does compare them ("iso2022-from-start", the
    behaviour of this library up to 0.1.7 under other names) stops after one update for the eleven
    results in kelvin, constructed for this test: the start (291,55 and 0,2966) and the first update
    (291,69 and 0,2968) agree to three figures, s* is 78 % too small and four results get an action
    signal. "equivalent-figure" tests the same decimal place in x* as in s*."""
    k = [v + 273.15 for v in X11]
    full = robust.algorithm_a(X11)
    assert full.scale == pytest.approx(1.3299, abs=5e-5)
    assert robust.algorithm_a(k).scale == pytest.approx(full.scale, rel=1e-9)
    for tol in ("iso2022", "equivalent-figure"):
        celsius, kelvin = robust.algorithm_a(X11, tol=tol), robust.algorithm_a(k, tol=tol)
        assert celsius.scale == pytest.approx(1.328, abs=5e-4) and celsius.iterations == 13
        assert kelvin.scale == pytest.approx(celsius.scale, rel=1e-9) and kelvin.iterations == 13
        assert record.round_record(k, tol=tol).counts["action"] == 0
    old = robust.algorithm_a(k, tol="iso2022-from-start")
    assert old.iterations == 1 and old.scale == pytest.approx(0.297, abs=5e-4)
    assert record.round_record(k, tol="iso2022-from-start").counts["action"] == 4
    assert robust.algorithm_a(X11, tol="iso2022-from-start").scale == pytest.approx(1.328, abs=5e-4)
    # the names of version 0.1.6 keep the behaviour they had there
    assert robust.algorithm_a(k, tol="sig3-of-x") == old
    assert robust.algorithm_a(k, tol="sig3") == robust.algorithm_a(k, tol="equivalent-figure")
    # Algorithm S (C.4) words its criterion in the same way
    assert robust.algorithm_s([0.5, 0.5, 0.5, 0.6, 0.7], 1, tol="iso2022").iterations >= 2


def test_three_figure_rule_depends_on_the_unit():
    """Significant figures depend on the unit, so the rule of C.3.1 stops at a different iterate
    after a change of unit: results in inches and the same results in millimetres."""
    x = [0.52, 0.55, 0.61, 0.48, 0.50, 0.57, 0.93, 0.49, 0.53, 0.60]
    inch, mm = robust.algorithm_a(x, tol="equivalent-figure"), robust.algorithm_a([25.4 * v for v in x], tol="equivalent-figure")
    full = robust.algorithm_a(x)
    assert robust.algorithm_a([25.4 * v for v in x]).scale / 25.4 == pytest.approx(full.scale, rel=1e-9)
    assert inch.iterations != mm.iterations
    assert abs(mm.scale / 25.4 - inch.scale) > 1e-4 * full.scale


@pytest.mark.parametrize("tol", [0, -1.0, NAN, math.inf, "three", True, None])
def test_invalid_stopping_criterion(tol):
    with pytest.raises(ValueError):
        robust.algorithm_a([1, 2, 3, 4, 9], tol=tol)
    with pytest.raises(ValueError):
        robust.algorithm_s([0.1, 0.2, 0.3], 1, tol=tol)


@pytest.mark.parametrize("tol", ["iso2022", "equivalent-figure", DEFAULT])
def test_slow_collapse_is_detected(tol):
    """Five of seven results identical and two symmetric ones: s* shrinks by 1,8 % per iteration, which
    took more than 1000 iterations to reach the collapse threshold in 0.1.5."""
    r = robust.algorithm_a([10, 10, 10, 10, 10, 9, 11], tol=tol)
    assert r.degenerate and r.scale == 0.0 and r.location == pytest.approx(10.0) and r.iterations < 50
    assert assigned_value.consensus([10, 10, 10, 10, 10, 9, 11]).degenerate
    with pytest.raises(ValueError, match="identical"):
        record.round_record([10, 10, 10, 10, 10, 9, 11])
    r = robust.algorithm_a([10, 10, 10, 10, 10, 10, 9.5, 12], tol=tol)          # asymmetric
    assert r.degenerate and r.location == pytest.approx(10.0)


def test_identical_majorities_never_run_into_the_iteration_limit():
    rng = np.random.default_rng(5)
    for _ in range(3000):
        p = int(rng.integers(5, 21))
        k = int(rng.integers(p // 2 + 1, p))
        x = np.concatenate([np.full(k, 10.0), np.round(rng.normal(10, 1, p - k), 1)])
        r = robust.algorithm_a(x)
        assert r.converged
        if not r.degenerate:
            assert r.scale > 0


@pytest.mark.parametrize("unit", [1e-200, 1e-30, 1e30, 1e160])
def test_extreme_units(unit):
    a = robust.algorithm_a(X11)
    b = robust.algorithm_a([unit * v for v in X11])
    assert not b.degenerate and b.scale / unit == pytest.approx(a.scale, rel=1e-9)
    assert b.location / unit == pytest.approx(a.location, rel=1e-9)
    w = [0.2, 0.5, 0.1, 0.4, 0.3, 0.6, 2.0]
    assert robust.algorithm_s([unit * v for v in w], 3).scale / unit == pytest.approx(robust.algorithm_s(w, 3).scale, rel=1e-9)


def test_strings_and_mappings_are_not_data():
    for f in (robust.algorithm_a, robust.q_method, robust.q_hampel, robust.qn, record.round_record,
              outliers.grubbs, robust.median):
        with pytest.raises(TypeError):
            f("12345")
        with pytest.raises(TypeError):
            f({1: 2.0, 2: 3.0})
    with pytest.raises(TypeError):
        robust.q_method([[1.0, 2.0], "34", [5.0]])
    with pytest.raises(TypeError):
        homogeneity.homogeneity("12345", sigma_pt=1.0)


def test_scores_reject_non_finite_values():
    for bad in (NAN, math.inf, -math.inf):
        for f, args in ((scores.z_score, (bad, 1.0, 1.0)), (scores.z_score, (1.0, bad, 1.0)),
                        (scores.z_score, (1.0, 1.0, bad)), (scores.z_prime_score, (1.0, 1.0, 1.0, bad)),
                        (scores.zeta_score, (1.0, 1.0, bad, 0.1)), (scores.en_score, (bad, 1.0, 0.1, 0.1)),
                        (scores.difference, (bad, 1.0)), (scores.percent_difference, (bad, 1.0)),
                        (scores.percent_allowed, (1.0, 1.0, bad)), (scores.delta_e_prime, (bad, 0.1)),
                        (scores.z_reduction_factor, (bad, 0.1)), (scores.uncertainty_flag, (0.1, 0.1, bad))):
            with pytest.raises(ValueError):
                f(*args)
        with pytest.raises(ValueError):
            scores.uncertainty_negligible(0.1, sigma_pt=bad)
        with pytest.raises(ValueError):
            record.round_record([1, 2, 3], x_pt=2.0, u_x_pt=0.1, sigma_pt=bad)
        with pytest.raises(ValueError):
            record.round_record([1, 2, 3], x_pt=2.0, u_x_pt=bad, sigma_pt=1.0)
        with pytest.raises(ValueError):
            robust.hampel([1, 2, 3], bad)
    with pytest.raises(ValueError):
        robust.hampel([1, 2, 3], -1.0)
    assert robust.hampel([1, 2, 4], 0.0) == 2.0                                   # no scale: the median
    with pytest.raises(ValueError):
        homogeneity.stability([1.0, 1.1], [1.0, 1.2], sigma_pt=-1.0)
    with pytest.raises(ValueError):
        homogeneity.stability([1.0, 1.1], [1.0, 1.2], sigma_pt=1.0, u_y1=-0.1, u_y2=0.1)
    with pytest.raises(ValueError):
        scores.uncertainty_negligible(0.1, sigma_pt=0.0)


@pytest.mark.parametrize("tol", ["iso2022", "equivalent-figure", 1e-12])
def test_large_majority_of_identical_results(tol):
    r = robust.algorithm_a([5, 5, 5, 5, 5, 5, 9], tol=tol)
    assert r.scale == 0.0 and r.degenerate and r.location == pytest.approx(5.0)
    assert not robust.algorithm_a([1, 2, 3, 4, 5, 6, 9], tol=tol).degenerate
    assert not robust.algorithm_a([5, 5, 5, 5, 6, 7, 9], tol=tol).degenerate          # 4 of 7 identical: s* stays positive
    with pytest.raises(ValueError, match="identical"):
        record.round_record([5, 5, 5, 5, 5, 5, 9])
    rec = record.round_record([5, 5, 5, 5, 5, 5, 9], sigma_pt=0.5)       # a value from Clause 8 is still usable
    assert rec.counts["action"] == 1


def test_non_finite_input_is_rejected():
    bad = [1.0, 2.0, NAN, 4.0, 5.0]
    for f in (robust.median, robust.made, robust.niqr, robust.algorithm_a, robust.qn, robust.q_method,
              robust.q_hampel, robust.mean_abs_dev_sd, record.round_record):
        with pytest.raises(ValueError):
            f(bad)
    for m in ("algorithm_a", "median", "q_hampel", "mean"):
        with pytest.raises(ValueError):
            assigned_value.consensus(bad, m)
    with pytest.raises(ValueError):
        assigned_value.consensus([], "mean")
    with pytest.raises(ValueError):
        assigned_value.consensus([1.0], "mean")
    with pytest.raises(ValueError):
        assigned_value.consensus([1, 2, 3], "median", median_scale="mad")
    with pytest.raises(ValueError):
        homogeneity.homogeneity([[1, 1.1], [1.2, NAN], [1, 1]], sigma_pt=0.1)
    with pytest.raises(ValueError):
        robust.algorithm_s([0.1, -0.2, 0.3], 1)
    with pytest.raises(ValueError):
        scores.classify_z(NAN)
    with pytest.raises(ValueError):
        scores.classify_en(NAN)
    with pytest.raises(ValueError):
        scores.classify_d(NAN, 1.0)
    with pytest.raises(ValueError):
        scores.uncertainty_flag(NAN, 0.1, 1.0)
    with pytest.raises(ValueError):
        scores.uncertainty_negligible(-0.1, sigma_pt=1.0)
    with pytest.raises(ValueError):
        record.round_record([1, 2, 3], x_pt=2.0, u_x_pt=-0.1, sigma_pt=1.0)


def test_hampel_iterative_with_two_distant_groups():
    x = [0.0] * 5 + [100.0] * 5
    assert math.isfinite(robust.hampel(x, 1.0, "iterative"))


@pytest.mark.parametrize("tol", ["iso2022", 1e-10, 1e-12])
@pytest.mark.parametrize("x", [
    [10.0] * 9 + [10.000001, 9.999998],
    [1000.0] * 9 + [1000.001, 999.998],
    [1000000.0] * 9 + [1000000.1, 999999.8],
])
def test_collapse_is_detected_when_the_spread_is_small_against_the_level(x, tol):
    r = robust.algorithm_a(x, tol=tol)
    assert r.degenerate and r.scale == 0.0
    with pytest.raises(ValueError):
        record.round_record(x)


def test_hampel_and_q_hampel_do_not_depend_on_the_unit():
    rng = np.random.default_rng(7)
    x = rng.normal(10, 1, 20)
    x[3] = 17
    ref = robust.q_hampel(x).location
    for unit in (1e-12, 1e-9, 1e-6, 1e6, 1e12):
        assert robust.q_hampel(x * unit).location / unit == pytest.approx(ref, rel=1e-10)
        assert robust.hampel(x * unit, 1.2 * unit) / unit == pytest.approx(robust.hampel(x, 1.2), rel=1e-10)
    y = np.round(x, 1)                                       # ties
    for unit in (1e-9, 1e-3, 7.0, 1e6):
        assert robust.q_method(y * unit) / unit == pytest.approx(robust.q_method(y), rel=1e-10)


def test_negative_fixed_scale_is_rejected():
    with pytest.raises(ValueError):
        robust.algorithm_a([1, 2, 3, 4, 9], update_scale=False, scale=-1.0)


def test_algorithm_s_with_a_large_majority_of_zeros():
    r = robust.algorithm_s([0.0] * 9 + [1.0], 1)
    assert r.location == 0.0 and r.degenerate
    assert not robust.algorithm_s([0.2, 0.5, 0.1, 0.4, 0.3], 1).degenerate


def test_arguments_outside_their_domain_are_rejected():
    from pt13528 import assigned_value, graphics, homogeneity, outliers, sigma_pt
    nan = float("nan")
    for call in (lambda: sigma_pt.from_precision(nan, 1.0, 2), lambda: sigma_pt.limit_sigma(nan),
                 lambda: sigma_pt.limit_sigma(1.0, lower=2.0, upper=1.0),
                 lambda: assigned_value.combine_uncertainty(nan), lambda: assigned_value.combine_uncertainty(-1.0),
                 lambda: assigned_value.u_robust(nan, 10), lambda: assigned_value.compare_with_reference(1.0, nan, 1.0, 0.1),
                 lambda: assigned_value.from_crm_comparison(nan, 0.1, [0.1, 0.2]),
                 lambda: homogeneity.expanded_sigma_pt(nan, 0.1), lambda: homogeneity.expanded_criterion_factors(1),
                 lambda: homogeneity.homogeneity([[1.0, 1.1], [1.2, 1.0]], sigma_pt=1.0, alpha=2),
                 lambda: graphics.bandwidth(20, robust_sd=nan), lambda: graphics.kernel_density([1.0, 2.0], 0.0),
                 lambda: graphics.repeatability_statistic(1.0, nan, 1.0, 1.0, 2),
                 lambda: graphics.ordinal_summary({"low": 3, "mid": 5, "high": 1}),
                 lambda: robust.sd_two_results(nan, 1.0), lambda: robust.algorithm_a([1, 2, 3, 4, 9], update_scale=False, scale=0.0),
                 lambda: outliers.grubbs_critical(2), lambda: outliers.cochran_critical(1, 2), lambda: outliers.cochran_critical(5, nan),
                 lambda: scores.z_reduction_factor(0.0, 0.0), lambda: scores.z_reduction_factor(-1.0, 0.1),
                 lambda: scores.classify_z(1.0, action=2.0, warning=3.0), lambda: scores.uncertainty_flag(1.0, 2.0, 1.0)):
        with pytest.raises(ValueError):
            call()
    assert graphics.ordinal_summary({"low": 3, "mid": 5, "high": 1}, order=["low", "mid", "high"])["median"] == "mid"


def test_strings_and_booleans_are_not_numbers_and_identical_results_have_no_scale():
    for bad in (["1", "2", "3", "9"], [True, False, True]):
        with pytest.raises(TypeError):
            robust.algorithm_a(bad)
    for v in (0.1, 21.8, 2.675):
        av = assigned_value.consensus([v] * 19, "mean")
        assert av.scale == 0.0 and av.degenerate
