"""Rerun all stages, verify protected inputs, preserve errors and seal manifest."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,datetime
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((HERE/n).read_text())
def write(n,d):(HERE/n).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def protected_check():
    before=read('protected_inputs_before.json')
    after={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and HERE not in p.parents}
    changed=[k for k in before if after.get(k)!=before[k]]
    added=[k for k in after if k not in before]
    return dict(protected_files=len(before),changed_or_missing=changed,added_outside_working_folder=added,pass_check=not changed and not added)
def main():
    begin=time.perf_counter();timings=[];logs=[];checks={}
    env=os.environ.copy();env['MPLCONFIGDIR']=str(HERE/'.mplconfig');env['PYTHONDONTWRITEBYTECODE']='1'
    stages=['extract.py','digitise.py','frp_check.py','h1_h2.py','retrofit_signal.py','figures.py','report.py']
    (HERE/'run_logs').mkdir(exist_ok=True)
    execution_id=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    try:
        checks['protected_before']=protected_check();assert checks['protected_before']['pass_check'],'Protected input changed before run'
        origin=Path('/Users/sreekaraditya/Downloads/applsci-14-09920.pdf')
        assert sha(HERE/'ozturkoglu2024_source.pdf')==read('source_freeze.json')['pdf_sha256'],'Source PDF differs from frozen input'
        if origin.exists():
            assert sha(HERE/'ozturkoglu2024_source.pdf')==sha(origin),'Source PDF differs from original'
        checks['source_pdf_integrity']=dict(frozen_hash_agrees=True,original_download_available=origin.exists())
        ref_frozen=read('source_freeze.json')['reference_hashes']
        changed_ref=[name for name,digest in ref_frozen.items() if sha(HERE/name)!=digest]
        checks['reference_snapshot_integrity']=dict(changed=changed_ref,pass_check=not changed_ref)
        assert not changed_ref,'Frozen reference snapshot changed'
        for stage in stages:
            t=time.perf_counter();r=subprocess.run([sys.executable,'-I',str(HERE/stage)],cwd=HERE,env=env,capture_output=True,text=True,timeout=600)
            elapsed=time.perf_counter()-t;timings.append(dict(script=stage,seconds=elapsed,returncode=r.returncode));logs.append(f'[{stage}]\n{r.stdout}{r.stderr}')
            print(stage,f'{elapsed:.2f}s',r.stdout.strip(),flush=True)
            assert r.returncode==0,stage+' failed: '+r.stderr
        # Numerical equilibrium quality is separate from model/test agreement.
        F=read('frp_results.json');H=read('h1_h2_results.json');D=read('ozturkoglu_extract.json');S=read('digitised_static.json')
        eq=max(r['ultimate']['equilibrium_relative_residual'] for r in F['strengthened'])
        checks['section_force_equilibrium']=dict(max_relative_residual=eq,acceptance_limit=.005,pass_check=eq<.005)
        assert checks['section_force_equilibrium']['pass_check'],'Neutral-axis equilibrium not resolved'
        checks['endpoint_digitisation']=dict(accepted_endpoints=len(S['rows']),excluded=S['exclusions'],expected_from_reported_states=11,pass_check=len(S['rows'])==11 and not S['exclusions'])
        assert checks['endpoint_digitisation']['pass_check'],'Incomplete endpoint digitisation'
        checks['text_visual_agreement']=dict(checked_values=D['read_audit']['table_numeric_values_checked'],status=read('source_read_audit.json')['status'])
        assert checks['text_visual_agreement']['status']=='AGREE'
        # Reproduce the frozen reference script in a private output folder,
        # independently of new specimen-specific capacities.
        qadir=HERE/'reference_replay';qadir.mkdir(exist_ok=True)
        rr=subprocess.run([sys.executable,'-I',str(HERE/'reference_snapshot/val_frp.py')],cwd=qadir,env=env,capture_output=True,text=True,timeout=600)
        assert rr.returncode==0,rr.stderr
        reference=read('reference_snapshot/musial_frp.json');replayed=read('reference_replay/musial_frp.json')
        delta=max(abs(reference[k]['P']-replayed[k]['P']) for k in ['unstrengthened','B-II-1','B-II-2'])
        checks['frozen_reference_replay']=dict(max_capacity_difference_kN=delta,pass_check=delta<1e-9)
        assert checks['frozen_reference_replay']['pass_check'],'Frozen capacity method regression'
        # Interventions must not be silently crossed by bias learning.
        no_intervention=all(r['previous_stage']!='D1' for group in H['twin'].values() for r in group['rows'] if 'Post' in r['beam'])
        checks['twin_intervention_boundary']=dict(pass_check=no_intervention)
        assert no_intervention,'Bias learning crossed retrofit intervention'
        from PIL import Image
        images=[]
        for fname in read('figure_settings.json')['files']:
            with Image.open(HERE/fname) as im:
                dpi=im.info.get('dpi',[0,0]);images.append(dict(file=fname,size=list(im.size),dpi=list(dpi),pass_check=all(abs(d-220)<.1 for d in dpi)))
        checks['figure_format']=images;assert all(r['pass_check'] for r in images)
        vr=read('visual_review.json') if (HERE/'visual_review.json').exists() else None
        if vr:
            valid=all(sha(HERE/r['file'])==r['sha256'] for r in vr['reviewed_files'])
            checks['visual_review_current']=dict(pass_check=valid,review_note=vr['note'])
            assert valid,'Latest outputs differ from visually reviewed images'
        else:checks['visual_review_current']=dict(pass_check=False,status='PENDING_MANUAL_IMAGE_INSPECTION')
        checks['protected_after']=protected_check();assert checks['protected_after']['pass_check'],'Protected inputs changed during run'
        total=time.perf_counter()-begin;assert total<600,'Whole rerun exceeds ten minutes'
        qa=dict(status='PASS_REPRODUCIBLE_WITH_SCIENTIFIC_LIMITATIONS',visual_status='PASS' if vr else 'PENDING',elapsed_seconds=total,run_id=execution_id,python=sys.executable,isolated_python=True,stages=timings,checks=checks,scientific_status=read('results_summary.json')['status'],no_tuning=True,limits='Successful QA means executable outputs and bookkeeping passed. It does not resolve the missing evidence or validate the service-deflection target.')
        write('QA.json',qa)
        (HERE/'run_logs'/f'{execution_id}_PASS.log').write_text('\n\n'.join(logs))
        excluded_dirs={'.venv','.mplconfig','__pycache__'}
        hashes={str(p.relative_to(HERE)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json' and not any(n in excluded_dirs for n in p.relative_to(HERE).parts)}
        write('manifest.json',dict(status=qa['status'],files=hashes,source_pdf_sha256=D['paper']['sha256'],original_source='/Users/sreekaraditya/Downloads/applsci-14-09920.pdf',excluded_rebuildable_environment_dirs=sorted(excluded_dirs),protected_workspace_unchanged=checks['protected_after']['pass_check']))
        print(f'PASS: {total:.2f}s, protected files unchanged, scientific limits retained.',flush=True)
    except Exception as e:
        failure=dict(status='FAIL',run_id=execution_id,error=repr(e),stages=timings,checks=checks,elapsed_seconds=time.perf_counter()-begin)
        write('QA.json',failure);write(f'run_logs/{execution_id}_FAIL.json',failure)
        (HERE/'run_logs'/f'{execution_id}_FAIL.log').write_text('\n\n'.join(logs))
        raise

if __name__=='__main__':main()
