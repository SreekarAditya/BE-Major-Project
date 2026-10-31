# StrucIQ Beam Damage and Retrofit Dataset, version 1.0

Simulated staged damage, vibration, crack width, corrosion, long-term and retrofit response of simply supported reinforced concrete beams: a reference specimen study, a 10,000-beam design-space population, strengthening simulated by mechanics, corrosion and sustained-load stages, a fatigue estimate, and validation against published laboratory tests.

**DOI:** [10.5281/zenodo.23769960](https://doi.org/10.5281/zenodo.23769960)

**Authors:** P. Sreekar Aditya Reddy, M. Bhagirath Reddy, P. Sahasra Reddy
**Licence:** data under Creative Commons Attribution 4.0 International (CC BY 4.0); code under the MIT licence. See `LICENSE-DATA.txt` and `LICENSE-CODE.txt`.
**How to cite:** Reddy, P. S. A., Reddy, M. B., & Reddy, P. S. (2026). *StrucIQ Beam Damage and Retrofit Dataset* (Version 1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23769960 (also in `CITATION.cff`).

## What the dataset is for

Damage in a cracked reinforced concrete beam shows up differently depending on how it is measured. Static deflection sees the full loss of flexural stiffness; a small-amplitude vibration test sees much less, because cracks close during part of each vibration cycle. This dataset gives both, across a wide range of beam designs, together with crack widths, steel stresses, residual deflections and the response after strengthening. It is meant for:

- developing and testing methods that estimate the condition of a beam from measurements (deflection, natural frequency, crack width);
- studying how stiffness loss, vibration bias and crack width depend on span, section, reinforcement and material grade;
- training and checking retrofit decision methods against simulated strengthened behaviour;
- benchmarking such methods, including on beams larger than those they were trained on.

## Contents

| Folder | Contents |
|---|---|
| `01_reference_specimen_monte_carlo` | 300 beams of one specimen design (230 x 300 mm, 3.0 m span, M30, 3 bars of 12 mm Fe500, four-point bending) with material scatter; staged damage at 35, 50, 65 and 72 kN; scripts and figures |
| `02_retrofit_population_10000` | 10,000 beams designed to IS 456:2000 with damage levels from folder 01, checked for flexure, shear, deflection and crack width before and after each retrofit scheme; least intrusive compliant scheme; decision tree; 3,000-beam convergence run |
| `03_validation_published_tests` | Blind reproduction of three published test programmes (see Validation) with digitised data and scripts |
| `04_model_and_twin` | The fibre beam model of the specimen, its parameter file and verified output, the digital twin estimator, and the IS 456:2000 design calculation |
| `05_independent_check_staad` | STAAD.Pro analysis files and output screenshots for the specimen, used as an independent check of the fibre model's elastic response |
| `06_design_space_population` | 10,000 beams sampled across the design space (generator, design table, raw output, processed tables, measurement layer, benchmarks), the strengthening-by-mechanics run, the corrosion and sustained-load stages, the fatigue estimate, the continuum cross-check and their validation |
| `quickstart.ipynb` | Loads the main tables and reproduces the headline results and a benchmark baseline |
| `MANIFEST.csv` | Every file with its size and SHA-256 checksum |
| `CHANGELOG.md`, `CITATION.cff`, `LICENSE-DATA.txt`, `LICENSE-CODE.txt` | Version history, citation, licences |

## Quick start

The processed tables of folder 06 are plain CSV files and can be used without running any simulation. `quickstart.ipynb` (Python 3 with `pandas`, `numpy`, `matplotlib` and `scikit-learn`) loads them, plots static against vibration stiffness loss, the corroded peak loads and the sustained-load deflections, and runs a short version of benchmark task A1. Every column is defined in `06_design_space_population/data_dictionary.csv`. Before fitting models, filter on the quality flags (`run_ok`, `reached`, `push_complete`, `push_diverged`, `valid`, `frequency_rise`, `capacity_gain_valid`), described under "Failed runs and quality flags".

### Tables of folder 06 (`06_design_space_population/tables`)

| File | Rows | One row per |
|---|---|---|
| `beams.csv` | 10,000 | beam: design, sampled materials, hand yield load, peak load, flags |
| `stages.csv` | 59,513 | beam and damage stage (0 to 5): deflections, frequencies, stiffness left, steel stress and strain, curvature, neutral axis, crack widths |
| `stages_measured.csv` | 57,444 | reached stage: one simulated instrument reading of each measured quantity |
| `envelopes.csv` | 314,600 | point of the 40-point load-deflection curve of each final push |
| `splits.csv` | 10,000 | beam: benchmark split (random, extrapolation) |
| `benchmark_results.json` | | benchmark baselines |
| `retrofit.csv` | 4,000 | beam (0 to 999) and strengthening scheme |
| `retrofit_envelopes.csv` | 158,400 | curve point of each retrofit push |
| `corrosion_runs.csv` | 6,000 | beam (0 to 1999) and steel mass loss |
| `corrosion_stages.csv` | 31,810 | corroded beam and stage |
| `corrosion_envelopes.csv` | 237,800 | curve point of each corroded beam |
| `sustained_runs.csv` | 2,000 | beam (0 to 999) and sustained-load case |
| `sustained_history.csv` | 8,000 | beam, case and time under load (0, 1, 10, 50 years) |
| `fatigue.csv` | 68,398 | reached stage of the main and corroded beams: fatigue life of the tension steel |
| `continuum_comparison.csv` | 40 | beam of the continuum cross-check |
| `quality_summary.json`, `conditions_summary.json` | | summary numbers of the quality flags and condition stages |

### File formats

CSV files are UTF-8, comma-separated, with a header row; booleans are `True`/`False` and missing values are empty. Raw simulation output (`raw/`, `raw_retrofit/`, `raw_continuum/`, `raw_corrosion/`, `raw_sustained/`) is JSON Lines: one JSON record per line, one record per run, spread over files named after the machine that produced them. Where a run appears more than once (a retry), the processing scripts use the last record in sorted file order; the raw files keep every attempt. Units are N, mm and MPa in the models and kN for loads in the tables, as stated in the data dictionary.

## Folder 06: the design-space population

### Design

10,000 beams from a Latin hypercube design (`code/design.py`, seed 2027):

| Variable | Range |
|---|---|
| Span | 2.0 to 6.0 m |
| Width | 200 to 300 mm |
| Span / effective depth | 10 to 16 (overall depth 250 to 600 mm) |
| Clear cover | 25 to 40 mm, 8 mm stirrups |
| Tension steel | from the IS 456:2000 minimum to 95% of the under-reinforced limit; bars of 12, 16, 20 or 25 mm in one layer, clear spacing at least the bar diameter and 25 mm |
| Compression steel | 2 bars of 10 mm (width up to 250 mm) or 12 mm |
| Concrete grade | M20, M25, M30, M35, M40 |
| Steel grade | Fe415, Fe500 |
| Loading | half four-point bending (loads at the third points), half uniformly distributed |

Material properties of each beam are sampled as in folder 01: characteristic strength normal about the grade with the IS 456:2000 Table 8 standard deviation (truncated 10 MPa below the grade); elastic modulus 5000 sqrt(fck) times a lognormal factor (coefficient of variation 15%); tensile strength 0.7 sqrt(fck) times a lognormal factor (15%); tension-softening slope 0.05 to 0.10 of the elastic modulus; yield strength normal with a 5% coefficient of variation.

### Model and loading protocol

The fibre model is the one of folder 01 (`code/gen.py` reproduces folder 01's beams to better than 1e-4 mm; `code/verify.py`): OpenSeesPy, 24 force-based beam-column elements, Concrete02 concrete with linear tension softening, Steel02 steel. Flexure only: shear failure and bond slip are not modelled.

Each beam is taken through five damage stages at 0.43, 0.62, 0.80, 0.89 and 1.00 times its hand-calculated first-yield load. After each stage it is unloaded, given a diagnostic load cycle (0.185 times the yield load) and a service cycle (0.37 times the yield load), and its first three bending frequencies are computed in the unloaded state. A final push to span/100 gives the peak load and a 40-point load-deflection curve. A stage the solver cannot reach, or a push it cannot complete, is kept and flagged.

### Vibration: open-crack and breathing-crack frequencies

The fibre model's frequency of the unloaded cracked beam (`f1_hz`) treats cracks as open, so it tracks static stiffness closely. Real beams vibrate at higher frequencies because cracks close during part of each cycle. The dataset therefore also gives the breathing-crack frequency, the standard bilinear-oscillator result

f_breathing = 2 f_open f_closed / (f_open + f_closed),

with f_open the cracked-beam frequency and f_closed the undamaged frequency of the same beam. No parameter is fitted. On the beams of Musiał et al. (2021) it predicts 76% vibration stiffness left at 44.5 kN against 78% and 83% measured, and a vibration bias (share of the static stiffness loss that vibration registers) of 0.44 against 0.42 measured (`validation/check_breathing_musial2021.py`). Across the population the bias rises with damage, from 0.48 at the first stage to 0.62 at the last (medians).

### Crack width

Crack width is estimated with IS 456:2000 Annex F at the soffit midway between bottom bars, from the strain distribution of the midspan section, both under the stage load (`peak_crack_width_mm`) and under the service load after the stage (`service_crack_width_mm`). It is a code estimate from the computed strains, not a discrete-crack simulation.

### Measurement layer

`tables/stages_measured.csv` gives one realisation (seed 2027) of what instruments would read, so that methods can be tested on imperfect data:

| Quantity | Assumed measurement |
|---|---|
| Breathing-crack frequency | identification scatter 0.5% (standard deviation); concrete temperature uniform 15 to 40 C with -0.2% frequency per C above 25 C |
| Deflections and residual | 0.01 mm plus 0.5% of the reading (standard deviation) |
| Crack widths | 0.01 mm standard deviation, reported to 0.01 mm, not negative |

These are stated assumptions, not calibrated instrument data. `code/process.py` generates further realisations with other seeds.

### Strengthening by mechanics

For beams 0 to 999 (`raw_retrofit/`), the damage history is run to the fourth stage (0.89 times the yield load), the beam is unloaded, and one of four cases is applied: no strengthening (control), carbon fibre laminates, a bonded steel plate, or a reinforced concrete jacket (`code/retrofit_mech.py`). Strengthening is added as parallel elements whose fibres are set to be stress-free at installation, so they carry only the strain added afterwards (see the installation check below). The beam is then cycled to the diagnostic and service loads, its frequencies are computed, and it is pushed to span/100.

| Scheme | Representation |
|---|---|
| Laminates | strips 50 x 1.2 mm (2 if width < 260 mm, else 3), 165 GPa, tension only, lost at the ACI PRC-440.2-23 debonding strain |
| Steel plate | 100 x 5 mm, yield 250 MPa, assumed anchored (no debonding) |
| Jacket | 75 mm U-jacket on the soffit and both sides, M30 nominal, compression-only concrete, 2 bars of 12 mm; jacket mass added |

Installation is on the unloaded beam (dead load is not modelled). Over the deflection range reached by both the strengthened push and the control push of the same beam, the median capacity gain is 44% for the jacket, 36% for the plate and 18% for the laminates (5th to 95th percentile 23 to 85%, 18 to 71% and 9 to 42%); `capacity_gain_valid` marks the comparisons in which that range extends past the deflection at which the control reaches 95% of its peak (2,950 of 2,970). The strengthening is not perfectly stress-free at installation: the largest moment it carries just after installation is a median 0.9% of the hand yield moment for the jacket (95th percentile 2.1%), 0.3% for the plate and effectively zero for the laminates (`install_moment_ratio`). Validation: on the strengthened beams of Musiał et al. (2021), the model gives 79.4 and 105.9 kN against 90.2 and 116.0 kN tested (12% and 9% on the safe side), in line with a strain-compatibility calculation with the same debonding strain (80.0 and 106.8 kN) (`validation/check_strengthened_musial2021.py`).

### Continuum cross-check

For 40 beams spread over span, depth and loading (`raw_continuum/`), a plane-stress continuum model (ASDConcrete3D, bars and stirrups as truss elements) is pushed monotonically (`code/cont_gen.py`). Its first frequency, cracking load, deflections at the stage loads and peak load are compared with the fibre model in `tables/continuum_comparison.csv`.

The two models agree on the undamaged beam and disagree once it cracks. The continuum first frequency is a median 0.96 of the fibre value (10th to 90th percentile 0.94 to 0.97). Under load the continuum beam is softer: at the stage loads its midspan deflection is a median 1.75, 1.93, 1.62, 1.52 and 1.36 times the fibre deflection at stages 1 to 5 (stages it reached; 32, 24, 13, 12 and 7 beams), and nine beams that remain nearly uncracked at the first stage agree within 4%. Only 12 of the 40 continuum pushes reach span/100; where a peak was reached, the continuum peak load is 0.56 to 0.97 of the fibre value. The continuum model represents shear deformation and diagonal cracking, which the fibre model does not, and smears cracking over its elements; the fibre model is flexure-only. Which is closer to real beams of these proportions cannot be settled from the models alone; the fibre model is the one validated against tests (folder 03). Users who need cracked-state deflections of short or deep beams should treat the fibre values as a lower bound.

### Corrosion

For beams 0 to 1999 (`raw_corrosion/`, `code/corrosion.py`), the staged protocol is repeated on the same beam with uniformly corroded longitudinal bars at 5, 10 and 15% mass loss (6,000 records). Corrosion is represented through the section and materials only:

| Effect | Relation |
|---|---|
| Bar area | reduced by the mass loss |
| Yield strength | fy (1 - 0.005 psi), psi in %, on the residual area (Du, Clark & Chan, 2005a) |
| Strain at maximum stress | 0.08 (1 - 0.05 psi); the bar carries no stress beyond it (Du, Clark & Chan, 2005b) |
| Cover concrete in compression | strength divided by 1 + 0.1 eps1/eps_c0, eps1 = n_bars w_cr / b, w_cr = 2 pi (nu_rs - 1) x loss of bar radius, nu_rs = 2 (Coronelli & Gambarova, 2004) |

The upper level is 15% because the ductility relation reaches zero at 20% and Du et al. tested up to about 16%. Loss of bond, pitting and stirrup corrosion are not represented, so the reductions below are those of section loss and steel and cover degradation alone. The stage loads are the same absolute loads as for the uncorroded beam. A stage the corroded beam cannot carry is recorded as unreached with the largest load reached in the attempt and its load-deflection curve; when the reason is that the deflection passed span/100 first, that load is the corroded beam's peak load. At zero mass loss the corroded model reproduces the main model (diagnostic deflection within 0.004%, peak load within 0.01%, frequency within 0.5%; `code/verify_conditions.py`).

| Mass loss | 5% | 10% | 15% |
|---|---|---|---|
| Diagnostic stiffness before overload, relative to the uncorroded beam (median) | 0.91 | 0.86 | 0.82 |
| Vibration (breathing) stiffness before overload, relative to the uncorroded beam (median) | 0.96 | 0.93 | 0.91 |
| Peak load / uncorroded peak load, median (5th to 95th percentile) | 0.92 (0.90 to 0.93) | 0.84 (0.82 to 0.87) | 0.78 (0.75 to 0.82) |
| Beams reaching the last stage load | 38% | 24% | 22% |

The peak-load ratios are from runs whose peak was determined for both the corroded and the uncorroded beam (push complete, or deflection limit reached before a stage load): about 1,130 of each level. `tables/corrosion_runs.csv` has one row per beam and level, `tables/corrosion_stages.csv` the stage records (same columns as `stages.csv`, with stiffness and vibration also relative to the uncorroded beam), and `tables/corrosion_envelopes.csv` the curves. 55 records failed before the third stage (nonconvergence, almost all uniformly loaded) and are kept with `run_ok` false.

### Sustained load

For beams 0 to 999 (`raw_sustained/`, `code/sustained.py`), the concrete is replaced by OpenSees' time-dependent TDConcrete (Knaack & Kurama, 2018: linear in compression, tension softening, creep and shrinkage with the ACI 209R-92 time functions), with displacement-based elements, which this material requires. Creep and shrinkage magnitudes follow IS 456:2000: creep coefficient 1.6 for loading at 28 days and shrinkage strain 0.0003. The analysis starts when the formwork is removed at 7 days, when drying also begins. Two cases (2,000 records, none failed):

- **service**: the service load (0.37 times the hand yield load) is applied at 28 days and held for 50 years;
- **overload**: the beam is first loaded to the third damage stage (0.80 times the hand yield load) and unloaded at 28 days, then carries the service load for 50 years.

Under the sustained load, at 0, 1, 10 and 50 years, `tables/sustained_history.csv` gives the deflection, steel stress and strain, curvature, neutral axis, IS 456 Annex F crack width, the deflection increment under an added short-term diagnostic load, and the first three frequencies of the loaded beam. `tables/sustained_runs.csv` gives the shrinkage deflection before loading, the response after removing the load at 50 years, the long-term deflection multiplier and, for the service case, the IS 456:2000 Annex C estimate of the long-term deflection (short-term deflection with the effective moment of inertia, creep with the effective modulus, shrinkage curvature).

| | Service | Overload |
|---|---|---|
| 50-year deflection / deflection just after loading, median (5th to 95th percentile) | 2.69 (2.02 to 3.58) | 1.53 (1.46 to 1.68) |
| Crack width under the sustained load, median: at loading, after 50 years | 0.02 mm, 0.09 mm | 0.09 mm, 0.11 mm |
| Steel stress under the sustained load, median: at loading, after 50 years | 32 MPa, 102 MPa | 117 MPa, 124 MPa |
| First-frequency stiffness of the unloaded beam after 50 years / at 28 days, median | 0.51 | 0.42 |

The 50-year deflection of the service case is a median 0.90 of the IS 456 Annex C estimate (5th to 95th percentile 0.69 to 1.01), an independent check of the time-dependent model against the code method with the same creep coefficient and shrinkage strain. The frequencies in this stage are those of the beam with cracks open (the breathing-crack correction of the main population is not applied). TDConcrete is linear in compression; in the overload case the concrete stress at the overload exceeds the range in which linear creep is a good approximation, so that case should be used with care.

### Repeated loading (fatigue estimate)

The fibre model has no fatigue degradation: repeated cycles to the same load shake down after the first cycle (checked over 10 cycles at two stage loads on three beams), so simulating repeated cycles would add no information. Instead, `tables/fatigue.csv` gives, for every reached stage of the main population and of the corroded beams, the fatigue life of the tension steel under repeated loading from zero to the service load, from the stress range computed by the model and the Eurocode 2 S-N curve for straight bars (EN 1992-1-1 Table 6.3N: 162.5 MPa at 10^6 cycles, slopes 5 and 9; design life with a partial factor of 1.15, and characteristic life). This is a code estimate on simulated stresses, not a fatigue simulation; it does not include the lower fatigue strength of pitted bars.

| Stage | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Median design fatigue life, cycles | 4 x 10^10 | 1.1 x 10^8 | 2.8 x 10^6 | 1.1 x 10^6 | 0.9 x 10^6 |
| Beams with a design life below 2 x 10^6 cycles | 0.3% | 13% | 45% | 61% | 70% |

### Failed runs and quality flags

Nothing is removed. 66 of the 10,000 beams (63 of them uniformly loaded) and 10 of the 1,000 retrofit beams (40 records, since the four cases share the damage history in which they failed) stopped before the third damage stage; they are kept with `run_ok` false. A retry with the same settings reproduced every failure, as expected of a deterministic solver. In 2,069 further beams the solver could not reach a later stage load (mostly the last), and 67% of the uniformly loaded pushes stop before span/100; `stages_reached`, `reached` and `push_complete` record this.

In 95 main pushes and 110 retrofit pushes the solver's last accepted step is spurious: the load jumps far above the trend of the curve (in a few cases by orders of magnitude) while the deflection advances by one normal step. `code/quality.py` detects such a step as the first curve point whose tangent stiffness exceeds twice the largest tangent stiffness of all earlier points, marks it and any later points `valid` false, sets `push_diverged`, and reports `Pmax_kN` as the peak of the valid points (the solver's value is kept as `Pmax_raw_kN`). After this, peak loads lie between 0.96 and 1.78 times the hand yield load. Summary numbers are in `tables/quality_summary.json`.

In 137 of the 47,510 reached damage-stage records (130 beams) the open-crack first frequency is higher, by 0.1 to 6%, than at the previous stage although the static stiffness has fallen (`frequency_rise`). The frequency is computed from the tangent stiffness of the unloaded beam, which depends on where the concrete fibres lie on their unloading branch after each cycle; these records are a model artefact and are flagged rather than corrected. No frequency exceeds the undamaged frequency of its beam by more than 0.07%.

### Benchmarks

`code/benchmarks.py` defines two tasks on `tables/` and reports baselines in `tables/benchmark_results.json`:

- **Task A, stiffness left from measurements** (regression): target is the static stiffness left at each stage; inputs are the beam design and the measured frequency, service crack width, residual deflection and temperature. A1 assumes the undamaged frequency of the same beam is known (monitoring); A2 does not (assessment, using a hand estimate of the undamaged frequency).
- **Task B, has the tension steel yielded?** (classification) from the same measurements.

Two splits by beam (`tables/splits.csv`): random 70/15/15, and extrapolation (train on spans up to 4.5 m and depths up to 450 mm, test on larger beams).

### Computation

All simulations use OpenSeesPy 3.8.0.0 with Python 3, NumPy, SciPy and pandas. The runs were made on a desktop computer and on rented cloud CPU servers; every server first ran the verification scripts (`code/verify.py`, `code/verify_conditions.py`) and had to reproduce the reference results before producing data. The model code and the design table were frozen by SHA-256 hash for the whole production run. Typical run times per record: main population 30 s (median), retrofit 60 s, corrosion 27 s, sustained load 53 s, continuum 19 min.

## Validation against published tests (folder 03)

| Test programme | What is reproduced |
|---|---|
| Musiał, Trapko and Grosel (2021), *Materials* 14, 910 | Blind: free-free frequency 85.5 vs 88.4 Hz, peak load 55.7 vs 57.4 kN, static stiffness left at 45 kN 55% vs 54%; strengthened capacities; static and vibration stiffness at every load step |
| Ozturkoglu, Yucel, Karademir and Durmazgezer (2024), *Applied Sciences* 14, 9920 | Static and vibration stiffness under progressive damage; strengthened capacities after yield |
| Pešić, Živanović, Dennis and Hargreaves (2015), *Engineering Structures* 103, 15–27 | Static and vibration stiffness under incremental loading; vibration bias by series |

Folder 03 holds only values digitised by the authors of this dataset and parameters read from the papers, each cited to its source; no publisher material is included.

## Known limitations

- Simulated data. Only the reference specimen design is validated against tests; elsewhere in the design space the model is checked against an independent continuum model, not against tests.
- Flexure only: no shear failure or bond slip (see the continuum cross-check).
- Creep and shrinkage only in the sustained-load stage; corrosion only through the section and material changes listed (no bond loss or pitting); repeated loading only through the Eurocode 2 fatigue estimate.
- The hand first-yield load underestimates the fibre model's yield in most beams, so the tension steel has yielded in 14% of beams at the last stage (1% at the fourth).
- Crack widths are IS 456:2000 Annex F estimates from computed strains.
- The breathing-crack frequency is a physical approximation validated on one test programme.
- Dead load is not modelled; strengthening is installed on the unloaded beam.

## Reproducing

Python 3 with `openseespy`, `numpy`, `scipy`, `pandas` and `scikit-learn`. In `06_design_space_population/code`: `python3 design.py 10000 ../data/design.csv`, `python3 verify.py`, `python3 run_parallel.py 0 10000`, `python3 run_jobs.py retrofit`, `python3 run_jobs.py continuum`, `python3 process.py`, `python3 process_followon.py`, `python3 quality.py`, `python3 benchmarks.py`; condition stages: `python3 verify_conditions.py`, `python3 run_jobs2.py corrosion`, `python3 run_jobs2.py sustained`, `python3 process_conditions.py`. Folders 01 and 02 have their own scripts.

## References

Musiał, M., Trapko, T., & Grosel, J. (2021). Static and dynamic stiffness of reinforced concrete beams strengthened with externally bonded CFRP strips. *Materials, 14*(4), 910. https://doi.org/10.3390/ma14040910

Ozturkoglu, O., Yucel, U., Karademir, C., & Durmazgezer, E. (2024). An experimental study on the effect of GFRP and CFRP strengthening on the static and dynamic behavior of R/C beams under progressive damage. *Applied Sciences, 14*(21), 9920. https://doi.org/10.3390/app14219920

Pešić, N., Živanović, S., Dennis, J., & Hargreaves, J. (2015). Experimental and finite element dynamic analysis of incrementally loaded reinforced concrete structures. *Engineering Structures, 103*, 15–27. https://doi.org/10.1016/j.engstruct.2015.07.037

Bureau of Indian Standards. (2000). *IS 456:2000 Plain and reinforced concrete: Code of practice* (4th rev.).

American Concrete Institute. (1992). *Prediction of creep, shrinkage, and temperature effects in concrete structures* (ACI 209R-92).

Coronelli, D., & Gambarova, P. (2004). Structural assessment of corroded reinforced concrete beams: Modeling guidelines. *Journal of Structural Engineering, 130*(8), 1214–1224. https://doi.org/10.1061/(ASCE)0733-9445(2004)130:8(1214)

Du, Y. G., Clark, L. A., & Chan, A. H. C. (2005a). Residual capacity of corroded reinforcing bars. *Magazine of Concrete Research, 57*(3), 135–147.

Du, Y. G., Clark, L. A., & Chan, A. H. C. (2005b). Effect of corrosion on ductility of reinforcing bars. *Magazine of Concrete Research, 57*(7), 407–419.

European Committee for Standardization. (2004). *EN 1992-1-1:2004 Eurocode 2: Design of concrete structures, Part 1-1: General rules and rules for buildings*.

Knaack, A. M., & Kurama, Y. C. (2018). Modeling time-dependent deformations: Application for reinforced concrete beams with recycled concrete aggregates. *ACI Structural Journal, 115*(1), 175–190. https://doi.org/10.14359/51701153

American Concrete Institute. (2023). *Design and construction of externally bonded fiber-reinforced polymer (FRP) systems for strengthening concrete structures: Guide* (ACI PRC-440.2-23).
