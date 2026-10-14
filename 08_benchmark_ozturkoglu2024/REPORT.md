# Job B1: independent published beam benchmark (2024)

## Findings first

- **Ultimate capacity, conditional:** pre-strengthened predictions are 50.57 and 64.05 kN against 51.94 and 66.24 kN; conservative by 2.6% to 3.3%. Fiber-equivalent thickness is inferred, so this is conditional agreement.
- **Yield prediction is poorer:** steel-strain yield predictions are 40.13 and 48.76 kN, 18.4% and 16.1% below the paper's equivalent elasto-plastic yields. Different yield definitions limit the comparison.
- **Post-strengthened capacity:** ignoring initial strain gives 50.60 and 64.04 kN; the residual-curvature proxy gives 48.49 and 64.19 kN. Local residual substrate strain is not identified.
- **Vibration versus static secant:** kappa = 0.348, beam-bootstrap 95% interval 0.306 to 0.484; overlaps Musial's 0.312 to 0.391. Vibration stiffness is larger in 10 of 11 comparisons. This secant includes plastic displacement.
- **Identical bare beams at D1:** vibration stiffness indices are 97.6% and 87.8%, a 9.82 percentage-point spread. D1 fixes displacement, so equal-load H1 is not demonstrated.
- **Twin test is not a service-accuracy confirmation:** over 5 consecutive predictions, median absolute proxy-deflection error is 24.4% with bias learning, 26.5% holding the last check and 66.9% from vibration alone.
- **Vibration sees an inconsistent repair signal:** first vertical frequency changes by -9.01% after glass-fiber strengthening and +1.17% after carbon-fiber strengthening. A matched static load and deflection check is required to confirm repair.

All numerical findings are generated from the JSON files named at the end. No input was adjusted to match the tests.

## Specimens and source extraction

Ozturkoglu and colleagues studied 4 nominally identical beams. The section is 150 by 250 mm, with 3000 mm span and 1350 mm shear span. Mean cylinder concrete strength is approximately 20 MPa. Steel yield, tensile strength and modulus are 420 MPa, 500 MPa and 200 GPa. The paper states steel and fiber properties without individual coupon results.

The extraction records source pages, tables and figures for every value, and marks inferred and missing inputs. 180 numeric table entries were checked between the layout text and an independent rendered-page transcription. The text layer contains duplicate and joined entries. Exact decimal substrings plus the visual read resolve those entries; the original strict token-boundary failure is retained. This lexical check alone is not a table-cell parser.

## Strengthening capacity method

The section uses the unchanged parabola-rectangle concrete and elastic-perfectly-plastic steel logic from `val_frp.py`, with 200 concrete slices and 2901 trial neutral-axis depths. Concrete peak and ultimate strains are 0.002 and 0.0035. The supplied American Concrete Institute guide debonding formula is `min(0.41*sqrt(fc/(n*Ef*tf)), 0.9*eps_fu)`. No safety or strength reduction factors are used. Jack load follows the specimen's four-point arrangement and subtracts self-weight moment.

Self-weight uses an assumed unit weight of 24 kN/m3 and a nominal modulus proxy of 22.36 GPa. The self-weight moment is 1.0125 kN m and initial soffit strain is 0.000029. Neither density nor concrete modulus is measured in the paper.

### Fiber modulus must use a compatible thickness

| Material | Wet total thickness (mm) | Fiber volume | Inferred fiber-equivalent total (mm) | Fiber modulus (GPa) | Derived rupture strain | Debonding limit |
|---|---:|---:|---:|---:|---:|---:|
| Glass fiber | 2.6 | 11.0% | 0.286 | 72 | 0.02708 | 0.01278 |
| Carbon fiber | 2.1 | 19.0% | 0.399 | 230 | 0.01739 | 0.00605 |

The primary mapping treats total fiber volume as longitudinal effective area and neglects resin load contribution. It is an input assumption, not a measured composite property. A second sensitivity uses only the dominant-direction fiber mass fraction, whose alignment along the beam is not confirmed. A cured axial coupon would resolve the basis. The reported thickness is already the total laminate thickness; it is not multiplied again by the number of layers.

No U-wrap or independent anchorage is reported. A wrap strain limit is therefore inapplicable. The official guide preview confirms the guide and anchorage scope but does not expose the full equation clause. The equation comes from the supplied job and frozen method; full guide compliance is not claimed.

### Conditional predictions and retained failures

