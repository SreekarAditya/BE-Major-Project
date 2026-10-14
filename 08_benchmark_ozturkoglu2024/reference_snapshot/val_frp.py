"""Check of the polymer-strengthening method (ACI PRC-440.2-23 debonding strain + strain compatibility)
against the published tests of Musial, Trapko and Grosel (2021), beams B-II-1 and B-II-2 (strengthened before loading).
Mean measured properties, no safety or reduction factors, three-point bending over 3.0 m."""
import numpy as np, json
b, h, d, dt = 150.0, 250.0, 224.0, 26.0
As, Ast = 3 * np.pi * 36, 2 * np.pi * 16
fc, Es, fy, Ef, tf, efu = 50.8, 195000.0, 558.0, 210000.0, 1.4, 0.017
eps_fd = min(0.41 * np.sqrt(fc / (1 * Ef * tf)), 0.9 * efu)     # SI form, one ply
def conc_force(c, eps_top, n=200):                               # parabola-rectangle, eps_c2 = 0.002, eps_cu = 0.0035
    y = (np.arange(n) + 0.5) / n * c; e = eps_top * (c - y) / c
    s = np.where(e < 0.002, fc * (1 - (1 - e / 0.002) ** 2), fc)
    return (s * b * c / n).sum(), (s * b * c / n * y).sum()
def capacity(Af):
    best = None
    for c in np.linspace(5, 150, 2901):
        ef = eps_fd if Af > 0 else 1.0; ec = ef * c / (h - c)
        if ec > 0.0035: ec = 0.0035; ef = ec * (h - c) / c                 # crushing governs
        es = ec * (d - c) / c; est = ec * (c - dt) / c
        Fs = As * np.clip(Es * es, -fy, fy); Fst = Ast * np.clip(Es * est, -fy, fy); Ff = Af * Ef * ef
        Cc, Mc = conc_force(c, ec)
        r = Cc + Fst - Fs - Ff
        if best is None or abs(r) < abs(best[0]): best = (r, c, Cc, Mc, Fs, Fst, Ff, ef, ec)
    r, c, Cc, Mc, Fs, Fst, Ff, ef, ec = best
    M = (Fs * d + Ff * h - Fst * dt - Mc) / 1e6      # moments about the top fibre
    M = -M if M < 0 else M
    return dict(c=c, eps_f=ef, eps_c=ec, M=M, P=4 * M / 3.0)
out = dict(eps_fd=eps_fd, unstrengthened=dict(capacity(0.0), test_P=57.41))
for name, Af, test in (('B-II-1', 84.0, 90.23), ('B-II-2', 168.0, 116.01)):
    r = capacity(Af); r['test_P'] = test; r['ratio'] = r['P'] / test; out[name] = r
json.dump(out, open('musial_frp.json', 'w'), indent=1)
print('debonding strain %.5f' % eps_fd)
for k in ('unstrengthened', 'B-II-1', 'B-II-2'):
    r = out[k]; print(k, 'P %.1f kN' % r['P'], 'c %.1f' % r['c'], 'eps_c %.5f' % r['eps_c'], '' if k == 'unstrengthened' else 'test %.1f ratio %.2f' % (r['test_P'], r['ratio']))
