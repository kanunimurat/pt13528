# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Comparison with code the authors did not write (statsmodels).

statsmodels implements Huber's proposal 2 and the Qn, MAD and IQR scale
estimators independently of ISO 13528. Algorithm A of ISO 13528 is Huber's
proposal 2 with tuning constant 1,5; the standard prints the consistency
factor as 1,134, statsmodels uses the unrounded value 1,13339... The test
therefore runs Algorithm A to convergence with the unrounded factor and
requires agreement to 1e-9, and separately checks that the printed factor
changes s* by less than 0,2 %.
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


def test_qn_made_niqr():
    for x in _sets():
        p = len(x)
        d = np.sort(np.abs(x[:, None] - x[None, :])[np.triu_indices(p, 1)])
        h = p // 2 + 1
        bp = robust.qn(x) / (2.2191 * d[h * (h - 1) // 2 - 1])           # finite-sample factor of Table C.2 / (C.20), (C.21)
        ref = float(sm.qn_scale(x))                                     # no finite-sample factor, constant 2.219144...
        if ref > 0:
            assert robust.qn(x) / bp == pytest.approx(ref, rel=3e-5)    # 2,2191 against 2,219144
        if sm.mad(x) > 0:
            assert robust.made(x) == pytest.approx(float(sm.mad(x)), rel=5e-4)   # 1,483 against 1,4826
        assert robust.niqr(x) == pytest.approx(float(sm.iqr(x)), rel=5e-5)       # 0,7413 against 1/1,349
