#!/usr/bin/env python3
"""Regenerate every report figure from the .dat files of this repository.

Usage (from the repository root):
    python3 tools/make_figures.py

INV figures are always produced. TSPCFF figures are produced only when
tspcff/results/TSPCFF_cell_rise.dat and/or TSPCFF_setup_explore.dat exist
(copy them from the lab machine, see README).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "docs", "figures")
os.makedirs(FIG, exist_ok=True)

INK, MUTED, GRID = "#1f2328", "#59636e", "#d8dee4"
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 10,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.titleweight": "bold", "axes.titlesize": 11,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "lines.linewidth": 2, "lines.markersize": 5, "legend.frameon": False,
})


def seq_colors(n, cmap="Blues"):
    """One hue, light -> dark (magnitude of the swept slope)."""
    return [plt.get_cmap(cmap)(v) for v in np.linspace(0.35, 0.95, n)]


def read_table(path):
    """Rows: slope, then (load, value) pairs. Returns slopes_ps, loads_fF, values_ps."""
    tab = np.atleast_2d(np.genfromtxt(path, skip_header=1))
    slopes = tab[:, 0] * 1e3
    loads = tab[0, 1::2]
    vals = tab[:, 2::2] * 1e3
    return slopes, loads, vals


def table_plot(path, title, ylabel, out, slope_name="input slope", limit=None):
    s, c, v = read_table(path)
    fig, ax = plt.subplots(figsize=(7, 4.3))
    for col, sl, row in zip(seq_colors(len(s)), s, v):
        ax.plot(c, row, "o-", color=col, label=f"{slope_name} {sl:g} ps")
    if limit is not None:
        ax.axhline(limit, color=MUTED, ls="--", lw=1)
        worst = v[np.argmax(s)]
        k = (worst[-1] - worst[-2]) / (c[-1] - c[-2])
        cmax = c[-1] + (limit - worst[-1]) / k
        ax.annotate(f"max transition {limit:g} ps  ->  max load ~ {cmax:.0f} fF",
                    xy=(c[0], limit), xytext=(0, 5), textcoords="offset points",
                    color=INK, fontsize=9)
        ax.set_ylim(0, limit * 1.12)
    ax.set_xlabel("Load capacitance (fF)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, out))
    plt.close(fig)
    print("wrote", out)
    return s, c, v


inv = os.path.join(ROOT, "inv", "results")
table_plot(os.path.join(inv, "INV_fall_transition.dat"),
           "INV - output fall transition (30%-70%)", "fall_transition (ps)",
           "inv_fall_transition.png", limit=200)
sf, cf, vf = table_plot(os.path.join(inv, "INV_cell_fall.dat"),
                        "INV - cell_fall (A rising 50% -> Y falling 50%)",
                        "cell_fall (ps)", "inv_cell_fall.png")
sr, cr, vr = table_plot(os.path.join(inv, "INV_cell_rise.dat"),
                        "INV - cell_rise (A falling 50% -> Y rising 50%)",
                        "cell_rise (ps)", "inv_cell_rise.png")

# Rise / fall asymmetry : two separate charts would hide the comparison,
# so plot the ratio (one measure, one axis).
fig, ax = plt.subplots(figsize=(7, 4.3))
ratio = vr / vf
for col, sl, row in zip(seq_colors(len(sr)), sr, ratio):
    ax.plot(cr, row, "o-", color=col, label=f"input slope {sl:g} ps")
ax.axhline(1.0, color=MUTED, ls="--", lw=1)
ax.set_xlabel("Load capacitance (fF)")
ax.set_ylabel("cell_rise / cell_fall")
ax.set_title("INV - rise/fall delay asymmetry (PMOS weaker than NMOS)")
ax.legend(loc="upper right", fontsize=8, ncol=2)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "inv_rise_fall_ratio.png"))
plt.close(fig)
print("wrote inv_rise_fall_ratio.png")

# ---- TSPCFF (only if the .dat files have been copied in) ----
tsp = os.path.join(ROOT, "tspcff", "results")
p = os.path.join(tsp, "TSPCFF_cell_rise.dat")
if os.path.exists(p):
    table_plot(p, "TSPCFF - CK->Q cell_rise (CK rising 50% -> Q rising 50%)",
               "CK->Q cell_rise (ps)", "tspcff_cell_rise.png", slope_name="CK slope")

p = os.path.join(tsp, "TSPCFF_setup_explore.dat")
if os.path.exists(p):
    t = np.atleast_2d(np.genfromtxt(p, skip_header=1))
    ok = t[:, 1] >= 0
    su, tp, ts = t[:, 0] * 1e3, t[:, 1] * 1e3, t[:, 2] * 1e3
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
    a1.plot(su[ok], tp[ok], "o-", color=seq_colors(1)[0])
    a1.set_title("TSPCFF - CK->Q delay vs setup time")
    a1.set_ylabel("CK->Q cell_rise (ps)")
    a2.plot(su[ok], ts[ok], "o-", color=seq_colors(1)[0])
    i = np.argmin(np.where(ok, ts, np.inf))
    a2.plot(su[i], ts[i], "*", color=INK, markersize=14)
    a2.annotate(f"min {ts[i]:.1f} ps @ Tsetup {su[i]:.0f} ps", (su[i], ts[i]),
                xytext=(10, 15), textcoords="offset points", color=INK)
    a2.set_title("TSPCFF - Tprop + Tsetup")
    a2.set_ylabel("Tprop + Tsetup (ps)")
    for a in (a1, a2):
        a.set_xlabel("Setup time D->CK (ps)")
        for s_ in su[~ok]:
            a.axvline(s_, color=MUTED, ls=":", lw=1)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "tspcff_setup_explore.png"))
    plt.close(fig)
    print("wrote tspcff_setup_explore.png")
