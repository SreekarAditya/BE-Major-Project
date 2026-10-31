"""StrucIQ beam population generator: staged damage of simply supported reinforced concrete beams.

Same fibre model and solver as the 230 x 300 mm reference Monte Carlo (mc.py), with the whole beam
parameterised: span, section, cover, bars, concrete and steel grades, load arrangement.
Units: N, mm, MPa. Total load P in kN.

Per beam:  undamaged check, then for each damage stage:
  load to the stage load, record peak state (deflection, steel stress and strain, curvature, neutral axis,
  IS 456 Annex F crack width) -> unload -> residual deflection -> diagnostic cycle (P_d) ->
  first three natural frequencies of the unloaded beam -> service cycle (P_s, with crack width under P_s);
  finally a push to span/100 for peak load and a 40-point envelope.

Usage:  python3 gen.py design.csv first last out.jsonl
"""
import sys, json, time, math, csv
import numpy as np
import openseespy.opensees as ops

ES, RHO = 2.0e5, 2.5e-9              # steel modulus; concrete density (tonne/mm^3)
NE = 24                               # force-based elements, as in the reference model
NMID = NE // 2 + 1


def bar_area(d): return math.pi * d * d / 4


def hand_yield_load(g):
    """First-yield load (kN) from cracked elastic section, nominal Ec of the grade."""
    m = ES / (5000 * math.sqrt(g['grade']))
    rho = g['As'] / (g['b'] * g['d'])
    k = math.sqrt(2 * rho * m + (rho * m) ** 2) - rho * m
    My = g['As'] * g['fy_nom'] * g['d'] * (1 - k / 3)          # N mm
    lever = g['span'] / 6 if g['load'] == 'four_point' else g['span'] / 8
    return My / lever / 1e3


