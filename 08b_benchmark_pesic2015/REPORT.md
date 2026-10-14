# Pešić benchmark: available-data analysis, full scope unmet

- Extracted 51 loaded frequency states across 5 beams. Static measurements are published graphically for only 1 beam, yielding 11 recovered paired peaks.
- Conditional loss slope kappa is 0.180. Its bounded reading sensitivity interval is 0.1641 to 0.1982; a valid beam-bootstrap confidence interval is unavailable because there is only one paired beam.
- Changing the vibration reference to the same readable state as the static reference changes kappa to 0.132. Baseline choice materially affects the result.
- Vibration stiffness exceeds static stiffness at 10 of 11 paired points. The naive one-sided sign-test probability is 0.006, but repeated steps are dependent; the beam-level probability is 0.500.
- Across 10 consecutive transitions, bias learning gives median absolute deflection error 12.62% and maximum 43.54%. Holding static stiffness gives 17.29% and 44.12%; vibration alone gives 82.52% and 86.09%.
- The requested comparison at equal load divided by cracking load is unavailable. A supplemental comparison at load divided by approximate yield load = 0.800 has dynamic stiffness spread 17.91 percentage points, across different geometries and histories.
- Blind fibre prediction is skipped because material inputs are incomplete and reinforcement depth is inconsistent. No parameters were tuned.

## Method

