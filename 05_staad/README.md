# STAAD.Pro check: beam 230 × 300 mm, span 3.0 m

Open `beam_230x300_check.std` in STAAD.Pro (File > Open), then Analyze > Run Analysis. Units are metre and kilonewton.

## What STAAD should give (hand values to compare)

| Output | Where to read it | Hand value |
|---|---|---|
| Support reaction, load 2 | Support reactions | 35.0 kN each |
| Shear in the end thirds, load 2 | Member forces, member 1 | 35.0 kN |
| Midspan moment, load 2 | Member forces, members 6 and 7 at node 7 | 35.0 kN·m |
| Midspan moment, self-weight (load 1) | Same | 1.94 kN·m |
| Midspan deflection, load 3 (15 kN total) | Joint displacements, node 7 | 0.51 mm (gross section, uncracked) |
| First natural frequency, load 5 | Modal results in the output file | 50.0 Hz |
| Bottom steel required, combination 4 | Concrete design output | slightly above 339 mm² (self-weight adds about 2.9 kN·m factored) |

## If STAAD rejects a line

- **Modal case (load 5):** some versions want the mass defined through the load case type instead. In the editor, set load 5's type to Mass, or remove load 5 and add `CALCULATE RAYLEIGH FREQUENCY` after `PERFORM ANALYSIS` for load 1.
- **Concrete design parameters:** `MAXMAIN`, `MINMAIN` and `MINSEC` are bar diameters in millimetres. Remove them if your version does not accept them; the design still runs.

## Notes

- STAAD uses the gross concrete section, without the steel bars, so compare its frequency and deflection with the gross-section hand values: 50.0 Hz and 0.51 mm. The 51.9 Hz and 0.47 mm on slide 8 include the bars and are for comparison with the fibre model.
- The design combination treats the 70 kN jack load as the factored load, because 70 kN is the load at which the IS 456 design moment of resistance (34.8 kN·m) is reached.
