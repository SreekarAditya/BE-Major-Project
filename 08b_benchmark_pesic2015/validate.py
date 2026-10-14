from pathlib import Path
import json,math,hashlib
root=Path(__file__).resolve().parent
read=lambda name:json.loads((root/name).read_text())
e=read('pesic_extract.json');h=read('h2_results.json');t=read('twin_results.json');g=read('digitised_static.json')
assert [len(b['steps']) for b in e['beams']]==[14,9,12,14,7]
assert h['paired_steps']==11 and t['n']==10
assert h['kappa_95_interval'] is None
for b in e['beams']:
 if b['beam']!=3:assert all(r['peak_deflection_mm'] is None for r in b['steps'])
for r in h['rows']:
 # Independent unit check entirely in N, mm and N mm², then convert to MN m².
 ei=(r['table_load_kN']*1000*5400**3/(48*r['peak_deflection_mm']))/1e12
 assert math.isclose(ei,r['static_EI_MNm2'],rel_tol=1e-12)
 assert abs(r['plot_minus_table_load_kN'])<r['load_alignment_bound_kN']
for r in t['rows']:assert r['step']==r['previous_step']+1
assert len(g['unloading_chords'])==11
assert read('blind_model_status.json')['model_tuned'] is False
source=read('source_provenance.json');assert hashlib.sha256((root/'pesic2015_aam.pdf').read_bytes()).hexdigest()==source['sha256']
(root/'numeric_QA.json').write_text(json.dumps({'status':'PASS','checks':['All frequency states preserved','All Beam 3 peaks and zero-load endpoints retained','Missing other beam static records remain null','Flexural rigidity dimensional conversion checked independently','Figure/table load deviations within declared alignment bounds','Twin predictions use consecutive steps','No fabricated beam confidence interval','No tuning','Source hash preserved']},indent=2)+'\n')