class Beam:
    def __init__(self, g, q):
        self.g, self.q = g, q
        L, b, h = g['span'], g['b'], g['h']
        self.le = L / NE
        ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
        for i in range(NE + 1): ops.node(i + 1, i * self.le, 0.)
        ops.fix(1, 1, 1, 0); ops.fix(NE + 1, 0, 1, 0)
        fcm = 0.8 * q['fck']
        ops.uniaxialMaterial('Concrete02', 1, -fcm, -2 * fcm / q['Ec'], -0.2 * fcm, -0.0035, 0.1, q['ft'], q['ets'] * q['Ec'])
        ops.uniaxialMaterial('Steel02', 2, q['fy'], ES, 0.01, 18, 0.925, 0.15)
        yb = -h / 2
        self.y_bot = yb + g['y_bot']; self.y_top = yb + g['y_top']
        ops.section('Fiber', 1)
        ops.patch('rect', 1, max(60, int(round(h / 5))), 1, yb, -b / 2, h / 2, b / 2)
        ops.layer('straight', 2, g['n_bot'], bar_area(g['d_bot']), self.y_bot, 0, self.y_bot, 0)
        ops.layer('straight', 2, g['n_top'], bar_area(g['d_top']), self.y_top, 0, self.y_top, 0)
        ops.geomTransf('Linear', 1); ops.beamIntegration('Lobatto', 1, 1, 5)
        for i in range(NE): ops.element('forceBeamColumn', i + 1, i + 1, i + 2, 1, 1, '-iter', 200, 1e-12)
        for i in range(NE + 1):
            mi = RHO * b * h * self.le * (0.5 if i in (0, NE) else 1.)
            ops.mass(i + 1, mi, mi, 0.)
        ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
        if g['load'] == 'four_point':
            for n in (NE // 3 + 1, 2 * NE // 3 + 1): ops.load(n, 0, -0.5, 0)
        else:                                      # uniform load lumped at the 23 interior nodes
            for n in range(2, NE + 1): ops.load(n, 0, -1.0 / (NE - 1), 0)
        ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
        ops.test('NormDispIncr', 1e-8, 100); ops.algorithm('Newton')
        self.du = g.get('du', 0.02 * L / 3000.0)

    # ---- solver (identical strategy to mc.py)
    def _try(self, du):
        ops.integrator('DisplacementControl', NMID, 2, du); ops.analysis('Static')
        for alg in (('Newton',), ('ModifiedNewton', '-initial'), ('NewtonLineSearch',), ('KrylovNewton',)):
            ops.algorithm(*alg)
            if ops.analyze(1) == 0:
                ops.algorithm('Newton'); return 0
        ops.algorithm('Newton'); return -1

    def step(self, du):
        if self._try(du) == 0: return 0
        ops.test('NormDispIncr', 1e-6, 200)
        for _ in range(10):
            if self._try(du / 10) != 0:
                for _ in range(10):                    # deeper sub-stepping, as in the beam-56 rerun
                    if self._try(du / 100) != 0:
                        ops.test('NormDispIncr', 1e-8, 100); return -1
        ops.test('NormDispIncr', 1e-8, 100); return 0

    def state(self): return ops.getLoadFactor(1) / 1e3, -ops.nodeDisp(NMID, 2)

    def freqs(self):
        """First three vertical bending frequencies of the beam in its current (unloaded) state."""
        w2 = ops.eigen(6); out = []
        for m, w in enumerate(w2, start=1):
            vx = max(abs(ops.nodeEigenvector(n, m, 1)) for n in range(1, NE + 2))
            vy = max(abs(ops.nodeEigenvector(n, m, 2)) for n in range(1, NE + 2))
            if vy > vx: out.append(float(math.sqrt(max(w, 0)) / (2 * math.pi)))
        return (out + [float('nan')] * 3)[:3]

    # ---- midspan section response
    def section(self):
        g = self.g; h = g['h']
        ele, sec = NE // 2, 5                        # section at the midspan node
        eps, kap = ops.eleResponse(ele, 'section', sec, 'deformation')[:2]
        st = lambda y: eps - y * kap                  # fibre strain, y from centroid
        e_bot, e_top = st(-h / 2), st(h / 2)
        if e_bot < e_top:                             # make tension at the soffit positive
            e_bot, e_top = -e_bot, -e_top
        es = st(self.y_bot) if st(-h / 2) >= st(h / 2) else -st(self.y_bot)
        if e_bot > 0 > e_top:
            x = h * (-e_top) / (e_bot - e_top)        # neutral axis depth from top
        else:
            x = float('nan')
        try:
            ss = ops.eleResponse(ele, 'section', sec, 'fiber', self.y_bot, 0.0, 2, 'stressStrain')[0]
            ss = abs(ss)
        except Exception:
            ss = float('nan')
        return dict(curv=abs(kap), e_soffit=e_bot, e_steel=es, x=x, steel_stress=ss,
                    crack_w=self.crack_width(e_bot, x))

    def crack_width(self, e1, x):
        """IS 456:2000 Annex F, at the soffit midway between bottom bars."""
        g = self.g
        if not (x == x) or e1 <= 0: return 0.0
        h, b, d, As = g['h'], g['b'], g['d'], g['As']
        n, phi, cmin = g['n_bot'], g['d_bot'], g['cover'] + g['d_stir']
        s = (b - 2 * cmin - phi) / max(n - 1, 1)
        acr = math.hypot(s / 2, cmin + phi / 2) - phi / 2
        em = e1 - b * (h - x) * (h - x) / (3 * ES * As * (d - x))
        if em <= 0: return 0.0
        return 3 * acr * em / (1 + 2 * (acr - cmin) / (h - x))

    def load_to(self, Pt):
        P = []; D = []
        while True:
            if self.step(-self.du) != 0: raise RuntimeError('nonconvergence')
            p, d = self.state(); P.append(p); D.append(d)
            if p >= Pt: return np.array(P), np.array(D)
            if d > self.g['span'] / 100 or len(P) > 6000: raise RuntimeError('target load not reached')

    def unload(self):
        while ops.getLoadFactor(1) > 0.02e3:
            if self.step(self.du) != 0: break

    def cycle(self, Pt, with_section=False):
        d0 = self.state()[1]; P, D = self.load_to(Pt)
        sec = self.section() if with_section else None
        self.unload()
        return float(np.interp(Pt, P, D) - d0), sec


def run(g, q, Pd, Ps, stages, push_to):
    bm = Beam(g, q); rows = []
    for k, Pst in enumerate((None,) + tuple(stages)):
        rec = dict(stage=k, damage_kN=float(Pst or 0.0))
        if Pst is not None:
            try:
                P, D = bm.load_to(Pst)
            except RuntimeError as e:
                if k <= 2: raise                       # early-stage failure: the whole beam is reported as failed
                rows.append(dict(stage=k, damage_kN=float(Pst), reached=False, reason=str(e))); break
            rec['peak_deflection_mm'] = float(D[-1]); rec['peak'] = bm.section()
            bm.unload()
        rec['residual_mm'] = float(bm.state()[1])
        rec['delta_d_mm'], _ = bm.cycle(Pd)
        rec['freq_hz'] = bm.freqs()
        if Pst is not None:
            rec['delta_s_mm'], rec['service'] = bm.cycle(Ps, with_section=True)
        rows.append(rec)
    env = []; Pmax = 0.0
    if rows[-1].get('reached', True) is False:             # domain may be unusable after a failed stage
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


def geometry(row):
    g = dict(span=float(row['span_mm']), b=float(row['b_mm']), h=float(row['h_mm']), cover=float(row['cover_mm']),
             d_stir=float(row['d_stir_mm']), n_bot=int(row['n_bot']), d_bot=float(row['d_bot_mm']),
             n_top=int(row['n_top']), d_top=float(row['d_top_mm']), grade=float(row['grade_MPa']),
             fy_nom=float(row['fy_nom_MPa']), load=row['load'])
    g['y_bot'] = g['cover'] + g['d_stir'] + g['d_bot'] / 2
    g['y_top'] = g['h'] - g['cover'] - g['d_stir'] - g['d_top'] / 2
    g['d'] = g['h'] - g['y_bot']; g['As'] = g['n_bot'] * bar_area(g['d_bot'])
    return g


if __name__ == '__main__':
    design, i0, i1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    rows = list(csv.DictReader(open(design)))
    done = set()
    try:
        for line in open(out): done.add(json.loads(line)['beam'])
    except FileNotFoundError:
        pass
    with open(out, 'a') as fh:
        for row in rows[i0:i1]:
            i = int(row['beam'])
            if i in done: continue
            g = geometry(row)
            q = dict(fck=float(row['fck_MPa']), Ec=float(row['Ec_MPa']), ft=float(row['ft_MPa']),
                     ets=float(row['ets']), fy=float(row['fy_MPa']))
            Py = float(row['Py_hand_kN'])
            fr = [float(x) for x in row['stage_fractions'].split(';')]
            t = time.time()
            try:
                st, Pmax, env = run(g, q, 0.185 * Py, 0.37 * Py, [f * Py for f in fr], g['span'] / 100)
                rec = dict(beam=i, ok=True, stages=st, Pmax_kN=Pmax, envelope=env)
            except Exception as e:
                rec = dict(beam=i, ok=False, err=str(e))
            rec['sec'] = round(time.time() - t, 1)
            fh.write(json.dumps(rec) + '\n'); fh.flush()
