"""Space-filling design of the beam population (Latin hypercube, seed 2027).
Usage: python3 design.py N design.csv"""
import sys, csv, math
import numpy as np
from scipy.stats import qmc
import gen

SD = {20: 4.0, 25: 4.0, 30: 5.0, 35: 5.0, 40: 5.0}           # IS 456 Table 8 assumed standard deviation
GRADES = [20, 25, 30, 35, 40]; DIAS = [12, 16, 20, 25]; FY = [415, 500]
XUMAX = {415: 0.48, 500: 0.46}
FRACTIONS = '0.43;0.62;0.80;0.89;1.00'                          # of the hand first-yield load

def make(N, seed=2027):
    u = qmc.LatinHypercube(d=9, seed=seed).random(N)
    rows = []
    for i in range(N):
        v = u[i]
        L = 2000 + 4000 * v[0]
        b = 10 * round((200 + 100 * v[1]) / 10)
        ratio = 10 + 6 * v[2]
        cover = 5 * round((25 + 15 * v[5]) / 5)
        grade = GRADES[min(int(v[6] * 5), 4)]; fy_nom = FY[int(v[7] * 2)]
        load = 'four_point' if v[8] < 0.5 else 'udl'
        phi = DIAS[min(int(v[4] * 4), 3)]
        d = L / ratio
        h = 25 * math.ceil((d + cover + 8 + phi / 2) / 25); h = min(max(h, 250), 600)
        d = h - cover - 8 - phi / 2
        pt = 0.5 + 1.1 * v[3]
        As_t = pt / 100 * b * d
        As_min = 0.85 * b * d / fy_nom
        As_max = XUMAX[fy_nom] * 0.36 * grade * b * d / (0.87 * fy_nom)      # under-reinforced limit
        As_t = min(max(As_t, As_min), 0.95 * As_max)
        # bars in one layer: clear spacing >= max(phi, 25 mm); go up a size if they do not fit
        for p in [x for x in DIAS if x >= phi] + [25]:
            n = max(2, round(As_t / gen.bar_area(p)))
            clear = (b - 2 * (cover + 8) - n * p) / (n - 1)
            if clear >= max(p, 25): phi = p; break
        else:
            phi = 25; n = max(2, int((b - 2 * (cover + 8) + 25) // 50))
        d = h - cover - 8 - phi / 2
        As_max = XUMAX[fy_nom] * 0.36 * grade * b * d / (0.87 * fy_nom)
        while n > 2 and n * gen.bar_area(phi) > As_max: n -= 1
        while n * gen.bar_area(phi) > As_max and phi > 12:
            phi = DIAS[DIAS.index(phi) - 1]; d = h - cover - 8 - phi / 2
        d_top = 10 if b <= 250 else 12
        rng = np.random.default_rng(20270000 + i)
        fck = max(grade - 10.0, rng.normal(grade, SD[grade]))
        Ec = 5000 * math.sqrt(fck) * rng.lognormal(0, 0.15)
        ft = 0.7 * math.sqrt(fck) * rng.lognormal(0, 0.15)
        ets = rng.uniform(0.05, 0.10); fy = rng.normal(fy_nom, 0.05 * fy_nom)
        row = dict(beam=i, span_mm=round(L, 1), b_mm=b, h_mm=h, cover_mm=cover, d_stir_mm=8, n_bot=n, d_bot_mm=phi,
                   n_top=2, d_top_mm=d_top, grade_MPa=grade, fy_nom_MPa=fy_nom, load=load,
                   fck_MPa=round(fck, 3), Ec_MPa=round(Ec, 1), ft_MPa=round(ft, 3), ets=round(ets, 4), fy_MPa=round(fy, 2))
        g = gen.geometry(row)
        row.update(d_mm=round(g['d'], 1), As_mm2=round(g['As'], 1), pt_pct=round(100 * g['As'] / (b * g['d']), 3),
                   span_over_d=round(L / g['d'], 2), Py_hand_kN=round(gen.hand_yield_load(g), 2), stage_fractions=FRACTIONS)
        rows.append(row)
    return rows

if __name__ == '__main__':
    N, out = int(sys.argv[1]), sys.argv[2]
    rows = make(N)
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    import collections
    print(N, 'beams; load', collections.Counter(r['load'] for r in rows), '; bars', collections.Counter(r['d_bot_mm'] for r in rows))
    for k in ('span_mm', 'b_mm', 'h_mm', 'pt_pct', 'span_over_d', 'Py_hand_kN'):
        x = np.array([r[k] for r in rows], float); print(k, x.min(), np.median(x), x.max())
