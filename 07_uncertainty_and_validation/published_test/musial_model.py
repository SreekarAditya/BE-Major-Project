"""Fibre model of the Musial, Trapko and Grosel (2021) beams (Materials 14, 910), same modelling rules as our beam.
150 x 250 mm, overall 3300 mm, span 3000 mm, three-point bending; 3 bars of 12 mm (from the 1.01% ratio), top bars assumed 2 x 8 mm.
Measured: fcm 50.8 MPa, Ec 27.3 GPa, splitting tensile 6.7 MPa, fy 558 MPa, fu 617 MPa, Es 195 GPa, mean weight 293 kg.
Functions: run_B0 (monotonic to failure), run_BI (load steps, static secant stiffness under load, free-free frequency after unloading)."""
import numpy as np, openseespy.opensees as ops

b, h, Ltot, span = 150.0, 250.0, 3300.0, 3000.0
fc, Ec, fy, fu, Es = 50.8, 27300.0, 558.0, 617.0, 195000.0
FT_SPLIT = 0.9 * 6.7                                   # Eurocode 2 cl 3.1.2(8): direct tension = 0.9 x splitting
As_b, y_b = 3 * np.pi * 12 ** 2 / 4, 26.0
m_line = 293.0 / 3300.0 * 1e-3
ne = 22; le = Ltot / ne; sA, sB, nmid = 2, 22, 12
eps0 = 2 * fc / Ec
b_h = (fu - fy) / (Es * (0.075 - fy / Es))

def I_transformed(top_d=8.0):
    n = Es / Ec; At = 2 * np.pi * top_d ** 2 / 4; yt = h - 26.0
    A = b * h + (n - 1) * (As_b + At); ybar = (b * h * h / 2 + (n - 1) * (As_b * y_b + At * yt)) / A
    I = b * h ** 3 / 12 + b * h * (h / 2 - ybar) ** 2 + (n - 1) * (As_b * (ybar - y_b) ** 2 + At * (yt - ybar) ** 2)
    return I, ybar

def ft_from_cracking(Fcr_kN=11.15, top_d=8.0):
    """tensile stress at the soffit when the measured cracking load is reached (uncracked transformed section)"""
    I, ybar = I_transformed(top_d); M = Fcr_kN * 1e3 * span / 4
    return M * ybar / I

def build(ft=FT_SPLIT, ets=0.1, top_d=8.0, law='c02', et=0.002, beta=0.1, alpha=0.4, e2=0.001, e3=0.004):
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    for i in range(ne + 1): ops.node(i + 1, i * le, 0.)
    if law == 'c02':     # linear tension softening (rule used so far)
        ops.uniaxialMaterial('Concrete02', 1, -fc, -eps0, -0.2 * fc, -(eps0 + 0.00175), 0.1, ft, ets * Ec)
    elif law == 'c04':   # Popovics compression, exponential tension stiffening: stress decays from ft to beta ft at strain et
        ops.uniaxialMaterial('Concrete04', 1, -fc, -0.0024, -0.0035, Ec, ft, et, beta)
    else:                # 'tri': compression from Concrete02 (negligible tension) in parallel with a tension-only
                         # tri-linear tension-stiffening law: ft at cracking, alpha ft at strain e2, zero at strain e3
        ops.uniaxialMaterial('Concrete02', 11, -fc, -eps0, -0.2 * fc, -(eps0 + 0.00175), 0.1, 0.01, 0.01 * Ec)
        ecr = ft / Ec
        ops.uniaxialMaterial('Hysteretic', 12, ft, ecr, alpha * ft, e2, 0.001 * ft, e3, -0.001, -1e-3, -0.002, -1e-2, -0.003, -1e-1, 1.0, 1.0, 0.0, 0.0, 0.0)
        ops.uniaxialMaterial('Parallel', 1, 11, 12)
    ops.uniaxialMaterial('Steel02', 2, fy, Es, b_h, 18, 0.925, 0.15)
    ops.section('Fiber', 1); yb = -h / 2
    ops.patch('rect', 1, 60, 1, yb, -b / 2, h / 2, b / 2)
    ops.layer('straight', 2, 3, As_b / 3, yb + y_b, 0, yb + y_b, 0)
    At = 2 * np.pi * top_d ** 2 / 4
    ops.layer('straight', 2, 2, At / 2, yb + h - 26.0, 0, yb + h - 26.0, 0)
    ops.geomTransf('Linear', 1); ops.beamIntegration('Lobatto', 1, 1, 5)
    for i in range(ne): ops.element('forceBeamColumn', i + 1, i + 1, i + 2, 1, 1, '-iter', 50, 1e-10)
    for i in range(ne + 1):
        mi = m_line * le * (0.5 if i in (0, ne) else 1.); ops.mass(i + 1, mi, mi, 1e-9)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1); ops.load(nmid, 0, -1.0, 0)
    support(True)

def support(on):
    if on: ops.fix(sA, 1, 1, 0); ops.fix(sB, 0, 1, 0)
    else: ops.remove('sp', sA, 1); ops.remove('sp', sA, 2); ops.remove('sp', sB, 2)
    ops.wipeAnalysis(); ops.constraints('Plain'); ops.numberer('RCM'); ops.system('FullGeneral')
    ops.test('NormDispIncr', 1e-8, 100); ops.algorithm('Newton')

def free_free_freq():
    support(False); w2 = np.array(ops.eigen('-fullGenLapack', 8)); support(True)
    w2 = np.sort(w2[w2 > (2 * np.pi * 5) ** 2]); return float(np.sqrt(w2[0]) / (2 * np.pi))

def _try(du):
    ops.integrator('DisplacementControl', nmid, 2, du); ops.analysis('Static')
    for alg in (('Newton',), ('ModifiedNewton', '-initial'), ('NewtonLineSearch',), ('KrylovNewton',)):
        ops.algorithm(*alg)
        if ops.analyze(1) == 0: ops.algorithm('Newton'); return 0
    ops.algorithm('Newton'); return -1
def step(du):
    if _try(du) == 0: return 0
    ops.test('NormDispIncr', 1e-6, 200)
    for _ in range(20):
        if _try(du / 20) != 0: ops.test('NormDispIncr', 1e-8, 100); return -1
    ops.test('NormDispIncr', 1e-8, 100); return 0
defl = lambda: -ops.nodeDisp(nmid, 2)
load = lambda: ops.getLoadFactor(1) / 1e3

def run_B0(dmax=34.0, **kw):
    build(**kw); f0 = free_free_freq(); P, D = [0.], [0.]
    while D[-1] < dmax:
        if step(-0.05) != 0: break
        P.append(load()); D.append(defl())
    P, D = np.array(P), np.array(D)
    return dict(f_free=f0, P=P, D=D, Pmax=float(P.max()), D_end=float(D[-1]), P_at_32=float(np.interp(32.03, D, P)) if D[-1] >= 32 else None)

def run_BI(steps=(5, 10, 12.5, 15, 17.5, 20, 25, 30, 35, 40, 45), **kw):
    build(**kw); rows = [dict(F=0.0, EIs=None, f=free_free_freq())]
    for Ft in steps:
        while load() < Ft:
            if step(-0.02) != 0: raise RuntimeError('nonconvergence at %.1f kN' % load())
        a = defl(); EIs = Ft * 1e3 * span ** 3 / (48 * a) * 1e-12
        while load() > 0.05:
            if step(0.02) != 0: break
        rows.append(dict(F=Ft, a=a, EIs=EIs, f=free_free_freq()))
    return rows
