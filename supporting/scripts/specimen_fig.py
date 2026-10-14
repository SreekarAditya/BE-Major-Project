"""Dimensioned specimen drawing for the deck: elevation (left) and cross-section (right), large text."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, Polygon, Circle
for f in fm.findSystemFonts():
    if 'Carlito' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family': 'Carlito', 'font.size': 17})
INK, MUTED, ACC, CON = '#1A1A1A', '#6B6B6B', '#8E1B2E', '#EDEDED'

fig = plt.figure(figsize=(12.1, 4.3))
# ---------------- elevation (scale 1 mm = 1 unit)
a = fig.add_axes([0.0, 0.0, 0.72, 1.0]); a.set_aspect(1); a.axis('off')
L, H = 3200, 300
a.add_patch(Rectangle((0, 0), L, H, fc=CON, ec=INK, lw=1.4))
a.plot([30, L - 30], [39, 39], color=ACC, lw=2.4)            # bottom bars
a.plot([30, L - 30], [262, 262], color=ACC, lw=1.6)          # top bars
for x in range(25, 3176, 150): a.plot([x, x], [29, 271], color='#A6A6A6', lw=0.7)  # 22 stirrups: (3200 - 2 x 25) / 150 + 1, first and last at end cover
for xs in (100, 3100):                                        # supports
    a.add_patch(Polygon([[xs, 0], [xs - 70, -110], [xs + 70, -110]], closed=True, fc=INK))
a.add_patch(Rectangle((1000, H + 25), 1200, 45, fc='#BDBDBD', ec=INK, lw=1))   # spreader beam
for xp in (1100, 2100): a.plot([xp, xp], [H, H + 25], color=INK, lw=2)
a.annotate('', xy=(1600, H + 75), xytext=(1600, H + 330), arrowprops=dict(arrowstyle='-|>', lw=2.2, color=INK, mutation_scale=22))
a.text(1650, H + 250, 'Load P (jack)', va='center', fontsize=17)
a.text(1100, H + 120, 'P/2', ha='center', fontsize=16, color=MUTED); a.text(2100, H + 120, 'P/2', ha='center', fontsize=16, color=MUTED)
# sensors
a.add_patch(Rectangle((850 - 45, H), 90, 30, fc='#4A6C8C', ec='none')); a.text(760, H + 160, 'Accelerometer', ha='center', fontsize=15, color='#4A6C8C')   # quarter span: 100 + 3000/4
a.plot([1600], [-25], marker='v', ms=13, color=ACC); a.text(1600, -120, 'Deflection sensor', ha='center', va='top', fontsize=15, color=ACC)
a.plot([2600], [H + 20], marker='s', ms=10, color='#B07A1E'); a.text(2600, H + 160, 'Tapper', ha='center', fontsize=15, color='#B07A1E')
# dimension chain
yd = -400
for x0, x1, t in ((0, 100, '100'), (100, 1100, '1000'), (1100, 2100, '1000'), (2100, 3100, '1000'), (3100, 3200, '100')):
    a.annotate('', xy=(x0, yd), xytext=(x1, yd), arrowprops=dict(arrowstyle='<->', lw=1.1, color=INK))
    if t != '100': a.text((x0 + x1) / 2, yd + 25, t, ha='center', va='bottom', fontsize=16)
for x in (0, 100, 1100, 2100, 3100, 3200): a.plot([x, x], [yd - 30, -135 if x in (100, 3100) else -20], color=MUTED, lw=0.7)   # extension lines stop short of the object
yd2 = -540
a.annotate('', xy=(100, yd2), xytext=(3100, yd2), arrowprops=dict(arrowstyle='<->', lw=1.1, color=INK))
a.text(1600, yd2 - 30, 'Span 3000 mm   (overall 3200 mm)', ha='center', va='top', fontsize=17)
a.set_xlim(-60, 3260); a.set_ylim(-700, H + 360)
# ---------------- cross-section (scale 1 mm = 1 unit)
s = fig.add_axes([0.73, 0.06, 0.27, 0.88]); s.set_aspect(1); s.axis('off')
b = 230
s.add_patch(Rectangle((0, 0), b, H, fc=CON, ec=INK, lw=1.4))
s.add_patch(Rectangle((29, 29), b - 58, H - 58, fc='none', ec='#7A7A7A', lw=1.6))   # stirrup
for x in (39, 115, 191): s.add_patch(Circle((x, 39), 6, fc=ACC))
for x in (38, 192): s.add_patch(Circle((x, 262), 5, fc=ACC))
s.annotate('', xy=(0, -45), xytext=(b, -45), arrowprops=dict(arrowstyle='<->', lw=1.1, color=INK)); s.text(b / 2, -60, '230', ha='center', va='top', fontsize=16)
s.annotate('', xy=(-45, 0), xytext=(-45, H), arrowprops=dict(arrowstyle='<->', lw=1.1, color=INK)); s.text(-60, H / 2, '300', ha='right', va='center', fontsize=16, rotation=90)
s.text(b + 25, 262, '2 bars 10 mm', va='center', fontsize=15)
s.text(b + 25, 150, '8 mm stirrups\nat 150 mm', va='center', fontsize=15)
s.text(b + 25, 39, '3 bars 12 mm', va='center', fontsize=15)
s.text(b / 2, H + 30, 'Section (mm)', ha='center', va='bottom', fontsize=16, color=MUTED)
s.set_xlim(-130, 470); s.set_ylim(-140, H + 90)
fig.savefig('../ppt/c_specimen.png', dpi=650, facecolor='white')
print('ok')
