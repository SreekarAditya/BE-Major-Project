from pathlib import Path
import runpy
C=runpy.run_path(str(Path(__file__).with_name('common.py')));globals().update(C)
E=read('pesic_extract.json');H=read('h2_results.json');T=read('twin_results.json');A=read('h1_results.json');P=read('pooled_results.json');G=read('digitised_static.json');B=read('blind_model_status.json')
f=lambda x:f'{x:.3f}'; pct=lambda x:f'{x:.2f}%'; ci=lambda a:' to '.join(f'{x:.4f}' for x in a)
summaryfile={'job':'B2','status':'COMPLETED_AVAILABLE_DATA_ANALYSIS_WITH_UNMET_FULL_SCOPE','paper_beams':E['counts']['beams'],'paired_beams':H['available_static_beams'],'paired_steps':H['paired_steps'],
'kappa_conditional':H['kappa'],'kappa_95_beam_interval':None,'kappa_reading_interval_95':H['kappa_reading_interval_95'],'matched_reference_sensitivity_kappa':H['matched_reference_sensitivity_kappa'],
'H1_cracking_normalised_spread':None,'H1_supplemental_yield_normalised_dynamic_spread_pp':A['supplemental_yield_normalised_dynamic']['spread_percentage_points'],
'twin_predictions':T['n'],'twin_median_error_bias_pct':T['pooled']['bias']['median_abs_pct'],'twin_max_error_bias_pct':T['pooled']['bias']['max_abs_pct'],
'full_job_done':False,'missing':E['missing'],'blind_prediction':B['status'],'pooled_common_calibration_valid':False}
save('results_summary.json',summaryfile)
text=f'''# Pešić benchmark: available-data analysis, full scope unmet

- Extracted {E['counts']['loaded_frequency_steps']} loaded frequency states across {E['counts']['beams']} beams. Static measurements are published graphically for only {H['available_static_beams']} beam, yielding {H['paired_steps']} recovered paired peaks.
- Conditional loss slope kappa is {f(H['kappa'])}. Its bounded reading sensitivity interval is {ci(H['kappa_reading_interval_95'])}; a valid beam-bootstrap confidence interval is unavailable because there is only one paired beam.
- Changing the vibration reference to the same readable state as the static reference changes kappa to {f(H['matched_reference_sensitivity_kappa'])}. Baseline choice materially affects the result.
- Vibration stiffness exceeds static stiffness at {H['sign_test_naive']['positive']} of {H['sign_test_naive']['n']} paired points. The naive one-sided sign-test probability is {f(H['sign_test_naive']['one_sided_p'])}, but repeated steps are dependent; the beam-level probability is {f(H['sign_test_beam_level']['one_sided_p'])}.
- Across {T['n']} consecutive transitions, bias learning gives median absolute deflection error {pct(T['pooled']['bias']['median_abs_pct'])} and maximum {pct(T['pooled']['bias']['max_abs_pct'])}. Holding static stiffness gives {pct(T['pooled']['hold']['median_abs_pct'])} and {pct(T['pooled']['hold']['max_abs_pct'])}; vibration alone gives {pct(T['pooled']['vibration']['median_abs_pct'])} and {pct(T['pooled']['vibration']['max_abs_pct'])}.
- The requested comparison at equal load divided by cracking load is unavailable. A supplemental comparison at load divided by approximate yield load = {f(A['supplemental_yield_normalised_dynamic']['load_over_yield'])} has dynamic stiffness spread {A['supplemental_yield_normalised_dynamic']['spread_percentage_points']:.2f} percentage points, across different geometries and histories.
- Blind fibre prediction is skipped because material inputs are incomplete and reinforcement depth is inconsistent. No parameters were tuned.

## Method

The user supplied the published journal version, rather than the accepted manuscript requested in the job. Identity was checked from its title, author list and digital object identifier. The original remains untouched in Downloads. [Paper identifier](https://doi.org/{E['paper']['doi']}). All page references here use printed journal page numbers.

Geometry and all used frequency cells were checked against rendered pages. Every extracted field cites its page, table or figure in `pesic_extract.json`. The unloaded vibration response follows the source's hammer-impact and Fourier-spectrum method; the static response is the peak total deflection. The ultrasonic concrete modulus is a separate material measurement and is not substituted for beam stiffness.

The graph was rendered at high resolution and calibrated using axis ticks. Open-circle experimental markers on the blue dashed line were selected manually. A vector-path check caught two intermediate markers initially misidentified as peaks. That failed extraction is retained in `retained_fail_intermediate_marker_picks` and is excluded from all current results. The original ordered blue experimental path then guided pixel positions for obscured turning points. The isolated-path overlay uses the same calibrated pixel coordinates and source path; it does not borrow a numerical model curve. Remaining peak assignments follow chronological envelope order and are explicitly inferred. Figure and table loads differ slightly; the pixel values and discrepancies are retained, without rescaling. Bounds cover displacement reading and load alignment. The overlay permits review of every selected marker.

Static stiffness is peak load divided by peak total deflection. Equivalent flexural rigidity uses the central point-load, simply supported span expression. This does not correct bearing compliance, permanent curvature or support settlements. The static ratio uses the earliest readable damaged state; the vibration ratio uses the initial measured frequency. Consequently the reported primary slope is conditional on inconsistent baseline states. The matched-reference sensitivity uses the same readable state for both ratios. Neither estimates loss relative to an independently measured undamaged static state.

The fitted line minimises squared vibration-loss residuals through the origin. Beam resampling with one cluster returns an identical number every time; that degenerate result is stored but is not represented as a valid confidence interval. Uniform samples within reading bounds give sensitivity intervals, preserving shared readings and reference values. These intervals do not include all experimental errors or validate the inferred curve assignments.

Unloading endpoints and peak-to-zero chords were also digitised from the same experimental path. They are peak-to-zero secants, not tangent reloading stiffness. No uncracked unloading baseline exists. Their conditional point slope is {f(H['unloading_chord_conditional_kappa'])}; the small first recovered deflection makes its reading interval unreliable. These chords do not replace the primary peak-deflection series.

The twin learns the previous log ratio, applies it to the next vibration ratio, and computes signed deflection error as static true divided by static predicted, minus unity. It uses the same formula as the workspace reference, with variable consecutive load gaps. Bias and hold errors cancel the constant baseline scale; the vibration-alone error depends on the missing static-reference assumption. Predictions across missing peaks are excluded.

## Series comparison

The table reports median absolute errors. It does not fit a common calibration or aggregate accuracy across incompatible series.

| Test series | Beams in paper / paired | Kappa | Beam-bootstrap interval | Bias learning | Vibration alone | Predictions |
|---|---:|---:|---|---:|---:|---:|
'''
for r in P['series']:
    text+=f"| {r['series']} | {r['paper_beams']} / {r['paired_beams']} | {f(r['kappa'])} | {ci(r['kappa_95_interval']) if r['kappa_95_interval'] else 'Unavailable'} | {pct(r['twin_bias_median_pct'])} | {pct(r['twin_vibration_median_pct'])} | {r['n_predictions']} |\n"
