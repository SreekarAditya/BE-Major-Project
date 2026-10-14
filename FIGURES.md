# Figure index

Every figure in this folder, with what it shows. All charts carry a legend; digitisation checks carry a legend band and their source.

Resolution: every chart and drawing made by our scripts is saved at 650 dpi (04_figures, 07, 08 and 08b, the deck and the notebook). Two kinds of image are records rather than drawings and keep their original resolution: the STAAD.Pro screenshots in 05_staad (screen captures) and the digitisation checks on published figures (fig22_overlay, figure4_overlay, figure7_overlay, fig22_source_600dpi), whose pixel positions are the measurements; re-sampling them would change the record.

## 04_figures (review figures)

| File | What it shows |
|---|---|
| `01_specimen.png` | Test beam elevation and cross-section, four-point bending, sensor positions (accelerometer at quarter span, deflection sensor at midspan, tapper); dimensions in mm |
| `02_strengthening_capacity.png` | Total jack load capacity, unstrengthened and with polymer laminates, steel plate and concrete jacket: design capacity (grey) and expected capacity with mean strengths (maroon) |
| `03_stiffness_loss_with_damage.png` | One beam with nominal properties: stiffness remaining after each damage stage, from the 15 kN deflection check and from frequency (simulation; real vibration over-reads stiffness, see 09 and 12) |
| `04_twin_prediction.png` | Same beam: error of the 30 kN deflection prediction for no updating, vibration only, static only and the combined twin |
| `09_stiffness_deflection_vs_vibration.png` | 300 simulated beams: median and 90% band of stiffness remaining, from deflection and as a vibration reading would show it |
| `10_sobol_sensitivity.png` | Sobol sensitivity of stiffness left after 72 kN: share of variance from each input alone (first order) and with interactions (total effect) |
| `11_twin_accuracy_calibrated.png` | Error of the 30 kN prediction on 150 test beams by method and damage stage: bar = median, whisker = 95th percentile, logarithmic scale |
| `12_validation_both_test_beams.png` | Musiał et al. (2021): stiffness remaining measured on two beams (markers with reading uncertainty) against the blind model prediction (lines) |
| `13_continuum_stress_and_cracks_76kN.png` | Second, independent OpenSeesPy model (plane-stress continuum, bars as truss elements) at 76 kN: longitudinal stress (compression blue, tension red, colour bar in MPa) and the crack pattern, flexural cracks concentrated between the load points |
| `14_model_with_reinforcement_cage.png` | Three-dimensional view of the modelled beam: 3 bars of 12 mm (bottom), 2 bars of 10 mm (top), 8 mm stirrups at 150 mm, loads P/2 at the third points |
| `15_continuum_first_mode.png` | First vibration mode of the undamaged beam from the continuum model: 49.6 Hz against 50.0 Hz by beam theory |

## 07_uncertainty_and_validation

| File | What it shows |
|---|---|
| `mc2_stiffness.png`, `mc2_sobol.png`, `mc2_twin.png` | Same charts as 09, 10 and 11, written by `mc_stats2.py` |
| `published_test/fig22_overlay.png` | Digitisation check on Musiał et al. (2021) Figure 22 (CC BY 4.0): coloured circles are the points read by `digitise.py`, legend under the image |
| `published_test/fig22_source_600dpi.png` | The published Figure 22 rendered at 600 dpi (CC BY 4.0); input to `digitise.py` |
| `published_test/val_musial2.png` | Same chart as 12, written by `val_fig2.py` |

## 08_benchmark_ozturkoglu2024

| File | What it shows |
|---|---|
| `01_capacity_predicted_vs_test.png` | Predicted against published peak load of the polymer-strengthened beams, with the equal-value line and the material-basis sensitivity |
| `02_static_vs_vibration.png` | Stiffness ratio by damage level for each beam: static secant against vibration modes 1 and 2; kappa = 0.348 |
| `03_retrofit_vertical_signal.png` | Frequency change after bonding for the two beams strengthened after damage, vertical modes 1 to 3 |
| `figure4_overlay.png`, `figure7_overlay.png` | Digitisation checks on the published load–displacement Figures 4 and 7 (CC BY 4.0): D1 to D4 points read at each damage level, legend under the image |

## 08b_benchmark_pesic2015

| File | What it shows |
|---|---|
| `01_static_vs_vibration.png` | Beam 3: vibration stiffness ratio against static stiffness ratio by load step, conditional fit kappa = 0.180 |
| `02_kappa_by_series.png` | Kappa for each published series with its interval where one can be estimated |
| `fig11_experimental_path.png` | Beam 3 load path digitised from the published Figure 11 with the eleven peak picks; the source figure itself is not reproduced (publisher copyright) |

## 09_retrofit_simulation

| File | What it shows |
|---|---|
| `retrofit_decision_map.png` | Fig. 5 of the deck: least intrusive compliant scheme for each of 10,000 simulated beams; horizontal axis moment demand / capacity before retrofit, vertical axis crack width / IS 456 limit, dashed lines at 1; legend gives the scheme and its count |
| `retrofit_success_rate.png` | Fig. 6 of the deck: share of beams in which each scheme complies with IS 456, against the strength increase needed; beams per bin printed under the axis; legend gives the scheme |

## Presentation and notebook

- Deck (version 34): Fig. 1 specimen, Fig. 2 stiffness left, Fig. 3 Sobol sensitivity, Fig. 4 twin error, Fig. 5 retrofit decision map, Fig. 6 scheme compliance; each captioned on its slide.
- `StrucIQ_review_notebook.html`: Figures 1 to 6, each with a title, legend and numbered caption.
