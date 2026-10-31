"""Tables from the condition stages (corrosion, sustained load) and the fatigue estimate. Run after process.py and
quality.py.

Writes (../tables):
  corrosion_runs.csv       one row per beam and mass loss: capacity, comparison with the uncorroded beam
  corrosion_stages.csv     staged-protocol records of the corroded beams (columns as stages.csv, plus psi_pct and
                           stiffness and vibration measures relative to the uncorroded beam)
  corrosion_envelopes.csv  load-deflection curves of the corroded beams (push, or the final unreached attempt)
  sustained_runs.csv       one row per beam and case: shrinkage, residual and unloaded response after 50 years,
                           long-term deflection multiplier, IS 456:2000 Annex C estimate
  sustained_history.csv    one row per beam, case and time under load (0, 1, 10, 50 years)
  fatigue.csv              Eurocode 2 fatigue life of the tension steel under repeated service loading, for every
                           reached stage of the main population and of the corroded beams
Usage (from 06_design_space_population/code): python3 process_conditions.py
"""
import os, glob, json, math
import numpy as np
import pandas as pd
from quality import n_valid

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); T = os.path.join(ROOT, 'tables')
ES = 2.0e5
THETA, EPS_CS = 1.6, 3.0e-4                   # IS 456:2000 6.2.5.1 and 6.2.4.1 (same values as sustained.py)
# Eurocode 2 (EN 1992-1-1) Table 6.3N, straight and bent bars: N* = 1e6, k1 = 5, k2 = 9, characteristic stress range 162.5 MPa
N_STAR, K1, K2, DS_RSK, GAMMA_S_FAT = 1e6, 5.0, 9.0, 162.5, 1.15


def records(folder, key):
    out = {}
    for fn in sorted(glob.glob(os.path.join(ROOT, folder, '*.jsonl'))):
        for line in open(fn):
            try: r = json.loads(line)
            except Exception: continue
            out[key(r)] = r
    return out


def breathing(f_open, f_closed): return 2 * f_open * f_closed / (f_open + f_closed)


def stage_rows(i, st, Py, fy, extra):
    """Same flattening as process.py."""
    out = []; dd0, f0 = st[0]['delta_d_mm'], st[0]['freq_hz'][0]
    for s in st:
        row = dict(beam=i, **extra, stage=s['stage'], damage_kN=s['damage_kN'],
                   damage_fraction=s['damage_kN'] / Py if s['stage'] else 0.0, reached=s.get('reached', True))
        if row['reached']:
            f = s['freq_hz']
            row.update(residual_mm=s['residual_mm'], delta_d_mm=s['delta_d_mm'], f1_hz=f[0], f2_hz=f[1], f3_hz=f[2],
                       static_left=dd0 / s['delta_d_mm'], vib_left_open=(f[0] / f0) ** 2,
                       f1_breathing_hz=breathing(f[0], f0), vib_left_breathing=(breathing(f[0], f0) / f0) ** 2)
            if s['stage']:
                pk, sv = s['peak'], s['service']
                row.update(peak_deflection_mm=s['peak_deflection_mm'], delta_s_mm=s['delta_s_mm'],
                           recovery=1 - s['residual_mm'] / s['peak_deflection_mm'] if s['peak_deflection_mm'] > 0 else np.nan,
                           peak_steel_stress_MPa=pk['steel_stress'], peak_steel_strain=pk['e_steel'],
                           peak_curvature_per_mm=pk['curv'], peak_neutral_axis_mm=pk['x'],
                           peak_crack_width_mm=pk['crack_w'], service_crack_width_mm=sv['crack_w'],
                           service_steel_stress_MPa=sv['steel_stress'], steel_yielded=bool(pk['e_steel'] > fy / ES))
        else:
            row.update(reason=s.get('reason'), peak_in_attempt_kN=s.get('peak_in_attempt_kN'))
        out.append(row)
    return out


