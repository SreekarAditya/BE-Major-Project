from pathlib import Path
import runpy,math
C=runpy.run_path(str(Path(__file__).with_name('common.py')));globals().update(C)
E=read('pesic_extract.json');D=read('digitised_static.json');B=E['beams'][2];R=D['rows'];span=B['geometry']['span_m']['value']
p=np.array([r['table_load_kN'] for r in R]);u=np.array([r['peak_deflection_mm'] for r in R]);K=p/u
s=K/K[0]; f=np.array([B['steps'][r['step']]['frequency_mode1_Hz']['value'] for r in R]);f0=B['steps'][0]['frequency_mode1_Hz']['value'];d=(f/f0)**2;dm=(f/f[0])**2
rng=np.random.default_rng(SEED);N=20000
us=rng.uniform(u-np.array([r['deflection_reading_bound_mm'] for r in R]),u+np.array([r['deflection_reading_bound_mm'] for r in R]),(N,len(u)))
ps=rng.uniform(p-.03,p+.03,(N,len(p)));ks=ps/us; ss=ks/ks[:,[0]]
fs=rng.uniform(f-.005,f+.005,(N,len(f)));f0s=rng.uniform(f0-.005,f0+.005,(N,1));ds=(fs/f0s)**2;dms=(fs/fs[:,[0]])**2
x=1-ss; bootread=np.sum(x*(1-ds),axis=1)/np.sum(x*x,axis=1);matchedread=np.sum(x*(1-dms),axis=1)/np.sum(x*x,axis=1)
rows=[]
for i,r in enumerate(R):
    rows.append(dict(r,static_secant_kN_per_mm=float(K[i]),static_EI_MNm2=float(K[i]*1e6*span**3/48/1e6),static_left=float(s[i]),dynamic_left=float(d[i]),dynamic_matched_reference_left=float(dm[i]),
    static_reading_interval_95=np.percentile(ss[:,i],[2.5,97.5]).tolist(),dynamic_reading_interval_95=np.percentile(ds[:,i],[2.5,97.5]).tolist()))
positive=int(np.sum(d>s)); negative=int(np.sum(d<s));n=positive+negative
sign=sum(math.comb(n,k) for k in range(positive,n+1))/2**n
k=fit(s,d);km=fit(s,dm)
unloading=D['unloading_chords']
save('h2_results.json',{'status':'PARTIAL_CONDITIONAL_BASELINE','available_static_beams':1,'paper_beams':5,'paired_steps':len(R),'rows':rows,
'static_definition':'Peak applied load / peak total deflection, normalised by earliest readable Beam 3 peak at step 1. This reference is already damaged and is not an uncracked stiffness.',
'dynamic_definition':'(mode 1 frequency / measured initial mode 1 frequency)^2; mode 2 states are retained in extraction.',
'kappa':k,'kappa_95_interval':None,'beam_bootstrap_raw_interval_95':[k,k],
'bootstrap':{'replicates':20000,'unit':'beam','clusters':1,'status':'DEGENERATE_ONE_CLUSTER_NOT_A_VALID_POPULATION_CONFIDENCE_INTERVAL','explanation':'Resampling a single available beam repeats identical data. No cross-beam interval can be estimated.'},
'kappa_reading_interval_95':np.percentile(bootread,[2.5,97.5]).tolist(),'matched_reference_sensitivity_kappa':km,'matched_reference_reading_interval_95':np.percentile(matchedread,[2.5,97.5]).tolist(),
'per_beam':{str(b['beam']):{'kappa':k if b['beam']==3 else None,'kappa_95_interval':None,'status':'Conditional paired history' if b['beam']==3 else 'Static records absent'} for b in E['beams']},'unloading_chords':unloading,'unloading_chord_conditional_kappa':fit(np.array([r['unloading_chord_kN_per_mm'] for r in unloading])/unloading[0]['unloading_chord_kN_per_mm'],d),'unloading_uncertainty_status':'First chord recovered deflection is small relative to combined reading bounds; a finite reliable normalisation interval is unavailable. Point slope is descriptive only.',
'sign_test_naive':{'positive':positive,'negative':negative,'n':n,'one_sided_p':sign,'alternative':'dynamic_left > static_left','limitation':'Repeated steps share one beam and a shared baseline; the binomial independence assumption fails.'},
'sign_test_beam_level':{'positive':int(np.median(d-s)>0),'n':1,'one_sided_p':.5},
'musial_comparison_range':[.31,.39],'comparability':'Conditional baseline mismatch, pre-existing damage and one available beam prevent a defensible direct calibration comparison.',
'all_beams_vibration_ratios':[{ 'beam':b['beam'],'states':[{'step':r['step'],'load_kN':r['load_kN']['value'],'mode1_left':(r['frequency_mode1_Hz']['value']/b['steps'][0]['frequency_mode1_Hz']['value'])**2,'mode2_left':(r['frequency_mode2_Hz']['value']/b['steps'][0]['frequency_mode2_Hz']['value'])**2,'source':'p. 19, Table 3'} for r in b['steps']]} for b in E['beams']], 'reading_propagation':{'draws':N,'seed':SEED,'distribution':'Uniform bounded reading sensitivity; include plot/table load alignment ±0.03 kN and shared baseline; not a measurement-error model or confidence interval.'}})
# Numeric samples for downstream uncertainty propagation; no pickle.
np.savez_compressed(ROOT/'reading_samples.npz',static=ss,dynamic=ds,dynamic_matched=dms)
print('Conditional kappa',k,'matched-reference sensitivity',km)
