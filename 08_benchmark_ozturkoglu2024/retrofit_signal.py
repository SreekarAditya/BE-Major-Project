"""Frequency changes at D1 before and after retrofit, no intervening load test."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
def main():
    D=json.loads((HERE/'ozturkoglu_extract.json').read_text()); rows=[]; capacity_gain={}
    for beam in ['GFRP_PostStr','CFRP_PostStr']:
        modal=D['modal'][beam]; states=modal['frequency_ratios']
        for direction in ['vertical','horizontal']:
            before=states['D1_bare'][direction]['value'];after=states['D1_strengthened'][direction]['value'];f0=modal['f0_Hz'][direction]['value']
            for i,(b,a,z) in enumerate(zip(before,after,f0)):
                rows.append(dict(beam=beam,direction=direction,mode=i+1,f_ratio_before=b,f_ratio_after=a,frequency_change_pct=100*(a/b-1),frequency_change_rounding_bounds_pct=[100*((a-.0005)/(b+.0005)-1),100*((a+.0005)/(b-.0005)-1)],apparent_frequency_squared_change_pct=100*((a/b)**2-1),estimated_frequency_before_Hz=b*z,estimated_frequency_after_Hz=a*z,frequency_Hz_note='Multiplication by the merged Table 5 bare baseline is approximate for each individual post beam.',source=states['D1_bare'][direction]['source']))
        s=D['static'];bare=s[beam+'_bare']['ultimate_load_kN']['value'];after=s[beam+'_after']['ultimate_load_kN']['value']
        capacity_gain[beam]=dict(bare_observed_peak_kN=bare,strengthened_observed_peak_kN=after,gain_pct=100*(after/bare-1),source='p. 11, Table 4',note='Capacity gain is not static-stiffness gain. Peaks occur at different displacement/history; cannot substitute for an immediate static retrofit check.')
    out=dict(status='COMPLETED',rows=rows,static_capacity_gain=capacity_gain,static_stiffness_change_at_same_D1=dict(value=None,status='NOT_MEASURED',reason='Modal tests bracket strengthening at unchanged D1 history, but static loading resumes afterward. Figure 7 does not provide an immediate same-load diagnostic before and after bonding.'),Musial_context=dict(frequency_gain_pct=[1,4],static_stiffness_gain_pct=[20,30],source='Job B1 task statement and current review evidence context; approximate comparative ranges, not re-extracted in this job.'),implication='Frequency detects a direction- and mode-dependent change. It cannot by itself confirm recovery of static stiffness or load capacity. A matched static load/deflection check is required.',limitations=['Transport and one-week curing under self-weight intervene; paper pp. 16 and 18 proposes these as possible causes of vertical-frequency decrease.','Additional laminate mass and boundary/mode changes are not resolved.','No experimental repeatability interval; rounding bounds cover table precision only.'])
    (HERE/'retrofit_signal_results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    for r in rows:
        if r['mode']==1:print(r['beam'],r['direction'],f'{r["frequency_change_pct"]:+.3f}%')
if __name__=='__main__':main()