The user supplied the published journal version, rather than the accepted manuscript requested in the job. Identity was checked from its title, author list and digital object identifier. The original remains untouched in Downloads. [Paper identifier](https://doi.org/10.1016/j.engstruct.2015.07.037). All page references here use printed journal page numbers.

Geometry and all used frequency cells were checked against rendered pages. Every extracted field cites its page, table or figure in `pesic_extract.json`. The unloaded vibration response follows the source's hammer-impact and Fourier-spectrum method; the static response is the peak total deflection. The ultrasonic concrete modulus is a separate material measurement and is not substituted for beam stiffness.

The graph was rendered at high resolution and calibrated using axis ticks. Open-circle experimental markers on the blue dashed line were selected manually. A vector-path check caught two intermediate markers initially misidentified as peaks. That failed extraction is retained in `retained_fail_intermediate_marker_picks` and is excluded from all current results. The original ordered blue experimental path then guided pixel positions for obscured turning points. The isolated-path overlay uses the same calibrated pixel coordinates and source path; it does not borrow a numerical model curve. Remaining peak assignments follow chronological envelope order and are explicitly inferred. Figure and table loads differ slightly; the pixel values and discrepancies are retained, without rescaling. Bounds cover displacement reading and load alignment. The overlay permits review of every selected marker.

Static stiffness is peak load divided by peak total deflection. Equivalent flexural rigidity uses the central point-load, simply supported span expression. This does not correct bearing compliance, permanent curvature or support settlements. The static ratio uses the earliest readable damaged state; the vibration ratio uses the initial measured frequency. Consequently the reported primary slope is conditional on inconsistent baseline states. The matched-reference sensitivity uses the same readable state for both ratios. Neither estimates loss relative to an independently measured undamaged static state.

The fitted line minimises squared vibration-loss residuals through the origin. Beam resampling with one cluster returns an identical number every time; that degenerate result is stored but is not represented as a valid confidence interval. Uniform samples within reading bounds give sensitivity intervals, preserving shared readings and reference values. These intervals do not include all experimental errors or validate the inferred curve assignments.

Unloading endpoints and peak-to-zero chords were also digitised from the same experimental path. They are peak-to-zero secants, not tangent reloading stiffness. No uncracked unloading baseline exists. Their conditional point slope is 0.213; the small first recovered deflection makes its reading interval unreliable. These chords do not replace the primary peak-deflection series.

The twin learns the previous log ratio, applies it to the next vibration ratio, and computes signed deflection error as static true divided by static predicted, minus unity. It uses the same formula as the workspace reference, with variable consecutive load gaps. Bias and hold errors cancel the constant baseline scale; the vibration-alone error depends on the missing static-reference assumption. Predictions across missing peaks are excluded.

## Series comparison

The table reports median absolute errors. It does not fit a common calibration or aggregate accuracy across incompatible series.

| Test series | Beams in paper / paired | Kappa | Beam-bootstrap interval | Bias learning | Vibration alone | Predictions |
|---|---:|---:|---|---:|---:|---:|
| Musiał et al. (2021) | 2 / 2 | 0.391 | 0.3906 to 0.3911 | 3.99% | 29.50% | 14 |
| Pešić et al. (2015) | 5 / 1 | 0.180 | Unavailable | 12.62% | 82.52% | 10 |
| Ozturkoglu et al. (2024) | 4 / 4 | 0.348 | 0.3063 to 0.4837 | 24.36% | 66.93% | 5 |

- **Musiał et al. (2021):** Published static secant ratios and vibration ratios, raw static reference; 5 kN prediction gaps; source supplied by workspace. Beam bootstrap recreated from supplied raw ratios, 2 clusters; narrow coverage cannot establish population uncertainty.
- **Pešić et al. (2015):** Conditional: static normalised to earliest readable damaged state, dynamic to initial state; peak total-deflection secant, variable consecutive load gaps. Unavailable: 1 beam cluster; reading sensitivity reported separately.
- **Ozturkoglu et al. (2024):** Frequency-squared loss versus large-displacement envelope secant loss; baseline is first-crack secant. Consecutive envelope-secant proxy, not service-deflection validation. Beam bootstrap, 4 clusters; source Job B1.

For Musiał, the raw slope and compliance-corrected sensitivity are 0.391 and 0.312. The quoted benchmark range is not an acceptance gate. The intervals reflect very few beam clusters and should not be treated as precise population estimates.

## Reading sensitivity of twin errors

| Method | Median absolute error sensitivity | Maximum absolute error sensitivity |
|---|---|---|
| Bias learning | 6.83% to 15.76% | 33.86% to 62.61% |
| Hold previous static | 11.74% to 19.70% | 34.60% to 63.02% |
| Vibration alone | 76.39% to 87.93% | 81.30% to 90.39% |

## Limitations and outstanding records

This analysis does not complete the requested five-beam stiffness benchmark. It adds one conditional paired history plus the complete published frequency histories. Beam 3 may already have been damaged before loading, as the paper notes. The baseline mismatch makes kappa inappropriate as a transferable calibration. The source's best-fit finite element parameters were tuned by its authors and were excluded from any claimed blind prediction.

The section cover in the geometry table conflicts with reinforcement coordinates in the example finite element input. No interpretation was selected to force a model result. Quantitative vibration amplitude, damping and measured cracking loads are missing. The initial measured Beam 3 frequency is below the broad frequency range stated in the abstract; the table value was retained.

The different spans, overhangs, initial conditions and repeated cycles prevent an equal normalized load comparison from identifying specimen-to-specimen damage variation. The supplemental yield-normalised spread is descriptive only. Vibration ratios additionally assume a stable mass and support condition, which is not independently verified here.

`HUMAN_NEEDED.md` lists records needed to remove these limits. Every numeric finding is generated from `pesic_extract.json`, `digitised_static.json`, `h2_results.json`, `h1_results.json`, `twin_results.json` or `pooled_results.json` by this script. `RUN.md` provides the reproducible execution command.

![Static versus vibration](/Users/sreekaraditya/Desktop/StrucIQ_Review2_230x300/00_SHOW_IN_REVIEW/08b_benchmark_pesic2015/01_static_vs_vibration.png)

![Kappa by series](/Users/sreekaraditya/Desktop/StrucIQ_Review2_230x300/00_SHOW_IN_REVIEW/08b_benchmark_pesic2015/02_kappa_by_series.png)

Digitised Beam 3 load path with the eleven peak picks: `fig11_experimental_path.png` (script `fig11_path_chart.py`). The overlay on the original publisher figure, the calibrated page render and the extracted paper text are kept outside the review folder (`_not_for_review/pesic2015_publisher_copy/derived_from_publisher_figure/`) because the source is not open access.
