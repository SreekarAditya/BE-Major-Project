"""Parallel runner for the two follow-on jobs. Safe to stop and restart: finished work is skipped.

  python3 run_jobs.py retrofit     -> retrofit by mechanics, beams 0-999, schemes none/laminate/plate/jacket
                                      output ../raw_retrofit/part_XX.jsonl
  python3 run_jobs.py continuum    -> continuum cross-check, 48 stratified beams (+ reference specimen)
                                      output ../raw_continuum/part_XX.jsonl
"""
import os, sys, json, glob, time, csv
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
DESIGN = os.path.join(ROOT, 'data', 'design.csv')
RETROFIT_BEAMS = list(range(1000))
SCHEMES = ('none', 'laminate', 'plate', 'jacket')


def continuum_beams():
    """4 beams in each of 12 cells: span (2-3.33, 3.33-4.67, 4.67-6 m) x depth (<=400, >400 mm) x load arrangement,
    taking the lowest beam numbers in each cell (the design is already in random order)."""
    rows = list(csv.DictReader(open(DESIGN))); cells = {}
    for r in rows:
        L, h = float(r['span_mm']), float(r['h_mm'])
        key = (min(int((L - 2000) // (4000 / 3)), 2), int(h > 400), r['load'])
        cells.setdefault(key, [])
        if len(cells[key]) < 4: cells[key].append(int(r['beam']))
    return sorted(i for v in cells.values() for i in v)


def done(folder, keyfn):
    s = set()
    for fn in glob.glob(os.path.join(folder, '*.jsonl')):
        for line in open(fn):
            try: s.add(keyfn(json.loads(line)))
            except Exception: pass
    return s


def w_retrofit(args):
    wid, items, out = args
    sys.path.insert(0, HERE); import gen, retrofit_mech as rm
    rows = {int(r['beam']): r for r in csv.DictReader(open(DESIGN))}
    with open(os.path.join(out, 'part_%02d.jsonl' % wid), 'a') as fh:
        for i, scheme in items:
            row = rows[i]; g = gen.geometry(row)
            q = dict(fck=float(row['fck_MPa']), Ec=float(row['Ec_MPa']), ft=float(row['ft_MPa']), ets=float(row['ets']), fy=float(row['fy_MPa']))
            Py = float(row['Py_hand_kN']); fr = [float(x) for x in row['stage_fractions'].split(';')]
            t = time.time()
            try: rec = dict(beam=i, ok=True, **rm.run_retrofit(g, q, 0.185 * Py, 0.37 * Py, [f * Py for f in fr], g['span'] / 100, scheme))
            except Exception as e: rec = dict(beam=i, scheme=scheme, ok=False, err=str(e))
            rec['sec'] = round(time.time() - t, 1); fh.write(json.dumps(rec) + '\n'); fh.flush()
    return wid


def w_continuum(args):
    wid, items, out = args
    sys.path.insert(0, HERE); import cont_gen
    rows = {int(r['beam']): r for r in csv.DictReader(open(DESIGN))}
    with open(os.path.join(out, 'part_%02d.jsonl' % wid), 'a') as fh:
        for i in items:
            t = time.time()
            try: rec = dict(beam=i, ok=True, **cont_gen.run(rows[i]))
            except Exception as e: rec = dict(beam=i, ok=False, err=str(e))
            rec['sec'] = round(time.time() - t, 1); fh.write(json.dumps(rec) + '\n'); fh.flush()
    return wid


if __name__ == '__main__':
    job = sys.argv[1]; n = max(1, (os.cpu_count() or 2) - 1)
    if job == 'retrofit':
        out = os.path.join(ROOT, 'raw_retrofit'); os.makedirs(out, exist_ok=True)
        fin = done(out, lambda r: (r['beam'], r['scheme']))
        todo = [(i, s) for i in RETROFIT_BEAMS for s in SCHEMES if (i, s) not in fin]; fn = w_retrofit
    else:
        out = os.path.join(ROOT, 'raw_continuum'); os.makedirs(out, exist_ok=True)
        fin = done(out, lambda r: r['beam'])
        todo = [i for i in continuum_beams() if i not in fin]; fn = w_continuum
    print('%s: %d items on %d cores' % (job, len(todo), n), flush=True)
    with Pool(n) as p:
        for w in p.imap_unordered(fn, [(w, todo[w::n], out) for w in range(n)]): print('worker %d finished' % w, flush=True)
    print('all done', flush=True)
