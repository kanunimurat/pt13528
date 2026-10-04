# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Standard deviation for proficiency assessment, ISO 13528:2022 Clause 8."""
from __future__ import annotations

import math
from typing import Iterable, NamedTuple, Optional

import numpy as np

__all__ = ["horwitz", "from_precision", "LinearFit", "fit_previous_rounds", "limit_sigma"]


def horwitz(c: float) -> float:
    """8.4, Formula (8) - Horwitz model as modified by Thompson; c is a mass fraction."""
    if not 0 <= c <= 1:
        raise ValueError("c is a mass fraction, 0 <= c <= 1")
    if c < 1.2e-7:
        return 0.22 * c
    if c <= 0.138:
        return 0.02 * c ** 0.8495
    return 0.01 * math.sqrt(c)


def from_precision(sigma_R: float, sigma_r: float, m: int) -> float:
    """8.5.1, Formula (9) - sigma_pt = sqrt(sigma_R^2 - sigma_r^2 (1 - 1/m))."""
    if m < 1:
        raise ValueError("m must be at least 1")
    v = sigma_R ** 2 - sigma_r ** 2 * (1.0 - 1.0 / m)
    if v < 0:
        raise ValueError("sigma_r is inconsistent with sigma_R")
    return math.sqrt(v)


class LinearFit(NamedTuple):
    slope: float
    intercept: float
    r_squared: float

    def predict(self, x: float) -> float:
        return self.intercept + self.slope * x


def fit_previous_rounds(assigned_values: Iterable[float], sds: Iterable[float]) -> LinearFit:
    """8.3.2 - least-squares line of (robust) standard deviation on assigned value (see E.8)."""
    x = np.asarray(list(assigned_values), dtype=float)
    y = np.asarray(list(sds), dtype=float)
    if x.size != y.size or x.size < 3:
        raise ValueError("at least three previous rounds are required")
    slope, intercept = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    return LinearFit(float(slope), float(intercept), float(r * r))


def limit_sigma(sigma: float, lower: Optional[float] = None, upper: Optional[float] = None) -> float:
    """8.6.2.1 and 8.6.2.2 - floor and ceiling on a sigma_pt derived from participant results."""
    if lower is not None:
        sigma = max(sigma, lower)
    if upper is not None:
        sigma = min(sigma, upper)
    return sigma
