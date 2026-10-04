# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Ledger of the values printed in ISO 13528:2022 that the library is compared with.

``reproduced()`` lists every printed value that the library reproduces to
within half a unit of its last printed digit, as (source, label, printed,
computed, decimals). ``inconsistent()`` lists the printed items that do not
follow from the accompanying text or from rounding. Both are used by the
tests and by the verification figure of the article, so that the counts
quoted there are produced by this file and by nothing else.

Run ``python tests/printed_values.py`` for a summary.
"""
import numpy as np

from pt13528 import assigned_value as av
from pt13528 import homogeneity as hm
from pt13528 import robust, scores
from pt13528 import sigma_pt as sp

import annex_e_data as E


def reproduced():
    rows = []

    def add(src, label, printed, computed, d):
        rows.append((src, label, printed, float(computed), d))

    for k in ("ignored", "deleted"):
        dat, xs, ss = E.E1[k]
        r = robust.algorithm_a(dat)
        add("E.1", f"x* ({k})", xs, r.location, 2)
        add("E.1", f"s* ({k})", ss, r.scale, 2)
    h = hm.homogeneity(E.E2_HOMOGENEITY)
    for name, pr, c in (("mean", 0.18715, h.mean), ("s_x", 0.00398, h.s_x), ("s_w", 0.00556, h.s_w), ("s_s", 0.00060, h.s_s)):
        add("E.2", name, pr, c, 5)
    sig = 0.15 * h.mean
    add("E.2", "sigma_pt", 0.02807, sig, 5)
    add("E.2", "0,3 sigma_pt", 0.00842, hm.homogeneity(E.E2_HOMOGENEITY, sigma_pt=sig).criterion, 5)
    flat = [v for p_ in E.E2_HOMOGENEITY for v in p_]
    st = hm.stability(flat, [v for p_ in E.E2_STABILITY for v in p_], sigma_pt=sig)
    add("E.2", "stability mean", 0.19375, st.mean_2, 5)
    add("E.2", "stability difference", 0.00660, st.difference, 5)
    med = av.consensus(E.E3, "median")
    add("E.3", "median", 0.2620, med.x_pt, 4)
    add("E.3", "nIQR", 0.0402, robust.niqr(E.E3), 4)
    add("E.3", "MADe", 0.0386, robust.made(E.E3), 4)
    add("E.3", "u(median), nIQR", 0.0086, med.u_x_pt, 4)
    for m_, pr in (("algorithm_a", (0.2570, 0.0395, 0.0085)), ("q_hampel", (0.2600, 0.0426, 0.0091)), ("mean", (0.2512, 0.0672, 0.0115))):
        a_ = av.consensus(E.E3, m_)
        for name, q, c in zip(("location", "scale", "u"), pr, (a_.x_pt, a_.scale, a_.u_x_pt)):
            add("E.3", f"{m_} {name}", q, c, 4)
    u_pt = E.E4_BIG_U / 2
    delta_e = 3 * E.E4_SIGMA
    for code, x_, big_u, k_, _f, d_pct, pa, z_, zp, zeta, en in E.E4:
        add("E.4", f"{code} D%", d_pct, scores.percent_difference(x_, E.E4_XPT), 1)
        add("E.4", f"{code} PA", pa, scores.percent_allowed(x_, E.E4_XPT, delta_e), 1)
        add("E.4", f"{code} z", z_, scores.z_score(x_, E.E4_XPT, E.E4_SIGMA), 2)
        add("E.4", f"{code} z'", zp, scores.z_prime_score(x_, E.E4_XPT, E.E4_SIGMA, u_pt), 2)
        add("E.4", f"{code} zeta", zeta, scores.zeta_score(x_, E.E4_XPT, big_u / k_, u_pt), 2)
        add("E.4", f"{code} En", en, scores.en_score(x_, E.E4_XPT, big_u, E.E4_BIG_U), 2)
    c5 = av.from_crm_comparison(E.E5_XCRM, E.E5_UCRM, E.E5_D)
    add("E.5", "x_pt", 23.35, c5.x_pt, 2)
    add("E.5", "u(x_pt)", 0.35, c5.u_x_pt, 2)
    add("E.5", "u_d", 0.24, c5.scale, 2)
    add("E.6", "kernel mode", 3.79, av.kernel_mode(E.E6, 0.75 * 0.25), 2)
    vals = [r[1] for r in E.E4]
    r7 = robust.algorithm_a(vals)
    u7 = av.u_robust(r7.scale, len(vals))
    c7 = av.compare_with_reference(E.E4_XPT, u_pt, r7.location, u7)
    for name, pr, c, d in (("x*", 0.03161, r7.location, 5), ("s*", 0.0164, r7.scale, 4), ("u(x*)", 0.0045, u7, 4),
                           ("u_diff", 0.0061, c7.u_diff, 4), ("x_diff", 0.012, c7.x_diff, 3)):
        add("E.7", name, pr, c, d)
    add("E.9", "sigma_pt, c = 1,195 mg/kg", 0.186, sp.horwitz(1.195e-6) * 1e6, 3)
    add("E.9", "sigma_pt, c = 2,565 mg/kg", 0.356, sp.horwitz(2.565e-6) * 1e6, 3)
    add("E.10", "sigma_pt", 20.9, sp.from_precision(23.2, 14.3, 2), 1)
    for name, data, zs, mean, sd in (("A", E.E12_A, E.E12_ZA, 11.54, 3.29), ("B", E.E12_B, E.E12_ZB, 7.66, 2.90)):
        a = np.array(data)
        add("E.12", f"allergen {name} average", mean, a.mean(), 2)
        add("E.12", f"allergen {name} standard deviation", sd, a.std(ddof=1), 2)
        for i, (zc, zpr) in enumerate(zip((a - a.mean()) / a.std(ddof=1), zs)):
            add("E.12", f"allergen {name} z {i + 1}", zpr, zc, 3)
    add("E.12", "correlation", 0.706, np.corrcoef(E.E12_A, E.E12_B)[0, 1], 3)
    add("E.13", "x* of averages", 1.57, robust.algorithm_a(E.E13_AVG).location, 2)
    add("E.13", "w* of standard deviations", 0.34, robust.algorithm_s(E.E13_SD, nu=3).location, 2)
    for g_ in sorted(E.TABLE_B1):
        f1, f2 = hm.expanded_criterion_factors(g_)
        add("Table B.1", f"F1, g = {g_}", E.TABLE_B1[g_][0], f1, 2)
        add("Table B.1", f"F2, g = {g_}", E.TABLE_B1[g_][1], f2, 2)
    return rows


def deviation(row):
    """Computed minus printed, in units of the last printed digit."""
    _src, _label, printed, computed, d = row
    return (computed - printed) * 10 ** d


def inconsistent():
    """Printed items that do not follow from the text or from rounding (after Amd 1:2026).

    Each entry: (item, kind, what the text gives, what is printed, deviation in last-digit units or None).
    """
    dat, xs, ss = E.E1["half"]
    full = robust.algorithm_a(dat, tol=1e-12)
    fit = sp.fit_previous_rounds(E.E8_AV, E.E8_SD)
    a12 = robust.algorithm_a(E.E12_A)
    return [
        ("E.1, Table E.1, third column, x*", "last digit", round(full.location, 4), xs, (full.location - xs) * 100),
        ("E.8, coefficient of determination", "last digit", round(fit.r_squared, 4), 0.82, (fit.r_squared - 0.82) * 100),
        ("E.12, Table E.10: text names Algorithm A, table uses the arithmetic mean and SD", "text and table",
         round(a12.location, 2), 11.54, (a12.location - 11.54) * 100),
        ("E.3, Table E.5: row labelled with nIQR and MADe, printed u follows nIQR", "text and table",
         round(av.consensus(E.E3, "median", median_scale="made").u_x_pt, 4), 0.0086, None),
        ("E.4, Table E.6: flags do not follow the limits of 9.8", "text and table", None, None, None),
    ]


if __name__ == "__main__":
    rows = reproduced()
    by = {}
    for r in rows:
        by[r[0]] = by.get(r[0], 0) + 1
    print(len(rows), "printed values reproduced; largest deviation",
          round(max(abs(deviation(r)) for r in rows), 3), "units of the last digit")
    print(by)
    for item in inconsistent():
        print(item)
