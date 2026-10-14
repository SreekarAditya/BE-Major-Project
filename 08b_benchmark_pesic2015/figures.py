from pathlib import Path
import runpy,os
C=runpy.run_path(str(Path(__file__).with_name('common.py')));globals().update(C)
os.environ['MPLCONFIGDIR']=str(ROOT/'.mplconfig')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
for q in (ROOT/'fonts').glob('*.ttf'):font_manager.fontManager.addfont(str(q))
plt.rcParams.update({'font.family':'Carlito','font.size':11,'figure.facecolor':'white','axes.facecolor':'white','savefig.dpi': 650,'axes.spines.top':False,'axes.spines.right':False})
H=read('h2_results.json');R=H['rows']; x=np.array([r['static_left'] for r in R]);y=np.array([r['dynamic_left'] for r in R]);lo=np.array([r['static_reading_interval_95'] for r in R]);dy=np.array([r['dynamic_reading_interval_95'] for r in R]); k=H['kappa']
fig,ax=plt.subplots(figsize=(7,5.1));ax.errorbar(x,y,xerr=np.maximum(0,np.vstack((x-lo[:,0],lo[:,1]-x))),yerr=np.maximum(0,np.vstack((y-dy[:,0],dy[:,1]-y))),fmt='o',color='#4A6C8C',ecolor='#8E1B2E',capsize=3,label='Beam 3 readable peaks; reading sensitivity')
a=np.linspace(0,1.15,100);ax.plot(a,a,color='#777777',linestyle=':',label='Equal stiffness ratios');ax.plot(a,1-k*(1-a),color='#8E1B2E',label=f'Conditional fit, kappa = {k:.3f}')
for r in R:ax.annotate(str(r['step']),(r['static_left'],r['dynamic_left']),xytext=(5,6),textcoords='offset points',fontsize=9)
ax.set(xlabel='Static stiffness / earliest readable damaged-state stiffness',ylabel='Vibration stiffness / initial vibration stiffness',xlim=(0,1.2),ylim=(0,1.15),title='Pešić: one beam with mismatched reference states')
ax.legend(loc='lower right',fontsize=9);fig.text(.12,.01,'Labels: load-step indices. Bars: bounded reading sensitivity, not population confidence.',fontsize=9);fig.tight_layout(rect=(0,.04,1,1));fig.savefig(ROOT/'01_static_vs_vibration.png');plt.close(fig)
P=read('pooled_results.json');fig,ax=plt.subplots(figsize=(7.5,4.6))
for i,r in enumerate(P['series']):
    ci=r['kappa_95_interval'];k=r['kappa'];col='#8E1B2E' if ci is None else '#4A6C8C'
    if ci is not None:ax.errorbar(k,i,xerr=[[k-ci[0]],[ci[1]-k]],fmt='o',color=col,capsize=5)
    else:ax.plot(k,i,'D',color=col);ax.text(k+.025,i,'No valid beam confidence interval',va='center',fontsize=9,color=col)
ax.set_yticks(range(len(P['series'])),[r['series']+f"\n{r['paired_beams']} paired beam(s)" for r in P['series']]);ax.invert_yaxis();ax.set(xlabel='Frequency-squared loss / static secant loss, fitted through origin',xlim=(0,.8),title='Series shown separately because definitions differ')
fig.text(.03,.01,'Bars: beam bootstrap intervals where estimable. Pešić point uses a conditional damaged baseline.',fontsize=9);fig.tight_layout(rect=(0,.05,1,1));fig.savefig(ROOT/'02_kappa_by_series.png');plt.close(fig)
save('figure_metadata.json',{'files':['01_static_vs_vibration.png','02_kappa_by_series.png'],'dpi':650,'font':'Carlito','colours':{'static':'#8E1B2E','vibration':'#4A6C8C'},'background':'white'})
