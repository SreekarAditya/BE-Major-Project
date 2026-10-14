"""Read-only source extraction, validated visually against published pp. 17 and 19.
The user-supplied file is the version of record, despite the job's prescribed filename.
Run with python -I. All output paths remain in this job directory.
"""
from pathlib import Path
import runpy, subprocess, hashlib
C=runpy.run_path(str(Path(__file__).with_name('common.py')));globals().update(C)
subprocess.run(['pdftotext','-layout',str(ROOT/'pesic2015_aam.pdf'),str(ROOT/'paper.txt')],check=True)
P=[ [0,1.25,1.61,1.85,2.11,2.4,2.6,2.87,3.01,3.26,3.54,3.72,4.07,4.96],
[0,1.31,1.43,1.67,1.98,2.2,2.46,2.55,3.3],
[0,.34,.45,.55,.67,.82,.95,1.09,1.26,1.41,1.64,2.2],
[0,.5,1.2,1.5,1.95,2.45,3,3.45,4,4.6,4.9,5.5,6,7],
[0,1.5,1.6,1.6,1.6,3,4.5]]
F1=[[14,13.5,13.2,12.9,12.7,12.4,12.1,11.9,11.6,11.5,11.4,11.2,11.1,10.3],
[10.1,8.72,8.6,8.5,8.43,8.27,8.06,7.82,7.73],
[5.95,5.82,5.79,5.74,5.71,5.68,5.64,5.54,5.46,5.4,5.3,5.05],
[16.9,16.8,16.6,16.5,16.1,15.9,15.6,15.1,14.2,13.8,13.3,13.3,13.2,13.2],
[12.6,12.3,12.2,12.1,11.9,11.3,10.4]]
F2=[[52.6,52,51.7,51.4,51.1,50.6,49.9,49.6,48.8,48.4,48,47.4,46.9,45],
[40,37.6,37.5,37.2,36.5,36.1,35.5,34.7,34.2],
[23.9,23.6,23.5,23.4,23.3,23.2,23.1,22.9,22.6,22.4,22.2,20.9],
[56.8,56.7,56.6,56.5,56.3,56.3,56.2,55.6,55.4,53.9,53.1,53.1,52.8,52.5],
[36.5,36,35.9,35.9,35.8,34.9,34.1]]
geom=list(zip([4,4.7,5.6,4.7,5.6],[3.8,4.5,5.4,3.3,3.8],[31.7,37.5,45,27.5,31.7],[14,10,6.6,18,12.5],[13.7,9.8,6.8,17.1,13.1]))
beams=[]
for j,(length,span,sl,f_FE,f_a) in enumerate(geom):
    steps=[]
    for i,(p,f1,f2) in enumerate(zip(P[j],F1[j],F2[j])):
        steps.append({'step':i,'load_kN':v(p,'p. 19, Table 3'),'frequency_mode1_Hz':v(f1,'p. 19, Table 3'),'frequency_mode2_Hz':v(f2,'p. 19, Table 3'),
        'frequency_rounding_half_unit_Hz':.005 if j in (1,2) else .05,
        'repeated_cycle_count':v(10 if i==3 else 100,'p. 19, Table 3 footnotes') if j==4 and i in (3,4) else None,
        'peak_deflection_mm':None,'residual_deflection_mm':None,'damping':None})
    beams.append({'beam':j+1,'geometry':{'length_m':v(length,'p. 17, Table 2'),'span_m':v(span,'p. 17, Table 2'),'span_depth_ratio':v(sl,'p. 17, Table 2'),
    'width_mm':v(300,'p. 17, Table 2'),'height_mm':v(120,'p. 17, Table 2'),'supports':v('Simply supported, one fixed bearing and one low-friction bearing','p. 17, section 2.2'),
    'load_arrangement':v('Symmetric three-point bending, point load at midspan','p. 17, section 2.2'),
    'overhang_each_m':v((length-span)/2,'p. 17, Table 2',inferred=True,reason='Symmetric supports assumed from stated symmetric test and Fig. 3; not independently dimensioned.')},
    'reinforcement':{'bottom_bars':v('3 bars, diameter 10 mm','p. 17, Table 2'),'area_mm2':v(235.6,'p. 17, Table 2'),
    'cover_mm':v(25,'p. 17, Table 2'),'effective_depth_mm':v(90,'p. 17, Table 2',inferred=True,reason='120 - 25 - 10/2; assumes cover denotes clear cover to main bars. Appendix B uses bar centre 20 mm above soffit, inconsistent with Table 2, so this is not adopted for blind modelling.'),
    'top_bars':None,'bar_depth_discrepancy':'Table 2 implies 30 mm bar centre above soffit; Appendix B node y=-40 in 120 mm deep section implies 20 mm.'},
    'steel':{'yield_strength_MPa':v(555,'p. 17, section 2.2'),'ultimate_strength_MPa':v(615,'p. 17, section 2.2'),'measured_elastic_modulus_MPa':None,'measured_ultimate_strain':None},
    'concrete':{'characteristic_cube_strength_32d_MPa':v(48,'p. 16, section 2.1',approximate=True),'characteristic_cylinder_strength_32d_MPa':v(43,'p. 16, section 2.1',approximate=True),
    'cylinder_32d_MPa':v(42.9,'p. 17, Fig. 1 printed label'),'cylinder_105d_MPa':v(51,'p. 17, Fig. 1 printed label'),
    'static_modulus_32d_GPa':v(30.5,'pp. 16-17, section 2.1; Fig. 2 printed label',approximate=True),'dynamic_modulus_after60d_GPa':v(40.1,'p. 17, section 2.1',approximate=True),
    'density_28d_kg_m3':v(2286,'p. 17, section 2.1',approximate=True),'density_range_kg_m3':v([2250,2300],'p. 16, section 2.1'),
    'ultrasonic_velocity_km_s':v(4.4,'p. 17, section 2.1',approximate=True),'poisson_ratio':v(.2,'p. 16, section 2.1',adopted_by_authors=True),
    'independently_measured_tensile_strength_MPa':None,'beam_specific_age_and_density':None,
    'authors_model_inputs_not_measurements':{'compressive_strength_MPa':v(53,'p. 19, section 3.1'),'tensile_strength_best_fit_MPa':v(2.5,'p. 21, Table 4',tuned_by_paper_authors=True),'modulus_best_fit_GPa':v(29,'p. 21, Table 4',tuned_by_paper_authors=True)}},
    'paper_predictions':{'unloaded_FE_frequency_Hz':v(f_FE,'p. 17, Table 2',model_output=True),'unloaded_segmental_frequency_Hz':v(f_a,'p. 17, Table 2',model_output=True)},
    'yield_moment_kNm':v(3,'p. 17, section 2.2',approximate=True),'yield_load_kN':v(12/span,'p. 17, section 2.2',inferred=True,reason='Paper formula Py = 4 My / span with My approximately 3.00 kNm; used only for supplemental comparison.'),
    'measured_cracking_load_kN':None,'steps':steps})