| Beam and strain assumption | Predicted ultimate (kN) | Test ultimate (kN) | Predicted/test | Predicted steel yield (kN) | Test yield (kN) | Yield ratio |
|---|---:|---:|---:|---:|---:|---:|
| Glass fiber, before damage, self weight only | 50.57 | 51.94 | 0.974 | 40.13 | 49.18 | 0.816 |
| Glass fiber, after damage, ignore initial strain | 50.60 | 50.09 | 1.010 | 40.15 | unreported | unavailable |
| Glass fiber, after damage, residual global curvature proxy | 48.49 | 50.09 | 0.968 | 37.63 | unreported | unavailable |
| Carbon fiber, before damage, self weight only | 64.05 | 66.24 | 0.967 | 48.76 | 58.12 | 0.839 |
| Carbon fiber, after damage, ignore initial strain | 64.04 | 63.22 | 1.013 | 48.88 | unreported | unavailable |
| Carbon fiber, after damage, residual global curvature proxy | 64.19 | 63.22 | 1.015 | 37.63 | unreported | unavailable |

The model predicts first steel-strain yield, whereas the paper determines an equivalent elasto-plastic yield from reduced stiffness. This definition mismatch, unreported coupon variation and cyclic response may explain poor yield agreement. No parameter was changed to improve it. Post-strengthened yield is not separately reported; the bare-stage yield must not be reused as a repaired yield.

| Material-basis diagnostic, before damage | Predicted ultimate (kN) | Predicted/test | Status |
|---|---:|---:|---|
| Glass fiber, before damage, dominant direction sensitivity | 49.50 | 0.953 | Conditional orientation sensitivity |
| Glass fiber, before damage, gross thickness diagnostic | 73.74 | 1.420 | Invalid fiber/gross pairing, retained |
| Carbon fiber, before damage, dominant direction sensitivity | 62.77 | 0.948 | Conditional orientation sensitivity |
| Carbon fiber, before damage, gross thickness diagnostic | 89.65 | 1.353 | Invalid fiber/gross pairing, retained |

### Initial strain after damage

The post-strengthened beams were already past their bare yield and retained permanent displacement. The second calculation uses a residual global-curvature proxy. It assigns the elastic four-point deflection shape to that residual displacement, and uses the bare steel-yield neutral axis to convert curvature to soffit strain. This is not the actual residual strain state. The American Concrete Institute elastic substrate treatment cannot represent yielded steel, local hinges, crushing or bond degradation.

| Beam | Residual displacement proxy (mm) | Reading bound (mm) | Initial substrate strain proxy |
|---|---:|---:|---:|
| Glass fiber, after damage | 13.41 | +/-1.0 | 0.00277 |
| Carbon fiber, after damage | 14.75 | +/-1.0 | 0.00304 |

Both zero-offset and residual-proxy results remain in the results file. Neither is promoted to an identified damaged-section prediction. Residual displacement alone cannot determine the neutral-axis location or plastic curvature distribution.

### Bare beam check

Indian Standard 456:2000, clause 38.1: plane sections, no concrete tension, 0.0035 crushing; parabola-rectangle scaled to 0.67 times strength, material safety factors removed, steel elastoplastic. Mean cylinder used directly as strength proxy because mean cube strength is missing; conditional benchmark, not a code design resistance.

| Bare beam | Predicted ultimate (kN) | Observed bare peak (kN) | Predicted/test | Predicted yield/test |
|---|---:|---:|---:|---:|
| Glass fiber, after damage | 37.97 | 43.88 | 0.865 | 0.860 |
| Carbon fiber, after damage | 37.97 | 44.63 | 0.851 | 0.876 |

The bare trials stopped for repair. Their observed peaks are not independent bare failure capacities. An additional direct-cylinder parabola-rectangle result is retained in the JSON to expose the strength-basis difference.

![Capacity predictions](/Users/sreekaraditya/Desktop/StrucIQ_Review2_230x300/00_SHOW_IN_REVIEW/08_benchmark_ozturkoglu2024/01_capacity_predicted_vs_test.png)

## Vibration versus damage

Vibration stiffness index is the squared frequency ratio. Static stiffness is the envelope load divided by imposed displacement, normalized to the first-crack load/displacement secant. This includes permanent deformation and is not a reloading tangent or an independently measured service stiffness. Dynamic testing was unloaded with the jack detached, but residual deformation remained. The quantities answer different physical questions.

The pixel method calibrates the outer plot frame and grid ticks, selects the colored or black loading plateau and saves an overlay. Slightly left-of-target readings avoid vertical cycle drops. The carbon bare D1 plateau is obscured at the target, so the nearest clear flat segment is used with a larger displacement reading bound.

Typical reading bounds are +/-1.0 kN and +/-0.5 mm; the carbon bare D1 displacement bound is +/-1.0 mm. These are reading bounds, not confidence intervals. Baseline-proxy reading sensitivity is propagated separately from beam-bootstrap uncertainty.

