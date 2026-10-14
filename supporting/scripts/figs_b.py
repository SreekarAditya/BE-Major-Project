import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from p import *
F=json.load(open('fibre.json')); T=F['twin']; f0=T['f0']; Pd,Ps=T['Pd'],T['Ps']; R=T['rows']
ink,ink2,grid,bg='#1f1f1e','#6b6b66','#e6e5e0','#fcfcfb'; col=['#2a78d6','#eb6834','#1baf7a','#eda100']
C_=lambda P:(P*1e3/2)*a*(3*span**2-4*a**2)/24
EI0=C_(Pd)/R[0]['delta_d']
sf=0.3; sd=0.01; sm=0.10; snl=0.03; sl=0.02; z=1.645
res={k:[] for k in ('Reference model','Vibration only','Static diagnostic only','Combined')}
rows=R[1:]; truth=[r['delta_s'] for r in rows]; dmg=[r['damage'] for r in rows]
for r in rows:
    lr,vr=np.log(EI0),0.05**2
    lv=np.log(EI0)+2*np.log(r['f']/f0); vv=(2*sf/r['f'])**2+(2*sf/f0)**2+sm**2
    ls=np.log(C_(Pd)/r['delta_d']); vs=(sd/r['delta_d'])**2+sl**2+snl**2
    w=np.array([1/vv,1/vs]); lc=(w@[lv,ls])/w.sum(); vc=1/w.sum()
    for k,(l,v) in zip(res,[(lr,vr),(lv,vv),(ls,vs),(lc,vc)]):
        mu=np.log(C_(Ps))-l; s=np.sqrt(v); res[k].append((np.exp(mu),np.exp(mu-z*s),np.exp(mu+z*s)))
fig,ax=plt.subplots(1,2,figsize=(14,5),dpi=650)
for a_ in ax:
    a_.grid(color=grid,lw=0.8); a_.set_axisbelow(True)
    for sp in ['top','right']: a_.spines[sp].set_visible(False)
x=np.arange(len(rows)); off=np.linspace(-0.27,0.27,4); labs=[f'After damage\nto {d:.0f} kN' for d in dmg]
A=ax[0]; A.scatter(x,truth,marker='_',s=900,color=ink,lw=2.5,zorder=5,label='Simulated measurement (true service deflection)')
for (k,v),c,o in zip(res.items(),col,off):
    m=np.array([t[0] for t in v]); lo=np.array([t[1] for t in v]); hi=np.array([t[2] for t in v])
    A.errorbar(x+o,m,yerr=[m-lo,hi-m],fmt='o',ms=6,color=c,mec='white',mew=1.2,elinewidth=1.6,capsize=0,label=k+' (90% interval)')
A.set_xticks(x); A.set_xticklabels(labs,fontsize=9); A.set_ylabel(f'Deflection at {Ps:.0f} kN service load (mm)')
A.set_title('Twin prediction of the next service-load test',loc='left',fontsize=11,color=ink); A.legend(fontsize=8,frameon=False,loc='upper left')
A=ax[1]
for (k,v),c in zip(res.items(),col):
    e=[100*(t[0]/tr-1) for t,tr in zip(v,truth)]
    A.plot(x,e,color=c,lw=2,marker='o',ms=7,mec='white',mew=1.5)
    dy={'Static diagnostic only':7,'Combined':-7}.get(k,0)
    A.annotate(k,(x[-1],e[-1]),xytext=(8,dy),textcoords='offset points',fontsize=8.5,color=ink,va='center')
A.axhline(0,color=ink2,lw=0.9); A.set_xticks(x); A.set_xticklabels(labs,fontsize=9); A.set_xlim(-0.3,len(rows)-1+1.6)
A.set_ylabel('Prediction error (%)'); A.text(0.02,0.04,'Below zero: deflection under-predicted (unsafe side)',transform=A.transAxes,fontsize=8,color=ink2)
A.set_title('Prediction error by updating method',loc='left',fontsize=11,color=ink)
fig.text(0.01,0.01,f'Simulation: fibre model of the beam stands in for the physical specimen.\nBaseline: {Pd:.0f} kN diagnostic cycle only (below the {26.5:.1f} kN cracking load). After each damage stage: {Pd:.0f} kN diagnostic cycle and vibration, then prediction of the {Ps:.0f} kN service cycle, always below the highest load already applied.\nAssumed: frequency repeatability 0.3 Hz, displacement transducer 0.01 mm, 10% dynamic-to-static model uncertainty.',fontsize=7.5,color=ink2)
fig.tight_layout(rect=(0,0.09,1,1)); fig.savefig('fig_twin_prediction.png',facecolor=bg); plt.close(fig)
for k,v in res.items(): print(k,[round(100*(t[0]/tr-1),1) for t,tr in zip(v,truth)])
# staged frequency and stiffness vs damage
fig,ax=plt.subplots(1,2,figsize=(12,4.3),dpi=650)
for a_ in ax:
    a_.grid(color=grid,lw=0.8); a_.set_axisbelow(True)
    for sp in ['top','right']: a_.spines[sp].set_visible(False)
xl=['Undamaged']+[f'{d:.0f} kN' for d in dmg]; xx=np.arange(len(R))
fq=[r['f'] for r in R]; EIs=[C_(Pd)/r['delta_d']/1e9 for r in R]
for a_,y,lab,fmt,c in ((ax[0],fq,'First natural frequency after unloading (Hz)','{:.1f}',col[0]),(ax[1],EIs,'Stiffness from the 15 kN diagnostic cycle (kN·m²)','{:,.0f}',col[2])):
    a_.plot(xx,y,color=c,lw=2,marker='o',ms=8,mec='white',mew=2)
    for xi,yi in zip(xx,y): a_.annotate(fmt.format(yi),(xi,yi),xytext=(0,9),textcoords='offset points',ha='center',fontsize=8.5,color=ink)
    a_.set_xticks(xx); a_.set_xticklabels(xl,fontsize=9); a_.set_xlabel('Highest load applied so far'); a_.set_title(lab,loc='left',fontsize=10.5,color=ink); a_.set_ylim(0,max(y)*1.18)
fig.text(0.01,0.01,'Fibre model of the 230 × 300 mm beam, staged damage below yield (yield about 81 kN).',fontsize=8,color=ink2)
fig.tight_layout(rect=(0,0.05,1,1)); fig.savefig('fig_damage_stages.png',facecolor=bg); plt.close(fig)
print([round(v,1) for v in fq],[round(v) for v in EIs])
