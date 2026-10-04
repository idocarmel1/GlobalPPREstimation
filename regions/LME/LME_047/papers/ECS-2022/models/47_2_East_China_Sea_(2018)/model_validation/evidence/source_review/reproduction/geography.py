from pathlib import Path
import json,shutil,hashlib
import numpy as np
from shapely.geometry import shape,mapping,Polygon,Point
from shapely.ops import unary_union
from pyproj import Geod
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw
ROOT=Path.cwd();Q=Path(__file__).parent;R=ROOT/'regions/LME_047';G=R/'validation_reports/47_2_East_China_Sea_(2018)/geography';G.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(G/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
target=next(f for f in json.loads((ROOT/'common_reference_data/geography/LMEs.geojson').read_text(encoding='utf-8'))['features']if f['properties']['region_id']==47)
tg=shape(target['geometry']);land=unary_union([shape(f['geometry'])for f in json.loads((ROOT/'common_reference_data/geography/basemaps/ne_50m_land.geojson').read_text(encoding='utf-8'))['features']])
shutil.copy2(R/'papers/ECS-2022/footprint.geojson',G/'historical_whole_LME_envelope.geojson');shutil.copy2(Q/'figure1_raw.png',G/'original_figure1.png')
# Pixel coordinates recorded on the original 2559x2361 embedded image. Tick positions are native, not resampled pixels.
cal={'longitude_ticks':[{'pixel_x':478,'longitude':120},{'pixel_x':1547,'longitude':125}], 'latitude_ticks':[{'pixel_y':157,'latitude':30},{'pixel_y':1227,'latitude':25},{'pixel_y':2295,'latitude':20}]}
xs=np.array([r['pixel_x']for r in cal['longitude_ticks']]);xx=np.array([r['longitude']for r in cal['longitude_ticks']]);ys=np.array([r['pixel_y']for r in cal['latitude_ticks']]);yy=np.array([r['latitude']for r in cal['latitude_ticks']]);cx=np.polyfit(xs,xx,1);cy=np.polyfit(ys,yy,1)
half=[(241,513),(253,501),(286,502),(306,452),(330,439),(353,419),(375,378),(412,345),(449,310),(477,293),(496,265),(508,224),(520,225),(537,237),(565,241),(612,251),(666,257),(718,270),(771,280),(826,288),(872,292),(879,307),(877,349),(829,392),(769,451),(705,464),(627,482),(550,501),(471,518),(393,536),(347,553),(294,559),(267,536),(241,513)]
px=[(round(x*2559/1280),round(y*2361/1180))for x,y in half];ll=[(float(np.polyval(cx,x)),float(np.polyval(cy,y)))for x,y in px]
poly=Polygon(ll);assert poly.is_valid;marine=poly.difference(land);over=tg.intersection(marine);geod=Geod(ellps='WGS84')
def area(g):
 if g.geom_type=='Polygon':return abs(geod.geometry_area_perimeter(g)[0])/1e6
 return sum(area(p)for p in g.geoms)
S=area(marine);T=area(tg);I=area(over);aa=100*I/T;bb=100*I/S
controls=[('interior shelf',123,27,True),('western shelf',121,26,True),('northeastern hatch',125,27.5,True),('northern beyond hatch',123,29,False),('coast-water gap',120.3,27,False),('southern Taiwan water',122,25,False),('southeastern bend water',124.5,26.7,True),('west notch below northern bend',122.3,28.4,False)]
check=[]
for n,x,y,e in controls:
 actual=marine.covers(Point(x,y));check.append({'name':n,'lon':x,'lat':y,'expected_inside':e,'actual_inside':actual,'passed':actual==e})
assert all(r['passed']for r in check),check
write('calibration_and_controls.json',{'native_image_dimensions':[2559,2361],'image_sha256':sha(G/'original_figure1.png'),'ticks':cal,'affine_lon_coefficients':cx.tolist(),'affine_lat_coefficients':cy.tolist(),'lat_tick_residual_degrees':(np.polyval(cy,ys)-yy).tolist(),'ordered_pixel_vertices':px,'ordered_lonlat_vertices':ll,'water_controls':check,'source_fidelity':'The hatch has an offshore gap from the mainland shoreline; that gap is preserved. All western bends, southern arc and northeastern sloping edge retained; no unrelated blue line or inset geometry used. Pixel precision is not geographic accuracy.'})
for n,geo in [('target_region',tg),('source_outer_outline',poly),('study_area_reconstructed',marine),('overlap',over)]:write(n+'.geojson',{'type':'Feature','properties':{'label':n,'method':'native Figure1 graticule trace'if n!='target_region'else'SAU target LME47','approximate':n!='target_region'},'geometry':mapping(geo)})
def plotgeom(ax,g,**kw):
 if g.geom_type=='Polygon':a=np.asarray(g.exterior.coords);ax.plot(a[:,0],a[:,1],**kw)
 else:
  for p in g.geoms:plotgeom(ax,p,**kw)
def fillgeom(ax,g,color,alpha=1):
 if g.geom_type=='Polygon':a=np.asarray(g.exterior.coords);ax.fill(a[:,0],a[:,1],color=color,alpha=alpha)
 else:
  for p in g.geoms:fillgeom(ax,p,color,alpha)
for f,only in [('target_region.png',True),('comparison.png',False)]:
 fig,ax=plt.subplots(figsize=(7.5,6));fillgeom(ax,land,'#eeeeea');plotgeom(ax,tg,color='#475b6a',linewidth=1.6,label='Target LME47')
 if not only:
  fillgeom(ax,marine,'#49a1b8',.48);plotgeom(ax,marine,color='#006a86',linewidth=1.2)
 ax.set(xlim=(117,131),ylim=(23,34),xlabel='Longitude (°E)',ylabel='Latitude (°N)',title='East China Sea target'+(''if only else' and approximate Figure1 study footprint'));ax.set_aspect(1/np.cos(np.deg2rad(28.5)));ax.grid(alpha=.2);fig.tight_layout();fig.savefig(G/f,dpi=160);plt.close(fig)
im=Image.open(G/'original_figure1.png').convert('RGB');dr=ImageDraw.Draw(im);dr.line(px,fill='#c32132',width=5)
for r in check:
 x=(r['lon']-cx[1])/cx[0];y=(r['lat']-cy[1])/cy[0];dr.ellipse((x-10,y-10,x+10,y+10),fill='#168a49'if r['expected_inside']else'#bd3737')
im.save(G/'calibrated_trace_overlay.png')
caption='FIGURE 1 | The study area in the East China Sea.'
passage='The second model data were from a joint survey in the ECS in the autumn of 2018 and the spring of 2019.'
assessment={'target_area_km2':T,'reconstructed_study_marine_area_km2':S,'intersection_area_km2':I,'A_percent':aa,'B_percent':bb,'report_A_range':'10–15%','report_B_range':'90–100%','source_caption':caption,'methods_passage':passage,'source_locations':'Xu2022 Figure1 PDF3; §2.2 PDF4','modeled_extent_limit':'The paper labels the hatched footprint study area and identifies the joint ECS survey for M2018. It does not supply survey station coordinates, modeled-area km², a separate explicit model boundary, or an explicit assertion of whole-LME representativeness. This reconstruction measures the displayed study/survey footprint, not a verified exact native model boundary. The broader ECS description is contextual.','land_mask':'Natural Earth ne_50m means1:50million cartographic scale; it is not50metre resolution. Same land mask applied to source trace; target boundary preserved.','uncertainty':'Approximate graticule tracing/registration, hatch edge thickness and coarse coastlines. Percent ranges are descriptive, not statistical intervals. Coverage is not a PPR multiplier.','prior_geometry':'Whole-LME envelope preserved as historical evidence only; proposed replacement is calibrated article study footprint.','controls_passed':all(r['passed']for r in check)}
write('geographic_assessment.json',assessment);print('GEOGRAPHY',aa,bb,S,T)

