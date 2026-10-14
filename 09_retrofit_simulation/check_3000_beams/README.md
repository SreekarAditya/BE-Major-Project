# Check: the same retrofit simulation with 3000 beams

Earlier main run (until 14 October 2026, deck versions 22 to 31). Same code with N = 3000 (`retrofit_sim.py`), same tree settings. Run from this folder: `python3 retrofit_sim.py`, then `python3 retrofit_tree.py`.

| | 3000 beams (this folder) | 10,000 beams (main folder) |
|---|---|---|
| Monitor / seal cracks / polymer / plate / jacket | 33 / 15 / 48 / 4.1 / 0.1% | 32 / 15 / 49 / 4.3 / 0.2% |
| Polymer complies, 0–30% more strength needed | 97–100% | 97–100% |
| Polymer complies, 30–40% / 40–50% / 50–60% | 86 / 70 / 65% | 85 / 69 / 58% |
| Tree accuracy on unseen beams | 89.6% (900 beams) | 90.1% (3000 beams) |
| Plate or jacket beams caught | 34 of 38 | 115 of 135 |

The tree's main splits are the same. With 3000 beams it also split on the twin's stiffness left (0.30); with 10,000 that split disappears, so it is not a finding.
