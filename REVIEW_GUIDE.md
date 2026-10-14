# What to open when the panel asks

| They ask | Open | What it shows |
|---|---|---|
| "Show your calculations / code" | `01_design_calculation/is456_beam_design.py` | IS 456 design, every step with its formula and clause. Runs in under a second: `python3 is456_beam_design.py` |
| "Show it running" | `StrucIQ_review_notebook.html` (any browser) or `StrucIQ_review_notebook.ipynb` (Jupyter) | All four steps with outputs and charts already shown: design, model check, damage stages, twin update |
| "Show your data" | `StrucIQ_results.xlsx` | Sheets: IS 456 design, model verification, mesh study, damage stages, twin prediction, strengthening |
| "How did you model it?" / "Open OpenSeesPy" | `02_model/fibre_model.py`, `02_model/quick_check.py` | OpenSeesPy fibre beam model. For a live run use `python3 quick_check.py` (a few seconds: builds the same model, prints 52.1 Hz and 0.470 mm against hand 51.9 Hz and 0.472 mm). The full study `fibre_model.py` takes a few minutes; its output is `fibre_verified.json`. OpenSeesPy is free: `python3 -m pip install openseespy` |
| "How does the twin work?" / "Open the twin" | `03_damage_and_twin/twin.py` | The five steps as five functions (static stiffness, vibration stiffness, learned bias, Bayesian combination, prediction with 90% range), run stage by stage. Runs in under a second: `python3 twin.py` |
| "Show images" | `04_figures/` | Specimen drawing, strengthening capacities, stiffness loss, twin prediction |
| "Did you check in software?" | `05_staad/STAAD_RESULTS.md`, screenshots in `05_staad/run_gross_section` and `05_staad/run_with_bars` | Two STAAD.Pro runs, 0 errors. Gross section: reactions and moments exact, deflection −0.2%, frequency −0.7%, steel +0.1%. With bars: deflection 0.483 mm (0.0%), frequency 50.71 Hz (−0.5%). Hand, OpenSeesPy and STAAD agree section for section |
| "ANSYS?" | `06_ansys_draft/` | Input files written, not yet run (planned after the review) |
| "How sure are you? Uncertainty?" | workbook sheets *Monte Carlo stiffness* and *Twin statistics*; `07_uncertainty_and_validation/mc2_summary.json` | 300 simulated beams; uncertainties calibrated on half, tested on the other half; significance tests |
| "Which input matters most?" | workbook sheet *Sensitivity*, `04_figures/10_sobol_sensitivity.png` | Sobol indices: scatter of tensile strength explains 67% of stiffness loss |
| "How did you get R² = 0.95? Show the data" | `07_uncertainty_and_validation/StrucIQ_MonteCarlo_data.xlsx` | Every one of the 300 simulated beams (inputs and outputs). Sheet *Surrogate fit*: Excel itself fits the regression (LINEST) and computes training R² 0.968 and five-fold cross-validated R² 0.951 live. Also the Sobol shares and the 150-beam twin test with medians by formula |
| "Is the model validated against real tests?" | workbook sheets *Validation* and *Calibration study*, `04_figures/12_validation_both_test_beams.png` | Blind prediction of a published test; 15 tension laws compared |
| "Did you test the twin on real data?" | workbook sheet *Twin on test data*, `published_test/twin_on_test.py` | Bias learning on the published measurements: 30% error cut to 4% |
| "How did you get the test numbers?" | `published_test/digitise.py`, `fig22_overlay.png` | Pixel digitisation of the paper's Figure 22, checked by overlay |
| "Second published test series?" | `08_benchmark_ozturkoglu2024/REPORT.md`, workbook sheet *Second published series* | Four beams, strengthened before or after damage: polymer capacity, vibration bias, twin step, repair signal |
| "Which retrofit for which beam?" / "Is the recommendation general?" | `09_retrofit_simulation/README.md`, `09_retrofit_simulation/StrucIQ_decision_tree_beams.xlsx` | 10,000 beams designed to IS 456, damaged from our Monte Carlo, checked before and after polymer laminates, steel plate and concrete jacket (cl 38.1, 40, 23.2, Annex F). Polymer complies in 97 to 100% of beams needing up to 30% more strength; plate or jacket beyond. Decision tree: 90% correct on 3000 unseen beams (Excel workbook recomputes it). A 3000-beam run gives the same result (`check_3000_beams`). `python3 retrofit_sim.py` (about 4 minutes), then `python3 retrofit_tree.py` |
| "What does this figure show?" | `FIGURES.md` | One-line description of every figure in this folder |
| "What are your hypotheses?" | workbook sheet *Hypotheses* | H1 to H4 with evidence and status |

## Hypotheses

