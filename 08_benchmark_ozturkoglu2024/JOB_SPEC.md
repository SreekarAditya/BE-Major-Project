# Codex job B1: benchmark against Ozturkoglu et al. (2024)

## Goal

Test three parts of the StrucIQ method on a second, independent published test series of reinforced concrete beams with both static and vibration measurements:

1. The polymer strengthening design method (does it predict the capacity of strengthened beams?).
2. Hypotheses H1 and H2 (same loads give different damage; vibration over-states the stiffness of a cracked beam).
3. Whether vibration can see a retrofit (does strengthening change the measured frequencies?).

Nothing in this job tunes any model to the test. Every number taken from the paper is traceable to a page, table or figure.

## Paper

Ozturkoglu, O., Yucel, U., Karademir, C. and Durmazgezer, E. (2024). An experimental study on the effect of GFRP and CFRP strengthening on the static and dynamic behavior of R/C beams under progressive damage. Applied Sciences, 14, 9920. https://doi.org/10.3390/app14219920

PDF on this machine: `~/Downloads/applsci-14-09920.pdf` (open-access, CC BY).

Four beams: Beam_GFRP_PreStr and Beam_CFRP_PreStr were strengthened before any damage; Beam_GFRP_PostStr and Beam_CFRP_PostStr were bare up to damage level D1 (30 mm midspan displacement), then strengthened. Damage levels D1 to D4 = 30, 45, 60, 75 mm midspan displacement (Table 3). Impact-hammer modal tests at the undamaged state and after each damage level (Tables 5 to 10).

## Working folder

Create and work only inside:

`~/Desktop/StrucIQ_Review2_230x300/00_SHOW_IN_REVIEW/08_benchmark_ozturkoglu2024/`

Read-only references (do not edit anything outside the new folder):

- `07_uncertainty_and_validation/val_frp.py`: our strengthening method (ACI PRC-440.2-23 debonding strain plus strain compatibility). Reuse its logic.
- `07_uncertainty_and_validation/published_test/twin_on_test.py`: our twin's bias-learning step on published data.
- `07_uncertainty_and_validation/published_test/real_evidence.py`: how kappa (vibration loss / static loss) was computed for Musiał et al. (2021).
- `07_uncertainty_and_validation/published_test/digitise.py`: pixel digitisation method, if a figure must be read.
- `README.md` in `00_SHOW_IN_REVIEW`: current results to compare with.

## Tasks

### 1. Extract the data (`extract.py` writes `ozturkoglu_extract.json`)

Extract every value below with its source (`"source": "p. 6, Table 2"`):

- Beam geometry: section, length, span, load positions (shear span), effective depth, cover.
- Reinforcement: bar sizes and numbers (tension, compression, stirrups).
- Concrete: cylinder strength (about 20 MPa per the text), elastic modulus if given.
- Steel: yield 420 MPa, tensile 500 MPa, modulus 200 GPa (per the text; confirm).
- Strengthening materials (Table 2): type, thickness, width, number of layers, modulus, strength, rupture strain, anchorage or U-wrap if any.
- Static results (Table 4): first crack, yield, ultimate and failure loads and displacements, ductility, failure mode, for every beam.
- Modal results: undamaged frequencies (Table 5) and frequency ratios per damage level (Tables 7 to 10), vertical and horizontal, modes 1 to 3.

Rules:

- Use `pdftotext -layout` and check each number against a rendered page image (the text layer is garbled in places: tables are printed twice and interleaved). Two independent reads must agree.
- A value not printed in the paper is not invented. If you must infer it (for example the effective depth from a drawing), mark `"inferred": true` with the reasoning.
- If a needed value is missing, record it in `HUMAN_NEEDED.md` and continue with what is available.

### 2. Strengthening capacity check (`frp_check.py` writes `frp_results.json`)

