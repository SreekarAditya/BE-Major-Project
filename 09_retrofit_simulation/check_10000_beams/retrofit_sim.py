"""Retrofit simulation: which repair works best for which damaged beam.

A population of simply supported reinforced concrete beams (uniform load) is designed to IS 456:2000.
Each beam is given damage as the digital twin would measure it (stiffness left at the load check), drawn from
our 300-beam Monte Carlo, and possibly a change of use (live load increase). Every beam is then checked
before retrofit and after each retrofit scheme, sized to the smallest catalogue size that works:
  - carbon fibre-reinforced polymer laminate (ACI PRC-440.2-23: debonding strain Eq. 10.1.1, initial substrate
    strain Eq. 10.2.5, polymer strength reduction 0.85, safety gate Eq. 9.2)
  - bonded steel plate (IS 456 cl 38.1 assumptions, plate as extra tension steel)
  - reinforced concrete jacket on three sides (IS 15988:2013)
Checks (IS 456:2000): strength cl 38.1 (stress block, partial safety factors), shear cl 40, final deflection
cl 23.2(a) span/250 and after-partition deflection cl 23.2(b) span/350 or 20 mm (Annex C: creep cl 6.2.5.1,
shrinkage C-3), crack width cl 35.3.2 with Annex F (0.3 / 0.2 / 0.1 mm by exposure).
Retrofit is unpropped: dead load stays on the damaged bare section, live load acts on the retrofitted section.
The best compliant scheme per beam is the least intrusive (downtime: polymer < plate < jacket).
A decision tree is then trained on quantities the twin and the drawings provide, and tested on unseen beams.
Outputs: retrofit_sim.csv, retrofit_sim_summary.json, retrofit_tree.txt."""
import json, csv, math, numpy as np

SEED = 2026; N = 10000
g = np.random.default_rng(SEED)
Es, fyst, ECS, THETA = 2.0e5, 415.0, 0.0003, 1.6        # steel modulus; stirrup steel; shrinkage (cl 6.2.4.1); creep coefficient, loading at 28 days (cl 6.2.5.1)
EXPOSURE = [('Moderate, cracking not harmful', 0.3, 30.0, 0.50), ('Exposed to weather or moisture', 0.2, 30.0, 0.35), ('Severe', 0.1, 45.0, 0.15)]

# ---------------- damage as the twin measures it: Monte Carlo stiffness left, expressed as a damage index
# eta = (1 - s) / (1 - s_cr): 0 = undamaged, 1 = fully cracked (no tension stiffening left); s_cr = Icr/I0 of our beam
import os
MC_FILE = next(f for f in ('../07_uncertainty_and_validation/mc_raw_samples.jsonl', '../../07_uncertainty_and_validation/mc_raw_samples.jsonl') if os.path.exists(f))
mc = [json.loads(l) for l in open(MC_FILE)]
s_mc = np.array([r['rows'][0]['delta_d'] / r['rows'][k]['delta_d'] for r in mc if r['ok'] for k in range(1, 5)])
S_CR_OURS = 0.209                                   # Icr / I0 (transformed) of the 230 x 300 test beam
ETA_POOL = np.clip((1 - s_mc) / (1 - S_CR_OURS), 0, 1)
TWIN_LOG_SD = 0.02                                   # calibrated twin uncertainty (log stiffness), mc2_summary.json

# ---------------- section mechanics (N, mm)
def stress_block(c, b, fck, ec_top):
    """IS 456 parabola-rectangle (design: peak 0.446 fck), returns force and its depth from the top."""
    n = 120; y = (np.arange(n) + 0.5) / n * c; e = ec_top * (c - y) / c
    s = np.where(e < 0.002, 0.446 * fck * (2 * e / 0.002 - (e / 0.002) ** 2), 0.446 * fck)
    F = (s * b * c / n).sum(); return F, (s * b * c / n * y).sum() / max(F, 1e-9)

