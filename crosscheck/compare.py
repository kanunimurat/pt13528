# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Cross-check of pt13528 against the PHP engine of the LAKSiS platform, and the
effect of the stopping rule of Algorithm A.

The PHP engine is proprietary and is not part of this repository. Its outputs
for the data sets generated below are stored in php_200.json (16 quantities,
200 sets) and php_5000.json (Algorithm A only, 5000 sets). The data sets are
regenerated here from fixed seeds, so the comparison can be repeated without
the PHP code. The PHP engine comes from the same group as this library; the
comparison shows where the two implementations agree, not that they are
independent readings of the standard (see tests/test_external.py for that).
php_200_before_fix.json holds the outputs of the PHP engine before its Q
method merged differences that are equal in exact arithmetic (the library
does so since version 0.1.3, the PHP engine since October 2026);
php_200.json holds the outputs after that correction.

Run from the repository root:  python crosscheck/compare.py
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pt13528 import homogeneity, robust, scores  # noqa: E402

HERE = os.path.dirname(__file__)


def sets_200():
    rng = np.random.default_rng(20261003)
    for c in range(200):
        p = int(rng.integers(6, 41))
        x = rng.normal(rng.uniform(1, 100), rng.uniform(0.1, 5), p)
        k = int(rng.integers(0, max(1, p // 5) + 1))
        if k:
            x[rng.choice(p, k, replace=False)] += rng.normal(0, 25, k)
        if c % 2:
            x = np.round(x, 1)                      # ties
        x = [float(v) for v in x]
        g, m = int(rng.integers(7, 15)), int(rng.integers(2, 5))
        hom = (rng.normal(50, 0.3, (g, 1)) + rng.normal(0, 0.2, (g, m))).tolist()
        w = [float(v) for v in np.abs(rng.normal(0, 1, p)) + 0.05]
        sc = [float(v) for v in (rng.normal(50, 2), 50.0, rng.uniform(0.5, 2), rng.uniform(0.1, 1), rng.uniform(0.05, 0.5))]
        yield x, hom, w, sc


def sets_5000():
    rng = np.random.default_rng(7)
    for c in range(5000):
        p = int(rng.integers(6, 41))
        x = rng.normal(rng.uniform(1, 100), rng.uniform(0.1, 5), p)
        k = int(rng.integers(0, max(1, p // 5) + 1))
        if k:
            x[rng.choice(p, k, replace=False)] += rng.normal(0, 25, k)
        if c % 2:
            x = np.round(x, 1)
        yield [float(v) for v in x]


# php_200.json and php_5000.json are outputs of the PHP engine 1.6.0, which iterates Algorithms A and S
# to convergence like the library. php_5000_engine_1.5.0.json holds the Algorithm A outputs of engine
# 1.5.0, which stopped when the third significant figures of x* and of s* no longer changed (the
# criterion "iso2022" of the library).


def python_200():
    out = []
    for x, hom, w, (xi, xpt, s, u, upt) in sets_200():
        a = robust.algorithm_a(x)
        qh = robust.q_hampel(x)
        h = homogeneity.homogeneity(hom, sigma_pt=s)
        out.append({"median": robust.median(x), "MADe": robust.made(x), "nIQR": robust.niqr(x),
                    "Algorithm A x*": a.location, "Algorithm A s*": a.scale,
                    "Algorithm S": robust.algorithm_s(w, 1).location, "Qn": robust.qn(x),
                    "Q method": float(robust.q_method(x)), "Q/Hampel x*": qh.location,
                    "s_s": h.s_s, "s_w": h.s_w, "expanded criterion": h.expanded_criterion,
                    "z": scores.z_score(xi, xpt, s), "z'": scores.z_prime_score(xi, xpt, s, upt),
                    "zeta": scores.zeta_score(xi, xpt, u, upt), "E_n": scores.en_score(xi, xpt, 2 * u, 2 * upt)})
    return out


def sig(v, n):
    return 0.0 if v == 0 else round(v, n - 1 - int(math.floor(math.log10(abs(v)))))


def rule_statistics(all_x, rule):
    """A stopping rule of Algorithm A against convergence (default tolerance), and after a change of
    unit (inch to millimetre) or of origin (degree Celsius to kelvin) of the same results."""
    third_x = third_s = results = signals = sets_with_signal_change = 0
    rel, iters = [], []
    unit_changed = origin_changed = unit_sig = origin_sig = 0
    unit_worst = origin_worst = 0.0
    for x in all_x:
        x = np.asarray(x)
        a = robust.algorithm_a(x, tol=rule)
        c = robust.algorithm_a(x)
        if c.degenerate:
            continue
        # z scores with x_pt = x* and sigma_pt = s* (8.6) under the two stopping rules
        za = [scores.classify_z(scores.z_score(v, a.location, a.scale)) for v in x]
        zc = [scores.classify_z(scores.z_score(v, c.location, c.scale)) for v in x]
        changed = sum(u != v for u, v in zip(za, zc))
        results += len(x)
        signals += changed
        sets_with_signal_change += changed > 0
        third_x += sig(a.location, 3) != sig(c.location, 3)
        third_s += sig(a.scale, 3) != sig(c.scale, 3)
        rel.append(abs(a.scale - c.scale) / c.scale)
        iters.append((a.iterations, c.iterations))
        for kind, y, back in (("unit", x * 25.4, lambda r: (r.location / 25.4, r.scale / 25.4)),
                              ("origin", x + 273.15, lambda r: (r.location - 273.15, r.scale))):
            loc, sc = back(robust.algorithm_a(y, tol=rule))
            moved = abs(sc - a.scale) > 1e-9 * a.scale
            zb = [scores.classify_z(scores.z_score(v, loc, sc)) for v in x]
            nsig = sum(u != v for u, v in zip(za, zb))
            err = abs(sc - c.scale) / c.scale
            if kind == "unit":
                unit_changed += moved; unit_sig += nsig; unit_worst = max(unit_worst, err)
            else:
                origin_changed += moved; origin_sig += nsig; origin_worst = max(origin_worst, err)
    return {
        "sets": len(rel),
        "against convergence": {
            "x* differs in the third significant figure": int(third_x),
            "s* differs in the third significant figure": int(third_s),
            "relative difference of s*: median, 95th percentile, maximum":
                [float(np.median(rel)), float(np.percentile(rel, 95)), float(max(rel))],
            "median iterations: rule, convergence":
                [float(np.median([i[0] for i in iters])), float(np.median([i[1] for i in iters]))],
            "z signals (acceptable, warning, action) that change: results, of results, sets":
                [int(signals), int(results), int(sets_with_signal_change)],
        },
        "after a change of unit (x 25,4) or of origin (+ 273,15)": {
            "sets in which s* changes: unit, origin": [int(unit_changed), int(origin_changed)],
            "z signals that change: unit, origin": [int(unit_sig), int(origin_sig)],
            "largest relative error of s* against convergence: unit, origin": [float(unit_worst), float(origin_worst)],
        },
    }


def main():
    py = python_200()
    php = json.load(open(os.path.join(HERE, "php_200.json")))
    # even-numbered sets are continuous, odd-numbered sets are rounded to one decimal (ties)
    largest = {k: max(abs(a[k] - b[k]) for a, b in zip(py[0::2], php[0::2])) for k in py[0]}
    largest_ties = {k: max(abs(a[k] - b[k]) for a, b in zip(py[1::2], php[1::2])) for k in py[0]}
    before = json.load(open(os.path.join(HERE, "php_200_before_fix.json")))
    q_rel = [abs(a["Q method"] - b["Q method"]) / a["Q method"] for a, b in zip(py[1::2], before[1::2])]
    q_rel_0 = [abs(a["Q method"] - b["Q method"]) / a["Q method"] for a, b in zip(py[0::2], before[0::2])]
    differing_200 = [i for i, (a, b) in enumerate(zip(py, php)) if abs(a["Algorithm A s*"] - b["Algorithm A s*"]) > 1e-9]
    xs = list(sets_5000())
    php5 = json.load(open(os.path.join(HERE, "php_5000.json")))
    differing_5000 = [i for i, (x, b) in enumerate(zip(xs, php5))
                      if (lambda a: abs(a.location - b[0]) > 1e-9 or abs(a.scale - b[1]) > 1e-9)(robust.algorithm_a(x))]
    old5 = json.load(open(os.path.join(HERE, "php_5000_engine_1.5.0.json")))
    differing_old = [i for i, (x, b) in enumerate(zip(xs, old5))
                     if (lambda a: abs(a.location - b[0]) > 1e-9 or abs(a.scale - b[1]) > 1e-9)(robust.algorithm_a(x, tol="iso2022"))]
    all_x = [s[0] for s in sets_200()] + xs
    q_diff = [r for r in q_rel if r > 1e-9]
    res = {
        "largest absolute difference, Python - PHP, 100 sets without ties": largest,
        "largest absolute difference, Python - PHP, 100 sets with ties": largest_ties,
        "Q method, PHP engine before the correction, 100 sets with ties: sets that differ by more than 1e-9, "
        "median and largest relative difference":
            [int(sum(r > 1e-9 for r in q_rel)), float(np.median(q_rel)), float(max(q_rel))],
        "Q method, PHP engine before the correction: median relative difference in the sets that differ": float(np.median(q_diff)),
        "Q method, PHP engine before the correction, 100 sets without ties: largest relative difference": float(max(q_rel_0)),
        "sets with a different Algorithm A result (convergence)": {"of 200": len(differing_200), "of 5000": len(differing_5000)},
        "sets with a different Algorithm A result, engine 1.5.0 against tol='iso2022', of 5000": len(differing_old),
        "criterion of ISO 13528:2022, third significant figures of x* and s* (iso2022)": rule_statistics(all_x, "iso2022"),
        "criterion quoted from the 2015 edition, third figure of s* and equivalent figure of x* (iso2015)": rule_statistics(all_x, "iso2015"),
    }
    json.dump(res, open(os.path.join(HERE, "result.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
