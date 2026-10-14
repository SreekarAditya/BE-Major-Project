"""Corrected fibre beam model of the 230 x 300 mm beam (OpenSeesPy), with verification.
Changes from fibre.py:
  * concrete initial modulus = IS 456 value 5000*sqrt(fck) = 27,386 MPa (was 24,000 MPa implied by Concrete02)
  * concrete tension: ft = 0.7*sqrt(fck) (IS 456 cl 6.2.2), linear softening with slope ETS_FACTOR * Ec
Outputs fibre2.json: verification table, mesh study, pushover, staged damage history."""
import numpy as np, openseespy.opensees as ops, json, sys
from p import *
ETS_FACTOR = float(sys.argv[1]) if len(sys.argv) > 1 else 0.10
fcm = 0.8 * fck                     # cylinder strength used for the stress-strain curve
eps0 = 2 * fcm / Ec                 # gives initial tangent = Ec
Pd, Ps = 15.0, 30.0

def build(ne):
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    le = span / ne
    for i in range(ne + 1): ops.node(i + 1, i * le, 0.)
    ops.fix(1, 1, 1, 0); ops.fix(ne + 1, 0, 1, 0)
    ops.uniaxialMaterial('Concrete02', 1, -fcm, -eps0, -0.2 * fcm, -0.0035, 0.1, ft, ETS_FACTOR * Ec)
    ops.uniaxialMaterial('Steel02', 2, fy, Es, 0.01, 18, 0.925, 0.15)
    ops.section('Fiber', 1)
    yb = -h / 2
    ops.patch('rect', 1, 60, 1, yb, -b / 2, h / 2, b / 2)
    ops.layer('straight', 2, bot['n'], np.pi * bot['d'] ** 2 / 4, yb + y_bot, 0, yb + y_bot, 0)
    ops.layer('straight', 2, top['n'], np.pi * top['d'] ** 2 / 4, yb + y_top, 0, yb + y_top, 0)
    ops.geomTransf('Linear', 1); ops.beamIntegration('Lobatto', 1, 1, 5)
    for i in range(ne): ops.element('forceBeamColumn', i + 1, i + 1, i + 2, 1, 1)
    for i in range(ne + 1):
        mi = rho * b * h * le * (0.5 if i in (0, ne) else 1.); ops.mass(i + 1, mi, mi, 0.)
    nmid = ne // 2 + 1; nl = (ne // 3 + 1, 2 * ne // 3 + 1)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
    for n in nl: ops.load(n, 0, -0.5, 0)
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('FullGeneral')
    ops.test('NormDispIncr', 1e-8, 100); ops.algorithm('Newton')
    return nmid

def step(nmid, du):
    ops.integrator('DisplacementControl', nmid, 2, du); ops.analysis('Static')
    ok = ops.analyze(1)
    if ok != 0: ops.algorithm('ModifiedNewton', '-initial'); ok = ops.analyze(1); ops.algorithm('Newton')
    return ok
def freq():
    w2 = ops.eigen('-fullGenLapack', 2); return float(np.sqrt(min(w2)) / (2 * np.pi))
state = lambda nmid: (ops.getLoadFactor(1) / 1e3, -ops.nodeDisp(nmid, 2))

def pushover(ne, dmax=40, du=0.05):
    nmid = build(ne); f0 = freq(); P = [0.]; D = [0.]
    while D[-1] < dmax:
        if step(nmid, -du) != 0: break
        p, d = state(nmid); P.append(p); D.append(d)
        if p < 0.8 * max(P) and d > 8: break
    P, D = np.array(P), np.array(D)
    k0 = P[1] / D[1]
    sec = P[1:] / D[1:]; icr = int(np.argmax(sec < 0.95 * k0)) + 1          # first 5% loss of secant stiffness
    return dict(f0=f0, P=P.tolist(), D=D.tolist(), d15=float(np.interp(15, P[:np.argmax(P)], D[:np.argmax(P)])),
                Pcr=float(P[icr]), Ppeak=float(P.max()), Dpeak=float(D[np.argmax(P)]))

out = dict(ets_factor=ETS_FACTOR, Ec=Ec, fcm=fcm, ft=ft)
# mesh study
out['mesh'] = {}
for ne in (12, 24, 48):
    r = pushover(ne); out['mesh'][ne] = {k: r[k] for k in ('f0', 'd15', 'Pcr', 'Ppeak', 'Dpeak')}
    print('mesh', ne, {k: round(v, 3) for k, v in out['mesh'][ne].items()}, flush=True)
    if ne == 24: out['push'] = dict(P=r['P'], D=r['D'])

# staged damage history (24 elements)
nmid = build(24); f00 = freq()
def load_to(Pt, du=0.01):
    P = []; D = []
    while True:
        if step(nmid, -du) != 0: raise RuntimeError('nonconv')
        p, d = state(nmid); P.append(p); D.append(d)
        if p >= Pt: return np.array(P), np.array(D)
def unload(du=0.01):
    while ops.getLoadFactor(1) > 0.02e3:
        if step(nmid, du) != 0: break
def cycle(Pt):
    d0 = state(nmid)[1]; P, D = load_to(Pt); unload(); return float(np.interp(Pt, P, D) - d0)
rows = []
for Dmg in [None, 35., 50., 65., 72.]:
    pl = None
    if Dmg is not None:
        P, D = load_to(Dmg); pl = float(D[-1]); unload()
    resid = state(nmid)[1]; dd = cycle(Pd); f = freq(); ds = cycle(Ps) if Dmg is not None else None
    rows.append(dict(damage=Dmg or 0.0, defl_at_damage=pl, resid=resid, delta_d=dd, f=f, delta_s=ds))
    print('stage', Dmg, round(resid, 3), round(dd, 3), round(f, 2), ds and round(ds, 3), flush=True)
out['twin'] = dict(f0=f00, Pd=Pd, Ps=Ps, rows=rows)
json.dump(out, open(f'fibre2_{ETS_FACTOR}.json', 'w'))