def corrosion(beams, base_stages):
    raw = records('raw_corrosion', lambda r: (r['beam'], r['psi']))
    if not raw: return None
    b = beams.set_index('beam'); s0 = base_stages[base_stages['stage'] == 0].set_index('beam')
    runs, stages, env = [], [], []
    for (i, psi), r in sorted(raw.items()):
        Py, fy = float(b.loc[i, 'Py_hand_kN']), float(b.loc[i, 'fy_MPa'])
        row = dict(beam=i, psi_pct=psi, run_ok=r['ok'], error=r.get('err', ''), run_seconds=r.get('sec'))
        if r['ok']:
            c = r['corrosion']; st = r['stages']; last = st[-1]
            row.update(area_factor=c['area_factor'], fy_corroded_MPa=c['fy'], esu_corroded=c['esu'],
                       fc_cover_ratio=c['fc_cover'] / (0.8 * float(b.loc[i, 'fck_MPa'])),
                       stages_reached=len([s for s in st if s.get('reached', True)]) - 1, f0_hz=st[0]['freq_hz'][0])
            if last.get('reached', True):
                ev = r.get('envelope') or []; n = n_valid(ev)
                row.update(Pmax_kN=max(x[1] for x in ev[:n]) if n < len(ev) else r['Pmax_kN'], capacity_source='push',
                           push_complete=last.get('push_complete'), push_diverged=n < len(ev))
                curve, src = ev, 'push'
            else:
                ev = last.get('attempt_envelope') or []; n = n_valid(ev)
                lim = last.get('reason') == 'target load not reached'
                row.update(Pmax_kN=last.get('peak_in_attempt_kN') if n == len(ev) else max(x[1] for x in ev[:n]),
                           capacity_source='stage%d_attempt' % last['stage'], push_complete=lim, push_diverged=n < len(ev))
                curve, src = ev, 'attempt'
            for k, (dm, p) in enumerate(curve): env.append(dict(beam=i, psi_pct=psi, source=src, point=k, deflection_mm=dm, load_kN=p, valid=k < n))
            for sr in stage_rows(i, st, Py, fy, dict(psi_pct=psi)):
                if sr['reached'] and i in s0.index:
                    sr['static_left_vs_uncorroded'] = float(s0.loc[i, 'delta_d_mm']) / sr['delta_d_mm']
                    fb = breathing(sr['f1_hz'], float(s0.loc[i, 'f1_hz']))
                    sr['vib_left_breathing_vs_uncorroded'] = (fb / float(s0.loc[i, 'f1_hz'])) ** 2
                stages.append(sr)
        runs.append(row)
    runs = pd.DataFrame(runs).merge(beams[['beam', 'Pmax_kN', 'push_complete']].rename(columns={'Pmax_kN': 'Pmax_uncorroded_kN', 'push_complete': 'push_complete_uncorroded'}), on='beam', how='left')
    runs['capacity_ratio'] = runs['Pmax_kN'] / runs['Pmax_uncorroded_kN']
    stages = pd.DataFrame(stages)
    runs.to_csv(os.path.join(T, 'corrosion_runs.csv'), index=False)
    stages.to_csv(os.path.join(T, 'corrosion_stages.csv'), index=False)
    pd.DataFrame(env).to_csv(os.path.join(T, 'corrosion_envelopes.csv'), index=False)
    ok = runs[runs['run_ok'] & runs['push_complete'].fillna(False).astype(bool) & runs['push_complete_uncorroded'].fillna(False).astype(bool)]
    return dict(runs=len(runs), failed=int((~runs['run_ok']).sum()),
                capacity_ratio_median={str(k): round(float(v), 3) for k, v in ok.groupby('psi_pct')['capacity_ratio'].median().items()},
                capacity_ratio_n={str(k): int(v) for k, v in ok.groupby('psi_pct').size().items()}), stages


