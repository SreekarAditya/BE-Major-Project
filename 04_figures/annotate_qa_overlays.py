"""Adds a legend and description band under each digitisation-check overlay (originals kept in _not_for_review/raw_overlays_before_annotation)."""
from PIL import Image, ImageDraw, ImageFont
import os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
RAW = os.path.join(os.path.dirname(ROOT), '_not_for_review', 'raw_overlays_before_annotation')
def font(sz, bold=False):
    for p in ('/usr/share/fonts/truetype/crosextra/Carlito-%s.ttf' % ('Bold' if bold else 'Regular'),):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
def annotate(src, dst, title, items, notes):
    im = Image.open(src).convert('RGB'); W, H = im.size; s = W / 2000
    f1, f2 = font(int(40 * s), True), font(int(34 * s)); lh = int(48 * s)
    band = int((90 + 52 * (len(items) + len(notes))) * s) + lh
    out = Image.new('RGB', (W, H + band), 'white'); out.paste(im, (0, 0)); d = ImageDraw.Draw(out)
    x0, y = int(40 * s), H + int(30 * s)
    d.text((x0, y), title, font=f1, fill=(34, 34, 34)); y += int(64 * s)
    for col, label in items:
        r = int(11 * s); cy = y + int(20 * s)
        d.ellipse((x0 + int(6 * s) - r, cy - r, x0 + int(6 * s) + r, cy + r), outline=col, width=max(2, int(4 * s)))
        d.text((x0 + int(36 * s), y), label, font=f2, fill=(34, 34, 34)); y += int(52 * s)
    for n in notes:
        d.text((x0, y), n, font=f2, fill=(110, 110, 110)); y += int(52 * s)
    out.save(dst)
P = os.path.join(ROOT, '07_uncertainty_and_validation', 'published_test', 'fig22_overlay.png')
annotate(os.path.join(RAW, 'fig22_overlay.png'), P,
  'Digitisation check: Musial, Trapko and Grosel (2021), Materials 14, 910, Figure 22 (CC BY 4.0)',
  [((255, 0, 0), 'Points read by our script: vibration stiffness, beam B-I-2'), ((0, 160, 0), 'Points read by our script: vibration stiffness, beam B-I-1'),
   ((0, 0, 255), 'Points read by our script: static stiffness, beam B-I-2'), ((255, 140, 0), 'Points read by our script: static stiffness, beam B-I-1')],
  ['Black curves: published vibration stiffness; grey curves: published static stiffness. Reading uncertainty about 0.05 MN m2.'])
for n, fig, what in (('figure4', 'Figure 4', 'Beams strengthened before damage.'), ('figure7', 'Figure 7', 'Beams strengthened after damage level D1.')):
    annotate(os.path.join(RAW, n + '_overlay.png'), os.path.join(ROOT, '08_benchmark_ozturkoglu2024', n + '_overlay.png'),
      'Digitisation check: Ozturkoglu et al. (2024), Applied Sciences 14, 9920, ' + fig + ' (CC BY 4.0)',
      [((142, 27, 46), 'D1 to D4: loading-plateau points read by our script at each damage level')],
      [what + ' Points give the static secant stiffness; reading bounds about 1 kN and 0.5 mm.'])
print('annotated 3 overlays')
