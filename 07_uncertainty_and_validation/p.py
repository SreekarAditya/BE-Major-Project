# Single source of parameters for the 230 x 300 mm simulation set (units: N, mm, MPa)
import numpy as np
b, h = 230.0, 300.0
span = 3000.0; overhang = 100.0; Ltot = span + 2*overhang
a = span/3.0                      # shear span (third-point loading)
cover = 25.0; dst = 8.0
fck = 30.0; Ec = 5000*np.sqrt(fck); ft = 0.7*np.sqrt(fck); nu = 0.2; rho = 2.5e-9  # tonne/mm3
fy = 500.0; Es = 2e5; fy_st = 415.0
bot = dict(n=3, d=12.0); top = dict(n=2, d=10.0)
y_bot = cover + dst + bot['d']/2          # 39 mm from soffit
y_top = h - cover - dst - top['d']/2      # 262 mm from soffit
d_eff = h - y_bot                          # 261 mm
A_bot = bot['n']*np.pi*bot['d']**2/4; A_top = top['n']*np.pi*top['d']**2/4
s_st = 150.0; A_sv = 2*np.pi*dst**2/4
# repairs (standard sizes)
frp = dict(name='Carbon laminate strips', n=2, w=50.0, t=1.2, E=165000.0)   # 2 x CarboDur-type S512 (50 x 1.2)
plate = dict(name='Bonded steel plate', w=100.0, t=5.0, fy=250.0)          # standard flat 100 x 5
jacket = dict(name='Concrete jacket', t=75.0, n=2, d=12.0)                  # 75 mm on 3 sides, 2 bars of 12 mm
