# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Performance statistics of ISO 13528:2022 Clause 9."""
from __future__ import annotations

import math
from typing import Optional

__all__ = [
    "difference", "percent_difference", "percent_allowed", "delta_e_prime",
    "z_score", "z_prime_score", "zeta_score", "en_score", "z_reduction_factor",
    "classify_z", "classify_en", "classify_d", "uncertainty_negligible",
    "uncertainty_flag",
]


def difference(x: float, x_pt: float) -> float:
    """9.3.1, Formula (11) - D = x - x_pt."""
    return x - x_pt


def percent_difference(x: float, x_pt: float) -> float:
    """9.3.1, Formula (12) - D% = 100 (x - x_pt) / x_pt. Undefined for x_pt = 0."""
    if x_pt == 0:
        raise ZeroDivisionError("Formula (12) cannot be applied when x_pt = 0")
    return 100.0 * (x - x_pt) / x_pt


def percent_allowed(x: float, x_pt: float, delta_e: float) -> float:
    """9.3.6, Formula (13) - PA = (D / delta_E) x 100 %."""
    if delta_e <= 0:
        raise ValueError("delta_E must be positive")
    return 100.0 * (x - x_pt) / delta_e


def delta_e_prime(delta_e: float, big_u_x_pt: float) -> float:
    """9.5.2, Formula (16) - delta_E' = sqrt(delta_E^2 + U^2(x_pt)), U with k = 2."""
    return math.hypot(delta_e, big_u_x_pt)


def z_score(x: float, x_pt: float, sigma_pt: float) -> float:
    """9.4.1, Formula (14)."""
    if sigma_pt <= 0:
        raise ValueError("sigma_pt must be positive")
    return (x - x_pt) / sigma_pt


def z_prime_score(x: float, x_pt: float, sigma_pt: float, u_x_pt: float) -> float:
    """9.5.1, Formula (15)."""
    den = math.hypot(sigma_pt, u_x_pt)
    if den <= 0:
        raise ValueError("sigma_pt and u(x_pt) cannot both be zero")
    return (x - x_pt) / den


def z_reduction_factor(sigma_pt: float, u_x_pt: float) -> float:
    """9.5.4, Formula (17) - constant ratio z'/z."""
    return sigma_pt / math.hypot(sigma_pt, u_x_pt)


def zeta_score(x: float, x_pt: float, u_x: float, u_x_pt: float) -> float:
    """9.6.1, Formula (19) - standard uncertainties."""
    den = math.hypot(u_x, u_x_pt)
    if den <= 0:
        raise ValueError("u(x) and u(x_pt) cannot both be zero")
    return (x - x_pt) / den


def en_score(x: float, x_pt: float, big_u_x: float, big_u_x_pt: float) -> float:
    """9.7.1, Formula (20) - expanded uncertainties.

    The standard defines E_n against an assigned value determined in a
    reference laboratory. When one laboratory of a pair is treated as the
    reference (10.7.1), pass its result and expanded uncertainty as ``x_pt``
    and ``big_u_x_pt``; the library has no separate laboratory-to-laboratory
    scoring mode.
    """
    den = math.hypot(big_u_x, big_u_x_pt)
    if den <= 0:
        raise ValueError("U(x) and U(x_pt) cannot both be zero")
    return (x - x_pt) / den


def classify_z(score: Optional[float], action: float = 3.0, warning: Optional[float] = 2.0) -> str:
    """9.4.2 - 'acceptable', 'warning' or 'action' (also used for z' and zeta).

    Pass ``warning=None, action=2.0`` for the two-band rule of 9.4.2 NOTE 1.
    """
    if score is None:
        return "not scored"
    a = abs(score)
    if warning is None:
        return "acceptable" if a <= action else "action"
    if a <= warning:
        return "acceptable"
    return "warning" if a < action else "action"


def classify_en(score: Optional[float]) -> str:
    """9.7.2 - |E_n| >= 1,0 is a signal; -1,0 < E_n < 1,0 is not."""
    if score is None:
        return "not scored"
    return "acceptable" if abs(score) < 1.0 else "action"


def classify_d(d: float, delta_e: float) -> str:
    """9.3.2 - acceptable when -delta_E < D < delta_E (same rule for D% and PA)."""
    return "acceptable" if abs(d) < delta_e else "action"


def uncertainty_negligible(u_x_pt: float, sigma_pt: Optional[float] = None,
                           delta_e: Optional[float] = None) -> bool:
    """9.2.1, Formula (10) - u(x_pt) < 0,3 sigma_pt or u(x_pt) < 0,1 delta_E."""
    if sigma_pt is None and delta_e is None:
        raise ValueError("give sigma_pt or delta_E")
    limit = 0.3 * sigma_pt if sigma_pt is not None else 0.1 * delta_e
    return u_x_pt < limit


def uncertainty_flag(u_x: float, u_min: float, u_max: float) -> str:
    """9.8.3 to 9.8.5 - informative screening of a reported standard uncertainty.

    u_min is typically u(x_pt) (9.8.3) and u_max 1,5 s* (9.8.4). Returns 'a'
    (u_min <= u <= u_max), 'b' (u < u_min) or 'c' (u > u_max); the letters
    follow Table E.6.
    """
    if u_x < u_min:
        return "b"
    if u_x > u_max:
        return "c"
    return "a"
