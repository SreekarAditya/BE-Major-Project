# Design calculations: beam 230 × 300 mm, 3.0 m span

Units: kN, mm, MPa. IS 456 design values use partial safety factors; expected values use mean material strengths (no safety factors) and are what a test should show.

## Section and materials

| Item | Value |
|---|---|
| Section | 230 mm wide × 300 mm deep, 3,200 mm long, 3,000 mm span, 100 mm overhangs |
| Loading | four-point bending, loads at third points (shear span 1,000 mm) |
| Bottom bars | 3 bars of 12 mm, Fe500, area 339 mm², effective depth 261 mm, steel ratio 0.57% |
| Top bars | 2 bars of 10 mm, Fe500 |
| Stirrups | 8 mm, two legs, Fe415, at 150 mm |
| Concrete | M30: modulus 27386 MPa (5000√fck), tensile strength 3.83 MPa (0.7√fck) |
| Cover | 25 mm clear |

## Unstrengthened beam

| Quantity | Hand calculation | Fibre model |
|---|---|---|
| Cracking moment / load | 13.2 kN·m / 26.5 kN | clear stiffness loss by about 35–38 kN |
| Neutral axis depth (limit state) | 45.5 mm, limit 0.46d = 120.1 mm: under-reinforced | |
| Yield moment / load | 40.6 kN·m / 81.2 kN | about 89 kN |
| IS 456 design resistance | 34.9 kN·m / 69.8 kN | |
| Expected peak (mean strengths) | 41.1 kN·m / 82.2 kN | 90.9 kN |
| Cracked / gross moment of inertia | 0.22 | |
| First natural frequency, undamaged | 50.0 Hz (beam theory) | 49.1 Hz |
| Second natural frequency | 200 Hz | 196 Hz |
| First frequency, fully cracked bound | 23.7 Hz | |

## Shear check (IS 456)

| Item | Value |
|---|---|
| Concrete shear capacity | 31.4 kN |
| Stirrup shear capacity | 63.2 kN |
| Total design shear capacity | 94.5 kN |
| Shear at expected flexural failure | 41.1 kN: flexure governs |
| Jacketed section shear capacity | 127.4 kN against 77.0 kN at its flexural failure |

## Repairs (standard sizes)

| Scheme | Size | Design load (kN) | Expected peak (kN) | Fibre model peak (kN) | Governing failure |
|---|---|---|---|---|---|
| Fibre-reinforced polymer strips | 2 carbon laminates 50 × 1.2 mm, E = 165 GPa | 107 | 126 | 135 | strip debonding at strain 0.0045 (ACI 440.2R) |
| Bonded steel plate | standard flat 100 × 5 mm, Fe250 | 125 | 147 | 156 | plate and bars yield, concrete crushes (plate-end debonding to be checked with anchorage) |
| Concrete jacket | 75 mm on soffit and both sides, 2 bars of 12 mm | 131 | 154 | ≥ 171 (analysis stopped at 13.7 mm) | flexure |

## Load protocol for the tests and simulations

| Step | Total jack load |
|---|---|
| Diagnostic cycle | 15 kN (below cracking) |
| Damage stages | 35, 50, 65, 72 kN (all below yield) |
| Service test predicted by the twin | 30 kN (always below the highest load already applied) |

## Damage stages (fibre model)

| Highest load so far | First frequency after unloading (Hz) | Deflection at 15 kN (mm) | Deflection in the 30 kN service test (mm) |
|---|---|---|---|
| undamaged | 49.0 | 0.531 | not run (would crack the beam) |
| 35 kN | 48.9 | 0.553 | 1.094 |
| 50 kN | 43.6 | 0.681 | 1.356 |
| 65 kN | 36.0 | 1.015 | 2.036 |
| 72 kN | 33.2 | 1.266 | 2.537 |