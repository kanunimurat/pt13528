# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
from common import *
import json, os
import annex_e_data as E
from pt13528 import assigned_value as av, sigma_pt as sp, homogeneity as hm
from matplotlib.patches import Rectangle, FancyBboxPatch
GREEN, PURPLE = "#3A8F5C", "#7B5EA7"

# ---------- (a) printed against computed, in units of the last printed digit ----------
import printed_values as P
rows = P.reproduced()
dev = [(r[0], P.deviation(r)) for r in rows]
groups = []
for g, _ in dev:
    if g not in groups: groups.append(g)
inc = P.inconsistent()
dat, xs, ss = E.E1["half"]; a12 = robust.algorithm_a(E.E12_A)
open_cases = [("Table E.1\ncol. 3\n$x^*$", inc[0][4]), ("Table E.5\n$u$ with\nMADe", inc[2][4]),
              ("Table E.10\nmean by\nAlg. A", inc[1][4]), ("Table E.10\nSD by\nAlg. A", (a12.scale - 3.29) * 100)]
print(len(rows), "comparisons; max |dev| =", max(abs(v) for _, v in dev)); print(open_cases)

# ---------- (b) Python against PHP ----------
import compare
A = compare.python_200(); B = json.load(open(os.path.join(HERE, "..", "crosscheck", "php_200.json")))   # 200 sets
keys = list(A[0])

fig = plt.figure(figsize=(7.4, 7.3))
bg = fig.add_axes([0, 0, 1, 1]); bg.set_xlim(0, 100); bg.set_ylim(0, 100); bg.axis("off")
def ptitle(x, y, letter, t, sub):
    bg.text(x, y, letter, fontsize=10, fontweight="bold", color=DARK, va="center")
    bg.text(x + 2.6, y, t, fontsize=9.2, fontweight="bold", color=DARK, va="center")
    bg.text(x + 2.6, y - 2.4, sub, fontsize=7.4, color=MID, va="center")
def clean(ax):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(MID)
    ax.tick_params(labelsize=7, length=2, width=0.5, colors=MID, pad=1.5)

ptitle(2, 97.3, "a", "Printed in the standard against computed", f"{len(rows)} printed values; difference in units of the last printed digit; band: ± 0.5 unit")
ax = fig.add_axes([0.085, 0.655, 0.89, 0.255])
ax.axhspan(-0.5, 0.5, color=BLUE, alpha=0.14, lw=0); ax.axhline(0, color=DARK, lw=0.6)
rj = np.random.default_rng(3)
for gi, g in enumerate(groups):
    v = np.array([d for gg, d in dev if gg == g])
    ax.plot(gi + rj.uniform(-0.28, 0.28, len(v)), v, ls="none", marker="o", ms=3.4, mfc=BLUE, mec="white", mew=0.3, alpha=0.9)
    ax.text(gi, 3.25, f"n = {len(v)}", fontsize=6.6, color=MID, ha="center")
x0 = len(groups) + 0.4
ax.axvline(x0 - 0.7, color="#BDBDBD", lw=0.7, ls=(0, (2, 2)))
lim = 3.0
for i, (lab_, v) in enumerate(open_cases):
    xx = x0 + i * 1.5; vv = float(np.clip(v, -lim + 0.25, lim - 0.25))
    ax.plot(xx, vv, marker="o" if abs(v) < lim else ("v" if v < 0 else "^"), ms=5, mfc=ORANGE, mec="white", mew=0.4, ls="none")
    ax.text(xx, vv + (0.42 if (v > 0 or abs(v) >= lim) else -0.42), (f"{v:+.1f}" if abs(v) < lim else f"{v:+.0f}").replace("-", "−"), fontsize=6.8, color=ORANGE, ha="center", va="center", fontweight="bold")
ax.text(x0 + 2.25, 3.25, "do not follow from the text", fontsize=6.6, color=ORANGE, ha="center")
ax.set_xticks(list(range(len(groups))) + [x0 + i * 1.5 for i in range(len(open_cases))])
ax.set_xticklabels([g.replace("Table ", "Table\n") for g in groups] + [c[0] for c in open_cases], fontsize=6.2)
ax.set_ylim(-lim, 3.7); ax.set_xlim(-0.6, x0 + 5.2); ax.set_yticks([-2, -1, -0.5, 0, 0.5, 1, 2]); ax.set_yticklabels(["−2", "−1", "−0.5", "0", "0.5", "1", "2"])
ax.set_ylabel("computed − printed", fontsize=7.6, color=MID, labelpad=2); clean(ax)
ax.text((len(groups) - 2) / 2, -4.25, "worked example of Annex E", fontsize=6.8, color=MID, ha="center", va="center")

