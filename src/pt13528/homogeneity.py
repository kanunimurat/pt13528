# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Homogeneity and stability checks, ISO 13528:2022 Annex B."""
from __future__ import annotations

import math
from typing import Iterable, NamedTuple, Optional, Sequence

import numpy as np
from scipy import stats

__all__ = [
    "Homogeneity", "homogeneity", "homogeneity_single", "expanded_criterion_factors",
    "expanded_sigma_pt", "Stability", "stability", "stability_t_test",
]


class Homogeneity(NamedTuple):
    g: int
    m: int
    mean: float
    s_x: float                 # standard deviation of item averages (B.7 / B.14)
    s_w: Optional[float]       # within-sample standard deviation (B.8 / B.15)
    s_s: float                 # between-sample standard deviation (B.10 / B.16)
    criterion: Optional[float]           # 0,3 sigma_pt (B.1) or 0,1 delta_E (B.2)
    sufficient: Optional[bool]
    expanded_criterion: Optional[float]  # sqrt(c) of B.2.3
    sufficient_expanded: Optional[bool]
    f_statistic: Optional[float]         # B.2.4 a)
    f_critical: Optional[float]
    f_significant: Optional[bool]


def expanded_criterion_factors(g: int, m: int = 2) -> tuple[float, float]:
    """B.2.3 - factors F1 and F2 (Table B.1), or F1 and F_m when m > 2.

    F1 = chi2_0,95(g - 1) / (g - 1).
    F2 = (F_0,95(g - 1, g) - 1) / 2 for duplicates.
    F_m = (F_0,95(g - 1, g(m - 1)) - 1) / m for m > 2.
    """
    f1 = stats.chi2.ppf(0.95, g - 1) / (g - 1)
    f2 = (stats.f.ppf(0.95, g - 1, g * (m - 1)) - 1.0) / m
    return float(f1), float(f2)


def homogeneity(samples: Sequence[Sequence[float]], sigma_pt: Optional[float] = None,
                delta_e: Optional[float] = None, alpha: float = 0.05) -> Homogeneity:
    """B.3 - homogeneity check with g items measured m times each (m >= 2).

    Computes s_x, s_w and s_s (Formulae B.4 to B.10; B.11 to B.16 are the
    m = 2 special case), the criterion of B.2.2, the expanded criterion of
    B.2.3 and the analysis-of-variance F test of B.2.4 a).
    """
    x = np.asarray(samples, dtype=float)
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 2:
        raise ValueError("samples must be g x m with g >= 2 and m >= 2 (balanced design)")
    g, m = x.shape
    item_mean = x.mean(axis=1)
    s_x2 = float(item_mean.var(ddof=1))
    s_w2 = float(x.var(axis=1, ddof=1).mean())
    s_s = math.sqrt(max(0.0, s_x2 - s_w2 / m))
    crit = 0.3 * sigma_pt if sigma_pt is not None else (0.1 * delta_e if delta_e is not None else None)
    exp_crit = suff = suff_exp = None
    if crit is not None:
        suff = s_s <= crit
        f1, f2 = expanded_criterion_factors(g, m)      # Table B.1 lists g = 7..20; the formulae are general
        exp_crit = math.sqrt(f1 * crit ** 2 + f2 * s_w2)
        suff_exp = s_s <= exp_crit
    f_stat = f_crit = f_sig = None
    if s_w2 > 0:
        f_stat = m * s_x2 / s_w2
        f_crit = float(stats.f.ppf(1 - alpha, g - 1, g * (m - 1)))
        f_sig = f_stat > f_crit
    return Homogeneity(g, m, float(item_mean.mean()), math.sqrt(s_x2), math.sqrt(s_w2), s_s,
                       crit, suff, exp_crit, suff_exp, f_stat, f_crit, f_sig)


def homogeneity_single(values: Iterable[float], sigma_pt: Optional[float] = None,
                       delta_e: Optional[float] = None) -> Homogeneity:
    """B.1.2 - one measurement per item (no replicates possible).

    The standard deviation of the results is used as s_s; it includes the
    repeatability of the method and is therefore an upper bound.
    """
    v = np.asarray(list(values), dtype=float)
    if v.size < 2:
        raise ValueError("at least two items are required")
    s = float(v.std(ddof=1))
    crit = 0.3 * sigma_pt if sigma_pt is not None else (0.1 * delta_e if delta_e is not None else None)
    return Homogeneity(int(v.size), 1, float(v.mean()), s, None, s, crit,
                       None if crit is None else s <= crit, None, None, None, None, None)


def expanded_sigma_pt(sigma_pt: float, s_s: float) -> float:
    """B.2.5 a), Formula (B.3) - sigma'_pt = sqrt(sigma_pt^2 + s_s^2)."""
    return math.hypot(sigma_pt, s_s)


class Stability(NamedTuple):
    mean_1: float
    mean_2: float
    difference: float
    criterion: float
    stable: bool
    expanded_criterion: Optional[float]
    stable_expanded: Optional[bool]


def stability(y1: Iterable[float], y2: Iterable[float], sigma_pt: Optional[float] = None,
              delta_e: Optional[float] = None, u_y1: Optional[float] = None,
              u_y2: Optional[float] = None) -> Stability:
    """B.5.1 and B.5.2 - |mean(y1) - mean(y2)| against 0,3 sigma_pt (B.17).

    With u_y1 and u_y2 the expanded criterion of Formula (B.18),
    0,3 sigma_pt + 2 sqrt(u^2(y1) + u^2(y2)), is evaluated as well. The same
    criteria apply to transport stability (B.6.3).
    """
    if sigma_pt is None and delta_e is None:
        raise ValueError("give sigma_pt or delta_E")
    a = np.asarray(list(y1), dtype=float)
    b = np.asarray(list(y2), dtype=float)
    crit = 0.3 * sigma_pt if sigma_pt is not None else 0.1 * delta_e
    diff = abs(float(a.mean()) - float(b.mean()))
    exp_crit = stable_exp = None
    if u_y1 is not None and u_y2 is not None:
        exp_crit = crit + 2.0 * math.hypot(u_y1, u_y2)
        stable_exp = diff <= exp_crit
    return Stability(float(a.mean()), float(b.mean()), diff, crit, diff <= crit, exp_crit, stable_exp)


def stability_t_test(item_means_1: Iterable[float], item_means_2: Iterable[float],
                     alpha: float = 0.05, equal_var: bool = False):
    """B.5.4 NOTE - t test at the 95 % level using the means for each proficiency test item.

    Pass one mean per item, not the individual test portions; pooling the
    portions would understate the standard error of the difference. Returns
    (t, degrees of freedom, p value, significant).
    """
    a = np.asarray(list(item_means_1), dtype=float)
    b = np.asarray(list(item_means_2), dtype=float)
    if a.size < 2 or b.size < 2:
        raise ValueError("at least two item means per occasion are required")
    res = stats.ttest_ind(a, b, equal_var=equal_var)
    return float(res.statistic), float(res.df), float(res.pvalue), bool(res.pvalue < alpha)
