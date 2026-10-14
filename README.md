# StrucIQ: digital twin for live condition monitoring and retrofit decision support of reinforced concrete members

BE major project, Department of Civil Engineering, Chaitanya Bharathi Institute of Technology. Batch 120ABR. Material for Review 2 (14 October 2026).

**Aim.** To develop and experimentally validate a digital twin that measures damage in reinforced concrete beams and recommends retrofitting.

**Objectives.**

1. To design and instrument under-reinforced beams to IS 456:2000 for staged four-point load tests with automated sensing.
2. To develop a digital twin that fuses static and vibration data by Bayesian updating to estimate flexural stiffness and predict service deflection.
3. To develop a retrofit decision framework from IS 456 checks on simulated beams.
4. To validate the twin's predictions and the recommended strengthening by service-load and failure tests.

**Beam.** 230 × 300 mm, 3000 mm span (3200 mm long), M30 concrete, Fe500 bars (3 of 12 mm bottom, 2 of 10 mm top), Fe415 stirrups of 8 mm at 150 mm (22 stirrups), four-point bending with loads at the third points.

## Folders

| Folder or file | Contents |
|---|---|
| `presentation/` | Review 2 deck, version 34 (PowerPoint and PDF) |
| `abstract/` | Review 2 abstract (PDF) |
| `REVIEW_GUIDE.md` | What to open for each question from the panel, the hypotheses and the key numbers |
| `FIGURES.md` | One-line description of every figure |
| `StrucIQ_results.xlsx` | Main workbook: IS 456 design, model verification, damage stages, twin, strengthening, hypotheses |
| `StrucIQ_review_notebook.ipynb`, `.html` | The four steps (design, model check, damage stages, twin update) with outputs and charts |
| `01_design_calculation/` | IS 456 beam design, every step with its formula and clause |
| `02_model/` | OpenSeesPy fibre beam model and a quick check |
| `03_damage_and_twin/` | The twin: static stiffness, vibration stiffness, learned bias, Bayesian combination, prediction with 90% range |
| `04_figures/` | Review figures at 650 dpi |
| `05_staad/` | STAAD.Pro input files, results and screenshots (gross section and with bars) |
| `06_ansys_draft/` | ANSYS Mechanical input files (draft, not yet run) |
| `07_uncertainty_and_validation/` | Monte Carlo of 300 beams, Sobol sensitivity, twin statistics, blind prediction of a published test; workbook `StrucIQ_MonteCarlo_data.xlsx` |
| `08_benchmark_ozturkoglu2024/` | Second published test series: strengthening capacity, vibration bias, twin step |
| `08b_benchmark_pesic2015/` | Third published series (static data for one beam only; not used in the deck) |
| `09_retrofit_simulation/` | 10,000 simulated beams checked to IS 456 before and after polymer laminates, steel plate and concrete jacket; decision tree; workbook `StrucIQ_decision_tree_beams.xlsx` |
| `supporting/` | Earlier hand calculations, scripts and figures from the 230 × 300 mm study |

## Running the code

Python 3 with NumPy, SciPy, pandas and Matplotlib. The model needs OpenSeesPy (`python3 -m pip install openseespy`) and the decision tree needs scikit-learn (`python3 -m pip install scikit-learn`). Each folder's README gives the command and running time.

## Published data used

Musiał, Trapko and Grosel (2021), *Materials*, 14, 910, and Ozturkoglu et al. (2024), *Applied Sciences*, 14, 9920, both published under the Creative Commons Attribution 4.0 licence; figures read from them are marked as such. The publisher's copy of Pešić et al. (2015) is not included.
