"""Validation of the strengthened fibre model against Musial, Trapko and Grosel (2021): beams strengthened before loading."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "code"))
import gen, retrofit_mech as rm, openseespy.opensees as ops
g = gen.geometry(dict(span_mm=3000, b_mm=150, h_mm=250, cover_mm=12, d_stir_mm=8, n_bot=3, d_bot_mm=12, n_top=2, d_top_mm=8,
                      grade_MPa=50, fy_nom_MPa=558, load='four_point')); g['du'] = 0.05
q = dict(fck=50.8 / 0.8, Ec=27300.0, ft=0.9 * 6.7, ets=0.10, fy=558.0)
def three_point(bm):
    ops.remove('loadPattern', 1); ops.timeSeries('Linear', 2); ops.pattern('Plain', 1, 2); ops.load(gen.NMID, 0, -1.0, 0)
    ops.wipeAnalysis(); ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral'); ops.test('NormDispIncr', 1e-8, 100); ops.algorithm('Newton')
res = {}
for name, lam, test in (('B-0', None, 57.41), ('B-II-1', dict(n=1, wf=60.0, tf=1.4, Ef=210000.0, efu=0.017), 90.23), ('B-II-2', dict(n=2, wf=60.0, tf=1.4, Ef=210000.0, efu=0.017), 116.01)):
    gg = dict(g); 
    if lam: gg['laminate'] = lam
    bm = gen.Beam(gg, q); three_point(bm)
    info = rm.strengthen(bm, 'laminate') if lam else {}
    Pmax = 0; D = 0
    while bm.state()[1] < 34:
        if bm.step(-bm.du) != 0: break
        p, d = bm.state()
        if p > Pmax: Pmax, D = p, d
        if p < 0.6 * Pmax and d > 5: break
    res[name] = dict(Pmax_model=round(Pmax, 1), test=test, ratio=round(Pmax / test, 3), defl_at_peak=round(D, 2), **info)
    print(name, res[name], flush=True)
json.dump(res, open(os.path.join(HERE, 'musial2021_strengthened_check.json'), 'w'), indent=1)
