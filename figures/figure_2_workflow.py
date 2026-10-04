# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
from common import *
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

W, Hh = 7.4, 8.9
fig = plt.figure(figsize=(W, Hh))
bg = fig.add_axes([0, 0, 1, 1]); bg.set_xlim(0, 100); bg.set_ylim(0, 100); bg.axis("off")

# column geometry (figure %)
XL, XB0, XB1, XR = 20.5, 23.0, 62.0, 65.5
R = {"sig": (84.0, 7.6), "hom": (66.6, 13.4), "av": (49.2, 13.4), "sc": (31.8, 13.4), "gr": (14.4, 13.4)}
rows = [R["hom"], R["av"], R["sig"], R["sc"], R["gr"]]
heads = ["Input", "Computation in pt13528", "Result"]
for xx, t, ha in [(XL, heads[0], "right"), ((XB0 + XB1) / 2, heads[1], "center"), (XR, heads[2], "left")]:
    bg.text(xx, 96.3, t, ha=ha, va="center", fontsize=9.5, fontweight="bold", color=DARK)
bg.text((XB0 + XB1) / 2, 94.3, "module  ·  clause of ISO 13528:2022", ha="center", va="center", fontsize=7.5, color=MID)
for xx in (XB0 - 1.2, XB1 + 1.2):
    bg.plot([xx, xx], [14.4, 92.6], ls=(0, (2, 2)), lw=0.7, color="#BDBDBD", zorder=0)

def box(i, title, clause):
    y, h = rows[i]
    bg.add_patch(Rectangle((XB0, y), XB1 - XB0, h, fc="white", ec="#5A5A5A", lw=1.0, zorder=2))
    bg.plot([XB0, XB1], [y + h, y + h], color="#5A5A5A", lw=2.4, solid_capstyle="butt", zorder=3)
    bg.text(XB0 + 1.0, y + h - 1.35, title, fontsize=8.5, fontweight="bold", color=DARK, va="center", zorder=4,
            family="DejaVu Sans Mono")
    bg.text(XB1 - 1.0, y + h - 1.35, clause, fontsize=7.5, color=MID, va="center", ha="right", zorder=4)
    return fig.add_axes([(XB0 + 2.2) / 100, (y + 3.3) / 100, (XB1 - XB0 - 4.0) / 100, (h - 6.6) / 100], zorder=5)

def left(i, bold, grey, dy=0.0):
    y, h = rows[i]; yc = y + h / 2 + dy
    bg.text(XL, yc + 1.1, bold, ha="right", va="center", fontsize=9, fontweight="bold", color=DARK)
    bg.text(XL, yc - 1.3, grey, ha="right", va="center", fontsize=7.8, color=MID, linespacing=1.25)

def right(i, lines):
    y, h = rows[i]; yc = y + h / 2
    n = len(lines); step = 2.35
    for k, (t, kw) in enumerate(lines):
        bg.text(XR, yc + (n - 1) * step / 2 - k * step, t, ha="left", va="center", **({"fontsize": 8.2, "color": DARK} | kw))

def clean(ax, xlabel=None):
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.set_yticks([]); ax.tick_params(axis="x", labelsize=6.5, length=2, width=0.5, pad=1.5, colors=MID)
    ax.spines["bottom"].set_color(MID); ax.patch.set_alpha(0)
    if xlabel: ax.set_xlabel(xlabel, fontsize=6.8, color=MID, labelpad=1)

# ---------- 1 homogeneity ----------
ax = box(0, "homogeneity", "Annex B")
g = hom.shape[0]
for k in range(g):
    ax.plot([k + 1, k + 1], hom[k], color=GREY, lw=1.0, zorder=1)
    ax.plot([k + 1, k + 1], hom[k], ls="none", marker="o", ms=3.6, mfc=GREY, mec="white", mew=0.4, zorder=2)
    ax.plot(k + 1, hom[k].mean(), marker="_", ms=7, mew=1.3, color=DARK, zorder=3)
ax.axhline(H.mean, color=MID, lw=0.6, ls=(0, (3, 2)))
ax.set_xlim(0.3, g + 0.7); ax.set_xticks(range(1, g + 1)); clean(ax, "proficiency test item")
left(0, "Item check data", "10 items × 2 test portions")
right(0, [("between-item SD", {"color": MID, "fontsize": 7.8}),
          (rf"$s_s$ = {H.s_s:.2f}", {"fontweight": "bold"}),
          (rf"criterion 0.3$\,\sigma_{{pt}}$ = {H.criterion:.2f}", {"color": MID, "fontsize": 7.8}),
          ("sufficiently homogeneous", {"color": BLUE, "fontweight": "bold"})])

