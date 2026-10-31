import json, time, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen
ref = [json.loads(l) for l in open(os.path.join(HERE, '..', '..', '01_reference_specimen_monte_carlo', 'data', 'mc_raw_samples.jsonl'))]
g = gen.geometry(dict(span_mm=3000, b_mm=230, h_mm=300, cover_mm=25, d_stir_mm=8, n_bot=3, d_bot_mm=12, n_top=2, d_top_mm=10, grade_MPa=30, fy_nom_MPa=500, load='four_point'))
g['du'] = 0.02
print('hand yield', round(gen.hand_yield_load(g), 1))
for i in (0, 57, 210):
    r = ref[i]; t = time.time()
    rows, Pmax, env = gen.run(g, r['q'], 15.0, 30.0, (35., 50., 65., 72.), 25.0)
    dt = time.time() - t
    md = 0
    for a, b in zip(rows, r['rows']):
        for ka, kb in (('delta_d_mm', 'delta_d'), ('residual_mm', 'resid')):
            md = max(md, abs(a[ka] - b[kb]))
        md = max(md, abs(a['freq_hz'][0] - b['f']))
        if b['delta_s'] is not None: md = max(md, abs(a['delta_s_mm'] - b['delta_s']))
    print(f"beam {i}: max abs diff {md:.2e}; Pmax {Pmax:.3f} vs {r['Pmax']:.3f}; {dt:.1f}s; freqs {rows[-1]['freq_hz']}; crack@72 {rows[-1]['peak']['crack_w']:.3f} mm, steel {rows[-1]['peak']['steel_stress']:.0f} MPa, service crack {rows[-1]['service']['crack_w']:.3f}")
