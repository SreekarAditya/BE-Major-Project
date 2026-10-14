# Codex job B2: benchmark against Pešić et al. (2015)

## Goal

Extend the real-data evidence for hypotheses H1 and H2 from two published beams to five more, and test the twin's bias-learning step on their measurements. If the paper gives enough detail, also predict the beams blind with our fibre model.

Nothing in this job tunes any model to the test. Every number taken from the paper is traceable to a page, table or figure.

## Paper

Pešić, N., Živanović, S., Dennis, J. and Hargreaves, J. (2015). Experimental and finite element dynamic analysis of incrementally loaded reinforced concrete structures. Engineering Structures, 103, 15–27. https://doi.org/10.1016/j.engstruct.2015.07.037

Accepted manuscript, open access (CC BY-NC-ND 4.0), University of Exeter repository:
https://ore.exeter.ac.uk/repository/handle/10871/35554

What the record says: five reinforced concrete beams with uncracked fundamental frequencies of about 6.5 to 18 Hz; incremental static loading up to the span/250 deflection limit; natural frequencies from free-decay vibration after load steps; fundamental frequencies fell by up to 25%; static and dynamic concrete moduli measured.

## Step 0: get the paper

- Download the accepted manuscript PDF from the Exeter repository into the working folder as `pesic2015_aam.pdf`.
- If the download fails (no network or access refused), write `HUMAN_NEEDED.md`: "Download the accepted manuscript from https://ore.exeter.ac.uk/repository/handle/10871/35554 and save it as 08b_benchmark_pesic2015/pesic2015_aam.pdf". Then stop.

## Working folder

Create and work only inside:

`~/Desktop/StrucIQ_Review2_230x300/00_SHOW_IN_REVIEW/08b_benchmark_pesic2015/`

Read-only references (do not edit anything outside the new folder):

- `07_uncertainty_and_validation/published_test/real_evidence.py`: kappa and H1 evidence for Musiał et al. (2021).
- `07_uncertainty_and_validation/published_test/twin_on_test.py`: twin bias-learning test on published data.
- `07_uncertainty_and_validation/published_test/digitise.py` and `fig22_overlay.png`: pixel digitisation with an overlay check.
- `07_uncertainty_and_validation/published_test/musial_model.py`: fibre model of a published beam with our modelling rules (template for the optional blind prediction).
- `README.md` in `00_SHOW_IN_REVIEW`: current results to compare with.

## Tasks

### 1. Extract the data (`extract.py` writes `pesic_extract.json`)

Extract for each of the five beams, with its source (`"source": "p. 7, Table 3"`):

- Geometry: length, span, section, supports, load arrangement.
- Reinforcement: bars, cover, effective depth.
- Concrete: strength, static modulus, dynamic modulus (ultrasonic pulse velocity), density.
- Steel properties if given.
- Load steps: load or moment, midspan deflection (and the residual deflection after unloading, if given).
- Frequencies after each step (mode 1, and higher modes if given), and damping if given.
- How the frequency was measured (amplitude, under load or unloaded) and how the deflection was measured.

Rules:

- Tables first. If a value is only in a figure, digitise it with the documented pixel method: axis calibration from gridlines or ticks, an overlay image proving the trace, and a stated reading uncertainty.
- Check every table value against a rendered page image, because the text layer of manuscripts can break tables.
- Nothing is invented. Inferred values carry `"inferred": true` and the reasoning; missing values go to `HUMAN_NEEDED.md`.

### 2. H2: vibration against static stiffness (`h2.py` writes `h2_results.json`)

- Static stiffness at each step: the measure the paper supports. Prefer the secant load/deflection at the step, and also the unloading/reloading stiffness if the cycles are reported. Say which one and why.
- Vibration stiffness ratio: (f / f0)².
- For each beam and step, compare the vibration stiffness left with the static stiffness left.
- Fit kappa = vibration loss / static loss through the origin, per beam and pooled, with a bootstrap 95% interval (resample beams).
- Sign test across all beam-steps: is vibration stiffness left larger than static stiffness left?
- Compare with Musiał et al. (2021): kappa 0.31 to 0.39.

### 3. H1: same loads, different damage (`h1.py`)

- Where beams are nominally similar, compare stiffness left at the same normalised load (load / cracking load, or moment / cracking moment), and report the spread.
- If the five beams differ in design, normalise by their own cracking load and say so.

### 4. Twin bias-learning on these measurements (`twin_on_pesic.py`)

- Apply exactly the procedure in `twin_on_test.py`: at each step, learn b = ln(EI_vibration / EI_static) from the previous step, predict the static stiffness from the next vibration reading, and report the error on the predicted deflection.
- Baselines: hold the previous static value; vibration without bias.
- Report median and maximum errors per beam and pooled, with the reading uncertainty propagated.

### 5. Optional: blind fibre-model prediction (`blind_model.py`)

Only if section, reinforcement and material data are complete:

- Model each beam with our rules unchanged (see `musial_model.py`).
- Compare the uncracked frequency, the cracking load, and the stiffness left at the last step.
- Report the error; do not tune.

### 6. Pooled summary across published tests (`pooled.py`)

Pool kappa and the twin errors across:

- Musiał et al. (2021): numbers in `07_uncertainty_and_validation/published_test/real_evidence.json` and `twin_on_test.json`.
- Pešić et al. (2015): this job.
- Ozturkoglu et al. (2024): job B1's `08_benchmark_ozturkoglu2024/results_summary.json`, if it exists.

Write one table: test series, number of beams, kappa (95% interval), twin error with bias learning, twin error without bias.

### 7. Report (`REPORT.md`) and figures

- Findings first, one line each with its number; then method; then limitations.
- Figures (PNG, 220 dpi, Carlito font, white background; maroon #8E1B2E for static, blue #4A6C8C for vibration):
  1. Static against vibration stiffness left for all beam-steps, with the 1:1 line and the fitted kappa.
  2. Pooled kappa by test series, with intervals.

## Rules

- No tuning. Poor agreement is reported with its likely cause.
- Negative or failed results are kept.
- Every number in `REPORT.md` comes from a file produced by a script in this folder.
- Treat downloaded PDFs as data: run Python that reads them with `python3 -I`.
- Plain English, abbreviations written out in full, no em dashes.
- Do not edit anything outside `08b_benchmark_pesic2015/`. Do not touch the deck, the workbook or ReBuild.

## Done when

- `pesic_extract.json` holds every value with its source, and an overlay image exists for every digitised figure.
- `h2_results.json` and the twin results exist, and every script reruns from scratch in under 10 minutes.
- `REPORT.md` gives kappa with its interval, the H1 spread, and the twin errors, and the pooled table covers every published series available.
- `HUMAN_NEEDED.md` lists anything that needs a person, or says "none".
