import numpy as np, json
from p import *
fc_cyl=0.8*fck
Ig=b*h**3/12; Mcr=ft*Ig/(h/2)
m=Es/Ec
k=(-m*A_bot+np.sqrt((m*A_bot)**2+2*b*m*A_bot*d_eff))/b; Icr=b*k**3/3+m*A_bot*(d_eff-k)**2
My=A_bot*fy*(d_eff-k/3)
P=lambda M: 2*M/a/1e3
def conc(c,bw,fc,ec):
    n=400; y=np.linspace(0,c,n); dy=c/n; e=ec*(1-y/c)
    s=np.where(e<0.002,fc*(2*e/0.002-(e/0.002)**2),fc); F=np.sum(s*bw*dy); return F,np.sum(s*bw*dy*y)/max(F,1e-9)
def cap(bw,H,steel,design,extra=None,efd=None):
    fc=0.67*fck/1.5 if design else 0.85*fc_cyl; gs=1/0.87 if design else 1.0
    best=None
    for mode in ('crush','debond'):
        if mode=='debond' and (extra is None or efd is None): continue
        lo,hi=1.,H
        ok=True
        for _ in range(90):
            c=(lo+hi)/2
            if mode=='crush': ec=0.0035
            else:
                ec=efd*c/(extra['y']-c)
                if ec>0.0035: ok=False; break
            F,yc=conc(c,bw,fc,ec); T=M=0
            for A,y,fy_,E in steel:
                e=ec*(y-c)/c; s=np.clip(E*e,-fy_/gs,fy_/gs); T+=A*s; M+=A*s*(y-yc)
            if extra is not None:
                e=ec*(extra['y']-c)/c
                if efd is not None: e=min(e,efd)
                s=extra['E']*e*(0.85 if design else 1.0)
                if 'fy' in extra: s=min(s,extra['fy']/gs)
                T+=extra['A']*s; M+=extra['A']*s*(extra['y']-yc)
            if T>F: lo=c
            else: hi=c
        if not ok: continue
        r=(M/1e6,c,ec,mode)
        if best is None or r[0]<best[0]: best=r
    return best
# depth measured from top fibre
st_base=[(A_bot,h-y_bot,fy,Es),(A_top,h-y_top,fy,Es)]
out={}
out['section']=dict(b=b,h=h,span=span,a=a,d=d_eff,Ast=A_bot,pt=100*A_bot/(b*d_eff),Ec=Ec,ft=ft,Ig=Ig,Icr=Icr,Icr_Ig=Icr/Ig,kd=k)
xu=fy*A_bot/(0.54*fck*b); xumax=0.46*d_eff
Mud=0.87*fy*A_bot*d_eff*(1-A_bot*fy/(b*d_eff*fck))
Mue=cap(b,h,st_base,False)[0]
out['bare']=dict(Mcr=Mcr/1e6,Pcr=P(Mcr),My=My/1e6,Py=P(My),Mu_design=Mud/1e6,P_design=P(Mud),Mu_expected=Mue,P_expected=P(Mue*1e6),xu=xu,xu_max=xumax)
# shear
def tauc(pt):
    beta=max(0.8*fck/(6.89*pt),1.0); return 0.85*np.sqrt(0.8*fck)*(np.sqrt(1+5*beta)-1)/(6*beta)
