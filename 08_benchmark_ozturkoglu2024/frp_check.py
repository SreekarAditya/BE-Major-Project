"""Unchanged val_frp.py constitutive logic; specimen inputs and strain offsets.

Mean-property section benchmark, no strength reduction or safety factors.
Fiber-equivalent and gross-thickness inputs are both kept, without tuning.
"""
from pathlib import Path
import json, math
import numpy as np
HERE=Path(__file__).resolve().parent
def load(n):return json.loads((HERE/n).read_text())
def dump(n,d):(HERE/n).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')

def main():
    D=load('ozturkoglu_extract.json'); S=load('digitised_static.json')
    g=D['geometry']; v=lambda k:g[k]['value']
    b,h,d,dt=v('width_mm'),v('height_mm'),v('effective_depth_mm'),v('top_bar_centroid_depth_mm')
    As=v('tension_bar_count')*np.pi*v('tension_bar_diameter_mm')**2/4
    Ast=v('compression_bar_count')*np.pi*v('compression_bar_diameter_mm')**2/4
    fc=D['concrete']['cylinder_strength_MPa']['value']; Es=D['steel']['modulus_MPa']['value']; fy=D['steel']['yield_MPa']['value']
    span,a=v('span_mm'),v('shear_span_mm')
    unit_weight=24.0; Ec=5000*math.sqrt(fc); Ig=b*h**3/12
    Msw=unit_weight*b*h/1e6*(span/1000)**2/8
    ebi_sw=Msw*1e6/(Ec*Ig)*(h/2)
    def conc_force(c,eps_top,n=200,factor=1):
        y=(np.arange(n)+.5)/n*c; e=eps_top*(c-y)/c
        s=np.where(e<.002,fc*(1-(1-e/.002)**2),fc)*factor
        return (s*b*c/n).sum(), (s*b*c/n*y).sum()
    def state(c,ec,Af=0,Ef=0,fd=1,ebi=0,factor=1):
        ef=max(0.0,ec*(h-c)/c-ebi)
        es=ec*(d-c)/c; est=ec*(c-dt)/c
        Fs=As*np.clip(Es*es,-fy,fy); Fst=Ast*np.clip(Es*est,-fy,fy); Ff=Af*Ef*ef
        Cc,Mc=conc_force(c,ec,factor=factor)
        r=Cc+Fst-Fs-Ff
        M=abs(Fs*d+Ff*h-Fst*dt-Mc)/1e6
        return dict(equilibrium_residual_N=float(r),c_mm=float(c),eps_f=float(ef),eps_c=float(ec),eps_s=float(es),M_kNm=float(M),P_total_equivalent_kN=float(2*M/(a/1000)),P_jack_kN=float(2*(M-Msw)/(a/1000)),concrete_N=float(Cc),compression_steel_N=float(Fst),tension_steel_N=float(Fs),fiber_N=float(Ff),debonding_limit=fd,initial_substrate_strain=ebi)
    def ultimate(Af=0,Ef=0,fd=1,ebi=0,factor=1):
        # Identical 5 to 150 mm grid, 2901 points and 200 concrete slices as
        # the read-only reference. No empirical residual-strain calibration.
        best=None
        for c in np.linspace(5,150,2901):
            ec=min(.0035,(fd+ebi)*c/(h-c)) if Af>0 else .0035
            r=state(c,ec,Af,Ef,fd,ebi,factor)
            if best is None or abs(r['equilibrium_residual_N'])<abs(best['equilibrium_residual_N']):best=r
        best['governing']='concrete_crushing' if best['eps_c']>=.0035-1e-10 else 'fiber_debonding'
        best['equilibrium_relative_residual']=abs(best['equilibrium_residual_N'])/max(best['concrete_N']+abs(best['compression_steel_N']),1)
        return best
    def steel_yield(Af=0,Ef=0,fd=1,ebi=0,factor=1):
        # Extend the reference strain compatibility to first steel yield. This
        # differs from the paper's equivalent elasto-plastic yield definition.
        def f(c):return state(c,(fy/Es)*c/(d-c),Af,Ef,fd,ebi,factor)
        lo,hi=1.0,d-1
        for _ in range(90):
            mid=(lo+hi)/2
            if f(mid)['equilibrium_residual_N']>0:hi=mid
            else:lo=mid
        r=f((lo+hi)/2)
        r['definition']='First tension-steel strain reaches fy/Es; not equivalent elasto-plastic yield.'
        if r['eps_f']>fd or r['eps_c']>.0035:
            return dict(status='limit_reached_before_steel_yield',unconstrained_state=r,P_jack_kN=None)
        return r
    bare_u=ultimate(); bare_y=steel_yield()
    # Residual displacement alone does not identify residual substrate strain.
    # This declared global-curvature proxy supplies the requested second case,
    # and is kept separate from a validated damaged-section prediction.
    residual={}
    for beam,r in S['residual_D1'].items():
        lever=h-bare_y['c_mm']; curvature=24*r['value_mm']/(3*span**2-4*a**2)
        ebi=curvature*lever
        residual[beam]=dict(residual_displacement_mm=r['value_mm'],reading_uncertainty_mm=r['reading_uncertainty_mm'],curvature_per_mm=curvature,neutral_axis_proxy_mm=bare_y['c_mm'],substrate_strain_proxy=ebi,substrate_strain_proxy_uncertainty=24*r['reading_uncertainty_mm']/(3*span**2-4*a**2)*lever,formula='kappa_res = 24*delta_res/(3*L^2-4*a^2); eps_bi = kappa_res*(h-c_y_bare)',status='conditional_proxy_not_identified_residual_state',source=r['source'],assumptions='Residual shape assigned the elastic four-point shape and bare-yield neutral axis; actual plastic curvature distribution and residual stresses unknown.')
    material_inputs={}
    results=[]
    for mat,m in D['strengthening'].items():
        Ef=m['fiber_modulus_MPa']['value']; efu=m['fiber_rupture_strain']['value']; twet=m['wet_laminate_total_thickness_mm']['value']; vf=m['fiber_volume_fraction']['value']
        # Each representation is specified before looking at capacity ratios.
        # Longitudinal fraction is a sensitivity, since alignment is unstated.
        tfiber=twet*vf
        dominant_fraction=m['weft_mass_g_m2']['value']/(m['weft_mass_g_m2']['value']+m['warp_mass_g_m2']['value'])
        cases=[('fiber_equivalent',tfiber,'Conditional primary: fiber modulus with total fiber-equivalent thickness, all fiber axial.'),('dominant_direction_sensitivity',tfiber*dominant_fraction,'Conditional sensitivity: only dominant fiber-direction mass fraction carries longitudinal load; alignment is not confirmed.'),('gross_thickness_diagnostic',twet,'INVALID MATERIAL BASIS: fiber modulus applied to resin-rich gross thickness; retained to expose overprediction, not accepted as a model.')]
        material_inputs[mat]=[]
        for representation,tt,note in cases:
            fd=min(.41*math.sqrt(fc/(Ef*tt)),.9*efu); Af=b*tt
            material_inputs[mat].append(dict(representation=representation,total_effective_thickness_mm=tt,ply_thickness_mm=tt/2,n=2,Ef_MPa=Ef,Af_mm2=Af,eps_fu=efu,eps_fd=fd,note=note))
            for timing in ['PreStr','PostStr']:
                beam=mat+'_'+timing
                conditions=[('self_weight_only',ebi_sw)] if timing=='PreStr' else [('ignore_initial_strain',0.0),('residual_global_curvature_proxy',residual[beam]['substrate_strain_proxy'])]
                for initial,ebi in conditions:
                    u=ultimate(Af,Ef,fd,ebi); y=steel_yield(Af,Ef,fd,ebi)
                    test=D['static'][beam if timing=='PreStr' else beam+'_after']
                    Pu=test['ultimate_load_kN']['value']; Py=test['yield_load_kN']['value']
                    u['test_P_kN']=Pu; u['predicted_to_test']=u['P_jack_kN']/Pu
                    y['test_P_kN']=Py; y['predicted_to_test']=y['P_jack_kN']/Py if Py is not None and y['P_jack_kN'] is not None else None
                    results.append(dict(beam=beam,representation=representation,initial_strain_case=initial,conditional=True,material_basis_status='invalid_diagnostic' if representation=='gross_thickness_diagnostic' else 'inferred_no_coupon',ultimate=u,yield_prediction=y,note=note,post_damage_limit='ACI initial-strain treatment is an elastic substrate approximation; residual global curvature does not model yielded steel, crushing or bond degradation.' if timing=='PostStr' else 'Self-weight modulus and density assumed because the paper does not provide them.'))
    is_u=ultimate(factor=.67); is_y=steel_yield(factor=.67)
    bare=[]
    for beam in ['GFRP_PostStr','CFRP_PostStr']:
        t=D['static'][beam+'_bare']
        bare.append(dict(beam=beam,IS456_shape_ultimate=is_u,IS456_shape_yield=is_y,test_ultimate_kN=t['ultimate_load_kN']['value'],test_yield_kN=t['yield_load_kN']['value'],ultimate_predicted_to_test=is_u['P_jack_kN']/t['ultimate_load_kN']['value'],yield_predicted_to_test=is_y['P_jack_kN']/t['yield_load_kN']['value'],cylinder_direct_parabola_ultimate=bare_u,cylinder_direct_parabola_yield=bare_y,comparison_limit='Bare tests stop at D1, so reported ultimate is the observed bare peak, not a separate bare failure test.'))
    mus=load('reference_snapshot/musial_frp.json')
    out=dict(status='COMPLETED_WITH_CONDITIONAL_INPUTS',method=dict(reference='reference_snapshot/val_frp.py',eps_fd_formula='min(0.41*sqrt(fc/(n*Ef*tf)), 0.9*eps_fu)',eps_cu=.0035,eps_c2=.002,concrete_slices=200,neutral_axis_grid_points=2901,neutral_axis_grid_mm=[5,150],safety_factors='none',strength_basis='Approximate mean cylinder concrete strength; steel and fiber properties as stated, not individual measured coupon strengths.',wrap_clause='Not applicable: only longitudinal soffit sheets reported; no wrap or U-wrap capacity assumed.',ACI_reference=dict(url='https://www.concrete.org/Portals/0/Files/PDF/Previews/440.2-23_preview.pdf',scope='Official preview verifies guide identity, flexural strengthening chapter and anchorage qualifications; full equation/clause text is not in the preview. Formula is supplied by job and frozen val_frp.py.',clause_verification='Full flexural equation clause number not independently verified; do not claim full guide compliance.'),IS456_bare='Indian Standard 456:2000, clause 38.1: plane sections, no concrete tension, 0.0035 crushing; parabola-rectangle scaled to 0.67 times strength, material safety factors removed, steel elastoplastic. Mean cylinder used directly as strength proxy because mean cube strength is missing; conditional benchmark, not a code design resistance.'),assumed_self_weight=dict(unit_weight_kN_m3=unit_weight,Ec_MPa=Ec,Ec_basis='5000*sqrt(20) as a declared nominal modulus proxy, not measured; cylinder strength not IS cube strength.',gross_I_mm4=Ig,M_self_weight_kNm=Msw,initial_substrate_strain=ebi_sw,initial_strain_basis='Gross uncracked elastic section, neutral axis at middepth; beam simply supported under self-weight at bonding.'),residual_state_proxies=residual,material_inputs=material_inputs,strengthened=results,bare=bare,Musial_comparison=dict(predicted_to_test_BII1=mus['B-II-1']['ratio'],predicted_to_test_BII2=mus['B-II-2']['ratio'],source='reference_snapshot/musial_frp.json'),limitations=['Cured composite coupon data and longitudinal fiber orientation missing; no unconditional capacity validation.','Top compression-steel depth inferred; no tuning of strengths or geometry.','Post-strengthened yield is not separately reported; comparison unavailable.','Residual displacement cannot uniquely determine local substrate strain.','A scalar initial-strain offset cannot represent plastic steel strain, crack localization, bond degradation or concrete crushing.','No strength reduction/safety factors; output is not a design recommendation.'])
    dump('frp_results.json',out)
    for r in results:
        if r['representation']=='fiber_equivalent':print(r['beam'],r['initial_strain_case'],round(r['ultimate']['P_jack_kN'],2),'ratio',round(r['ultimate']['predicted_to_test'],3))

if __name__=='__main__':main()
