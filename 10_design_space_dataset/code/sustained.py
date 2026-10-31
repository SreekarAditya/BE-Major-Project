"""Sustained-load stage: creep and shrinkage of the beam under its service load over 50 years.

The beam of gen.py, with the concrete replaced by OpenSees' time-dependent TDConcrete (Knaack & Kurama 2018:
linear in compression, Tamai tension softening, creep and shrinkage by ACI 209R-92 time functions) and
displacement-based elements, which this material requires. Creep and shrinkage magnitudes follow IS 456:2000:
ultimate creep coefficient 1.6 for loading at 28 days (6.2.5.1) and total shrinkage strain 0.0003 (6.2.4.1).
Time functions: shrinkage t/(35 + t) from the start of drying, creep t^0.6/(10 + t^0.6) (ACI 209R-92 standard).

Timeline (days from casting): the analysis starts when the formwork is removed at 7 days, when drying also
begins; loading at 28 days. Two cases:
  service    the service load Ps = 0.37 Py_hand is applied at 28 days and held
  overload   the beam is first loaded to 0.80 Py_hand (the third damage stage) and unloaded at 28 days, then Ps is
             applied and held
At 28 days (just after loading) and after 1, 10 and 50 years under load, the following are recorded under the
sustained load: midspan deflection, tension steel stress and strain, curvature, neutral axis, IS 456 Annex F
crack width; the deflection increment under an added diagnostic load (0.185 Py_hand, short-term) and the first
three frequencies of the loaded beam. After 50 years the load is removed and the residual deflection,
diagnostic deflection and frequencies of the unloaded beam are recorded. Short-term load changes are made with
creep switched off, so they are instantaneous.

Usage:  python3 sustained.py design.csv first last out.jsonl
"""
import sys, json, time, math, csv
import numpy as np
import openseespy.opensees as ops
import gen
from gen import NE, NMID, ES, RHO, bar_area

PHI_U, EPS_SH_U = 1.6, -300e-6                  # IS 456:2000 6.2.5.1 and 6.2.4.1
PSI_SH, PSI_CR1, PSI_CR2, BETA = 35.0, 0.6, 10.0, 0.4
T_CAST, AGE_DRY, AGE_LOAD = 2.0, 7.0, 28.0       # TDConcrete needs a casting time of at least 2 days
YEARS = (1, 10, 50)
SCALE = 1e6                                       # N per unit load factor in a ramp pattern (keeps time shifts small)


