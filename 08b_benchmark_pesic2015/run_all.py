from pathlib import Path
import subprocess,sys,time,json,os,hashlib
root=Path(__file__).resolve().parent
started=time.perf_counter();env=os.environ.copy();env['MPLCONFIGDIR']=str(root/'.mplconfig')
subprocess.run(['/Users/sreekaraditya/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3','-B','-I',str(root/'check_vector.py')],check=True,cwd=root)
for name in ['extract.py','digitise.py','h2.py','h1.py','twin_on_pesic.py','blind_model.py','pooled.py','figures.py','report.py','validate.py']:
    subprocess.run([sys.executable,'-B','-I',str(root/name)],check=True,cwd=root,env=env)
elapsed=time.perf_counter()-started
before=json.loads((root/'protected_before.json').read_text());workspace=root.parent.parent
changed=[name for name,h in before.items() if not (workspace/name).exists() or hashlib.sha256((workspace/name).read_bytes()).hexdigest()!=h]
after=set(str(p.relative_to(workspace)) for p in workspace.rglob('*') if p.is_file() and root not in p.parents)
new=sorted(after-set(before))
qa={'status':'PASS_REPRODUCIBLE_AVAILABLE_DATA_ONLY' if not changed and not new and elapsed<600 else 'FAIL',
'full_job_done':False,'unmet_scope':'Four static histories, cracking-normalised comparisons and a valid Pešić beam confidence interval unavailable.',
'elapsed_seconds':elapsed,'under_10_minutes':elapsed<600,'protected_existing_files':len(before),'protected_changed':changed,'outside_new_files':new,'visual_review':'PENDING'}
(root/'QA.json').write_text(json.dumps(qa,indent=2)+'\n')
receipt=json.loads((root/'retrieval_status.json').read_text());receipt['status']='RESUMED_WITH_USER_PROVIDED_PUBLISHED_PDF';receipt['pdf_available']=True;receipt['analysis_started']=True;(root/'retrieval_status.json').write_text(json.dumps(receipt,indent=2)+'\n')
files={str(p.relative_to(root)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and p.name!='MANIFEST.json'}
(root/'MANIFEST.json').write_text(json.dumps(files,indent=2)+'\n');print(json.dumps(qa,indent=2))
