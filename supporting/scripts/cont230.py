# Plane-stress continuum model of the 230 x 300 mm beam (OpenSees ASDConcrete3D), with bars and stirrups as truss elements
import numpy as np, openseespy.opensees as ops, json, sys
from p import *
xs=np.linspace(0,span,61)            # 50 mm columns
ys=[0,20,39,60,85,110,135,160,185,210,235,262,280,300]
nx,ny=len(xs)-1,len(ys)-1
nid=lambda i,j: j*(nx+1)+i+1
ecr=ft/Ec
Te=[0,ecr,2*ecr,5*ecr,10*ecr,20*ecr,100*ecr]; Ts=[0,ft,0.6*ft,0.3*ft,0.1*ft,0.05*ft,0.05*ft]
Td=[0,0]+[1-s/(Ec*e) for e,s in zip(Te[2:],Ts[2:])]
fcm=0.8*fck; e0=0.002
Ce=[0,0.4*fcm/Ec,0.001,0.0015,0.002,0.0035,0.006]
par=lambda e: fcm*(2*e/e0-(e/e0)**2)
Cs=[0,0.4*fcm,par(0.001),par(0.0015),fcm,0.85*fcm,0.2*fcm]
Cd=[0,0]+[0.3*(1-s/(Ec*e)) for e,s in zip(Ce[2:],Cs[2:])]
NE=nx*ny
def build():
    ops.wipe(); ops.model('basic','-ndm',2,'-ndf',2)
    for j,y in enumerate(ys):
        for i,x in enumerate(xs): ops.node(nid(i,j),float(x),float(y))
    L=lambda v:[float(q) for q in v]
    ops.nDMaterial('ASDConcrete3D',1,Ec,nu,'-Te',*L(Te),'-Ts',*L(Ts),'-Td',*L(Td),'-Ce',*L(Ce),'-Cs',*L(Cs),'-Cd',*L(Cd),'-implex')
    ops.nDMaterial('PlaneStress',2,1)
    ops.uniaxialMaterial('Steel02',3,fy,Es,0.01,18,0.925,0.15)
    ops.uniaxialMaterial('Steel02',4,fy_st,Es,0.01,18,0.925,0.15)
    e=1
    for j in range(ny):
        for i in range(nx):
            ops.element('enhancedQuad',e,nid(i,j),nid(i+1,j),nid(i+1,j+1),nid(i,j+1),b,'PlaneStress',2); e+=1
    jb,jt=ys.index(39),ys.index(262)
    for i in range(nx):
        ops.element('truss',e,nid(i,jb),nid(i+1,jb),A_bot,3); e+=1
        ops.element('truss',e,nid(i,jt),nid(i+1,jt),A_top,3); e+=1
    for i in range(1,nx,3):          # stirrups every 150 mm
        for j in range(jb,jt): ops.element('truss',e,nid(i,j),nid(i,j+1),A_sv,4); e+=1
    dx=xs[1]-xs[0]
    for j in range(ny+1):
        for i in range(nx+1):
            hy=(ys[min(j+1,ny)]-ys[max(j-1,0)])/2
            m=rho*b*dx*hy*(0.5 if i in (0,nx) else 1); ops.mass(nid(i,j),m,m)
    ops.fix(nid(0,0),1,1); ops.fix(nid(nx,0),0,1)
    ops.timeSeries('Linear',1); ops.pattern('Plain',1,1)
    for ic in (20,40):
        for di,w in ((-1,0.25),(0,0.5),(1,0.25)): ops.load(nid(ic+di,ny),0,-0.5*w)
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('UmfPack')
    ops.test('NormDispIncr',1e-5,100); ops.algorithm('Newton')
def step(du):
    ops.integrator('DisplacementControl',nid(20,ny),2,du); ops.analysis('Static')
    if ops.analyze(1)==0: return 0
    for alg in (('KrylovNewton',),('ModifiedNewton','-initial')):
        ops.algorithm(*alg); ok=ops.analyze(1); ops.algorithm('Newton')
        if ok==0: return 0
    return 1
state=lambda: (ops.getLoadFactor(1)/1e3, -ops.nodeDisp(nid(30,0),2))
def snap(name):
    E=[]
    for k in range(1,NE+1):
        s=np.array(ops.eleResponse(k,'stresses')).reshape(4,3).mean(0)
        d=float(np.mean([ops.eleResponse(k,'material',str(g),'damage')[0] for g in (1,2,3,4)]))
        E.append([*map(float,s),d])
    U=[ops.nodeDisp(n) for n in range(1,(nx+1)*(ny+1)+1)]
    S=[float(ops.eleResponse(NE+1+2*i,'axialForce')[0])/A_bot for i in range(nx)]
    p,dd=state(); print('SNAP',name,round(p,1),round(dd,2),flush=True)
    return dict(name=name,P=p,d=dd,E=E,U=U,steel=S)
build()
w2=ops.eigen('-genBandArpack',2); f1=float(np.sqrt(w2[0])/(2*np.pi))
mode=[[ops.nodeEigenvector(n,1,1),ops.nodeEigenvector(n,1,2)] for n in range(1,(nx+1)*(ny+1)+1)]
print('f1',round(f1,1),flush=True)
out=dict(xs=xs.tolist(),ys=ys,f1=f1,mode1=mode,snaps=[],P=[0],D=[0])
targets=[('Service load',30.0),('Cracked, before yield',55.0),('Approaching yield',76.0)]; k=0
while out['D'][-1]<45:
    if step(-0.1)!=0: print('nonconv at',out['D'][-1],flush=True); break
    p,d=state(); out['P'].append(p); out['D'].append(d)
    if len(out['P'])%20==0: print('S',round(d,2),round(p,1),flush=True)
    if k<len(targets) and p>=targets[k][1]: out['snaps'].append(snap(targets[k][0])); k+=1
    if p<0.8*max(out['P']) and d>10: break
json.dump(out,open('cont230.json','w'))
print('DONE peak',round(max(out['P']),1),flush=True)
