"""Pixel digitisation of Musial et al. (2021) Figure 22 (600 dpi render of page 18): static and dynamic flexural stiffness
of the unstrengthened beams B-I-1 and B-I-2 against load. Axis calibration from the grid lines (10 kN and 1 MN m2 spacing).
Curves are tracked column by column by colour (black dashed = vibration, grey dashed = deflection) with continuity.
Writes fig22_digitised.json and an overlay image for checking."""
import sys, json, numpy as np
from PIL import Image, ImageDraw
src = sys.argv[1]
c = np.array(Image.open(src).convert('RGB')).astype(int); g = c.mean(2)
X0, DX = 215.9, 153.6          # pixel of 0 kN, pixels per 10 kN
Y0, DY = 1213.5, 153.4         # pixel of 0 MN m2, pixels per 1 MN m2
px = lambda F: X0 + F / 10 * DX
val = lambda row: (Y0 - row) / DY
def groups(mask_col):
    idx = np.where(mask_col)[0]
    if len(idx) == 0: return []
    out, s = [], [idx[0]]
    for a in idx[1:]:
        if a - s[-1] <= 2: s.append(a)
        else: out.append((np.mean(s), len(s))); s = [a]
    out.append((np.mean(s), len(s))); return out
def track(mask, start_val, F_from, F_to, avoid=()):
    rows = []; y = Y0 - start_val * DY; slope = 0.0; last_hit = None
    for col in range(int(px(F_from)), int(px(F_to)) + 1):
        cand = [(r, n) for r, n in groups(mask[:, col]) if n <= 12 and all(abs(r - a) > 4 for a in avoid)]
        pred = y + slope
        best = min(cand, key=lambda t: abs(t[0] - pred), default=None)
        if best is not None and abs(best[0] - pred) < 10:
            if last_hit is not None and col - last_hit[0] > 0:
                slope = 0.7 * slope + 0.3 * (best[0] - last_hit[1]) / (col - last_hit[0])
            y = best[0]; last_hit = (col, y); rows.append((col, y, True))
        else:
            y = pred; rows.append((col, y, False))
    return rows
black = g < 60
grey = (np.abs(c[:, :, 0] - 160) < 30) & (np.abs(c[:, :, 0] - c[:, :, 2]) < 10) & (g > 120) & (g < 200)
res = {}
def two_curves(mask, lo, hi, avoid, F_from=12.5, F_to=44.5):
    """columns where exactly two thin line segments lie in the band: upper -> first curve, lower -> second"""
    up, low = [], []
    for col in range(int(px(F_from)), int(px(F_to)) + 1):
        gs = [(r, n) for r, n in groups(mask[int(Y0 - hi * DY):int(Y0 - lo * DY), col]) if n <= 14]
        gs = [(r + int(Y0 - hi * DY), n) for r, n in gs]
        gs = [t for t in gs if all(abs(t[0] - a) > 6 for a in avoid)]
        if len(gs) == 2:
            F = (col - X0) / DX * 10; up.append((F, val(gs[0][0]))); low.append((F, val(gs[1][0])))
    return np.array(up), np.array(low)
def plateau(mask, lo, hi, avoid):
    u, l = two_curves(mask, lo, hi, avoid, 3, 10.5); return float(np.median(u[:, 1])), float(np.median(l[:, 1]))