ptitle(2, 57.5, "b", "Python library against the PHP engine", "16 quantities; largest absolute difference in 100 generated sets without ties (blue) and in 100 with ties, where larger (orange)")
ax = fig.add_axes([0.20, 0.335, 0.775, 0.185])
mx0 = {k: max(abs(x[k] - y[k]) for x, y in zip(A[0::2], B[0::2])) for k in keys}
mx1 = {k: max(abs(x[k] - y[k]) for x, y in zip(A[1::2], B[1::2])) for k in keys}
order_ = sorted(keys, key=lambda k: mx0[k])
ax.bar(range(len(order_)), [max(mx0[k], 1e-17) for k in order_], color=BLUE, width=0.66, lw=0)
ties_ = [k for k in ("Algorithm A x*", "Algorithm A s*", "Q/Hampel x*", "Q method") if mx1[k] > 1e-9]
xa = len(order_) + 0.6
ax.bar([xa + i for i in range(len(ties_))], [mx1[k] for k in ties_], color=ORANGE, width=0.66, lw=0)
ax.set_yscale("log"); ax.set_ylim(1e-17, 1e0); ax.axhline(1e-10, color=MID, lw=0.6, ls=(0, (3, 2)))
ax.text(-0.5, 2.2e-10, "$10^{-10}$", fontsize=6.8, color=MID, va="bottom")
lab = {"expanded criterion": "exp.\ncrit.", "Q/Hampel x*": "Q/H.\n$x^*$", "Q method": "Q\nmeth.", "Algorithm S": "Alg.\nS", "zeta": r"$\zeta$", "E_n": "$E_n$", "z'": "$z'$", "z": "$z$", "s_s": "$s_s$", "s_w": "$s_w$",
       "Algorithm A x*": "Alg.\nA $x^*$", "Algorithm A s*": "Alg.\nA $s^*$", "median": "med.", "MADe": "MADe", "nIQR": "nIQR"}
ax.set_xticks(list(range(len(order_))) + [xa + i for i in range(len(ties_))]); ax.set_xticklabels([lab.get(k, k) for k in order_] + [lab.get(k, k) for k in ties_], fontsize=6.2)
for i, k in enumerate(order_):
    if mx0[k] == 0: ax.text(i, 3e-17, "0", fontsize=6.8, color=BLUE, ha="center", va="bottom", fontweight="bold")
nq = sum(abs(x["Q method"] - y["Q method"]) > 1e-9 * x["Q method"] for x, y in zip(A[1::2], B[1::2]))
ax.text(xa - 0.75, 6e-1, f"With ties: Algorithm A differs in 1 set of 5200\n(first iterate exactly 41.15, rounded to 41.1 or 41.2).\nThe Q method differs in {nq} of 100 sets: the PHP\nengine does not merge tied differences", fontsize=6.6, color=ORANGE, ha="right", va="top", linespacing=1.25)
ax.set_xlim(-0.7, xa + len(ties_) - 0.3); ax.set_ylabel("largest |difference|", fontsize=7.6, color=MID, labelpad=2); clean(ax)

ptitle(2, 26.3, "c", "Printed results that do not follow from the text, and the 2026 amendment", "status after ISO 13528:2022/Amd 1:2026")
tab = [("Table E.1, third column, $x^*$", "printed 23.95; both stopping rules give 23.96", "open", ORANGE),
       ("Table E.10, $z$ scores", "text names Algorithm A, numbers are arithmetic", "open", ORANGE),
       ("Table E.5, $u$(median)", "follows nIQR; the row names nIQR and MADe", "open", ORANGE),
       ("Table E.6, flags", "not reproduced by the limits of Clause 9.8", "open", ORANGE),
       ("Formula (C.18), $h$", "undefined for $p$ = 2, 3; now $\\lfloor p/2 \\rfloor + 1$", "corrected", GREEN),
       ("Formula (C.19), factor", "2.2219; now 2.2191", "corrected", GREEN),
       ("Table E.12", "one assigned value corrected; footnote on rounding added", "corrected", GREEN)]
y = 20.3
for nm, why, stt, col in tab:
    bg.add_patch(FancyBboxPatch((2.5, y - 0.95), 11.5, 1.9, boxstyle="round,pad=0,rounding_size=0.5", fc=col, ec="none"))
    bg.text(8.25, y, stt, fontsize=7, color="white", ha="center", va="center", fontweight="bold")
    bg.text(16, y, nm, fontsize=7.8, color=DARK, va="center", fontweight="bold")
    bg.text(46, y, why, fontsize=7.6, color=DARK, va="center")
    y -= 2.75
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(HERE, f"Figure_4.{ext}"), dpi=300, facecolor="white")
