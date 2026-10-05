# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Input check and default tolerance shared by the modules (no calculation of the standard)."""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np

DEFAULT_TOL = 1e-10                 # relative stopping tolerance of the iterative estimators


def _arr(x: Iterable[float]) -> np.ndarray:
    if isinstance(x, (str, bytes, dict)):
        raise TypeError("a sequence of numbers is required")
    a = np.asarray(list(x), dtype=float)
    if a.ndim != 1 or a.size == 0:
        raise ValueError("a non-empty one-dimensional sequence is required")
    if not np.all(np.isfinite(a)):
        raise ValueError("values must be finite")
    return a


def _finite(*values: float) -> None:
    for v in values:
        if isinstance(v, (str, bytes, bool)) or not math.isfinite(v):
            raise ValueError("results, assigned values, standard deviations and uncertainties must be finite numbers")


def _nonneg(*values: float) -> None:
    _finite(*values)
    if any(v < 0 for v in values):
        raise ValueError("standard deviations and uncertainties must not be negative")
