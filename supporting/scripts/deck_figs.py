"""Clean, presentation-sized charts for the Review 2 deck.
Each figure is drawn at the exact size it occupies on the slide, so 18 pt text here is 18 pt on screen."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from p import *

for f in fm.findSystemFonts():
    if 'Carlito' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family': 'Carlito', 'font.size': 18, 'axes.titlesize': 18, 'axes.labelsize': 18,
                     'xtick.labelsize': 16, 'ytick.labelsize': 16, 'axes.edgecolor': '#8A8A8A', 'axes.linewidth': 1.0,
                     'xtick.color': '#444444', 'ytick.color': '#444444', 'axes.labelcolor': '#222222',
                     'savefig.dpi': 650, 'figure.dpi': 220})
INK, MUTED, GRID, ACC, SEC = '#222222', '#7A7A7A', '#E6E6E6', '#8E1B2E', '#4A6C8C'
OUT = '../ppt/'

def clean(a):
    a.grid(axis='y', color=GRID, lw=1); a.set_axisbelow(True)
    for s in ('top', 'right'): a.spines[s].set_visible(False)

F = json.load(open('fibre.json')); D = json.load(open('cont230.json')); C = json.load(open('calc.json'))

# ---------- 1. load-deflection (8.2 x 5.0 in)
fig, a = plt.subplots(figsize=(8.2, 5.0)); clean(a)
fb = F['bare']; a.plot(fb['D'], fb['P'], color=ACC, lw=3)
a.plot(D['D'], D['P'], color=SEC, lw=3)
br = np.array(C['deflection_curves']); a.plot(br[:, 1], br[:, 0], color=MUTED, lw=2.2, ls='--')
for y, t, xx, ha in ((82, 'Expected capacity 82 kN', 0.3, 'left'), (70, 'IS 456 design 70 kN', 0.3, 'left'), (26.5, 'Cracking 26.5 kN', 19.8, 'right')):
    a.axhline(y, color='#B0B0B0', lw=1.2, ls=':'); a.text(xx, y + 1.5, t, ha=ha, va='bottom', fontsize=15, color=MUTED)
a.text(13.2, 93.5, 'Fibre model', color=ACC, fontsize=17, fontweight='bold')
a.text(12.6, 62, 'Continuum model', color=SEC, fontsize=17, fontweight='bold', ha='left')
a.text(6.6, 45, 'Hand (Branson)', color=MUTED, fontsize=17, fontweight='bold')
a.set_xlim(0, 20); a.set_ylim(0, 102); a.set_xlabel('Midspan deflection (mm)'); a.set_ylabel('Total load (kN)')
fig.tight_layout(); fig.savefig(OUT + 'c_load_deflection.png', facecolor='white'); plt.close(fig)

# ---------- 2. damage stages: stiffness remaining (8.2 x 5.0 in)
R = F['twin']['rows']; f0 = R[0]['f']; d0 = R[0]['delta_d']
lab = ['Undamaged'] + [f"{r['damage']:.0f} kN" for r in R[1:]]
ks = [100 * d0 / r['delta_d'] for r in R]; kf = [100 * (r['f'] / f0) ** 2 for r in R]
fig, a = plt.subplots(figsize=(8.2, 5.0)); clean(a); x = np.arange(len(R))
a.plot(x, ks, color=ACC, lw=3, marker='o', ms=9, mec='white', mew=2)
a.plot(x, kf, color=SEC, lw=3, marker='o', ms=9, mec='white', mew=2)
for i in (0, len(R) - 1):
    a.annotate(f'{ks[i]:.0f}%', (x[i], ks[i]), xytext=(0, 12), textcoords='offset points', ha='center', fontsize=16, color=ACC, fontweight='bold')
a.annotate(f'{kf[-1]:.0f}%', (x[-1], kf[-1]), xytext=(0, -26), textcoords='offset points', ha='center', fontsize=16, color=SEC, fontweight='bold')
a.text(0.4, 70, 'From deflection', color=ACC, fontsize=17, fontweight='bold')
a.text(2.25, 88, 'From frequency', color=SEC, fontsize=17, fontweight='bold')
a.set_xticks(x); a.set_xticklabels(lab); a.set_ylim(0, 112); a.set_xlim(-0.3, len(R) - 0.7)
a.set_xlabel('Highest load applied so far'); a.set_ylabel('Stiffness remaining (%)')
fig.tight_layout(); fig.savefig(OUT + 'c_damage.png', facecolor='white'); plt.close(fig)

# ---------- 3. twin prediction error (8.2 x 5.0 in), same method as figs_b.py
Pd, Ps = F['twin']['Pd'], F['twin']['Ps']
C_ = lambda P: (P * 1e3 / 2) * a_ * (3 * span ** 2 - 4 * a_ ** 2) / 24
import p as PP; a_ = PP.a
EI0 = C_(Pd) / R[0]['delta_d']; sf, sd, sm, snl, sl = 0.3, 0.01, 0.10, 0.03, 0.02
rows = R[1:]; truth = [r['delta_s'] for r in rows]
err = {k: [] for k in ('No updating', 'Vibration only', 'Static only', 'Combined')}
for r, tr in zip(rows, truth):
    lv = np.log(EI0) + 2 * np.log(r['f'] / f0); vv = (2 * sf / r['f']) ** 2 + (2 * sf / f0) ** 2 + sm ** 2
    ls_ = np.log(C_(Pd) / r['delta_d']); vs = (sd / r['delta_d']) ** 2 + sl ** 2 + snl ** 2
    w = np.array([1 / vv, 1 / vs]); lc = (w @ [lv, ls_]) / w.sum()
    for k, l in zip(err, (np.log(EI0), lv, ls_, lc)):
        err[k].append(100 * (np.exp(np.log(C_(Ps)) - l) / tr - 1))
fig, a2 = plt.subplots(figsize=(8.2, 5.0)); clean(a2); x = np.arange(len(rows))
sty = {'No updating': (MUTED, 2.2, '--'), 'Vibration only': (SEC, 2.2, '-'), 'Static only': ('#B0B0B0', 2.2, '-'), 'Combined': (ACC, 3.4, '-')}
for k, v in err.items():
    c, lw, ls = sty[k]; a2.plot(x, v, color=c, lw=lw, ls=ls, marker='o', ms=8 if k == 'Combined' else 6, mec='white', mew=1.5)
a2.axhline(0, color='#555555', lw=1.2)
a2.text(x[-1] + 0.1, err['No updating'][-1], 'No updating', color=MUTED, fontsize=16, va='center', fontweight='bold')
a2.text(x[-1] + 0.1, err['Vibration only'][-1] - 2.5, 'Vibration only', color=SEC, fontsize=16, va='center', fontweight='bold')
a2.text(x[-1] + 0.1, 4.5, 'Combined', color=ACC, fontsize=16, va='center', fontweight='bold')
a2.text(x[-1] + 0.1, -0.2 + 11, 'Static only', color='#9A9A9A', fontsize=16, va='center', fontweight='bold')
a2.set_xticks(x); a2.set_xticklabels([f"{r['damage']:.0f} kN" for r in rows]); a2.set_xlim(-0.25, len(rows) - 1 + 1.35)
a2.set_ylim(-62, 16); a2.set_xlabel('Damage stage'); a2.set_ylabel('Prediction error (%)')
fig.tight_layout(); fig.savefig(OUT + 'c_twin.png', facecolor='white'); plt.close(fig)
print({k: [round(e, 1) for e in v] for k, v in err.items()})

# ---------- 4. repair capacity (8.2 x 5.0 in)
names = ['Unstrengthened', 'Fibre-reinforced\npolymer', 'Steel plate', 'Concrete\njacket']
rep = C['repairs']; des = [C['bare']['P_design']] + [rep[k]['P_design'] for k in ('Fibre-reinforced polymer strips', 'Bonded steel plate', 'Concrete jacket')]
exp_ = [C['bare']['P_expected']] + [rep[k]['P_expected'] for k in ('Fibre-reinforced polymer strips', 'Bonded steel plate', 'Concrete jacket')]
fig, a3 = plt.subplots(figsize=(8.2, 5.0)); clean(a3); x = np.arange(4); w = 0.36
b1 = a3.bar(x - w / 2, des, w, color='#C9C9C9'); b2 = a3.bar(x + w / 2, exp_, w, color=[MUTED] + [ACC] * 3)
for b, v in list(zip(b1, des)) + list(zip(b2, exp_)):
    a3.text(b.get_x() + b.get_width() / 2, v + 2, f'{v:.0f}', ha='center', va='bottom', fontsize=16, color=INK)
a3.set_xticks(x); a3.set_xticklabels(names, fontsize=16); a3.set_ylim(0, 180); a3.set_ylabel('Load capacity (kN)')
a3.text(-0.45, 168, 'Grey: IS 456 design', fontsize=16, color=MUTED); a3.text(1.55, 168, 'Dark: expected (mean strengths)', fontsize=16, color=ACC)
fig.tight_layout(); fig.savefig(OUT + 'c_repair.png', facecolor='white'); plt.close(fig)

# ---------- 5. stress and cracks at 76 kN (12.3 x 4.4 in)
xs = np.array(D['xs']); ys = np.array(D['ys']); nx, ny = len(xs) - 1, len(ys) - 1
nid = lambda i, j: j * (nx + 1) + i
X0 = np.array([[xx, yy] for yy in ys for xx in xs])
def quads(U, sc):
    P = X0 + sc * np.array(U); return [[P[nid(i, j)], P[nid(i + 1, j)], P[nid(i + 1, j + 1)], P[nid(i, j + 1)]] for j in range(ny) for i in range(nx)]
div = LinearSegmentedColormap.from_list('d', ['#1F3B57', '#4A6C8C', '#C9D6E2', '#F5F5F5', '#E8B9C0', '#B5475A', '#8E1B2E'])
s = D['snaps'][2]
fig, (t, b) = plt.subplots(2, 1, figsize=(12.3, 4.6), gridspec_kw={'hspace': 0.35})
pc = PolyCollection(quads(s['U'], 8), array=np.array(s['E'])[:, 0], cmap=div, norm=TwoSlopeNorm(vmin=-30, vcenter=0, vmax=4), edgecolors='none')
t.add_collection(pc); t.autoscale_view(); t.set_aspect(1); t.axis('off')
t.set_title('Longitudinal stress (MPa): compression blue, tension red', loc='left', fontsize=18, color=INK)
cb = fig.colorbar(pc, ax=t, fraction=0.025, pad=0.01, ticks=[-30, -15, 0, 4]); cb.ax.tick_params(labelsize=14); cb.outline.set_visible(False)
E = np.array(s['E']); segs = []; ws = []
for j in range(ny):
    for i in range(nx):
        sx, sy, txy, dm = E[j * nx + i]
        if dm < 0.3: continue
        th = 0.5 * np.arctan2(2 * txy, sx - sy); cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2; hh = min(xs[i + 1] - xs[i], ys[j + 1] - ys[j]) * 0.55
        dx, dy = -np.sin(th), np.cos(th); segs.append([[cx - hh * dx, cy - hh * dy], [cx + hh * dx, cy + hh * dy]]); ws.append(0.8 + 2.4 * dm)
b.add_patch(plt.Rectangle((0, 0), span, h, fc='#F2F2F2', ec='#8A8A8A', lw=1)); b.add_collection(LineCollection(segs, colors=ACC, linewidths=ws))
for xp in (1000, 2000): b.plot([xp], [h + 25], marker='v', ms=12, color=INK, clip_on=False)
for x_ in (0, span): b.plot([x_], [-30], marker='^', ms=13, color=INK, clip_on=False)
b.set_xlim(-60, span + 60); b.set_ylim(-60, h + 60); b.set_aspect(1); b.axis('off')
b.set_title('Crack pattern: flexural cracks between the load points', loc='left', fontsize=18, color=INK)
fig.savefig(OUT + 'c_stress_cracks.png', facecolor='white', bbox_inches='tight'); plt.close(fig)
print('done', round(s['P'], 1))
