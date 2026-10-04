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
    assert len(items) == 4
    assert [i[1] for i in items].count("not reproduced") == 1
    rule, full = items[0][2]
    assert round(rule, 2) == round(full, 2) == 23.96 and items[0][3] == 23.95   # neither rule gives 23,95
    assert items[1][4] == pytest.approx(-37, abs=1)               # Table E.10: Algorithm A is 0,37 lower
    assert items[2][4] == pytest.approx(-3, abs=1)                # Table E.5: MADe gives 0,0083


def test_notes():
    n = P.notes()
    printed, rule, full = n["E.1 third column s*: printed, three-figure rule, convergence"]
    assert round(full, 2) == printed and round(rule, 2) != printed
    printed, rule, full = n["E.1 first column s*: printed, three-figure rule, convergence"]
    assert round(rule, 2) == printed and round(full, 2) != printed
    printed, plain, adjusted = n["E.8 coefficient of determination: printed, plain, adjusted"]
    assert round(adjusted, 2) == printed and round(plain, 2) == 0.83