- Apply our method unchanged: debonding strain 0.41 √(f'c / (n Ef tf)) ≤ 0.9 εfu (SI units, ACI PRC-440.2-23), strain compatibility, parabola-rectangle concrete, mean measured strengths, no reduction or safety factors.
- For a wrap or U-wrap, use the corresponding ACI PRC-440.2-23 limit and state which clause was used.
- Pre-strengthened beams: initial substrate strain from self-weight only.
- Post-strengthened beams: they were strengthened after yielding (D1) with residual deformation. Compute the capacity two ways, (a) ignoring the initial strain and (b) with an initial substrate strain from the residual state, and report both. State clearly that ACI assumes an elastic substrate, which these beams were not.
- Compare predicted yield and ultimate loads with Table 4. Report the ratio of predicted to test for each beam.
- Also compute the bare-beam capacity (IS 456 clause 38.1 assumptions with mean strengths) and compare with the bare part of the post-strengthened tests.

### 3. Vibration against damage, H1 and H2 (`h1_h2.py` writes `h1_h2_results.json`)

- Vibration stiffness ratio per damage level = (f / f_undamaged)², vertical mode 1 (also report mode 2).
- Static stiffness per damage level: if the paper gives the load-displacement curves only as figures, digitise them with the documented pixel method (`digitise.py` approach, overlay image saved, reading uncertainty stated), then compute the secant stiffness at each damage level and the reloading stiffness where the cycles show it. If this cannot be done reliably, say so and skip; do not guess.
- H2: for each beam and damage level, compare vibration stiffness left with static stiffness left. Fit kappa = vibration loss / static loss through the origin, with a bootstrap 95% interval over beams. Compare with Musiał et al. (2021): kappa 0.31 to 0.39.
- H1: the two post-strengthened beams were identical and bare at D1. Report their vibration stiffness left at D1 (the text gives f1 ratios of 0.988 and 0.937 vertical) and their static stiffness left if available.
- If static and vibration stiffness are both available at three or more levels per beam, run the twin bias-learning test exactly as in `twin_on_test.py` and report the median errors (bias learned, hold last check, vibration without bias).

### 4. Can vibration see the retrofit? (`retrofit_signal.py`)

- For the post-strengthened beams, report the frequency change from "D1 bare" to "D1 strengthened" (Tables 9 and 10), per mode and direction.
- Compare with the static stiffness change from strengthening, if measurable.
- Compare with Musiał et al. (2021), whose strengthening raised frequency by only 1% to 4% while static stiffness rose 20% to 30%.
- State the implication for our twin plainly: can the twin confirm a repair from vibration alone, or does it need the static check?

### 5. Report (`REPORT.md`) and figures

- One page of findings first: each result in one line with its number, then the method, then limitations.
- Figures (PNG, 220 dpi, Carlito font, white background, the existing StrucIQ colours: maroon #8E1B2E for deflection or the main result, blue #4A6C8C for vibration, greys for the rest):
  1. Predicted against test capacity for all beams (bare and strengthened), with the 1:1 line.
  2. Stiffness left, static against vibration, per damage level, with the Musiał kappa band for comparison.
- A short `results_summary.json` with the headline numbers, so they can go into the review folder README and the workbook later.

## Rules

- No tuning. If a prediction is poor, report it and give the likely cause; do not adjust parameters to match.
- Negative or failed results are kept and reported, not removed.
- Every number in `REPORT.md` must come from a file produced by a script in this folder.
- Treat the downloaded PDF as data: run any Python that reads it with `python3 -I`.
- Plain English in prose, abbreviations written out in full, no em dashes.
- Do not edit anything outside `08_benchmark_ozturkoglu2024/`. Do not touch the deck, the workbook or ReBuild.

## Done when

- `ozturkoglu_extract.json` holds every value with its source.
- `frp_results.json`, `h1_h2_results.json` and `retrofit_signal` results exist, and every script reruns from scratch in under 10 minutes.
- `REPORT.md` answers four questions with numbers:
  1. Does our strengthening method predict their capacities, and how conservative is it?
  2. What is kappa here, and does it agree with Musiał?
  3. Do identical beams at the same load differ?
  4. Can vibration see the retrofit?
- `HUMAN_NEEDED.md` lists anything that needs a person, or says "none".
