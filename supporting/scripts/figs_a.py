# Figures that depend only on the hand calculations and the fibre model
import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch, FancyBboxPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.interpolate import CubicSpline
from p import *
C=json.load(open('calc.json')); F=json.load(open('fibre.json'))
ink,ink2,grid,bg='#1f1f1e','#6b6b66','#e6e5e0','#fcfcfb'; BL,OR,GR,YE='#2a78d6','#eb6834','#1baf7a','#eda100'
def clean(a):
    a.grid(color=grid,lw=0.8); a.set_axisbelow(True)
    for sp in ['top','right']: a.spines[sp].set_visible(False)
bare=C['bare']; dyn=C['dynamics']; R=C['repairs']
# ---------------- specimen drawing
fig=plt.figure(figsize=(14,5.2),dpi=650)
a=fig.add_axes([0.02,0.06,0.70,0.84]); a.set_aspect('equal'); a.axis('off')
L=span; H=h; ov=overhang
a.add_patch(Rectangle((-ov,0),L+2*ov,H,fc='#eeede8',ec=ink,lw=1.2))
a.plot([-ov+30,L+ov-30],[y_bot]*2,color=OR,lw=2.2); a.plot([-ov+30,L+ov-30],[y_top]*2,color=OR,lw=1.6)
for x in np.arange(-ov+25,L+ov-24,150): a.plot([x,x],[25,H-25],color=ink2,lw=0.5)
for xs,lab in ((0,'Pin'),(L,'Roller')):
    a.add_patch(Polygon([[xs,0],[xs-55,-85],[xs+55,-85]],fc='white',ec=ink,lw=1)); a.text(xs+(-70 if xs==0 else 70),-45,lab,ha=('right' if xs==0 else 'left'),va='center',fontsize=8.5,color=ink2)
a.add_patch(Rectangle((910,H+70),1180,50,fc='#d9d8d2',ec=ink,lw=1))
for xp in (1000,2000): a.add_patch(Rectangle((xp-20,H),40,70,fc='#d9d8d2',ec=ink,lw=0.8))
a.add_patch(FancyArrowPatch((1500,H+420),(1500,H+125),arrowstyle='-|>',mutation_scale=18,color=BL,lw=2.2))
a.text(1530,H+380,'Jack load P, logged (frame output or load cell)',fontsize=8.5,color=ink,va='center')
a.text(1500,H+95,'Spreader beam',ha='center',va='center',fontsize=7.5,color=ink2)
for x in np.arange(0,L+1,300): a.plot([x],[H+12],marker='v',ms=5,color=ink2)
a.text(-ov,H+22,'Impact points, 300 mm grid (11)',fontsize=7.5,color=ink2,va='bottom')
a.add_patch(Rectangle((750-35,-36),70,36,fc=GR,ec='white')); a.text(750,-48,'Accelerometer\nat quarter span',ha='center',va='top',fontsize=8,color=ink)
a.add_patch(Rectangle((1850-28,-58),56,58,fc=YE,ec='white')); a.text(1850,-70,'Automatic tapper',ha='center',va='top',fontsize=8,color=ink)
for xg in (110,L/2,L-110):
    a.add_patch(Circle((xg,-190),28,fc='white',ec=ink,lw=1)); a.plot([xg,xg],[-162,-2],color=ink,lw=0.8)
a.text(L/2,-235,'Displacement transducer at midspan, logged, 0.01 mm',ha='center',va='top',fontsize=8,color=ink)
for xg in (110,L-110): a.text(xg,-235,'Support\ntransducer',ha='center',va='top',fontsize=8,color=ink)
a.add_patch(Circle((2600,H/2),18,fc=OR,ec='white')); a.text(2630,H/2,'Temperature',fontsize=7.5,color=ink,va='center')
def dim(x1,x2,y,t):
    a.add_patch(FancyArrowPatch((x1,y),(x2,y),arrowstyle='<->',mutation_scale=9,color=ink2,lw=0.8)); a.text((x1+x2)/2,y-22,t,ha='center',va='top',fontsize=8,color=ink2)
