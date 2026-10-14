import json, numpy as np, openseespy.opensees as ops
exec(open('fibre.py').read().split("out={}")[0])
def step2(du):
    ops.integrator('DisplacementControl',nmid,2,du); ops.analysis('Static')
    for alg in (('Newton',),('KrylovNewton',),('NewtonLineSearch',),('ModifiedNewton','-initial')):
        ops.algorithm(*alg); 
        if ops.analyze(1)==0: ops.algorithm('Newton'); return 0
    return 1
build('jacket'); f0=freq(1)[0]; P=[0];D=[0];M=[0];K=[0]; ops.test('NormDispIncr',1e-6,200)
while D[-1]<60:
    if step2(-0.05)!=0:
        if step2(-0.01)!=0: print('stop',D[-1]); break
    p,d=state(); P.append(p); D.append(d); M.append(abs(ops.sectionForce(12,5,2))/1e6); K.append(abs(ops.sectionDeformation(12,5,2))*1e3)
    if p<0.8*max(P) and d>8: break
o=json.load(open('fibre.json')); o['jacket']=dict(f0=f0,P=P,D=D,M=M,K=K); json.dump(o,open('fibre.json','w'))
i=int(np.argmax(P)); print('jacket',round(P[i],1),round(D[i],1),round(D[-1],1))
