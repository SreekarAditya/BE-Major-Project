import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle, Patch
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
from datetime import date

plt.rcParams.update({
    "font.family": "Times New Roman", "font.size": 9, "axes.titlesize": 9,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 650,
})
ACC, GREY, DARK = "#1f5fa8", "#b5b5b5", "#555555"
OUT = "figs/"


def save(fig, name):
    fig.savefig(OUT + name, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


# Figure 3.1 specimen
fig, ax = plt.subplots(figsize=(6.3, 1.9))
ax.set_xlim(-0.3, 4.6); ax.set_ylim(-0.75, 0.85); ax.axis("off"); ax.set_aspect("equal")
ax.add_patch(Rectangle((0, 0), 3.0, 0.3, fill=False, lw=1))
ax.add_patch(Rectangle((1.0, 0), 1.0, 0.3, color=ACC, alpha=0.15, lw=0))
ax.plot([0.03, 2.97], [0.05, 0.05], ls="--", color=DARK, lw=0.7)
ax.add_patch(Polygon([[0, 0], [-0.08, -0.13], [0.08, -0.13]], fill=False, lw=0.9))
ax.add_patch(Circle((3.0, -0.065), 0.065, fill=False, lw=0.9))
for x in (1.0, 2.0):
    ax.annotate("", xy=(x, 0.31), xytext=(x, 0.68), arrowprops=dict(arrowstyle="-|>", lw=0.9, fc="k", ec="k"))
    ax.text(x, 0.72, "P/2", ha="center", va="bottom")
ax.text(1.5, 0.15, "Constant moment", ha="center", va="center", fontsize=8)
ax.plot([0, 3.0], [-0.3, -0.3], color="k", lw=0.6)
for x in (0, 1, 2, 3):
    ax.plot([x, x], [-0.34, -0.26], color="k", lw=0.6)
for x in (0.5, 1.5, 2.5):
    ax.text(x, -0.42, "1.0 m", ha="center", va="top", fontsize=8)
ax.text(1.5, -0.6, "Span 3.0 m, simply supported; P = total load", ha="center", va="top", fontsize=8)
# section
sx = 3.6
ax.add_patch(Rectangle((sx, -0.15), 0.23, 0.30 * 2, fill=False, lw=1))
for dx in (0.05, 0.115, 0.18):
    ax.add_patch(Circle((sx + dx, -0.08), 0.022, color="k"))
ax.text(sx + 0.115, -0.2, "230 mm", ha="center", va="top", fontsize=8)
ax.text(sx + 0.27, 0.15, "300 mm", ha="left", va="center", fontsize=8)
ax.text(sx + 0.115, -0.38, "M30; 3 bars of\n12 mm, Fe500", ha="center", va="top", fontsize=8)
ax.text(1.5, 0.85, "Elevation", ha="center", va="bottom", fontsize=8, fontweight="bold")
ax.text(sx + 0.115, 0.55, "Section (scale x2)", ha="center", va="bottom", fontsize=8, fontweight="bold")
ax.legend(handles=[Patch(color=ACC, alpha=0.15, label="Constant-moment zone"),
                   Line2D([], [], ls="--", color=DARK, lw=0.7, label="Bottom reinforcement")],
          loc="lower left", bbox_to_anchor=(-0.02, -0.12), fontsize=7, frameon=False, ncol=2)
save(fig, "f31_specimen.png")

# Figure 3.2 methodology flow (2 rows x 4)
steps = [
    ("1. Define specimen", "230 x 300 mm, 3.0 m span,\nM30, Fe500; IS 456 checks"),
    ("2. Fibre-section model", "OpenSeesPy, 24 force-\nbased elements"),
    ("3. Simulate 300 beams", "Material scatter; loaded\nto 72 kN"),
    ("4. Rank the inputs", "Sobol total indices on a\nquadratic surrogate"),
    ("5. Calibrate the twin", "Calibrate on beams 0-149,\ntest on 150-299"),
    ("6. Blind validation", "Published test of\nMusiał et al. (2021)"),
    ("7. Retrofit simulation", "10,000 IS 456 beams; least\nintrusive compliant scheme"),
    ("8. Decision tree, rule", "Depth-3 tree; Red/Amber/\nGreen rule for specimens"),
]
fig, ax = plt.subplots(figsize=(6.3, 2.35))
ax.set_xlim(0, 4); ax.set_ylim(0, 2); ax.axis("off")
w, h = 0.9, 0.7
pos = [(0.03 + i * 1.0, 1.15) for i in range(4)] + [(0.03 + (3 - i) * 1.0, 0.15) for i in range(4)]
for k, ((t, b), (x, y)) in enumerate(zip(steps, pos)):
    main = k == 4
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.05",
                                fc=ACC if main else "white", alpha=1, ec=ACC if main else DARK,
                                lw=1.3 if main else 0.8))
    col = "white" if main else "black"
    ax.text(x + w / 2, y + h - 0.13, t, ha="center", va="center", fontsize=7.2, fontweight="bold", color=col)
    ax.text(x + w / 2, y + 0.26, b, ha="center", va="center", fontsize=6.6, color=col)
