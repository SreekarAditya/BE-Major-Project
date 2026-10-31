import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, pandas as pd
plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 9, "axes.titlesize": 9,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 650})
ACC, GREY, DARK = "#1f5fa8", "#b5b5b5", "#555555"
import os
T = os.environ.get("STRUCIQ_TABLES", "tables/")  # folder 06_design_space_population/tables of the Zenodo dataset
s = pd.read_csv(T + "stages.csv"); s = s[s.reached & (s.stage > 0)]
fig, ax = plt.subplots(figsize=(3.1, 2.7))
sub = s.sample(6000, random_state=1)
ax.scatter(1 - sub.static_left, 1 - sub.vib_left_breathing, s=1.2, color=GREY, alpha=0.5, lw=0, rasterized=True)
med = s.groupby("stage")[["static_left", "vib_left_breathing"]].median()
ax.plot(1 - med.static_left, 1 - med.vib_left_breathing, "o-", color=ACC, ms=4, lw=1.2, label="Median by damage stage")
for k, r in med.iterrows(): ax.annotate(str(k), (1 - r.static_left, 1 - r.vib_left_breathing), xytext=(4, -9), textcoords="offset points", fontsize=7, color=ACC)
ax.plot([0, 0.9], [0, 0.9], ls="--", color=DARK, lw=0.8, label="Vibration registers all of the loss")
ax.set_xlim(0, 0.9); ax.set_ylim(0, 0.9); ax.set_xlabel("Static stiffness loss"); ax.set_ylabel("Vibration stiffness loss")
ax.legend(fontsize=6.5, frameon=False, loc="upper left")
fig.savefig("figs/f47_static_vib.png", bbox_inches="tight", pad_inches=0.04); plt.close(fig)
h = pd.read_csv(T + "sustained_history.csv")
h0 = h[h.years == 0].set_index(["beam", "case"]).deflection_mm
h["rel"] = h.deflection_mm.values / h0.reindex(list(zip(h.beam, h.case))).values
fig, ax = plt.subplots(figsize=(3.1, 2.7))
x = {0: 0, 1: 1, 10: 2, 50: 3}
for case, col, lab in (("service", ACC, "Service load from 28 days"), ("overload", DARK, "Overload, then service load")):
    g = h[h.case == case].groupby("years").rel
    xs = [x[y] for y in g.median().index]
    ax.fill_between(xs, g.quantile(.05).values, g.quantile(.95).values, color=col, alpha=0.15, lw=0)
    ax.plot(xs, g.median().values, "o-", color=col, ms=4, lw=1.2, label=lab)
ax.set_xticks(range(4)); ax.set_xticklabels(["0", "1", "10", "50"]); ax.set_xlabel("Years under load")
ax.set_ylabel("Deflection / deflection at loading"); ax.legend(fontsize=6.5, frameon=False, loc="upper left"); ax.set_ylim(0.9, 4)
fig.savefig("figs/f48_sustained.png", bbox_inches="tight", pad_inches=0.04); plt.close(fig)
print(med.round(3))