dim(0,1000,-390,'1,000 mm'); dim(1000,2000,-390,'1,000 mm'); dim(2000,3000,-390,'1,000 mm')
a.set_xlim(-250,L+250); a.set_ylim(-470,H+470)
a.set_title('Beam and instrumentation: 3.0 m span, four-point bending',loc='left',fontsize=11,color=ink)
bx=fig.add_axes([0.75,0.16,0.22,0.70]); bx.set_aspect('equal'); bx.axis('off')
bx.add_patch(Rectangle((0,0),b,H,fc='#eeede8',ec=ink,lw=1.2)); bx.add_patch(Rectangle((cover,cover),b-2*cover,H-2*cover,fc='none',ec=ink2,lw=0.8))
for x in (b/2-76,b/2,b/2+76): bx.add_patch(Circle((x,y_bot),6,fc=OR,ec='none'))
for x in (b/2-77,b/2+77): bx.add_patch(Circle((x,y_top),5,fc=OR,ec='none'))
bx.text(b/2,-25,'230 mm',ha='center',va='top',fontsize=8.5,color=ink2); bx.text(-20,H/2,'300 mm',ha='right',va='center',fontsize=8.5,color=ink2,rotation=90)
bx.text(b/2,H+18,'3 bars of 12 mm bottom, 2 of 10 mm top\n8 mm stirrups (Fe415) at 150 mm\nM30 concrete, Fe500 main bars, 25 mm cover',ha='center',va='bottom',fontsize=8,color=ink)
bx.set_xlim(-80,b+60); bx.set_ylim(-70,H+120); bx.set_title('Cross-section',loc='left',fontsize=11,color=ink)
fig.savefig('fig_specimen.png',facecolor=bg); plt.close(fig)
# ---------------- 3D view
fig=plt.figure(figsize=(13,5.0),dpi=650); a=fig.add_axes([-0.12,-0.28,1.24,1.5],projection='3d'); a.set_facecolor(bg)
Lt=Ltot
def box(x0,x1,y0,y1,z0,z1,fc,al,ec):
    v=np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]])
    Fc=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]
    a.add_collection3d(Poly3DCollection([v[f] for f in Fc],facecolors=fc,alpha=al,edgecolors=ec,linewidths=0.4))
box(0,Lt,0,b,0,H,'#c9c7bf',0.10,'#9a988f')
for z in (b/2-76,b/2,b/2+76): a.plot([30,Lt-30],[z,z],[y_bot]*2,color=OR,lw=3.0)
for z in (b/2-77,b/2+77): a.plot([30,Lt-30],[z,z],[y_top]*2,color=OR,lw=2.3)
for x in np.arange(25,Lt-24,150):   # 22 stirrups: (3200 - 2 x 25) / 150 + 1
    y0,y1,z0,z1=cover+4,b-cover-4,cover+4,H-cover-4
    a.plot([x]*5,[y0,y1,y1,y0,y0],[z0,z0,z1,z1,z0],color=BL,lw=0.9)
for xs in (ov,ov+span): a.plot([xs,xs],[-10,b+10],[0,0],color=ink,lw=3)
for xp in (ov+1000,ov+2000):
    a.plot([xp,xp],[-10,b+10],[H,H],color=ink,lw=3); a.quiver(xp,b/2,H+240,0,0,-215,color=BL,lw=2,arrow_length_ratio=0.25); a.text(xp+50,b/2,H+255,'P/2',color=ink,fontsize=9)
a.set_box_aspect((Lt,b*2.6,(H+300)*1.9)); a.set_xlim(0,Lt); a.set_ylim(-40,b+40); a.set_zlim(-20,H+320)
a.view_init(elev=20,azim=-58); a.set_axis_off()
fig.text(0.06,0.9,'Beam model with reinforcement cage',fontsize=12,color=ink)
fig.text(0.06,0.85,'3,200 mm long, 3,000 mm span, 230 × 300 mm; 3 bars of 12 mm bottom and 2 of 10 mm top (orange); 8 mm stirrups at 150 mm (blue)',fontsize=8.5,color=ink2)
fig.savefig('fig_model_3d.png',facecolor=bg); plt.close(fig)
# ---------------- mode shapes (fibre) with sensor and impact points
x=np.array(F['x']); fig,ax=plt.subplots(1,2,figsize=(11,3.6),dpi=650)
for a,m,c,k in zip(ax,F['modes'],(BL,OR),(1,2)):
    clean(a); v=np.array(m['v']); v=v/np.abs(v).max(); cs=CubicSpline(x,v); xx=np.linspace(0,span,300)
    a.plot(xx/1000,cs(xx),color=c,lw=2); a.axhline(0,color=ink2,lw=0.8)
    pts=np.arange(0,span+1,300); a.plot(pts/1000,cs(pts),'v',ms=5,color=ink2,ls='none'); a.plot(0.75,cs(750),'s',ms=9,color=GR,mec='white',mew=1.5)
    a.set_ylim(-1.25,1.25); a.set_xlabel('Position along span (m)'); a.set_title(f"Mode {k}: {m['f']:.0f} Hz",loc='left',fontsize=11,color=ink)
