# Rerun of Monte Carlo beam 56

**What failed.** In the original runs (`mc.py`, seed 1000 + 56), beam 56 stopped with "nonconvergence" during the 65 kN damage stage, at 41 kN. Its random inputs sit at the edge of the sample:

- concrete stiffness E<sub>c</sub> = 40,725 MPa, higher than any of the 299 beams that converged (maximum 40,417 MPa);
- tensile strength 3.23 MPa.

Together these give a steep tension-softening law.

**What was changed.** Only the solver; the model and the inputs are the same (`rerun56.py`):

- force-based element internal iterations raised from 10 to 200;
- deeper sub-stepping, to 1/1000 of the 0.02 mm displacement step.

**Check that the change does not alter results.** Three beams that converged originally (0, 57 and 210) were rerun with the same solver settings. They gave identical results to every printed digit: stiffness left at 72 kN, first frequency and peak load (`check_beam*.json`).

**Beam 56 result:**

- first frequency 62.7 Hz;
- stiffness left after 72 kN: 17.7%, lowest of all 300 (lowest of the 299 was 19.2%);
- peak load 80.0 kN.

**Effect of including it (300 beams against 299):**

| Quantity | 299 beams | 300 beams |
|---|---|---|
| Stiffness left after 72 kN, 5th / median / 95th percentile | 23.0 / 39.4 / 65.8% | 22.9 / 39.4 / 65.8% |
| Sobol total share of tensile strength scatter | 66% | 67% |
| Other Sobol total shares: E<sub>c</sub> scatter / softening / f<sub>ck</sub> / f<sub>y</sub> | 19 / 11 / 7 / 0% | 19 / 11 / 7 / 0% |
| Surrogate R², training / five-fold cross-validated | 0.968 / 0.962 | 0.968 / 0.951 |

**Twin statistics.** These also shift by Monte Carlo noise. The random vibration-bias draw (κ) is drawn beam by beam in sequence, so adding a beam re-draws κ for every beam after it.

- Twin median error at 72 kN: 0.6% → 0.7%.
- Coverage of the 90% interval: 89–92% → 81–93% (the 81% is at the 35 kN stage).

The full recomputed summary is `mc2_summary_300beams.json`. Since 14 October 2026 the deck (version 27 onwards), both workbooks, the notebook and the retrofit simulation use all 300 beams.
