# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""One real round, recomputed from the values of its formal report.

Point load strength index, 2026, three accredited participants (anonymous
codes), consensus by the median with the small-sample estimators of D.1.4.2.
The report was produced with the PHP engine of the LAKSiS platform; the
numbers below are the 14 values it prints.
"""
import pytest

from pt13528 import assigned_value, homogeneity, robust, scores

MEANS = {"C": 1.5310, "H": 1.4030, "U": 1.6300}
HOMOGENEITY = [(1.5220, 1.4640), (1.4550, 1.4940), (1.4620, 1.4950), (1.4830, 1.4800), (1.5110, 1.4610),
               (1.4800, 1.5040), (1.4500, 1.4650), (1.4710, 1.4520), (1.4910, 1.5040), (1.4720, 1.4830)]


def test_reported_values():
    x = list(MEANS.values())
    av = assigned_value.consensus(x, "median", median_scale="made")
    sigma = robust.mean_abs_dev_sd(x)
    assert av.x_pt == pytest.approx(1.5310, abs=5e-5)
    assert av.u_x_pt == pytest.approx(0.1060, abs=5e-5)
    assert sigma == pytest.approx(0.0948, abs=5e-5)
    assert not scores.uncertainty_negligible(av.u_x_pt, sigma_pt=sigma)        # z' is the statistic to use
    for code, z, zp in (("C", 0.00, 0.00), ("H", -1.35, -0.90), ("U", 1.04, 0.70)):
        assert scores.z_score(MEANS[code], av.x_pt, sigma) == pytest.approx(z, abs=5e-3)
        assert scores.z_prime_score(MEANS[code], av.x_pt, sigma, av.u_x_pt) == pytest.approx(zp, abs=5e-3)
    h = homogeneity.homogeneity(HOMOGENEITY, sigma_pt=sigma)
    assert h.s_w == pytest.approx(0.0223, abs=5e-5)
    assert h.s_s == pytest.approx(0.0, abs=5e-5)
    assert h.criterion == pytest.approx(0.0284, abs=5e-5)
    assert h.f_statistic == pytest.approx(0.69, abs=5e-3)
    assert h.f_critical == pytest.approx(3.02, abs=5e-3)
