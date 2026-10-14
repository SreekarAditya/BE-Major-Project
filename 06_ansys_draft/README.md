# ANSYS input files: reinforced concrete beam, 230 × 300 mm, 3.0 m span

Mechanical APDL command files for the beam, its load history, and the three repairs. Every file is plain text and can be opened in any editor.

**Status: draft, not yet run.** These files were written without access to ANSYS. The first run is expected to need a round of fixes (see "Expected first-run issues" below).

## What each file does

| File | Purpose |
|---|---|
| `01_params.inp` | Every number: geometry, bars, materials, plates, mesh size, load protocol, repair choice, bond-slip values. **Edit only this file** when measured values arrive. |
| `02_materials.inp` | Element types and materials: concrete (SOLID65 or SOLID185 with Menetrey–Willam), Fe500 and Fe415 bars, bearing plates, steel plate, carbon laminate, bond interface. |
| `03_mesh.inp` | Half model across the width (symmetry plane z = 0), generated node by node so bars and stirrups share nodes with the concrete. Creates the repair elements when a repair is selected. |
| `04_bc_solve.inp` | Supports (pin and roller under steel plates), symmetry, and the full load history. |
| `05_modal.inp` | Natural frequencies at the end of every unloaded diagnostic cycle, using the stiffness of the beam at that moment. |
| `06_post.inp` | Load–deflection curve, service-test deflections, and PNG images (stress contours, crack pattern, bar stress, deformed shape). |
| `run_bare.inp` | Unstrengthened beam. |
| `run_jacket.inp` | Concrete jacket, 75 mm on the soffit and both sides, 2 bars of 12 mm. |
| `run_plate.inp` | Bonded steel plate, standard flat 100 × 5 mm, Fe250, with a bond interface that can debond. |
| `run_frp.inp` | Two carbon laminates 50 × 1.2 mm, E = 165 GPa, with a bond interface that can debond. |

## How to run

1. Put all files in one folder on the Windows machine.
2. Open Mechanical APDL (ANSYS Student), set the working directory to that folder.
3. File > Read Input From > `run_bare.inp`. Or, in batch from a command prompt:
   `MAPDL -b -i run_bare.inp -o run_bare.out -j bare` (the executable name depends on the installed version, for example `ANSYS2025R1`).
4. Repeat for `run_jacket.inp`, `run_plate.inp`, `run_frp.inp`.

## Model summary

- **Units:** N, mm, MPa, tonne, s.
- **Geometry:** 3,200 mm long, 3,000 mm span, 100 mm overhangs, load points at 1,100 and 2,100 mm (third points).
- **Mesh:** about 7,000 concrete elements in the half model, well inside the ANSYS Student limit of 128,000 nodes.
- **Reinforcement:**
  - **Bottom bars:** 3 of 12 mm. One sits on the symmetry plane, modelled with half its area.
  - **Top bars:** 2 of 10 mm.
  - **Stirrups:** 8 mm at 150 mm, modelled as LINK180 elements sharing nodes with the concrete.
- **Concrete:**
  - **Compression:** Hognestad curve to 0.8 × fck at a strain of 0.002.
  - **Cracking:** at the IS 456 tensile strength, 0.7√fck. Shear transfer coefficients are 0.3 for open cracks and 0.9 for closed cracks.
- **Load history** (total jack load):
  - **Baseline:** 15 kN diagnostic cycle.
  - **Each damage stage:** load to 35, 50, 65 and 72 kN, unload, run a 15 kN diagnostic cycle, then a 30 kN service cycle.
  - **Final test:** a 40 mm displacement-controlled push to failure.
- **Repairs:** created at the start but switched off (EKILL). They are switched on (EALIVE) after the damage stage set by `I_REP` (default: after 65 kN), on the unloaded, damaged beam. Then diagnostic and service cycles run, followed by the push to failure.
- **Bond of plate and laminate:**
  - **Model:** bilinear cohesive zone, with peak shear stress, slip and fracture energy from the Lu et al. (2005) bond–slip model. That gives a peak shear stress of about 6.0 MPa and an interfacial fracture energy of about 0.65 N/mm.
  - **Peak peeling stress:** taken equal to the concrete tensile strength.
  - **Calibration:** the bond values should be calibrated once test data exist.

## Outputs (one set per run, prefixed with the run name)

- `bare_load_deflection.csv`: total load and midspan deflection at every converged substep.
- `bare_service_tests.csv`: deflection increment in each 30 kN service test. These are the values the twin predicts.
- `bare_frequencies.csv`: modes 1 to 4 at the baseline and after each damage stage.
- PNG images in the working folder:
  - stress contours and the crack pattern (or plastic strain) at each damage peak;
  - bar stress;
  - deformed shape and stress near failure;
  - mode shapes.

## Checks before any result is used

The unstrengthened model must reproduce the hand calculations:

| Quantity | Hand calculation | Fibre model |
|---|---|---|
| Cracking load | 26.5 kN | clear stiffness loss by about 35–38 kN (tension softening delays it) |
| Yield load | about 81 kN | about 89 kN (strain hardening and concrete tension) |
| Expected peak (mean strengths) | 82 kN | 91 kN |
| IS 456 design resistance | 70 kN | not applicable |
| First natural frequency, undamaged | 50.0 Hz | 49.1 Hz |

If the ANSYS peak differs from these by more than about 10%, check the mesh, the concrete parameters and the support plates before using any image.

## Expected first-run issues

1. **Linear perturbation modal with SOLID65.** SOLID65 is a legacy element and may not support the restart-based modal analysis in `05_modal.inp`. If the run stops there, set `CONC = 2` in `01_params.inp`, which switches to SOLID185 with the Menetrey–Willam concrete model.
2. **Menetrey–Willam data order.** The `TB,CONCR ... MW` and softening data in `02_materials.inp` must be checked against the help pages of the installed version before using `CONC = 2`.
3. **Convergence near cracking.** SOLID65 often needs smaller substeps at first cracking. Increase the substep numbers in `04_bc_solve.inp`, or loosen `CNVTOL`.
4. **Strain-free activation of the repair.** The repair runs use `NLGEOM,ON` so the repair elements switch on in the deformed position. Check that the repair elements carry no stress immediately after activation.
5. **Cohesive interface orientation.** If the plate or laminate separates under the first load step with no damage, the INTER205 node order in `03_mesh.inp` must be reversed.

## Simplifications to state when presenting

- **Half model:** symmetric across the width.
- **Bars:** fully bonded to the concrete, with no bond-slip of the steel bars.
- **Jacket:** fully bonded to the original concrete, with no interface slip. Jacket stirrups are not modelled.
- **Plate and laminate:** represented by an equivalent strip 114 mm wide with the same cross-sectional area as the real plate or two laminates.
- **Material values:** nominal M30, Fe500 and Fe415 until measured values are available.

## Reference for the bond–slip values

Lu, X.Z., Teng, J.G., Ye, L.P. and Jiang, J.J. (2005). Bond–slip models for FRP sheets/plates bonded to concrete. *Engineering Structures*, 27(6), 920–937.
