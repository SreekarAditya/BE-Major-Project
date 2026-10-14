import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from p import *
D=json.load(open('cont230.json')); C=json.load(open('calc.json')); F=json.load(open('fibre.json'))
xs=np.array(D['xs']); ys=np.array(D['ys']); nx,ny=len(xs)-1,len(ys)-1
ink,ink2,grid,bg='#1f1f1e','#6b6b66','#e6e5e0','#fcfcfb'
div=LinearSegmentedColormap.from_list('d',['#104281','#3987e5','#b7d3f6','#f3f2ee','#f6c9b4','#eb6834','#9a3412'])
seqb=LinearSegmentedColormap.from_list('b',['#f3f2ee','#cde2fb','#86b6ef','#3987e5','#1c5cab','#0d366b'])
nid=lambda i,j:j*(nx+1)+i
X0=np.array([[x,y] for y in ys for x in xs])
def quads(U,sc):
    P=X0+sc*np.array(U); return [[P[nid(i,j)],P[nid(i+1,j)],P[nid(i+1,j+1)],P[nid(i,j+1)]] for j in range(ny) for i in range(nx)]
def frame(a): a.set_aspect(1); a.axis('off')
def clean(a):
    a.grid(color=grid,lw=0.8); a.set_axisbelow(True)
    for sp in ['top','right']: a.spines[sp].set_visible(False)
S=D['snaps']
# 1 stress contours
fig,axs=plt.subplots(3,1,figsize=(12,6.8),dpi=650)
for a,s in zip(axs,S):
    sxx=np.array(s['E'])[:,0]; sc=25 if s['d']<3 else 8
    pc=PolyCollection(quads(s['U'],sc),array=sxx,cmap=div,norm=TwoSlopeNorm(vmin=-30,vcenter=0,vmax=4),edgecolors='none'); a.add_collection(pc)
    a.autoscale_view(); frame(a); a.set_title(f"{s['name']}: P = {s['P']:.0f} kN, midspan deflection {s['d']:.1f} mm (deformation × {sc})",loc='left',fontsize=10,color=ink)
cb=fig.colorbar(pc,ax=axs,fraction=0.02,pad=0.01,ticks=[-30,-20,-10,0,2,4]); cb.set_label('Longitudinal stress σxx (MPa); compression negative',fontsize=9,color=ink); cb.ax.tick_params(labelsize=8)
fig.text(0.01,0.01,'Plane-stress continuum model (OpenSees ASDConcrete3D concrete; bars and stirrups as bar elements). Cracked concrete carries little tension, so the steel takes it.',fontsize=7.5,color=ink2)
fig.savefig('fig_fe_stress_contours.png',facecolor=bg,bbox_inches='tight'); plt.close(fig)
# 2 crack pattern
fig,axs=plt.subplots(3,1,figsize=(12,6.0),dpi=650)
for a,s in zip(axs,S):
    E=np.array(s['E']); segs=[]; ws=[]
    for j in range(ny):
        for i in range(nx):
            sx,sy,txy,dm=E[j*nx+i]
            if dm<0.3: continue
            th=0.5*np.arctan2(2*txy,sx-sy); cx,cy=(xs[i]+xs[i+1])/2,(ys[j]+ys[j+1])/2; hh=min(xs[i+1]-xs[i],ys[j+1]-ys[j])*0.55
            dx,dy=-np.sin(th),np.cos(th); segs.append([[cx-hh*dx,cy-hh*dy],[cx+hh*dx,cy+hh*dy]]); ws.append(0.6+2.2*dm)
    a.add_patch(plt.Rectangle((0,0),span,h,fc='#eeede8',ec=ink2,lw=0.8)); a.add_collection(LineCollection(segs,colors='#9a3412',linewidths=ws))
    for xp in (1000,2000): a.plot([xp],[h],marker='v',ms=7,color=ink2,clip_on=False)
    for x_ in (0,span): a.plot([x_],[0],marker='^',ms=8,color=ink,clip_on=False)
    a.set_xlim(-40,span+40); a.set_ylim(-40,h+40); frame(a); a.set_title(f"{s['name']}: P = {s['P']:.0f} kN",loc='left',fontsize=10,color=ink)
