# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""The counts quoted in the article and in docs/coverage.md come from this test."""
import pytest

import printed_values as P


def test_all_listed_printed_values_are_reproduced_to_half_a_unit():
    rows = P.reproduced()
    assert len(rows) == 256
    assert sum(r[0] != "Table B.1" for r in rows) == 228          # Annex E
    worst = max(rows, key=lambda r: abs(P.deviation(r)))
    assert abs(P.deviation(worst)) <= 0.5 + 1e-9, worst


def test_inconsistent_items():
    items = P.inconsistent()
    assert len(items) == 5
    last_digit = [i for i in items if i[1] == "last digit"]
    assert len(last_digit) == 2
    for _item, _kind, _computed, _printed, dev in last_digit:
        assert 0.5 < dev < 1.0                                    # printed value is the truncated one
    assert items[2][4] == pytest.approx(-37, abs=1)               # Table E.10: Algorithm A is 0,37 lower
