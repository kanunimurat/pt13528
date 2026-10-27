# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""The three-figure stopping criterion of Algorithm A on two data generators (added in 0.1.9).
Generator 1 = crosscheck/compare.py (5200 sets). Generator 2 = moderate contamination in units of sigma,
other distributions, p from 3, data quantized relative to sigma. Reports quantiles of the change in s*,
operational definitions, and the effect of a power of ten."""
import sys, math, json, importlib.util
import numpy as np
import gzip, os
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(REPO, "src"))
spec = importlib.util.spec_from_file_location("cmp", REPO + "/crosscheck/compare.py"); cmp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cmp)
from pt13528 import robust, scores
sig = cmp.sig

def gen2(n=5000, seed=20261027):
    rng = np.random.default_rng(seed)
    for c in range(n):
        p = int(rng.choice([3, 4, 5])) if c % 5 == 0 else int(rng.integers(6, 41))
        mu, s = rng.uniform(1, 100), rng.uniform(0.1, 5)
        kind = c % 4
        if kind == 0: x = rng.normal(mu, s, p)
        elif kind == 1: x = mu + s * rng.standard_t(3, p) / math.sqrt(3)
        elif kind == 2: x = mu * np.exp(rng.normal(0, s / mu, p))          # mildly skewed
        else: x = rng.normal(mu, s, p)
        k = int(rng.integers(0, max(1, p // 5) + 1)) if p >= 6 else int(rng.integers(0, 2))
        if k:
            x[rng.choice(p, k, replace=False)] += rng.choice([-1, 1], k) * rng.choice([2, 3, 4, 6], k) * s
        if c % 2:
            res = 10 ** math.floor(math.log10(0.1 * s)); x = np.round(x / res) * res   # resolution about 0.1 sigma
        yield [float(v) for v in x], kind, k

def stats(sets, rule):
    out = dict(n=0, third_s=0, third_x=0, results=0, sig_changed=0, rel=[], rel_x=[], it=[],
               unit=[0, 0, 0.0], origin=[0, 0, 0.0], pow10=[0, 0], small_p=dict(n=0, third_s=0, rel=[]))
    for x in sets:
        x = np.asarray(x)
        c = robust.algorithm_a(x)
        if c.degenerate or c.scale == 0: continue
        try: a = robust.algorithm_a(x, tol=rule)
        except Exception: continue
        out["n"] += 1
        za = [scores.classify_z(scores.z_score(v, a.location, a.scale)) for v in x]
        zc = [scores.classify_z(scores.z_score(v, c.location, c.scale)) for v in x]
        out["results"] += len(x); out["sig_changed"] += sum(u != v for u, v in zip(za, zc))
        d3s = sig(a.scale, 3) != sig(c.scale, 3); out["third_s"] += d3s
        out["third_x"] += sig(a.location, 3) != sig(c.location, 3)
        r = abs(a.scale - c.scale) / c.scale; out["rel"].append(r)
        out["rel_x"].append(abs(a.location - c.location) / c.scale)
        out["it"].append((a.iterations, c.iterations))
        if len(x) < 6:
            out["small_p"]["n"] += 1; out["small_p"]["third_s"] += d3s; out["small_p"]["rel"].append(r)
        for key, y, back in (("unit", x * 25.4, lambda q: (q.location / 25.4, q.scale / 25.4)),
                             ("origin", x + 273.15, lambda q: (q.location - 273.15, q.scale))):
            loc, sc = back(robust.algorithm_a(y, tol=rule))
            zb = [scores.classify_z(scores.z_score(v, loc, sc)) for v in x]
            out[key][0] += abs(sc - a.scale) > 1e-9 * a.scale
            out[key][1] += sum(u != v for u, v in zip(za, zb))
            out[key][2] = max(out[key][2], abs(sc - c.scale) / c.scale)
        b = robust.algorithm_a(x * 1000.0, tol=rule)
        out["pow10"][0] += abs(b.scale / 1000.0 - a.scale) > 1e-9 * a.scale
        out["pow10"][1] += 1
    q = lambda v: [float(np.percentile(v, p)) for p in (25, 50, 75, 95, 99)] + [float(np.max(v))]
    return {"sets": out["n"],
            "s* differs from converged after rounding both to 3 significant figures": int(out["third_s"]),
            "x* differs (same definition)": int(out["third_x"]),
            "relative change of s*: P25, P50, P75, P95, P99, max": q(out["rel"]),
            "change of x* in units of s*: P50, P95, max": [float(np.median(out["rel_x"])), float(np.percentile(out["rel_x"], 95)), float(max(out["rel_x"]))],
            "median iterations rule / convergence": [float(np.median([i[0] for i in out["it"]])), float(np.median([i[1] for i in out["it"]]))],
            "z signals changed (z with x*, s* of each rule; classes |z|<=2, 2<|z|<3, |z|>=3), of results": [int(out["sig_changed"]), int(out["results"])],
            "unit x25.4: sets s* changes, signals changed, worst error vs convergence": [int(out["unit"][0]), int(out["unit"][1]), out["unit"][2]],
            "origin +273.15: sets s* changes, signals changed, worst error": [int(out["origin"][0]), int(out["origin"][1]), out["origin"][2]],
            "x1000: sets in which s* changes (expected 0), of": out["pow10"],
            "p = 3 to 5: sets, s* differs at 3 s.f., median and max relative change": [out["small_p"]["n"], int(out["small_p"]["third_s"])] + ([float(np.median(out["small_p"]["rel"])), float(max(out["small_p"]["rel"]))] if out["small_p"]["rel"] else [])}

MODERATE = os.path.join(HERE, "inputs_moderate.json.gz")

if __name__ == "__main__":
    if "--store-inputs" in sys.argv or not os.path.exists(MODERATE):
        with gzip.open(MODERATE, "wt") as fh:
            json.dump({"numpy": np.__version__, "sets": [s[0] for s in gen2()]}, fh)
    with gzip.open(MODERATE, "rt") as fh:
        moderate = json.load(fh)["sets"]
    res = {}
    for which, sets in (("generator of compare.py, 5200 sets", list(cmp.sets_5000()) + [s[0] for s in cmp.sets_200()]),
                        ("moderate generator, 5000 sets", moderate)):
        res[which] = {rule: stats(sets, rule) for rule in ("iso2022", "iso2022-from-start", "equivalent-figure")}
    json.dump(res, open(os.path.join(HERE, "stopping_result.json"), "w"), indent=1)
    print(json.dumps(res, indent=1)[:2000])
