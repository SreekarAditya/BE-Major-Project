"""
StrucIQ digital twin algorithm: the five steps, run stage by stage on one beam.

Run:   python3 twin.py            (needs only Python 3; runs in under a second; writes no files)

Input: ../02_model/fibre_verified.json   simulated beam (deflection at the 15 kN check, frequency, true 30 kN deflection)
       ../07_uncertainty_and_validation/mc2_summary.json   estimator uncertainties calibrated on 149 simulated beams

The fibre model cannot show cracks closing under a small vibration, so the frequency reading here is made realistic:
vibration sees only a fraction KAPPA of the real stiffness loss, KAPPA = 0.35 as measured in the published tests
(Musial et al. 2021: 0.31 to 0.39; Ozturkoglu et al. 2024: 0.35). With real sensors, steps 1 and 2 take measured values.
"""
import json, math

SPAN, A = 3000.0, 1000.0          # mm: span and shear span (loads at the third points)
P_CHECK, P_SERVICE = 15.0, 30.0   # kN: load check (below cracking) and service load to be predicted
KAPPA, Z90 = 0.35, 1.645          # vibration bias from published tests; 90% interval multiplier

def deflection_times_EI(P_kN):
    """Midspan deflection x EI for total jack load P in four-point bending: 23 P L^3 / 1296 (N mm^3)."""
    return (P_kN * 1e3 / 2) * A * (3 * SPAN ** 2 - 4 * A ** 2) / 24

# Step 1: stiffness from the static load check
def static_stiffness(deflection_mm):
    return deflection_times_EI(P_CHECK) / deflection_mm                        # EI_s = 23 P L^3 / (1296 delta)

# Step 2: stiffness from the first natural frequency
def vibration_stiffness(f_hz, f0_hz, EI0):
    return EI0 * (f_hz / f0_hz) ** 2                                         # EI_v = EI_0 (f / f_0)^2

# Step 3: learn the vibration bias at a load check
def learn_bias(EI_v, EI_s):
    return math.log(EI_v / EI_s)                                             # b = ln(EI_v / EI_s)

# Step 4: Bayesian combination in log space, each estimate weighted by 1 / variance
def combine(ln_static, sd_static, ln_vib_corrected, sd_vib):
    w_s, w_v = 1 / sd_static ** 2, 1 / sd_vib ** 2
    mean = (w_s * ln_static + w_v * ln_vib_corrected) / (w_s + w_v)
    return mean, math.sqrt(1 / (w_s + w_v))

# Step 5: predict the service deflection with a 90% interval
def predict(ln_EI, sd):
    centre = deflection_times_EI(P_SERVICE) / math.exp(ln_EI)
    return centre, deflection_times_EI(P_SERVICE) / math.exp(ln_EI + Z90 * sd), deflection_times_EI(P_SERVICE) / math.exp(ln_EI - Z90 * sd)

if __name__ == '__main__':
    beam = json.load(open('../02_model/fibre_verified.json'))['twin']['rows']
    sd = json.load(open('../07_uncertainty_and_validation/mc2_summary.json'))['calibrated_log_sd']
    sd_static, sd_vib = sd['Static only'], sd['Vibration, bias learned']

    d0, f0_model = beam[0]['delta_d'], beam[0]['f']
    EI0 = static_stiffness(d0)
    print('Undamaged: deflection at 15 kN %.3f mm, frequency %.2f Hz, EI0 = %.0f kN m2\n' % (d0, f0_model, EI0 / 1e9))
    print('%6s %9s %9s %9s %8s %8s %16s %10s %7s' % ('stage', 'EI_s', 'EI_v', 'bias b', 'EI twin', 'left', 'predicted 30 kN', 'actual', 'error'))
    print('%6s %9s %9s %9s %8s %8s %16s %10s %7s' % ('kN', 'kN m2', 'kN m2', '', 'kN m2', '%', 'mm (90% range)', 'mm', '%'))
    bias_last = 0.0                                                          # no bias before the first check
    between = []
    for k, r in enumerate(beam[1:]):
        true_left = d0 / r['delta_d']
        f_read = f0_model * math.sqrt(1 - KAPPA * (1 - true_left))            # what a real tap test would read
        EI_s = static_stiffness(r['delta_d'])                                # step 1
        EI_v = vibration_stiffness(f_read, f0_model, EI0)                     # step 2
        ln_vib_corrected = math.log(EI_v) - bias_last                         # correct vibration with the last learned bias
        ln_EI, s = combine(math.log(EI_s), sd_static[k], ln_vib_corrected, sd_vib[k])   # step 4
        pred, lo, hi = predict(ln_EI, s)                                      # step 5
        err = 100 * (pred / r['delta_s'] - 1)
        print('%6.0f %9.0f %9.0f %9.3f %8.0f %8.0f %6.3f (%.3f-%.3f) %10.3f %7.2f' % (
            r['damage'], EI_s / 1e9, EI_v / 1e9, learn_bias(EI_v, EI_s), math.exp(ln_EI) / 1e9, 100 * math.exp(ln_EI) / EI0, pred, lo, hi, r['delta_s'], err))
        p_raw, _, _ = predict(math.log(EI_v), sd_vib[k]); p_cor, lo_c, hi_c = predict(ln_vib_corrected, sd_vib[k])
        between.append((r['damage'], p_raw, p_cor, lo_c, hi_c, r['delta_s']))
        bias_last = learn_bias(EI_v, EI_s)                                   # step 3: kept for the next stage
    print('\nBetween load checks (tap test only): vibration as read, and corrected with the bias learned at the previous check')
    print('%6s %16s %26s %10s' % ('stage', 'raw vibration', 'bias-corrected (90% range)', 'actual'))
    for st, p_raw, p_cor, lo_c, hi_c, act in between:
        print('%6.0f %9.3f (%+4.0f%%) %9.3f (%.3f-%.3f) %+4.0f%% %8.3f' % (st, p_raw, 100 * (p_raw / act - 1), p_cor, lo_c, hi_c, 100 * (p_cor / act - 1), act))
    print('\nVibration alone would report %.0f%% stiffness left after 72 kN; the static check shows %.0f%%.' % (
        100 * (1 - KAPPA * (1 - d0 / beam[-1]['delta_d'])), 100 * d0 / beam[-1]['delta_d']))
