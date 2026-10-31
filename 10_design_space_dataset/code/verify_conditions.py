"""Checks before the condition runs.

1. corrosion.py at zero mass loss must reproduce gen.py (the corroded model differs only in its materials):
   diagnostic deflections and residuals within 0.1%, frequencies within 1% (the top-cover fibres are split
   differently), peak load within 0.1%, for beams 0 and 57.
2. sustained.py must run on beam 0 (service case) and give finite results with a 50-year deflection multiplier
   between 1.5 and 5.
Prints PASS or FAIL for each check. Usage (from 06_design_space_population/code): python3 verify_conditions.py
"""
import os, sys, csv, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
fd = os.open(os.devnull, os.O_WRONLY); keep = os.dup(1); os.dup2(fd, 1); os.dup2(fd, 2)
import gen, corrosion, sustained


def say(*a):
    os.write(keep, (' '.join(str(x) for x in a) + '\n').encode())


rows = {int(r['beam']): r for r in csv.DictReader(open(os.path.join(HERE, '..', 'data', 'design.csv')))}
ok_all = True
for i in (0, 57):
    row = rows[i]; g = gen.geometry(row)
    q = dict(fck=float(row['fck_MPa']), Ec=float(row['Ec_MPa']), ft=float(row['ft_MPa']), ets=float(row['ets']), fy=float(row['fy_MPa']))
    Py = float(row['Py_hand_kN']); fr = [float(x) for x in row['stage_fractions'].split(';')]
    st, P, _ = gen.run(g, q, 0.185 * Py, 0.37 * Py, [f * Py for f in fr], g['span'] / 100)
    c = corrosion.run_corrosion(row, 0.0); sc = c['stages']
    rel = lambda a, b: abs(a - b) / max(abs(b), 1e-9)
    n = min(len(st), len(sc)); dd = rs = ff = 0.0
    for a, b in zip(sc[:n], st[:n]):
        if a.get('reached', True) and b.get('reached', True):
            dd = max(dd, rel(a['delta_d_mm'], b['delta_d_mm'])); rs = max(rs, abs(a['residual_mm'] - b['residual_mm']))
            ff = max(ff, rel(a['freq_hz'][0], b['freq_hz'][0]))
    pm = rel(c['Pmax_kN'], P) if (P == P and c['Pmax_kN'] == c['Pmax_kN']) else (0.0 if (P != P and c['Pmax_kN'] != c['Pmax_kN']) else 1.0)
    ok = len(st) == len(sc) and dd < 1e-3 and rs < 1e-3 + 1e-3 * max(abs(s.get('residual_mm', 0)) for s in st) and ff < 1e-2 and pm < 1e-3
    ok_all &= ok
    say('corrosion psi=0 vs gen, beam %d: stages %d/%d, delta_d rel %.2e, residual abs %.2e mm, f1 rel %.2e, Pmax rel %.2e -> %s'
        % (i, len(sc), len(st), dd, rs, ff, pm, 'PASS' if ok else 'FAIL'))
r = sustained.run_sustained(rows[0], 'service'); u = r['under_load']
m = u[-1]['deflection_mm'] / u[0]['deflection_mm']
vals = [x['deflection_mm'] for x in u] + [r['residual_50y_mm'], r['f_unloaded_50y_hz'][0]]
ok = all(math.isfinite(v) for v in vals) and 1.5 < m < 5
ok_all &= ok
say('sustained beam 0 service: deflection %s mm, multiplier %.2f -> %s' % ([round(v, 3) for v in vals[:4]], m, 'PASS' if ok else 'FAIL'))
say('ALL PASS' if ok_all else 'SOME CHECKS FAILED')
sys.exit(0 if ok_all else 1)
