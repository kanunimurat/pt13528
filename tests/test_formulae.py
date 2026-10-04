# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Checks of formulae that have no worked example in Annex E."""
import math

import numpy as np
import pytest

from pt13528 import assigned_value as av
from pt13528 import homogeneity as hom, outliers, robust, scores


def test_formula_3_and_16_and_17():
    assert av.combine_uncertainty(3, 4) == 5
    assert scores.delta_e_prime(3, 4) == 5
    assert 0.96 < scores.z_reduction_factor(1.0, 0.29) < 1.0          # Formula (18)


def test_classification_rules():
    assert [scores.classify_z(v) for v in (2.0, 2.5, 3.0)] == ["acceptable", "warning", "action"]
    assert scores.classify_z(2.1, action=2.0, warning=None) == "action"
    assert [scores.classify_en(v) for v in (0.99, 1.0, -1.0)] == ["acceptable", "action", "action"]
    assert scores.uncertainty_negligible(0.29, sigma_pt=1) and not scores.uncertainty_negligible(0.3, sigma_pt=1)


def test_en_with_one_laboratory_as_reference():
    assert scores.en_score(10.0, 9.0, 0.6, 0.8) == pytest.approx(1.0)


def test_small_p_estimators():
    assert robust.sd_two_results(1.0, 3.0) == pytest.approx(math.sqrt(2))
    assert robust.mean_abs_dev_sd([1.0, 2.0, 4.0]) == pytest.approx(3.0 / (0.798 * 3))


def test_qn_printed_formula_is_undefined_for_tiny_sets():
    with pytest.raises(ValueError):
        robust.qn([1.0, 2.0, 4.0], h_rule="iso-literal")
    assert robust.qn([1.0, 2.0]) == pytest.approx(2.2191 * 0.3994)      # factor of Amd 1:2026
    x = [1.0, 2.0, 4.0, 7.0, 11.0, 16.0]
    assert robust.qn(x, h_rule="iso-literal") != robust.qn(x)                # 2022 text differs from the amended one


def test_qn_and_q_method_estimate_sigma():
    rng = np.random.default_rng(7)
    x = rng.normal(10, 2, 2000)
    assert robust.qn(x) == pytest.approx(2.0, rel=0.06)
    assert robust.q_method(x) == pytest.approx(2.0, rel=0.06)
    reps = [rng.normal(m, 0.2, 3) for m in rng.normal(10, 2, 300)]
    assert robust.q_method(reps) == pytest.approx(2.0, rel=0.12)


def test_q_method_with_ties_and_fixed_scale_algorithm_a():
    x = [5, 5, 5, 5, 6, 6, 7, 4, 5, 6, 5, 9]
    s = robust.q_method(x)
    assert s > 0
    r = robust.algorithm_a(x, update_scale=False, scale=s)             # C.3.2 b)
    assert r.scale == s and r.converged


def test_homogeneity_general_m_matches_duplicate_formulae():
    rng = np.random.default_rng(3)
    x = rng.normal(5, 0.1, (10, 2))
    h = hom.homogeneity(x, sigma_pt=0.5)
    w = x[:, 0] - x[:, 1]
    s_w = math.sqrt(np.sum(w ** 2) / (2 * 10))                         # B.15
    s_x = x.mean(axis=1).std(ddof=1)                                   # B.14
    assert h.s_w == pytest.approx(s_w)
    assert h.s_s == pytest.approx(math.sqrt(max(0, s_x ** 2 - s_w ** 2 / 2)))  # B.16
    h3 = hom.homogeneity(rng.normal(5, 0.1, (8, 3)), sigma_pt=0.5)
    assert h3.m == 3 and h3.expanded_criterion > h3.criterion


def test_stability_expanded_and_t_test():
    s = hom.stability([10.0, 10.2], [10.5, 10.7], sigma_pt=1.0, u_y1=0.1, u_y2=0.1)
    assert not s.stable and s.stable_expanded
    assert s.expanded_criterion == pytest.approx(0.3 + 2 * math.hypot(0.1, 0.1))        # B.18
    t, df, p, sig = hom.stability_t_test([10.0, 10.1, 9.9], [10.0, 10.2, 9.8])
    assert not sig and 0 < p <= 1
    assert hom.expanded_sigma_pt(3, 4) == 5                                              # B.3


def test_outlier_critical_values_iso_5725_2():
    assert outliers.grubbs_critical(10, 0.05) == pytest.approx(2.290, abs=0.001)
    assert outliers.grubbs_critical(10, 0.01) == pytest.approx(2.482, abs=0.001)
    assert outliers.cochran_critical(10, 2, 0.05) == pytest.approx(0.602, abs=0.001)
    assert outliers.cochran_critical(10, 2, 0.01) == pytest.approx(0.718, abs=0.001)


def test_kernel_bandwidth_and_density_integrates_to_one():
    from pt13528 import graphics
    assert graphics.bandwidth(32, robust_sd=2.0) == pytest.approx(0.9 * 2.0 / 2.0)
    assert graphics.bandwidth(10, sigma_pt=0.25) == pytest.approx(0.1875)
    g, d = graphics.kernel_density([1.0, 2.0, 2.5, 4.0], 0.5, grid=2001, cut=8)
    assert float(np.sum(d) * (g[1] - g[0])) == pytest.approx(1.0, abs=1e-3)
