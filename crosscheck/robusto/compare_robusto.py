# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Comparison of the Q method, the Hampel estimator, Q/Hampel, Qn and Algorithm A with the Go library Robusto.

Step 1 (writes sets.json and scales.json):  python crosscheck/robusto/compare_robusto.py prepare
Step 2 (needs Go and Robusto v0.2.0):        see README.md, writes robusto_out.json
Step 3 (writes robusto_result.json):         python crosscheck/robusto/compare_robusto.py
"""
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
from pt13528 import robust  # noqa: E402

spec = importlib.util.spec_from_file_location("compare", os.path.join(HERE, "..", "compare.py"))
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)


def prepare():
    sets = [s[0] for s in compare.sets_200()]
    json.dump(sets, open(os.path.join(HERE, "sets.json"), "w"))
    scales = [[robust.q_method(x), robust.made(x), robust.qn(x)] for x in sets]
    json.dump(scales, open(os.path.join(HERE, "scales.json"), "w"))


def main():
    sets = json.load(open(os.path.join(HERE, "sets.json")))
    scales = json.load(open(os.path.join(HERE, "scales.json")))
    ro = json.load(open(os.path.join(HERE, "robusto_out.json")))
    before = json.load(open(os.path.join(HERE, "..", "php_200_before_fix.json")))
    res = {}
    for name, idx in (("100 sets without ties", range(0, 200, 2)), ("100 sets with ties", range(1, 200, 2))):
        q = [abs(robust.q_method(sets[i]) - ro[i]["q_scale"]) / ro[i]["q_scale"] for i in idx]
        qh = [abs(robust.q_hampel(sets[i]).location - ro[i]["qhampel_loc"]) / scales[i][0] for i in idx]
        qn = [abs(robust.qn(sets[i]) - ro[i]["qn_scale"]) / ro[i]["qn_scale"] for i in idx]
        aa = [max(abs(robust.algorithm_a(sets[i]).location - ro[i]["a_loc"]), abs(robust.algorithm_a(sets[i]).scale - ro[i]["a_scale"])) / ro[i]["a_scale"] for i in idx]
        ph = [abs(ro[i]["q_scale"] - before[i]["Q method"]) / before[i]["Q method"] for i in idx]
        res[name] = {
            "Q method: largest relative difference; sets above 1e-9; median of those": [max(q), int(sum(v > 1e-9 for v in q)), float(np.median([v for v in q if v > 1e-9])) if any(v > 1e-9 for v in q) else 0.0],
            "Q/Hampel location: largest difference / s*": max(qh),
            "Qn: largest relative difference (rounded finite-sample factors)": max(qn),
            "Algorithm A: largest difference / s*": max(aa),
            "Robusto Q method against the PHP engine before its correction: largest relative difference": max(ph),
        }
    hf, hi = [], []
    for i, x in enumerate(sets):
        for j in range(3):
            s = scales[i][j]
            hf.append(abs(robust.hampel(x, s, "finite") - ro[i]["hampel_at_q_made_qn"][j]) / s)
            hi.append(abs(robust.hampel(x, s, "iterative") - ro[i]["hampel_at_q_made_qn"][j]) / (0.01 * s / np.sqrt(len(x))))
    res["Hampel at fixed scales (Q, MADe, Qn), 600 cases: largest difference / s*, finite-step"] = max(hf)
    res["Hampel, iterative variant (C.5.3.2): largest difference / its stopping limit 0,01 s*/sqrt(p)"] = max(hi)
    json.dump(res, open(os.path.join(HERE, "robusto_result.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    prepare() if sys.argv[1:] == ["prepare"] else main()
