"""Monte Carlo statistics, version 2.
Changes from mc_stats.py:
 1. Realistic vibration: the fibre model cannot reproduce crack closure under small vibrations, so the 'measured'
    vibration stiffness loss is taken as kappa x the deflection-based loss, with kappa ~ U(0.31, 0.39) per beam,
    the range fitted to the published tests (val/real_evidence.py).
 2. Twin with bias learning: at every load check the twin learns b = ln(EI_vibration / EI_static) and corrects the
    next vibration estimate with it.
 3. Uncertainties of each estimator are calibrated on beams 0-149 and coverage of the 90% intervals is tested on 150-299.
 4. Variance-based (Sobol) sensitivity from a quadratic surrogate fitted to the 300 runs (beam 56 rerun with a more patient solver, see rerun_beam56/README.md).
Writes mc2_summary.json, mc2_twin.csv and charts mc2_*.png."""
import json, csv, math, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from scipy.stats import wilcoxon, binomtest
import sys
for f in fm.findSystemFonts():
    if 'Carlito' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family': 'Carlito', 'font.size': 18, 'xtick.labelsize': 16, 'ytick.labelsize': 16, 'axes.edgecolor': '#8A8A8A'})
plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Carlito', 'mathtext.it': 'Carlito:italic', 'mathtext.bf': 'Carlito:bold'})
ACC, SEC, MUTED, GRID = '#8E1B2E', '#4A6C8C', '#7A7A7A', '#E6E6E6'
RAW = sys.argv[1] if len(sys.argv) > 1 else None
S = [json.loads(l) for l in open(RAW)] if RAW else [json.loads(l) for fn in ('mc_a.jsonl', 'mc_b.jsonl') for l in open(fn)]
OUT = sys.argv[2] if len(sys.argv) > 2 else '../ppt/mc2_'
ok = [s for s in S if s['ok']]; ok.sort(key=lambda s: s['i'])
stages = [r['damage'] for r in ok[0]['rows']]; nst = len(stages)
span, a, Pd, Ps, z = 3000.0, 1000.0, 15.0, 30.0, 1.645
C = lambda P: (P * 1e3 / 2) * a * (3 * span ** 2 - 4 * a ** 2) / 24
s_f, s_d = 0.3, 0.01
rng = np.random.default_rng(7)

# ---------------- simulate measurements for every beam
rec = []
for s in ok:
    R = s['rows']; kap = rng.uniform(0.31, 0.39)
    true_left = np.array([R[0]['delta_d'] / r['delta_d'] for r in R])           # deflection-based stiffness left (truth of the check)
    f_true = R[0]['f'] * np.sqrt(1 - kap * (1 - true_left))                       # vibration sees kappa of the loss
    fm_ = f_true + rng.normal(0, s_f, nst); dm = np.array([r['delta_d'] for r in R]) + rng.normal(0, s_d, nst)
    rec.append(dict(i=s['i'], kappa=kap, fm=fm_, dm=dm, truth=np.array([np.nan] + [r['delta_s'] for r in R[1:]]), q=s['q']))

def estimates(r):
    """log-EI estimates at each stage: vibration (relative to undamaged static), static, and bias-corrected vibration"""
    EI0 = C(Pd) / r['dm'][0]
    lv = math.log(EI0) + 2 * np.log(r['fm'] / r['fm'][0])
    ls = np.log(C(Pd) / r['dm'])
    b = lv - ls                                     # bias learned at each check
    lvc = lv.copy(); lvc[1:] = lv[1:] - b[:-1]      # corrected with the bias from the previous check
    return EI0, lv, ls, lvc
# ---------------- calibrate estimator uncertainties on beams 0-149 (log error of the 30 kN prediction)
cal = [r for r in rec if r['i'] < 150]; tst = [r for r in rec if r['i'] >= 150]
def log_err(r):
    EI0, lv, ls, lvc = estimates(r); t = np.log(r['truth'][1:])
    pred = {'No updating': np.full(nst - 1, math.log(C(Ps)) - math.log(EI0)), 'Vibration only': math.log(C(Ps)) - lv[1:],
            'Static only': math.log(C(Ps)) - ls[1:], 'Vibration, bias learned': math.log(C(Ps)) - lvc[1:],
            'Last check held': math.log(C(Ps)) - ls[:-1]}
    return {k: v - t for k, v in pred.items()}
