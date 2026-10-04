# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Comparison with R packages that the authors of pt13528 did not write.

    python r_compare.py sets      writes r_sets.csv (input of r_compare.R)
    Rscript r_compare.R           writes r_reference.csv (needs metRology, MASS, robustbase)
    python r_compare.py           compares and prints the largest differences

r_reference.csv is stored in the repository, so that tests/test_external.py runs
without R. It was produced with R 4.3.3, metRology 0.9-29-2 (algA, algS), MASS
7.3-60.0.1 (hubers) and robustbase 0.99-2 (Qn).
"""
import csv
import json
import math
import os
import sys

import numpy as np
from scipy.stats import chi2, norm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)
from pt13528 import robust   # noqa: E402
import compare               # noqa: E402


def sets():
    """200 sets of results (kind "x", the sets of compare.py) and 200 sets of standard deviations
    (kind "w", 20 for each nu = 1..10, some of them inflated)."""
    out = [("x", 0, s[0]) for s in compare.sets_200()]
    rng = np.random.default_rng(13528)
    for nu in range(1, 11):
        for _ in range(20):
            p = int(rng.integers(8, 31))
            w = rng.uniform(0.05, 5) * np.sqrt(rng.chisquare(nu, p) / nu)
            k = int(rng.integers(0, max(1, p // 6) + 1))
            if k:
                w[rng.choice(p, k, replace=False)] *= rng.uniform(2, 6, k)
            out.append(("w", nu, [float(v) for v in w]))
    return out


def read_sets():
    """The stored input of the R script (r_sets.csv), so that the comparison does not depend on the
    random number generator of the installed NumPy."""
    out = []
    with open(os.path.join(HERE, "r_sets.csv")) as f:
        for line in f:
            _i, kind, nu, v = line.rstrip("\n").split(";")
            out.append((kind, int(nu), [float(t) for t in v.split(",")]))
    return out


def exact_factors():
    """The factors that the standard prints rounded: Algorithm A (1,134) and Table C.1."""
    c = 1.5
    theta = 2 * norm.cdf(c) - 1
    alg_a = 1 / math.sqrt(theta + (1 - theta) * c * c - 2 * c * norm.pdf(c))
    alg_s = {}
    for nu in range(1, 11):
        eta = math.sqrt(chi2.ppf(0.9, nu) / nu)
        alg_s[nu] = (eta, 1 / math.sqrt(chi2.cdf(nu * eta * eta, nu + 2) + 0.1 * eta * eta))
    return alg_a, alg_s


def read_reference():
    with open(os.path.join(HERE, "r_reference.csv"), newline="") as f:
        return [{k: (float(v) if v not in ("", "NA") else None) for k, v in row.items()} for row in csv.DictReader(f)]


def main(write=True):
    if write and sys.argv[1:] == ["sets"]:
        with open(os.path.join(HERE, "r_sets.csv"), "w", newline="") as f:
            for i, (kind, nu, v) in enumerate(sets()):
                f.write(f"{i};{kind};{nu};" + ",".join(repr(t) for t in v) + "\n")
        return
    ref = read_reference()
    alg_a, alg_s = exact_factors()
    rel = lambda a, b: abs(a - b) / abs(b)
    d = {"Algorithm A s*, printed factor 1,134, against metRology algA": [],
         "Algorithm A x*, printed factor, against metRology algA (in units of s*)": [],
         "Algorithm A s*, unrounded factor, against metRology algA": [],
         "Algorithm A s*, unrounded factor, against MASS hubers": [],
         "Algorithm S, printed Table C.1, against metRology algS": [],
         "Algorithm S, unrounded factors, against metRology algS": [],
         "Qn against robustbase Qn": [],
         "metRology algA with its default stopping (tol 1.2e-4, 25 iterations) against its converged result": []}
    for (kind, nu, v), r in zip(read_sets(), ref):
        if kind == "x":
            a = robust.algorithm_a(v, tol=1e-13, max_iter=5000)
            if r["algA_s"] is not None:
                d["Algorithm A s*, printed factor 1,134, against metRology algA"].append(rel(a.scale, r["algA_s"]))
                d["Algorithm A x*, printed factor, against metRology algA (in units of s*)"].append(
                    abs(a.location - r["algA_mu"]) / r["algA_s"])
            saved = robust.ALG_A_FACTOR
            robust.ALG_A_FACTOR = alg_a
            try:
                e = robust.algorithm_a(v, tol=1e-13, max_iter=5000)
            finally:
                robust.ALG_A_FACTOR = saved
            if r["algA_s"] is not None:
                d["Algorithm A s*, unrounded factor, against metRology algA"].append(rel(e.scale, r["algA_s"]))
            if r["hubers_s"] is not None:
                d["Algorithm A s*, unrounded factor, against MASS hubers"].append(rel(e.scale, r["hubers_s"]))
            d["Qn against robustbase Qn"].append(rel(robust.qn(v), r["Qn"]))
            d["metRology algA with its default stopping (tol 1.2e-4, 25 iterations) against its converged result"].append(
                rel(r["algA_default_s"], r["algA_s"]))
        else:
            d["Algorithm S, printed Table C.1, against metRology algS"].append(
                rel(robust.algorithm_s(v, nu, tol=1e-13, max_iter=5000).scale, r["algS"]))
            saved = robust._ALG_S[nu]
            robust._ALG_S[nu] = alg_s[nu]
            try:
                d["Algorithm S, unrounded factors, against metRology algS"].append(
                    rel(robust.algorithm_s(v, nu, tol=1e-13, max_iter=5000).scale, r["algS"]))
            finally:
                robust._ALG_S[nu] = saved
    res = {k: {"sets": len(v), "largest relative difference": float(max(v)),
               "sets differing by more than 1e-9": int(sum(t > 1e-9 for t in v))} for k, v in d.items()}
    if write:
        json.dump(res, open(os.path.join(HERE, "r_result.json"), "w"), indent=1)
    for k, v in res.items():
        print(f"{k}: {v['sets']} sets, largest {v['largest relative difference']:.3g}, "
              f"{v['sets differing by more than 1e-9']} above 1e-9")
    return res, d


if __name__ == "__main__":
    main()
