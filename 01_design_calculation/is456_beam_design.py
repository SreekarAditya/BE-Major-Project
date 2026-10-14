"""
IS 456:2000 design check of the test beam: 230 x 300 mm, span 3.0 m, four-point bending.
Every quantity is printed with its formula and the IS 456 clause it comes from.
Run:  python3 is456_beam_design.py
"""
import math

# ---------------- inputs
b, h = 230.0, 300.0          # section width and depth (mm)
span, a = 3000.0, 1000.0     # simply supported span and shear span (mm), loads at third points
cover, d_stir = 25.0, 8.0    # clear cover and stirrup diameter (mm)
n_bot, d_bot = 3, 12.0       # bottom bars
n_top, d_top = 2, 10.0       # top bars
s_v = 150.0                  # stirrup spacing (mm), 2 legs
fck, fy, fy_sv = 30.0, 500.0, 415.0   # M30, Fe500 main bars, Fe415 stirrups (MPa)

rows = []
def show(name, formula, value, unit, clause):
    rows.append((name, formula, value, unit, clause))
    print(f"{name:<28}{formula:<34}{value:>12.4g} {unit:<7}{clause}")

print("FLEXURE")
d = h - cover - d_stir - d_bot / 2
show("Effective depth d", "h - cover - stirrup - bar/2", d, "mm", "26.4")
Ast = n_bot * math.pi * d_bot ** 2 / 4
show("Steel area Ast", "3 x pi x 12^2 / 4", Ast, "mm2", "-")
xu = 0.87 * fy * Ast / (0.36 * fck * b)
show("Neutral axis depth xu", "0.87 fy Ast / (0.36 fck b)", xu, "mm", "38.1")
xu_max = 0.46 * d
show("Limiting depth xu,max", "0.46 d (Fe500)", xu_max, "mm", "38.1 note")
Mu = 0.87 * fy * Ast * (d - 0.42 * xu) / 1e6
show("Moment of resistance Mu", "0.87 fy Ast (d - 0.42 xu)", Mu, "kN m", "38.1")
Mu_lim = 0.133 * fck * b * d ** 2 / 1e6
show("Limiting moment Mu,lim", "0.133 fck b d^2", Mu_lim, "kN m", "G-1.1")
P_design = 2 * Mu / (a / 1000)
show("Jack load at Mu", "2 Mu / a", P_design, "kN", "four-point bending")
print("  under-reinforced:", xu < xu_max, "\n")

print("CRACKING")
fcr = 0.7 * math.sqrt(fck)
show("Flexural tensile strength", "0.7 sqrt(fck)", fcr, "MPa", "6.2.2")
Ig = b * h ** 3 / 12
show("Gross second moment Ig", "b h^3 / 12", Ig, "mm4", "-")
Mcr = fcr * Ig / (h / 2) / 1e6
show("Cracking moment Mcr", "fcr Ig / yt", Mcr, "kN m", "Annex C-2.1")
Pcr = 2 * Mcr / (a / 1000)
show("Cracking load", "2 Mcr / a", Pcr, "kN", "-")
print()

print("SHEAR (at the design jack load)")
Vu = P_design / 2
show("Shear demand Vu", "P / 2", Vu, "kN", "-")
tau_v = Vu * 1e3 / (b * d)
show("Nominal shear stress", "Vu / (b d)", tau_v, "MPa", "40.1")
pt = 100 * Ast / (b * d)
tau_c = 0.50 + (0.59 - 0.50) * (pt - 0.50) / 0.25     # Table 19, M30: 0.50 % -> 0.50, 0.75 % -> 0.59
show("Concrete shear strength", "Table 19, M30, pt %", tau_c, "MPa", "Table 19")
Vc = tau_c * b * d / 1e3
show("Concrete shear capacity", "tau_c b d", Vc, "kN", "40.2")
Asv = 2 * math.pi * d_stir ** 2 / 4
Vus = 0.87 * fy_sv * Asv * d / s_v / 1e3
show("Stirrup shear capacity", "0.87 fy Asv d / sv", Vus, "kN", "40.4(a)")
show("Total shear capacity", "Vc + Vus", Vc + Vus, "kN", "-")
show("Max stirrup spacing", "0.75 d", 0.75 * d, "mm", "26.5.1.5")
show("Min stirrup area", "0.4 b sv / (0.87 fy)", 0.4 * b * s_v / (0.87 * fy_sv), "mm2", "26.5.1.6")
print()

print("SERVICEABILITY AND DYNAMICS")
show("Span / effective depth", "L / d  (limit 20)", span / d, "-", "23.2.1")
Ec = 5000 * math.sqrt(fck)
show("Elastic modulus Ec", "5000 sqrt(fck)", Ec, "MPa", "6.2.3.1")
EI = Ec * Ig / 1e9                                    # kN m^2
show("Flexural stiffness EI", "Ec Ig", EI, "kN m2", "-")
m = 2500 * b * h * 1e-6                               # kg/m
show("Mass per metre", "rho b h", m, "kg/m", "-")
L = span / 1000
f1 = math.pi / (2 * L ** 2) * math.sqrt(EI * 1e3 / m)
show("First natural frequency", "(pi / 2L^2) sqrt(EI / m)", f1, "Hz", "beam theory")
d15 = 23 * 15e3 * span ** 3 / (1296 * Ec * Ig)
show("Midspan deflection at 15 kN", "23 P L^3 / (1296 EI)", d15, "mm", "beam theory")

# save every step to a table that opens in Excel
import csv
with open('design_steps.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['Quantity', 'Formula', 'Value', 'Unit', 'IS 456 clause'])
    for r in rows: w.writerow([r[0], r[1], round(r[2], 4), r[3], r[4]])
print('written design_steps.csv')
