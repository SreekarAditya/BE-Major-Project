# Fibre beam-column model of the 230 x 300 mm beam: pushover, repairs, staged damage with diagnostic and service cycles, modes
import numpy as np, openseespy.opensees as ops, json
from p import *
ne=24; le=span/ne; nmid=13; nload=(9,17)
efd=0.41*np.sqrt(0.8*fck/(frp['E']*frp['t']))
def build(kind='bare'):
    ops.wipe(); ops.model('basic','-ndm',2,'-ndf',3)
    for i in range(ne+1): ops.node(i+1,i*le,0.)
    ops.fix(1,1,1,0); ops.fix(ne+1,0,1,0)
    fcm=0.8*fck
    ops.uniaxialMaterial('Concrete02',1,-fcm,-0.002,-0.2*fcm,-0.0035,0.1,ft,ft/0.002)
    ops.uniaxialMaterial('Steel02',2,fy,Es,0.01,18,0.925,0.15)
    ops.uniaxialMaterial('Steel02',3,plate['fy'],Es,0.01,18,0.925,0.15)
    ops.uniaxialMaterial('Elastic',4,frp['E']); ops.uniaxialMaterial('MinMax',5,4,'-min',-1.0,'-max',float(efd))
    ops.section('Fiber',1)
    yb=-h/2
    if kind=='jacket':
        t=jacket['t']; B=b+2*t; ybj=yb-t
        ops.patch('rect',1,48,1,ybj,-B/2,h/2,B/2); mass_A=B*(h+t)
        ops.layer('straight',2,jacket['n'],np.pi*jacket['d']**2/4,ybj+cover+dst+jacket['d']/2,0,ybj+cover+dst+jacket['d']/2,0)
    else:
        ops.patch('rect',1,48,1,yb,-b/2,h/2,b/2); mass_A=b*h
    ops.layer('straight',2,bot['n'],np.pi*bot['d']**2/4,yb+y_bot,0,yb+y_bot,0)
    ops.layer('straight',2,top['n'],np.pi*top['d']**2/4,yb+y_top,0,yb+y_top,0)
    if kind=='plate': ops.layer('straight',3,1,plate['w']*plate['t'],yb-plate['t']/2,0,yb-plate['t']/2,0)
    if kind=='frp':   ops.layer('straight',5,1,frp['n']*frp['w']*frp['t'],yb-frp['t']/2,0,yb-frp['t']/2,0)
    ops.geomTransf('Linear',1); ops.beamIntegration('Lobatto',1,1,5)
    for i in range(ne): ops.element('forceBeamColumn',i+1,i+1,i+2,1,1)
    for i in range(ne+1):
        mi=rho*mass_A*le*(0.5 if i in (0,ne) else 1.); ops.mass(i+1,mi,mi,0.)
    ops.timeSeries('Linear',1); ops.pattern('Plain',1,1)
    for n in nload: ops.load(n,0,-0.5,0)
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('FullGeneral')
    ops.test('NormDispIncr',1e-8,100); ops.algorithm('Newton')
def step(du):
    ops.integrator('DisplacementControl',nmid,2,du); ops.analysis('Static')
    ok=ops.analyze(1)
    if ok!=0: ops.algorithm('ModifiedNewton','-initial'); ok=ops.analyze(1); ops.algorithm('Newton')
    return ok
def freq(n=1):
    w2=ops.eigen('-fullGenLapack',max(n,2)); return [float(np.sqrt(v)/(2*np.pi)) for v in sorted(w2)[:n]]
state=lambda:(ops.getLoadFactor(1)/1e3,-ops.nodeDisp(nmid,2))
out={}
# pushovers
for kind in ('bare','frp','plate','jacket'):
    build(kind); f0=freq(1)[0]; P=[0];D=[0];M=[0];K=[0]
    while D[-1]<60:
        if step(-0.1)!=0: break
        p,d=state(); P.append(p); D.append(d)
        M.append(abs(ops.sectionForce(12,5,2))/1e6); K.append(abs(ops.sectionDeformation(12,5,2))*1e3)
        if p<0.8*max(P) and d>8: break
    out[kind]=dict(f0=f0,P=P,D=D,M=M,K=K)
    i=int(np.argmax(P)); print(kind,'f0',round(f0,1),'peak',round(P[i],1),'at',round(D[i],1),flush=True)
# modes (bare, undamaged): shapes for figure
build('bare'); w2=ops.eigen('-fullGenLapack',6); fs=np.sqrt(w2)/(2*np.pi); modes=[]
for k in range(6):
    v=[ops.nodeEigenvector(i+1,k+1,2) for i in range(ne+1)]; u=[ops.nodeEigenvector(i+1,k+1,1) for i in range(ne+1)]
    if max(abs(np.array(v)))>10*max(abs(np.array(u))+1e-30): modes.append(dict(f=float(fs[k]),v=v))
out['modes']=modes[:2]; out['x']=[i*le for i in range(ne+1)]
# staged damage history with diagnostic (15 kN) and service (30 kN) cycles
Pd,Ps=15.0,30.0
build('bare'); f00=freq(1)[0]
def load_to(Pt,du=0.02):
    P=[];D=[]
    while True:
        if step(-du)!=0: raise RuntimeError('nonconv')
        p,d=state(); P.append(p); D.append(d)
        if p>=Pt: return np.array(P),np.array(D)
def unload(du=0.02):
    while ops.getLoadFactor(1)>0.05e3:
        if step(du)!=0: break
def cycle(Pt):
    d0=state()[1]; P,D=load_to(Pt); unload(); return float(np.interp(Pt,P,D)-d0)
rows=[]
for Dmg in [None,35.,50.,65.,72.]:
    pl=None
    if Dmg is not None:
        P,D=load_to(Dmg); pl=float(D[-1]); unload()
    resid=state()[1]; dd=cycle(Pd); f=freq(1)[0]; ds=cycle(Ps) if Dmg is not None else None
    rows.append(dict(damage=Dmg or 0.0,defl_at_damage=pl,resid=resid,delta_d=dd,f=f,delta_s=ds))
    print('stage',Dmg,round(resid,3),round(dd,3),round(f,1),ds,flush=True)
out['twin']=dict(f0=f00,Pd=Pd,Ps=Ps,rows=rows)
json.dump(out,open('fibre.json','w'))
