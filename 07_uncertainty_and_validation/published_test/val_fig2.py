"""Chart: published measurements (both beams, digitised, with reading uncertainty) against the blind model prediction."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'Carlito' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family': 'Carlito', 'font.size': 18, 'xtick.labelsize': 16, 'ytick.labelsize': 16, 'axes.edgecolor': '#8A8A8A'})
ACC, SEC, MUTED, GRID = '#8E1B2E', '#4A6C8C', '#7A7A7A', '#E6E6E6'
D = json.load(open('fig22_digitised.json')); U = D['reading_uncertainty_MNm2']; F = np.array(D['dyn_BI1']['F'])
V = json.load(open('../musial_val.json'))['BI_model']
L = np.array([0, 12, 15, 20, 25, 30, 35, 40, 44.5])
fig, ax = plt.subplots(figsize=(7.4, 4.7)); ax.grid(axis='y', color=GRID); ax.set_axisbelow(True)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
for kind, col, mk in (('dyn', SEC, 'o'), ('sta', ACC, 's')):
    for b, dx in (('BI1', -0.5), ('BI2', 0.5)):
        p = D[kind + '_' + b]['plateau']; y = np.array([p if x < 12.5 else np.interp(x, F, D[kind + '_' + b]['EI']) for x in L])
        ax.errorbar(L + dx, 100 * y / p, yerr=100 * U / p, fmt=mk, color=col, ms=7, mec='white', mew=1.2, elinewidth=1.2, capsize=0, label=('Test, vibration (2 beams)' if kind == 'dyn' else 'Test, deflection (2 beams)') if b == 'BI1' else None)
Fm = [0] + [r['F'] for r in V if r['F'] > 0]
ax.plot(Fm, [100] + [100 * r['static_left'] for r in V if r['F'] > 0], '-', color=ACC, lw=2.5, label='Model, deflection')
ax.plot(Fm, [100] + [100 * r['dynamic_left'] for r in V if r['F'] > 0], '-', color=SEC, lw=2.5, label='Model, vibration')
ax.legend(frameon=False, fontsize=13, loc='center left', bbox_to_anchor=(1.01, 0.5))
ax.set_xlim(0, 46); ax.set_ylim(40, 105); ax.set_xticks([0, 15, 30, 45])
ax.set_xlabel('Load reached (kN)'); ax.set_ylabel('Stiffness remaining (%)')
fig.tight_layout(); fig.subplots_adjust(right=0.62)
fig.savefig('val_musial2.png', dpi=650, facecolor='white'); print('ok')
