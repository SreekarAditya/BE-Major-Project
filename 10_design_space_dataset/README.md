# 10. Design-space dataset (after Review 2)

After Review 2, the fibre beam model of folder `02_model` was applied to 10,000 simply supported reinforced concrete beams covering the range found in buildings. The result is published as an open dataset:

**Pesaru, S. A. R., Patlola, S. R., & Murari, B. R. (2026). *StrucIQ Beam Damage and Retrofit Dataset* (Version 1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23769960** (data CC BY 4.0, code MIT)

The full tables and raw simulation output (about 80 MB compressed) are on Zenodo only. This folder keeps everything needed to read, check and regenerate them.

## Contents

| Path | Contents |
|---|---|
| `DATASET_README.md` | Full documentation of the dataset as published (method, every table, quality flags, failed runs, limitations) |
| `code/` | Generation, processing, quality-flag and benchmark scripts (OpenSeesPy fibre model, strengthening, corrosion, sustained load, continuum cross-check) |
| `validation/` | Checks against the published tests of Musiał et al. (2021): breathing-crack frequency and strengthened capacity |
| `data/design.csv` | Latin hypercube design of the 10,000 beams (seed 2027) |
| `data_dictionary.csv` | Definition and unit of every column in the dataset tables |
| `tables/*.json` | Summary results: quality flags, condition stages, benchmark baselines |
| `quickstart.ipynb` | Loads the Zenodo tables and reproduces the headline results and a benchmark baseline |
| `CITATION.cff`, `LICENSE-CODE.txt`, `LICENSE-DATA.txt` | Citation and licences |

## Main results

- 9,934 of the 10,000 beams completed at least three of the five damage stages; the 66 failed runs and all flagged anomalies are kept in the dataset.
- Vibration registered only a fraction of the static stiffness loss: 0.48 at the first damage stage rising to 0.62 at the last (medians).
- With one noisy instrument reading per stage, a gradient-boosting model estimated the stiffness left within 2.9 percentage points, against 19.9 for reading the vibration result directly.
- Strengthening raised the peak load by a median of 18% (laminates), 36% (steel plate) and 44% (concrete jacket).
- Corrosion of 5%, 10% and 15% steel mass loss reduced the peak load to 0.91, 0.84 and 0.78 of the uncorroded beam.
- Fifty years of sustained service load increased the deflection by a median of 2.7 times, 0.90 of the IS 456:2000 Annex C estimate.

## Running the code

Download the dataset from Zenodo and run the scripts from its folder `06_design_space_population/code`, which has the layout the scripts expect. Python 3 with `openseespy` (3.8.0.0), `numpy`, `scipy`, `pandas` and `scikit-learn`. The order of the commands is given at the end of `DATASET_README.md`; run `python3 verify.py` and `python3 verify_conditions.py` first to confirm the model reproduces the reference results on your machine.