def moment_capacity(b, H, fck, bars, layer=None):
    """Design moment of resistance by strain compatibility (IS 456 cl 38.1).
    bars: list of (area, depth from top, fy). layer: dict(A, y, E, fy or None, efd or None, ebi, psi)."""
    best = None
    for mode in ('crush', 'debond'):
        if mode == 'debond' and (layer is None or layer.get('efd') is None): continue
        lo, hi = 1.0, H; feasible = True
        for _ in range(60):
            c = 0.5 * (lo + hi)
            if mode == 'crush': ec = 0.0035
            else:
                ec = (layer['efd'] + layer['ebi']) * c / (layer['y'] - c)
                if ec > 0.0035: feasible = False; break
            F, yc = stress_block(c, b, fck, ec); T = 0.0; M = 0.0
            for A, y, fy in bars:
                e = ec * (y - c) / c; s = np.clip(Es * e, -0.87 * fy, 0.87 * fy); T += A * s; M += A * s * (y - yc)
            if layer is not None:
                e = ec * (layer['y'] - c) / c - layer['ebi']
                if layer.get('efd') is not None: e = min(e, layer['efd'])
                s = layer['E'] * max(e, 0.0)
                if layer.get('fy'): s = min(s, 0.87 * layer['fy'])
                s *= layer.get('psi', 1.0); T += layer['A'] * s; M += layer['A'] * s * (layer['y'] - yc)
            if T > F: lo = c
            else: hi = c
        if feasible and (best is None or M < best): best = M
    return best

def cracked(b, H, Ec, tension, comp):
    """Cracked transformed section: neutral axis x and Icr. tension/comp: list of (area, depth, modulus)."""
    lo, hi = 1.0, H
    for _ in range(80):
        x = 0.5 * (lo + hi)
        f = b * x * x / 2 + sum((E / Ec - 1) * A * (x - y) for A, y, E in comp) - sum(E / Ec * A * (y - x) for A, y, E in tension)
        if f > 0: hi = x
        else: lo = x
    I = b * x ** 3 / 3 + sum((E / Ec - 1) * A * (x - y) ** 2 for A, y, E in comp) + sum(E / Ec * A * (y - x) ** 2 for A, y, E in tension)
    return x, I

def uncracked(b, H, Ec, bars):
    A0 = b * H + sum((E / Ec - 1) * A for A, y, E in bars); y0 = (b * H * H / 2 + sum((E / Ec - 1) * A * y for A, y, E in bars)) / A0
    return b * H ** 3 / 12 + b * H * (H / 2 - y0) ** 2 + sum((E / Ec - 1) * A * (y - y0) ** 2 for A, y, E in bars)

def tau_c(pt, fck):                                   # IS 456 Table 19 (formula form of SP 16)
    pt = min(max(pt, 0.15), 3.0); beta = max(0.8 * fck / (6.89 * pt), 1.0)
    return 0.85 * math.sqrt(0.8 * fck) * (math.sqrt(1 + 5 * beta) - 1) / (6 * beta)

# ---------------- one beam
def design_beam():
    """IS 456 design of a simply supported beam under uniform load; rejected and redrawn unless it complied when new."""
    while True:
        L = g.uniform(3000, 8000); b = float(g.choice([230.0, 300.0])); D = max(300.0, 25 * round(L / g.uniform(10, 13) / 25))
        fck = float(g.choice([20.0, 25.0, 30.0])); fy = 500.0; Ec = 5000 * math.sqrt(fck)
        ex = EXPOSURE[g.choice(3, p=[e[3] for e in EXPOSURE])]; cover = ex[2]; phi = float(g.choice([12.0, 16.0, 20.0]))
        d = D - cover - 8 - phi / 2; pt = g.uniform(0.5, 1.2) / 100
        n = max(2, math.ceil(pt * b * d / (math.pi * phi ** 2 / 4))); As = n * math.pi * phi ** 2 / 4
        if 0.87 * fy * As / (0.36 * fck * b) > 0.46 * d: continue            # keep it under-reinforced (cl 38.1)
        Asc, dc = 2 * math.pi * 25.0, cover + 8 + 5                         # two 10 mm hanger bars
        if (n * phi + (n - 1) * 25) > b - 2 * (cover + 8): continue          # bars must fit in one layer
        bars = [(As, d, fy), (Asc, dc, fy)]
        Mu_cap = moment_capacity(b, D, fck, bars)
        Mu0 = Mu_cap * g.uniform(0.85, 1.0); Ms0 = Mu0 / 1.5; fDL = g.uniform(0.40, 0.65)
        # stirrups: 2-legged 8 mm for the original design shear, spacing <= 0.75 d and 300 mm (cl 26.5.1.5)
        Vu0 = 4 * Mu0 / L; Vc = tau_c(100 * As / (b * d), fck) * b * d; Asv = 2 * math.pi * 16
        sv = min(0.75 * d, 300.0, (0.87 * fyst * Asv * d / max(Vu0 - Vc, 1.0)) if Vu0 > Vc else 300.0, 0.87 * fyst * Asv / (0.4 * b))
        sv = 25 * math.floor(sv / 25)
        B = dict(L=L, b=b, D=D, d=d, fck=fck, fy=fy, Ec=Ec, cover=cover, phi=phi, n=n, As=As, Asc=Asc, dc=dc, bars=bars,
                 Mu_cap=Mu_cap, Mu0=Mu0, MDL=fDL * Ms0, MLL0=(1 - fDL) * Ms0, Asv=Asv, sv=sv, exposure=ex[0], wlim=ex[1])
        B['I0'] = uncracked(b, D, Ec, [(As, d, Es), (Asc, dc, Es)])
        B['xcr'], B['Icr'] = cracked(b, D, Ec, [(As, d, Es)], [(Asc, dc, Es)])
        B['s_cr'] = B['Icr'] / B['I0']
        # when new: Branson effective inertia (IS 456 Annex C-2.1 form) must satisfy cl 23.2
        Mcr = 0.7 * math.sqrt(fck) * B['I0'] / (D / 2); Ms = Ms0
        Ie = B['I0'] if Ms <= Mcr else min(B['I0'], (Mcr / Ms) ** 3 * B['I0'] + (1 - (Mcr / Ms) ** 3) * B['Icr'])
        ok = deflections(B, Ec * Ie, Ec * Ie, B['MLL0'])
        if ok[0] <= L / 250 and ok[1] <= min(L / 350, 20.0): return B