Fs = np.arange(12, 44.6, 0.5)
for kind, mask, lo, hi, avoid in (('dyn', black, 4.85, 6.7, [Y0 - 4.75 * DY, Y0 - 4.55 * DY]),
                                  ('sta', grey, 1.8, 4.35, [Y0 - 3.15 * DY, Y0 - 2.4 * DY])):
    p2, p1 = plateau(mask, lo, hi, avoid)
    u, l = two_curves(mask, lo, hi, avoid)
    for name, arr, p in ((kind + '_BI2', u, p2), (kind + '_BI1', l, p1)):
        # bin by 0.5 kN, median, then interpolate gaps
        cen = []; 
        for F in Fs:
            m = arr[np.abs(arr[:, 0] - F) <= 0.5][:, 1] if len(arr) else []
            cen.append(np.median(m) if len(m) else np.nan)
        cen = np.array(cen); ok = ~np.isnan(cen)
        e = np.interp(Fs, Fs[ok], cen[ok])
        # remove label text: drop points far from a running median, then enforce a non-increasing curve (pool adjacent violators)
        med = np.array([np.median(e[max(0, i - 4):i + 5]) for i in range(len(e))])
        keep = ok & (np.abs(cen - med) < 0.10)
        e = np.interp(Fs, Fs[keep], cen[keep])
        blocks = [[x] for x in e]
        i = 0
        while i < len(blocks) - 1:
            if np.mean(blocks[i]) < np.mean(blocks[i + 1]):
                blocks[i] += blocks.pop(i + 1); i = max(i - 1, 0)
            else: i += 1
        e = np.concatenate([[np.mean(b_)] * len(b_) for b_ in blocks])
        ok = keep
        res[name] = dict(plateau=round(p, 3), F=Fs.tolist(), EI=[round(float(x), 3) for x in e], coverage=round(float(ok.mean()), 2))
        print(name, 'plateau %.2f' % p, 'bins with data %.0f%%' % (100 * ok.mean()), ' '.join('%g:%.2f' % (F, x) for F, x in zip(Fs, e) if F % 5 == 0 or F == 12.5))
res['axis'] = dict(X0=X0, DX=DX, Y0=Y0, DY=DY); res['reading_uncertainty_MNm2'] = 0.05
json.dump(res, open('fig22_digitised.json', 'w'), indent=1)
im = Image.open(src).convert('RGB'); d = ImageDraw.Draw(im)
for k, col in (('dyn_BI2', (255, 0, 0)), ('dyn_BI1', (0, 160, 0)), ('sta_BI2', (0, 0, 255)), ('sta_BI1', (255, 140, 0))):
    for F, e in zip(res[k]['F'], res[k]['EI']):
        x, y = px(F), Y0 - e * DY; d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=col, width=2)
im.save('fig22_overlay.png')

# ---- static curves: label text and the solid strengthened lines cross them, so they were read from the per-column pixel
# line centres (listed by grey_columns below) at chosen loads; values are line centres in MN m2
STATIC = {'sta_BI2': {12.5: 4.06, 13: 3.92, 14: 3.68, 15: 3.49, 16: 3.36, 17: 3.24, 17.5: 3.19, 18: 3.14, 19: 3.06, 20: 3.00, 21: 2.94,
                      22.5: 2.86, 24: 2.79, 25: 2.74, 26: 2.72, 27.5: 2.67, 30: 2.59, 32.5: 2.54, 35: 2.51, 37.5: 2.51, 40: 2.50, 42.5: 2.42, 44.5: 2.38},
          'sta_BI1': {12.5: 3.76, 13: 3.57, 14: 3.34, 15: 3.13, 16: 2.95, 17: 2.83, 17.5: 2.78, 18: 2.75, 19: 2.64, 20: 2.57, 21: 2.49,
                      22.5: 2.43, 24: 2.37, 25: 2.33, 26: 2.30, 27.5: 2.28, 30: 2.20, 32.5: 2.15, 35: 2.10, 37.5: 2.06, 40: 2.03, 42.5: 2.00, 44.5: 2.00}}
for k, d in STATIC.items():
    Fk = np.array(sorted(d)); res[k]['EI'] = [round(float(x), 3) for x in np.interp(Fs, Fk, [d[f] for f in Fk])]; res[k]['read_points'] = {str(f): d[f] for f in Fk}
json.dump(res, open('fig22_digitised.json', 'w'), indent=1)
im = Image.open(src).convert('RGB'); d = ImageDraw.Draw(im)
for k, col in (('dyn_BI2', (255, 0, 0)), ('dyn_BI1', (0, 160, 0)), ('sta_BI2', (0, 0, 255)), ('sta_BI1', (255, 140, 0))):
    for F, e in zip(res[k]['F'], res[k]['EI']):
        x, y = px(F), Y0 - e * DY; d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=col, width=2)
im.save('fig22_overlay.png')
print('final', {k: [res[k]['EI'][i] for i in (0, 6, 16, 36, 65)] for k in ('dyn_BI2', 'dyn_BI1', 'sta_BI2', 'sta_BI1')})
