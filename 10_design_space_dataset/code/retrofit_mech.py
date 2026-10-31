"""Retrofit by mechanics: strengthening added to the damaged fibre model, then reloaded to failure.

The beam is first taken through the same staged damage history as gen.py, up to and including the
installation stage, and unloaded. The strengthening is then added as parallel displacement-based
elements on the same nodes. Every strengthening fibre is given an initial strain equal to minus the strain
of the damaged beam at that fibre's position, so it is stress-free when installed and only carries the
strain added afterwards (installation on the unloaded beam; dead load is not modelled).

Schemes:
  laminate  carbon fibre strips 50 x 1.2 mm (2 strips if b < 260 mm, else 3), Ef 165 GPa, epsilon_fu 0.017;
            tension only; the strip is lost when its added strain reaches the ACI PRC-440.2-23 debonding strain
            0.41 sqrt(fc'/(n Ef tf)) <= 0.9 epsilon_fu, with fc' = 0.8 fck of the beam
  plate     bonded steel plate 100 x 5 mm, fy 250 MPa, assumed anchored (no debonding)
  jacket    75 mm reinforced concrete U-jacket (soffit and both sides), M30 nominal, 2 bars of 12 mm Fe500,
            perfect bond; jacket concrete as a path-independent compression-only law (parabola to 0.8 x 30 MPa,
            then linear to 20% at 0.0035), tension neglected; its mass is added to the beam
  none      control: same history, no strengthening
"""
import math, json, sys, time, csv
import numpy as np
import openseespy.opensees as ops
import gen
from gen import NE, NMID, ES

LOB_X = [0.0, (1 - math.sqrt(3 / 7)) / 2, 0.5, (1 + math.sqrt(3 / 7)) / 2, 1.0]
LOB_W = [0.05, 49 / 180, 32 / 90, 49 / 180, 0.05]
_tag = [10000]


def newtag():
    _tag[0] += 1; return _tag[0]


def ip_strain_fields(le):
    """Axial strain and curvature at the 5 Lobatto points of each element, from the current nodal
    displacements with the displacement-based (Hermite) interpolation that the add-on elements use."""
    out = []
    for e in range(1, NE + 1):
        n1, n2 = e, e + 1
        u1, v1, t1 = ops.nodeDisp(n1); u2, v2, t2 = ops.nodeDisp(n2)
        eps = (u2 - u1) / le
        row = []
        for x in LOB_X:
            k = ((-6 + 12 * x) * v1 + le * (-4 + 6 * x) * t1 + (6 - 12 * x) * v2 + le * (-2 + 6 * x) * t2) / le ** 2
            row.append((eps, k))
        out.append(row)
    return out


def fibre_list(g, q, scheme):
    """(y from centroid of the original section, area, material builder) for the strengthening."""
    h, b = g['h'], g['b']; yb = -h / 2; F = []
    if scheme == 'laminate':
        lam = g.get('laminate', {})
        n = lam.get('n', 2 if b < 260 else 3); tf = lam.get('tf', 1.2); wf = lam.get('wf', 50.0)
        Ef = lam.get('Ef', 165000.0); efu = lam.get('efu', 0.017)
        fc = 0.8 * q['fck']
        efd = min(0.41 * math.sqrt(fc / (1 * Ef * tf)), 0.9 * efu)
        def mat(e0, Ef=Ef, efd=efd):
            t1, t2, t3 = newtag(), newtag(), newtag()
            ops.uniaxialMaterial('Elastic', t1, Ef, 0.0, 1e-6 * Ef)            # no compression
            ops.uniaxialMaterial('MinMax', t2, t1, '-max', efd)                 # lost at the debonding strain
            ops.uniaxialMaterial('InitStrainMaterial', t3, t2, -e0); return t3
        F.append((yb - tf / 2, n * wf * tf, mat))
        info = dict(n_strips=n, Af_mm2=n * wf * tf, eps_fd=efd)
    elif scheme == 'plate':
        wp, tp = 100.0, 5.0                                                 # standard flat 100 x 5 mm
        def mat(e0):
            t1, t2 = newtag(), newtag()
            ops.uniaxialMaterial('Steel02', t1, 250.0, ES, 0.01, 18, 0.925, 0.15)
            ops.uniaxialMaterial('InitStrainMaterial', t2, t1, -e0); return t2
        F.append((yb - tp / 2, wp * tp, mat)); info = dict(plate_mm=[wp, tp])
    elif scheme == 'jacket':
        t, fckj = 75.0, 30.0; Ecj = 5000 * math.sqrt(fckj); ftj = 0.7 * math.sqrt(fckj); fcm = 0.8 * fckj
        def cmat(e0):
            t1, t2 = newtag(), newtag()
            e2 = 2 * fcm / Ecj                                              # parabola to fcm at e2, linear to 0.2 fcm at 0.0035
            es = [-0.0035, -e2] + [-e2 * k / 6 for k in range(5, 0, -1)] + [0.0, 1.0]
            ss = [-0.2 * fcm, -fcm] + [-fcm * (2 * (k / 6) - (k / 6) ** 2) for k in range(5, 0, -1)] + [0.0, 1e-6]
            ops.uniaxialMaterial('ElasticMultiLinear', t1, 0.0, '-strain', *es, '-stress', *ss)   # path-independent, no tension
            ops.uniaxialMaterial('InitStrainMaterial', t2, t1, -e0); return t2
        def smat(e0):
            t1, t2 = newtag(), newtag()
            ops.uniaxialMaterial('Steel02', t1, 500.0, ES, 0.01, 18, 0.925, 0.15)
            ops.uniaxialMaterial('InitStrainMaterial', t2, t1, -e0); return t2
        nb = 4; dy = t / nb                                                 # soffit slab, width b + 2t
        for k in range(nb): F.append((yb - t + (k + 0.5) * dy, (b + 2 * t) * dy, cmat))
        ns = max(8, int(h / 25)); dy = h / ns                              # two side strips, full depth
        for k in range(ns): F.append((yb + (k + 0.5) * dy, 2 * t * dy, cmat))
        F.append((yb - t + 40.0, 2 * gen.bar_area(12), smat))
        info = dict(jacket_mm=t, jacket_area_mm2=(b + 2 * t) * t + 2 * t * h)
    else:
        info = {}
    return F, info