- **H1** Damage must be measured; it cannot be inferred from the load history. Supported: two identical published beams with the same loads kept 51% and 57% of their stiffness; simulation 23 to 66%; the model misses the stiffness path by up to 29 points.
- **H2** Vibration over-estimates the stiffness of a cracked beam. Supported by two published tests: 80% against 54% left; vibration registers only 31 to 39% of the loss.
- **H3** The twin predicts service deflection within 5%. Supported in simulation (0.7% median; 90% intervals hold in 81 to 93% of test beams) and its bias-learning step on published data (30% cut to 4%); to be confirmed on our beams.
- **H4** The recommended repair meets the target capacity. To be tested in the failure tests.

## "Do you have a dataset?"

Say it plainly: **not yet an experimental dataset**. The beams have not been cast; tests start after casting and curing (Gantt chart). The data shown is **simulated** from the verified model, and the twin is checked on it before real tests. Once testing starts, the sensors produce the dataset: load, deflection, acceleration and temperature for every beam and every stage.

## Key numbers

- Design (IS 456): d = 261 mm, Ast = 339 mm², xu = 59.4 mm < xu,max = 120 mm, Mu = 34.8 kN·m, design jack load 70 kN, cracking 26.5 kN, shear capacity 94.6 kN against 34.8 kN demand.
- Model check: frequency 52.1 Hz against 51.9 Hz by hand, deflection at 15 kN 0.47 mm against 0.47 mm, same results for 12, 24 and 48 elements.
- Damage: after the 72 kN stage, 28 % of stiffness left by deflection, 33 % by frequency.
- Twin (one beam with nominal properties, vibration seeing 35% of the loss, `twin.py`): 30 kN prediction within 0.4% at every stage with a load check after each stage; vibration alone reports 75% stiffness left after 72 kN against 28% from the static check.
- Monte Carlo (300 beams; beam 56 rerun with a more patient solver, `07_uncertainty_and_validation/rerun_beam56`): after 72 kN, 39 % of stiffness left by deflection (90 % band 23 to 66 %); the vibration reading still shows 79 %. Sobol: scatter of tensile strength 67 %, Ec scatter 19 %, tension softening 11 %, concrete strength 7 %, steel 0 % (surrogate cross-validated R² 0.95).
- Twin on 150 test beams at 72 kN, median error: no updating 60 %, vibration only 51 %, deflection only 0.7 %, twin 0.7 %. 90 % intervals hold 81 to 93 % (81 % at 35 kN, slightly below the nominal 90 %). Uncertainties were calibrated on the other 150 beams.
- Published test (Musiał, Trapko and Grosel 2021, Materials 14, 910), blind: free-free frequency 85.5 against 88.4 Hz (−3.3 %); peak load 55.7 against 57.4 kN (−3.0 %); stiffness left at 45 kN 55 % against 54 %; polymer capacities 80 and 107 against 90 and 116 kN (our method conservative by 8 to 11 %). Assumed top bars change these by under 1.5 %.
- Limitation, quantified: between 12 and 45 kN the model's stiffness path is off by 19 points on average and 29 at worst; 14 other tension laws (strength from the measured cracking load) still leave 10 to 11 points. A smeared fibre beam cannot show early discrete cracking. This is why the twin measures stiffness rather than predicting it.
- Twin logic on the published measurements: vibration without bias errs 30 %; with the bias learned at the previous check 4 %; holding the previous check 5.5 % (reading uncertainty about 3 %).
- Second published series (Ozturkoglu et al. 2024, Applied Sciences 14, 9920; four beams, glass and carbon polymer): our strengthening method predicted ultimate load within 2.6 to 3.3% for beams strengthened before damage and within 3% after damage. Vibration registered 35% of the stiffness loss (95% interval 31 to 48%), in line with Musiał (31 to 39%), and read the beam stiffer in 10 of 11 comparisons. Between load checks the learned bias gave 24% error against 27% holding the last check and 67% vibration alone; their damage steps were far beyond yield, and in both series the error grows with the damage added since the last check. After strengthening, frequency fell 9% (glass) and rose 1% (carbon): repairs are verified with a static check.
- Across both published series (six strengthened beams) the polymer method was within 11%, and the learned bias was the most accurate between-check estimate at every step (19 predictions).
- A third paper (Pešić et al. 2015) was analysed in `08b_benchmark_pesic2015/`; it publishes static data for one beam only, so it is not used in the deck.
- Superseded version-6 results are kept in the `superseded_v6` folders for the record; use the numbers above.

## Running the Python files on the Mac

`is456_beam_design.py` and `twin.py` need only Python 3. Open Terminal in the folder and type `python3 is456_beam_design.py`. The notebook needs Jupyter (included in Anaconda).
