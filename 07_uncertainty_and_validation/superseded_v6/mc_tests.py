"""Significance tests on the twin results of the 299 converged Monte Carlo beams (reads mc_twin.csv, writes mc_tests.json).
H2: sign test that vibration gives a higher stiffness than the load test.
H3: Wilcoxon signed-rank tests (combined error smaller than vibration only and than no updating); bootstrap interval of the median."""
import csv, json, numpy as np
from scipy.stats import wilcoxon, binomtest
R = list(csv.DictReader(open('mc_twin.csv'))); out = {}
for st in ('35.0', '50.0', '65.0', '72.0'):
    r = [x for x in R if x['damage_kN'] == st]
    ratio = np.array([float(x['dynamic_to_static_EI']) for x in r])
    ec, ev, en = (np.abs([float(x[k]) for x in r]) for k in ('error_combined_pct', 'error_vibration_pct', 'error_no_update_pct'))
    rng = np.random.default_rng(1); bs = [np.median(rng.choice(ec, len(ec))) for _ in range(2000)]
    k = int((ratio > 1).sum())
    out[st] = dict(n=len(r), share_vibration_stiffer=k / len(r), sign_test_p=binomtest(k, len(r), 0.5, alternative='greater').pvalue,
                   wilcoxon_combined_vs_vibration_p=wilcoxon(ec, ev, alternative='less').pvalue,
                   wilcoxon_combined_vs_no_update_p=wilcoxon(ec, en, alternative='less').pvalue,
                   combined_median_error_CI95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                   share_combined_below_5pct=float((ec < 5).mean()))
    print(st, out[st])
json.dump(out, open('mc_tests.json', 'w'), indent=1)
