from pathlib import Path
import runpy
C=runpy.run_path(str(Path(__file__).with_name('common.py')));globals().update(C)
E=read('pesic_extract.json');target=.8;rows=[]
for b in E['beams']:
    py=b['yield_load_kN']['value']; steps=b['steps']; x=np.array([a['load_kN']['value']/py for a in steps]);f=np.array([a['frequency_mode1_Hz']['value'] for a in steps]);f0=f[0]
    # For repeated load levels retain final history state, explicitly not exchangeable.
    unique=sorted(set(x));dy=[(f[np.where(x==a)[0][-1]]/f0)**2 for a in unique]
    fr=np.interp(target,unique,dy)
    rows.append({'beam':b['beam'],'yield_load_kN_approx':py,'target_load_kN':target*py,'dynamic_left':float(fr),'interpolation':'Linear in frequency-squared stiffness ratio versus load / approximate yield load. Beam 5 uses last (100-cycle) state at repeated 1.60 kN.'})
vals=[r['dynamic_left'] for r in rows]
# Same span pair, differing overall length / overhang and cycling history.
a,b=E['beams'][0],E['beams'][4];p=1.6
fa=np.interp(p,[s['load_kN']['value'] for s in a['steps']],[s['frequency_mode1_Hz']['value'] for s in a['steps']]);d1=(fa/a['steps'][0]['frequency_mode1_Hz']['value'])**2
cycles=[{'step':i,'dynamic_left':(b['steps'][i]['frequency_mode1_Hz']['value']/b['steps'][0]['frequency_mode1_Hz']['value'])**2} for i in (2,3,4)]
save('h1_results.json',{'status':'REQUESTED_CRACKING_NORMALISATION_UNAVAILABLE','cracking_normalised_spread':None,'static_spread_same_normalised_load':None,
'reason':'No measured cracking load for any beam; only one static beam history published. Same nominal section does not give same geometry or initial damage.',
'supplemental_yield_normalised_dynamic':{'load_over_yield':target,'rows':rows,'spread_percentage_points':100*(max(vals)-min(vals)),'interpretation':'Descriptive frequency-squared spread across different spans, overhangs, initial condition and cycle histories. Not an equal cracking-normalised damage test.'},
'supplemental_equal_load_pair':{'load_kN':p,'beam1_dynamic_left':float(d1),'beam5_cycle_states':cycles,'single_cycle_spread_percentage_points':100*abs(d1-cycles[0]['dynamic_left']),
'limitation':'Beams 1 and 5 share span and section but have different overhangs. Their initial frequencies and histories differ; absolute equal load does not establish equal cracking-normalised load.'}})
