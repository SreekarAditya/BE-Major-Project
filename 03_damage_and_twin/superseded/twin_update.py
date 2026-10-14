"""
Digital twin update on the simulated damage stages.
Input : ../02_model/fibre_verified.json  (output of fibre_model.py)
Steps for every damage stage:
  1. stiffness from deflection under the 15 kN check load:  EI_s = 23 P L^3 / (1296 delta)
  2. stiffness from the first frequency:                  EI_v = EI_0 (f / f_0)^2
  3. Bayesian combination in log space, each estimate weighted by 1 / variance
  4. prediction of the 30 kN service deflection, made before that test, compared with the 'measured' value
Output: twin_results.csv
Run:  python3 twin_update.py
"""
import json, math, csv

F = json.load(open('../02_model/fibre_verified.json'))
T = F['twin']; rows = T['rows']; Pd, Ps = T['Pd'], T['Ps']
span, a = 3000.0, 1000.0
def C(P):        # deflection x EI for total jack load P (kN) in four-point bending, N mm^3
    return (P * 1e3 / 2) * a * (3 * span ** 2 - 4 * a ** 2) / 24

f0 = rows[0]['f']; EI0 = C(Pd) / rows[0]['delta_d']
# measurement and model uncertainties (standard deviations)
s_f, s_d = 0.3, 0.01          # frequency repeatability (Hz), deflection sensor (mm)
s_dyn = 0.10                  # dynamic vs static stiffness difference of a cracked beam (10 %)
s_lin, s_load = 0.03, 0.02    # non-linearity within the check cycle, load-cell error

out = []
print(f"{'stage':>7}{'f (Hz)':>9}{'EI left %':>11}{'pred (mm)':>11}{'meas (mm)':>11}{'error %':>9}")
for r in rows[1:]:
    lv = math.log(EI0) + 2 * math.log(r['f'] / f0); vv = (2 * s_f / r['f']) ** 2 + (2 * s_f / f0) ** 2 + s_dyn ** 2
    ls = math.log(C(Pd) / r['delta_d']);            vs = (s_d / r['delta_d']) ** 2 + s_lin ** 2 + s_load ** 2
    w_v, w_s = 1 / vv, 1 / vs
    lc = (w_v * lv + w_s * ls) / (w_v + w_s); sc = math.sqrt(1 / (w_v + w_s))
    EI = math.exp(lc)
    pred = C(Ps) / EI; meas = r['delta_s']
    err = 100 * (pred / meas - 1)
    out.append(dict(damage_kN=r['damage'], frequency_Hz=round(r['f'], 2), delta_15kN_mm=round(r['delta_d'], 3),
                    EI_combined_kNm2=round(EI / 1e9, 0), EI_left_percent=round(100 * EI / EI0, 1),
                    EI_uncertainty_percent=round(100 * sc, 1), predicted_30kN_mm=round(pred, 3),
                    measured_30kN_mm=round(meas, 3), error_percent=round(err, 2)))
    print(f"{r['damage']:>7.0f}{r['f']:>9.2f}{100*EI/EI0:>11.1f}{pred:>11.3f}{meas:>11.3f}{err:>9.2f}")

with open('twin_results.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print('written twin_results.csv')
