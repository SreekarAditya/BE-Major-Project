"""Chart of the Beam 3 load path digitised from Pesic et al. (2015) Fig. 11 (isolated from the PDF vector path), with the eleven peak picks.
Replaces the earlier unlabelled pixel trace. Inputs: vector_trace_check.json, digitised_static.json."""
import json, os, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
H = os.path.dirname(os.path.abspath(__file__))
for f in fm.findSystemFonts():
    if 'Carlito' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family': 'Carlito', 'font.size': 13})
cal = json.load(open(os.path.join(H, 'digitised_static.json'))); C = cal['calibration']
(x0, x1), (v0, v1) = C['x_pixels'], C['x_values_mm']; (y0, y1), (w0, w1) = C['y_pixels'], C['y_values_kN']
tf = lambda z: ((z[0] * 600 / 72 - 331) * 1728 / 2076, (z[1] * 600 / 72 - 2352) * 1728 / 2076)   # same transform as digitise.py
X = lambda px: v0 + (px - x0) * (v1 - v0) / (x1 - x0); Y = lambda py: w0 + (py - y0) * (w1 - w0) / (y1 - y0)
pts = [tf(z) for z in json.load(open(os.path.join(H, 'vector_trace_check.json')))[0]['pts']]
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.plot([X(p[0]) for p in pts], [Y(p[1]) for p in pts], color='#4A6C8C', lw=1.8, label='Experimental load path, Beam 3 (from the PDF vector path)')
R = cal['rows']
ax.errorbar([r['peak_deflection_mm'] for r in R], [r['plotted_peak_load_kN'] for r in R], xerr=[r['deflection_reading_bound_mm'] for r in R],
            fmt='o', color='#8E1B2E', ms=6, mec='white', mew=1, elinewidth=1.2, capsize=0, label='Peak picks used, load steps 1 to 11 (bar: reading bound)')
for r in R: ax.annotate(str(r['step']), (r['peak_deflection_mm'], r['plotted_peak_load_kN']), xytext=(4, 5), textcoords='offset points', fontsize=10, color='#8E1B2E')
ax.set_xlim(0, 35); ax.set_ylim(0, 2.4); ax.grid(color='#E6E6E6'); ax.set_axisbelow(True)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.set_xlabel('Midspan deflection (mm)'); ax.set_ylabel('Applied load P (kN)')
ax.set_title('Pesic et al. (2015), Beam 3: digitised load path and peak picks', fontsize=14)
ax.legend(frameon=False, fontsize=10.5, loc='upper left')
fig.text(0.01, 0.01, 'Axis calibration from the figure ticks; values in the units of the published figure. Source figure not reproduced (publisher copyright).', fontsize=9.5, color='#6B6B6B')
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(os.path.join(H, 'fig11_experimental_path.png'), dpi=650, facecolor='white'); print('ok')
