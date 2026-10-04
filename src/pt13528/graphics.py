# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Numerical parts of the graphical methods of ISO 13528:2022 Clause 10 and of Clause 11.

The functions return the numbers to plot; drawing is left to the caller.
"""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from scipy import stats

__all__ = ["bandwidth", "kernel_density", "repeatability_statistic", "repeatability_region", "ordinal_summary"]


def bandwidth(p: int, robust_sd: float | None = None, sigma_pt: float | None = None,
              delta_e: float | None = None) -> float:
    """10.3.2 i) - a) 0,9 s*/p^0,2 for general inspection; b) 0,75 sigma_pt or 0,25 delta_E."""
    if robust_sd is not None:
        return 0.9 * robust_sd / p ** 0.2
    if sigma_pt is not None:
        return 0.75 * sigma_pt
    if delta_e is not None:
        return 0.25 * delta_e
    raise ValueError("give robust_sd, sigma_pt or delta_E")


def kernel_density(x: Iterable[float], bandwidth: float, grid: int = 512, cut: float = 3.0):
    """10.3 - Gaussian kernel density estimate. Returns (grid points, density)."""
    a = np.asarray(list(x), dtype=float)
    g = np.linspace(a.min() - cut * bandwidth, a.max() + cut * bandwidth, grid)
    z = (g[:, None] - a[None, :]) / bandwidth
    dens = np.exp(-0.5 * z * z).sum(axis=1) / (a.size * bandwidth * math.sqrt(2 * math.pi))
    return g, dens


def repeatability_statistic(mean_i: float, sd_i: float, x_star: float, w_star: float, m: int) -> float:
    """10.6.2, Formula (23) - approximately chi-squared with 2 degrees of freedom."""
    return m * ((mean_i - x_star) / w_star) ** 2 + 2 * (m - 1) * math.log(sd_i / w_star) ** 2


def repeatability_region(x_star: float, w_star: float, m: int, level: float = 0.99, points: int = 201):
    """10.6.2, Formulae (24) and (25) - critical region. Returns (x, s_lower, s_upper)."""
    chi = stats.chi2.ppf(level, 2)
    half = w_star * math.sqrt(chi / m)
    x = np.linspace(x_star - half, x_star + half, points)
    inner = np.clip(chi - m * ((x - x_star) / w_star) ** 2, 0.0, None)
    e = np.sqrt(inner / (2 * (m - 1)))
    return x, w_star * np.exp(-e), w_star * np.exp(e)


def ordinal_summary(counts: dict) -> dict:
    """Clause 11 / E.15 - mode and median of an ordinal quantity given {category: count}."""
    cats = sorted(counts)
    total = sum(counts.values())
    mode = max(cats, key=lambda c: counts[c])
    cum, med = 0, cats[-1]
    for c in cats:
        cum += counts[c]
        if cum >= total / 2:
            med = c
            break
    return {"mode": mode, "median": med, "n": total}