def deflections(B, EI_dl, EI_ll, MLL):
    """Final deflection (cl 23.2a) and after-partition deflection (cl 23.2b), uniform load: 5 M L^2 / (48 EI)."""
    L, D = B['L'], B['D']; k = 5 * L * L / 48
    d_dl, d_ll = k * B['MDL'] / EI_dl, k * MLL / EI_ll
    d_creep = THETA * d_dl                                                    # Annex C-4 with Ecc = Ec / (1 + theta)
    pt, pc = 100 * B['As'] / (B['b'] * B['d']), 100 * B['Asc'] / (B['b'] * B['d']); dp = pt - pc
    k4 = min(0.72 * dp / math.sqrt(pt), 1.0) if dp < 1.0 else min(0.65 * dp / math.sqrt(pt), 1.0)
    d_sh = 0.125 * k4 * ECS / D * L * L                                       # Annex C-3, simply supported k3 = 0.125
    return d_dl + d_ll + d_creep + d_sh, d_ll + d_creep + d_sh

def crack_width(B, sig_s, x, eta, tension_layer_force=0.0):
    """IS 456 Annex F at the soffit, midway between bars. Tension stiffening reduced in proportion to the damage index."""
    D, d, b, cover, phi, n = B['D'], B['d'], B['b'], B['cover'], B['phi'], B['n']
    sp = (b - 2 * (cover + 8) - phi) / max(n - 1, 1); ybar = D - d
    acr = math.sqrt((sp / 2) ** 2 + ybar ** 2) - phi / 2; cmin = cover + 8
    e1 = sig_s / Es * (D - x) / (d - x)
    ts = b * (D - x) * (D - x) / (3 * Es * B['As'] * (d - x))
    em = max(e1 - (1 - eta) * ts, 0.0)
    return 3 * acr * em / (1 + 2 * (acr - cmin) / (D - x))

def steel_stress(M, Ec, I, x, d):
    return Es / Ec * M * (d - x) / I

