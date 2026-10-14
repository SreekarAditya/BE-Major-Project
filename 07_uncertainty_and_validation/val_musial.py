"""Independent validation: blind prediction of a published test with the same modelling rules as our beam.
Test: Musial, Grosel et al. (2021), Materials 14(4):910, beams B-0 and B-I (unstrengthened stage).
  Section 150 x 250 mm, overall length 3300 mm, span 3000 mm, three-point bending.
  Bottom 3 bars, tension reinforcement ratio 1.01 % (gives 3 x 12 mm at d = 224 mm), top 2 bars (2 x 8 mm assumed).
  Measured: fcm 50.8 MPa (cylinder), Ecm 27.3 GPa, splitting tensile 6.7 MPa, fy 558 MPa, fu 617 MPa, Es 195 GPa.
Modelling rules carried over unchanged (no calibration to this test):
  Concrete02, initial modulus = measured Ec, crushing strain 1.75 per mille beyond the peak strain (as in our beam), tension softening slope 0.1 Ec, Steel02; forceBeamColumn, Lobatto 5.
  Direct tensile strength = 0.9 x splitting strength (Eurocode 2 cl 3.1.2(8)).
Outputs musial_val.json."""
import json, numpy as np, openseespy.opensees as ops

b, h, Ltot, span, ov = 150.0, 250.0, 3300.0, 3000.0, 150.0
fc, Ec, ft, fy, fu, Es = 50.8, 27300.0, 0.9 * 6.7, 558.0, 617.0, 195000.0
As_b, y_b = 3 * np.pi * 12 ** 2 / 4, 26.0          # 339 mm2 at 26 mm from soffit (d = 224 mm)
As_t, y_t = 2 * np.pi * 8 ** 2 / 4, h - 26.0
m_line = 293.0 / 3300.0 * 1e-3                       # mean measured weight 293 kg -> tonne per mm
ne = 22; le = Ltot / ne                              # 150 mm elements, supports at nodes 2 and 22, load at node 12
sA, sB, nmid = 2, 22, 12
eps0 = 2 * fc / Ec                                   # peak strain so that the initial tangent equals measured Ec
b_h = (fu - fy) / (Es * (0.075 - fy / Es))           # Steel02 hardening ratio from fy, fu, 7.5 % uniform elongation

def build():
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    for i in range(ne + 1): ops.node(i + 1, i * le, 0.)
    ops.uniaxialMaterial('Concrete02', 1, -fc, -eps0, -0.2 * fc, -(eps0 + 0.00175), 0.1, ft, 0.1 * Ec)
    ops.uniaxialMaterial('Steel02', 2, fy, Es, b_h, 18, 0.925, 0.15)
    ops.section('Fiber', 1); yb = -h / 2
    ops.patch('rect', 1, 60, 1, yb, -b / 2, h / 2, b / 2)
    ops.layer('straight', 2, 3, As_b / 3, yb + y_b, 0, yb + y_b, 0)
    ops.layer('straight', 2, 2, As_t / 2, yb + y_t, 0, yb + y_t, 0)
    ops.geomTransf('Linear', 1); ops.beamIntegration('Lobatto', 1, 1, 5)
    for i in range(ne): ops.element('forceBeamColumn', i + 1, i + 1, i + 2, 1, 1, '-iter', 50, 1e-10)
    for i in range(ne + 1):
        mi = m_line * le * (0.5 if i in (0, ne) else 1.); ops.mass(i + 1, mi, mi, 1e-9)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1); ops.load(nmid, 0, -1.0, 0)
    support(True)

def support(on):
    if on: ops.fix(sA, 1, 1, 0); ops.fix(sB, 0, 1, 0)
    else:
        ops.remove('sp', sA, 1); ops.remove('sp', sA, 2); ops.remove('sp', sB, 2)
    ops.wipeAnalysis(); ops.constraints('Plain'); ops.numberer('RCM'); ops.system('FullGeneral')
    ops.test('NormDispIncr', 1e-8, 100); ops.algorithm('Newton')

def free_free_freq():
    """first bending frequency of the beam hanging free (as tested): supports removed, rigid-body modes skipped"""
    support(False)
    w2 = np.array(ops.eigen('-fullGenLapack', 8)); support(True)
    w2 = np.sort(w2[w2 > (2 * np.pi * 5) ** 2])
    return float(np.sqrt(w2[0]) / (2 * np.pi))

