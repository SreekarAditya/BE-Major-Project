"""Figures for the retrofit simulation (650 dpi): decision map and scheme success rate."""
import csv, json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
for f in fm.findSystemFonts():
    if 'Carlito' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family': 'Carlito', 'font.size': 20, 'axes.labelsize': 20, 'xtick.labelsize': 18, 'ytick.labelsize': 18,
                     'axes.edgecolor': '#8A8A8A', 'xtick.color': '#444444', 'ytick.color': '#444444', 'axes.labelcolor': '#222222',
                     'savefig.dpi': 650})
GRID = '#E6E6E6'
COL = {'Monitor': '#9E9E9E', 'Seal cracks': '#C9A227', 'Polymer laminate': '#8E1B2E', 'Steel plate': '#4A6C8C', 'Concrete jacket': '#2E6B35'}
R = list(csv.DictReader(open('retrofit_sim.csv')))
def clean(a):
    a.grid(color=GRID, lw=1); a.set_axisbelow(True)
    for s in ('top', 'right'): a.spines[s].set_visible(False)

# ---- Fig. 5: decision map
fig, a = plt.subplots(figsize=(6.4, 5.6)); clean(a)
fig.subplots_adjust(left=0.14, right=0.97, top=0.97, bottom=0.36)
rng = np.random.default_rng(1)
for lab in ('Monitor', 'Seal cracks', 'Polymer laminate', 'Steel plate', 'Concrete jacket'):
    sub = [r for r in R if r['best'] == lab]
    x = np.array([float(r['strength_ratio']) for r in sub]); y = np.array([float(r['crack_ratio']) for r in sub])
    a.scatter(x, y, s=(9 if len(R) <= 3000 else 4) if lab != 'Concrete jacket' else (40 if len(R) <= 3000 else 24), color=COL[lab], alpha=(0.65 if len(R) <= 3000 else 0.5) if lab != 'Concrete jacket' else 1, lw=0,
              label=f'{lab} ({len(sub)})', marker='o' if lab != 'Concrete jacket' else 'D')
a.axvline(1.0, color='#444444', lw=1.2, ls='--'); a.axhline(1.0, color='#444444', lw=1.2, ls='--')
a.set_xlim(0.8, 1.65); a.set_ylim(0, 6); a.set_xlabel('Moment demand / capacity, before retrofit'); a.set_ylabel('Crack width / IS 456 limit')
a.legend(frameon=False, fontsize=16, loc='upper center', bbox_to_anchor=(0.45, -0.2), ncol=2, markerscale=2.2, handletextpad=0.2, columnspacing=0.6)
a.set_xticks([0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]); a.set_xticklabels(['0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6'])
fig.savefig('retrofit_decision_map.png', facecolor='white'); plt.close(fig)

# ---- Fig. 6: success rate of each scheme against the strength increase needed
need = [r for r in R if float(r['strength_ratio']) > 1]
edges = np.array([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]); mid = 100 * (0.5 * (edges[1:] + edges[:-1]) - 1)
fig, a = plt.subplots(figsize=(6.4, 5.6)); clean(a)
for key, lab in (('jacket', 'Concrete jacket'), ('plate', 'Steel plate'), ('polymer', 'Polymer laminate')):
    rate = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sub = [r for r in need if lo < float(r['strength_ratio']) <= hi]
        rate.append(100 * np.mean([r[key + '_ok'] == 'True' for r in sub]) if sub else np.nan)
    a.plot(mid, rate, '--s' if key == 'jacket' else '-o', color=COL[lab], lw=3, ms=9, mec='white', mew=2, label=lab, zorder=4 if key == 'jacket' else 3)
a.set_ylim(50, 103); a.set_xlim(0, 60); a.set_xticks(mid)
ns = [sum(lo < float(r['strength_ratio']) <= hi for r in need) for lo, hi in zip(edges[:-1], edges[1:])]
a.set_xticklabels([f'{int(round(100*(lo-1)))}–{int(round(100*(hi-1)))}\n{n}' for lo, hi, n in zip(edges[:-1], edges[1:], ns)], fontsize=15.5)
a.set_xlabel('Strength increase needed (%); beams per bin'); a.set_ylabel('Beams where it complies (%)')
a.legend(frameon=False, fontsize=18, loc='lower left')
fig.tight_layout(); fig.savefig('retrofit_success_rate.png', facecolor='white'); plt.close(fig)
print('ok', len(need))
