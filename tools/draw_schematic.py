#!/usr/bin/env python3
"""Draw the TSPC D flip-flop transistor schematic -> docs/figures/tspcff_schematic.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "figures", "tspcff_schematic.png")

INK = "#1f2328"; ACC = "#0969da"; MUT = "#59636e"
LW = 1.6
fig, ax = plt.subplots(figsize=(13, 7.4))
ax.set_aspect("equal"); ax.axis("off")

def L(*pts, c=INK, lw=LW):
    xs, ys = zip(*pts); ax.plot(xs, ys, color=c, lw=lw, solid_capstyle="round")

def dot(p, c=INK): ax.add_patch(Circle(p, 0.07, color=c, zorder=5))

def T(p, s, **kw):
    kw.setdefault("color", INK); kw.setdefault("fontsize", 11)
    ax.text(p[0], p[1], s, **kw)

def fet(x, ytop, kind, name, gate=None):
    """Conduction path on column x, from ytop to ytop-2. Returns gate lead end (x,y)."""
    yb = ytop - 2.0; yc = ytop - 1.0
    L((x, ytop), (x, yc + 0.4), (x - 0.45, yc + 0.4))
    L((x, yb), (x, yc - 0.4), (x - 0.45, yc - 0.4))
    L((x - 0.45, yc - 0.55), (x - 0.45, yc + 0.55), lw=2.2)          # channel
    L((x - 0.62, yc - 0.4), (x - 0.62, yc + 0.4), lw=2.2)            # gate plate
    if kind == "P":
        ax.add_patch(Circle((x - 0.74, yc), 0.12, fill=False, ec=INK, lw=LW))
        L((x - 0.86, yc), (x - 1.4, yc))
    else:
        L((x - 0.62, yc), (x - 1.4, yc))
    T((x + 0.12, yc - 0.1), name, color="#cf222e", fontsize=10)
    if gate:
        T((x - 1.5, yc), gate, ha="right", va="center", color=ACC)
    return (x - 1.4, yc)

TOP, BOT = 9.0, -0.5
X = [3.5, 8.0, 12.5]
# rails
L((1.6, TOP), (14.2, TOP)); L((1.6, BOT), (14.2, BOT))
T((7.6, TOP + 0.25), "VDD", fontsize=12, fontweight="bold")
T((7.6, BOT - 0.55), "VSS", fontsize=12, fontweight="bold")

def node(p, name, dx=0.15):
    dot(p); T((p[0] + dx, p[1] + 0.12), name, fontsize=11, fontweight="bold")

# ---- stage 1 : MP1 (D) | MN4 (CKb) | MN1 (D)
x = X[0]
gMP1 = fet(x, TOP, "P", "MP1")
L((x, TOP - 2), (x, TOP - 2.6)); px = (x, TOP - 2.3); node(px, "x")
gMN4 = fet(x, TOP - 2.6, "N", "MN4", "CKb")
L((x, TOP - 4.6), (x, TOP - 5.2)); node((x, TOP - 4.9), "a")
gMN1 = fet(x, TOP - 5.2, "N", "MN1")
L((x, TOP - 7.2), (x, BOT))
# D input
xd = gMP1[0] - 1.5
L(gMP1, (xd, gMP1[1]), (xd, gMN1[1]), gMN1)
dot((xd, (gMP1[1] + gMN1[1]) / 2))
L((xd, (gMP1[1] + gMN1[1]) / 2), (xd - 0.6, (gMP1[1] + gMN1[1]) / 2))
T((xd - 0.75, (gMP1[1] + gMN1[1]) / 2), "D", ha="right", va="center", fontsize=13, fontweight="bold")

# ---- stage 2 : MP2 (CKb) | MP4 (x) | MN2 (CKb)
x = X[1]
fet(x, TOP, "P", "MP2", "CKb")
L((x, TOP - 2), (x, TOP - 2.6)); node((x, TOP - 2.3), "b")
gMP4 = fet(x, TOP - 2.6, "P", "MP4")
L((x, TOP - 4.6), (x, TOP - 5.2)); py = (x, TOP - 4.9); node(py, "y")
fet(x, TOP - 5.2, "N", "MN2", "CKb")
L((x, TOP - 7.2), (x, BOT))
# x -> gate MP4
xr = gMP4[0] - 0.5
L(px, (xr, px[1]), (xr, gMP4[1]), gMP4)

# ---- stage 3 : MP3 (y) | MP5 (CKb) | MN3 (y)
x = X[2]
gMP3 = fet(x, TOP, "P", "MP3")
L((x, TOP - 2), (x, TOP - 2.6)); node((x, TOP - 2.3), "c")
fet(x, TOP - 2.6, "P", "MP5", "CKb")
L((x, TOP - 4.6), (x, TOP - 5.2)); pqb = (x, TOP - 4.9); node(pqb, "Qb")
gMN3 = fet(x, TOP - 5.2, "N", "MN3")
L((x, TOP - 7.2), (x, BOT))
# y -> gates MP3, MN3
xy = gMP3[0] - 1.6
L(py, (xy, py[1])); dot((xy, py[1]))
L((xy, gMP3[1]), (xy, gMN3[1])); L((xy, gMP3[1]), gMP3); L((xy, gMN3[1]), gMN3)

def inverter(p, label, sizes, out_name, in_name=None, above=True):
    x0, y0 = p
    ax.add_patch(Polygon([(x0, y0 + 0.45), (x0, y0 - 0.45), (x0 + 0.8, y0)], closed=True,
                         fill=False, ec=INK, lw=LW))
    ax.add_patch(Circle((x0 + 0.92, y0), 0.12, fill=False, ec=INK, lw=LW))
    L((x0 + 1.04, y0), (x0 + 1.7, y0))
    T((x0 + 1.8, y0), out_name, va="center", fontsize=12, fontweight="bold")
    if above:
        T((x0 + 0.4, y0 + 0.6), f"{label}  WN/WP = {sizes}", ha="center", va="bottom", fontsize=9, color=MUT)
    else:
        T((x0 + 0.6, y0 - 0.6), f"{label}  WN/WP = {sizes}", ha="left", va="top", fontsize=9, color=MUT)
    if in_name:
        L((x0 - 0.7, y0), (x0, y0))
        T((x0 - 0.8, y0), in_name, ha="right", va="center", fontsize=12, fontweight="bold")

# output inverter
L(pqb, (pqb[0] + 1.2, pqb[1]))
inverter((pqb[0] + 1.2, pqb[1]), "INV_Q", "260n/390n", "Q", above=False)
# clock inverter (drawn apart)
inverter((0.6, TOP + 1.3), "INV_CK", "145n/215n", "CKb", in_name="CK")

T((7.1, BOT - 1.3),
  "Core transistors : NMOS g45n1svt W = 145 nm, PMOS g45p1svt W = 214 nm, L = 45 nm   |   bulks : PMOS->VDD, NMOS->VSS",
  ha="center", fontsize=9.5, color=MUT)
ax.set_xlim(-1.4, 16.6); ax.set_ylim(BOT - 1.7, TOP + 2.4)
fig.tight_layout()
fig.savefig(OUT, dpi=150, facecolor="white")
print("wrote", OUT)