fig.text(0.01,0.01,'Predicted crack pattern: lines perpendicular to the principal tensile stress in damaged concrete; thickness shows damage.',fontsize=7.5,color=ink2)
fig.savefig('fig_fe_crack_pattern.png',facecolor=bg,bbox_inches='tight'); plt.close(fig)
# 3 steel stress
fig,a=plt.subplots(figsize=(9,4.2),dpi=650); clean(a)
xm=(xs[:-1]+xs[1:])/2/1000
for s,c in zip(S,['#2a78d6','#eb6834','#1baf7a']):
    a.plot(xm,s['steel'],color=c,lw=2); a.annotate(f"{s['name']} ({s['P']:.0f} kN)",(xm[len(xm)//2],max(s['steel'])),xytext=(0,6),textcoords='offset points',ha='center',fontsize=8.5,color=ink)
a.axhline(fy,color=ink2,ls=(0,(4,3)),lw=0.9); a.text(0.03,fy+5,'Yield stress 500 MPa',fontsize=8,color=ink2,va='bottom')
a.set_xlabel('Position along span (m)'); a.set_ylabel('Bottom bar stress (MPa)'); a.set_ylim(0,580)
a.set_title('Tension in the bottom reinforcement',loc='left',fontsize=11,color=ink)
fig.tight_layout(); fig.savefig('fig_fe_steel_stress.png',facecolor=bg); plt.close(fig)
# 4 mode 1
fig,a=plt.subplots(figsize=(12,2.7),dpi=650)
U=np.array(D['mode1']); U=U/np.abs(U).max(); mag=np.sqrt((U**2).sum(1))
val=[mag[[nid(i,j),nid(i+1,j),nid(i+1,j+1),nid(i,j+1)]].mean() for j in range(ny) for i in range(nx)]
a.add_collection(PolyCollection(quads(U,150),array=np.array(val),cmap=seqb,edgecolors='#ffffff',linewidths=0.15))
a.add_patch(plt.Rectangle((0,0),span,h,fc='none',ec=ink2,lw=0.6,ls=(0,(3,3)))); a.autoscale_view(); frame(a)
a.set_title(f"First vibration mode of the undamaged beam: {D['f1']:.1f} Hz (beam theory {C['dynamics']['f1']:.1f} Hz)",loc='left',fontsize=10,color=ink)
fig.text(0.01,0.01,'Continuum model. Colour shows relative displacement; dashed outline is the undeformed beam.',fontsize=7.5,color=ink2)
fig.savefig('fig_fe_modes.png',facecolor=bg,bbox_inches='tight'); plt.close(fig)
# 5 mesh
fig,a=plt.subplots(figsize=(12,2.9),dpi=650)
a.add_patch(plt.Rectangle((0,0),span,h,fc='#eeede8',ec=ink,lw=0.9,zorder=0))
a.add_collection(LineCollection([[[x,ys[0]],[x,ys[-1]]] for x in xs]+[[[xs[0],y],[xs[-1],y]] for y in ys],colors='#b9b7ae',linewidths=0.5))
a.plot([0,span],[39,39],color='#eb6834',lw=2.4); a.plot([0,span],[262,262],color='#eb6834',lw=1.8)
for x_ in xs[1::3]: a.plot([x_,x_],[39,262],color='#2a78d6',lw=0.9)
for x_,lab in ((0,'Pin'),(span,'Roller')): a.plot([x_],[0],marker='^',ms=10,color=ink,clip_on=False); a.text(x_,-60,lab,ha='center',va='top',fontsize=8,color=ink2)
for xp in (1000,2000):
    a.annotate('',(xp,h),xytext=(xp,h+170),arrowprops=dict(arrowstyle='-|>',color='#2a78d6',lw=1.6),annotation_clip=False); a.text(xp+25,h+130,'P/2',fontsize=8.5,color=ink)
a.text(span+40,39,'3 bars of 12 mm',fontsize=8,va='center',color=ink); a.text(span+40,262,'2 bars of 10 mm',fontsize=8,va='center',color=ink); a.text(span+40,150,'stirrups (blue)',fontsize=8,va='center',color=ink)
a.set_xlim(-80,span+500); a.set_ylim(-120,h+200); frame(a)
a.set_title(f"Finite element mesh: {nx*ny} four-node plane-stress elements; bars and stirrups as bar elements",loc='left',fontsize=10,color=ink)
fig.savefig('fig_fe_mesh.png',facecolor=bg,bbox_inches='tight'); plt.close(fig)
# 6 analytical vs simulation
fig,a=plt.subplots(figsize=(8.5,5),dpi=650); clean(a)
fb=F['bare']; Df,Pf=np.array(fb['D']),np.array(fb['P']); m=Df<=30
a.plot(Df[m],Pf[m],color='#2a78d6',lw=2,label='Simulation: fibre beam model')
a.plot(D['D'],D['P'],color='#eb6834',lw=2,label='Simulation: plane-stress continuum model')
rows=np.array(C['deflection_curves']); a.plot(rows[:,1],rows[:,0],color='#1baf7a',lw=2,label='Analytical: effective moment of inertia (Branson, ACI 318)')
a.plot(rows[:,2],rows[:,0],color='#eda100',lw=2,label='Analytical: IS 456 Annex C')
for val,lab,top_ in ((C['bare']['Pcr'],f"Cracking load, hand calculation: {C['bare']['Pcr']:.1f} kN",False),(C['bare']['P_design'],f"Design resistance, IS 456 with partial safety factors: {C['bare']['P_design']:.0f} kN",False),(C['bare']['P_expected'],f"Expected peak, mean material strengths: {C['bare']['P_expected']:.0f} kN",True)):
    a.axhline(val,color=ink2,lw=0.9,ls=(0,(4,3)))
    if top_: a.text(0.4,val+1.2,lab,ha='left',va='bottom',fontsize=8,color=ink2)
    else: a.text(29.5,val-1.2,lab,ha='right',va='top',fontsize=8,color=ink2)
a.set_xlim(0,30); a.set_ylim(0,110); a.set_xlabel('Midspan deflection (mm)'); a.set_ylabel('Total jack load (kN)')
a.set_title('Unstrengthened beam: analytical predictions against simulation',loc='left',fontsize=11,color=ink)
a.legend(loc='lower right',bbox_to_anchor=(1,0.3),fontsize=8,frameon=False)
fig.tight_layout(); fig.savefig('fig_analytical_vs_simulation.png',facecolor=bg); plt.close(fig)
print('cont peak',round(max(D['P']),1),'f1',round(D['f1'],1))
