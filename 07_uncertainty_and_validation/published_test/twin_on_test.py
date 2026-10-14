"""Digital-twin logic tested on real measurements: Musial et al. (2021), beams B-I-1 and B-I-2 (digitised Figure 22).
At a load check the twin has both measurements (deflection gives static stiffness, vibration gives dynamic stiffness)
and learns the vibration bias b = ln(EI_dynamic / EI_static). Between checks it has vibration only and predicts
EI_static = EI_dynamic x exp(-b_last). Error reported on predicted deflection (deflection is proportional to 1/EI).
Compared with: (1) no updating since the last check, (2) vibration without bias learning (ratio to the undamaged state)."""
import json, numpy as np
D = json.load(open('fig22_digitised.json')); U = D['reading_uncertainty_MNm2']
F = np.array(D['dyn_BI1']['F'])
def at(name, loads):
    return np.array([D[name]['plateau'] if f < 12 else np.interp(f, F, D[name]['EI']) for f in loads])
out = {}
for gap in (5, 10):
    rows = []
    for beam in ('BI1', 'BI2'):
        loads = np.arange(15, 45.1, 5.0)
        s, d = at('sta_' + beam, loads), at('dyn_' + beam, loads)
        s0, d0 = D['sta_' + beam]['plateau'], D['dyn_' + beam]['plateau']
        for k in range(len(loads)):
            prev = loads[k] - gap
            if prev < 15 and gap == 5 and k == 0: prev = 12.5
            if prev < 12: continue
            sp, dp = at('sta_' + beam, [prev])[0], at('dyn_' + beam, [prev])[0]
            b = np.log(dp / sp)
            pred_bias = d[k] * np.exp(-b)
            pred_none = sp
            pred_vib = s0 * d[k] / d0
            err = lambda p: 100 * (s[k] / p - 1)          # deflection error: predicted / true - 1 = EI_true / EI_pred - 1
            rows.append(dict(beam=beam, load=float(loads[k]), last_check=float(prev), EI_true=round(float(s[k]), 3),
                             err_bias_learning=round(err(pred_bias), 2), err_no_update=round(err(pred_none), 2), err_vibration_no_bias=round(err(pred_vib), 2)))
    e = {k: np.abs([r[k] for r in rows]) for k in ('err_bias_learning', 'err_no_update', 'err_vibration_no_bias')}
    # reading uncertainty propagated: four readings of +-0.05 MN m2 enter each bias-learning prediction
    sig = 100 * U * np.sqrt(np.mean([1 / r['EI_true'] ** 2 for r in rows]) * 2 + np.mean([1 / 5.5 ** 2]) * 2)
    out['gap_%d_kN' % gap] = dict(rows=rows, n=len(rows), median_abs={k: round(float(np.median(v)), 2) for k, v in e.items()},
                                  max_abs={k: round(float(np.max(v)), 2) for k, v in e.items()}, reading_uncertainty_pct=round(float(sig), 1))
    print('checks every %d kN, n = %d predictions' % (gap, len(rows)))
    for k, v in e.items(): print('   %-24s median %5.1f%%   max %5.1f%%' % (k, np.median(v), np.max(v)))
    print('   reading uncertainty of each error about +-%.1f%%' % sig)
json.dump(out, open('twin_on_test.json', 'w'), indent=1)