methods = ['No updating', 'Vibration only', 'Static only', 'Vibration, bias learned', 'Last check held']
sig = {m: np.sqrt(np.mean(np.array([log_err(r)[m] for r in cal]) ** 2, axis=0)) for m in methods}    # per stage
# combined twin: inverse-variance combination of static and bias-corrected vibration, with calibrated variances
def twin(r):
    EI0, lv, ls, lvc = estimates(r)
    vs, vv = sig['Static only'] ** 2, sig['Vibration, bias learned'] ** 2
    lc = (lvc[1:] / vv + ls[1:] / vs) / (1 / vv + 1 / vs)
    return math.log(C(Ps)) - lc, np.sqrt(1 / (1 / vv + 1 / vs))
sig_tw = np.sqrt(np.mean(np.array([twin(r)[0] - np.log(r['truth'][1:]) for r in cal]) ** 2, axis=0))
methods_all = methods + ['Twin (combined)']
err = {m: [] for m in methods_all}; cover = {m: [] for m in methods_all}; rows = []
for r in tst:
    le = log_err(r); t = np.log(r['truth'][1:])
    for m in methods:
        err[m].append(100 * (np.exp(le[m]) - 1)); cover[m].append(np.abs(le[m]) <= z * sig[m])
    mu, _ = twin(r); e = mu - t
    err['Twin (combined)'].append(100 * (np.exp(e) - 1)); cover['Twin (combined)'].append(np.abs(e) <= z * sig_tw)
    for j, st in enumerate(stages[1:]):
        rows.append(dict(sample=r['i'], damage_kN=st, kappa=round(r['kappa'], 3), true_30kN_mm=round(float(r['truth'][j + 1]), 4),
                         **{('error_' + m.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '') + '_pct'): round(float(err[m][-1][j]), 2) for m in methods_all}))
err = {m: np.array(v) for m, v in err.items()}; cover = {m: np.array(v) for m, v in cover.items()}
summ = dict(n_beams=len(ok), calibration_beams=len(cal), test_beams=len(tst), kappa_range=[0.31, 0.39],
            calibrated_log_sd={m: [round(float(x), 4) for x in sig[m]] for m in methods} | {'Twin (combined)': [round(float(x), 4) for x in sig_tw]},
            twin={m: {str(int(st)): dict(abs_err_median=float(np.median(np.abs(err[m][:, j]))), abs_err_p95=float(np.percentile(np.abs(err[m][:, j]), 95)),
                                         coverage90=float(cover[m][:, j].mean()), share_below5=float((np.abs(err[m][:, j]) < 5).mean()))
                      for j, st in enumerate(stages[1:])} for m in methods_all})
j72 = nst - 2
summ['tests_72kN'] = dict(
    twin_vs_vibration_p=float(wilcoxon(np.abs(err['Twin (combined)'][:, j72]), np.abs(err['Vibration only'][:, j72]), alternative='less').pvalue),
    biaslearned_vs_lastcheck_p=float(wilcoxon(np.abs(err['Vibration, bias learned'][:, j72]), np.abs(err['Last check held'][:, j72]), alternative='less').pvalue),
    twin_vs_static_p_two_sided=float(wilcoxon(np.abs(err['Twin (combined)'][:, j72]), np.abs(err['Static only'][:, j72])).pvalue))
bs = np.random.default_rng(1)
summ['twin_median_CI95_72kN'] = [float(np.percentile([np.median(bs.choice(np.abs(err['Twin (combined)'][:, j72]), len(tst))) for _ in range(2000)], p)) for p in (2.5, 97.5)]

# ---------------- variance-based sensitivity (Sobol) via quadratic surrogate
# Sobol indices need independent inputs, so Ec and ft enter as their scatter factors about the IS 456 formulas
names = {'fck': r'Concrete strength $f_{\mathrm{ck}}$', 'uE': r'Scatter of $E_{\mathrm{c}}$', 'uT': r'Scatter of $f_{\mathrm{t}}$', 'ets': 'Tension softening slope', 'fy': r'Steel yield $f_{\mathrm{y}}$'}
keys = list(names)
X = np.array([[s['q']['fck'], s['q']['Ec'] / (5000 * np.sqrt(s['q']['fck'])), s['q']['ft'] / (0.7 * np.sqrt(s['q']['fck'])), s['q']['ets'], s['q']['fy']] for s in ok])
Y = {'left72': np.array([100 * s['rows'][0]['delta_d'] / s['rows'][-1]['delta_d'] for s in ok]), 'f0': np.array([s['rows'][0]['f'] for s in ok]),
     'Pmax': np.array([s['Pmax'] for s in ok])}
