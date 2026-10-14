"""Statistics of the Monte Carlo runs: stiffness loss bands, twin accuracy with simulated sensor noise,
90 % interval coverage, dynamic-to-static stiffness ratio, rank-correlation sensitivity.
Writes mc_summary.json, mc_samples.csv, mc_twin.csv and three charts."""
import json, csv, math, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from scipy.stats import spearmanr
for f in fm.findSystemFonts():
    if 'Carlito' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family': 'Carlito', 'font.size': 18, 'xtick.labelsize': 16, 'ytick.labelsize': 16, 'axes.edgecolor': '#8A8A8A'})
ACC, SEC, MUTED, GRID = '#8E1B2E', '#4A6C8C', '#7A7A7A', '#E6E6E6'
OUT = 'mc_'

S = [json.loads(l) for l in open('mc_raw_samples.jsonl')]
ok = [s for s in S if s['ok']]
print('samples', len(S), 'converged', len(ok))
stages = [r['damage'] for r in ok[0]['rows']]
span, a, Pd, Ps = 3000.0, 1000.0, 15.0, 30.0
C = lambda P: (P * 1e3 / 2) * a * (3 * span ** 2 - 4 * a ** 2) / 24

# ---------- stiffness remaining (true, noise-free)
ks = np.array([[100 * s['rows'][0]['delta_d'] / r['delta_d'] for r in s['rows']] for s in ok])
kf = np.array([[100 * (r['f'] / s['rows'][0]['f']) ** 2 for r in s['rows']] for s in ok])
f0 = np.array([s['rows'][0]['f'] for s in ok]); Pmax = np.array([s['Pmax'] for s in ok])
q = lambda x: [float(np.percentile(x, p)) for p in (5, 50, 95)]
summary = dict(n_samples=len(S), n_converged=len(ok), f0=q(f0), Pmax=q(Pmax),
               stiffness_left_deflection={str(int(st)): q(ks[:, i]) for i, st in enumerate(stages)},
               stiffness_left_frequency={str(int(st)): q(kf[:, i]) for i, st in enumerate(stages)})

# ---------- twin on every sample with simulated sensor noise
s_f, s_d, s_dyn, s_lin, s_load, z = 0.3, 0.01, 0.10, 0.03, 0.02, 1.645
rng = np.random.default_rng(7)
methods = ('No updating', 'Vibration only', 'Static only', 'Combined')
err = {m: [[] for _ in stages[1:]] for m in methods}; cover = {m: [[] for _ in stages[1:]] for m in methods}
ratio = [[] for _ in stages[1:]]; twin_rows = []
for s in ok:
    R = s['rows']
    fm0 = R[0]['f'] + rng.normal(0, s_f); dm0 = R[0]['delta_d'] + rng.normal(0, s_d)
    EI0 = C(Pd) / dm0
    for j, r in enumerate(R[1:]):
        fmj = r['f'] + rng.normal(0, s_f); dmj = r['delta_d'] + rng.normal(0, s_d)
        lv = math.log(EI0) + 2 * math.log(fmj / fm0); vv = (2 * s_f / fmj) ** 2 + (2 * s_f / fm0) ** 2 + s_dyn ** 2
        ls = math.log(C(Pd) / dmj); vs = (s_d / dmj) ** 2 + s_lin ** 2 + s_load ** 2
        lc = (lv / vv + ls / vs) / (1 / vv + 1 / vs); vc = 1 / (1 / vv + 1 / vs)
        truth = r['delta_s']
        for m, (l, v) in zip(methods, ((math.log(EI0), 0.05 ** 2), (lv, vv), (ls, vs), (lc, vc))):
            mu = math.log(C(Ps)) - l; sd = math.sqrt(v)
            err[m][j].append(100 * (math.exp(mu) / truth - 1))
            cover[m][j].append(math.exp(mu - z * sd) <= truth <= math.exp(mu + z * sd))
        ratio[j].append(math.exp(lv - ls))
        twin_rows.append(dict(sample=s['i'], damage_kN=r['damage'], true_30kN_mm=round(truth, 4),
                              pred_combined_mm=round(math.exp(math.log(C(Ps)) - lc), 4),
                              error_combined_pct=round(err['Combined'][j][-1], 2), error_static_pct=round(err['Static only'][j][-1], 2),
                              error_vibration_pct=round(err['Vibration only'][j][-1], 2), error_no_update_pct=round(err['No updating'][j][-1], 2),
                              dynamic_to_static_EI=round(ratio[j][-1], 3)))
summary['twin'] = {m: {str(int(st)): dict(abs_err_median=float(np.median(np.abs(err[m][j]))), abs_err_p95=float(np.percentile(np.abs(err[m][j]), 95)),
                                           coverage90=float(np.mean(cover[m][j])))
                       for j, st in enumerate(stages[1:])} for m in methods}
summary['dynamic_to_static_EI'] = {str(int(st)): q(ratio[j]) for j, st in enumerate(stages[1:])}

