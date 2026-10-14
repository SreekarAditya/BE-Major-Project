from pathlib import Path
import runpy
C=runpy.run_path(str(Path(__file__).with_name('common.py')));globals().update(C)
H=read('h2_results.json');R=H['rows'];s=np.array([r['static_left'] for r in R]);d=np.array([r['dynamic_left'] for r in R]);A=np.load(ROOT/'reading_samples.npz');ss=A['static'];dd=A['dynamic']
rows=[];errors={'bias':[],'hold':[],'vibration':[]};sampleerrors={k:[] for k in errors}
for i in range(1,len(R)):
    if R[i]['step'] != R[i-1]['step'] + 1: continue
    b=float(np.log(d[i-1]/s[i-1]));pred={'bias':d[i]*np.exp(-b),'hold':s[i-1],'vibration':d[i]}
    # Static undamaged baseline unavailable. The requested vibration-no-bias comparison
    # assumes earliest-readable static reference corresponds to f0, explicitly conditional.
    sp={'bias':dd[:,i]*ss[:,i-1]/dd[:,i-1],'hold':ss[:,i-1],'vibration':dd[:,i]}
    errs={k:100*(s[i]/v-1) for k,v in pred.items()};bounds={}
    for k in pred:
        e=100*(ss[:,i]/sp[k]-1);sampleerrors[k].append(e);errors[k].append(errs[k]);bounds[k]=np.percentile(e,[2.5,97.5]).tolist()
    rows.append({'beam':3,'previous_step':R[i-1]['step'],'step':R[i]['step'],'load_kN':R[i]['table_load_kN'],'bias_log_ratio_previous':b,'predicted_static_left':{k:float(v) for k,v in pred.items()},'signed_deflection_error_pct':{k:float(v) for k,v in errs.items()},'reading_interval_95_signed_error_pct':bounds})
agg={}
for k,e in errors.items():
    a=np.stack(sampleerrors[k],axis=1);agg[k]=dict(summary(e),median_abs_reading_interval_95=np.percentile(np.median(np.abs(a),axis=1),[2.5,97.5]).tolist(),max_abs_reading_interval_95=np.percentile(np.max(np.abs(a),axis=1),[2.5,97.5]).tolist())
save('twin_results.json',{'status':'PARTIAL_CONDITIONAL_CONSECUTIVE_TRANSITIONS','n':len(rows),'rows':rows,'pooled':agg,'per_beam':{'3':agg},
'formula':'b_previous = ln(dynamic_previous/static_previous); static_predicted = dynamic_current exp(-b_previous); deflection error = 100(static_true/static_predicted - 1)',
'baselines':{'hold':'Previous measured static secant','vibration':'Dynamic ratio referenced to initial f0, taken as static ratio; conditional because initial static baseline is missing.'},
'scope':'Ten consecutive published load-step transitions in one beam, no predictions across unreadable or excluded cycles. Predicts peak total-deflection secant, not elastic reloading stiffness or prospective independent validation.',
'uncertainty':'20,000 uniform bounded reading samples, retaining shared baseline and previous/current reuse; intervals are sensitivity intervals, not statistical confidence.',
'load_gap':'Variable consecutive load steps. Musial reference uses 5 kN gaps, so errors are not a common-horizon pooled accuracy estimate.'})
print({k:summary(v) for k,v in errors.items()})
