"""Evidence from the published measurements (digitised Figure 22 of Musial et al. 2021, beams B-I-1 and B-I-2):
H1: two nominally identical beams, same load history, different stiffness loss.
H2: vibration-based stiffness loss against deflection-based stiffness loss, and the ratio kappa = dynamic loss / static loss,
    fitted through the origin. 'Corrected' removes the extra compliance implied by the test's low initial static stiffness
    (4.0 to 4.2 MN m2 against 6.1 MN m2 by theory and 6.4 to 6.5 MN m2 from vibration)."""
import json, numpy as np
D = json.load(open('fig22_digitised.json')); F = np.array(D['dyn_BI1']['F']); L = np.array([15, 17.5, 20, 25, 30, 35, 40, 44.5])
E0 = 6.11
out = {}
for b in ('BI1', 'BI2'):
    s0, d0 = D['sta_' + b]['plateau'], D['dyn_' + b]['plateau']
    s, d = np.interp(L, F, D['sta_' + b]['EI']), np.interp(L, F, D['dyn_' + b]['EI'])
    c = 1 / s0 - 1 / E0
    out[b] = dict(static_left=(s / s0).tolist(), static_left_corrected=(1 / (E0 * (1 / s - c))).tolist(), dynamic_left=(d / d0).tolist())
out['loads'] = L.tolist()
for key in ('static_left', 'static_left_corrected'):
    xs = np.concatenate([1 - np.array(out[b][key]) for b in ('BI1', 'BI2')]); ys = np.concatenate([1 - np.array(out[b]['dynamic_left']) for b in ('BI1', 'BI2')])
    out['kappa_' + key] = float((xs * ys).sum() / (xs * xs).sum())
i = -1
out['H1'] = dict(static_left_45=[out['BI1']['static_left'][i], out['BI2']['static_left'][i]], dynamic_left_45=[out['BI1']['dynamic_left'][i], out['BI2']['dynamic_left'][i]],
                 EI_static_45=[float(np.interp(44.5, F, D['sta_BI1']['EI'])), float(np.interp(44.5, F, D['sta_BI2']['EI']))],
                 ozturkoglu_bare_D1_f_ratio=[0.988, 0.937], ozturkoglu_dynamic_left=[0.988 ** 2, 0.937 ** 2])
json.dump(out, open('real_evidence.json', 'w'), indent=1)
print('kappa raw %.2f corrected %.2f' % (out['kappa_static_left'], out['kappa_static_left_corrected']))
for b in ('BI1', 'BI2'): print(b, 'at 45 kN: static left %.2f (corrected %.2f), vibration left %.2f' % (out[b]['static_left'][i], out[b]['static_left_corrected'][i], out[b]['dynamic_left'][i]))
print('H1 static EI at 45 kN', out['H1']['EI_static_45'])