def strengthen(bm, scheme):
    g, q = bm.g, bm.q
    F, info = fibre_list(g, q, scheme)
    if not F: return info
    fields = ip_strain_fields(bm.le)
    for e in range(1, NE + 1):
        secs = []
        for ip, (eps, k) in enumerate(fields[e - 1]):
            st = newtag(); ops.section('Fiber', st, '-noCentroid')   # strains about the original centroid
            for (y, A, mk) in F:
                e0 = eps - y * k
                ops.fiber(y, 0.0, A, mk(e0))
            secs.append(st)
        it = newtag()
        ops.beamIntegration('UserDefined', it, 5, *secs, *LOB_X, *LOB_W)
        ops.element('dispBeamColumn', 5000 + e, e, e + 1, 1, it)
    if scheme == 'jacket':                                                  # added mass
        mline = gen.RHO * (info['jacket_area_mm2'] + g['b'] * g['h'])       # nodal mass is replaced, so beam + jacket
        for i in range(NE + 1):
            m = mline * bm.le * (0.5 if i in (0, NE) else 1.0)
            ops.mass(i + 1, m, m, 0.0)
    ops.wipeAnalysis(); ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-8, 100); ops.algorithm('Newton')
    ops.integrator('LoadControl', 0.0); ops.analysis('Static'); ops.analyze(1)   # null step: elements see the current state
    return info


def addon_force():
    """Largest end moment carried by the strengthening elements (check that installation is stress-free)."""
    m = 0.0
    for e in range(1, NE + 1):
        f = ops.eleResponse(5000 + e, 'force'); m = max(m, abs(f[2]), abs(f[5]))
    return m


def run_retrofit(g, q, Pd, Ps, stages, push_to, scheme, install_after=4):
    """Damage history to stage `install_after`, strengthen, then service cycle, frequencies and push."""
    bm = gen.Beam(g, q); out = dict(scheme=scheme)
    for k, Pst in enumerate(stages[:install_after], start=1):
        bm.load_to(Pst); bm.unload()
    out['residual_before_mm'] = float(bm.state()[1])
    out['f_before_hz'] = bm.freqs()
    out['delta_d_before_mm'], _ = bm.cycle(Pd)
    out.update(strengthen(bm, scheme))
    if scheme != 'none':
        out['install_moment_Nmm'] = addon_force()
    out['delta_d_after_mm'], _ = bm.cycle(Pd)
    out['f_after_hz'] = bm.freqs()
    out['delta_s_after_mm'], sec = bm.cycle(Ps, with_section=True)
    out['service_steel_stress_after_MPa'] = sec['steel_stress']
    env = []; Pmax = 0.0; ok = True
    while bm.state()[1] < push_to:
        if bm.step(-bm.du * 2.5) != 0: ok = False; break
        p, d = bm.state(); Pmax = max(Pmax, p); env.append((d, p))
    out['Pmax_kN'] = float(Pmax); out['push_complete'] = ok
    if env:
        env = np.array(env); idx = np.linspace(0, len(env) - 1, min(40, len(env))).astype(int)
        out['envelope'] = [[round(float(env[i, 0]), 4), round(float(env[i, 1]), 3)] for i in idx]
    return out


if __name__ == '__main__':
    design, i0, i1, outfn = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    rows = list(csv.DictReader(open(design))); done = set()
    try:
        for line in open(outfn):
            r = json.loads(line); done.add((r['beam'], r['scheme']))
    except FileNotFoundError:
        pass
    with open(outfn, 'a') as fh:
        for row in rows[i0:i1]:
            i = int(row['beam']); g = gen.geometry(row)
            q = dict(fck=float(row['fck_MPa']), Ec=float(row['Ec_MPa']), ft=float(row['ft_MPa']),
                     ets=float(row['ets']), fy=float(row['fy_MPa']))
            Py = float(row['Py_hand_kN']); fr = [float(x) for x in row['stage_fractions'].split(';')]
            for scheme in ('none', 'laminate', 'plate', 'jacket'):
                if (i, scheme) in done: continue
                t = time.time()
                try:
                    rec = dict(beam=i, ok=True, **run_retrofit(g, q, 0.185 * Py, 0.37 * Py, [f * Py for f in fr], g['span'] / 100, scheme))
                except Exception as e:
                    rec = dict(beam=i, scheme=scheme, ok=False, err=str(e))
                rec['sec'] = round(time.time() - t, 1)
                fh.write(json.dumps(rec) + '\n'); fh.flush()
