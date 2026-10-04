# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Degenerate and invalid input, and independence of the unit of the data."""
import math

import numpy as np
import pytest

from pt13528 import assigned_value, homogeneity, record, robust, scores

NAN = float("nan")


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


def test_three_figure_rule_depends_on_the_origin():
    """The criterion of C.3.1 on the same eleven results in degrees Celsius and in kelvin.

    In kelvin the third significant figure of x* is the units digit, which no iterate changes, and
    s* happens to keep its third figure in the first step: the iteration stops at once with an s*
    that is 78 % too small, and four results get an action signal. See docs/coverage.md.
    """
    x = [18.2, 18.2, 18.4, 18.4, 18.4, 18.4, 18.6, 19.8, 20.5, 20.9, 22.3]
    k = [v + 273.15 for v in x]
    full = robust.algorithm_a(x)
    assert full.scale == pytest.approx(1.3299, abs=5e-5)
    assert robust.algorithm_a(k).scale == pytest.approx(full.scale, rel=1e-9)
    celsius, kelvin = robust.algorithm_a(x, tol="sig3"), robust.algorithm_a(k, tol="sig3")
    assert celsius.scale == pytest.approx(1.328, abs=5e-4)
    assert kelvin.iterations == 1 and kelvin.scale == pytest.approx(0.297, abs=5e-4)
    assert record.round_record(k, tol="sig3").counts["action"] == 4
    assert record.round_record(k).counts["action"] == 0
    assert record.round_record(x, tol="sig3").counts["action"] == 0


@pytest.mark.parametrize("tol", ["sig3", 1e-12])
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


@pytest.mark.parametrize("tol", ["sig3", 1e-10, 1e-12])
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
