"""Summary of the constitutive study on the published beams: blind rule and 14 alternative tension laws
(tensile strength from the measured cracking load). Error = root-mean-square difference in static stiffness remaining,
12.5 to 45 kN, against the raw test and against the test corrected for its extra setup compliance."""
import json, glob, numpy as np
D = json.load(open('fig22_digitised.json')); F = np.array(D['dyn_BI1']['F']); L = np.array([12.5, 15, 17.5, 20, 25, 30, 35, 40, 45])
raw = np.mean([np.interp(L, F, D['sta_' + b]['EI']) / D['sta_' + b]['plateau'] for b in ('BI1', 'BI2')], 0)
cor = np.mean([1 / (6.11 * (1 / np.interp(L, F, D['sta_' + b]['EI']) - (1 / D['sta_' + b]['plateau'] - 1 / 6.11))) for b in ('BI1', 'BI2')], 0)
V = json.load(open('../musial_val.json'))['BI_model']; Fv = [r['F'] for r in V if r['F'] > 0]; Sv = [r['static_left'] for r in V if r['F'] > 0]
blind = np.interp(L, Fv, Sv)
rms = lambda m, t: float(np.sqrt(np.mean((m - t) ** 2)))
out = dict(loads=L.tolist(), test_raw=raw.tolist(), test_corrected=cor.tolist(), blind=dict(model=blind.tolist(), rms_raw=rms(blind, raw), rms_corrected=rms(blind, cor),
           max_abs_raw=float(np.max(np.abs(blind - raw)))), variants={})
for f in sorted(g for g in glob.glob('calib_*.json') if 'summary' not in g):
    r = json.load(open(f)); m = np.array(r['model_static'])
    out['variants'][f[6:-5]] = dict(model=m.tolist(), rms_raw=rms(m, raw), rms_corrected=rms(m, cor), end_45=float(m[-1]))
best_raw = min(out['variants'].items(), key=lambda kv: kv[1]['rms_raw']); best_cor = min(out['variants'].items(), key=lambda kv: kv[1]['rms_corrected'])
out['best_raw'] = [best_raw[0], best_raw[1]['rms_raw']]; out['best_corrected'] = [best_cor[0], best_cor[1]['rms_corrected']]
out['n_variants'] = len(out['variants'])
out['top_bar_sensitivity'] = {str(d): json.load(open('topbar_%g.json' % d)) for d in (6, 8, 10)}
json.dump(out, open('calib_summary.json', 'w'), indent=1)
print('blind rms raw %.3f corrected %.3f max %.3f' % (out['blind']['rms_raw'], out['blind']['rms_corrected'], out['blind']['max_abs_raw']))
print('variants', out['n_variants'], 'best raw', out['best_raw'], 'best corrected', out['best_corrected'])
