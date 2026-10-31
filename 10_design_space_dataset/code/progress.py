"""Progress of the beam population run: beams finished, failures, time per beam, estimated time left."""
import os, glob, json, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
recs = []
for fn in glob.glob(os.path.join(HERE, '..', 'raw', '*.jsonl')):
    for line in open(fn):
        try: recs.append(json.loads(line))
        except Exception: pass
ok = [r for r in recs if r['ok']]
print('finished %d of 10000 | failed %d | median %.1f s per beam' % (
    len(recs), len(recs) - len(ok), statistics.median([r['sec'] for r in recs]) if recs else 0))
