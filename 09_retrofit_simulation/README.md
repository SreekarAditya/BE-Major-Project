# 09 Retrofit simulation: which scheme works for which beam

**Question.** For a damaged beam, which retrofit is the least intrusive one that makes it comply with IS 456 again?

## Procedure

1. **Design 10,000 beams to IS 456** (`retrofit_sim.py`, seed 2026).
   - Simply supported, uniformly loaded; span 3 to 8 m; width 230 or 300 mm; span/depth 10 to 13.
   - M20, M25 or M30; Fe500; tension steel 0.5 to 1.2%.
   - All three exposure classes (crack limits 0.3, 0.2 and 0.1 mm, IS 456 cl 35.3.2).
   - Each beam must satisfy cl 38.1, cl 40 and cl 23.2 when new; otherwise it is redrawn.
2. **Damage.** Each beam receives a damage level drawn from our Monte Carlo of 300 beams. The twin's stiffness is used at its lower 95% bound.
3. **Change of use.** Half of the beams keep their load. A quarter get 1.5 × live load and a quarter get 2.0 × live load.
4. **Check before and after each scheme:**
   - flexure (cl 38.1) and shear (cl 40);
   - deflection (cl 23.2 a and b, creep and shrinkage per Annex C);
   - crack width (Annex F).
5. **Schemes:**
   - polymer laminates: carbon strips 50 × 1.2 mm, 1 to 4 strips, 1 or 2 plies; ACI PRC-440.2-23 debonding strain and initial substrate strain; U-wraps for shear;
   - steel plate, 3 to 6 mm;
   - concrete jacket, 75 to 125 mm (IS 15988:2013).

   Every scheme is applied unpropped first, and propped only if unpropped fails. Crack sealing accompanies every scheme.
6. **Choice.** The least intrusive compliant option is chosen, in this order: monitor < seal cracks < polymer < plate < jacket.
7. **Decision tree** (`retrofit_tree.py`, scikit-learn):
   - depth 3, at least 20 beams per leaf, balanced class weights;
   - 70/30 stratified split (random_state 7).

## Results

**Least intrusive compliant scheme (all 10,000 beams):**

| Monitor | Seal cracks | Polymer laminates | Steel plate | Concrete jacket | Beyond all schemes |
|---|---|---|---|---|---|
| 3178 | 1464 | 4909 | 426 | 23 | 0 |

**How often each scheme complies, by strength increase needed (Fig. 6):**

| Strength increase needed (%) | Beams | Polymer (%) | Plate (%) | Jacket (%) |
|---|---|---|---|---|
| 0–10 | 803 | 100 | 100 | 100 |
| 10–20 | 1435 | 99 | 100 | 100 |
| 20–30 | 1044 | 97 | 100 | 100 |
| 30–40 | 947 | 85 | 100 | 100 |
| 40–50 | 623 | 69 | 99 | 100 |
| 50–60 | 174 | 58 | 91 | 100 |

**Decision tree on 3000 beams it never saw** (trained on the other 7000):

- 90.1% correct (91.0% on the training beams); balanced accuracy 91.5%.
- It catches 115 of 135 beams that need a plate or jacket.
- Its errors are mostly on the safe side: 249 polymer beams are sent to plate; 20 plate or jacket beams are sent to polymer.
- An unweighted tree scores 95.7% overall but catches only 60 of the 135 plate or jacket beams, which is why the weighted tree is used.
- Rules are in `retrofit_tree.txt`. Its splits are:
  - moment demand / capacity (1.00 and 1.34);
  - crack width / limit (1.00);
  - deflection / limit (0.96, 1.00 and 1.17);
  - span / effective depth (13.3).

**Check with 3000 beams** (`check_3000_beams/`): same scheme shares (33 / 15 / 48 / 4.1 / 0.1%), same polymer limit at about 30% extra strength, tree 89.6% correct on 900 unseen beams. The result does not depend on the number of beams. With 3000 beams the tree also split on the twin's stiffness left (0.30); with 10,000 that split disappears, so it is not a finding.

**Without a change of use**, damage that leaves the steel elastic never needed strengthening for strength. Those beams needed monitoring, crack sealing, or laminates (332 beams) for deflection. Propping was needed in 501 beams.

## Scope

- Damage before yield only.
- Simply supported, uniformly loaded beams (our four-point bending specimen is outside this population).
- These are IS 456 design checks; they do not replace an engineer's inspection.

## Files

| File | Content |
|---|---|
| `retrofit_sim.py` | Simulation; runs in about 4 minutes |
| `retrofit_sim.csv` | One row per beam: inputs, checks before retrofit, the size chosen in each scheme, and pass or fail |
| `retrofit_tree.py` | Decision tree; needs scikit-learn (`python3 -m pip install scikit-learn`) |
| `retrofit_tree.txt` | Decision tree rules |
| `StrucIQ_decision_tree_beams.xlsx` | The 7000 training beams and 3000 test beams, one row each. Excel predicts every beam with the tree's rules as formulas and computes the accuracy (2703 of 3000 test beams correct) and the confusion tables itself |
| `build_tree_xl.py` | Builds that workbook |
| `retrofit_sim_summary.json` | Counts and accuracies |
| `retrofit_figs.py` | Figures at 650 dpi |
| `retrofit_decision_map.png` | Fig. 5: best scheme per beam. Horizontal axis: moment demand / capacity before retrofit. Vertical axis: crack width / IS 456 limit. Colours: scheme (legend). |
| `retrofit_success_rate.png` | Fig. 6: share of beams where each scheme complies, against the strength increase needed. Beams per bin are printed under the axis. |