# ---------- sensitivity: Spearman rank correlation
names = {'fck': 'Concrete strength fck', 'Ec': 'Elastic modulus Ec', 'ft': 'Tensile strength ft', 'ets': 'Tension stiffening', 'fy': 'Steel yield fy'}
X = {k: np.array([s['q'][k] for s in ok]) for k in names}
outs = {'f0': f0, 'left72': ks[:, -1], 'Pmax': Pmax}
summary['sensitivity'] = {o: {k: float(spearmanr(X[k], y)[0]) for k in names} for o, y in outs.items()}
json.dump(summary, open('mc_summary.json', 'w'), indent=1)
with open('mc_twin.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(twin_rows[0].keys())); w.writeheader(); w.writerows(twin_rows)
with open('mc_samples.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['sample', 'fck_MPa', 'Ec_MPa', 'ft_MPa', 'tension_stiffening_x_Ec', 'fy_MPa', 'f0_Hz', 'stiffness_left_72kN_pct', 'peak_load_kN'])
    for s, a0, b0, c0 in zip(ok, f0, ks[:, -1], Pmax):
        w.writerow([s['i']] + [round(s['q'][k], 3) for k in ('fck', 'Ec', 'ft', 'ets', 'fy')] + [round(a0, 2), round(b0, 1), round(c0, 1)])

def clean(ax):
    ax.grid(axis='y', color=GRID); ax.set_axisbelow(True)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
labels = ['Undamaged'] + [f'{int(s)} kN' for s in stages[1:]]; x = np.arange(len(stages))
# chart 1: stiffness bands
fig, ax = plt.subplots(figsize=(6.0, 4.7)); clean(ax)
for arr, c, lab, dx in ((ks, ACC, 'From deflection', -0.06), (kf, SEC, 'From frequency', 0.06)):
    lo, med, hi = np.percentile(arr, 5, 0), np.median(arr, 0), np.percentile(arr, 95, 0)
    ax.fill_between(x, lo, hi, color=c, alpha=0.15, lw=0); ax.plot(x, med, color=c, lw=3, marker='o', ms=8, mec='white', mew=2)
ax.text(1.3, 101, 'From frequency', color=SEC, fontsize=16, fontweight='bold'); ax.text(0.0, 58, 'From deflection', color=ACC, fontsize=16, fontweight='bold')
ax.text(x[-1], np.percentile(ks[:, -1], 5) - 7, '90% band', ha='center', color=MUTED, fontsize=15)
ax.set_xticks(x); ax.set_xticklabels(['None'] + [f'{int(s)}' for s in stages[1:]]); ax.set_ylim(0, 112); ax.set_xlim(-0.3, len(x) - 0.7)
ax.set_xlabel('Damage stage (kN)'); ax.set_ylabel('Stiffness remaining (%)')
fig.tight_layout(); fig.savefig(OUT + 'stiffness.png', dpi=220, facecolor='white'); plt.close(fig)
# chart 2: twin absolute error by method (median and 95th percentile)
fig, ax = plt.subplots(figsize=(8.2, 5.0)); clean(ax); xs = np.arange(len(stages) - 1)
sty = {'No updating': ('#BDBDBD', -0.27), 'Vibration only': (SEC, -0.09), 'Static only': ('#4D4D4D', 0.09), 'Combined': (ACC, 0.27)}
for m, (c, dx) in sty.items():
    med = [np.median(np.abs(e)) for e in err[m]]; p95 = [np.percentile(np.abs(e), 95) for e in err[m]]
    ax.bar(xs + dx, med, 0.17, color=c); ax.errorbar(xs + dx, med, yerr=[np.zeros(len(med)), np.array(p95) - np.array(med)], fmt='none', ecolor='#333333', capsize=0, lw=1.4)
ax.set_yscale('log'); ax.set_ylim(0.1, 200); ax.set_yticks([0.1, 1, 10, 100]); ax.set_yticklabels(['0.1', '1', '10', '100']); ax.minorticks_off()
ax.set_xticks(xs); ax.set_xticklabels([f'{int(s)} kN' for s in stages[1:]]); ax.set_xlabel('Damage stage'); ax.set_ylabel('Prediction error (%)')
for i, (m, (c, _)) in enumerate(sty.items()): ax.text(-0.35 + i * 0.95, 120, m, color=c, fontsize=15, fontweight='bold')
fig.tight_layout(); fig.savefig(OUT + 'twin.png', dpi=220, facecolor='white'); plt.close(fig)
# chart 3: sensitivity tornado for stiffness left after 72 kN
fig, ax = plt.subplots(figsize=(6.0, 4.7))
order = list(names); v = [summary['sensitivity']['left72'][k] for k in order]
ax.barh(range(len(order)), v, color=[ACC if abs(t_) >= 0.25 else '#BDBDBD' for t_ in v], height=0.6)
ax.axvline(0, color='#555555', lw=1); ax.set_xlim(-1, 1.15)
for i, t_ in enumerate(v): ax.text(t_ + (0.04 if t_ >= 0 else -0.04), i, f'{t_:+.2f}'.replace('-', '−'), va='center', ha='left' if t_ >= 0 else 'right', fontsize=15)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
ax.set_yticks(range(len(order))); ax.set_yticklabels([names[k] for k in order], fontsize=15); ax.invert_yaxis()
ax.set_xlabel('Rank correlation with stiffness left'); ax.set_title('Stiffness left after 72 kN', fontsize=17, loc='left')
fig.tight_layout(); fig.savefig(OUT + 'sensitivity.png', dpi=220, facecolor='white'); plt.close(fig)
print(json.dumps({k: summary[k] for k in ('n_samples', 'n_converged', 'f0', 'Pmax')}, indent=0))
print('left72 deflection', summary['stiffness_left_deflection']['72'], 'frequency', summary['stiffness_left_frequency']['72'])
for m in methods: print(m, {k: (round(v['abs_err_median'], 2), round(v['abs_err_p95'], 2), round(v['coverage90'], 2)) for k, v in summary['twin'][m].items()})
print('dyn/static', summary['dynamic_to_static_EI'])
print('sens', {o: {k: round(v, 2) for k, v in d.items()} for o, d in summary['sensitivity'].items()})
