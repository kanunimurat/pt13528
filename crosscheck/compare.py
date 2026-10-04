# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Cross-check of pt13528 against the PHP engine of the LAKSiS platform, and the
effect of the stopping rule of Algorithm A.

The PHP engine is proprietary and is not part of this repository. Its outputs
for the data sets generated below are stored in php_200.json (16 quantities,
200 sets) and php_5000.json (Algorithm A only, 5000 sets). The data sets are
regenerated here from fixed seeds, so the comparison can be repeated without
the PHP code. The PHP engine comes from the same group as this library; the
comparison shows that the two implementations agree, not that they are
independent readings of the standard (see tests/test_external.py for that).

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


def main():
    py = python_200()
    php = json.load(open(os.path.join(HERE, "php_200.json")))
    largest = {k: max(abs(a[k] - b[k]) for a, b in zip(py, php)) for k in py[0]}
    differing_200 = [i for i, (a, b) in enumerate(zip(py, php)) if abs(a["Algorithm A s*"] - b["Algorithm A s*"]) > 1e-9]
    xs = list(sets_5000())
    py5 = [robust.algorithm_a(x) for x in xs]
    php5 = json.load(open(os.path.join(HERE, "php_5000.json")))
    differing_5000 = [i for i, (a, b) in enumerate(zip(py5, php5)) if abs(a.location - b[0]) > 1e-9 or abs(a.scale - b[1]) > 1e-9]
    all_x = [s[0] for s in sets_200()] + xs
    third_x = third_s = 0
    rel = []
    iters = []
    results = signals = sets_with_signal_change = 0
    for x in all_x:
        a = robust.algorithm_a(x)
        c = robust.algorithm_a(x, tol=1e-12)
        # z scores with x_pt = x* and sigma_pt = s* (8.6) under the two stopping rules
        ca = [scores.classify_z(scores.z_score(v, a.location, a.scale)) for v in x]
        cc = [scores.classify_z(scores.z_score(v, c.location, c.scale)) for v in x]
        changed = sum(u != v for u, v in zip(ca, cc))
        results += len(x)
        signals += changed
        sets_with_signal_change += changed > 0
        third_x += sig(a.location, 3) != sig(c.location, 3)
        third_s += sig(a.scale, 3) != sig(c.scale, 3)
        rel.append(abs(a.scale - c.scale) / c.scale)
        iters.append((a.iterations, c.iterations))
    n = len(all_x)
    res = {
        "largest absolute difference, Python - PHP, 200 sets": largest,
        "sets with a different Algorithm A result": {"of 200": len(differing_200), "of 5000": len(differing_5000)},
        "three-figure rule against convergence": {
            "sets": n,
            "x* differs in the third significant figure": third_x,
            "s* differs in the third significant figure": third_s,
            "relative difference of s*: median, 95th percentile, maximum":
                [float(np.median(rel)), float(np.percentile(rel, 95)), float(max(rel))],
            "median iterations: rule, convergence": [float(np.median([i[0] for i in iters])), float(np.median([i[1] for i in iters]))],
            "z signals (acceptable, warning, action) that change: results, of results, sets":
                [int(signals), int(results), int(sets_with_signal_change)],
        },
    }
    json.dump(res, open(os.path.join(HERE, "result.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
