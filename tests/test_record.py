# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""The result record must contain exactly what the single functions return."""
import math

import pytest

import pt13528
from pt13528 import assigned_value, scores

X = [0.227, 0.230, 0.243, 0.255, 0.264, 0.270, 0.274, 0.281, 0.289, 0.311]


def test_consensus_record_equals_single_calls():
    r = pt13528.round_record(X)
    av = assigned_value.consensus(X, "algorithm_a")
    assert (r.x_pt, r.u_x_pt, r.sigma_pt, r.p) == (av.x_pt, av.u_x_pt, av.scale, 10)
    # with sigma_pt = s*, u = 1,25 s*/sqrt(p) < 0,3 s* only when p >= 18
    assert not r.uncertainty_negligible and r.statistic == "z_prime"
    assert r.clauses["statistic"].startswith("9.5.1")
    for row, x in zip(r.participants, X):
        assert row.score == scores.z_prime_score(x, av.x_pt, av.scale, av.u_x_pt)
        assert row.signal == scores.classify_z(row.score)
    assert sum(r.counts.values()) == 10


def test_negligible_uncertainty_switches_to_z_at_18_results():
    for p, stat in ((17, "z_prime"), (18, "z")):
        x = [10 + 0.1 * math.sin(7 * i) + 0.01 * i for i in range(p)]
        assert pt13528.round_record(x).statistic == stat


def test_independent_assigned_value_and_zeta():
    r = pt13528.round_record([9.6, 10.1, 10.9, 12.2], x_pt=10.0, u_x_pt=0.05, sigma_pt=0.5,
                             u_x=[0.2, None, 0.3, 0.1], labels=list("ABCD"))
    assert r.method == "given" and r.statistic == "z" and r.criterion_limit == pytest.approx(0.15)
    assert [q.signal for q in r.participants] == ["acceptable", "acceptable", "acceptable", "action"]
    assert r.counts == {"acceptable": 3, "warning": 0, "action": 1}
    assert r.participants[1].zeta is None
    assert r.participants[3].zeta == pytest.approx(scores.zeta_score(12.2, 10.0, 0.1, 0.05))
    assert r.rows()[0]["label"] == "A" and r.summary()["n_action"] == 1


def test_statistic_can_be_fixed_and_bad_input_is_refused():
    assert pt13528.round_record(X, statistic="z").statistic == "z"
    assert pt13528.round_record(X, statistic="z").uncertainty_negligible is False
    assert "warning" not in pt13528.round_record(X, action=2.0, warning=None).counts
    with pytest.raises(ValueError):
        pt13528.round_record(X, x_pt=0.26)                     # no u(x_pt)
    with pytest.raises(ValueError):
        pt13528.round_record(X, x_pt=0.26, u_x_pt=0.005)       # no sigma_pt
    with pytest.raises(ValueError):
        pt13528.round_record([1.0, float("nan")])
