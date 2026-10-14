import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
ink,ink2,bg='#1f1f1e','#6b6b66','#fcfcfb'
LANE={'prep':'#cde2fb','test':'#e9f6ef','twin':'#fdecdf','rep':'#fbf0d0'}
fig,a=plt.subplots(figsize=(16,10),dpi=650); a.set_xlim(0,160); a.set_ylim(-17,86); a.axis('off')
def box(x,y,w,h,t,c,bold=None):
    a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.25,rounding_size=1.2',fc=c,ec=ink2,lw=0.8))
    if bold: a.text(x+w/2,y+h-1.6,bold,ha='center',va='top',fontsize=9.2,color=ink,weight='bold'); a.text(x+w/2,y+h-5.2,t,ha='center',va='top',fontsize=7.8,color=ink,linespacing=1.35)
    else: a.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=7.8,color=ink)
def arr(x1,y1,x2,y2,rad=0):
    a.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=12,color=ink2,lw=1,connectionstyle=f'arc3,rad={rad}'))
def lane(y,h,t):
    a.text(1,y+h/2,t,ha='left',va='center',fontsize=9.5,color=ink2,rotation=90)
lane(66,18,'1  Preparation'); lane(36,28,'2  Damage and twin loop'); lane(4,30,'3  Repair and final test')
W=24; H=15
# lane 1
xs=[6,37,68,99,130]
P=[('Specimen design','IS 456 flexure and shear checks\nunder-reinforced, flexure governs\ndesign 70 kN, expected 82 kN'),
   ('Casting','pilot beam, damaged control,\nbeams for repair; cubes\nfor each batch (IS 516)'),
   ('Material tests','cube strength at 28 days\nmodulus, rebound, ultrasonic\npulse velocity (IS 516)'),
   ('Pilot beam','find cracking load, failure\nset damage loads and the\ncrack-width criterion'),
   ('Reference model','fibre beam model with\nmeasured materials\nchecked by hand calculation')]
for x,(b,t) in zip(xs,P): box(x,68,W,H,t,LANE['prep'],b)
for i in range(4): arr(xs[i]+W+0.6,75.5,xs[i+1]-0.6,75.5)
# lane 2
y2=42
T=[('Baseline','vibration; 15 kN diagnostic\ncycle only (below cracking);\nchecks: remount, known mass'),
   ('Controlled damage','load below yield to a set\ncrack-width criterion, unload'),
   ('Inspection','crack map, vibration,\ndiagnostic cycle to 15 kN'),
   ('Twin update','Bayesian update of\nflexural stiffness (kN·m²)\nwith uncertainty'),
   ('Predict, then test','prediction saved first, then\n30 kN service test, always\nbelow the highest load so far')]
for x,(b,t) in zip(xs,T): box(x,y2,W,H+1,t,LANE['test'] if b not in ('Twin update','Predict, then test') else LANE['twin'],b)
for i in range(4): arr(xs[i]+W+0.6,y2+8,xs[i+1]-0.6,y2+8)
arr(xs[4]+W/2,y2-0.3,xs[1]+W/2,y2-0.3,rad=-0.12)
a.text((xs[1]+xs[4])/2+W/2,y2-7.2,'repeat at the next damage level',ha='center',fontsize=7.8,color=ink2)
def route(x0,y0,ymid,x1,y1,label=None):
    a.plot([x0,157,157,x1,],[y0,y0,ymid,ymid],color=ink2,lw=1); arr(x1,ymid,x1,y1)
    if label: a.text(x1+2,ymid+0.8,label,ha='left',va='bottom',fontsize=7.8,color=ink2)
route(xs[4]+W+0.4,75.5,63.5,xs[0]+W/2,y2+H+1.4)
# lane 3
y3=8
R=[('Retrofit proposal','jacket, plate, polymer strip\nchecked against the target\nagreed with the guide:\nflexure, shear, anchorage'),
   ('Review and repair','guide reviews the proposal;\nassigned scheme built,\ncontrol beam left unrepaired'),
   ('New reference','monitoring re-baselined for\nnew mass and section;\ntwin updated after curing'),
   ('Predict, then test','service-load prediction\nsaved, then measured'),
   ('Load to failure','measured capacity against\nsection analysis (plate, strip:\nACI 440.2R debonding limit)')]
for x,(b,t) in zip(xs,R): box(x,y3,W,H+4,t,{'Retrofit proposal':LANE['twin'],'Review and repair':LANE['rep'],'New reference':LANE['twin'],'Predict, then test':LANE['twin'],'Load to failure':LANE['rep']}[b],b)
for i in range(4): arr(xs[i]+W+0.6,y3+9,xs[i+1]-0.6,y3+9)
route(xs[4]+W+0.4,y2+8,30.5,xs[0]+W/2,y3+H+4.4,'after the last damage level')
# live monitoring band
a.add_patch(FancyBboxPatch((6,-9.5),148,8,boxstyle='round,pad=0.25,rounding_size=1.2',fc='#eeede8',ec=ink2,lw=0.8))
a.text(8,-3.2,'Live monitoring throughout stages 2 and 3',fontsize=9.2,color=ink,weight='bold',va='center')
a.text(8,-7.2,'acceleration, load, deflection and temperature streamed; alerts carry their evidence and uncertainty',fontsize=7.8,color=ink,va='center')
for i,t in enumerate(('Event detected','Lasting change','Assessment pending','Condition updated','Sensor fault')):
    a.add_patch(FancyBboxPatch((82+i*14.6,-7.6),13.2,4.2,boxstyle='round,pad=0.15,rounding_size=0.8',fc='white',ec=ink2,lw=0.6)); a.text(82+i*14.6+6.6,-5.5,t,ha='center',va='center',fontsize=6.8,color=ink)
# legend chips
for i,(c,t) in enumerate(((LANE['prep'],'Design and preparation'),(LANE['test'],'Physical test'),(LANE['twin'],'Digital twin step'),(LANE['rep'],'Repair and capacity'))):
    a.add_patch(FancyBboxPatch((6+i*34,-15.6),3,2,boxstyle='round,pad=0.1',fc=c,ec=ink2,lw=0.6)); a.text(10+i*34,-14.6,t,va='center',fontsize=8,color=ink)
a.set_title('Methodology',loc='left',fontsize=12,color=ink)
fig.savefig('fig_methodology.png',facecolor=bg,bbox_inches='tight'); print('ok')
