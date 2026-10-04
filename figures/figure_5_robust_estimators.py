# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
from common import *
from matplotlib.patches import Rectangle
PURPLE, GREEN = "#7B5EA7", "#3A8F5C"
rng4 = np.random.default_rng(4)
TRUE_MU, TRUE_SD = 50.0, 1.5
base = np.round(rng4.normal(TRUE_MU, TRUE_SD, 24), 1)
dat = base.copy(); dat[[2, 9, 17]] = [58.4, 59.7, 61.2]          # three high results
est = {"arithmetic mean": ("mean", MID, "s"), "median": ("median", GREEN, "D"),
       "Algorithm A": ("algorithm_a", BLUE, "o"), "Q/Hampel": ("q_hampel", ORANGE, "^")}
res = {k: assigned_value.consensus(dat, m) for k, (m, _, _) in est.items()}

fig = plt.figure(figsize=(7.4, 5.9))
bg = fig.add_axes([0, 0, 1, 1]); bg.set_xlim(0, 100); bg.set_ylim(0, 100); bg.axis("off")
def ptitle(x, y, letter, t, sub):
    bg.text(x, y, letter, fontsize=10, fontweight="bold", color=DARK, va="center")
    bg.text(x + 2.6, y, t, fontsize=9.2, fontweight="bold", color=DARK, va="center")
    bg.text(x + 2.6, y - 3.0, sub, fontsize=7.4, color=MID, va="center")
def clean(ax):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(MID)
    ax.tick_params(labelsize=7, length=2, width=0.5, colors=MID, pad=1.5)

# ---- (a) location ----
ptitle(2, 96.5, "a", "Assigned value from the same results", "24 simulated results, three of them high  ·  marker: $x_{pt}$, bar: ± $u(x_{pt})$")
ax = fig.add_axes([0.20, 0.585, 0.77, 0.30])
out = dat > 56
jit = np.random.default_rng(2).uniform(-0.25, 0.25, len(dat))
ax.plot(dat[~out], 4.6 + jit[~out], ls="none", marker="o", ms=4.4, mfc=GREY, mec="white", mew=0.4)
ax.plot(dat[out], 4.6 + jit[out], ls="none", marker="o", ms=4.4, mfc="white", mec=DARK, mew=1.0)
ax.axvline(TRUE_MU, color=DARK, lw=0.7, ls=(0, (3, 2)), zorder=0)
ax.axhline(3.9, color="#CFCFCF", lw=0.6)
for i, (k, (m, col, mk)) in enumerate(est.items()):
    y = 3.2 - i * 0.9; r = res[k]
    ax.errorbar(r.x_pt, y, xerr=r.u_x_pt, fmt=mk, ms=5.2, color=col, mec="white", mew=0.5, elinewidth=1.4, capsize=2.5)
    ax.text(62.6, y, f"{r.x_pt:.2f} ± {r.u_x_pt:.2f}", fontsize=7.6, color=col, va="center", ha="right", fontweight="bold")
ax.set_yticks([4.6] + [3.2 - i * 0.9 for i in range(4)]); ax.set_yticklabels(["results"] + list(est), fontsize=7.8, color=DARK)
ax.set_ylim(0.0, 5.35); ax.set_xlim(45.5, 62.8); ax.set_xlabel("reported result", fontsize=7.6, color=MID, labelpad=1)
clean(ax); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
ax.text(TRUE_MU + 0.15, 5.05, "value used to simulate", fontsize=6.8, color=MID, ha="left", va="center")

# ---- (b) scale ----
ptitle(2, 49.5, "b", "Dispersion", "same results; dashed: SD used to simulate")
ax = fig.add_axes([0.20, 0.085, 0.24, 0.335])
sc = [("SD", float(np.std(dat, ddof=1)), MID), ("MADe", robust.made(dat), GREEN), ("nIQR", robust.niqr(dat), GREEN),
      ("$s^*$ (Algorithm A)", robust.algorithm_a(dat).scale, BLUE), ("Qn", robust.qn(dat), PURPLE), ("Q method", robust.q_method(dat), ORANGE)]
for i, (n, v, c) in enumerate(sc):
    y = len(sc) - 1 - i
    ax.barh(y, v, color=c, height=0.62, lw=0)
    ax.text(max(v, TRUE_SD) + 0.08, y, f"{v:.2f}", fontsize=7.4, color=DARK, va="center")
ax.axvline(TRUE_SD, color=DARK, lw=0.7, ls=(0, (3, 2)))
ax.set_yticks(range(len(sc))); ax.set_yticklabels([n for n, _, _ in sc][::-1], fontsize=7.6, color=DARK)
ax.set_xlim(0, 4.6); ax.set_xlabel("estimate of standard deviation", fontsize=7.6, color=MID, labelpad=1)
clean(ax); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)

# ---- (c) contamination ----
ptitle(51, 49.5, "c", "Contamination and the assigned value", "$k$ results at 60 are added to the 24 clean results")
ax = fig.add_axes([0.575, 0.085, 0.395, 0.335])
ks = list(range(0, 11)); srt = np.argsort(base)
for k_, (m, col, mk) in est.items():
    ys = []
    for k in ks:
        d = np.concatenate([base, np.full(k, 60.0)])
        ys.append(assigned_value.consensus(d, m).x_pt - TRUE_MU)
    print(k_, np.round(ys, 2))
    ax.plot(ks, ys, color=col, lw=1.4, marker=mk, ms=4.2, mec="white", mew=0.4, label=k_)
ax.axhline(0, color=DARK, lw=0.7, ls=(0, (3, 2)))
ax.set_xlabel("number of added results, $k$", fontsize=7.6, color=MID, labelpad=1)
ax.set_ylabel("shift of $x_{pt}$", fontsize=7.6, color=MID, labelpad=2)
ax.set_xticks(ks); ax.set_xlim(-0.3, 10.3)
ax.legend(fontsize=7.2, frameon=False, loc="upper left", handlelength=1.6, labelspacing=0.3, borderaxespad=0.2)
clean(ax)
for k in res: print(k, round(res[k].x_pt, 3), round(res[k].u_x_pt, 3))
print([(n, round(v, 3)) for n, v, _ in sc])
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(HERE, f"Figure_5.{ext}"), dpi=300, facecolor="white")
