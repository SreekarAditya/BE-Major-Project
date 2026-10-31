"""Tables from the two follow-on runs.

Writes ../tables/retrofit.csv            one row per beam and scheme (none, laminate, plate, jacket)
       ../tables/continuum_comparison.csv one row per beam of the continuum cross-check, with the fibre results beside it
Usage (from 06_design_space_population/code): python3 process_followon.py   (after process.py)
"""
import os, glob, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); T = os.path.join(ROOT, 'tables')


def records(folder):
    out = []
    for fn in sorted(glob.glob(os.path.join(ROOT, folder, '*.jsonl'))):
        for line in open(fn):
            try: out.append(json.loads(line))
            except Exception: pass
    return out


def retrofit():
    rows = []
    for r in records('raw_retrofit'):
        row = dict(beam=r['beam'], scheme=r['scheme'], run_ok=r['ok'], error=r.get('err', ''), run_seconds=r.get('sec'))
        if r['ok']:
            for k in ('residual_before_mm', 'delta_d_before_mm', 'delta_d_after_mm', 'delta_s_after_mm',
                      'service_steel_stress_after_MPa', 'Pmax_kN', 'push_complete', 'install_moment_Nmm',
                      'n_strips', 'Af_mm2', 'eps_fd', 'jacket_mm'):
                row[k] = r.get(k)
            row['f1_before_hz'] = r['f_before_hz'][0]; row['f1_after_hz'] = r['f_after_hz'][0]
        rows.append(row)
    df = pd.DataFrame(rows).drop_duplicates(['beam', 'scheme'], keep='last')
    ctrl = df[df['scheme'] == 'none'][['beam', 'Pmax_kN', 'delta_s_after_mm']].rename(columns={'Pmax_kN': 'Pmax_control_kN', 'delta_s_after_mm': 'delta_s_control_mm'})
    b = pd.read_csv(os.path.join(T, 'beams.csv'))[['beam', 'Py_hand_kN']]
    df = df.merge(ctrl, on='beam', how='left').merge(b, on='beam', how='left')
    df['capacity_gain'] = df['Pmax_kN'] / df['Pmax_control_kN'] - 1
    df['service_deflection_reduction'] = 1 - df['delta_s_after_mm'] / df['delta_s_control_mm']
    df['stiffness_restored_ratio'] = df['delta_d_before_mm'] / df['delta_d_after_mm']
    df.to_csv(os.path.join(T, 'retrofit.csv'), index=False)
    print('retrofit records %d; median capacity gain by scheme:' % len(df))
    print(df[df['run_ok']].groupby('scheme')['capacity_gain'].median().round(3).to_string())


def continuum():
    c = records('raw_continuum')
    if not c: return
    st = pd.read_csv(os.path.join(T, 'stages.csv')); b = pd.read_csv(os.path.join(T, 'beams.csv'))
    rows = []
    for r in c:
        row = dict(beam=r['beam'], run_ok=r['ok'], error=r.get('err', ''))
        if r['ok']:
            bb = b[b['beam'] == r['beam']]; s = st[(st['beam'] == r['beam']) & (st['stage'] > 0) & st['reached']]
            row.update(f1_continuum_hz=r['f1_hz'], f1_fibre_hz=float(bb['f0_hz'].iloc[0]) if len(bb) else np.nan,
                       Pmax_continuum_kN=r['Pmax_kN'], Pmax_fibre_kN=float(bb['Pmax_kN'].iloc[0]) if len(bb) else np.nan,
                       Pcr_continuum_kN=r['Pcr_kN'], push_complete_continuum=r['push_complete'])
            for k, dc in enumerate(r['stage_deflection_mm'], start=1):
                ds = s[s['stage'] == k]['peak_deflection_mm']
                row['stage%d_deflection_continuum_mm' % k] = dc
                row['stage%d_deflection_fibre_mm' % k] = float(ds.iloc[0]) if len(ds) else np.nan
        rows.append(row)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(T, 'continuum_comparison.csv'), index=False)
    ok = df[df['run_ok']]
    print('continuum beams %d; median ratio continuum/fibre: f1 %.3f, Pmax %.3f' % (
        len(df), (ok['f1_continuum_hz'] / ok['f1_fibre_hz']).median(), (ok['Pmax_continuum_kN'] / ok['Pmax_fibre_kN']).median()))


if __name__ == '__main__':
    retrofit(); continuum()