| Beam | Stage | Condition | Load from figure (kN) | Static secant left | Vertical mode one left | Vertical mode two left |
|---|---|---|---:|---:|---:|---:|
| Glass fiber, before damage | D1 | strengthened | 51.99 | 54.2% | 90.1% | 93.1% |
| Glass fiber, before damage | D2 | strengthened | 52.69 | 36.6% | 83.5% | 92.0% |
| Glass fiber, before damage | D3 | strengthened | 48.80 | 25.4% | 76.9% | 91.0% |
| Glass fiber, before damage | D4 | strengthened | 45.51 | 19.0% | 74.0% | 90.8% |
| Carbon fiber, before damage | D1 | strengthened | 64.02 | 62.8% | 61.5% | 77.6% |
| Glass fiber, after damage | D1 | bare | 42.57 | 45.1% | 97.6% | 98.2% |
| Glass fiber, after damage | D2 | strengthened | 49.81 | 35.2% | 71.9% | 85.6% |
| Glass fiber, after damage | D3 | strengthened | 48.82 | 25.8% | 69.9% | 83.9% |
| Glass fiber, after damage | D4 | strengthened | 47.80 | 20.2% | 68.7% | 83.9% |
| Carbon fiber, after damage | D1 | bare | 44.40 | 47.6% | 87.8% | 83.0% |
| Carbon fiber, after damage | D2 | strengthened | 63.21 | 45.1% | 74.8% | 82.3% |

The retained counterexample is Carbon fiber, before damage at D1: static secant left 62.8% versus vibration left 61.5%. The difference is small relative to source-reading and stiffness-definition uncertainty; no universal ordering is established.

### Kappa fit and uncertainty

Loss ratios are fitted through the origin. The bootstrap resamples 4 beam clusters with all their steps, using 20000 draws and seed 20241030. The sample is small, combines different strengthening histories and has unequal numbers of steps.

| Vibration mode | Pooled kappa | Beam-bootstrap 95% interval |
|---|---:|---|
| Vertical first | 0.348 | 0.306 to 0.484 |
| Vertical second | 0.190 | 0.139 to 0.378 |

| Beam | First-mode kappa | Matched levels |
|---|---:|---:|
| Glass fiber, before damage | 0.292 | 4 |
| Carbon fiber, before damage | 1.035 | 1 |
| Glass fiber, after damage | 0.350 | 4 |
| Carbon fiber, after damage | 0.351 | 2 |

Assigning all static ratios to their low or high source-reading bounds changes first-mode kappa to 0.321 and 0.381. This sensitivity is not included in the beam-bootstrap interval. The interval also excludes bias from baseline choice, plastic deformation, mass changes and source discrepancies.

The earlier Musial raw and compliance-corrected results are 0.391 and 0.312. The central value here is compatible with that range, but agreement of different secant/tangent definitions does not establish a transferable calibration. Keep this series separate in any pooled table and label its stiffness definition.

### Source discrepancies kept

- Glass fiber, before damage: figure load 52.69 kN versus tabulated ultimate 51.94 kN, difference 0.75 kN. Later figure plateau exceeds tabulated ultimate. No rescaling applied.
- Carbon fiber, before damage: figure load 64.02 kN versus tabulated ultimate 66.24 kN, difference 2.22 kN. Figure 4 near D1 reads below Table 4 peak; capacity comparison uses table, secant analysis uses figure. This discrepancy is larger than the pure pixel reading bound.

Reloading and unloading readings were attempted and retained. Overlapping branches are not labelled by time or cycle direction clearly enough to establish the correct tangent at each modal state. They are excluded. Immediate after-bonding D1 frequencies also remain modal-only, with no fabricated static match.

![Stiffness comparison](/Users/sreekaraditya/Desktop/StrucIQ_Review2_230x300/00_SHOW_IN_REVIEW/08_benchmark_ozturkoglu2024/02_static_vs_vibration.png)

## H1: nominally identical beams

The two post-strengthened beams were bare at an imposed 30 mm D1 displacement. Their endpoint loads read 42.57 and 44.40 kN, and their static secant ratios are 45.1% and 47.6%. Their static spread is 2.51 percentage points, with overlapping reading bounds. The vibration spread is 9.82 percentage points. Nominally equal specimens do differ, but the protocol does not supply vibration measurements at a matched load, so equal-load H1 remains untested here.

## Twin bias-learning check

At the previous measured state, learn the logarithm of vibration stiffness divided by static stiffness. At the next state, multiply the new vibration stiffness by the exponential of the negative previous bias. Deflection-proxy error is true stiffness divided by predicted stiffness, minus unity. Holding the last static check and normalized vibration alone are the baselines. This is the same algebra as the existing test. Consecutive damage-level gaps replace its load gaps; no calibration uses a target-stage measurement.

Only strengthened histories with enough matched stages are used. No prediction crosses the bare-to-repaired intervention. Error bounds from static reading and frequency rounding are stored for every prediction.

