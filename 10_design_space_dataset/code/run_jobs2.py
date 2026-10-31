"""Parallel runner for the condition stages. Safe to stop and restart: finished work is skipped.

  python3 run_jobs2.py corrosion   -> beams 0-1999, mass loss 5, 10, 15%           output ../raw_corrosion/part_<host>_XX.jsonl
  python3 run_jobs2.py sustained   -> beams 0-999, cases service and overload       output ../raw_sustained/part_<host>_XX.jsonl
  (beams 0-999 are also the retrofit beams, so they carry all conditions)

OpenSees writes solver warnings to the process's standard output; each worker sends them to /dev/null.
Optional third and fourth arguments set the beam range (first, last+1) instead of the default, so that pods can
share the work or the corrosion range can be extended (e.g. 2000 3000).
"""
import os, sys, json, glob, time, csv
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
DESIGN = os.path.join(ROOT, 'data', 'design.csv')
JOBS = dict(corrosion=dict(beams=range(2000), folder='raw_corrosion'),
            sustained=dict(beams=range(1000), folder='raw_sustained'))


def done(folder, keyfn):
    s = set()
    for fn in glob.glob(os.path.join(folder, '*.jsonl')):
        for line in open(fn):
            try: s.add(keyfn(json.loads(line)))
            except Exception: pass
    return s


def worker(args):
    job, wid, items, out = args
    fd = os.open(os.devnull, os.O_WRONLY); os.dup2(fd, 1); os.dup2(fd, 2)
    sys.path.insert(0, HERE)
    import corrosion, sustained
    rows = {int(r['beam']): r for r in csv.DictReader(open(DESIGN))}
    import socket
    with open(os.path.join(out, 'part_%s_%02d.jsonl' % (socket.gethostname(), wid)), 'a') as fh:
        for i, v in items:
            t = time.time()
            try:
                if job == 'corrosion': rec = dict(beam=i, ok=True, **corrosion.run_corrosion(rows[i], v))
                else: rec = dict(beam=i, ok=True, **sustained.run_sustained(rows[i], v))
            except Exception as e:
                rec = dict(beam=i, ok=False, err=str(e)); rec['psi' if job == 'corrosion' else 'case'] = v
            rec['sec'] = round(time.time() - t, 1); fh.write(json.dumps(rec) + '\n'); fh.flush()
    return wid


if __name__ == '__main__':
    job = sys.argv[1]; spec = JOBS[job]
    beams = list(spec['beams'])
    if len(sys.argv) >= 4: beams = list(range(int(sys.argv[2]), int(sys.argv[3])))
    n = max(1, (os.cpu_count() or 2) - 1)
    out = os.path.join(ROOT, spec['folder']); os.makedirs(out, exist_ok=True)
    sys.path.insert(0, HERE)
    if job == 'corrosion':
        import corrosion
        fin = done(out, lambda r: (r['beam'], r['psi'])); todo = [(i, p) for i in beams for p in corrosion.LEVELS if (i, p) not in fin]
    else:
        fin = done(out, lambda r: (r['beam'], r['case'])); todo = [(i, c) for i in beams for c in ('service', 'overload') if (i, c) not in fin]
    print('%s: %d items on %d cores' % (job, len(todo), n), flush=True)
    with Pool(n) as p:
        for w in p.imap_unordered(worker, [(job, w, todo[w::n], out) for w in range(n)]): print('worker %d finished' % w, flush=True)
    print('all done', flush=True)
