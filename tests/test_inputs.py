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


def test_three_figure_rule_does_not_depend_on_the_unit():
    rng = np.random.default_rng(6)
    x = rng.normal(10, 1, 20)
    a, b = robust.algorithm_a(x), robust.algorithm_a(x * 1e-6)
    assert a.iterations == b.iterations and b.scale / 1e-6 == pytest.approx(a.scale, rel=1e-9)


@pytest.mark.parametrize("tol", ["sig3", 1e-12])
def test_more_than_half_identical_results(tol):
    r = robust.algorithm_a([5, 5, 5, 5, 5, 5, 9], tol=tol)
    assert r.scale == 0.0 and r.degenerate and r.location == pytest.approx(5.0)
    assert not robust.algorithm_a([1, 2, 3, 4, 5, 6, 9], tol=tol).degenerate
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
        scores.uncertainty_negligible(-0.1, sigma_pt=1.0)
    with pytest.raises(ValueError):
        record.round_record([1, 2, 3], x_pt=2.0, u_x_pt=-0.1, sigma_pt=1.0)


def test_hampel_iterative_with_two_distant_groups():
    x = [0.0] * 5 + [100.0] * 5
    assert math.isfinite(robust.hampel(x, 1.0, "iterative"))
