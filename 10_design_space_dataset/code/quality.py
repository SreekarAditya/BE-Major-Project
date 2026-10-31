"""Quality flags for the final push and the retrofit comparison. Run after process.py and process_followon.py.

The raw output is not changed. In a small number of pushes the solver's last accepted step is spurious: the load
jumps far above the trend of the curve (in some cases by orders of magnitude) while the deflection advances by one
normal step. Such a step is detected on the 40-point load-deflection curve as the first point whose tangent
stiffness exceeds DIVERGENCE_FACTOR times the largest tangent stiffness of all earlier points; that point and any
later points are marked invalid.

Writes (in ../tables):
  beams.csv            + push_diverged, Pmax_raw_kN (solver value); Pmax_kN is the peak of the valid points
                         when the push diverged, otherwise unchanged
  envelopes.csv        + valid
  retrofit.csv         + push_diverged, Pmax_raw_kN, common_deflection_mm, capacity_gain_valid, install_moment_ratio;
                         capacity_gain is recomputed over the deflection range reached by both this push and the
                         control push of the same beam
  stages.csv           + frequency_rise: the open-crack first frequency is more than 0.1% above that of the
                         previous reached stage although the static stiffness has fallen
  retrofit_envelopes.csv  40-point load-deflection curve of each retrofit push, with valid
Usage (from 06_design_space_population/code): python3 quality.py
"""
import os, glob, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); T = os.path.join(ROOT, 'tables')
DIVERGENCE_FACTOR = 2.0


def records(folder, key):
    """Last record wins, files in sorted order (same rule as process.py and process_followon.py)."""
    out = {}
    for fn in sorted(glob.glob(os.path.join(ROOT, folder, '*.jsonl'))):
        for line in open(fn):
            try: r = json.loads(line)
            except Exception: continue
            out[key(r)] = r
    return out


def n_valid(env):
    """Number of leading points of the curve that are valid."""
    if not env: return 0
    d = np.array([e[0] for e in env], float); p = np.array([e[1] for e in env], float)
    if not (np.isfinite(d[0]) and np.isfinite(p[0])): return 0
    kmax = None
    for i in range(1, len(p)):
        if not (np.isfinite(p[i]) and np.isfinite(d[i])): return i
        dd = d[i] - d[i - 1]
        k = (p[i] - p[i - 1]) / dd if dd > 0 else np.inf
        if kmax is not None and k > DIVERGENCE_FACTOR * kmax: return i
        kmax = k if kmax is None else max(kmax, k)
    return len(p)


def peak_upto(env, dc):
    """Peak load of a curve over deflections up to dc (linear interpolation at dc)."""
    d = np.array([e[0] for e in env], float); p = np.array([e[1] for e in env], float)
    m = d <= dc + 1e-9; pk = p[m].max() if m.any() else np.nan
    j = np.searchsorted(d, dc)
    if 0 < j < len(d): pk = np.nanmax([pk, np.interp(dc, d, p)])
    return pk


def main_population():
    b = pd.read_csv(os.path.join(T, 'beams.csv'), float_precision='round_trip'); e = pd.read_csv(os.path.join(T, 'envelopes.csv'), float_precision='round_trip')
    for c in ('push_diverged', 'Pmax_raw_kN'):
        if c in b: b = b.drop(columns=c)
    if 'valid' in e: e = e.drop(columns='valid')
    raw = records('raw', lambda r: r['beam'])
    div, praw, pv, nv = {}, {}, {}, {}
    for i, r in raw.items():
        env = r.get('envelope') or []
        if not r.get('ok') or not env: continue
        n = n_valid(env); nv[i] = n; div[i] = n < len(env); praw[i] = r.get('Pmax_kN')
        pv[i] = max(x[1] for x in env[:n]) if n else np.nan
    b['Pmax_raw_kN'] = b['beam'].map(praw)
    b['push_diverged'] = b['beam'].map(div).astype('boolean')
    m = b['push_diverged'].fillna(False).astype(bool)
    b.loc[m, 'Pmax_kN'] = b.loc[m, 'beam'].map(pv)
    e['valid'] = e['point'] < e['beam'].map(nv).fillna(0)
    b.to_csv(os.path.join(T, 'beams.csv'), index=False); e.to_csv(os.path.join(T, 'envelopes.csv'), index=False)
    return dict(pushes=len(div), diverged=int(sum(div.values())),
                Pmax_over_Py_hand_max=float((b['Pmax_kN'] / b['Py_hand_kN']).max()),
                Pmax_over_Py_hand_max_raw=float((b['Pmax_raw_kN'] / b['Py_hand_kN']).max()))