for k in range(7):
    (x1, y1), (x2, y2) = pos[k], pos[k + 1]
    if k == 3:
        ax.annotate("", xy=(x2 + w / 2, y2 + h), xytext=(x1 + w / 2, y1), arrowprops=dict(arrowstyle="-|>", lw=0.8, fc="k", ec="k"))
    elif k < 3:
        ax.annotate("", xy=(x2, y2 + h / 2), xytext=(x1 + w, y1 + h / 2), arrowprops=dict(arrowstyle="-|>", lw=0.8, fc="k", ec="k"))
    else:
        ax.annotate("", xy=(x2 + w, y2 + h / 2), xytext=(x1, y1 + h / 2), arrowprops=dict(arrowstyle="-|>", lw=0.8, fc="k", ec="k"))
ax.legend(handles=[Patch(fc=ACC, label="Twin calibration (core step)"),
                   Patch(fc="white", ec=DARK, label="Supporting step")],
          loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=2, fontsize=7, frameon=False)
save(fig, "f32_flow.png")

# Figure 4.1 Sobol
inp = ["Tensile strength scatter", "Elastic modulus scatter", "Tension-softening slope",
       "Concrete strength", "Steel yield strength"]
val = [67, 19, 11, 7, 0]
fig, ax = plt.subplots(figsize=(3.1, 1.9))
cols = [ACC] + [GREY] * 4
ax.barh(inp[::-1], val[::-1], color=cols[::-1], height=0.6)
for i, v in enumerate(val[::-1]):
    ax.text(v + 1, i, f"{v}%", va="center", fontsize=8)
ax.set_xlim(0, 80); ax.set_xlabel("Sobol total index (%)")
ax.legend(handles=[Patch(color=ACC, label="Dominant input"), Patch(color=GREY, label="Other inputs")],
          fontsize=7, frameon=False, loc="lower right")
save(fig, "f41_sobol.png")

# Figure 4.2 estimator error
est = ["No updating", "Vibration only", "Deflection only", "Twin (both)"]
err = [60, 51, 0.7, 0.7]
fig, ax = plt.subplots(figsize=(3.1, 1.9))
cols = [GREY, GREY, GREY, ACC]
ax.barh(est[::-1], err[::-1], color=cols[::-1], height=0.6)
for i, v in enumerate(err[::-1]):
    ax.text(max(v, 5) + 1.2, i, f"{v}%", va="center", fontsize=8)
ax.axvline(5, color=DARK, ls="--", lw=0.8)
ax.set_xlim(0, 72); ax.set_xlabel("Median deflection error at 72 kN (%)")
ax.legend(handles=[Patch(color=ACC, label="Twin"), Patch(color=GREY, label="Other estimators"),
                   Line2D([], [], color=DARK, ls="--", lw=0.8, label="5% target (H3)")],
          fontsize=7, frameon=False, loc="lower right")
save(fig, "f42_error.png")

# Figure 4.3 scheme counts
sch = ["Monitor", "Seal\ncracks", "Carbon fibre\nlaminates", "Steel\nplate", "Concrete\njacket"]
n = [3178, 1464, 4909, 426, 23]
fig, ax = plt.subplots(figsize=(3.1, 1.95))
cols = [GREY, GREY, ACC, GREY, GREY]
ax.bar(range(5), n, color=cols, width=0.65)
for i, v in enumerate(n):
    ax.text(i, v + 80, f"{v}\n({v/100:.1f}%)", ha="center", va="bottom", fontsize=7)
ax.set_xticks(range(5)); ax.set_xticklabels(sch, fontsize=7)
ax.set_ylim(0, 6300); ax.set_ylabel("Number of beams")
ax.legend(handles=[Patch(color=ACC, label="Most frequent scheme"), Patch(color=GREY, label="Other schemes")],
          fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=2)
save(fig, "f43_counts.png")

