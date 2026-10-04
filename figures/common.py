# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
"""Simulated round shared by the figures of the article (fixed seed)."""
import sys, math
import os
HERE = os.path.dirname(os.path.abspath(__file__))
for d_ in ("src", "tests", "crosscheck"):
    sys.path.insert(0, os.path.join(HERE, "..", d_))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pt13528 import robust, assigned_value, scores, homogeneity, graphics

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "pdf.fonttype": 42, "svg.fonttype": "none",
    "axes.linewidth": 0.6, "hatch.linewidth": 0.6,
})
BLUE, ORANGE, GREY, DARK, MID, LIGHT = "#1F77B4", "#D1580F", "#9E9E9E", "#2B2B2B", "#666666", "#EFEFEF"

# ---- simulated round (seeded); all statistics below are computed with pt13528 ----
rng = np.random.default_rng(13528)
x = np.round(rng.normal(50.0, 1.4, 20), 1)
x[3], x[11], x[16] = 56.9, 43.6, 53.6          # two outlying results and one borderline
p = len(x)
ra = robust.algorithm_a(x)
x_star, s_star = ra.location, ra.scale
u_xpt = assigned_value.u_robust(s_star, p)
sigma_pt = 1.5                                    # fixed in advance by the provider (8.2)
negligible = scores.uncertainty_negligible(u_xpt, sigma_pt)
z = np.array([scores.z_score(v, x_star, sigma_pt) for v in x])
cls = [scores.classify_z(v) for v in z]
order = np.argsort(z)

hom = np.round(rng.normal(50.0, 0.22, (10, 1)) + rng.normal(0, 0.20, (10, 2)), 2)
H = homogeneity.homogeneity(hom, sigma_pt=sigma_pt)

bw = graphics.bandwidth(p, robust_sd=s_star)
kd_x, kd_y = graphics.kernel_density(x, bw)

def zcol(c):
    c = str(c).lower()
    if "action" in c or "unaccept" in c: return ORANGE
    if "warn" in c or "question" in c: return "#F2B78F"
    return BLUE

if __name__ == "__main__":
    print(x); print(ra); print(u_xpt, sigma_pt, negligible)
    print(np.round(z, 2)); print(cls); print(H); print(bw)