mu_, sd_ = X.mean(0), X.std(0)
def feats(Xn):
    cols = [np.ones(len(Xn))] + [Xn[:, i] for i in range(5)] + [Xn[:, i] * Xn[:, j] for i in range(5) for j in range(i, 5)]
    return np.column_stack(cols)
# input sampler that reproduces the Monte Carlo distributions
def sample(n, g):
    return np.column_stack([np.maximum(20, g.normal(30, 5, n)), g.lognormal(0, 0.15, n), g.lognormal(0, 0.15, n), g.uniform(0.05, 0.10, n), g.normal(500, 25, n)])
g = np.random.default_rng(11); N = 400000
A_, B_ = sample(N, g), sample(N, g)
sobol = {}
for o, y in Y.items():
    Fm = feats((X - mu_) / sd_); coef, *_ = np.linalg.lstsq(Fm, y, rcond=None)
    pred = Fm @ coef; r2 = 1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)
    # 5-fold cross-validated R2
    idx = np.arange(len(y)); g2 = np.random.default_rng(3); g2.shuffle(idx); cv = np.zeros(len(y))
    for k in range(5):
        te = idx[k::5]; tr = np.setdiff1d(idx, te); c2, *_ = np.linalg.lstsq(Fm[tr], y[tr], rcond=None); cv[te] = Fm[te] @ c2
    r2cv = 1 - np.sum((y - cv) ** 2) / np.sum((y - y.mean()) ** 2)
    f = lambda M: feats((M - mu_) / sd_) @ coef
    fA, fB = f(A_), f(B_); V = np.var(np.concatenate([fA, fB]))
    S1, ST = {}, {}
    for i, k in enumerate(keys):
        ABi = A_.copy(); ABi[:, i] = B_[:, i]; fABi = f(ABi)
        S1[k] = float(np.mean(fB * (fABi - fA)) / V); ST[k] = float(0.5 * np.mean((fA - fABi) ** 2) / V)
    sobol[o] = dict(R2=float(r2), R2_cross_validated=float(r2cv), first_order=S1, total=ST)