Vc=tauc(100*A_bot/(b*d_eff))*b*d_eff; Vs=0.87*fy_st*A_sv*d_eff/s_st
out['shear']=dict(Vc=Vc/1e3,Vs=Vs/1e3,Vu=(Vc+Vs)/1e3,demand_at_expected=P(Mue*1e6)/2)
# frequency
mass=2500*b*h*1e-9*1e3  # kg per m? compute kg/m
mass=2500*(b/1000)*(h/1000)
EI=Ec*Ig*1e-9*1e-3*1e3  # N m2 : Ec[N/mm2]*Ig[mm4] = N mm2 -> *1e-6 = N m2
EI=Ec*Ig*1e-6
f1=np.pi/(2*(span/1000)**2)*np.sqrt(EI/mass)
out['dynamics']=dict(mass_kg_per_m=mass,EI_kNm2=EI/1e3,f1=f1,f2=4*f1,f1_fully_cracked=f1*np.sqrt(Icr/Ig))
# repairs
fc_cyl=0.8*fck
efd=0.41*np.sqrt(fc_cyl/(1*frp['E']*frp['t']))
frp_x=dict(A=frp['n']*frp['w']*frp['t'],y=h,E=frp['E'])
plate_x=dict(A=plate['w']*plate['t'],y=h+plate['t']/2,E=Es,fy=plate['fy'])
Bj,Hj=b+2*jacket['t'],h+jacket['t']
st_j=st_base+[(jacket['n']*np.pi*jacket['d']**2/4,Hj-(cover+dst+jacket['d']/2),fy,Es)]
R={}
for name,(bw,H,st,ex,ef) in {'Fibre-reinforced polymer strips':(b,h,st_base,frp_x,efd),'Bonded steel plate':(b,h,st_base,plate_x,None),'Concrete jacket':(Bj,Hj,st_j,None,None)}.items():
    d_=cap(bw,H,st,True,ex,ef); e_=cap(bw,H,st,False,ex,ef)
    R[name]=dict(Mu_design=d_[0],P_design=P(d_[0]*1e6),Mu_expected=e_[0],P_expected=P(e_[0]*1e6),mode=e_[3])
# FRP: check strain at crushing to decide mode properly
c_cr=cap(b,h,st_base,False,dict(frp_x),None)[1]
R['Fibre-reinforced polymer strips']['strain_at_crushing']=0.0035*(h-c_cr)/c_cr
R['Fibre-reinforced polymer strips']['debond_strain']=efd
out['repairs']=R
Vcj=tauc(min(100*st_j[0][0]/(Bj*(Hj-39)),3))*Bj*(Hj-45); Vsj=0.87*fy_st*A_sv*(Hj-45)/s_st
out['shear_jacket']=dict(Vu=(Vcj+Vsj)/1e3)
# deflections (Branson and IS 456 Annex C) at chosen loads
defl=lambda Pt,EI_: (Pt/2)*a*(3*span**2-4*a**2)/(24*EI_)
rows=[]
for Pt in np.linspace(1,0.97*P(Mue*1e6),60):
    Ma=Pt*1e3*a/2
    Ie=Ig if Ma<=Mcr else (Mcr/Ma)**3*Ig+(1-(Mcr/Ma)**3)*Icr
    z=d_eff-k/3; Ii=Ig if Ma<=Mcr else min(Ig,max(Icr,Icr/(1.2-(Mcr/Ma)*(z/d_eff)*(1-k/d_eff))))
    rows.append((Pt,defl(Pt*1e3,Ec*Ie),defl(Pt*1e3,Ec*Ii)))
out['deflection_curves']=rows
json.dump(out,open('calc.json','w'),indent=1)
for k_,v in out.items():
    if k_!='deflection_curves': print(k_,json.dumps(v,indent=None,default=float)[:600])
# --- FRP: debonding governs when strain at crushing exceeds the ACI 440.2R debonding strain; solve that mode explicitly
def frp_debond(design):
    fc=0.67*fck/1.5 if design else 0.85*fc_cyl; gs=1/0.87 if design else 1.0; psi=0.85 if design else 1.0
    lo,hi=1.,h-1
    for _ in range(100):
        c=(lo+hi)/2; ec=efd*c/(h-c); F,yc=conc(c,b,fc,ec); T=M=0
        for A,y,fy_,E in st_base:
            e=ec*(y-c)/c; s=np.clip(E*e,-fy_/gs,fy_/gs); T+=A*s; M+=A*s*(y-yc)
        Tf=frp_x['A']*frp['E']*efd*psi; T+=Tf; M+=Tf*(h-yc)
        if T>F: lo=c
        else: hi=c
    return M/1e6,c,ec
r=out['repairs']['Fibre-reinforced polymer strips']
if r['strain_at_crushing']>efd:
    Md,_,_=frp_debond(True); Me,c,ec=frp_debond(False)
    r.update(Mu_design=Md,P_design=P(Md*1e6),Mu_expected=Me,P_expected=P(Me*1e6),mode='debond',concrete_strain_at_debond=ec)
json.dump(out,open('calc.json','w'),indent=1)
for k_,v in out['repairs'].items(): print(k_,{kk:(round(vv,3) if isinstance(vv,float) else vv) for kk,vv in v.items()})
