"""Sensitivity of the blind validation to the assumed top bars (not reported in the paper): 2 x 6, 2 x 8, 2 x 10 mm."""
import sys, json, numpy as np
from musial_model import run_B0, run_BI
d = float(sys.argv[1])
B0 = run_B0(top_d=d); rows = run_BI(steps=(5, 45), top_d=d)
rec = dict(top_d=d, f_free=B0['f_free'], Pmax=B0['Pmax'], static_left_45=rows[2]['EIs'] / rows[1]['EIs'], dynamic_left_45=(rows[2]['f'] / rows[0]['f']) ** 2)
json.dump(rec, open('topbar_%g.json' % d, 'w')); print(rec, flush=True)