def step(du):
    if _try(du) == 0: return 0
    ops.test('NormDispIncr', 1e-6, 200)
    for _ in range(10):
        if _try(du / 10) != 0: ops.test('NormDispIncr', 1e-8, 100); return -1
    ops.test('NormDispIncr', 1e-8, 100); return 0
def _try(du):
    ops.integrator('DisplacementControl', nmid, 2, du); ops.analysis('Static')
    for alg in (('Newton',), ('ModifiedNewton', '-initial'), ('NewtonLineSearch',), ('KrylovNewton',)):
        ops.algorithm(*alg)
        if ops.analyze(1) == 0: ops.algorithm('Newton'); return 0
    ops.algorithm('Newton'); return -1
defl = lambda: -(ops.nodeDisp(nmid, 2) - 0.5 * (ops.nodeDisp(sA, 2) + ops.nodeDisp(sB, 2)))
load = lambda: ops.getLoadFactor(1) / 1e3

# ---- 1. B-0: monotonic test to failure
build(); f_ff0 = free_free_freq()
P, D = [0.], [0.]
while D[-1] < 34:
    if step(-0.05) != 0: break
    P.append(load()); D.append(defl())
P, D = np.array(P), np.array(D)
k0 = P[1] / D[1]; icr = int(np.argmax(P[1:] / D[1:] < 0.95 * k0)) + 1
Mcr_hand = ft * (b * h ** 3 / 12) / (h / 2) / 1e6
res = dict(inputs=dict(fc=fc, Ec=Ec, ft=round(ft, 2), fy=fy, fu=fu, Es=Es, steel_hardening=round(b_h, 4)),
           B0=dict(P=P[::4].round(3).tolist(), D=D[::4].round(3).tolist(), Pcr=float(P[icr]), Dcr=float(D[icr]),
                   Pmax=float(P.max()), D_at_Pmax=float(D[np.argmax(P)]), P_at_32mm=float(np.interp(32.03, D, P))),
           test_B0=dict(Pcr=11.15, Dcr=1.943, Pmax=57.41, D_at_Pmax=32.03),
           free_free=dict(model=f_ff0, test_range=[87.0, 89.1], test_mean=float(np.mean([87.0, 88.0, 89.1, 89.0, 88.6, 88.7]))))

# ---- 2. B-I loading history: load steps, deflection under load (static stiffness), unload, free-free frequency (dynamic)
build(); steps = [5, 10, 12, 15, 20, 25, 30, 35, 40, 45]
rows = [dict(F=0.0, EIs=None, f=free_free_freq())]
for Ft in steps:
    while load() < Ft:
        if step(-0.02) != 0: raise RuntimeError('nonconvergence')
    a = defl(); EIs = Ft * 1e3 * span ** 3 / (48 * a) * 1e-12          # N mm2 -> MN m2
    while load() > 0.05:
        if step(0.02) != 0: break
    rows.append(dict(F=Ft, a=a, EIs=EIs, f=free_free_freq()))
EIs0 = rows[1]['EIs']; f0 = rows[0]['f']
for r in rows:
    r['static_left'] = None if r['EIs'] is None else r['EIs'] / EIs0
    r['dynamic_left'] = (r['f'] / f0) ** 2
res['BI_model'] = rows
# test values read from the published stiffness chart (Figure 22, mean of B-I-1 and B-I-2), MN m2
res['BI_test'] = dict(F=[0, 12, 15, 20, 30, 40, 45], EIs=[4.05, 4.05, 3.30, 2.83, 2.47, 2.27, 2.19],
                      EId=[6.47, 6.47, 6.15, 5.72, 5.50, 5.42, 5.16])
json.dump(res, open('musial_val.json', 'w'), indent=1)
print('free-free f model %.1f Hz, test %.1f (87.0-89.1)' % (f_ff0, res['free_free']['test_mean']))
print('B-0 cracking model %.2f kN at %.2f mm | test 11.15 kN at 1.94 mm' % (P[icr], D[icr]))
print('B-0 peak model %.2f kN at %.1f mm, load at 32 mm %.2f | test 57.41 kN at 32.0 mm' % (P.max(), D[np.argmax(P)], res['B0']['P_at_32mm']))
print('hand Mcr %.2f kN m -> Fcr %.2f kN' % (Mcr_hand, 4 * Mcr_hand / 3))
for r in rows: print(r['F'], None if r['EIs'] is None else round(r['EIs'], 2), round(r['f'], 2), r['static_left'] and round(r['static_left'], 3), round(r['dynamic_left'], 3))
