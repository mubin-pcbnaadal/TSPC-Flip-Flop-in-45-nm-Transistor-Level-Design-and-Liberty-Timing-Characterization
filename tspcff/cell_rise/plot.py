#!/usr/bin/python
# -*- coding: utf-8 -*-
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys

Title = sys.argv[1] if len(sys.argv) > 1 else "TSPCFF cell_rise"

# Read results from the simulation
tab = np.genfromtxt('results/TSPCFF_cell_rise.dat', skip_header=1)

# Loop on each clock slope
for islope in range(0, tab.shape[0]):
    ltab = tab[islope]
    label = "CK slope " + str(ltab[0]) + " ns"
    ltab = np.delete(ltab, 0)
    xtab = ltab[0::2]   # load capacitor values
    ytab = ltab[1::2]   # CK->Q rise propagation time
    plt.plot(xtab, ytab, 'o-', label=label)

plt.title(Title)
plt.xlabel('Load capacitor (ff)')
plt.ylabel(r'CK to Q rise propagation time (ns)')
plt.grid(True, alpha=0.3)
legend = plt.legend(loc='upper left', shadow=True)

plt.show()
