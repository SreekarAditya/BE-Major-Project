"""Corrosion stage: the staged damage protocol of gen.py on a beam whose reinforcement has corroded.

Uniform corrosion of all longitudinal bars with mass loss psi (%), represented by published relations:
  bar area           As_c  = As (1 - 0.01 psi)                         (uniform loss: mass loss = area loss)
  yield strength     fy_c  = fy (1 - 0.005 psi)                         Du, Clark & Chan (2005a), on the residual area
  ultimate strain    esu_c = esu (1 - 0.05 psi), esu = 0.08 assumed    Du, Clark & Chan (2005b); the bar carries no
                                                                        stress beyond esu_c (rupture)
  cover concrete     fc_c  = fc / (1 + K eps1 / eps_c0)                 Coronelli & Gambarova (2004), K = 0.1,
                     eps1  = n_bars w_cr / b,  w_cr = 2 pi (nu_rs - 1) X, nu_rs = 2, X = loss of bar radius;
                     applied to the concrete between the top face and the top bars (compression zone)
Not represented: loss of bond, pitting, stirrup corrosion, the change of mass.

The stage loads are the same absolute loads as for the uncorroded beam (fractions of its Py_hand_kN), so that
the corroded and uncorroded beams can be compared at equal load. A stage the corroded beam cannot reach is
recorded as unreached with the largest load reached in the attempt (peak_in_attempt_kN): when the reason is
'target load not reached' this is the corroded beam's peak load up to span/100, and the 40-point curve of that
attempt is kept (attempt_envelope).

Usage:  python3 corrosion.py design.csv first last out.jsonl      (levels in LEVELS)
"""
import sys, json, time, math, csv
import numpy as np
import openseespy.opensees as ops
import gen
from gen import NE, ES, RHO, bar_area

LEVELS = (5.0, 10.0, 15.0)           # mass loss, % (Du et al. tested up to about 16%)
ESU0, K_CG, NU_RS = 0.08, 0.1, 2.0


def corroded(g, q, psi):
    """Corroded bar areas, steel strength, rupture strain and reduced top-cover concrete strength."""
    f = 0.01 * psi
    c = dict(psi=psi, area_factor=1 - f, fy=q['fy'] * (1 - 0.005 * psi), esu=ESU0 * max(1 - 0.05 * psi, 0.0))
    fcm = 0.8 * q['fck']; ec0 = 2 * fcm / q['Ec']
    X = g['d_top'] / 2 * (1 - math.sqrt(1 - f))                       # loss of radius of the top bars
    w = 2 * math.pi * (NU_RS - 1) * X
    eps1 = g['n_top'] * w / g['b']
    c['fc_cover'] = fcm / (1 + K_CG * eps1 / ec0)
    c['top_cover_depth'] = g['cover'] + g['d_stir'] + g['d_top'] / 2  # top face to top bar centre
    return c