# Figure 4.4 compliance
bins = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60"]
beams = [803, 1435, 1044, 947, 623, 174]
lam = [100, 99, 97, 85, 69, 58]; plate = [100, 100, 100, 100, 99, 91]; jack = [100] * 6
fig, ax = plt.subplots(figsize=(3.1, 1.95))
x = range(6)
ax.plot(x, jack, ls="--", color=GREY, marker="o", ms=3, lw=1.2, label="Concrete jacket")
ax.plot(x, plate, color=DARK, marker="s", ms=3, lw=1.2, label="Steel plate")
ax.plot(x, lam, color=ACC, marker="o", ms=3.5, lw=1.6, label="Carbon fibre laminates")
for i in (3, 4, 5):
    ax.text(i + 0.1, lam[i] + 1, f"{lam[i]}%", ha="left", va="bottom", fontsize=7, color=ACC)
ax.axvline(2.5, color=DARK, ls=":", lw=0.8)
ax.text(2.55, 52, "Laminate limit\nabout 30%", fontsize=6.5, va="bottom")
ax.set_xticks(list(x)); ax.set_xticklabels([f"{b}\n({m})" for b, m in zip(bins, beams)], fontsize=6.5)
ax.set_xlabel("Strength increase needed (%) (beams in bin)", fontsize=8)
ax.set_ylabel("Beams complying (%)"); ax.set_ylim(50, 104); ax.set_xlim(-0.3, 5.6)
ax.legend(fontsize=6.5, frameon=False, loc="lower left", bbox_to_anchor=(0, 0.12))
save(fig, "f44_compliance.png")

# Figure 6.1 Gantt
tasks = [
    ("Literature review", date(2026, 7, 15), date(2026, 10, 28), "done", date(2027, 4, 30)),
    ("Problem definition and scope", date(2026, 7, 15), date(2026, 8, 20), "done"),
    ("Review 1", date(2026, 8, 27), None, "ms"),
    ("Beam model and simulations", date(2026, 8, 15), date(2026, 10, 5), "done"),
    ("Published-test validation", date(2026, 9, 28), date(2026, 10, 13), "done"),
    ("Retrofit simulation and tree", date(2026, 10, 5), date(2026, 10, 31), "done"),
    ("Review 2", date(2026, 10, 14), None, "ms"),
    ("Specimen design and procurement", date(2026, 10, 28), date(2026, 12, 10), "plan"),
    ("Specimen casting and curing", date(2026, 12, 1), date(2027, 1, 15), "plan"),
    ("Sensors and live monitoring", date(2026, 12, 20), date(2027, 2, 20), "plan"),
    ("Damage, retrofit, failure tests", date(2027, 1, 15), date(2027, 3, 20), "plan"),
    ("Twin validation on own beams", date(2027, 2, 15), date(2027, 4, 5), "plan"),
    ("Thesis and final review", date(2027, 3, 15), date(2027, 4, 30), "plan"),
]
fig, ax = plt.subplots(figsize=(6.3, 3.2))
for i, (name, s, e, st, *rest) in enumerate(tasks):
    y = len(tasks) - 1 - i
    if rest:                                   # continuing task: planned remainder after the report date
        ax.barh(y, mdates.date2num(rest[0]) - mdates.date2num(e), left=mdates.date2num(e), height=0.55, color=GREY)
    if st == "ms":
        ax.plot(mdates.date2num(s), y, marker="D", color=ACC, ms=5)
    else:
        sn, en = mdates.date2num(s), mdates.date2num(e)
        kw = dict(done=dict(color=ACC), now=dict(fc=ACC, alpha=0.35, ec=ACC), plan=dict(color=GREY))[st]
        ax.barh(y, en - sn, left=sn, height=0.55, **kw)
ax.set_yticks(range(len(tasks))); ax.set_yticklabels([t[0] for t in tasks][::-1], fontsize=7.5)
ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.tick_params(axis="x", labelsize=7)
ax.set_xlim(mdates.date2num(date(2026, 7, 10)), mdates.date2num(date(2027, 4, 30)) + 0.5)
ax.grid(axis="x", color="#e5e5e5", lw=0.6); ax.set_axisbelow(True)
ax.legend(handles=[Patch(color=ACC, label="Done"), Patch(color=GREY, label="Planned"),
                   Line2D([], [], marker="D", color=ACC, ls="", ms=5, label="Review")],
          fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.16), ncol=3)
save(fig, "f61_gantt.png")
print("ok")
