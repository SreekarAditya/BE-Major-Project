"""Breathing-crack check on Musial et al. (2021) beams BI-1/BI-2: vibration frequency of a beam whose cracks
open and close each cycle, from the bilinear-oscillator result f_v = 2 f_open f_closed / (f_open + f_closed),
with f_open = model frequency of the cracked unloaded beam and f_closed = undamaged frequency."""
import json, os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(HERE, "..", "..", "03_validation_published_tests", "musial2021"); sys.path.insert(0, V)
import musial_model as M
ev = json.load(open(os.path.join(V, 'real_evidence.json'))); L = ev['loads']
rows = M.run_BI(law='c02', steps=tuple(L)); f0 = rows[0]['f']
EIs0 = None
out = []
for r in rows[1:]:
    fo = r['f']; fv = 2 * fo * f0 / (fo + f0)
    out.append(dict(F=r['F'], EIs=r['EIs'], open_left=(fo / f0) ** 2, breathing_left=(fv / f0) ** 2))
EIs_ref = out[0]['EIs'] / ev['BI1']['static_left'][0]           # same normalisation as the test record (first step)
print(' F   static(model) | dynamic: open-crack  breathing | measured dynamic BI1 BI2 | measured static BI1 BI2')
for k, o in enumerate(out):
    print('%5.1f %6.2f        |      %5.2f        %5.2f   |     %5.2f %5.2f       |   %5.2f %5.2f' % (
        o['F'], o['EIs'] / out[0]['EIs'] * ev['BI1']['static_left'][0], o['open_left'], o['breathing_left'],
        ev['BI1']['dynamic_left'][k], ev['BI2']['dynamic_left'][k], ev['BI1']['static_left'][k], ev['BI2']['static_left'][k]))
s = out[-1]['EIs'] / out[0]['EIs'] * ev['BI1']['static_left'][0]
for name, d in (('open crack', out[-1]['open_left']), ('breathing', out[-1]['breathing_left'])):
    print('kappa at 44.5 kN, %s: %.2f' % (name, (1 - d) / (1 - s)))
md = np.mean([ (ev['BI1']['dynamic_left'][-1] + ev['BI2']['dynamic_left'][-1]) / 2 ])
ms = (ev['BI1']['static_left'][-1] + ev['BI2']['static_left'][-1]) / 2
print('measured kappa at 44.5 kN (mean of BI1, BI2): %.2f' % ((1 - md) / (1 - ms)))
json.dump(out, open(os.path.join(HERE, 'musial2021_breathing_check.json'), 'w'), indent=1)
