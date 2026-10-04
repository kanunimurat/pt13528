# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Assigned value and its standard uncertainty, ISO 13528:2022 Clause 7."""
from __future__ import annotations

import math
from typing import Callable, Iterable, NamedTuple, Optional

import numpy as np

from . import robust

__all__ = [
    "AssignedValue", "combine_uncertainty", "from_crm_comparison", "consensus",
    "u_robust", "compare_with_reference", "Comparison", "bootstrap", "kernel_mode",
]


class AssignedValue(NamedTuple):
    x_pt: float
    u_x_pt: float
    method: str
    scale: Optional[float] = None
    p: Optional[int] = None
    degenerate: bool = False     # no standard deviation could be derived from the results


def combine_uncertainty(u_char: float, u_hom: float = 0.0, u_trans: float = 0.0, u_stab: float = 0.0) -> float:
    """7.2.2, Formula (3) - u(x_pt) = sqrt(u_char^2 + u_hom^2 + u_trans^2 + u_stab^2)."""
    return math.sqrt(u_char ** 2 + u_hom ** 2 + u_trans ** 2 + u_stab ** 2)


def from_crm_comparison(x_crm: float, u_crm: float, differences: Iterable[float]) -> AssignedValue:
    """7.5.2, Formulae (4) and (5) - value assigned by one laboratory against a CRM.

    ``differences`` are d_i, PT item average minus CRM average on sample i.
    u_d is the standard deviation of d_i divided by sqrt(n) (Table E.8).
    """
    d = np.asarray(list(differences), dtype=float)
    if d.size < 2:
        raise ValueError("at least two differences are required")
    d_bar = float(d.mean())
    u_d = float(d.std(ddof=1) / math.sqrt(d.size))
    return AssignedValue(x_crm + d_bar, math.hypot(u_crm, u_d), "crm-comparison", u_d, int(d.size))


def u_robust(scale: float, p: int, factor: float = 1.25) -> float:
    """7.7.7, Formula (6) - u(x_pt) = 1,25 s* / sqrt(p). NOTE 2 allows another factor."""
    if p < 1:
        raise ValueError("p must be positive")
    return factor * scale / math.sqrt(p)


def consensus(x: Iterable[float], method: str = "algorithm_a", median_scale: str = "niqr",
              tol: str | float = robust.DEFAULT_TOL) -> AssignedValue:
    """7.7 - consensus value from participant results with u(x_pt) from Formula (6).

    method: 'algorithm_a', 'median', 'q_hampel' or 'mean'. For the median the
    scale entering Formula (6) is nIQR by default (this reproduces Table E.5)
    or MADe with ``median_scale='made'``. For the arithmetic mean
    u = s / sqrt(p). ``tol`` is the stopping criterion of Algorithm A
    (see :func:`robust.algorithm_a`). ``degenerate`` is set when the scale
    is zero, in which case u(x_pt) is zero as well and has no meaning.
    """
    a = robust._arr(x)
    p = int(a.size)
    if median_scale not in ("niqr", "made"):
        raise ValueError("median_scale is 'niqr' or 'made'")
    if method == "algorithm_a":
        r = robust.algorithm_a(a, tol=tol)
        return AssignedValue(r.location, u_robust(r.scale, p), method, r.scale, p, not r.scale > 0)
    if method == "median":
        s = robust.niqr(a) if median_scale == "niqr" else robust.made(a)
        return AssignedValue(robust.median(a), u_robust(s, p), method, s, p, not s > 0)
    if method == "q_hampel":
        r = robust.q_hampel(a)
        return AssignedValue(r.location, u_robust(r.scale, p), method, float(r.scale), p, not r.scale > 0)
    if method == "mean":
        if p < 2:
            raise ValueError("the standard deviation needs at least two results")
        s = float(a.std(ddof=1))
        return AssignedValue(float(a.mean()), s / math.sqrt(p), method, s, p, not s > 0)
    raise ValueError("unknown method")


class Comparison(NamedTuple):
    x_diff: float
    u_diff: float
    ratio: float
    investigate: bool


def compare_with_reference(x_ref: float, u_ref: float, x_pt: float, u_x_pt: float) -> Comparison:
    """7.8, Formula (7) - x_diff = x_ref - x_pt against u_diff; investigate when |x_diff| > 2 u_diff."""
    x_diff = x_ref - x_pt
    u_diff = math.hypot(u_ref, u_x_pt)
    ratio = abs(x_diff) / u_diff if u_diff > 0 else math.inf
    return Comparison(x_diff, u_diff, ratio, ratio > 2.0)


def kernel_mode(x: Iterable[float], bandwidth: float, grid: int = 4096, cut: float = 3.0) -> float:
    """10.3 / E.6 - mode of a Gaussian kernel density estimate with a given bandwidth."""
    a = robust._arr(x)
    if not bandwidth > 0:
        raise ValueError("bandwidth must be positive")
    g = np.linspace(a.min() - cut * bandwidth, a.max() + cut * bandwidth, grid)
    dens = np.exp(-0.5 * ((g[:, None] - a[None, :]) / bandwidth) ** 2).sum(axis=1)
    return float(g[int(np.argmax(dens))])


def bootstrap(x: Iterable[float], statistic: Callable[[np.ndarray], float], replicates: int = 1000,
              seed: Optional[int] = None) -> AssignedValue:
    """7.7.6 - nonparametric bootstrap standard error of any location statistic.

    Returns the statistic of the original sample as x_pt and the standard
    deviation of the bootstrap replicates as u(x_pt). Results depend on the
    random number generator, so they agree with other software only within
    Monte Carlo error.
    """
    a = robust._arr(x)
    rng = np.random.default_rng(seed)
    reps = np.array([statistic(a[rng.integers(0, a.size, a.size)]) for _ in range(replicates)])
    return AssignedValue(float(statistic(a)), float(reps.std(ddof=1)), "bootstrap", float(reps.mean()), int(a.size))
