"""Chart: published test (Musial et al. 2021, beams B-I) against blind model prediction, stiffness remaining vs load."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'Carlito' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family': 'Carlito', 'font.size': 18, 'xtick.labelsize': 16, 'ytick.labelsize': 16, 'axes.edgecolor': '#8A8A8A'})
ACC, SEC, MUTED, GRID = '#8E1B2E', '#4A6C8C', '#7A7A7A', '#E6E6E6'
R = json.load(open('musial_val.json'))
T = R['BI_test']; M = [r for r in R['BI_model'] if r['F'] > 0]
Ft = np.array(T['F']); ts = 100 * np.array(T['EIs']) / T['EIs'][0]; td = 100 * np.array(T['EId']) / T['EId'][0]
Fm = np.array([0] + [r['F'] for r in M]); ms = 100 * np.array([1] + [r['static_left'] for r in M]); md = 100 * np.array([1] + [r['dynamic_left'] for r in M])
fig, ax = plt.subplots(figsize=(6.0, 4.7))
ax.grid(axis='y', color=GRID); ax.set_axisbelow(True)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
ax.plot(Ft, td, 'o', color=SEC, ms=9, mec='white', mew=1.5); ax.plot(Fm, md, '-', color=SEC, lw=2.5)
ax.plot(Ft, ts, 's', color=ACC, ms=9, mec='white', mew=1.5); ax.plot(Fm, ms, '-', color=ACC, lw=2.5)
ax.text(46, td[-1], 'Test, vibration', color=SEC, fontsize=15, va='center', fontweight='bold')
ax.text(46, md[-1] + 1, 'Model, vibration', color=SEC, fontsize=15, va='center')
ax.text(46, ts[-1] - 4, 'Deflection', color=ACC, fontsize=15, va='center', fontweight='bold')
ax.set_xlim(0, 45.5); ax.set_ylim(40, 105); ax.set_xticks([0, 15, 30, 45])
ax.set_xlabel('Load reached (kN)'); ax.set_ylabel('Stiffness remaining (%)')
ax.text(1, 42, 'Markers: test    Lines: model', color=MUTED, fontsize=14)
fig.tight_layout(); fig.subplots_adjust(right=0.70)
fig.savefig('val_musial.png', dpi=220, facecolor='white')
print('test 45 kN: static %.0f%% dynamic %.0f%% | model static %.0f%% dynamic %.0f%%' % (ts[-1], td[-1], ms[-1], md[-1]))
