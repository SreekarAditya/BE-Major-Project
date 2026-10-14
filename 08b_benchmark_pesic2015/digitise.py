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
'pixel_resolution_mm':35/(1677-305),'manual_method':'Inspect black open-circle experimental markers on the blue dashed curve; ordered PDF vector path identifies turning points obscured by model overlays. Fixed pixel picks use image-axis calibration. Original and isolated-path overlays prove assignments. Chronological assignments are inferred and discrepancies retained.'}
# Pixel picks are fixed before analysis. Occluded peaks located using the ordered blue experimental vector path; all values still read through calibrated image axes.
picks=[(1, 324, 936, 0.15), (2, 350, 886, 0.15), (3, 374, 841, 0.15), (4, 430, 787, 0.3), (5, 546, 719, 0.3), (6, 615, 661, 0.3), (7, 747, 597, 0.4), (8, 850, 521, 0.4), (9, 924, 453, 0.4), (10, 1082, 350, 0.4), (11, 1532, 97, 0.4)]
e=read('pesic_extract.json');beam=e['beams'][2]; rows=[];draw=ImageDraw.Draw(im)
for step,x,y,u in picks:
    d=(x-305)*35/(1677-305); pg=(1088-y)*2.25/(1088-74);p=beam['steps'][step]['load_kN']['value']
    row={'beam':3,'step':step,'pixel':[x,y],'peak_deflection_mm':d,'deflection_reading_bound_mm':u,'plotted_peak_load_kN':pg,'table_load_kN':p,'plot_minus_table_load_kN':pg-p,
    'load_alignment_bound_kN':.03,'source':'p. 23, Fig. 11; p. 19, Table 3, Beam 3','inferred':True,'reason':'Chronological envelope assignment to Table 3 load step; plot and table do not coincide exactly. Reading bounds include marker width, axis placement and local overlap; not statistical measurement errors.'}
    rows.append(row);beam['steps'][step]['peak_deflection_mm']=v(d,row['source'],inferred=True,reason=row['reason'],reading_bound_mm=u)
    draw.ellipse((x-16,y-16,x+16,y+16),outline='#8E1B2E',width=4);draw.text((x+18,y-16),str(step),fill='#8E1B2E',stroke_width=1)
# Ordered experimental path guides all zero-load endpoints, including obscured ones.
residuals=[(1, 314, 1088), (2, 335, 1088), (3, 354, 1088), (4, 387, 1088), (5, 472, 1088), (6, 529, 1088), (7, 603, 1088), (8, 660, 1088), (9, 715, 1088), (10, 811, 1088), (11, 1063, 1088)]
# Branches followed visually to their zero-load open-circle endpoints.
chords=[]
for step,x,y in residuals:
    if x is None:continue
    d=(x-305)*35/(1677-305);r=next(a for a in rows if a['step']==step)
    beam['steps'][step]['residual_deflection_mm']=v(d,'p. 23, Fig. 11',inferred=True,reason='Zero-load endpoint of corresponding original experimental vector branch, located on the calibrated image; chronological assignment.',reading_bound_mm=.15 if step<4 else .4)
    chords.append({'step':step,'residual_mm':d,'peak_mm':r['peak_deflection_mm'],'load_kN':r['table_load_kN'],'unloading_chord_kN_per_mm':r['table_load_kN']/(r['peak_deflection_mm']-d),'scope':'Peak-to-zero chord, not tangent reloading stiffness','residual_reading_bound_mm':.15 if step<4 else .4,'pixel':[x,y]})
    draw.rectangle((x-13,y-13,x+13,y+13),outline='#4A6C8C',width=4);draw.text((x+16,y-20),'R'+str(step),fill='#4A6C8C')
im.save(ROOT/'fig11_overlay.png')
trace=Image.new('RGB',im.size,'white');td=ImageDraw.Draw(trace)
source=read('vector_trace_check.json')[0]['pts'];tf=lambda z: ((z[0]*600/72-331)*1728/2076,(z[1]*600/72-2352)*1728/2076)
path=[tf(z) for z in source];td.line(path,fill='blue',width=3)
td.line([(305,74),(305,1088),(1677,1088)],fill='black',width=2)
for step,x,y,u in picks:
    td.ellipse((x-8,y-8,x+8,y+8),outline='#8E1B2E',width=3);td.text((x+10,y-15),str(step),fill='#8E1B2E')
for value in range(0,36,5):
    xp=305+value*(1677-305)/35;td.line([(xp,1088),(xp,1100)],fill='black',width=2);td.text((xp-8,1110),str(value),fill='black')
for value in [0,.25,.5,.75,1,1.25,1.5,1.75,2,2.25]:
    yp=1088-value*(1088-74)/2.25;td.line([(295,yp),(305,yp)],fill='black',width=2);td.text((250,yp-6),str(value),fill='black')
td.text((305,1150),'Experimental blue path isolated from original PDF; same calibrated pixel coordinates',fill='black')
trace.save(ROOT/'fig11_experimental_path.png')

save('digitised_static.json',{'calibration':cal,'rows':rows,'unloading_chords':chords,'excluded_steps':[],'exclusion_reason':None,'reading_distribution_for_propagation':'Uniform within stated bounds, shared baseline sampled once per replicate. This is reading sensitivity, not a confidence interval.'})
save('pesic_extract.json',e)
print('Figure 11 overlay and eleven vector-assisted pixel peak picks saved.')