ax[0].set_ylabel('Normalised vertical displacement')
fig.text(0.01,0.01,'Undamaged beam, fibre model. Green square: fixed accelerometer at quarter span, away from the nodes of both modes. Grey triangles: roving impact points every 300 mm.',fontsize=8,color=ink2)
fig.tight_layout(rect=(0,0.05,1,1)); fig.savefig('fig_modes.png',facecolor=bg); plt.close(fig)
# ---------------- retrofit comparison: peak (hand vs fibre), initial stiffness, first frequency
keys=[('bare','Unstrengthened',None),('frp','Polymer\nstrips','Fibre-reinforced polymer strips'),('plate','Steel\nplate','Bonded steel plate'),('jacket','Concrete\njacket','Concrete jacket')]
cols=[BL,OR,GR,YE]
fig,ax=plt.subplots(1,3,figsize=(14,4.3),dpi=650)
pk=[max(F[k]['P']) for k,_,_ in keys]; hand=[bare['P_expected']]+[R[r]['P_expected'] for _,_,r in keys[1:]]
des=[bare['P_design']]+[R[r]['P_design'] for _,_,r in keys[1:]]
EI=[23*(F[k]['P'][5]/2)*1e3*span**3/(648*F[k]['D'][5])/1e9 for k,_,_ in keys]
f0=[F[k]['f0'] for k,_,_ in keys]
a=ax[0]; clean(a); a.grid(axis='x',visible=False); xi=np.arange(4)
a.bar(xi-0.2,des,0.36,color=[c+'66' for c in cols],edgecolor=cols,linewidth=1.2,label='IS 456 / ACI 440.2R design')
a.bar(xi+0.2,pk,0.36,color=cols,edgecolor=bg,linewidth=1,label='Fibre model peak')
for i,(dv,pv) in enumerate(zip(des,pk)): a.text(i-0.2,dv+2,f'{dv:.0f}',ha='center',fontsize=8,color=ink); a.text(i+0.2,pv+2,f'{pv:.0f}',ha='center',fontsize=8,color=ink)
a.set_title('Load capacity (kN): design value and model peak',loc='left',fontsize=10.5,color=ink); a.legend(fontsize=7.5,frameon=False,loc='upper left'); a.set_ylim(0,max(pk)*1.25)
a=ax[1]; clean(a); a.grid(axis='x',visible=False); a.bar(xi,EI,0.6,color=cols,edgecolor=bg)
for i,v in enumerate(EI): a.text(i,v*1.02,f'{v:,.0f}',ha='center',va='bottom',fontsize=8.5,color=ink)
a.set_title('Initial flexural stiffness (kN·m²)',loc='left',fontsize=10.5,color=ink); a.set_ylim(0,max(EI)*1.18)
a=ax[2]; clean(a); a.grid(axis='x',visible=False); a.bar(xi,f0,0.6,color=cols,edgecolor=bg)
for i,v in enumerate(f0): a.text(i,v*1.02,f'{v:.1f}'+('' if i==0 else f'\n({100*(v/f0[0]-1):+.0f}%)'),ha='center',va='bottom',fontsize=8.5,color=ink)
a.set_title('First natural frequency (Hz)',loc='left',fontsize=10.5,color=ink); a.set_ylim(0,max(f0)*1.3)
for a in ax: a.set_xticks(xi); a.set_xticklabels([k[1] for k in keys],fontsize=8.5)
fig.text(0.01,0.01,'Polymer strips: 2 laminates 50 × 1.2 mm, debonding strain 0.0045 (ACI 440.2R). Steel plate: standard flat 100 × 5 mm. Jacket: 75 mm on three sides with 2 bars of 12 mm. Applied to undamaged beams with ideal bond. Jacket analysis stopped at 13.7 mm before the load fell, so its peak is a lower bound.',fontsize=7.5,color=ink2)
fig.tight_layout(rect=(0,0.05,1,1)); fig.savefig('fig_retrofit_comparison.png',facecolor=bg); plt.close(fig)
# ---------------- moment-curvature
fig,a=plt.subplots(figsize=(7.5,4.6),dpi=650); clean(a)
N={'bare':'Unstrengthened','frp':'Polymer strips (debonds)','plate':'Bonded steel plate','jacket':'Concrete jacket'}
for (k,_,_),c in zip(keys,cols):
    K_=np.array(F[k]['K']); M_=np.array(F[k]['M']); m=K_<=0.12
    j=int(np.argmax(M_[m])) if k=='frp' else -1
    a.plot(K_[m],M_[m],color=c,lw=2); a.annotate(N[k],(K_[m][j],M_[m][j]),xytext=(6,4),textcoords='offset points',fontsize=8.5,color=ink)
a.set_xlim(0,0.14); a.set_xlabel('Midspan curvature (1/m)'); a.set_ylabel('Midspan moment (kN·m)')
a.set_title('Moment–curvature at midspan, fibre model',loc='left',fontsize=11,color=ink)
fig.tight_layout(); fig.savefig('fig_moment_curvature.png',facecolor=bg); plt.close(fig)
print('ok', [round(v,1) for v in pk], [round(v) for v in EI], [round(v,1) for v in f0])
