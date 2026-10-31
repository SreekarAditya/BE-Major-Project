import subprocess, json, sys
pdf='StrucIQ_Project_Part1_Report.pdf'
N=int(subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout.split('Pages:')[1].split()[0])
pg=[' '.join(subprocess.run(['pdftotext','-f',str(i),'-l',str(i),pdf,'-'],capture_output=True,text=True).stdout.split()) for i in range(1,N+1)]
keys={'ack':'ACKNOWLEDGEMENTS The authors','abs':'ABSTRACT Visual','lof':'LIST OF FIGURES Figure','lot':'LIST OF TABLES Table','nom':'NOMENCLATURE',
'ch1':'CHAPTER 1: INTRODUCTION 1.1','s11':'1.1 Background and Need for the Study Reinforced','s12':'1.2 Present State of Knowledge Vibration','s13':'1.3 Gap Identified Three','s14':'1.4 Aim, Objectives and Hypotheses Aim',
'ch2':'CHAPTER 2: LITERATURE REVIEW We','ch3':'CHAPTER 3: METHODOLOGY 3.1','s31':'3.1 Description of Location The','s32':'3.2 Specimen and Materials A','s33':'3.3 Methodology The',
'ch4':'CHAPTER 4: RESULTS AND DISCUSSION 4.1','s41':'4.1 Stiffness Left After Loading (H1) All','s42':'4.2 Vibration Against Deflection (H2) With','s43':'4.3 Twin Accuracy (H3) H3 states','s44':'4.4 Blind Validation Against a Published Test The test beam','s45':'4.5 Retrofit Simulation Across','s46':'4.6 Repair Rule for the Specimens All','s34':'3.4 Design-Space Dataset The model','s47':'4.7 Design-Space Dataset Across','anA':'ANNEXURE Table A-1: Ranges',
'ch5':'CHAPTER 5: CONCLUSIONS Nominally','ref':'REFERENCES American','ch6':'CHAPTER 6: WORK PROGRESS Part','ch7':'CHAPTER 7: ACHIEVEMENTS',
'f1':'Figure 1. Specimen elevation and cross-section','f2':'Figure 2. Methodology flow diagram','f3':'Figure 3. Sobol total indices of the stiffness left after 72 kN Figure','f4':'Figure 4. Median deflection error at 72 kN for four estimators','f5':'Figure 5. Least intrusive compliant scheme across 10,000 beams','f6':'Figure 6. Share of beams where each scheme complies, by strength increase needed','f7':'Figure 7. Gantt chart of the project, July','f8':'Figure A-1. Static against vibration','f9':'Figure A-2. Growth of deflection',
't1':'Table 1. Hypotheses and their status at the end','t2':'Table 2. Summary of key studies Study','t3':'Table 3. Materials and random inputs of the Monte Carlo simulation Material','t4':'Table 4. Deflection stiffness left at three load levels (300','t5':'Table 5. Blind prediction against the test','t6':'Table 6. Decision tree performance Measure','t7':'Table 7. Repair rule for the specimens Class','t8':'Table 8. Achievements of Part 1 No.','t9':'Table A-1. Ranges of the design-space','t10':'Table A-2. Stiffness left and vibration','t11':'Table A-3. Condition stages','tb1':'Table A-4. Mesh convergence','tb2':'Table A-5. Predicted and measured'}
out={'decl':'2','cert':'3'}; miss=[]
for k,s in keys.items():
    h=[i+1 for i,p in enumerate(pg) if s.lower() in p.lower() and (i+1)>=4 and (i+1 not in (6,7,8) or k in ('lof','lot'))]
    if h: out[k]=str(h[0])
    else: miss.append(k)
def roman(n):
    out='';
    for v,r in ((10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')):
        while n>=v: out+=r; n-=v
    return out
c1=int(out['ch1'])
out={k:(roman(int(v)-1) if int(v)<c1 else str(int(v)-c1+1)) for k,v in out.items()}
old=json.load(open('pages.json'))
json.dump(out,open('pages.json','w'))
print('missing',miss,'changed',{k:(old.get(k),v) for k,v in out.items() if old.get(k)!=v})
