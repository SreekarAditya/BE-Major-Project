# STAAD.Pro check: results (run 13 October 2026, 0 errors)

STAAD.Pro models the member by its outer size only (gross concrete section, no bars), as in normal design-office practice, so it is compared with the gross-section hand values. Input: `beam_230x300_check.std` (load combination 4 placed after load case 5, as STAAD requires).

| Result | STAAD.Pro | Hand | Difference |
|---|---|---|---|
| Support reactions, 70 kN jack load | 35.00 kN each | 35.0 kN | 0.0% |
| Midspan moment, 70 kN jack load | 35.00 kN·m | 35.0 kN·m | 0.0% |
| Midspan moment, self-weight | 1.94 kN·m | 1.94 kN·m | 0.0% |
| Midspan deflection, 15 kN | 0.518 mm (printed 0.0518 cm) | 0.519 mm with shear deformation (0.507 mm bending only) | −0.2% |
| First natural frequency | 48.97 Hz | 49.3 Hz with shear and rotary inertia (50.0 Hz simple beam theory) | −0.7% |
| Bottom steel for 1.5 × self-weight + 70 kN | 365.8 mm² | 365.6 mm² (IS 456, M = 37.91 kN·m, d = 265 mm) | +0.1% |

## Same section in all three tools (gross section, no bars)

| | Hand | OpenSeesPy fibre model, bars removed | STAAD.Pro |
|---|---|---|---|
| Deflection at 15 kN | 0.507 mm bending only; 0.519 mm with shear | 0.511 mm (bending only) | 0.518 mm (includes shear) |
| First frequency | 50.0 Hz; 49.3 Hz with shear and rotary inertia | 50.02 Hz (no shear) | 48.97 Hz (includes shear, lumped mass) |

## With the bars (transformed section, n = 7.3, I = 5.56 × 10⁸ mm⁴), second STAAD run `beam_230x300_transformed.std`

| | Hand | OpenSeesPy fibre model | STAAD.Pro |
|---|---|---|---|
| Deflection at 15 kN | 0.472 mm bending only; 0.483 mm with shear | 0.470 mm (bending only) | 0.483 mm (includes shear): 0.0% |
| First frequency | 51.9 Hz; 51.0 Hz with shear and rotary inertia | 52.1 Hz (no shear) | 50.71 Hz (includes shear, lumped mass): −0.5% |

Only the bending stiffness changes in this run; area, shear area, self-weight and mass are as in the gross-section run.

## Files

- `run_gross_section/`: STAAD output `beam_230x300_check.anl` and screenshots (analysis with 0 errors, member forces, reactions, node 7 displacement, frequencies, design of member 6).
- `run_with_bars/`: STAAD output `beam_230x300_transformed.anl` and screenshots (analysis with 0 errors, section properties, member forces, reactions, node 7 displacement, frequencies). Input: `beam_230x300_transformed.std`.

## Note on the steel result

339 mm² (3 bars of 12 mm) gives Mu = 34.8 kN·m. 70 kN is the jack load at which that moment is reached, self-weight not included; it is the beam's design capacity expressed as a jack load, not a load the beam was designed to carry in addition to factored self-weight. Including self-weight (1.94 kN·m unfactored), the jack load at Mu is 65.8 kN. STAAD combination 4 adds 1.5 × self-weight on top of 70 kN (37.91 kN·m) and so asks for 365.8 mm²; the hand calculation for the same moment gives 365.6 mm², so STAAD and IS 456 agree.

Warnings: each 250 mm segment has length/depth below 2.5 (STAAD designs every segment as a separate beam); grouping members 1 to 12 as one physical member removes them and does not change the results.
