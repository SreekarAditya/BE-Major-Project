"""Fig. 02: total jack load capacity, unstrengthened and with the three strengthening schemes (design and expected)."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'Carlito' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family': 'Carlito', 'font.size': 18, 'axes.labelsize': 18, 'xtick.labelsize': 16, 'ytick.labelsize': 16,
                     'axes.edgecolor': '#8A8A8A', 'xtick.color': '#444444', 'ytick.color': '#444444', 'axes.labelcolor': '#222222'})
INK, GRID, ACC = '#222222', '#E6E6E6', '#8E1B2E'
C = json.load(open('calc.json')); rep = C['repairs']; keys = ('Fibre-reinforced polymer strips', 'Bonded steel plate', 'Concrete jacket')
des = [C['bare']['P_design']] + [rep[k]['P_design'] for k in keys]
exp_ = [C['bare']['P_expected']] + [rep[k]['P_expected'] for k in keys]
names = ['Unstrengthened\n(IS 456)', 'Polymer\n(ACI PRC-440.2-23)', 'Steel plate\n(IS 456 cl 38.1)', 'Concrete jacket\n(IS 15988)']
fig, a = plt.subplots(figsize=(9.5, 5.2)); a.grid(axis='y', color=GRID, lw=1); a.set_axisbelow(True)
for s in ('top', 'right'): a.spines[s].set_visible(False)
x = np.arange(4); w = 0.36
b1 = a.bar(x - w / 2, des, w, color='#C9C9C9', label='Design capacity')
b2 = a.bar(x + w / 2, exp_, w, color=ACC, label='Expected capacity (no safety factors)')
for b, v in list(zip(b1, des)) + list(zip(b2, exp_)):
    a.text(b.get_x() + b.get_width() / 2, v + 2, f'{v:.0f}', ha='center', va='bottom', fontsize=16, color=INK)
a.set_xticks(x); a.set_xticklabels(names, fontsize=16); a.set_ylim(0, 175); a.set_yticks(range(0, 176, 25))
a.set_ylabel('Total jack load capacity (kN)'); a.legend(frameon=False, fontsize=16, loc='upper left')
fig.tight_layout(); fig.savefig('../hi/02_strengthening_capacity.png', facecolor='white'); plt.close(fig); print('ok', des, exp_)