# ---------- 2 assigned value ----------
ax = box(1, "robust · assigned_value", "Annex C  ·  Clause 7")
out = np.array([c == "action" for c in cls]); warn = np.array([c == "warning" for c in cls])
jit = np.random.default_rng(1).uniform(-0.28, 0.28, p)
ax.axvspan(x_star - u_xpt, x_star + u_xpt, color=BLUE, alpha=0.18, lw=0)
ax.axvline(x_star, color=BLUE, lw=1.4)
ax.axvline(np.mean(x), color=MID, lw=0.9, ls=(0, (3, 2)))
ax.plot(x[~out], jit[~out], ls="none", marker="o", ms=4.2, mfc=GREY, mec="white", mew=0.4)
ax.plot(x[out], jit[out], ls="none", marker="o", ms=4.2, mfc="white", mec=ORANGE, mew=1.2)
ax.set_ylim(-0.75, 0.75); ax.set_xlim(42.5, 58); clean(ax, "reported result")
left(1, "Participant results", f"p = {p} laboratories\n" + r"$x_i$ and $u(x_i)$", dy=0.6)
right(1, [("Algorithm A", {"color": MID, "fontsize": 7.8}),
          (rf"$x_{{pt}}$ = $x^*$ = {x_star:.2f}", {"fontweight": "bold"}),
          (rf"$s^*$ = {s_star:.2f}", {"fontweight": "bold"}),
          (rf"$u(x_{{pt}})$ = 1.25$\,s^*/\sqrt{{p}}$ = {u_xpt:.2f}", {"fontweight": "bold"})])

# ---------- 3 sigma_pt ----------
y, h = rows[2]
bg.add_patch(Rectangle((XB0, y), XB1 - XB0, h, fc="white", ec="#5A5A5A", lw=1.0, zorder=2))
bg.plot([XB0, XB1], [y + h, y + h], color="#5A5A5A", lw=2.4, solid_capstyle="butt", zorder=3)
bg.text(XB0 + 1.0, y + h - 1.35, "sigma_pt", fontsize=8.5, fontweight="bold", color=DARK, va="center", family="DejaVu Sans Mono", zorder=4)
bg.text(XB1 - 1.0, y + h - 1.35, "Clause 8", fontsize=7.5, color=MID, va="center", ha="right", zorder=4)
chips = ["expert\nperception", "previous\nrounds", "general\nmodel", "precision\nexperiment", "this round's\ndata"]
cw = (XB1 - XB0 - 2.0 - 4 * 0.8) / 5
for k, c in enumerate(chips):
    x0 = XB0 + 1.0 + k * (cw + 0.8); sel = k == 0
    bg.add_patch(FancyBboxPatch((x0, y + 0.9), cw, 3.6, boxstyle="round,pad=0,rounding_size=0.5", fc=BLUE if sel else LIGHT,
                                ec="none", zorder=3))
    bg.text(x0 + cw / 2, y + 2.7, c, ha="center", va="center", fontsize=5.5, color="white" if sel else DARK, zorder=4,
            linespacing=1.05, fontweight="bold" if sel else "normal")
left(2, "Fitness criterion", "set by the PT provider")
right(2, [(rf"$\sigma_{{pt}}$ = {sigma_pt:.2f}", {"fontweight": "bold"}),
          ("fixed before the round", {"color": MID, "fontsize": 7.8})])

# ---------- 4 scores ----------
ax = box(3, "scores", "Clause 9")
zs = z[order]; cs = [zcol(cls[i]) for i in order]
ax.bar(range(1, p + 1), zs, color=cs, width=0.72, lw=0)
for lim, ls in ((2, (0, (3, 2))), (3, "-")):
    for sgn in (-1, 1): ax.axhline(sgn * lim, color=MID, lw=0.6, ls=ls)
ax.axhline(0, color=DARK, lw=0.6)
ax.set_ylim(-5, 5); ax.set_xlim(0.2, p + 0.8); ax.set_xticks([])
for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
ax.spines["left"].set_color(MID); ax.set_yticks([-3, 0, 3]); ax.patch.set_alpha(0)
ax.tick_params(axis="y", labelsize=6.5, length=2, width=0.5, pad=1.5, colors=MID)
ax.set_xlabel("laboratories, ordered by score", fontsize=6.8, color=MID, labelpad=2)
left(3, "Scoring", r"$z$, $z'$, $\zeta$, $E_n$, $D$, $D_\%$, $P_A$")
nA = sum(c == "action" for c in cls); nW = sum(c == "warning" for c in cls)
right(3, [(rf"$u(x_{{pt}})$ < 0.3$\,\sigma_{{pt}}$ = {0.3*sigma_pt:.2f}, so $z$ is used", {"color": MID, "fontsize": 7.8}),
          (f"{p - nA - nW} acceptable", {"color": BLUE, "fontweight": "bold"}),
          (f"{nW} warning signal  (2 < |z| < 3)", {"color": "#C98A5E", "fontweight": "bold"}),
          (f"{nA} action signals  (|z| ≥ 3)", {"color": ORANGE, "fontweight": "bold"})])

