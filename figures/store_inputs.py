# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Writes the simulated inputs of Figs. 2, 5 and 6 to simulated_inputs.json.

The figure scripts generate their data from fixed seeds with NumPy's default_rng.
NumPy does not guarantee its random streams across versions, so the generated
values are stored as well. The generating code below repeats that of the scripts.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# Fig. 2 and graphical abstract (common.py): seed 13528
rng = np.random.default_rng(13528)
x = np.round(rng.normal(50.0, 1.4, 20), 1)
x[3], x[11], x[16] = 56.9, 43.6, 53.6
hom = np.round(rng.normal(50.0, 0.22, (10, 1)) + rng.normal(0, 0.20, (10, 2)), 2)

# Fig. 5: seed 4
rng4 = np.random.default_rng(4)
base = np.round(rng4.normal(50.0, 1.5, 24), 1)
dat = base.copy(); dat[[2, 9, 17]] = [58.4, 59.7, 61.2]

# Fig. 6: seed 5
rng5 = np.random.default_rng(5)
P = 16
u_true = rng5.uniform(0.45, 0.95, P)
xi = np.round(50.0 + rng5.normal(0, 1, P) * u_true, 2)
u_rep = np.round(u_true * rng5.uniform(0.9, 1.1, P), 2)
xi[4], u_rep[4] = 51.75, 0.25
xi[9], u_rep[9] = 46.60, 1.80
xi[13], u_rep[13] = 53.30, 0.50

out = {
    "numpy_version": np.__version__,
    "figure_2": {"seed": 13528, "generator": "normal(50.0, 1.4), 20 results rounded to 0.1; results 4, 12 and 17 set to 56.9, 43.6, 53.6; sigma_pt = 1.5",
                 "results": x.tolist(), "homogeneity_10x2": hom.tolist()},
    "figure_5": {"seed": 4, "generator": "normal(50.0, 1.5), 24 results rounded to 0.1; results 3, 10 and 18 set to 58.4, 59.7, 61.2 (a, b); panel c adds k results at 60 to the 24 clean results",
                 "clean_results": base.tolist(), "results": dat.tolist()},
    "figure_6": {"seed": 5, "generator": "x_pt = 50.0, u(x_pt) = 0.20, sigma_pt = 1.0; u_i uniform(0.45, 0.95); x_i = x_pt + N(0, 1) u_i rounded to 0.01; reported u = u_i uniform(0.9, 1.1); laboratories 5, 10 and 14 set by hand",
                 "results": xi.tolist(), "reported_u": u_rep.tolist()},
}
with open(os.path.join(HERE, "simulated_inputs.json"), "w") as f:
    json.dump(out, f, indent=1)
