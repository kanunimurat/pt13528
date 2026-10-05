# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""The counts quoted in the article and in docs/coverage.md come from this test."""
import pytest

import printed_values as P


def test_all_listed_printed_values_are_reproduced_to_half_a_unit():
    rows = P.reproduced()
    assert len(rows) == 255
    assert sum(r[0] != "Table B.1" for r in rows) == 227          # Annex E
    worst = max(rows, key=lambda r: abs(P.deviation(r)))
    assert abs(P.deviation(worst)) <= 0.5 + 1e-9, worst


def test_inconsistent_items():
    items = P.inconsistent()
    assert len(items) == 2
    assert [i[1] for i in items].count("not reproduced") == 1
    rule, full = items[0][2]
    assert round(rule, 2) == round(full, 2) == 23.96 and items[0][3] == 23.95   # neither rule gives 23,95
    assert items[1][4] == pytest.approx(-37, abs=1)               # Table E.10: Algorithm A is 0,37 lower


def test_flags_of_table_e6_do_not_identify_the_limits():
    with_u, with_U, (b_max, a_min, a_max, c_min) = P.e6_flags()
    assert (with_u, with_U) == (9, 21)                            # limits of 9.8.3 and 9.8.4 as suggested
    assert b_max < a_min <= a_max < c_min                         # so a range of limits for u_lab gives 21 of 21
    assert (round(b_max, 4), round(a_min, 4), round(a_max, 4), round(c_min, 3)) == (0.0020, 0.0025, 0.0065, 0.015)


def test_notes():
    n = P.notes()
    printed, rule, full = n["E.1 third column s*: printed, three-figure rule, convergence"]
    assert round(full, 2) == printed and round(rule, 2) != printed
    printed, rule, full = n["E.1 first column s*: printed, three-figure rule, convergence"]
    assert round(rule, 2) == printed and round(full, 2) != printed
    printed, niqr, made = n["E.3 Table E.5 u(x_pt) of the median row: printed, with nIQR, with MADe"]
    assert round(niqr, 4) == printed and round(made, 4) == 0.0083
    printed, plain, adjusted = n["E.8 coefficient of determination: printed, plain, adjusted"]
    assert round(adjusted, 2) == printed and round(plain, 2) == 0.83