def retrofit():
    t = pd.read_csv(os.path.join(T, 'retrofit.csv'), float_precision='round_trip')
    b = pd.read_csv(os.path.join(T, 'beams.csv'), float_precision='round_trip').set_index('beam')
    for c in ('push_diverged', 'Pmax_raw_kN', 'common_deflection_mm', 'capacity_gain_valid', 'install_moment_ratio'):
        if c in t: t = t.drop(columns=c)
    raw = records('raw_retrofit', lambda r: (r['beam'], r['scheme']))
    env, rows = {}, []
    for (i, s), r in raw.items():
        ev = r.get('envelope') or []
        if not r.get('ok') or not ev: continue
        n = n_valid(ev); env[(i, s)] = ev[:n]
        for k, (dm, p) in enumerate(ev): rows.append(dict(beam=i, scheme=s, point=k, deflection_mm=dm, load_kN=p, valid=k < n))
    pd.DataFrame(rows).sort_values(['beam', 'scheme', 'point']).to_csv(os.path.join(T, 'retrofit_envelopes.csv'), index=False)
    key = list(zip(t['beam'], t['scheme']))
    t['Pmax_raw_kN'] = [raw[k].get('Pmax_kN') if k in raw and raw[k].get('ok') else np.nan for k in key]
    t['push_diverged'] = pd.array([(len(env[k]) < len(raw[k]['envelope'])) if k in env else pd.NA for k in key], dtype='boolean')
    t['Pmax_kN'] = [max(x[1] for x in env[k]) if (k in env and env[k] and t['push_diverged'].iloc[j]) else t['Pmax_raw_kN'].iloc[j]
                    for j, k in enumerate(key)]
    ctrl = t[t['scheme'] == 'none'].set_index('beam')['Pmax_kN']
    t['Pmax_control_kN'] = t['beam'].map(ctrl)
    dcs, gains, valid = [], [], []
    for i, s in key:
        k, kc = (i, s), (i, 'none')
        if s == 'none' or k not in env or kc not in env or not env[k] or not env[kc]:
            dcs.append(np.nan); gains.append(0.0 if (s == 'none' and k in env) else np.nan); valid.append(s == 'none' and k in env); continue
        dc = min(env[k][-1][0], env[kc][-1][0])
        d = np.array([x[0] for x in env[kc]]); p = np.array([x[1] for x in env[kc]])
        d95 = d[np.argmax(p >= 0.95 * p.max())]          # control has reached 95% of its own peak
        dcs.append(dc); gains.append(peak_upto(env[k], dc) / peak_upto(env[kc], dc) - 1); valid.append(bool(dc >= d95))
    t['common_deflection_mm'] = dcs; t['capacity_gain'] = gains; t['capacity_gain_valid'] = valid
    My = np.where(t['beam'].map(b['load']) == 'udl', 1 / 8, 1 / 6) * t['beam'].map(b['Py_hand_kN']) * 1e3 * t['beam'].map(b['span_mm'])
    t['install_moment_ratio'] = t['install_moment_Nmm'] / My
    t.to_csv(os.path.join(T, 'retrofit.csv'), index=False)
    ok = t[t['capacity_gain_valid'] & (t['scheme'] != 'none')]
    return dict(pushes=len(env), diverged=int(t['push_diverged'].fillna(False).sum()),
                gain_valid={s: int(v) for s, v in ok.groupby('scheme').size().items()},
                gain_median={s: round(float(v), 3) for s, v in ok.groupby('scheme')['capacity_gain'].median().items()},
                gain_p05_p95={s: [round(float(v.quantile(.05)), 3), round(float(v.quantile(.95)), 3)] for s, v in ok.groupby('scheme')['capacity_gain']},
                install_moment_ratio_median={s: round(float(v), 4) for s, v in t[t['scheme'] != 'none'].groupby('scheme')['install_moment_ratio'].median().items()},
                install_moment_ratio_p95={s: round(float(v), 4) for s, v in t[t['scheme'] != 'none'].groupby('scheme')['install_moment_ratio'].quantile(.95).items()})


def stages():
    st = pd.read_csv(os.path.join(T, 'stages.csv'), float_precision='round_trip')
    if 'frequency_rise' in st: st = st.drop(columns='frequency_rise')
    r = st[st['reached'].astype(bool)].sort_values(['beam', 'stage'])
    prev = r.groupby('beam')['f1_hz'].shift(1)
    rise = (r['stage'] > 0) & (r['f1_hz'] / prev - 1 > 0.001)
    st['frequency_rise'] = False; st.loc[rise[rise].index, 'frequency_rise'] = True
    st.to_csv(os.path.join(T, 'stages.csv'), index=False)
    return dict(records=int(rise.sum()), beams=int(r.loc[rise, 'beam'].nunique()), of_reached_stage_records=int((r['stage'] > 0).sum()),
                max_rise=float((r['f1_hz'] / prev - 1).max()))


if __name__ == '__main__':
    out = dict(main=main_population(), retrofit=retrofit(), stages=stages())
    json.dump(out, open(os.path.join(T, 'quality_summary.json'), 'w'), indent=2)
    print(json.dumps(out, indent=2))
