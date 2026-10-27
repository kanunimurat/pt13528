# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Checks of the two printed results of Annex E that the library does not reproduce (added in 0.1.9).

1. Table E.1, third column, x* = 23,95: 324 hand-calculation scenarios (starting values, constants, rounding of
   x* and s* at every iteration, stopping rule). Which of them give the printed x* and s*?
2. Table E.10 (example E.12): every combination of 5 locations and 7 scales of Annex C and Clause 7 against the
   printed z scores and the "Average" and "Standard deviation" rows.
Run from the repository root: python crosscheck/annex_e_checks.py  (writes crosscheck/annex_e_checks.json)
"""
import itertools, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, os.path.join(HERE, "..", "tests"))
import annex_e_data as E
from pt13528 import robust


def table_e1():
    x = np.array(E.E1["half"][0], float)

    def r_dec(v, d): return None if d is None else round(v, d)
    def sig3(v): return float(f"{v:.3g}")

    def alg_a(x, start="median_made", made_f=1.483, delta_c=1.5, factor=1.134, round_dec=None, round_sig=False,
              stop="converge", max_iter=500):
        med = np.median(x)
        if start == "median_made": xs, ss = med, made_f * np.median(np.abs(x - med))
        elif start == "median_niqr":
            q1, q3 = np.quantile(x, [0.25, 0.75]); xs, ss = med, 0.7413 * (q3 - q1)
        elif start == "mean_sd": xs, ss = x.mean(), x.std(ddof=1)
        hist = [(xs, ss)]
        prev = None
        for it in range(1, max_iter + 1):
            d = delta_c * ss
            if round_dec is not None: d = round(d, round_dec)
            w = np.clip(x, xs - d, xs + d)
            nx = w.mean(); ns = factor * np.sqrt(np.sum((w - nx) ** 2) / (len(x) - 1))
            if round_dec is not None: nx, ns = round(nx, round_dec), round(ns, round_dec)
            if round_sig: nx, ns = sig3(nx), sig3(ns)
            if stop == "converge":
                if abs(nx - xs) < 1e-12 and abs(ns - ss) < 1e-12: xs, ss = nx, ns; break
            elif stop == "three_fig":
                if it >= 2 and sig3(nx) == sig3(xs) and sig3(ns) == sig3(ss): xs, ss = nx, ns; break
            elif stop == "three_fig_from_start":
                if sig3(nx) == sig3(xs) and sig3(ns) == sig3(ss): xs, ss = nx, ns; break
            xs, ss = nx, ns; hist.append((xs, ss))
        return xs, ss, it, hist

    base = alg_a(x)
    lib = robust.algorithm_a(list(x), tol=1e-12)
    assert abs(base[0] - lib.location) < 1e-9 and abs(base[1] - lib.scale) < 1e-9, (base[:2], lib)
    res = []
    grid = dict(start=["median_made", "median_niqr", "mean_sd"], made_f=[1.483, 1.4826], delta_c=[1.5],
                factor=[1.134, 1.13339, 1.0], round_dec=[None, 1, 2, 3, 4], round_sig=[False, True],
                stop=["converge", "three_fig", "three_fig_from_start"])
    for combo in itertools.product(*grid.values()):
        kw = dict(zip(grid.keys(), combo))
        if kw["round_sig"] and kw["round_dec"] is not None: continue
        xs, ss, it, h = alg_a(x, **kw)
        res.append({**kw, "x*": xs, "s*": ss, "iterations": it,
                    "x*_2dp_rounded": round(xs, 2), "x*_2dp_truncated": math.floor(xs * 100) / 100, "s*_2dp": round(ss, 2)})
    # all iterates of the default path (any stopping point)
    iterates = [round(v[0], 4) for v in base[3]]
    hits_round = [r for r in res if abs(r["x*_2dp_rounded"] - 23.95) < 1e-9]
    hits_trunc = [r for r in res if abs(r["x*_2dp_truncated"] - 23.95) < 1e-9]
    # delta constant variants (not ISO, sensitivity only)
    dsens = {c: round(alg_a(x, delta_c=c)[0], 4) for c in (1.4, 1.45, 1.5, 1.55, 1.6)}
    summary = {"library_converged": [lib.location, lib.scale], "scenarios": len(res),
               "scenarios_giving_23.95_by_rounding": len(hits_round),
               "scenarios_giving_23.95_by_truncation": len(hits_trunc),
               "range_x*_over_scenarios": [min(r["x*"] for r in res), max(r["x*"] for r in res)],
               "s*_printed_8.60_reproduced_in": sum(abs(r["s*_2dp"] - 8.60) < 1e-9 for r in res),
               "iterates_default_path_x*": iterates[:12],
               "delta_constant_sensitivity_x*": dsens,
               "hits_round_examples": hits_round[:10]}
    return {'summary': summary, 'pairs_reproduced_by_rounding': sum(1 for r in res if r['x*_2dp_rounded'] == 23.95 and r['s*_2dp'] == 8.60), 'scenarios': res}


def table_e10():
    out = {}
    for name, data, zs, avg, sd in (("A", E.E12_A, E.E12_ZA, 11.54, 3.29), ("B", E.E12_B, E.E12_ZB, 7.66, 2.90)):
        x = np.array(data); zp = np.array(zs)
        A = robust.algorithm_a(data); A3 = robust.algorithm_a(data, tol="iso2022"); QH = robust.q_hampel(data)
        loc = {"mean": x.mean(), "median": float(np.median(x)), "Algorithm A": A.location, "Algorithm A (three-figure)": A3.location, "Q/Hampel": QH.location}
        sca = {"SD": x.std(ddof=1), "MADe": robust.made(data), "nIQR": robust.niqr(data), "Algorithm A s*": A.scale,
               "Algorithm A s* (three-figure)": A3.scale, "Qn": robust.qn(data), "Q method": robust.q_method(data)}
        rows = []
        for (ln, l), (sn, s) in itertools.product(loc.items(), sca.items()):
            z = (x - l) / s
            ok = int(np.sum(np.abs(np.round(z, 3) - zp) < 1e-9))
            rows.append({"location": ln, "scale": sn, "x_pt": round(float(l), 4), "sigma": round(float(s), 4), "z reproduced (of %d)" % len(x): ok,
                         "max |z - printed|": round(float(np.max(np.abs(z - zp))), 3), "Average row": bool(round(l, 2) == avg), "SD row": bool(round(s, 2) == sd)})
        out[name] = {"printed": {"average": avg, "sd": sd, "mean of printed z": round(float(zp.mean()), 4), "sd of printed z": round(float(zp.std(ddof=1)), 4)}, "combinations": rows}
    return out


if __name__ == '__main__':
    r = {'Table E.1': table_e1(), 'Table E.10': table_e10()}
    json.dump(r, open(os.path.join(HERE, 'annex_e_checks.json'), 'w'), indent=1, default=float)
    print(json.dumps(r['Table E.1']['summary'], indent=1, default=float)[:1500])
    print('pairs reproduced by rounding:', r['Table E.1']['pairs_reproduced_by_rounding'])
