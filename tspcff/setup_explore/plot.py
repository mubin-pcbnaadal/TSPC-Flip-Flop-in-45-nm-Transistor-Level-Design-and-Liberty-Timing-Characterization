#!/usr/bin/python
# -*- coding: utf-8 -*-
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys

Title = sys.argv[1] if len(sys.argv) > 1 else "TSPCFF setup exploration"

# columns : setup(ns)  cell_rise(ns)  setup+cell_rise(ns)
tab = np.genfromtxt('results/TSPCFF_setup_explore.dat', skip_header=1)
tab = np.atleast_2d(tab)

ok   = tab[:,1] >= 0          # points where Q was captured
fail = ~ok

setup = tab[:,0] * 1000.0     # ps
tprop = tab[:,1] * 1000.0     # ps
tsum  = tab[:,2] * 1000.0     # ps

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# Left : propagation time vs setup time
ax1.plot(setup[ok], tprop[ok], 'o-', label='CK->Q (cell_rise)')
for s in setup[fail]:
    ax1.axvline(s, color='red', ls=':', lw=1)
ax1.set_xlabel('Setup time (ps)')
ax1.set_ylabel('CK to Q rise propagation time (ps)')
ax1.set_title(Title + ' : Tprop vs Tsetup')
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right')

# Right : Tprop + Tsetup vs setup time (minimum = best clock period)
ax2.plot(setup[ok], tsum[ok], 'o-', color='tab:green', label='Tprop + Tsetup')
if ok.any():
    i = np.argmin(np.where(ok, tsum, np.inf))
    ax2.plot(setup[i], tsum[i], 'r*', markersize=14,
             label='min : %.1f ps at Tsetup = %.0f ps' % (tsum[i], setup[i]))
    print("Minimum Tprop+Tsetup = %.2f ps at Tsetup = %.1f ps (Tprop = %.2f ps)"
          % (tsum[i], setup[i], tprop[i]))
for s in setup[fail]:
    ax2.axvline(s, color='red', ls=':', lw=1)
ax2.set_xlabel('Setup time (ps)')
ax2.set_ylabel('Tprop + Tsetup (ps)')
ax2.set_title(Title + ' : Tprop + Tsetup')
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper right')

if fail.any():
    print("Capture failed for setup times (ps):", setup[fail])

plt.tight_layout()
plt.show()