# ---------- 5 graphics ----------
ax = box(4, "graphics", "Clause 10")
ax.fill_between(kd_x, kd_y, color=BLUE, alpha=0.18, lw=0); ax.plot(kd_x, kd_y, color=BLUE, lw=1.2)
ax.plot(x, np.full(p, -0.012), ls="none", marker="|", ms=5, mew=0.9, color=DARK)
ax.set_ylim(-0.03, max(kd_y) * 1.12); ax.set_xlim(42.5, 58); clean(ax, "reported result")
left(4, "Review", "shape of the distribution")
right(4, [("kernel density plot", {"fontweight": "bold"}),
          (f"bandwidth {bw:.2f}", {"color": MID, "fontsize": 7.8}),
          ("one main mode,", {"color": MID, "fontsize": 7.8}), ("two detached results", {"color": MID, "fontsize": 7.8})])

# ---------- arrows ----------
def arr(x0, y0, x1, y1, col=DARK, lw=1.3):
    bg.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, lw=lw, color=col,
                                 shrinkA=0, shrinkB=0, zorder=6))
xm = (XB0 + XB1) / 2
seq = ["sig", "hom", "av", "sc", "gr"]
for a, b in zip(seq[:-1], seq[1:]):
    arr(xm, R[a][0], xm, R[b][0] + R[b][1] + 0.35)
# result of step 1 (sigma_pt needed by criterion) is shown by a side note, not an arrow, to keep the flow simple

# ---------- legend ----------
ly = 10.6
def lg(xx, yy, kind, txt):
    if kind == "dot": bg.plot(xx + 0.8, yy, marker="o", ms=4.6, mfc=GREY, mec="white", mew=0.4, ls="none")
    elif kind == "out": bg.plot(xx + 0.8, yy, marker="o", ms=4.6, mfc="white", mec=ORANGE, mew=1.2, ls="none")
    elif kind == "band":
        bg.add_patch(Rectangle((xx, yy - 0.75), 1.6, 1.5, fc=BLUE, alpha=0.18, ec="none")); bg.plot([xx + 0.8] * 2, [yy - 0.75, yy + 0.75], color=BLUE, lw=1.4)
    elif kind == "mean": bg.plot([xx + 0.8] * 2, [yy - 0.75, yy + 0.75], color=MID, lw=0.9, ls=(0, (3, 2)))
    elif kind == "lim": bg.plot([xx, xx + 1.6], [yy + 0.35] * 2, color=MID, lw=0.6); bg.plot([xx, xx + 1.6], [yy - 0.35] * 2, color=MID, lw=0.6, ls=(0, (3, 2)))
    else: bg.add_patch(Rectangle((xx, yy - 0.75), 1.6, 1.5, fc=kind, ec="none"))
    bg.text(xx + 2.6, yy, txt, va="center", fontsize=7.8, color=DARK)
lg(2, ly, "dot", "reported result");            lg(34, ly, "band", r"$x_{pt}$ ± $u(x_{pt})$");      lg(66, ly, BLUE, "acceptable")
lg(2, ly - 2.6, "out", "result with action signal"); lg(34, ly - 2.6, "mean", "arithmetic mean");  lg(66, ly - 2.6, "#F2B78F", "warning signal")
lg(34, ly - 5.2, "lim", "action (±3) and warning (±2) limits"); lg(66, ly - 5.2, ORANGE, "action signal")
bg.plot(2.8, ly - 5.2, marker="_", ms=8, mew=1.3, color=DARK); bg.text(4.6, ly - 5.2, "item mean", va="center", fontsize=7.8, color=DARK)

bg.add_patch(FancyBboxPatch((1.5, 0.8), 97, 3.4, boxstyle="round,pad=0,rounding_size=0.6", fc="#F8F8F8", ec="#BDBDBD", lw=0.8))
bg.text(3, 2.5, "Simulated round for illustration (p = 20); every number shown is computed with pt13528 " + __import__("pt13528").__version__ + ".", va="center", fontsize=7.8, color=DARK)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(HERE, f"Figure_2.{ext}"), dpi=300, facecolor="white")
