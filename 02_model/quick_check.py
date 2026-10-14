"""
Quick live check of the OpenSeesPy fibre beam model (runs in a few seconds).

OpenSeesPy is the free Python version of OpenSees (Open System for Earthquake Engineering Simulation,
University of California, Berkeley). Install once:   python3 -m pip install openseespy
Run:                                                   python3 quick_check.py

Builds the 230 x 300 mm beam exactly as fibre_model.py does (24 force-based fibre elements, Concrete02, Steel02),
then reports the first natural frequency and the midspan deflection at 15 kN (below cracking),
next to the hand values for the transformed section (n = Es / Ec = 7.3).
"""
import numpy as np, openseespy.opensees as ops
from p import *

fcm = 0.8 * fck; eps0 = 2 * fcm / Ec; NE = 24
ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
le = span / NE
for i in range(NE + 1): ops.node(i + 1, i * le, 0.)
ops.fix(1, 1, 1, 0); ops.fix(NE + 1, 0, 1, 0)                                   # pin and roller
ops.uniaxialMaterial('Concrete02', 1, -fcm, -eps0, -0.2 * fcm, -0.0035, 0.1, ft, 0.1 * Ec)
ops.uniaxialMaterial('Steel02', 2, fy, Es, 0.01, 18, 0.925, 0.15)
ops.section('Fiber', 1); yb = -h / 2
ops.patch('rect', 1, 60, 1, yb, -b / 2, h / 2, b / 2)                           # concrete, 60 layers
ops.layer('straight', 2, bot['n'], np.pi * bot['d'] ** 2 / 4, yb + y_bot, 0, yb + y_bot, 0)   # 3 bars of 12 mm
ops.layer('straight', 2, top['n'], np.pi * top['d'] ** 2 / 4, yb + y_top, 0, yb + y_top, 0)   # 2 bars of 10 mm
ops.geomTransf('Linear', 1); ops.beamIntegration('Lobatto', 1, 1, 5)
for i in range(NE): ops.element('forceBeamColumn', i + 1, i + 1, i + 2, 1, 1)
for i in range(NE + 1):
    mi = rho * b * h * le * (0.5 if i in (0, NE) else 1.); ops.mass(i + 1, mi, mi, 0.)
nmid = NE // 2 + 1
f1 = float(np.sqrt(min(ops.eigen('-fullGenLapack', 2))) / (2 * np.pi))

ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
for n in (NE // 3 + 1, 2 * NE // 3 + 1): ops.load(n, 0, -7500.0, 0)            # 7.5 kN at each third point
ops.constraints('Plain'); ops.numberer('RCM'); ops.system('FullGeneral')
ops.test('NormDispIncr', 1e-8, 100); ops.algorithm('Newton')
ops.integrator('LoadControl', 0.1); ops.analysis('Static'); ops.analyze(10)    # 15 kN in 10 steps
d15 = -ops.nodeDisp(nmid, 2)

print('OpenSeesPy fibre model, 24 elements')
print('  First natural frequency   %6.2f Hz    hand (transformed section): 51.86 Hz' % f1)
print('  Deflection at 15 kN       %6.3f mm    hand (transformed section): 0.472 mm' % d15)
