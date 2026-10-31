"""Benchmark tasks and baseline results on the beam population.

Task A  Stiffness left from measurements (regression). Target: static stiffness left (diagnostic-cycle
        secant stiffness / undamaged value) at each damage stage. Inputs: beam design, measured frequency,
        measured crack width under service load, measured residual deflection, temperature.
        A1 (monitoring): the undamaged frequency of the same beam is known.  A2 (assessment): it is not.
Task B  Has the tension steel yielded? (classification) from the same measurements.

Splits: split_random (70/15/15 by beam) and split_extrapolation (train on spans <= 4.5 m and depths <= 450 mm,
test on larger beams). Metric for A: mean absolute error in percentage points of stiffness left.
Metric for B: balanced accuracy and recall of yielded stages.
Usage: python3 benchmarks.py   (writes ../tables/benchmark_results.json)
"""
import os, json, math
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.metrics import balanced_accuracy_score, recall_score

HERE = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(HERE, '..', 'tables')
KAPPA = 0.35                                    # vibration bias from published tests (used by the twin)


def hand_f0(r):
    """First frequency of the uncracked simply supported beam from gross section and nominal Ec."""
    Ec = 5000 * math.sqrt(r['grade_MPa']); I = r['b_mm'] * r['h_mm'] ** 3 / 12; m = 2.5e-9 * r['b_mm'] * r['h_mm']
    return math.pi / (2 * r['span_mm'] ** 2) * math.sqrt(Ec * I / m)


def table():
    b = pd.read_csv(os.path.join(T, 'beams.csv')); s = pd.read_csv(os.path.join(T, 'stages.csv'))
    m = pd.read_csv(os.path.join(T, 'stages_measured.csv')); sp = pd.read_csv(os.path.join(T, 'splits.csv'))
    s = s[s['reached'] & (s['stage'] > 0)].merge(m, on=['beam', 'stage', 'damage_kN', 'damage_fraction'])
    f0m = m[m['stage'] == 0][['beam', 'f1_breathing_hz_measured']].rename(columns={'f1_breathing_hz_measured': 'f0_measured'})
    s = s.merge(f0m, on='beam').merge(b, on='beam').merge(sp, on='beam')
    s['f0_hand'] = s.apply(hand_f0, axis=1)
    s['ratio_monitoring'] = (s['f1_breathing_hz_measured'] / s['f0_measured']) ** 2
    s['ratio_assessment'] = (s['f1_breathing_hz_measured'] / s['f0_hand']) ** 2
    return s


DESIGN = ['span_mm', 'b_mm', 'h_mm', 'cover_mm', 'd_bot_mm', 'pt_pct', 'span_over_d', 'grade_MPa', 'fy_nom_MPa']
MEAS = ['f1_breathing_hz_measured', 'service_crack_width_mm_measured', 'residual_mm_measured', 'temperature_C']


def X(s, monitoring):
    cols = DESIGN + MEAS + (['f0_measured', 'ratio_monitoring'] if monitoring else ['f0_hand', 'ratio_assessment'])
    x = s[cols].copy(); x['four_point'] = (s['load'] == 'four_point').astype(int); return x


def main():
    s = table(); res = {}
    y = s['static_left']
    for split in ('split_random', 'split_extrapolation'):
        tr, te = s[split] == 'train', s[split] == 'test'
        r = {}
        for name, mon in (('A1_monitoring', True), ('A2_assessment', False)):
            ratio = s['ratio_monitoring'] if mon else s['ratio_assessment']
            r[name + '_vibration_as_read'] = float((ratio[te].clip(0, 1.2) - y[te]).abs().mean() * 100)
            r[name + '_kappa_corrected'] = float(((1 - (1 - ratio[te]) / KAPPA).clip(0, 1.2) - y[te]).abs().mean() * 100)
            mdl = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, random_state=0).fit(X(s[tr], mon), y[tr])
            r[name + '_gradient_boosting'] = float((mdl.predict(X(s[te], mon)) - y[te]).abs().mean() * 100)
        yb = s['steel_yielded'].astype(int)
        rule = (s['residual_mm_measured'] / s['peak_deflection_mm_measured'] > 0.25).astype(int)    # recovery below 75%
        r['B_rule_recovery_below_75pct_bal_acc'] = float(balanced_accuracy_score(yb[te], rule[te]))
        r['B_rule_recall'] = float(recall_score(yb[te], rule[te], zero_division=0))
        clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, class_weight='balanced', random_state=0)
        xb = X(s, True); clf.fit(xb[tr], yb[tr]); pb = clf.predict(xb[te])
        r['B_gradient_boosting_bal_acc'] = float(balanced_accuracy_score(yb[te], pb))
        r['B_gradient_boosting_recall'] = float(recall_score(yb[te], pb, zero_division=0))
        r['n_test_stages'] = int(te.sum()); r['n_test_yielded'] = int(yb[te].sum())
        res[split] = r
    json.dump(res, open(os.path.join(T, 'benchmark_results.json'), 'w'), indent=1)
    for k, v in res.items():
        print(k); [print('  %-45s %.3f' % (a, b)) for a, b in v.items()]


if __name__ == '__main__':
    main()
