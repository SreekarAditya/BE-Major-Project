"""H1/H2 and previous-check bias learning on digitised secant proxies.

Every beam-step remains, including counterexamples. Bootstrap resamples beams,
not individual steps. Ratios are not converted to calibrated elastic moduli.
"""
from pathlib import Path
import json
import numpy as np
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_text())
def dump(n,x):(HERE/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def fit(rows,mode=1):
    x=np.array([1-r['static_left'] for r in rows]);y=np.array([1-r[f'vibration_mode{mode}_left'] for r in rows])
    return float(np.dot(x,y)/np.dot(x,x))
def main():
    D=read('ozturkoglu_extract.json'); S=read('digitised_static.json'); rows=[]
    for r in S['rows']:
        beam=r['beam']; state=r['stage']+('_bare' if 'Post' in beam and r['stage']=='D1' else '')
        ratios=D['modal'][beam]['frequency_ratios'][state]['vertical']['value']
        init=S['initial_static_stiffness'][beam]; P0,d0=init['P_kN'],init['delta_mm']; K0=init['K0_kN_mm']
        P,dlt=r['load_kN'],r['displacement_mm']; uP,ud=r['reading_uncertainty_load_kN'],r['reading_uncertainty_displacement_mm']
        K=P/dlt; s=K/K0
        # Conservative reading bounds, including +/-1 kN and +/-0.5 mm on
        # the baseline proxy. These bounds are not a confidence interval.
        s_low=(P-uP)/(dlt+ud)/((P0+uP)/(d0-ud))
        s_high=(P+uP)/(dlt-ud)/((P0-uP)/(d0+ud))
        row=dict(beam=beam,stage=r['stage'],condition=r['condition'],displacement_mm=dlt,load_kN=P,K_secant_kN_mm=K,K0_first_crack_kN_mm=K0,static_left=s,static_left_reading_bounds=[s_low,s_high],vibration_mode1_left=ratios[0]**2,vibration_mode2_left=ratios[1]**2,vibration_frequency_ratios=ratios[:2],vibration_mode1_rounding_bounds=[(ratios[0]-.0005)**2,(ratios[0]+.0005)**2],source_static=r['source'],source_modal=D['modal'][beam]['frequency_ratios'][state]['vertical']['source'],static_definition='Load/displacement envelope secant divided by first-crack secant; retains plastic displacement.')
        row['H2_mode1_vibration_larger']=bool(row['vibration_mode1_left']>s)
        row['H2_mode2_vibration_larger']=bool(row['vibration_mode2_left']>s)
        rows.append(row)
    beams=list(D['modal']); rng=np.random.default_rng(20241030); B=20000
    bybeam={b:[r for r in rows if r['beam']==b] for b in beams}
    boot={1:[],2:[]}
    for _ in range(B):
        sample=[r for b in rng.choice(beams,len(beams),replace=True) for r in bybeam[b]]
        for mode in [1,2]:boot[mode].append(fit(sample,mode))
    fits={}
    for mode in [1,2]:
        # Source-reading sensitivity varies static ratios within conservative
        # bounds. It is distinct from between-beam bootstrap uncertainty.
        bs=[]
        for side in [0,1]:
            altered=[dict(r,static_left=r['static_left_reading_bounds'][side]) for r in rows];bs.append(fit(altered,mode))
        fits[f'mode{mode}']=dict(pooled=fit(rows,mode),bootstrap_95_interval=np.quantile(boot[mode],[.025,.975]).tolist(),bootstrap_unit='beam',bootstrap_draws=B,bootstrap_seed=20241030,n_beams=len(beams),n_beam_steps=len(rows),per_beam={b:dict(kappa=fit(rr,mode),n_steps=len(rr)) for b,rr in bybeam.items()},source_reading_extremes=bs,source_reading_note='All static ratios simultaneously assigned low/high reading bounds; sensitivity check, not a complete stochastic measurement-error model.',fitting_formula='sum(static_loss*vibration_loss)/sum(static_loss^2)')
    # Beam steps are dependent. Report counts, no invalid independent-step
    # significance claim; four specimens cannot establish population effects.
    counts={f'mode{m}':dict(vibration_larger=sum(r[f'H2_mode{m}_vibration_larger'] for r in rows),total=len(rows),counterexamples=[dict(beam=r['beam'],stage=r['stage'],static_left=r['static_left'],vibration_left=r[f'vibration_mode{m}_left']) for r in rows if not r[f'H2_mode{m}_vibration_larger']]) for m in [1,2]}
    h1=[r for r in rows if 'Post' in r['beam'] and r['stage']=='D1']
    H1=dict(status='PARTIAL_SAME_DISPLACEMENT_ONLY',rows=h1,vibration_mode1_spread_percentage_points=100*(max(r['vibration_mode1_left'] for r in h1)-min(r['vibration_mode1_left'] for r in h1)),static_secant_spread_percentage_points=100*(max(r['static_left'] for r in h1)-min(r['static_left'] for r in h1)),displacement_mm=h1[0]['displacement_mm'],load_kN=[r['load_kN'] for r in h1],explanation='Nominally identical bare beams differ at equal imposed displacement. D1 is not equal load; this is not an independent demonstration of equal-load H1. Individual initial frequencies are merged in Table 5.')
    # Preserve the previous-check b=ln(dynamic/static) formula, three baselines
    # and deflection error exactly. No parameter fitting to target stages.
    twin={}
    for gap in [1,2]:
        pred=[]
        for beam,rr in bybeam.items():
            # Require >=3 matched levels in the SAME structural condition.
            series=[r for r in rr if r['condition']=='strengthened']
            if len(series)<3:continue
            for i in range(gap,len(series)):
                prev,cur=series[i-gap],series[i]
                sp,dp=prev['static_left'],prev['vibration_mode1_left']; s,dd=cur['static_left'],cur['vibration_mode1_left']
                bias=np.log(dp/sp); p_bias=dd*np.exp(-bias); p_hold=sp; p_vib=dd
                errs={name:100*(s/p-1) for name,p in [('bias_learning',p_bias),('hold_last_check',p_hold),('vibration_no_bias',p_vib)]}
                # Reading sensitivity: evaluate all 8 corners of current and
                # previous static bounds and previous/current vibration
                # rounding. Retain error bounds without statistical labels.
                ranges={name:[] for name in errs}
                for sc in cur['static_left_reading_bounds']:
                  for spp in prev['static_left_reading_bounds']:
                    for dcc in cur['vibration_mode1_rounding_bounds']:
                      for dpp in prev['vibration_mode1_rounding_bounds']:
                        ranges['bias_learning'].append(100*(sc/(dcc*spp/dpp)-1))
                        ranges['hold_last_check'].append(100*(sc/spp-1))
                        ranges['vibration_no_bias'].append(100*(sc/dcc-1))
                pred.append(dict(beam=beam,current_stage=cur['stage'],previous_stage=prev['stage'],learned_log_bias=float(bias),static_true=s,predicted_static_bias=float(p_bias),predicted_static_hold=p_hold,predicted_static_vibration=p_vib,error_deflection_pct=errs,error_reading_bounds_pct={k:[min(v),max(v)] for k,v in ranges.items()}))
        keys=['bias_learning','hold_last_check','vibration_no_bias']
        def stats(rr):return dict(n_predictions=len(rr),median_abs_error_pct={k:float(np.median([abs(r['error_deflection_pct'][k]) for r in rr])) for k in keys},max_abs_error_pct={k:float(np.max([abs(r['error_deflection_pct'][k]) for r in rr])) for k in keys})
        twin[f'gap_{gap}_damage_levels']=dict(rows=pred,pooled=stats(pred),per_beam={b:stats([r for r in pred if r['beam']==b]) for b in beams if any(r['beam']==b for r in pred)},scope='Predict next envelope secant, not independently measured service deflection.',procedure='Same algebra and error formula as twin_on_test.py. Damage-level intervals replace that test series load gaps because these tests are displacement controlled. No predictions across the retrofit intervention. First-crack secant is the baseline for the vibration-without-bias comparison.')
    mus=read('reference_snapshot/real_evidence.json')
    out=dict(status='COMPLETED_SECANT_PROXY_ONLY',rows=rows,H1=H1,H2=dict(fits=fits,counts=counts,Musial_reference=dict(kappa_raw=mus['kappa_static_left'],kappa_compliance_corrected=mus['kappa_static_left_corrected'],source='reference_snapshot/real_evidence.json'),conclusion='Most steps show vibration ratio larger than the envelope secant ratio, but counterexamples are kept. Different stiffness definitions and yielded loading prevent an unqualified elastic/service-stiffness validation.'),twin=twin,reloading_stiffness=dict(status='SKIPPED_UNRELIABLE_BRANCH_ASSOCIATION',reason='Color curves contain overlapping unlabeled cyclic loading, unloading and repaired branches; retained attempted pixel reads are not sufficient to establish reloading tangent after each modal test.'),excluded_modal_only_states=[dict(beam=b,state='D1_strengthened',reason='Frequency measured before resumed loading; no matching static stiffness check at that instant.') for b in beams if 'Post' in b],limitations=['Secant to plastic displacement compared with unloaded vibration at residual deformation; not the same physical stiffness measure.','First-crack secant baseline is a proxy; support/jack compliance not independently resolved.','Bootstrap has only four beam clusters, with unequal counts and different strengthening histories; interval does not cover missing coupon data or stiffness-definition bias.','Frequency-squared is an apparent stiffness index; mass, boundary conditions and mode shape changes are not independently corrected.','Twin calculations use consecutive peak secants and do not validate service-deflection accuracy or an absolute frequency-to-modulus conversion.'])
    dump('h1_h2_results.json',out);dump('twin_on_ozturkoglu_results.json',dict(twin=twin,status=out['status'],limitations=out['limitations']))
    print('Kappa mode 1',fits['mode1']['pooled'],'CI',fits['mode1']['bootstrap_95_interval'],'H2',counts['mode1'])
    print('Twin',twin['gap_1_damage_levels']['pooled'])

if __name__=='__main__':main()