def annex_c(bm, P_kN, E):
    """IS 456:2000 Annex C short-term deflection (mm) at total load P with concrete modulus E."""
    b, h, d, As = bm['b_mm'], bm['h_mm'], bm['d_mm'], bm['As_mm2']
    Asc = bm['n_top'] * math.pi * bm['d_top_mm'] ** 2 / 4; dc = bm['cover_mm'] + bm['d_stir_mm'] + bm['d_top_mm'] / 2
    m = ES / E; L = bm['span_mm']
    # cracked section: neutral axis x from b x^2/2 + (m-1) Asc (x - dc) = m As (d - x)
    A, B, C = b / 2, (m - 1) * Asc + m * As, -((m - 1) * Asc * dc + m * As * d)
    x = (-B + math.sqrt(B * B - 4 * A * C)) / (2 * A)
    Ir = b * x ** 3 / 3 + (m - 1) * Asc * (x - dc) ** 2 + m * As * (d - x) ** 2
    Igr = b * h ** 3 / 12; fcr = 0.7 * math.sqrt(bm['fck_MPa']); Mr = fcr * Igr / (h / 2)
    lever = L / 6 if bm['load'] == 'four_point' else L / 8; M = P_kN * 1e3 * lever
    z = d - x / 3
    Ieff = Ir / (1.2 - Mr / M * z / d * (1 - x / d)) if M > 0 else Igr
    Ieff = min(max(Ieff, Ir), Igr)
    P = P_kN * 1e3
    return (23 * P * L ** 3 / (1296 * E * Ieff)) if bm['load'] == 'four_point' else (5 * P * L ** 3 / (384 * E * Ieff))


def annex_c_long_term(bm, P_kN):
    Ec = bm['Ec_MPa']; ai = annex_c(bm, P_kN, Ec); acc = annex_c(bm, P_kN, Ec / (1 + THETA)) - ai
    Asc = bm['n_top'] * math.pi * bm['d_top_mm'] ** 2 / 4
    pt = 100 * bm['As_mm2'] / (bm['b_mm'] * bm['d_mm']); pc = 100 * Asc / (bm['b_mm'] * bm['d_mm'])
    k4 = (0.72 if pt - pc < 1.0 else 0.65) * (pt - pc) / math.sqrt(pt)
    acs = 0.125 * k4 * EPS_CS / bm['h_mm'] * bm['span_mm'] ** 2
    return ai, acc, acs


def sustained(beams):
    raw = records('raw_sustained', lambda r: (r['beam'], r['case']))
    if not raw: return None
    b = beams.set_index('beam'); runs, hist = [], []
    for (i, case), r in sorted(raw.items()):
        row = dict(beam=i, case=case, run_ok=r['ok'], error=r.get('err', ''), run_seconds=r.get('sec'))
        if r['ok']:
            u = r['under_load']; u0, u50 = u[0], u[-1]
            row.update(shrinkage_deflection_mm=r['shrinkage_deflection_mm'], f1_unloaded_28d_hz=r['f_unloaded_28d_hz'][0],
                       overload_peak_deflection_mm=r.get('overload_peak_deflection_mm'), overload_residual_mm=r.get('overload_residual_mm'),
                       sustained_load_kN=u0['load_kN'], deflection_0y_mm=u0['deflection_mm'], deflection_50y_mm=u50['deflection_mm'],
                       long_term_multiplier=u50['deflection_mm'] / u0['deflection_mm'],
                       residual_50y_mm=r['residual_50y_mm'], delta_d_unloaded_50y_mm=r['delta_d_unloaded_50y_mm'],
                       f1_unloaded_50y_hz=r['f_unloaded_50y_hz'][0],
                       vib_left_unloaded_50y=(r['f_unloaded_50y_hz'][0] / r['f_unloaded_28d_hz'][0]) ** 2)
            if case == 'service':
                ai, acc, acs = annex_c_long_term(b.loc[i], u0['load_kN'])
                row.update(is456_short_term_mm=ai, is456_creep_mm=acc, is456_shrinkage_mm=acs, is456_total_mm=ai + acc + acs,
                           model_over_is456_total=u50['deflection_mm'] / (ai + acc + acs))
            for x in u:
                s = x['section']
                hist.append(dict(beam=i, case=case, years=x['years'], load_kN=x['load_kN'], deflection_mm=x['deflection_mm'],
                                 delta_d_added_mm=x['delta_d_mm'], f1_hz=x['freq_hz'][0], f2_hz=x['freq_hz'][1], f3_hz=x['freq_hz'][2],
                                 steel_stress_MPa=s['steel_stress'], steel_strain=s['e_steel'], curvature_per_mm=s['curv'],
                                 neutral_axis_mm=s['x'], crack_width_mm=s['crack_w']))
        runs.append(row)
    runs = pd.DataFrame(runs); hist = pd.DataFrame(hist)
    runs.to_csv(os.path.join(T, 'sustained_runs.csv'), index=False); hist.to_csv(os.path.join(T, 'sustained_history.csv'), index=False)
    ok = runs[runs['run_ok']]
    sv = ok[ok['case'] == 'service']
    return dict(runs=len(runs), failed=int((~runs['run_ok']).sum()),
                long_term_multiplier_median={k: round(float(v), 3) for k, v in ok.groupby('case')['long_term_multiplier'].median().items()},
                model_over_is456_total_median=round(float(sv['model_over_is456_total'].median()), 3) if len(sv) else None,
                model_over_is456_total_p10_p90=[round(float(sv['model_over_is456_total'].quantile(q)), 3) for q in (.1, .9)] if len(sv) else None)


