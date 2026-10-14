from pathlib import Path
import json, numpy as np
ROOT=Path(__file__).resolve().parent
REF=ROOT.parent/'07_uncertainty_and_validation/published_test'
def read(name): return json.loads((ROOT/name).read_text())
def save(name,obj): (ROOT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def fit(s,d):
    x=1-np.asarray(s); y=1-np.asarray(d)
    return float(x@y/(x@x))
def summary(v): return {'median_abs_pct':float(np.median(np.abs(v))),'max_abs_pct':float(np.max(np.abs(v)))}
def v(value,source,**kw): return dict(value=value,source=source,**kw)
SEED=201507037
