"""Manual pixel picks, calibrated against Figure 11 axes. Ambiguity retained.
Peak-to-table assignments follow chronological envelope order, with load discrepancies
bounded separately. No model curve is used as experimental data.
"""
from pathlib import Path
import runpy,subprocess
C=runpy.run_path(str(Path(__file__).with_name('common.py')));globals().update(C)
from PIL import Image,ImageDraw
(ROOT/'pages').mkdir(exist_ok=True)
subprocess.run(['pdftoppm','-f','9','-l','9','-r','600','-png','-singlefile',str(ROOT/'pesic2015_aam.pdf'),str(ROOT/'pages/p23_600')],check=True,stdout=subprocess.DEVNULL)
im=Image.open(ROOT/'pages/p23_600.png'); scale=im.height/1800
im=im.crop(tuple(round(a*scale) for a in (90,640,655,1110)))
im=im.resize((1728,round(im.height*1728/im.width)),Image.Resampling.LANCZOS);im.save(ROOT/'fig11_calibrated.png')
cal={'x_pixels':[305,1677],'x_values_mm':[0,35],'y_pixels':[1088,74],'y_values_kN':[0,2.25],
'check_x_ticks_pixels':{'5':501,'10':697,'15':893,'20':1089,'25':1285,'30':1481},
'check_y_ticks_pixels':{'0.25':975,'0.5':863,'0.75':750,'1.0':637,'1.25':525,'1.5':412,'1.75':299,'2.0':187},
'source':'p. 23, Fig. 11, left-hand graph; axes at tick marks, image width 1728 pixels',
'pixel_resolution_mm':35/(1677-305),'manual_method':'Inspect black open-circle experimental markers on the blue dashed curve; select envelope turning points. Early overlapping curves excluded. Assign selected peaks to chronological Table 3 steps; assignments are inferred and load discrepancies retained.'}
# Pixel picks are fixed before analysis. First three cycles too occluded to read reliably.
picks=[(4,431,786,.7),(5,635,697,.5),(6,696,637,.5),(7,751,589,.5),(8,854,519,.4),(9,924,453,.4),(10,1082,348,.4),(11,1532,95,.4)]
e=read('pesic_extract.json');beam=e['beams'][2]; rows=[];draw=ImageDraw.Draw(im)
for step,x,y,u in picks:
    d=(x-305)*35/(1677-305); pg=(1088-y)*2.25/(1088-74);p=beam['steps'][step]['load_kN']['value']
    row={'beam':3,'step':step,'pixel':[x,y],'peak_deflection_mm':d,'deflection_reading_bound_mm':u,'plotted_peak_load_kN':pg,'table_load_kN':p,'plot_minus_table_load_kN':pg-p,
    'load_alignment_bound_kN':.075,'source':'p. 23, Fig. 11; p. 19, Table 3, Beam 3','inferred':True,'reason':'Chronological envelope assignment to Table 3 load step; plot and table do not coincide exactly. Reading bounds include marker width, axis placement and local overlap; not statistical measurement errors.'}
    rows.append(row);beam['steps'][step]['peak_deflection_mm']=v(d,row['source'],inferred=True,reason=row['reason'],reading_bound_mm=u)
    draw.ellipse((x-16,y-16,x+16,y+16),outline='#8E1B2E',width=4);draw.text((x+18,y-16),str(step),fill='#8E1B2E',stroke_width=1)
# Only last three unloading chords are clear enough to identify both endpoints.
residuals=[(9,719,1088),(10,819,1088),(11,1063,1088)]
# Branches followed visually to their zero-load open-circle endpoints.
chords=[]
for step,x,y in residuals:
    if x is None:continue
    d=(x-305)*35/(1677-305);r=next(a for a in rows if a['step']==step)
    beam['steps'][step]['residual_deflection_mm']=v(d,'p. 23, Fig. 11',inferred=True,reason='Visible zero-load marker at end of corresponding unloading branch; chronological branch assignment.',reading_bound_mm=.4)
    chords.append({'step':step,'residual_mm':d,'peak_mm':r['peak_deflection_mm'],'load_kN':r['table_load_kN'],'unloading_chord_kN_per_mm':r['table_load_kN']/(r['peak_deflection_mm']-d),'scope':'Peak-to-zero chord, not tangent reloading stiffness','residual_reading_bound_mm':.4,'pixel':[x,y]})
    draw.rectangle((x-13,y-13,x+13,y+13),outline='#4A6C8C',width=4);draw.text((x+16,y-20),'R'+str(step),fill='#4A6C8C')
im.save(ROOT/'fig11_overlay.png')
save('digitised_static.json',{'calibration':cal,'rows':rows,'unloading_chords':chords,'excluded_steps':[1,2,3],'exclusion_reason':'Experimental peaks obscured by numerical curves; no defensible unique marker pick.','reading_distribution_for_propagation':'Uniform within stated bounds, shared baseline sampled once per replicate. This is reading sensitivity, not a confidence interval.'})
save('pesic_extract.json',e)
print('Figure 11 overlay and eight conditional peak picks saved.')
