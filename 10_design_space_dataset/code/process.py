"""Turn the raw population output into clean tables, add the breathing-crack vibration stiffness and the
measurement layer, and write the benchmark splits.

Usage (from 06_design_space_population/code):  python3 process.py
Reads   ../data/design.csv, ../raw/*.jsonl
Writes  ../tables/beams.csv, stages.csv, envelopes.csv, stages_measured.csv, splits.csv
"""
import os, glob, json, math
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
ES = 2.0e5
SEED = 2027

# measurement layer (assumed sensor characteristics, one realisation per beam stage, seed 2027)
FREQ_SD_REL = 0.005        # frequency identified from ambient vibration: 0.5% standard deviation
TEMP_RANGE = (15.0, 40.0)  # concrete temperature at the test, uniform
TEMP_COEF = -0.002         # relative frequency change per degree Celsius from 25 C
DEFL_SD_ABS, DEFL_SD_REL = 0.01, 0.005   # deflection gauge: 0.01 mm plus 0.5% of reading
CRACK_SD, CRACK_STEP = 0.01, 0.01        # camera crack width: 0.01 mm standard deviation, reported to 0.01 mm


def load_raw():
    recs = {}
    for fn in sorted(glob.glob(os.path.join(ROOT, 'raw', '*.jsonl'))):
        for line in open(fn):
            try: r = json.loads(line)
            except Exception: continue
            recs[r['beam']] = r                       # last record of a beam wins (reruns)
    return recs


def breathing(f_open, f_closed):
    """Bilinear (breathing-crack) frequency: cracks open in one half-cycle and closed in the other."""
    return 2 * f_open * f_closed / (f_open + f_closed)


def main():
    design = pd.read_csv(os.path.join(ROOT, 'data', 'design.csv'))
    recs = load_raw()
    beams, stages, env = [], [], []
    for _, d in design.iterrows():
        i = int(d['beam']); r = recs.get(i)
        if r is None: continue
        b = dict(beam=i, run_ok=r['ok'], run_seconds=r.get('sec'), error=r.get('err', ''))
        if r['ok']:
            st = r['stages']
            reached = [s for s in st if s.get('reached', True)]
            b.update(stages_reached=len(reached) - 1, Pmax_kN=r.get('Pmax_kN'),
                     push_complete=st[-1].get('push_complete', None), f0_hz=st[0]['freq_hz'][0])
            dd0, f0 = st[0]['delta_d_mm'], st[0]['freq_hz'][0]
            fy = float(d['fy_MPa'])
            for s in st:
                row = dict(beam=i, stage=s['stage'], damage_kN=s['damage_kN'],
                           damage_fraction=s['damage_kN'] / float(d['Py_hand_kN']) if s['stage'] else 0.0,
                           reached=s.get('reached', True))
                if row['reached']:
                    f = s['freq_hz']
                    row.update(residual_mm=s['residual_mm'], delta_d_mm=s['delta_d_mm'],
                               f1_hz=f[0], f2_hz=f[1], f3_hz=f[2],
                               static_left=dd0 / s['delta_d_mm'],
                               vib_left_open=(f[0] / f0) ** 2,
                               f1_breathing_hz=breathing(f[0], f0),
                               vib_left_breathing=(breathing(f[0], f0) / f0) ** 2)
                    if s['stage']:
                        pk, sv = s['peak'], s['service']
                        row.update(peak_deflection_mm=s['peak_deflection_mm'], delta_s_mm=s['delta_s_mm'],
                                   recovery=1 - s['residual_mm'] / s['peak_deflection_mm'] if s['peak_deflection_mm'] > 0 else np.nan,
                                   peak_steel_stress_MPa=pk['steel_stress'], peak_steel_strain=pk['e_steel'],
                                   peak_curvature_per_mm=pk['curv'], peak_neutral_axis_mm=pk['x'],
                                   peak_crack_width_mm=pk['crack_w'], service_crack_width_mm=sv['crack_w'],
                                   service_steel_stress_MPa=sv['steel_stress'],
                                   steel_yielded=bool(pk['e_steel'] > fy / ES))
                stages.append(row)
            for k, (dm, p) in enumerate(r.get('envelope', []) or []):
                env.append(dict(beam=i, point=k, deflection_mm=dm, load_kN=p))
        beams.append(b)
    beams = design.merge(pd.DataFrame(beams), on='beam', how='inner')
    stages = pd.DataFrame(stages); env = pd.DataFrame(env)
    out = os.path.join(ROOT, 'tables'); os.makedirs(out, exist_ok=True)
    beams.to_csv(os.path.join(out, 'beams.csv'), index=False)
    stages.to_csv(os.path.join(out, 'stages.csv'), index=False)
    env.to_csv(os.path.join(out, 'envelopes.csv'), index=False)

    # measurement layer
    rng = np.random.default_rng(SEED)
    m = stages[stages['reached']].copy()
    n = len(m)
    m['temperature_C'] = rng.uniform(*TEMP_RANGE, n)
    tf = 1 + TEMP_COEF * (m['temperature_C'] - 25.0)
    for c in ('f1_breathing_hz',):
        m[c + '_measured'] = m[c] * tf * (1 + FREQ_SD_REL * rng.standard_normal(n))
    for c in ('delta_d_mm', 'residual_mm', 'delta_s_mm', 'peak_deflection_mm'):
        if c in m:
            v = m[c]
            m[c + '_measured'] = v + (DEFL_SD_ABS + DEFL_SD_REL * v.abs()) * rng.standard_normal(n)
    for c in ('service_crack_width_mm', 'peak_crack_width_mm'):
        if c in m:
            w = (m[c] + CRACK_SD * rng.standard_normal(n)).clip(lower=0)
            m[c + '_measured'] = (w / CRACK_STEP).round() * CRACK_STEP
    keep = ['beam', 'stage', 'damage_kN', 'damage_fraction', 'temperature_C'] + [c for c in m.columns if c.endswith('_measured')]
    m[keep].to_csv(os.path.join(out, 'stages_measured.csv'), index=False)

    # benchmark splits, by beam: random 70/15/15, and extrapolation (train on spans <= 4.5 m and depths <= 450 mm)
    rs = np.random.default_rng(SEED + 1)
    ids = beams['beam'].to_numpy(); u = rs.random(len(ids))
    split_random = np.where(u < 0.70, 'train', np.where(u < 0.85, 'validation', 'test'))
    inside = (beams['span_mm'] <= 4500) & (beams['h_mm'] <= 450)
    split_extrap = np.where(inside, np.where(rs.random(len(ids)) < 0.85, 'train', 'validation'), 'test')
    pd.DataFrame(dict(beam=ids, split_random=split_random, split_extrapolation=split_extrap)).to_csv(os.path.join(out, 'splits.csv'), index=False)
    print('beams %d (failed %d), stages %d, envelope points %d' % (len(beams), int((~beams['run_ok']).sum()), len(stages), len(env)))


if __name__ == '__main__':
    main()