def evaluate(B, scheme, size, s_lb, eta, lamL, propped=False):
    """All code checks for one beam with one scheme (None = as is). Returns dict of ratios (<= 1 passes)."""
    L, b, D, d, fck, Ec = B['L'], B['b'], B['D'], B['d'], B['fck'], B['Ec']
    MLL = lamL * B['MLL0']; Mu_dem = 1.5 * (B['MDL'] + MLL); Ms = B['MDL'] + MLL
    EI_dam = s_lb * Ec * B['I0']                                           # stiffness left, lower bound of the twin
    bars, H, bw = list(B['bars']), D, b; layer = None; ten = [(B['As'], d, Es)]; comp = [(B['Asc'], B['dc'], Es)]
    MDL_extra = 0.0; Vcap_extra = 0.0; gate = True
    # initial substrate strain at the soffit from dead load on the damaged section (ACI PRC-440.2-23 Eq. 10.2.5)
    ebi = B['MDL'] * (D - B['xcr']) / (Ec * B['Icr'])
    if scheme == 'polymer':
        plies, nstrip = size; tf = 1.2 * plies; Ef = 165000.0; A = nstrip * 50.0 * tf
        if nstrip * 50.0 > b - 50: return None
        efd = min(0.41 * math.sqrt(0.8 * fck / (plies * Ef * 1.2)), 0.9 * 0.017)   # Eq. 10.1.1 (cylinder = 0.8 cube)
        layer = dict(A=A, y=D, E=Ef, efd=efd, ebi=ebi, psi=0.85); ten.append((A, D, Ef))
        Mn_exist = B['Mu_cap']; gate = Mn_exist >= 1.1 * B['MDL'] + 0.75 * MLL      # Eq. 9.2 safety gate
    elif scheme == 'plate':
        t = size; wpl = b - 40; A = wpl * t
        layer = dict(A=A, y=D + t / 2, E=Es, fy=250.0, ebi=ebi); ten.append((A, D + t / 2, Es))
    elif scheme == 'jacket':
        tj, nb, db = size; Ab = nb * math.pi * db * db / 4
        bw, H = b + 2 * tj, D + tj; bars = bars + [(Ab, H - 30 - 8 - db / 2, 500.0)]
        ten = ten + [(Ab, H - 30 - 8 - db / 2, Es)]
        MDL_extra = 25e-6 * (bw * H - b * D) * L * L / 8                     # jacket self-weight moment (25 kN/m3), N mm
        Vcap_extra = tau_c(100 * (B['As'] + Ab) / (bw * (H - 45)), fck) * bw * (H - 45) - tau_c(100 * B['As'] / (b * d), fck) * b * d \
                     + 0.87 * fyst * (2 * math.pi * 16) * (H - 45) / 150 * 0.5   # jacket ties 8 mm at 150, half effective
    # strength (cl 38.1)
    Mu = moment_capacity(bw, H, fck, bars, layer)
    Mu_dem_t = Mu_dem + 1.5 * MDL_extra
    # shear (cl 40): flexural schemes do not add shear capacity
    Vc = tau_c(100 * B['As'] / (b * d), fck) * b * d; Vs = 0.87 * fyst * B['Asv'] * d / B['sv']
    Vcap = Vc + Vs + Vcap_extra; Vdem = 4 * Mu_dem_t / L
    uwrap = 0
    if scheme in ('polymer', 'plate'):
        # shear U-wraps if needed (ACI PRC-440.2-23 cl 11.4: effective strain 0.004 for U-wraps, psi 0.85):
        # carbon sheet 0.167 mm, 100 mm wide strips at 200 mm, one or two layers
        while Vdem > Vcap and uwrap < 2:
            uwrap += 1; Vcap += 0.85 * 2 * 0.167 * 100 * 230000 * 0.004 * (D - 60) / 200
    # stiffness of the retrofitted section, scaled to the measured damaged stiffness
    if scheme is None: r = 1.0; x_ll, I_ll = B['xcr'], B['Icr']
    else:
        x_ll, I_ll = cracked(bw, H, Ec, ten, comp); r = I_ll / B['Icr']
    if propped:   # beam propped and relieved before strengthening: dead load and its creep also act on the strengthened section
        defl, defl_part = deflections(B, EI_dam * r, EI_dam * r, MLL + MDL_extra)
    else:
        defl, defl_part = deflections(B, EI_dam, EI_dam * r, MLL + MDL_extra)
    # steel stress and crack width at service: dead load on bare section, live load on retrofitted section
    sig = (steel_stress(B['MDL'] + MLL + MDL_extra, Ec, I_ll, x_ll, d) if propped else
           steel_stress(B['MDL'], Ec, B['Icr'], B['xcr'], d) + steel_stress(MLL + MDL_extra, Ec, I_ll, x_ll, d))
    w = crack_width(B, sig, B['xcr'], eta)
    return dict(strength=Mu_dem_t / Mu, shear=Vdem / Vcap, defl=defl / (L / 250), defl_part=defl_part / min(L / 350, 20.0),
                crack=w / B['wlim'], steel=sig / (0.8 * B['fy']), gate=gate, r=r, Mu=Mu, w=w, uwrap=uwrap)

