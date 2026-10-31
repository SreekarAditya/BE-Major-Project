"""Plane-stress continuum model of any beam in the population, for an independent check of the fibre model.

Same formulation as the 230 x 300 mm continuum model of the Review 2 work (cont230.py): ASDConcrete3D in
plane stress (enhanced quadrilaterals, IMPL-EX), bottom and top bars and 8 mm stirrups at 150 mm as truss
elements with Steel02, perfect bond. The concrete tension law uses the beam's sampled tensile strength.
Monotonic push in displacement control to span/100 or a 20% load drop.

Output per beam: first natural frequency, cracking load (first 5% loss of secant stiffness), midspan deflection
at the five stage loads of the fibre run (0.43 ... 1.00 of the hand yield load), peak load.
Usage: python3 cont_gen.py design.csv beam_id [beam_id ...] out.jsonl
"""
import sys, json, time, csv, math
import numpy as np
import openseespy.opensees as ops
import gen

ES, NU, RHO = 2.0e5, 0.2, 2.5e-9


def run(row):
    g = gen.geometry(row)
    fck, Ec, ft, fy = float(row['fck_MPa']), float(row['Ec_MPa']), float(row['ft_MPa']), float(row['fy_MPa'])
    L, b, h = g['span'], g['b'], g['h']
    nx = int(round(L / 50.0)); nx += nx % 6                     # about 50 mm columns, divisible by 6 for load points
    xs = np.linspace(0, L, nx + 1)
    yb, yt = g['y_bot'], g['y_top']
    ys = sorted(set([0.0, round(yb / 2, 1), round(yb, 1), round(yt, 1), round((yt + h) / 2, 1), h] +
                    [round(v, 1) for v in np.linspace(yb, yt, max(4, int(round((yt - yb) / 25))) + 1)]))
    ny = len(ys) - 1
    nid = lambda i, j: j * (nx + 1) + i + 1
    ecr = ft / Ec
    Te = [0, ecr, 2 * ecr, 5 * ecr, 10 * ecr, 20 * ecr, 100 * ecr]; Ts = [0, ft, 0.6 * ft, 0.3 * ft, 0.1 * ft, 0.05 * ft, 0.05 * ft]
    Td = [0, 0] + [1 - s / (Ec * e) for e, s in zip(Te[2:], Ts[2:])]
    fcm = 0.8 * fck; e0 = 0.002
    Ce = [0, 0.4 * fcm / Ec, 0.001, 0.0015, 0.002, 0.0035, 0.006]
    par = lambda e: fcm * (2 * e / e0 - (e / e0) ** 2)
    Cs = [0, 0.4 * fcm, par(0.001), par(0.0015), fcm, 0.85 * fcm, 0.2 * fcm]
    Cd = [0, 0] + [0.3 * (1 - s / (Ec * e)) for e, s in zip(Ce[2:], Cs[2:])]
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 2)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs): ops.node(nid(i, j), float(x), float(y))
    F = lambda v: [float(q) for q in v]
    ops.nDMaterial('ASDConcrete3D', 1, Ec, NU, '-Te', *F(Te), '-Ts', *F(Ts), '-Td', *F(Td), '-Ce', *F(Ce), '-Cs', *F(Cs), '-Cd', *F(Cd), '-implex')
    ops.nDMaterial('PlaneStress', 2, 1)
    ops.uniaxialMaterial('Steel02', 3, fy, ES, 0.01, 18, 0.925, 0.15)
    ops.uniaxialMaterial('Steel02', 4, 415.0, ES, 0.01, 18, 0.925, 0.15)
    e = 1
    for j in range(ny):
        for i in range(nx):
            ops.element('enhancedQuad', e, nid(i, j), nid(i + 1, j), nid(i + 1, j + 1), nid(i, j + 1), b, 'PlaneStress', 2); e += 1
    jb, jt = ys.index(round(yb, 1)), ys.index(round(yt, 1))
    Ab = g['n_bot'] * gen.bar_area(g['d_bot']); At = g['n_top'] * gen.bar_area(g['d_top']); Asv = 2 * gen.bar_area(8.0)
    first_bar = e
    for i in range(nx):
        ops.element('truss', e, nid(i, jb), nid(i + 1, jb), Ab, 3); e += 1
        ops.element('truss', e, nid(i, jt), nid(i + 1, jt), At, 3); e += 1
    step_st = max(1, int(round(150.0 / (L / nx))))
    for i in range(step_st, nx, step_st):
        for j in range(jb, jt): ops.element('truss', e, nid(i, j), nid(i, j + 1), Asv, 4); e += 1
    dx = xs[1] - xs[0]
    for j in range(ny + 1):
        for i in range(nx + 1):
            hy = (ys[min(j + 1, ny)] - ys[max(j - 1, 0)]) / 2
            m = RHO * b * dx * hy * (0.5 if i in (0, nx) else 1); ops.mass(nid(i, j), m, m)
    ops.fix(nid(0, 0), 1, 1); ops.fix(nid(nx, 0), 0, 1)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
    if g['load'] == 'four_point':
        for ic in (nx // 3, 2 * nx // 3):
            for di, w in ((-1, 0.25), (0, 0.5), (1, 0.25)): ops.load(nid(ic + di, ny), 0, -0.5 * w)
    else:
        for i in range(1, nx): ops.load(nid(i, ny), 0, -1.0 / (nx - 1))
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('UmfPack')
    ops.test('NormDispIncr', 1e-5, 100); ops.algorithm('Newton')
    w2 = ops.eigen('-genBandArpack', 2); f1 = float(math.sqrt(min(w2)) / (2 * math.pi))
    cnode = nid(nx // 2, ny)
    def step(du):
        ops.integrator('DisplacementControl', cnode, 2, du); ops.analysis('Static')
        if ops.analyze(1) == 0: return 0
        for alg in (('KrylovNewton',), ('ModifiedNewton', '-initial')):
            ops.algorithm(*alg); ok = ops.analyze(1); ops.algorithm('Newton')
            if ok == 0: return 0
        return 1
    state = lambda: (ops.getLoadFactor(1) / 1e3, -ops.nodeDisp(nid(nx // 2, 0), 2))
    du = 0.1 * L / 3000.0; P = [0.0]; D = [0.0]; ok = True
    while D[-1] < L / 100:
        if step(-du) != 0: ok = False; break
        p, d = state(); P.append(p); D.append(d)
        if p < 0.8 * max(P) and d > L / 300: break
    P, D = np.array(P), np.array(D)
    Py = float(row['Py_hand_kN']); fr = [float(x) for x in row['stage_fractions'].split(';')]
    ip = int(np.argmax(P))
    stage_defl = [float(np.interp(f * Py, P[:ip + 1], D[:ip + 1])) if f * Py <= P[ip] else None for f in fr]
    k0 = P[1] / D[1]; sec = P[1:] / np.maximum(D[1:], 1e-12)
    icr = int(np.argmax(sec < 0.95 * k0)) + 1
    return dict(f1_hz=f1, Pcr_kN=float(P[icr]), Pmax_kN=float(P[ip]), defl_at_peak_mm=float(D[ip]),
                stage_deflection_mm=stage_defl, push_complete=ok, mesh=[nx, ny],
                curve=[[round(float(D[i]), 4), round(float(P[i]), 3)] for i in np.linspace(0, len(P) - 1, min(60, len(P))).astype(int)])


if __name__ == '__main__':
    design = sys.argv[1]; ids = [int(x) for x in sys.argv[2:-1]]; out = sys.argv[-1]
    rows = {int(r['beam']): r for r in csv.DictReader(open(design))}
    with open(out, 'a') as fh:
        for i in ids:
            t = time.time()
            try: rec = dict(beam=i, ok=True, **run(rows[i]))
            except Exception as e: rec = dict(beam=i, ok=False, err=str(e))
            rec['sec'] = round(time.time() - t, 1); fh.write(json.dumps(rec) + '\n'); fh.flush()