def fatigue_life(ds):
    """Cycles to fatigue failure of straight bars, EN 1992-1-1 Table 6.3N, with gamma_s,fat = 1.15 (design) or 1 (characteristic)."""
    out = []
    for g in (GAMMA_S_FAT, 1.0):
        r = DS_RSK / (g * np.asarray(ds, float))
        n1 = N_STAR * r ** K1; n2 = N_STAR * r ** K2
        out.append(np.where(r >= 1, n2, n1))
    return out


def fatigue(base, corr):
    rows = []
    for name, st in (('main', base), ('corrosion', corr)):
        if st is None or not len(st): continue
        s = st[st['reached'].astype(bool) & (st['stage'] > 0)].copy()
        s['population'] = name
        if 'psi_pct' not in s: s['psi_pct'] = 0.0
        s['stress_range_MPa'] = s['service_steel_stress_MPa']        # repeated loading from zero to the service load
        nd, nk = fatigue_life(s['stress_range_MPa'])
        s['fatigue_life_design_cycles'] = nd; s['fatigue_life_characteristic_cycles'] = nk
        rows.append(s[['population', 'beam', 'psi_pct', 'stage', 'damage_fraction', 'stress_range_MPa', 'fatigue_life_design_cycles', 'fatigue_life_characteristic_cycles']])
    f = pd.concat(rows); f.to_csv(os.path.join(T, 'fatigue.csv'), index=False)
    m = f[f['population'] == 'main']
    return dict(records=len(f), design_life_median_by_stage={int(k): float('%.3g' % v) for k, v in m.groupby('stage')['fatigue_life_design_cycles'].median().items()},
                share_below_2e6_design_by_stage={int(k): round(float(v), 3) for k, v in m.groupby('stage')['fatigue_life_design_cycles'].apply(lambda x: (x < 2e6).mean()).items()})


if __name__ == '__main__':
    beams = pd.read_csv(os.path.join(T, 'beams.csv'), float_precision='round_trip')
    base = pd.read_csv(os.path.join(T, 'stages.csv'), float_precision='round_trip')
    out = {}
    c = corrosion(beams, base)
    corr = None
    if c: out['corrosion'], corr = c
    out['sustained'] = sustained(beams)
    out['fatigue'] = fatigue(base, corr)
    json.dump(out, open(os.path.join(T, 'conditions_summary.json'), 'w'), indent=2)
    print(json.dumps(out, indent=2))
