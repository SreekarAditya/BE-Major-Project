"""Independent QA of Figure 11 chronological path; does not substitute for pixel picks.
Uses bundled pdfplumber, run with isolated Python. Saves original ordered path.
"""
from pathlib import Path
import json,pdfplumber
root=Path(__file__).resolve().parent
with pdfplumber.open(root/'pesic2015_aam.pdf') as doc:
    cs=[c for c in doc.pages[8].curves if c['top']>290 and c['bottom']<445 and c['stroking_color'] and tuple(c['stroking_color'])==(0,0,1)]
(root/'vector_trace_check.json').write_text(json.dumps(cs,default=str,indent=2)+'\n')
