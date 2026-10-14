from pathlib import Path
import runpy,json,hashlib
C=runpy.run_path(str(Path(__file__).with_name('common.py')));globals().update(C)
M=json.loads((REF/'real_evidence.json').read_text());T=json.loads((REF/'twin_on_test.json').read_text());H=read('h2_results.json');P=read('twin_results.json');rng=np.random.default_rng(SEED)
clusters=[]
for key in ['BI1','BI2']:
    s=np.array(M[key]['static_left']);d=np.array(M[key]['dynamic_left']);clusters.append((float((1-s)@(1-d)),float((1-s)@(1-s))))
a=np.array(clusters);idx=rng.integers(0,2,(20000,2));z=a[idx].sum(axis=1);ci=np.percentile(z[:,0]/z[:,1],[2.5,97.5]).tolist()
rows=[{'series':'Musiał et al. (2021)','paper_beams':2,'paired_beams':2,'kappa':M['kappa_static_left'],'kappa_95_interval':ci,'interval_kind':'Beam bootstrap recreated from supplied raw ratios, 2 clusters; narrow coverage cannot establish population uncertainty.',
'kappa_corrected_sensitivity':M['kappa_static_left_corrected'],'twin_bias_median_pct':T['gap_5_kN']['median_abs']['err_bias_learning'],'twin_hold_median_pct':T['gap_5_kN']['median_abs']['err_no_update'],'twin_vibration_median_pct':T['gap_5_kN']['median_abs']['err_vibration_no_bias'],
'n_predictions':T['gap_5_kN']['n'],'definition':'Published static secant ratios and vibration ratios, raw static reference; 5 kN prediction gaps; source supplied by workspace.'},
{'series':'Pešić et al. (2015)','paper_beams':5,'paired_beams':1,'kappa':H['kappa'],'kappa_95_interval':None,'interval_kind':'Unavailable: 1 beam cluster; reading sensitivity reported separately.',
'kappa_reading_interval_95':H['kappa_reading_interval_95'],'twin_bias_median_pct':P['pooled']['bias']['median_abs_pct'],'twin_hold_median_pct':P['pooled']['hold']['median_abs_pct'],'twin_vibration_median_pct':P['pooled']['vibration']['median_abs_pct'],'n_predictions':P['n'],
'definition':'Conditional: static normalised to earliest readable damaged state, dynamic to initial state; peak total-deflection secant, variable consecutive load gaps.'}]
b1=ROOT.parent/'08_benchmark_ozturkoglu2024/results_summary.json'
if b1.exists():
    O=json.loads(b1.read_text()); rows.append({'series':'Ozturkoglu et al. (2024)','paper_beams':O['number_of_beams'],'paired_beams':O['number_of_beams'],'kappa':O['kappa'],'kappa_95_interval':O['kappa_95_interval'],'interval_kind':'Beam bootstrap, 4 clusters; source Job B1.',
    'twin_bias_median_pct':O['twin_median_error_bias_pct'],'twin_hold_median_pct':O['twin_median_error_hold_pct'],'twin_vibration_median_pct':O['twin_median_error_vibration_pct'],'n_predictions':O['twin_predictions'],'definition':O['kappa_definition']+' '+O['twin_scope'],'directly_poolable_with_service_stiffness':False})
sourcefiles=[REF/'real_evidence.json',REF/'twin_on_test.json',b1]
save('pooled_results.json',{'series':rows,'combined_kappa':None,'combined_twin_accuracy':None,'reason':'Series differ in baseline, static measurement definition, support/mass state and prediction horizon. A combined number would conceal these differences.',
'musial_bootstrap':{'draws':20000,'seed':SEED,'clusters':2,'unit':'beam'},'read_only_source_hashes':{str(q):hashlib.sha256(q.read_bytes()).hexdigest() for q in sourcefiles if q.exists()}})
