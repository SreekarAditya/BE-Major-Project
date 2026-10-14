"""Read load-displacement figures by calibrated colored pixels; save overlays.

Only the loading envelope at imposed damage displacements is used for secants.
This is a large-displacement secant proxy, not an unloaded elastic modulus.
Unloading/reloading branches are read separately at 10, 20 and 30 kN.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE=Path(__file__).resolve().parent
def dump(name,d): (HERE/name).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def clusters(ids):
    if not len(ids): return []
    return [g for g in np.split(ids,np.where(np.diff(ids)>2)[0]+1) if len(g)]
def main():
    out={'method':'Pixel line-center readings; axes calibrated from outer axes and checked against gridlines; no smoothing or fitting to table loads.', 'reading_uncertainty':{'load_kN':1.0,'displacement_mm':.5,'residual_displacement_mm':1.0,'interpretation':'Conservative reading bounds, not statistical confidence intervals. Raster line resolution is finer; figure/table differences are retained.'}, 'rows':[], 'reload_rows':[], 'residual_D1':{}, 'axes':{}, 'exclusions':[]}
    specs={4:dict(page=9,seed=(1554,3454,1748,761),box=(1370,690,3525,1930),beams=['GFRP_PreStr','CFRP_PreStr']),7:dict(page=10,seed=(1575,3476,2805,1811),box=(1390,1750,3540,2990),beams=['GFRP_PostStr','CFRP_PostStr'])}
    for fig,spec in specs.items():
        im=Image.open(HERE/f'source_pages/highres-{spec["page"]:02d}.png').convert('RGB')
        a=np.asarray(im).astype(int); dark=(a.max(2)<100)
        sx0,sx1,sy0,sy1=spec['seed']
        # Outer black border is much longer than any curve or minor tick.
        def h_axis(seed):
            ys=range(seed-18,seed+19)
            return max(ys,key=lambda y:dark[y,sx0+25:sx1-25].sum())
        def v_axis(seed):
            xs=range(seed-18,seed+19)
            return max(xs,key=lambda x:dark[sy1+25:sy0-25,x].sum())
        x0,x1,y0,y1=v_axis(sx0),v_axis(sx1),h_axis(sy0),h_axis(sy1)
        dx=(x1-x0)/100; dy=(y0-y1)/70
        out['axes'][str(fig)]=dict(source=f'p. {spec["page"]}, Figure {fig}',x0=x0,x100=x1,y0=y0,y70=y1,pixels_per_mm=dx,pixels_per_kN=dy,gridline_check='Outer frame represents 0 to 100 mm and 0 to 70 kN; ticks visually inspected on overlay.')
        masks={'GFRP_PreStr':dark,'CFRP_PreStr':(a[:,:,2]>130)&(a[:,:,0]<100)&(a[:,:,2]-a[:,:,0]>80), 'GFRP_PostStr':(a[:,:,1]>120)&(a[:,:,0]<110)&(a[:,:,1]-a[:,:,0]>70)&(a[:,:,1]>a[:,:,2]*1.15), 'CFRP_PostStr':(a[:,:,0]>150)&(a[:,:,1]<130)&(a[:,:,2]<100)}
        draw=ImageDraw.Draw(im)
        font=ImageFont.truetype(str(HERE/'fonts/Carlito-Regular.ttf'),28)
        def mark(x,y,label,color):
            draw.ellipse((x-9,y-9,x+9,y+9),outline=color,width=4)
            draw.text((x+12,y+7),label,fill=color,font=font,stroke_width=1)
        draw.rectangle((x0,y1,x1,y0),outline='#8E1B2E',width=3)
        for mm in [0,10,20,30,45,60,75,100]:
            x=x0+dx*mm
            draw.line((x,y0,x,y0+12),fill='#8E1B2E',width=3)
        for beam in spec['beams']:
            mask=masks[beam]
            levels=[('D1',30),('D2',45),('D3',60),('D4',75)]
            if beam=='CFRP_PreStr': levels=levels[:1]
            if beam=='CFRP_PostStr': levels=levels[:2]
            for stage,delta in levels:
                # Figure 7 at x=30 contains both bare and repaired branches.
                # Select the bare 40-46 kN band explicitly, not the maximum.
                lo,hi=(41,44) if beam=='GFRP_PostStr' and stage=='D1' else (42,46) if beam=='CFRP_PostStr' and stage=='D1' else (38,68)
                # Read 0.4 mm left of the target, within the declared 0.5 mm
                # bound, to avoid vertical force drops at a cycle endpoint.
                offset=1.0 if beam=='CFRP_PostStr' and stage=='D1' else .4
                x=int(round(x0+dx*(delta-offset))); ylo=int(y0-hi*dy); yhi=int(y0-lo*dy)
                # Single-column centers prevent nearby sloping branches from
                # merging across a five-column window. At carbon bare D1 the
                # plateau is obscured at 30 mm; use 29 mm with a 1 mm bound.
                cand=clusters(np.where(mask[ylo:yhi+1,x])[0]+ylo)
                cand=[g for g in cand if len(g)<25]
                if not cand:
                    out['exclusions'].append(dict(beam=beam,stage=stage,reason='No isolated colored curve at imposed displacement')); continue
                group=cand[-1] if 'Post' in beam and stage=='D1' else cand[0]
                y=float(np.mean(group)); P=(y0-y)/dy
                row=dict(beam=beam,stage=stage,condition='bare' if 'Post' in beam and stage=='D1' else 'strengthened',displacement_mm=delta,pixel_read_displacement_mm=(x-x0)/dx,load_kN=float(P),pixel_x=x,pixel_y=y,source=f'p. {spec["page"]}, Figure {fig}',reading_uncertainty_load_kN=out['reading_uncertainty']['load_kN'],reading_uncertainty_displacement_mm=max(offset,out['reading_uncertainty']['displacement_mm']),candidate_loads_kN=[float((y0-g.mean())/dy) for g in cand],branch_rule='Bare plateau isolated in an explicit load band near D1 for post beams; upper loading envelope otherwise. Read slightly left of target within stated displacement bound; carbon bare D1 is extrapolated over a nearly flat 1 mm segment.')
                out['rows'].append(row)
                mark(x,y,stage,'#8E1B2E')
            # Read intersections of isolated colored traces with horizontal
            # load rows. Specific cycle windows disambiguate repeated branches.
            windows=[('D1',6,31),('D2',22,46),('D3',37,61),('D4',50,77)] if 'Post' in beam else [('D1',5,31),('D2',20,46),('D3',35,61),('D4',49,77)]
            if beam=='CFRP_PreStr': windows=windows[:1]
            if beam=='CFRP_PostStr': windows=windows[:2]
            for stage,dl,dh in windows:
                reads=[]
                for P in [10,20,30]:
                    y=int(round(y0-P*dy)); xl=int(x0+dl*dx); xh=int(x0+dh*dx)
                    gs=clusters(np.where(mask[y-1:y+2,xl:xh+1].any(0))[0]+xl)
                    gs=[g for g in gs if len(g)<30]
                    # Two expected branches: ascending/reloading at left,
                    # unloading at right. Nearby next-cycle branches can also
                    # enter a window; use two rightmost for the chosen cycle.
                    if len(gs)>=2:
                        gs=gs[-2:]
                        xs=[float(g.mean()) for g in gs]
                        reads.append(dict(load_kN=P,reload_mm=(xs[0]-x0)/dx,unload_mm=(xs[1]-x0)/dx,pixel_x_reload=xs[0],pixel_x_unload=xs[1],pixel_y=y,number_of_branches=len(gs)))
                        # Attempted reloading readings remain in JSON, not on
                        # the accepted secant overlay, to avoid implying
                        # that ambiguous branch associations were accepted.
                # Retain readings for auditing; manual review must approve
                # branch association before any unloading slope is used.
                out['reload_rows'].append(dict(beam=beam,stage=stage,source=f'p. {spec["page"]}, Figure {fig}',readings=reads,status='not_used_branch_association_ambiguous',reason='Overlapping cyclic branches and repaired paths are not time labelled; envelope secants only used for H2.'))
            if 'Post' in beam:
                # Residual from first bare cycle, endpoint nearest x~14 mm.
                # At 0.5 kN the trace can be distinguished from the black axis;
                # extrapolate last 0.5 kN using terminal unloading slope.
                rr=[]
                for P in [.5,1,2,5]:
                    y=int(round(y0-P*dy)); xl=int(x0+11*dx); xh=int(x0+18*dx)
                    gs=clusters(np.where(mask[y-1:y+2,xl:xh+1].any(0))[0]+xl)
                    if gs:
                        x=float(gs[0].mean()); rr.append(dict(load_kN=P,displacement_mm=(x-x0)/dx,pixel_x=x,pixel_y=y))
                        draw.ellipse((x-6,y-6,x+6,y+6),outline='#777777',width=3)
                if len(rr)>=2:
                    coeff=np.polyfit([r['load_kN'] for r in rr],[r['displacement_mm'] for r in rr],1)
                    out['residual_D1'][beam]=dict(value_mm=float(coeff[1]),reading_uncertainty_mm=1.0,source=f'p. {spec["page"]}, Figure {fig}, first bare unloading branch',inferred=True,reasoning='Extrapolated low-force colored branch to zero force; shape is not a residual strain field.',read_points=rr)
        crop=im.crop(spec['box']); crop.save(HERE/f'figure{fig}_overlay.png')
        Image.open(HERE/f'source_pages/highres-{spec["page"]:02d}.png').crop(spec['box']).save(HERE/f'source_pages/figure{fig}_600dpi.png')
    # Audit the early secant implied by first-crack table values against the
    # raster at that displacement. Discrepancies are reported, not corrected.
    D=json.loads((HERE/'ozturkoglu_extract.json').read_text())
    out['initial_static_stiffness']={}
    for beam in D['modal']:
        s=D['static'][beam if 'Pre' in beam else beam+'_bare']
        P=s['crack_load_kN']['value']; d=s['crack_displacement_mm']['value']
        out['initial_static_stiffness'][beam]=dict(K0_kN_mm=P/d,source='p. 11, Table 4, first-crack load / displacement',definition='Secant up to first crack, used as baseline proxy; no undamaged static tangent reported.',P_kN=P,delta_mm=d)
    dump('digitised_static.json',out)
    print('Digitised',len(out['rows']),'damage endpoints; residual offsets', {k:round(v['value_mm'],2) for k,v in out['residual_D1'].items()})

if __name__=='__main__':main()