text+='\n'
for r in P['series']:text+=f"- **{r['series']}:** {r['definition']} {r['interval_kind']}\n"
text+=f'''
For Musiał, the raw slope and compliance-corrected sensitivity are {f(P['series'][0]['kappa'])} and {f(P['series'][0]['kappa_corrected_sensitivity'])}. The quoted benchmark range is not an acceptance gate. The intervals reflect very few beam clusters and should not be treated as precise population estimates.

## Reading sensitivity of twin errors

| Method | Median absolute error sensitivity | Maximum absolute error sensitivity |
|---|---|---|
'''
for k,label in [('bias','Bias learning'),('hold','Hold previous static'),('vibration','Vibration alone')]:
    r=T['pooled'][k];text+=f"| {label} | {' to '.join(pct(x) for x in r['median_abs_reading_interval_95'])} | {' to '.join(pct(x) for x in r['max_abs_reading_interval_95'])} |\n"
text+='''
## Limitations and outstanding records

This analysis does not complete the requested five-beam stiffness benchmark. It adds one conditional paired history plus the complete published frequency histories. Beam 3 may already have been damaged before loading, as the paper notes. The baseline mismatch makes kappa inappropriate as a transferable calibration. The source's best-fit finite element parameters were tuned by its authors and were excluded from any claimed blind prediction.

The section cover in the geometry table conflicts with reinforcement coordinates in the example finite element input. No interpretation was selected to force a model result. Quantitative vibration amplitude, damping and measured cracking loads are missing. The initial measured Beam 3 frequency is below the broad frequency range stated in the abstract; the table value was retained.

The different spans, overhangs, initial conditions and repeated cycles prevent an equal normalized load comparison from identifying specimen-to-specimen damage variation. The supplemental yield-normalised spread is descriptive only. Vibration ratios additionally assume a stable mass and support condition, which is not independently verified here.

`HUMAN_NEEDED.md` lists records needed to remove these limits. Every numeric finding is generated from `pesic_extract.json`, `digitised_static.json`, `h2_results.json`, `h1_results.json`, `twin_results.json` or `pooled_results.json` by this script. `RUN.md` provides the reproducible execution command.

![Static versus vibration](01_static_vs_vibration.png)

![Kappa by series](02_kappa_by_series.png)
'''
text=text.replace('(01_static_vs_vibration.png)',f'({ROOT}/01_static_vs_vibration.png)').replace('(02_kappa_by_series.png)',f'({ROOT}/02_kappa_by_series.png)')
text+=f'\n[Original graph overlay]({ROOT}/fig11_overlay.png) and [isolated experimental path]({ROOT}/fig11_experimental_path.png).\n'
(ROOT/'REPORT.md').write_text(text)
print('Report saved; full scope remains unmet due to missing published records.')
