# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Robust estimators of ISO 13528:2022 Annex C (and D.1.4.2).

Every public function names the clause or formula it implements.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np
from scipy.stats import norm

from ._common import DEFAULT_TOL, _arr, _finite

__all__ = [
    "median", "made", "niqr", "algorithm_a", "algorithm_s", "qn", "q_method",
    "hampel", "q_hampel", "mean_abs_dev_sd", "sd_two_results", "RobustResult",
]

MADE_FACTOR = 1.483      # C.2.2
NIQR_FACTOR = 0.7413     # C.2.3
ALG_A_FACTOR = 1.134     # C.3.1, Formula (C.10)
ALG_A_DELTA = 1.5        # C.3.1, Formula (C.7)

# Table C.1 - limit factor (eta) and adjustment factor (xi) for Algorithm S
_ALG_S = {1: (1.645, 1.097), 2: (1.517, 1.054), 3: (1.444, 1.039), 4: (1.395, 1.032),
          5: (1.359, 1.027), 6: (1.332, 1.024), 7: (1.310, 1.021), 8: (1.292, 1.019),
          9: (1.277, 1.018), 10: (1.264, 1.017)}
# Table C.2 - correction factor b_p for Qn, 2 <= p <= 12
_QN_BP = {2: 0.3994, 3: 0.9937, 4: 0.5132, 5: 0.8440, 6: 0.6122, 7: 0.8588,
          8: 0.6699, 9: 0.8734, 10: 0.7201, 11: 0.8891, 12: 0.7574}


_EPS = 8 * np.finfo(float).eps     # floor of the relative stopping criterion
_COLLAPSE = 1e-9                    # s* below this fraction of its starting value is reported as zero