class TDBeam(gen.Beam):
    def __init__(self, g, q):
        self.g, self.q = g, q
        L, b, h = g['span'], g['b'], g['h']
        self.le = L / NE
        ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
        for i in range(NE + 1): ops.node(i + 1, i * self.le, 0.)
        ops.fix(1, 1, 1, 0); ops.fix(NE + 1, 0, 1, 0)
        fcm = 0.8 * q['fck']
        ops.uniaxialMaterial('TDConcrete', 1, -fcm, q['ft'], q['Ec'], BETA, T_CAST + AGE_DRY, EPS_SH_U, PSI_SH,
                             AGE_LOAD, PHI_U, PSI_CR1, PSI_CR2, T_CAST)
        ops.uniaxialMaterial('Steel02', 2, q['fy'], ES, 0.01, 18, 0.925, 0.15)
        yb = -h / 2
        self.y_bot = yb + g['y_bot']; self.y_top = yb + g['y_top']
        ops.section('Fiber', 1)
        ops.patch('rect', 1, max(60, int(round(h / 5))), 1, yb, -b / 2, h / 2, b / 2)
        ops.layer('straight', 2, g['n_bot'], bar_area(g['d_bot']), self.y_bot, 0, self.y_bot, 0)
        ops.layer('straight', 2, g['n_top'], bar_area(g['d_top']), self.y_top, 0, self.y_top, 0)
        ops.geomTransf('Linear', 1); ops.beamIntegration('Lobatto', 1, 1, 5)
        for i in range(NE): ops.element('dispBeamColumn', i + 1, i + 1, i + 2, 1, 1)
        for i in range(NE + 1):
            mi = RHO * b * h * self.le * (0.5 if i in (0, NE) else 1.)
            ops.mass(i + 1, mi, mi, 0.)
        ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
        ops.test('NormDispIncr', 1e-8, 100); ops.algorithm('Newton')
        self.du = g.get('du', 0.02 * L / 3000.0)
        self.P = 0.0; self.t = T_CAST + AGE_DRY; self.k = 1; self.ramp_t0 = None   # analysis starts at form removal (7 days)
        ops.setTime(self.t); ops.setCreep(0)
        ops.integrator('LoadControl', 0.0); ops.analysis('Static'); ops.analyze(1)

    def state(self):
        """Total load on the beam (kN) and midspan deflection (mm)."""
        extra = (ops.getTime() - self.ramp_t0) * SCALE / 1e3 * self.sign if self.ramp_t0 is not None else 0.0
        return self.P + extra, -ops.nodeDisp(NMID, 2)

    def _pattern(self, sign):
        self.k += 1; k = self.k; t = ops.getTime()
        ops.timeSeries('Path', k, '-time', t, t + 1e3, '-values', 0.0, 1e3)
        ops.pattern('Plain', k, k)
        if self.g['load'] == 'four_point':
            for n in (NE // 3 + 1, 2 * NE // 3 + 1): ops.load(n, 0, -0.5 * sign * SCALE, 0)
        else:
            for n in range(2, NE + 1): ops.load(n, 0, -sign * SCALE / (NE - 1), 0)
        self.ramp_t0, self.sign = t, sign

    def ramp(self, dP):
        """Instantaneous load change by dP kN (creep off), then hold the new load constant."""
        ops.setCreep(0); sign = 1.0 if dP > 0 else -1.0
        self._pattern(sign); target = self.P + dP; P = []; D = []
        while True:
            if self.step(-sign * self.du) != 0: raise RuntimeError('nonconvergence')
            p, d = self.state(); P.append(p); D.append(d)
            if (sign > 0 and p >= target) or (sign < 0 and p <= target): break
            if d > self.g['span'] / 100 or len(P) > 6000: raise RuntimeError('target load not reached')
        self.P = p; ops.loadConst('-time', self.t); self.ramp_t0 = None
        return np.array(P), np.array(D)

    def march(self, t_end):
        """Advance time to t_end (days) under the current loads, with creep and shrinkage."""
        ops.setCreep(1); ops.setTime(self.t)
        while self.t < t_end - 1e-9:
            dt = min(max(0.5, 0.15 * (self.t - T_CAST)), t_end - self.t)
            ops.integrator('LoadControl', dt); ok = ops.analyze(1)
            if ok != 0:
                ops.test('NormDispIncr', 1e-6, 200); ok = ops.analyze(1); ops.test('NormDispIncr', 1e-8, 100)
                if ok != 0: raise RuntimeError('nonconvergence in time step')
            self.t = ops.getTime()
        ops.setCreep(0)

    def unload_all(self):
        if self.P > 0.02: self.ramp(-(self.P - 0.0))

    def record(self, Pd):
        p, d = self.state(); sec = self.section()
        P, D = self.ramp(Pd); dd = float(D[-1] - d)
        self.ramp(-Pd)
        return dict(load_kN=float(p), deflection_mm=float(d), section=sec, delta_d_mm=dd, freq_hz=self.freqs())


def run_sustained(row, case):
    g = gen.geometry(row)
    q = dict(fck=float(row['fck_MPa']), Ec=float(row['Ec_MPa']), ft=float(row['ft_MPa']), ets=float(row['ets']), fy=float(row['fy_MPa']))
    Py = float(row['Py_hand_kN']); Pd, Ps = 0.185 * Py, 0.37 * Py
    bm = TDBeam(g, q); out = dict(case=case)
    bm.march(T_CAST + AGE_LOAD)
    out['shrinkage_deflection_mm'] = float(bm.state()[1])           # unloaded beam, before loading
    out['f_unloaded_28d_hz'] = bm.freqs()
    if case == 'overload':
        P, D = bm.ramp(0.80 * Py); out['overload_peak_deflection_mm'] = float(D[-1]); bm.unload_all()
        out['overload_residual_mm'] = float(bm.state()[1])
    P, D = bm.ramp(Ps)
    rec = [dict(years=0, **bm.record(Pd))]
    for y in YEARS:
        bm.march(T_CAST + AGE_LOAD + 365.25 * y)
        rec.append(dict(years=y, **bm.record(Pd)))
    out['under_load'] = rec
    bm.unload_all()
    out['residual_50y_mm'] = float(bm.state()[1])
    P, D = bm.ramp(Pd); out['delta_d_unloaded_50y_mm'] = float(D[-1] - out['residual_50y_mm']); bm.ramp(-Pd)
    out['f_unloaded_50y_hz'] = bm.freqs()
    return out


if __name__ == '__main__':
    design, i0, i1, outfn = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    rows = list(csv.DictReader(open(design))); done = set()
    try:
        for line in open(outfn): r = json.loads(line); done.add((r['beam'], r['case']))
    except FileNotFoundError:
        pass
    with open(outfn, 'a') as fh:
        for row in rows[i0:i1]:
            i = int(row['beam'])
            for case in ('service', 'overload'):
                if (i, case) in done: continue
                t = time.time()
                try: rec = dict(beam=i, ok=True, **run_sustained(row, case))
                except Exception as e: rec = dict(beam=i, case=case, ok=False, err=str(e))
                rec['sec'] = round(time.time() - t, 1); fh.write(json.dumps(rec) + '\n'); fh.flush()