summ['sobol'] = sobol
json.dump(summ, open('mc2_summary.json', 'w'), indent=1)
with open('mc2_twin.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# ---------------- charts
def clean(ax):
    ax.grid(axis='y', color=GRID); ax.set_axisbelow(True)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
fig, ax = plt.subplots(figsize=(8.2, 5.0)); clean(ax); xs = np.arange(nst - 1)
sty = {'No updating': ('#BDBDBD', -0.27), 'Vibration only': (SEC, -0.09), 'Static only': ('#4D4D4D', 0.09), 'Twin (combined)': (ACC, 0.27)}
for m, (c, dx) in sty.items():
    med = np.median(np.abs(err[m]), 0); p95 = np.percentile(np.abs(err[m]), 95, 0)
    ax.bar(xs + dx, med, 0.17, color=c, label=m); ax.errorbar(xs + dx, med, yerr=[np.zeros(len(med)), p95 - med], fmt='none', ecolor='#333333', capsize=0, lw=1.4)
ax.set_yscale('log'); ax.set_ylim(0.1, 200); ax.minorticks_off(); T = [0.1, 0.3, 1, 3, 10, 30, 100]
ax.set_yticks(T); ax.set_yticklabels([('%g%%' % t) for t in T])
ax.set_xticks(xs); ax.set_xticklabels([f'{int(s)} kN' for s in stages[1:]]); ax.set_xlabel('Damage stage'); ax.set_ylabel('Prediction error (log scale)')
from matplotlib.lines import Line2D
h, l = ax.get_legend_handles_labels(); h.append(Line2D([0], [0], color='#333333', lw=1.4)); l.append('Whisker: 95th percentile')
ax.legend(h, l, frameon=False, fontsize=14, ncol=3, loc='lower left', bbox_to_anchor=(0, 1.0), handlelength=1.2, columnspacing=1.0)
fig.tight_layout(); fig.savefig(OUT + 'twin.png', dpi=650, facecolor='white'); plt.close(fig)
fig, ax = plt.subplots(figsize=(6.0, 4.7))
v1 = [sobol['left72']['first_order'][k] for k in keys]; vt = [sobol['left72']['total'][k] for k in keys]
yy = np.arange(len(keys))
ax.barh(yy - 0.18, vt, height=0.34, color='#BDBDBD', label='Total effect'); ax.barh(yy + 0.18, v1, height=0.34, color=ACC, label='Alone (first order)')
for i in range(len(keys)): ax.text(max(vt[i], v1[i]) + 0.02, i, f'{100 * vt[i]:.0f}%', va='center', fontsize=15)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
ax.set_yticks(yy); ax.set_yticklabels([names[k] for k in keys], fontsize=15); ax.invert_yaxis(); ax.set_xlim(0, 1.0)
ax.set_xlabel('Share of variance'); ax.set_title('Stiffness left after 72 kN', fontsize=17, loc='left')
ax.legend(frameon=False, fontsize=14, loc='lower right')
fig.tight_layout(); fig.savefig(OUT + 'sobol.png', dpi=650, facecolor='white'); plt.close(fig)

print('beams', len(ok), 'calibration', len(cal), 'test', len(tst))
for m in methods_all:
    print('%-26s' % m, ' '.join('%s: %.1f%% (p95 %.1f, cover %.2f, <5%% %.2f)' % (k, v['abs_err_median'], v['abs_err_p95'], v['coverage90'], v['share_below5']) for k, v in summ['twin'][m].items()))
print('tests', summ['tests_72kN'], 'median CI', summ['twin_median_CI95_72kN'])
for o, d in sobol.items(): print(o, 'R2 %.3f cv %.3f' % (d['R2'], d['R2_cross_validated']), {k: (round(d['first_order'][k], 2), round(d['total'][k], 2)) for k in keys})

# chart: stiffness remaining by deflection (model) and as vibration would read it (kappa from the published tests)
ks = np.array([[100 * s['rows'][0]['delta_d'] / r['delta_d'] for r in s['rows']] for s in ok])
kv = np.array([100 * (1 - r['kappa'] * (1 - ks[n] / 100)) for n, r in enumerate(rec)])
fig, ax = plt.subplots(figsize=(6.0, 4.7)); clean(ax); x = np.arange(nst)
for arr, c, nm in ((ks, ACC, 'Deflection'), (kv, SEC, 'Vibration reading')):
    ax.fill_between(x, np.percentile(arr, 5, 0), np.percentile(arr, 95, 0), color=c, alpha=0.15, lw=0, label=nm + ', 90% band')
    ax.plot(x, np.median(arr, 0), color=c, lw=3, marker='o', ms=8, mec='white', mew=2, label=nm + ', median')
h, l = ax.get_legend_handles_labels(); order = [1, 0, 3, 2]
ax.legend([h[i] for i in order], [l[i] for i in order], frameon=False, fontsize=13, loc='lower left')
ax.set_xticks(x); ax.set_xticklabels(['None'] + [f'{int(s)}' for s in stages[1:]]); ax.set_ylim(0, 112); ax.set_xlim(-0.3, nst - 0.7)
ax.set_xlabel('Damage stage (kN)'); ax.set_ylabel('Stiffness remaining (%)')
fig.tight_layout(); fig.savefig(OUT + 'stiffness.png', dpi=650, facecolor='white'); plt.close(fig)
summ['vibration_reading_left'] = {str(int(st)): [float(np.percentile(kv[:, j], p)) for p in (5, 50, 95)] for j, st in enumerate(stages)}
summ['deflection_left'] = {str(int(st)): [float(np.percentile(ks[:, j], p)) for p in (5, 50, 95)] for j, st in enumerate(stages)}
json.dump(summ, open('mc2_summary.json', 'w'), indent=1)
print('vibration reading left at 72', summ['vibration_reading_left']['72'], 'deflection', summ['deflection_left']['72'])
