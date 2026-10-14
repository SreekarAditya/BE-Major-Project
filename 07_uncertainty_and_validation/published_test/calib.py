"""Calibration of the tension-softening slope on the published static stiffness path (beams B-I, mean of two),
with the tensile strength fixed by the measured cracking load (not fitted). Usage: python3 calib.py <ets values...>"""
import sys, json, numpy as np
from musial_model import run_BI, ft_from_cracking
D = json.load(open('fig22_digitised.json')); F = np.array(D['dyn_BI1']['F'])
LOADS = np.array([12.5, 15, 17.5, 20, 25, 30, 35, 40, 45])
def test_norm(kind):
    return np.mean([np.interp(LOADS, F, D[kind + b]['EI']) / D[kind + b]['plateau'] for b in ('_BI1', '_BI2')], axis=0)
ts, td = test_norm('sta'), test_norm('dyn')
ft = ft_from_cracking()
for arg in sys.argv[1:]:
    if arg.startswith('tri'):
        _, a_, e2_ = arg.split(':'); ets = arg
        kw = dict(law='tri', alpha=float(a_), e2=float(e2_))
    else:
        ets = float(arg); kw = dict(law='c04', et=ets) if ets < 0.05 else dict(ets=ets)
    try:
        rows = run_BI(ft=ft, **kw)
    except RuntimeError as e:
        print(ets, 'failed', e); continue
    R = {r['F']: r for r in rows}; s0 = R[5]['EIs']; f0 = R[0.0]['f']
    ms = np.array([R[f]['EIs'] / s0 for f in LOADS]); md = np.array([(R[f]['f'] / f0) ** 2 for f in LOADS])
    rec = dict(ets=ets, ft=ft, rms_static=float(np.sqrt(np.mean((ms - ts) ** 2))), rms_dynamic=float(np.sqrt(np.mean((md - td) ** 2))),
               loads=LOADS.tolist(), model_static=ms.tolist(), model_dynamic=md.tolist(), test_static=ts.tolist(), test_dynamic=td.tolist(),
               EIs_5kN=s0, f_free0=f0, rows=rows)
    json.dump(rec, open('calib_%s.json' % str(ets).replace(':', '_'), 'w'), indent=1)
    print('ets %s  rms static %.3f  dynamic %.3f   static %s' % (str(ets), rec['rms_static'], rec['rms_dynamic'], np.round(ms, 2)), flush=True)