class RobustResult(dict):
    """Dictionary with attribute access (location, scale, iterations, converged, degenerate)."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None


def _sig3(v: float) -> float:
    if v == 0:
        return 0.0
    return round(v, 2 - int(math.floor(math.log10(abs(v)))))


def median(x: Iterable[float]) -> float:
    """C.2.1 - median."""
    return float(np.median(_arr(x)))


def made(x: Iterable[float]) -> float:
    """C.2.2 - scaled median absolute deviation, MADe = 1,483 med|x_i - med(x)|."""
    a = _arr(x)
    return float(MADE_FACTOR * np.median(np.abs(a - np.median(a))))


def niqr(x: Iterable[float], quantile_method: str = "linear") -> float:
    """C.2.3 - normalized interquartile range, nIQR = 0,7413 (Q3 - Q1).

    Quartile definitions differ between software packages (see the NOTE under
    Table E.5). The default, linear interpolation (R type 7), reproduces the
    value printed in Table E.5.
    """
    a = _arr(x)
    q1, q3 = np.quantile(a, [0.25, 0.75], method=quantile_method)
    return float(NIQR_FACTOR * (q3 - q1))


_RULES = {"iso2022": "iso2022", "iso2022-from-start": "iso2022-from-start", "equivalent-figure": "equivalent-figure",
          "sig3-of-x": "iso2022-from-start", "sig3": "equivalent-figure"}      # 0.1.6 names keep their 0.1.6 behaviour


def _stopping(tol):
    if isinstance(tol, str):
        if tol not in _RULES:
            raise ValueError("tol must be a positive number, 'iso2022', 'iso2022-from-start' or 'equivalent-figure'")
        return _RULES[tol]
    if isinstance(tol, bool) or not isinstance(tol, (int, float)) or not (math.isfinite(tol) and tol > 0):
        raise ValueError("tol must be a positive number, 'iso2022', 'iso2022-from-start' or 'equivalent-figure'")
    return float(tol)


def algorithm_a(x: Iterable[float], tol: str | float = DEFAULT_TOL, max_iter: int = 100_000,
                update_scale: bool = True, scale: float | None = None) -> RobustResult:
    """C.3.1 / C.3.2 - Algorithm A (Formulae C.5 to C.10).

    Returns the robust mean x* (``location``) and robust standard deviation
    s* (``scale``).

    tol
        A float (default 1e-10) stops when the changes of x* and s* both
        fall below ``tol`` times s*. This criterion is relative, so the
        result depends neither on the unit nor on the origin of the data.

        ``"iso2022"`` is the stopping criterion of ISO 13528:2022, C.3.1:
        no change "from one iteration to the next" in the third significant
        figures of x* and of s*. The starting values (median, MADe) are not
        an iteration, so the earliest stop is after the second update. It
        stops before convergence, and because significant figures depend on
        the unit and on the origin of the results, so does its result (see
        docs/coverage.md). It reproduces the worked examples of Annex E.

        ``"iso2022-from-start"`` also compares the first update with the
        starting values and can therefore stop after one update. This is
        what ``"iso2022"`` did in 0.1.7 and what the library did by default
        up to 0.1.4. For data far from zero it can stop at a scale that is
        several times too small (see docs/coverage.md).

        ``"equivalent-figure"`` is a variant: no change in the third
        significant figure of s* and in the same decimal place of x*. The
        wording "the equivalent figure" is quoted in the literature from
        the 2005 edition of ISO 13528; the authors have not seen that
        edition. It reproduces Annex E as well and does not depend on the
        origin, but still on the unit.

        The names ``"sig3-of-x"`` and ``"sig3"`` of version 0.1.6 are
        accepted for ``"iso2022-from-start"`` and ``"equivalent-figure"``
        (the latter did compare the first update with the starting values
        in 0.1.6 and 0.1.7).

    When a large majority of the results is identical, the iteration can
    drive s* towards zero. This is detected and returned as ``scale=0.0``
    with ``degenerate=True``; no standard deviation can be derived from
    such data. The iteration runs on (x - median) / max|x - median|, so that
    neither the detection nor the result depends on the level or the unit of
    the results.
    update_scale, scale
        C.3.2 b): pass ``update_scale=False`` to keep s* fixed during iteration
        (at MADe, or at ``scale`` when given, e.g. the Q-method estimate).
    """
    tol = _stopping(tol)
    a = np.sort(_arr(x))
    p = a.size
    if p == 1:
        return RobustResult(location=float(a[0]), scale=0.0, iterations=0, converged=True, degenerate=True)
    if scale is not None and not (math.isfinite(scale) and scale > 0):
        raise ValueError("a given scale must be finite and positive")
    c = float(np.median(a))                 # iterate on x - median: identical results become exactly zero,
    a = a - c                               # so a collapsing s* is not masked by rounding noise of large x
    m = float(np.max(np.abs(a)))
    if m == 0.0:
        return RobustResult(location=c, scale=0.0, iterations=0, converged=True, degenerate=True)
    a = a / m                               # and on unit scale: no overflow or underflow of squares
    x_star = 0.0
    s_star = float(scale) / m if scale is not None else made(a)
    if s_star == 0.0:                       # C.3.1 NOTE 2
        s_star = float(np.std(a, ddof=1))
    s_0 = s_star
    ratio = None
    for it in range(1, max_iter + 1):
        delta = ALG_A_DELTA * s_star
        lo, hi = x_star - delta, x_star + delta
        w = np.clip(a, lo, hi)
        new_x = float(w.mean())
        new_s = float(ALG_A_FACTOR * np.sqrt(np.sum((w - new_x) ** 2) / (p - 1))) if update_scale else s_star
        if tol == "equivalent-figure":                # third figure of s*, equivalent figure (same decimal place) of x*
            d = 2 - int(math.floor(math.log10(m * new_s))) if new_s > 0 else 0
            done = (round(c + m * new_x, d) == round(c + m * x_star, d)
                    and _sig3(m * new_s) == _sig3(m * s_star))
        elif tol in ("iso2022", "iso2022-from-start"):   # third significant figures of x* and of s*
            done = (_sig3(c + m * new_x) == _sig3(c + m * x_star)
                    and _sig3(m * new_s) == _sig3(m * s_star))

        else:
            limit = max(tol * new_s, _EPS * abs(new_x))
            done = abs(new_x - x_star) < limit and abs(new_s - s_star) < limit
        if it == 1 and tol in ("iso2022", "equivalent-figure"):
            done = False                    # "from one iteration to the next": the starting values (median,
                                            # MADe) are not an iteration (C.3.1, Table E.4)
        if update_scale:
            if new_s < _COLLAPSE * s_0:
                return RobustResult(location=c + m * new_x, scale=0.0, iterations=it, converged=True, degenerate=True)
            # All results that are not winsorized are identical: s* then changes by a factor that
            # settles to a constant. A constant factor below one means s* falls to zero, however
            # slowly, and the iteration is stopped here instead of running into max_iter.
            inside = a[(a >= lo) & (a <= hi)]
            if inside.size and inside[0] == inside[-1] and new_s < s_star:
                r = new_s / s_star
                if ratio is not None and abs(r - ratio) <= 1e-12:
                    return RobustResult(location=c + m * float(inside[0]), scale=0.0, iterations=it,
                                        converged=True, degenerate=True)
                ratio = r
            else:
                ratio = None
        x_star, s_star = new_x, new_s
        if done:
            return RobustResult(location=c + m * x_star, scale=m * s_star, iterations=it, converged=True,
                                degenerate=False)
    return RobustResult(location=c + m * x_star, scale=m * s_star, iterations=max_iter, converged=False,
                        degenerate=False)


def algorithm_s(w: Iterable[float], nu: int, tol: str | float = DEFAULT_TOL, max_iter: int = 100_000) -> RobustResult:
    """C.4 - Algorithm S: robust pooled standard deviation (or range).

    nu is the degrees of freedom of each w_i (1 for ranges of duplicates,
    m - 1 for standard deviations of m results); Table C.1 covers nu = 1..10.
    A float ``tol`` is relative to w*, as in :func:`algorithm_a`; ``"iso2022"``
    (or ``"equivalent-figure"``, the two do not differ here) stops when the third
    significant figure of w* does not change from one iteration to the next;
    ``"iso2022-from-start"`` also compares the first update with the starting value.
    """
    tol = _stopping(tol)
    if isinstance(nu, bool) or nu not in _ALG_S:
        raise ValueError("Table C.1 gives factors for nu = 1..10 only")
    eta, xi = _ALG_S[nu]
    a = np.sort(_arr(w))
    if a[0] < 0:
        raise ValueError("ranges and standard deviations cannot be negative")
    m = float(a[-1])
    if m == 0.0:
        return RobustResult(location=0.0, scale=0.0, iterations=0, converged=True, degenerate=True)
    a = a / m                               # unit scale: no overflow or underflow of squares
    w_star = float(np.median(a))
    if w_star == 0.0:                       # C.4 NOTE
        w_star = float(np.sqrt(np.mean(a ** 2)))
    w_0 = w_star
    for it in range(1, max_iter + 1):
        psi = eta * w_star
        new = float(xi * np.sqrt(np.mean(np.minimum(a, psi) ** 2)))
        # a large majority of zeros drives w* to zero: either it has fallen far enough, or every
        # value below the limit is zero, in which case w* shrinks by the same factor for ever
        if new < _COLLAPSE * w_0 or (new < w_star and not np.any(a[a <= psi] > 0)):
            return RobustResult(location=0.0, scale=0.0, iterations=it, converged=True, degenerate=True)
        if isinstance(tol, str):
            done = _sig3(m * new) == _sig3(m * w_star) and (it > 1 or tol == "iso2022-from-start")
        else:
            done = abs(new - w_star) < max(tol * new, _EPS * new)
        w_star = new
        if done:
            return RobustResult(location=m * w_star, scale=m * w_star, iterations=it, converged=True,
                                degenerate=False)
    return RobustResult(location=m * w_star, scale=m * w_star, iterations=max_iter, converged=False,
                        degenerate=False)


def qn(x: Iterable[float], h_rule: str = "rousseeuw-croux") -> float:
    """C.5.2.1 - Qn estimator of the standard deviation (Formulae C.15 to C.21).

    h_rule
        The default ``"rousseeuw-croux"`` is h = floor(p/2) + 1 with the
        factor 2,219 1. This is the definition of the estimator's authors and,
        since ISO 13528:2022/Amd 1:2026, also the text of Formulae (C.18) and
        (C.19). ``"iso-literal"`` reproduces the 2022 edition as first
        printed: h = p/2 (p even) or (p - 1)/2 (p odd) with the factor
        2,221 9. That formula gives k = 0 for p = 2 and 3 and raises for
        p < 4.
    """
    a = _arr(x)
    p = a.size
    if p < 2:
        raise ValueError("Qn needs at least two results")
    i, j = np.triu_indices(p, k=1)
    d = np.sort(np.abs(a[i] - a[j]))
    factor = 2.2191
    if h_rule == "rousseeuw-croux":
        h = p // 2 + 1
    elif h_rule == "iso-literal":
        h = p // 2 if p % 2 == 0 else (p - 1) // 2
        factor = 2.2219
    else:
        raise ValueError("h_rule must be 'rousseeuw-croux' or 'iso-literal'")
    k = h * (h - 1) // 2
    if k < 1:
        raise ValueError("Formula (C.18) of the 2022 edition is undefined for p < 4")
    if p <= 12:
        bp = _QN_BP[p]
    elif p % 2:
        rp = (1 / p) * (1.6019 + (1 / p) * (-2.128 - 5.172 / p))
        bp = 1 / (rp + 1)
    else:
        rp = (1 / p) * (3.6756 + (1 / p) * (1.965 + (1 / p) * (6.987 - 77 / p)))
        bp = 1 / (rp + 1)
    return float(factor * d[k - 1] * bp)


def q_method(results: Sequence[float] | Sequence[Sequence[float]]) -> float:
    """C.5.2.2 - Q method robust (reproducibility) standard deviation (C.22 to C.25).

    ``results`` is either one value per laboratory or one sequence of replicates
    per laboratory. Between-laboratory absolute differences are weighted
    1/(n_i n_j) as in Formula (C.23).
    """
    if isinstance(results, (str, bytes, dict)) or any(isinstance(g, (str, bytes, dict)) for g in results):
        raise TypeError("results must be numbers or sequences of numbers")
    groups = [np.atleast_1d(np.asarray(g, dtype=float)) for g in results]
    if any(g.ndim != 1 for g in groups):
        raise ValueError("each laboratory needs a number or a one-dimensional sequence of numbers")
    if any(g.size == 0 or not np.all(np.isfinite(g)) for g in groups):
        raise ValueError("values must be finite and every laboratory needs at least one result")
    p = len(groups)
    if p < 2:
        raise ValueError("the Q method needs at least two laboratories")
    diffs, weights = [], []
    for i in range(p - 1):
        for j in range(i + 1, p):
            d = np.abs(groups[i][:, None] - groups[j][None, :]).ravel()
            diffs.append(d)
            weights.append(np.full(d.size, 1.0 / (groups[i].size * groups[j].size)))
    d = np.concatenate(diffs)
    w = np.concatenate(weights) * 2.0 / (p * (p - 1))
    order = np.argsort(d, kind="mergesort")
    d, w = d[order], w[order]
    # Differences that are equal in exact arithmetic (results reported to a fixed number of
    # decimals) differ by rounding noise in binary; they are merged so that H1 has one
    # discontinuity per distinct difference, whatever the unit of the data. Two such
    # differences are at most 2 eps max|x| apart; the tolerance is twice that. A group
    # extends from its first member only, so that close but distinct differences do not chain.
    tie = 4 * np.finfo(float).eps * max(float(np.max(np.abs(g))) for g in groups)
    d = np.where(d <= tie, 0.0, d)
    starts = [0]
    for k in range(1, d.size):
        if d[k] - d[starts[-1]] > tie:
            starts.append(k)
    idx = np.asarray(starts)
    pts = d[idx]
    h = np.add.reduceat(w, idx).cumsum()          # H1 at each discontinuity point
    h0 = float(h[0]) if pts[0] == 0.0 else 0.0
    if pts[0] == 0.0:
        gx = pts
        g = np.concatenate([[0.0], 0.5 * (h[1:] + h[:-1])])
    else:
        gx = np.concatenate([[0.0], pts])
        g = np.concatenate([[0.0], [0.5 * h[0]], 0.5 * (h[1:] + h[:-1])])
    q = 0.25 + 0.75 * h0
    num = float(np.interp(q, g, gx))
    den = math.sqrt(2.0) * norm.ppf(0.625 + 0.375 * h0)
    return num / den


def _psi(q: np.ndarray) -> np.ndarray:
    """Formula (C.30) with a = 1,5, b = 3, c = 4,5."""
    a = np.abs(q)
    out = np.where(a <= 1.5, q, np.where(a <= 3.0, 1.5 * np.sign(q),
                   np.where(a <= 4.5, (4.5 - a) * np.sign(q), 0.0)))
    return out


def hampel(x: Iterable[float], scale: float, method: str = "finite") -> float:
    """C.5.3 - Hampel estimator of location.

    method ``"finite"`` is the finite-step algorithm of C.5.3.3 (unique result);
    ``"iterative"`` is the reweighting scheme of C.5.3.2.
    """
    y = _arr(x)
    med = float(np.median(y))
    if method not in ("finite", "iterative"):
        raise ValueError("method must be 'finite' or 'iterative'")
    if isinstance(scale, bool) or not (isinstance(scale, (int, float, np.floating, np.integer))
                                       and math.isfinite(scale) and scale >= 0):
        raise ValueError("scale must be finite and not negative")
    if scale == 0:
        return med
    if method == "iterative":
        x_star = med
        limit = 0.01 * scale / math.sqrt(y.size)
        for _ in range(1000):
            q = np.abs((y - x_star) / scale)
            with np.errstate(divide="ignore", invalid="ignore"):
                w = np.where(q <= 1.5, 1.0, np.where(q <= 3.0, 1.5 / q,
                             np.where(q <= 4.5, (4.5 - q) / q, 0.0)))
            if np.sum(w) == 0:          # no result within 4,5 s* of the current value
                return med
            new = float(np.sum(w * y) / np.sum(w))
            if abs(new - x_star) < limit:
                return new
            x_star = new
        return x_star
    q = (y - med) / scale                   # standardized results: the search does not depend on the unit
    nodes = np.sort(np.concatenate([q + c for c in (-4.5, -3.0, -1.5, 1.5, 3.0, 4.5)]))
    pm = np.array([_psi(q - d).sum() for d in nodes])
    sols: list[float] = []
    tiny = 1e-12 * max(1.0, float(np.max(np.abs(q))))
    for m in range(nodes.size - 1):
        a, b = pm[m], pm[m + 1]
        if abs(a) < 1e-12:
            sols.append(float(nodes[m]))
        if abs(b) < 1e-12:
            sols.append(float(nodes[m + 1]))
        if a * b < 0 and nodes[m + 1] - nodes[m] > tiny:
            slope = (b - a) / (nodes[m + 1] - nodes[m])
            sols.append(float(nodes[m] - a / slope))
    if not sols:
        return med
    sols_arr = np.unique(np.round(np.array(sols), 12))
    dist = np.abs(sols_arr)
    best = np.flatnonzero(np.isclose(dist, dist.min(), rtol=0, atol=tiny))
    return float(med + scale * sols_arr[best[0]]) if best.size == 1 else med


def q_hampel(results: Sequence[float] | Sequence[Sequence[float]]) -> RobustResult:
    """C.5.4 - Q/Hampel: Q-method scale with the finite-step Hampel location."""
    s = q_method(results)
    means = [float(np.mean(g)) for g in results]
    return RobustResult(location=hampel(means, s, "finite"), scale=float(s), iterations=0, converged=True,
                        degenerate=not s > 0)


def mean_abs_dev_sd(x: Iterable[float]) -> float:
    """D.1.4.2 NOTE 4, Formula (D.1) - s* from the mean absolute deviation from the median."""
    a = _arr(x)
    return float(np.sum(np.abs(a - np.median(a))) / (0.798 * a.size))


def sd_two_results(x1: float, x2: float) -> float:
    """D.1.4.2 NOTE 3 - dispersion estimate for p = 2: |x1 - x2| / sqrt(2)."""
    _finite(x1, x2)
    return abs(x1 - x2) / math.sqrt(2.0)
