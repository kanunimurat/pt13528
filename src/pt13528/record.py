# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Result record of one measurand in one round.

The library does not write reports. This module collects, in one object, the
quantities that the report of a round has to state for a measurand (assigned
value and how it was obtained, its standard uncertainty, the standard
deviation for proficiency assessment and its source, the performance
statistic and its limits, and the score of every participant), each with the
clause of ISO 13528 it comes from. Layout, wording and file format are left
to the caller.
"""
from __future__ import annotations

from typing import Iterable, NamedTuple, Optional, Sequence

import numpy as np

from . import assigned_value, scores

__all__ = ["ParticipantRecord", "RoundRecord", "round_record"]

_METHOD_CLAUSE = {
    "algorithm_a": "7.7, C.3.1",
    "median": "7.7, C.2",
    "q_hampel": "7.7, C.5.4",
    "mean": "7.7",
    "given": "7.3 to 7.6",
}


class ParticipantRecord(NamedTuple):
    label: str
    x: float
    difference: float
    score: float
    signal: str
    u_x: Optional[float] = None
    zeta: Optional[float] = None
    zeta_signal: Optional[str] = None


class RoundRecord(NamedTuple):
    x_pt: float
    u_x_pt: float
    method: str
    sigma_pt: float
    sigma_pt_source: str
    p: int
    criterion_limit: float
    uncertainty_negligible: bool
    statistic: str
    warning: Optional[float]
    action: float
    participants: tuple
    counts: dict
    clauses: dict

    def summary(self) -> dict:
        """Round-level quantities as a flat dictionary (one row of a summary table)."""
        d = self._asdict()
        d.pop("participants")
        d.pop("clauses")
        counts = d.pop("counts")
        d.update({"n_" + k.replace(" ", "_"): v for k, v in counts.items()})
        return d

    def rows(self) -> list:
        """One dictionary per participant (rows of a results table)."""
        return [r._asdict() for r in self.participants]


def round_record(x: Iterable[float], *, method: str = "algorithm_a",
                 x_pt: Optional[float] = None, u_x_pt: Optional[float] = None,
                 sigma_pt: Optional[float] = None, u_x: Optional[Sequence[Optional[float]]] = None,
                 labels: Optional[Sequence[str]] = None, statistic: str = "auto",
                 action: float = 3.0, warning: Optional[float] = 2.0) -> RoundRecord:
    """Assemble the record of one measurand from participant results.

    Assigned value (Clause 7): the consensus of ``x`` by ``method`` (see
    :func:`assigned_value.consensus`), or ``x_pt`` with its standard
    uncertainty ``u_x_pt`` when it was set independently of the participants.

    Standard deviation for proficiency assessment (Clause 8): ``sigma_pt``
    when given, otherwise the robust standard deviation of the participant
    results (8.6), which requires a consensus method.

    Statistic (Clause 9): with ``statistic="auto"`` the criterion of 9.2.1,
    Formula (10), is evaluated and z is used when u(x_pt) is negligible,
    z' (9.5) otherwise. ``"z"`` or ``"z_prime"`` fixes the statistic; the
    outcome of the criterion is recorded either way. When standard
    uncertainties ``u_x`` are given, zeta (9.6) is added for every
    participant that reported one (use ``None`` for those that did not).

    ``action`` and ``warning`` are the limits of 9.4.2. The choice of method,
    of sigma_pt and of the limits remains with the provider; the function
    records the choices next to the numbers so that they can be reported.
    """
    a = np.asarray(list(x), dtype=float)
    p = int(a.size)
    if p < 1 or not np.all(np.isfinite(a)):
        raise ValueError("x must contain at least one result and only finite numbers")
    if labels is None:
        labels = [str(i + 1) for i in range(p)]
    if len(labels) != p:
        raise ValueError("labels and x differ in length")
    if u_x is not None and len(u_x) != p:
        raise ValueError("u_x and x differ in length")
    if statistic not in ("auto", "z", "z_prime"):
        raise ValueError("statistic is 'auto', 'z' or 'z_prime'")

    if x_pt is None:
        if u_x_pt is not None:
            raise ValueError("u_x_pt is given without x_pt")
        av = assigned_value.consensus(a, method)
        x_pt, u_x_pt, scale = av.x_pt, av.u_x_pt, av.scale
    else:
        if u_x_pt is None:
            raise ValueError("an assigned value needs its standard uncertainty u_x_pt (7.2)")
        method, scale = "given", None

    if sigma_pt is None:
        if scale is None:
            raise ValueError("sigma_pt is required when x_pt is given")
        sigma_pt, source = float(scale), "participant results of this round (8.6)"
    else:
        source = "set by the provider (8.2 to 8.5)"
    if sigma_pt <= 0:
        raise ValueError("sigma_pt must be positive")

    negligible = scores.uncertainty_negligible(u_x_pt, sigma_pt=sigma_pt)
    if statistic == "auto":
        statistic = "z" if negligible else "z_prime"

    rows = []
    for i in range(p):
        xi = float(a[i])
        if statistic == "z":
            s = scores.z_score(xi, x_pt, sigma_pt)
        else:
            s = scores.z_prime_score(xi, x_pt, sigma_pt, u_x_pt)
        ui = None if u_x is None or u_x[i] is None else float(u_x[i])
        zeta = None if ui is None else scores.zeta_score(xi, x_pt, ui, u_x_pt)
        rows.append(ParticipantRecord(
            str(labels[i]), xi, scores.difference(xi, x_pt), s,
            scores.classify_z(s, action, warning), ui, zeta,
            None if zeta is None else scores.classify_z(zeta, action, warning),
        ))

    counts = {k: sum(r.signal == k for r in rows) for k in ("acceptable", "warning", "action")}
    if warning is None:
        counts.pop("warning")
    clauses = {
        "x_pt": _METHOD_CLAUSE.get(method, "7"),
        "u_x_pt": "7.7.7, Formula (6)" if method in ("algorithm_a", "median", "q_hampel") else "7.2",
        "sigma_pt": "8.6" if source.endswith("(8.6)") else "8.2 to 8.5",
        "uncertainty_negligible": "9.2.1, Formula (10)",
        "statistic": "9.4.1, Formula (14)" if statistic == "z" else "9.5.1, Formula (15)",
        "signal": "9.4.2",
        "zeta": "9.6.1, Formula (19)",
    }
    return RoundRecord(float(x_pt), float(u_x_pt), method, float(sigma_pt), source, p,
                       0.3 * float(sigma_pt), bool(negligible), statistic, warning, float(action),
                       tuple(rows), counts, clauses)
