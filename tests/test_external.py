# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Comparison with code the authors did not write (statsmodels).

statsmodels implements Huber's proposal 2 and the Qn, MAD and IQR scale
estimators independently of ISO 13528. Algorithm A of ISO 13528 is Huber's
proposal 2 with tuning constant 1,5; the standard prints the consistency
factor as 1,134, statsmodels uses the unrounded value 1,13339... The test
therefore runs Algorithm A to convergence with the unrounded factor and
requires agreement to 1e-9, and separately checks that the printed factor
changes s* by less than 1 % (0,05 % to 0,3 % in these sets).

Qn is compared with the unscaled statsmodels estimate multiplied by the
finite-sample factors of Rousseeuw and Croux as tabulated, to six figures, in
the R package robustbase; the factors are typed here and not taken from the
library. The Hampel estimator is compared with a root search that shares no
code with the finite-step algorithm.
"""
import math

import numpy as np
import pytest

from pt13528 import robust

sm = pytest.importorskip("statsmodels.robust.scale")
norm = pytest.importorskip("scipy.stats").norm


def _sets(n=300):
    rng = np.random.default_rng(13528)
    for c in range(n):
        p = int(rng.integers(6, 41))
        x = rng.normal(rng.uniform(1, 100), rng.uniform(0.1, 5), p)
        k = int(rng.integers(0, max(1, p // 5) + 1))
        if k:
            x[rng.choice(p, k, replace=False)] += rng.normal(0, 25, k)
        yield np.round(x, 1) if c % 2 else x


def test_algorithm_a_is_huber_proposal_2(monkeypatch):
    c = 1.5
    gamma = 2 * norm.cdf(c) - 1 - 2 * c * norm.pdf(c) + 2 * c * c * (1 - norm.cdf(c))
    exact = 1 / math.sqrt(gamma)
    assert round(exact, 3) == 1.133                     # the standard prints 1,134
    huber = sm.Huber(c=c, tol=1e-13, maxiter=5000)
    worst_printed = 0.0
    for x in _sets():
        loc, scale = huber(x)
        printed = robust.algorithm_a(x, tol=1e-13, max_iter=5000)
        worst_printed = max(worst_printed, abs(printed.scale - scale) / scale)
        with monkeypatch.context() as m:
            m.setattr(robust, "ALG_A_FACTOR", exact)
            r = robust.algorithm_a(x, tol=1e-13, max_iter=5000)
        assert r.location == pytest.approx(float(loc), abs=1e-9 * max(1.0, abs(loc)))
        assert r.scale == pytest.approx(float(scale), rel=1e-9)
    assert worst_printed < 0.01


# finite-sample factors d_n of Qn, robustbase (>= 0.93): table for n = 2..12, polynomial above
_DN = {2: .399356, 3: .99365, 4: .51321, 5: .84401, 6: .61220, 7: .85877,
       8: .66993, 9: .87344, 10: .72014, 11: .88906, 12: .75743}


def _dn(n):
    if n <= 12:
        return _DN[n]
    if n % 2:
        return 1 / (1 + (1.60188 + (-2.1284 - 5.172 / n) / n) / n)
    return 1 / (1 + (3.67561 + (1.9654 + (6.987 - 77 / n) / n) / n) / n)


def test_qn_made_niqr():
    for x in _sets():
        ref = float(sm.qn_scale(x)) * _dn(len(x))                       # constant 2.219144... against 2,2191
        if ref > 0:
            assert robust.qn(x) == pytest.approx(ref, rel=1e-4)
        if sm.mad(x) > 0:
            assert robust.made(x) == pytest.approx(float(sm.mad(x)), rel=5e-4)   # 1,483 against 1,4826
        assert robust.niqr(x) == pytest.approx(float(sm.iqr(x)), rel=5e-5)       # 0,7413 against 1/1,349


def test_qn_small_samples():
    rng = np.random.default_rng(2)
    for p in range(2, 14):
        for _ in range(20):
            x = rng.normal(10, 2, p)
            assert robust.qn(x) == pytest.approx(float(sm.qn_scale(x)) * _dn(p), rel=1e-4)


def test_hampel_against_root_search():
    """All roots of sum(psi((x_i - m)/s)) = 0 by a dense sign-change search; the one nearest the median is taken."""
    brentq = pytest.importorskip("scipy.optimize").brentq
    for x in _sets(120):
        s = robust.q_method(x)
        if s <= 0:
            continue

        def f(m):
            return float(robust._psi((x - m) / s).sum())
        grid = np.linspace(x.min() - 5 * s, x.max() + 5 * s, 20001)
        v = np.array([f(m) for m in grid])
        roots = [brentq(f, grid[i], grid[i + 1], xtol=1e-14, rtol=1e-14)
                 for i in range(grid.size - 1) if v[i] * v[i + 1] < 0]
        inside = [r for r in roots if np.any(np.abs(x - r) < 4.5 * s)]
        med = float(np.median(x))
        best = min(inside, key=lambda r: abs(r - med))
        assert robust.hampel(x, s) == pytest.approx(best, abs=1e-8 * max(1.0, abs(best)))
