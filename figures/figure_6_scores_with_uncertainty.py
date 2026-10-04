# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
from common import *
from matplotlib.patches import Rectangle
rng5 = np.random.default_rng(5)
P = 16
XPT, U_XPT, SIG = 50.0, 0.20, 1.0            # reference value, its standard uncertainty, sigma_pt
u_true = rng5.uniform(0.45, 0.95, P)
xi = np.round(XPT + rng5.normal(0, 1, P) * u_true, 2)
u_rep = np.round(u_true * rng5.uniform(0.9, 1.1, P), 2)
# three instructive laboratories
xi[4], u_rep[4] = 51.75, 0.25      # small bias, uncertainty understated
xi[9], u_rep[9] = 46.60, 1.80      # large bias, generous uncertainty
xi[13], u_rep[13] = 53.30, 0.50    # large bias, ordinary uncertainty
lab = np.arange(1, P + 1)
zz = np.array([scores.z_score(v, XPT, SIG) for v in xi])
ze = np.array([scores.zeta_score(v, XPT, u, U_XPT) for v, u in zip(xi, u_rep)])
en = np.array([scores.en_score(v, XPT, 2 * u, 2 * U_XPT) for v, u in zip(xi, u_rep)])
s_star = robust.algorithm_a(xi).scale
flag = [scores.uncertainty_flag(u, U_XPT, 1.5 * s_star) for u in u_rep]
assert scores.uncertainty_negligible(U_XPT, sigma_pt=SIG)
def col(i):
    a, b = abs(zz[i]) >= 3, abs(ze[i]) >= 3
    return ORANGE if (a and b) else ("#7B5EA7" if b else ("#3A8F5C" if a else BLUE))
cols = [col(i) for i in range(P)]

fig = plt.figure(figsize=(7.4, 5.6))
bg = fig.add_axes([0, 0, 1, 1]); bg.set_xlim(0, 100); bg.set_ylim(0, 100); bg.axis("off")
def ptitle(x, y, letter, t, sub):
    bg.text(x, y, letter, fontsize=10, fontweight="bold", color=DARK, va="center")
    bg.text(x + 2.6, y, t, fontsize=9.2, fontweight="bold", color=DARK, va="center")
    bg.text(x + 2.6, y - 3.2, sub, fontsize=7.4, color=MID, va="center")
def clean(ax):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(MID)
    ax.tick_params(labelsize=7, length=2, width=0.5, colors=MID, pad=1.5)

# ---- (a) results with expanded uncertainty ----
ptitle(2, 96.3, "a", "Results with reported uncertainty", r"16 simulated laboratories  ·  bar: ± $U(x_i)$, $k$ = 2  ·  band: $x_{pt}$ ± $U(x_{pt})$  ·  dashed: ± 3$\,\sigma_{pt}$")
ax = fig.add_axes([0.075, 0.585, 0.90, 0.285])
ax.axhspan(XPT - 2 * U_XPT, XPT + 2 * U_XPT, color=BLUE, alpha=0.18, lw=0); ax.axhline(XPT, color=BLUE, lw=1.2)
for sg in (-1, 1): ax.axhline(XPT + sg * 3 * SIG, color=MID, lw=0.6, ls=(0, (3, 2)))
for i in range(P):
    ax.errorbar(lab[i], xi[i], yerr=2 * u_rep[i], fmt="o", ms=4.6, color=cols[i], mec="white", mew=0.5, elinewidth=1.3, capsize=2.2)
ax.set_xticks(lab); ax.set_xlim(0.4, P + 0.6); ax.set_ylim(42.6, 55.2)
ax.set_xlabel("laboratory", fontsize=7.6, color=MID, labelpad=1); ax.set_ylabel("result", fontsize=7.6, color=MID, labelpad=2); clean(ax)

# ---- (b) z against zeta ----
ptitle(2, 47.0, "b", r"$z$ and $\zeta$ answer different questions", "same laboratories; lines at ± 3")
ax = fig.add_axes([0.075, 0.085, 0.40, 0.31])
L = 8.2
ax.add_patch(Rectangle((-3, -3), 6, 6, fc="#EAF1F7", ec="none", zorder=0))
for v in (-3, 3):
    ax.axvline(v, color=MID, lw=0.6, ls=(0, (3, 2))); ax.axhline(v, color=MID, lw=0.6, ls=(0, (3, 2)))
ax.scatter(zz, ze, s=26, c=cols, edgecolors="white", linewidths=0.5, zorder=3)
for i in (4, 9, 13):
    dx, dy, ha, note = {4: (-0.35, 0.0, "right", "lab 5: uncertainty understated"), 9: (0.0, -1.25, "left", "lab 10: outside the scheme limit,\nconsistent with its own claim"),
                        13: (-0.2, 1.0, "right", "lab 14")}[i]
    ax.text(zz[i] + dx, ze[i] + dy, note, fontsize=6.9, color=cols[i], fontweight="bold", ha=ha, va="center", linespacing=1.2)
ax.set_xlim(-4.6, 4.6); ax.set_ylim(-4.6, L)
ax.set_xlabel(r"$z$  (deviation against $\sigma_{pt}$)", fontsize=7.6, color=MID, labelpad=1)
ax.set_ylabel(r"$\zeta$  (deviation against own uncertainty)", fontsize=7.6, color=MID, labelpad=2); clean(ax)

# ---- (c) En ----
ptitle(53, 47.0, "c", r"$E_n$ with expanded uncertainties", r"|$E_n$| ≥ 1 is an action signal  ·  c: $u(x_i)$ > 1.5$\,s^*$ (9.8)")
ax = fig.add_axes([0.585, 0.085, 0.39, 0.31])
ecol = [ORANGE if abs(e) >= 1 else BLUE for e in en]
ax.bar(lab, en, color=ecol, width=0.7, lw=0)
for v in (-1, 1): ax.axhline(v, color=MID, lw=0.6, ls=(0, (3, 2)))
ax.axhline(0, color=DARK, lw=0.6)
top = max(en.max(), 1) + 0.4
for i in range(P):
    if flag[i] != "a":
        ax.text(lab[i], 0.28, flag[i], fontsize=7.4, color=DARK, ha="center", va="center", fontweight="bold")
ax.set_xticks(lab); ax.set_xlim(0.3, P + 0.7); ax.set_ylim(min(en.min(), -1) - 0.5, top)
ax.set_xlabel("laboratory", fontsize=7.6, color=MID, labelpad=1); ax.set_ylabel(r"$E_n$", fontsize=7.6, color=MID, labelpad=1); clean(ax)
ax.tick_params(axis="x", labelsize=6.2)

# legend strip
items = [(BLUE, "no signal"), ("#7B5EA7", r"only $\zeta$ signals"), ("#3A8F5C", r"only $z$ signals"), (ORANGE, "both signal")]
x0 = 30
for c, t in items:
    bg.plot(x0, 52.3, marker="o", ms=4.6, mfc=c, mec="white", mew=0.4, ls="none"); bg.text(x0 + 1.3, 52.3, t, fontsize=7.4, color=DARK, va="center")
    x0 += 17.5
for i in (4, 9, 13): print(lab[i], xi[i], u_rep[i], round(zz[i], 2), round(ze[i], 2), round(en[i], 2), flag[i])
print("signals z", int((abs(zz) >= 3).sum()), "zeta", int((abs(ze) >= 3).sum()), "En", int((abs(en) >= 1).sum()), "s*", round(s_star, 3), flag)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(HERE, f"Figure_6.{ext}"), dpi=300, facecolor="white")