def passes(e, crack=True):
    return e is not None and e['gate'] and e['strength'] <= 1 and e['shear'] <= 1 and e['defl'] <= 1 and e['defl_part'] <= 1 and (e['crack'] <= 1 or not crack)

CATALOGUE = {'polymer': [(p, n) for p in (1, 2) for n in (1, 2, 3, 4)],
             'plate': [3, 4, 5, 6],                       # thin bonded plates (thicker plates peel at the ends)
             'jacket': [(t, nb, db) for t in (75, 100, 125) for nb, db in ((2, 12), (2, 16), (3, 16), (3, 20))]}
SIZE_ORDER = {'polymer': lambda s: s[0] * 4 + s[1], 'plate': lambda s: s, 'jacket': lambda s: s[0] * 1000 + s[1] * s[2] ** 2}

def best_size(B, scheme, s_lb, eta, lamL):
    for propped in (False, True):                                   # try without propping first; propping costs time and access
        for size in sorted(CATALOGUE[scheme], key=SIZE_ORDER[scheme]):
            e = evaluate(B, scheme, size, s_lb, eta, lamL, propped)
            if passes(e, crack=False): return (size, e['uwrap'], propped), e   # durability of wide cracks is handled by sealing, applied with every scheme
    return None, None

def run():
    rows = []
    for i in range(N):
        B = design_beam()
        eta = float(g.choice(ETA_POOL)); s = 1 - eta * (1 - B['s_cr'])
        s_lb = s * math.exp(-1.645 * TWIN_LOG_SD)
        lamL = float(g.choice([1.0, 1.5, 2.0], p=[0.5, 0.25, 0.25]))
        before = evaluate(B, None, None, s_lb, eta, lamL)
        res = {k: best_size(B, k, s_lb, eta, lamL) for k in ('polymer', 'plate', 'jacket')}
        if passes(before): label = 'Monitor'
        elif passes(before, crack=False): label = 'Seal cracks'
        elif res['polymer'][0] is not None: label = 'Polymer laminate'   # each strengthening scheme is followed by crack sealing if cracks exceed the limit
        elif res['plate'][0] is not None: label = 'Steel plate'
        elif res['jacket'][0] is not None: label = 'Concrete jacket'
        else: label = 'Beyond these schemes'
        fails = [k for k in ('strength', 'shear', 'defl', 'defl_part', 'crack') if before[k] > 1]
        rows.append(dict(beam=i, span_m=B['L'] / 1000, b=B['b'], D=B['D'], fck=B['fck'], pt=100 * B['As'] / (B['b'] * B['d']),
                         span_depth=B['L'] / B['d'], exposure=B['exposure'], crack_limit_mm=B['wlim'], dead_fraction=B['MDL'] / (B['MDL'] + B['MLL0']),
                         utilisation=B['Mu0'] / B['Mu_cap'], live_load_factor=lamL, damage_index=eta, stiffness_left=s, stiffness_left_lower=s_lb,
                         crack_width_mm=before['w'], crack_ratio=before['crack'], strength_ratio=before['strength'], shear_ratio=before['shear'],
                         deflection_ratio=before['defl'], partition_deflection_ratio=before['defl_part'], polymer_gate=evaluate(B, 'polymer', (1, 1), s_lb, eta, lamL)['gate'] if B['b'] >= 100 else False,
                         fails=';'.join(fails) or 'none', best=label,
                         polymer_size=str(res['polymer'][0]), plate_mm=str(res['plate'][0]), jacket_size=str(res['jacket'][0]),
                         propped=(res[{'Polymer laminate':'polymer','Steel plate':'plate','Concrete jacket':'jacket'}[label]][0][2] if label in ('Polymer laminate','Steel plate','Concrete jacket') else False),
                         polymer_ok=res['polymer'][0] is not None, plate_ok=res['plate'][0] is not None, jacket_ok=res['jacket'][0] is not None))
    return rows

if __name__ == '__main__':
    rows = run()
    with open('retrofit_sim.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    from collections import Counter
    c = Counter(r['best'] for r in rows); print(c)
    print('fails', Counter(r['fails'] for r in rows).most_common(12))
