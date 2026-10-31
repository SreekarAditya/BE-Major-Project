"""Run the beam population in parallel on all but one CPU core. Safe to stop and restart: finished beams are skipped.

Usage (from this folder):   python3 run_parallel.py            -> beams 0 to 8999
                            python3 run_parallel.py 0 10000    -> any range
Output: ../raw/part_XX.jsonl (one line per beam). Progress: python3 progress.py
"""
import os, sys, json, glob, time, csv
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, '..', 'raw')
DESIGN = os.path.join(HERE, '..', 'data', 'design.csv')


def done_beams():
    s = set()
    for fn in glob.glob(os.path.join(RAW, '*.jsonl')):
        for line in open(fn):
            try: s.add(json.loads(line)['beam'])
            except Exception: pass
    return s


def worker(args):
    wid, beams = args
    sys.path.insert(0, HERE)
    import gen
    rows = {int(r['beam']): r for r in csv.DictReader(open(DESIGN))}
    out = os.path.join(RAW, 'part_%02d.jsonl' % wid)
    with open(out, 'a') as fh:
        for i in beams:
            row = rows[i]; g = gen.geometry(row)
            q = dict(fck=float(row['fck_MPa']), Ec=float(row['Ec_MPa']), ft=float(row['ft_MPa']),
                     ets=float(row['ets']), fy=float(row['fy_MPa']))
            Py = float(row['Py_hand_kN']); fr = [float(x) for x in row['stage_fractions'].split(';')]
            t = time.time()
            try:
                st, Pmax, env = gen.run(g, q, 0.185 * Py, 0.37 * Py, [f * Py for f in fr], g['span'] / 100)
                rec = dict(beam=i, ok=True, stages=st, Pmax_kN=Pmax, envelope=env)
            except Exception as e:
                rec = dict(beam=i, ok=False, err=str(e))
            rec['sec'] = round(time.time() - t, 1)
            fh.write(json.dumps(rec) + '\n'); fh.flush()
    return wid


if __name__ == '__main__':
    i0 = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    i1 = int(sys.argv[2]) if len(sys.argv) > 2 else 9000
    os.makedirs(RAW, exist_ok=True)
    todo = [i for i in range(i0, i1) if i not in done_beams()]
    n = max(1, (os.cpu_count() or 2) - 1)
    print('%d beams to run on %d cores' % (len(todo), n), flush=True)
    chunks = [(w, todo[w::n]) for w in range(n)]
    with Pool(n) as p:
        for w in p.imap_unordered(worker, chunks): print('worker %d finished' % w, flush=True)
    print('all done', flush=True)
