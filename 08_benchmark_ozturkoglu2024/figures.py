"""Reproducible StrucIQ figures, Carlito, white, PNG at 650 dpi."""
from pathlib import Path
import os,json
HERE=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(HERE/'.mplconfig')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
def load(n):return json.loads((HERE/n).read_text())
def main():
    for p in (HERE/'fonts').glob('*.ttf'):font_manager.fontManager.addfont(str(p))
    plt.rcParams.update({'font.family':'Carlito','font.size':11,'axes.titlesize':13,'axes.titleweight':'bold','axes.labelsize':11,'legend.fontsize':9,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.16,'savefig.dpi': 650})
    maroon,blue,gray='#8E1B2E','#4A6C8C','#777777'
    F,H,R=load('frp_results.json'),load('h1_h2_results.json'),load('retrofit_signal_results.json')
    P=[r for r in F['strengthened'] if r['representation']=='fiber_equivalent']
    fig,axs=plt.subplots(1,2,figsize=(12,6.8))
    ax=axs[0];ax.plot([30,75],[30,75],color=gray,ls='--',lw=1,label='Equal prediction and test')
    primary=[r for r in P if r['initial_strain_case']!='residual_global_curvature_proxy']
    labels={'GFRP_PreStr':'Glass before damage','CFRP_PreStr':'Carbon before damage','GFRP_PostStr':'Glass after damage','CFRP_PostStr':'Carbon after damage'}
    offsets={'GFRP_PreStr':(8,15),'CFRP_PreStr':(-8,16),'GFRP_PostStr':(8,-21),'CFRP_PostStr':(-8,-26)}
    for i,r in enumerate(primary):
        u=r['ultimate'];ax.scatter(u['test_P_kN'],u['P_jack_kN'],s=65,color=maroon,marker='o',label='Fiber-equivalent primary' if i==0 else None,zorder=3)
        dx,dy=offsets[r['beam']];ax.annotate(labels[r['beam']],(u['test_P_kN'],u['P_jack_kN']),xytext=(dx,dy),textcoords='offset points',fontsize=9,ha='left' if dx>0 else 'right',arrowprops=dict(arrowstyle='-',color=gray,lw=.6))
    for i,r in enumerate([r for r in P if r['initial_strain_case']=='residual_global_curvature_proxy']):
        u=r['ultimate'];ax.scatter(u['test_P_kN'],u['P_jack_kN'],s=65,facecolors='white',edgecolors=maroon,marker='D',label='Residual-curvature proxy' if i==0 else None,zorder=4)
    for i,r in enumerate(F['bare']):
        ax.scatter(r['test_ultimate_kN'],r['IS456_shape_ultimate']['P_jack_kN'],s=55,color=gray,marker='s',label='Bare, conditional code shape' if i==0 else None,zorder=3)
    ax.set(xlim=(30,75),ylim=(30,75),xlabel='Published observed peak load (kN)',ylabel='Predicted jack load (kN)',title='Conditional ultimate capacities');ax.set_aspect('equal')
    handles,labs=ax.get_legend_handles_labels();fig.legend(handles,labs,loc='lower center',bbox_to_anchor=(.27,.075),ncol=1,frameon=False)
    ax=axs[1];ax.plot([35,100],[35,100],color=gray,ls='--',lw=1,label='Equal prediction and test')
    for representation,color,marker,label in [('fiber_equivalent',maroon,'o','Fiber-equivalent primary'),('dominant_direction_sensitivity',gray,'^','Dominant-fiber sensitivity'),('gross_thickness_diagnostic',blue,'x','Gross thickness + fiber modulus\n(invalid material pairing)')]:
        rr=[r for r in F['strengthened'] if r['representation']==representation and r['initial_strain_case']!='residual_global_curvature_proxy']
        for i,r in enumerate(rr):ax.scatter(r['ultimate']['test_P_kN'],r['ultimate']['P_jack_kN'],color=color,marker=marker,s=55,label=label if i==0 else None,zorder=3)
    ax.set(xlim=(35,100),ylim=(35,100),xlabel='Published observed peak load (kN)',ylabel='Predicted jack load (kN)',title='Material-basis sensitivity');ax.set_aspect('equal')
    handles,labs=ax.get_legend_handles_labels();fig.legend(handles,labs,loc='lower center',bbox_to_anchor=(.75,.075),ncol=1,frameon=False)
    fig.suptitle('Published beam benchmark: keep input assumptions visible',fontsize=16,fontweight='bold')
    fig.text(.5,.025,'Approximate mean properties; inferred fiber thickness; no safety factors.\nBare observed peaks precede strengthening. Residual curvature is an assumption, not a measured strain field.',ha='center',fontsize=10,color=gray)
    fig.tight_layout(rect=(0,.27,1,.94));fig.savefig(HERE/'01_capacity_predicted_vs_test.png',dpi=650);plt.close(fig)
    fig,axs=plt.subplots(2,2,figsize=(11.8,8.0),sharey=True)
    for ax,(beam,modal) in zip(axs.flat,load('ozturkoglu_extract.json')['modal'].items()):
        rr=[r for r in H['rows'] if r['beam']==beam];x=np.array([int(r['stage'][1:]) for r in rr]);s=np.array([r['static_left'] for r in rr]);v=np.array([r['vibration_mode1_left'] for r in rr]);v2=np.array([r['vibration_mode2_left'] for r in rr]);lo=np.array([r['static_left_reading_bounds'][0] for r in rr]);hi=np.array([r['static_left_reading_bounds'][1] for r in rr]);mus=H['H2']['Musial_reference']
        # Comparison band applies the earlier kappa range to this secant loss;
        # it is not a confidence band or a fitted result for these specimens.
        ax.fill_between(x,1-mus['kappa_raw']*(1-s),1-mus['kappa_compliance_corrected']*(1-s),color=gray,alpha=.17,label='Earlier kappa comparison band')
        ax.errorbar(x,s,yerr=[s-lo,hi-s],color=maroon,marker='o',capsize=3,lw=1.8,label='Static envelope secant proxy')
        ax.plot(x,v,color=blue,marker='s',lw=1.8,label='Vertical vibration mode 1')
        ax.plot(x,v2,color=blue,marker='^',ls=':',lw=1.6,label='Vertical vibration mode 2')
        if 'Post' in beam:
            sr=modal['frequency_ratios']['D1_strengthened']['vertical']['value']
            ax.scatter([1],[sr[0]**2],facecolor='white',edgecolor=blue,marker='D',s=60,zorder=5,label='After bonding at D1: modal only')
            ax.axvline(1.18,color=gray,ls='--',lw=.8)
        ax.set(title=labels[beam],xlabel='Imposed damage level',ylim=(0,1.08),xlim=(.8,4.2),xticks=[1,2,3,4],xticklabels=['D1','D2','D3','D4']);ax.set_ylabel('Ratio to baseline')
    handles,labs=axs[1,0].get_legend_handles_labels();fig.legend(handles,labs,loc='lower center',bbox_to_anchor=(.5,.07),ncol=3,frameon=False)
    k=H['H2']['fits']['mode1'];fig.suptitle(f'Static secant proxy and vibration: kappa = {k["pooled"]:.3f}',fontsize=16,fontweight='bold')
    fig.text(.5,.025,'Error bars: source-reading bounds, not confidence intervals. Plastic displacement remains in secants.\nPost beams are bare at D1; immediate after-bonding static checks are unavailable.',ha='center',fontsize=10,color=gray)
    fig.tight_layout(rect=(0,.18,1,.94));fig.savefig(HERE/'02_static_vs_vibration.png',dpi=650);plt.close(fig)
    # A third figure makes the asymmetric retrofit result easy to review.
    fig,ax=plt.subplots(figsize=(9,4.8));rr=[r for r in R['rows'] if r['direction']=='vertical'];x=np.arange(3);width=.35
    for i,beam in enumerate(['GFRP_PostStr','CFRP_PostStr']):
        yy=[r['frequency_change_pct'] for r in rr if r['beam']==beam];bars=ax.bar(x+(i-.5)*width,yy,width,color=maroon if i==0 else blue,label='Glass after damage' if i==0 else 'Carbon after damage')
        for bar,n in zip(bars,yy):ax.annotate(f'{n:+.1f}%',(bar.get_x()+bar.get_width()/2,n),xytext=(0,4 if n>=0 else -14),textcoords='offset points',ha='center',fontsize=10)
    ax.axhline(0,color=gray,lw=.8);ax.set(xticks=x,xticklabels=['Vertical mode 1','Vertical mode 2','Vertical mode 3'],ylim=(-11.5,15),ylabel='Frequency change after bonding (%)',title='Vibration sees a change, but cannot confirm static repair');ax.legend(frameon=False)
    fig.text(.5,.02,'Same D1 damage history, before and after strengthening. A matched static check is still required.',ha='center',fontsize=10,color=gray)
    fig.tight_layout(rect=(0,.06,1,1));fig.savefig(HERE/'03_retrofit_vertical_signal.png',dpi=650);plt.close(fig)
    style=dict(font='Carlito',dpi=650,background='white',maroon=maroon,blue=blue,files=['01_capacity_predicted_vs_test.png','02_static_vs_vibration.png','03_retrofit_vertical_signal.png'])
    (HERE/'figure_settings.json').write_text(json.dumps(style,indent=2)+'\n')
    print('Wrote',len(style['files']),'figures with Carlito at 650 dpi.')

if __name__=='__main__':main()
