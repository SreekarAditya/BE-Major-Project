"""Rerun Monte Carlo beam 56 (same random inputs, seed 1056), which did not converge in mc.py.
Only the solver is made more patient: smaller displacement steps and deeper sub-stepping. Model and inputs unchanged."""
import json, time, sys, numpy as np, openseespy.opensees as ops
import mc
DU = float(sys.argv[1]) if len(sys.argv) > 1 else 0.02
def step(du, depth=0):
    if mc._try(du) == 0: return 0
    if depth >= 3: return -1
    ops.test('NormDispIncr', 1e-6, 300)
    for _ in range(10):
        if step(du / 10, depth + 1) != 0:
            ops.test('NormDispIncr', 1e-8, 100); return -1
    ops.test('NormDispIncr', 1e-8, 100); return 0
mc.step = step
ITER = int(sys.argv[2]) if len(sys.argv) > 2 else 10
_el = ops.element
def element(*a):
    if a[0] == 'forceBeamColumn' and ITER > 10: a = a + ('-iter', ITER, 1e-12)
    return _el(*a)
ops.element = element          # more internal iterations of the force-based element (default 10); model unchanged
_load_to = mc.load_to
def load_to(Pt, du=DU):
    P = []; D = []
    while True:
        if step(-du) != 0: raise RuntimeError(f'nonconvergence at P = {mc.state()[0]:.2f} kN, target {Pt}')
        p, d = mc.state(); P.append(p); D.append(d)
        if p >= Pt: return np.array(P), np.array(D)
        if len(P) > 40000: raise RuntimeError('target load not reached')
mc.load_to = load_to
def unload(du=DU):
    while ops.getLoadFactor(1) > 0.02e3:
        if step(du) != 0: break
mc.unload = unload
i = int(sys.argv[3]) if len(sys.argv) > 3 else 56; q = mc.draw(np.random.default_rng(1000 + i)); print(q)
t = time.time()
try:
    rows, Pmax = mc.run(q); rec = dict(i=i, ok=True, q=q, rows=rows, Pmax=Pmax, solver=f'step {DU} mm, sub-stepping to 1/1000, element iterations {ITER}')
except Exception as e:
    rec = dict(i=i, ok=False, q=q, err=str(e))
rec['sec'] = round(time.time() - t, 1); print(json.dumps(rec)[:1500])
open(f'mc_rerun{i}_{DU}_{ITER}.json', 'w').write(json.dumps(rec))
