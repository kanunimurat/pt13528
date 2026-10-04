# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Outlier tests referenced by ISO 13528:2022 (6.6, B.2.1 c, D.1.2); definitions from ISO 5725-2."""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from scipy import stats

__all__ = ["grubbs_critical", "grubbs", "cochran_critical", "cochran"]


def grubbs_critical(n: int, alpha: float = 0.01) -> float:
    """6.6.2 NOTE, D.1.2 - critical value of Grubbs' test for one outlying observation, as tabulated
    in ISO 5725-2 (two-sided: alpha / (2n) in the t quantile)."""
    t = stats.t.ppf(1 - alpha / (2 * n), n - 2)
    return float((n - 1) / math.sqrt(n) * math.sqrt(t * t / (n - 2 + t * t)))


def grubbs(x: Iterable[float], alpha: float = 0.01):
    """6.6.2 NOTE, D.1.2 - Grubbs' test of ISO 5725-2 for the largest and the smallest observation.

    Returns (G_high, G_low, critical)."""
    a = np.asarray(list(x), dtype=float)
    if not np.all(np.isfinite(a)):
        raise ValueError("values must be finite")
    s = a.std(ddof=1) if a.size > 1 else 0.0
    if a.size < 3 or s == 0:
        raise ValueError("Grubbs' test needs at least three non-identical results")
    return float((a.max() - a.mean()) / s), float((a.mean() - a.min()) / s), grubbs_critical(a.size, alpha)


def cochran_critical(k: int, n: int, alpha: float = 0.01) -> float:
    """B.2.1 c), 6.6.2 NOTE - critical value of Cochran's test of ISO 5725-2 for k variances, each from n results."""
    f = stats.f.ppf(1 - alpha / k, n - 1, (k - 1) * (n - 1))
    return float(f / (f + k - 1))


def cochran(variances: Iterable[float], n: int, alpha: float = 0.01):
    """B.2.1 c), 6.6.2 NOTE - Cochran's C = max(s^2) / sum(s^2), the test of ISO 5725-2.

    Returns (C, critical, index of the largest variance)."""
    v = np.asarray(list(variances), dtype=float)
    if not np.all(np.isfinite(v)) or np.any(v < 0):
        raise ValueError("variances must be finite and not negative")
    if v.sum() <= 0:
        raise ValueError("all variances are zero")
    i = int(np.argmax(v))
    return float(v[i] / v.sum()), cochran_critical(v.size, n, alpha), i
