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


def test_simulated_round_of_twenty_against_the_evaluate_function_of_the_php_engine():
    """A simulated round of 20 participants with three outlying results, evaluated end to end by
    Evaluator::evaluate of the PHP engine 1.6.0 (the function that the LAKSiS platform calls for a
    round; consensus by Algorithm A, sigma_pt from the same results) and by round_record. The stored
    output is crosscheck/php_evaluate_round.json. The engine comes from the same group, so this is a
    check of the whole path on a round of realistic size and not an independent verification."""
    import json
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    data = json.load(open(os.path.join(here, "..", "crosscheck", "php_evaluate_round.json")))
    parts, php = data["input"]["participants"], data["php"]
    x = [q["value"] for q in parts]
    u = [q["uncertainty"] / q["coverage_factor"] for q in parts]
    rec = pt13528.round_record(x, method="algorithm_a", u_x=u, labels=[q["participant_id"] for q in parts])
    assert php["p"] == rec.p == 20 and php["algo_a_iterations"] > 6            # the iteration is exercised
    assert rec.x_pt == pytest.approx(php["x_pt"], rel=1e-12)
    assert rec.u_x_pt == pytest.approx(php["u_x_pt"], rel=1e-12)
    assert rec.sigma_pt == pytest.approx(php["sigma_pt"], rel=1e-12)
    assert rec.uncertainty_negligible is php["uncertainty_negligible"] is True and rec.statistic == "z"
    names = {"acceptable": "satisfactory", "warning": "questionable", "action": "unsatisfactory"}
    for r, q in zip(rec.participants, php["results"]):
        assert r.label == q["participant_id"]
        assert r.score == pytest.approx(q["z"], abs=1e-10)
        assert r.zeta == pytest.approx(q["zeta"], abs=1e-10)
        assert names[r.signal] == q["classification"] and names[r.zeta_signal] == q["zeta_class"]
        assert scores.z_prime_score(r.x, rec.x_pt, rec.sigma_pt, rec.u_x_pt) == pytest.approx(q["z_prime"], abs=1e-10)
        assert scores.en_score(r.x, rec.x_pt, 2 * r.u_x, 2 * rec.u_x_pt) == pytest.approx(q["en"], abs=1e-10)
    assert {names[k]: v for k, v in rec.counts.items() if k in names} == {k: php["distribution"][k] for k in names.values()}