| Check spacing | Predictions | Median bias-learning error | Median hold error | Median vibration-only error | Maximum bias-learning error |
|---|---:|---:|---:|---:|---:|
| gap 1 damage levels | 5 | 24.4% | 26.5% | 66.9% | 27.2% |
| gap 2 damage levels | 3 | 41.5% | 48.2% | 70.5% | 45.0% |

These errors concern an implied deflection at equal diagnostic force derived from successive large-displacement secants. They are not measured service-deflection predictions. Learning the bias helps against vibration alone, but it does not establish the earlier service-accuracy target in this series.

## Can vibration confirm the retrofit?

| Beam | Direction | Mode | Frequency change | Apparent squared-frequency change |
|---|---|---:|---:|---:|
| Glass fiber, after damage | vertical | 1 | -9.01% | -17.20% |
| Glass fiber, after damage | vertical | 2 | -3.23% | -6.35% |
| Glass fiber, after damage | vertical | 3 | -3.56% | -6.99% |
| Glass fiber, after damage | horizontal | 1 | +37.16% | +88.12% |
| Glass fiber, after damage | horizontal | 2 | +4.23% | +8.64% |
| Glass fiber, after damage | horizontal | 3 | +12.65% | +26.90% |
| Carbon fiber, after damage | vertical | 1 | +1.17% | +2.36% |
| Carbon fiber, after damage | vertical | 2 | +2.52% | +5.11% |
| Carbon fiber, after damage | vertical | 3 | +12.60% | +26.79% |
| Carbon fiber, after damage | horizontal | 1 | +66.72% | +177.95% |
| Carbon fiber, after damage | horizontal | 2 | +16.07% | +34.73% |
| Carbon fiber, after damage | horizontal | 3 | -11.81% | -22.22% |

Changes use the after/before D1 frequency-ratio quotient, not the difference between their ratios to the undamaged state. Printed-ratio rounding bounds are provided in the result file. Measurement repeatability is not reported, so small changes are not assigned statistical significance.

- Glass fiber, after damage: observed peak capacity rises from 43.88 to 50.09 kN, a 14.15% gain. This is capacity gain, not immediate static-stiffness recovery.
- Carbon fiber, after damage: observed peak capacity rises from 44.63 to 63.22 kN, a 41.65% gain. This is capacity gain, not immediate static-stiffness recovery.

The supplied Musial context reports frequency gains of about 1% to 4% against static-stiffness gains of about 20% to 30%. Those approximate ranges are carried from the job context, not newly extracted. Here even the sign of the vertical signal depends on the strengthening material. The paper proposes transport and curing under self-weight as possible explanations. A frequency change can show a change of state, but a static check is needed to verify useful repair.

![Retrofit signal](/Users/sreekaraditya/Desktop/StrucIQ_Review2_230x300/00_SHOW_IN_REVIEW/08_benchmark_ozturkoglu2024/03_retrofit_vertical_signal.png)

## Limitations and human evidence needed

- Concrete elastic modulus and density not printed
- Mean cube strength not printed
- Cured composite axial coupon properties and longitudinal fiber alignment not printed
- Top bar depth and top clear cover not explicitly dimensioned
- Post-strengthening yield not separately reported
- No static measurement immediately after strengthening at D1 without further loading
- Residual strain field and plastic-hinge length not reported

The requested numerical analyses and reproducible outputs are complete within these limits. Unconditional capacity validation, an identified post-yield residual-state prediction, equal-load H1, reloading stiffness and service-deflection validation remain unavailable. No slide deck, workbook, parent review README or ReBuild file is updated.

## Files and provenance

`ozturkoglu_extract.json`: sourced inputs and missing fields. `frp_results.json`: every capacity scenario, strain state and force residual. `digitised_static.json`: pixels, axes, bounds and excluded reads. `h1_h2_results.json`: paired ratios, cluster bootstrap and twin rows. `retrofit_signal_results.json`: every modal repair change. `results_summary.json`: headlines with pooling and scope flags. `QA.json` and `manifest.json`: execution and integrity checks. `RUN.md`: rerun instructions.

Source: [Ozturkoglu and colleagues, Applied Sciences, 2024](https://doi.org/10.3390/app14219920). Source pages and figure overlays reproduce the open-access paper under its Creative Commons Attribution license. Source PDF SHA-256: `fafce008a156ef295b2da8611b8b10ab2e6a6542b1e5e989b23e511bfe4ca272`.

Method reference: [American Concrete Institute guide preview](https://www.concrete.org/Portals/0/Files/PDF/Previews/440.2-23_preview.pdf); the full equation clause was not independently available. Existing Musial results and code are preserved as hashed read-only snapshots.