class CBeam(gen.Beam):
    """gen.Beam with corroded steel and cover concrete. Everything else (mesh, loading, solver) is gen.Beam."""

    def __init__(self, g, q, c):
        self.g, self.q, self.c = g, q, c
        L, b, h = g['span'], g['b'], g['h']
        self.le = L / NE
        ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
        for i in range(NE + 1): ops.node(i + 1, i * self.le, 0.)
        ops.fix(1, 1, 1, 0); ops.fix(NE + 1, 0, 1, 0)
        fcm = 0.8 * q['fck']
        ops.uniaxialMaterial('Concrete02', 1, -fcm, -2 * fcm / q['Ec'], -0.2 * fcm, -0.0035, 0.1, q['ft'], q['ets'] * q['Ec'])
        fcc = c['fc_cover']                                                # cracked cover: same strain at peak as gen.py's law
        ops.uniaxialMaterial('Concrete02', 3, -fcc, -2 * fcm / q['Ec'], -0.2 * fcc, -0.0035, 0.1, q['ft'], q['ets'] * q['Ec'])
        ops.uniaxialMaterial('Steel02', 4, c['fy'], ES, 0.01, 18, 0.925, 0.15)
        ops.uniaxialMaterial('MinMax', 2, 4, '-min', -1.0, '-max', c['esu'])
        yb = -h / 2
        self.y_bot = yb + g['y_bot']; self.y_top = yb + g['y_top']
        ycov = h / 2 - c['top_cover_depth']
        ny = max(60, int(round(h / 5))); ncov = max(2, int(round(ny * c['top_cover_depth'] / h)))
        ops.section('Fiber', 1)
        ops.patch('rect', 1, ny - ncov, 1, yb, -b / 2, ycov, b / 2)
        ops.patch('rect', 3, ncov, 1, ycov, -b / 2, h / 2, b / 2)
        ops.layer('straight', 2, g['n_bot'], bar_area(g['d_bot']) * c['area_factor'], self.y_bot, 0, self.y_bot, 0)
        ops.layer('straight', 2, g['n_top'], bar_area(g['d_top']) * c['area_factor'], self.y_top, 0, self.y_top, 0)
        ops.geomTransf('Linear', 1); ops.beamIntegration('Lobatto', 1, 1, 5)
        for i in range(NE): ops.element('forceBeamColumn', i + 1, i + 1, i + 2, 1, 1, '-iter', 200, 1e-12)
        for i in range(NE + 1):
            mi = RHO * b * h * self.le * (0.5 if i in (0, NE) else 1.)
            ops.mass(i + 1, mi, mi, 0.)
        ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
        if g['load'] == 'four_point':
            for n in (NE // 3 + 1, 2 * NE // 3 + 1): ops.load(n, 0, -0.5, 0)
        else:
            for n in range(2, NE + 1): ops.load(n, 0, -1.0 / (NE - 1), 0)
        ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
        ops.test('NormDispIncr', 1e-8, 100); ops.algorithm('Newton')
        self.du = g.get('du', 0.02 * L / 3000.0)

    def load_to(self, Pt):
        """gen.Beam.load_to, also keeping the largest load reached in the attempt (self.attempt_peak)."""
        P = []; D = []; self.attempt_peak = 0.0
        while True:
            if self.step(-self.du) != 0: raise RuntimeError('nonconvergence')
            p, d = self.state(); P.append(p); D.append(d); self.attempt_peak = max(self.attempt_peak, p)
            self.attempt_curve = (P, D)
            if p >= Pt: return np.array(P), np.array(D)
            if d > self.g['span'] / 100 or len(P) > 6000: raise RuntimeError('target load not reached')

    def crack_width(self, e1, x):
        """IS 456 Annex F with the corroded steel area (gen.Beam uses the nominal area)."""
        g = dict(self.g); g['As'] = g['As'] * self.c['area_factor']
        save = self.g; self.g = g
        try: return gen.Beam.crack_width(self, e1, x)
        finally: self.g = save


def sample(P, D, n=40):
    """40-point (deflection, load) curve, as for the push envelope."""
    if not P: return []
    idx = np.linspace(0, len(P) - 1, min(n, len(P))).astype(int)
    return [[round(float(D[i]), 4), round(float(P[i]), 3)] for i in idx]


def run(bm, Pd, Ps, stages, push_to):
    """gen.run applied to an already built beam. Differences: a stage the corroded beam is too weak to reach
    (deflection passes span/100 first) is recorded, with the largest load reached, at any stage; only
    nonconvergence before the third stage fails the run, as in gen.run."""
    rows = []
    for k, Pst in enumerate((None,) + tuple(stages)):
        rec = dict(stage=k, damage_kN=float(Pst or 0.0))
        if Pst is not None:
            try:
                P, D = bm.load_to(Pst)
            except RuntimeError as e:
                # the corroded beam may be too weak for a stage load: that is a result, not a failure
                if k <= 2 and str(e) == 'nonconvergence': raise
                rows.append(dict(stage=k, damage_kN=float(Pst), reached=False, reason=str(e),
                                 peak_in_attempt_kN=float(bm.attempt_peak), deflection_at_stop_mm=float(bm.state()[1]),
                                 attempt_envelope=sample(*bm.attempt_curve))); break
            rec['peak_deflection_mm'] = float(D[-1]); rec['peak'] = bm.section()
            bm.unload()
        rec['residual_mm'] = float(bm.state()[1])
        rec['delta_d_mm'], _ = bm.cycle(Pd)
        rec['freq_hz'] = bm.freqs()
        if Pst is not None:
            rec['delta_s_mm'], rec['service'] = bm.cycle(Ps, with_section=True)
        rows.append(rec)
    env = []; Pmax = 0.0
    if rows[-1].get('reached', True) is False:
        return rows, float('nan'), []
    push_complete = True
    while bm.state()[1] < push_to:
        if bm.step(-bm.du * 2.5) != 0: push_complete = False; break
        p, d = bm.state(); Pmax = max(Pmax, p); env.append((d, p))
    rows[-1]['push_complete'] = push_complete
    env = np.array(env)
    if len(env):
        idx = np.linspace(0, len(env) - 1, min(40, len(env))).astype(int)
        env = [[round(float(env[i, 0]), 4), round(float(env[i, 1]), 3)] for i in idx]
    return rows, float(Pmax), env


def run_corrosion(row, psi):
    g = gen.geometry(row)
    q = dict(fck=float(row['fck_MPa']), Ec=float(row['Ec_MPa']), ft=float(row['ft_MPa']), ets=float(row['ets']), fy=float(row['fy_MPa']))
    Py = float(row['Py_hand_kN']); fr = [float(x) for x in row['stage_fractions'].split(';')]
    c = corroded(g, q, psi)
    st, Pmax, env = run(CBeam(g, q, c), 0.185 * Py, 0.37 * Py, [f * Py for f in fr], g['span'] / 100)
    return dict(psi=psi, corrosion=c, stages=st, Pmax_kN=Pmax, envelope=env)


if __name__ == '__main__':
    design, i0, i1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    rows = list(csv.DictReader(open(design))); done = set()
    try:
        for line in open(out): r = json.loads(line); done.add((r['beam'], r['psi']))
    except FileNotFoundError:
        pass
    with open(out, 'a') as fh:
        for row in rows[i0:i1]:
            i = int(row['beam'])
            for psi in LEVELS:
                if (i, psi) in done: continue
                t = time.time()
                try: rec = dict(beam=i, ok=True, **run_corrosion(row, psi))
                except Exception as e: rec = dict(beam=i, psi=psi, ok=False, err=str(e))
                rec['sec'] = round(time.time() - t, 1); fh.write(json.dumps(rec) + '\n'); fh.flush()
