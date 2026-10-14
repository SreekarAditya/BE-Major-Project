"""Monte Carlo uncertainty runs of the verified fibre beam model (230 x 300 mm, span 3.0 m).
Each sample draws material properties, runs the staged damage history
(15 kN check cycle + frequency + 30 kN service cycle after each stage) and a final push to failure.
Usage: python3 mc.py <first_sample> <last_sample> <outfile.jsonl>

Input distributions (documented on the statistics slide):
  fck   ~ Normal(30, 5) MPa, truncated at 20         (IS 456 Table 8: assumed standard deviation 5 MPa for M30)
  Ec    = 5000 sqrt(fck) x LogNormal(median 1, CoV 0.15)  (scatter of the IS 456 empirical formula)
  ft    = 0.7 sqrt(fck) x LogNormal(median 1, CoV 0.15)
  Ets   = U(0.05, 0.10) x Ec   (tension stiffening: tension falls to zero over about 10-20 times the cracking strain)
  fy    ~ Normal(500, 25) MPa                        (CoV 5 %)
"""
import sys, json, time, numpy as np, openseespy.opensees as ops
from p import b, h, span, bot, top, y_bot, y_top, rho, Es
ne = 24; le = span / ne; nmid = ne // 2 + 1; nl = (ne // 3 + 1, 2 * ne // 3 + 1)
Pd, Ps, STAGES = 15.0, 30.0, (35., 50., 65., 72.)

def draw(rng):
    fck = max(20.0, rng.normal(30, 5))
    Ec = 5000 * np.sqrt(fck) * rng.lognormal(0, 0.15)
    ft = 0.7 * np.sqrt(fck) * rng.lognormal(0, 0.15)
    return dict(fck=fck, Ec=Ec, ft=ft, ets=rng.uniform(0.05, 0.10), fy=rng.normal(500, 25))

def build(q):
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    for i in range(ne + 1): ops.node(i + 1, i * le, 0.)
    ops.fix(1, 1, 1, 0); ops.fix(ne + 1, 0, 1, 0)
    fcm = 0.8 * q['fck']
    ops.uniaxialMaterial('Concrete02', 1, -fcm, -2 * fcm / q['Ec'], -0.2 * fcm, -0.0035, 0.1, q['ft'], q['ets'] * q['Ec'])
    ops.uniaxialMaterial('Steel02', 2, q['fy'], Es, 0.01, 18, 0.925, 0.15)
    ops.section('Fiber', 1); yb = -h / 2
    ops.patch('rect', 1, 60, 1, yb, -b / 2, h / 2, b / 2)
    ops.layer('straight', 2, bot['n'], np.pi * bot['d'] ** 2 / 4, yb + y_bot, 0, yb + y_bot, 0)
    ops.layer('straight', 2, top['n'], np.pi * top['d'] ** 2 / 4, yb + y_top, 0, yb + y_top, 0)
    ops.geomTransf('Linear', 1); ops.beamIntegration('Lobatto', 1, 1, 5)
    for i in range(ne): ops.element('forceBeamColumn', i + 1, i + 1, i + 2, 1, 1)
    for i in range(ne + 1):
        mi = rho * b * h * le * (0.5 if i in (0, ne) else 1.); ops.mass(i + 1, mi, mi, 0.)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
    for n in nl: ops.load(n, 0, -0.5, 0)
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-8, 100); ops.algorithm('Newton')

def _try(du):
    ops.integrator('DisplacementControl', nmid, 2, du); ops.analysis('Static')
    for alg in (('Newton',), ('ModifiedNewton', '-initial'), ('NewtonLineSearch',), ('KrylovNewton',)):
        ops.algorithm(*alg)
        if ops.analyze(1) == 0:
            ops.algorithm('Newton'); return 0
    ops.algorithm('Newton'); return -1
def step(du):
    if _try(du) == 0: return 0
    ops.test('NormDispIncr', 1e-6, 200)
    for _ in range(10):                      # substeps
        if _try(du / 10) != 0:
            ops.test('NormDispIncr', 1e-8, 100); return -1
    ops.test('NormDispIncr', 1e-8, 100); return 0
def freq():
    w2 = ops.eigen(3); return float(np.sqrt(min(w2)) / (2 * np.pi))
state = lambda: (ops.getLoadFactor(1) / 1e3, -ops.nodeDisp(nmid, 2))
def load_to(Pt, du=0.02):
    P = []; D = []
    while True:
        if step(-du) != 0: raise RuntimeError('nonconvergence')
        p, d = state(); P.append(p); D.append(d)
        if p >= Pt: return np.array(P), np.array(D)
        if len(P) > 4000: raise RuntimeError('target load not reached')
def unload(du=0.02):
    while ops.getLoadFactor(1) > 0.02e3:
        if step(du) != 0: break
def cycle(Pt):
    d0 = state()[1]; P, D = load_to(Pt); unload(); return float(np.interp(Pt, P, D) - d0)

def run(q):
    build(q); rows = []
    for Dmg in (None,) + STAGES:
        if Dmg is not None: load_to(Dmg); unload()
        dd = cycle(Pd); f = freq(); ds = cycle(Ps) if Dmg is not None else None
        rows.append(dict(damage=Dmg or 0.0, resid=state()[1], delta_d=dd, f=f, delta_s=ds))
    Pmax = 0.0
    while state()[1] < 25:
        if step(-0.05) != 0: break
        Pmax = max(Pmax, state()[0])
    return rows, Pmax

if __name__ == '__main__':
    i0, i1, fn = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    with open(fn, 'a') as fh:
        for i in range(i0, i1):
            rng = np.random.default_rng(1000 + i); q = draw(rng); t = time.time()
            try:
                rows, Pmax = run(q); rec = dict(i=i, ok=True, q=q, rows=rows, Pmax=Pmax)
            except Exception as e:
                rec = dict(i=i, ok=False, q=q, err=str(e))
            rec['sec'] = round(time.time() - t, 1)
            fh.write(json.dumps(rec) + '\n'); fh.flush()