missing=['Static peak and residual deflections for Beams 1, 2, 4 and 5 are not published in this PDF.',
'Raw Beam 3 load-deflection records are needed to check vector-assisted graph readings and quantify measurement uncertainty.',
'Measured cracking loads and pre-test static baseline stiffness are absent for all five beams.',
'Beam-specific test ages, density, damping and quantitative vibration amplitude are absent.',
'Independent concrete tensile tests, measured steel elastic modulus and ultimate strain are absent; Table 2 and Appendix B disagree on bar depth.',
'Beam 3 may have pre-existing damage (p. 21); its undamaged static reference cannot be reconstructed from the published measurements.']
prov=read('source_provenance.json');prov['document_version']='Published version of record, 13 pages; printed pages 15-27. User supplied; no accepted-manuscript licence claimed.';save('source_provenance.json',prov)
save('pesic_extract.json',{'paper':{'title':'Experimental and finite element dynamic analysis of incrementally loaded reinforced concrete structures','year':2015,'doi':'10.1016/j.engstruct.2015.07.037','version':prov['document_version'],'sha256':hashlib.sha256((ROOT/'pesic2015_aam.pdf').read_bytes()).hexdigest()},
'measurement':{'source':'p. 17, sections 2.2-2.3','frequency':'Five hammer impacts at quarter-span points; averaged Fourier spectra of 8 second free-decay acceleration records; 1652 Hz sampling; measured unloaded after approximately 30 minute peak-load hold.',
'hammer_mass_kg':5.5,'accelerometer_sensitivity_mV_per_g':500,'vibration_amplitude':'Described as low amplitude; no numerical displacement amplitude provided.','static':'Micrometer at peak load and after unloading.','reported_deflection_limit':'span/250 target; Fig. 11 final Beam 3 peak exceeds this target.'},
'beams':beams,'missing':missing,'table_visual_checks':{'Table 2':'Every used value checked on pages/page-03.png','Table 3':'Every used cell and both footnotes checked on pages/page-05.png','Table 4':'Best-fit values are model parameters, excluded from blind predictions'},
'counts':{'beams':5,'loaded_frequency_steps':sum(len(s)-1 for s in P),'frequency_states_including_initial':sum(map(len,P))}})
(ROOT/'HUMAN_NEEDED.md').write_text('\n'.join('- '+m for m in missing)+'\n')
print('Extracted five beam frequency histories; no missing static values invented.')
