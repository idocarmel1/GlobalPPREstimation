import json,sys,shutil
from pathlib import Path
import numpy as np,matplotlib.pyplot as plt,pymupdf
from shapely.geometry import shape,Polygon,mapping,Point
from pyproj import Geod
Q=Path(__file__).parent;ROOT=Q.parents[4];R=ROOT/'regions/LME_035';MID='35_412_Gulf_of_Thailande_(1963)';E=R/'validation_reports'/MID/'geography';E.mkdir(exist_ok=True)
features=json.loads((ROOT/'common_reference_data/geography/LMEs.geojson').read_text(encoding='utf-8'))['features'];f=next(f for f in features if str(f['properties'].get('region_id'))=='35');target=shape(f['geometry']);geod=Geod(ellps='WGS84')
def area(g):return abs(geod.geometry_area_perimeter(g)[0])/1e6
# Ordered visible Gulf coastline plus the angular whole-Gulf boundary in lineage Fig14-1.
outer=[(100.22,13.65),(100.5,13.45),(100.65,13.48),(100.7,13.1),(100.65,12.65),(100.85,12.45),(101.35,12.5),(102.08,12.2),(102.4,11.75),(102.65,11.3),(101.53,9.67),(103.22,7.53),(102.03,6.24),(101.83,6.42),(101.52,6.56),(101.48,6.76),(101.2,6.98),(100.78,6.83),(100.63,7.01),(100.27,7.17),(100.24,7.64),(100.1,8.02),(99.94,8.36),(99.68,8.68),(99.66,9.05),(99.38,9.14),(99.2,9.54),(99.12,10.07),(99.23,10.44),(99.47,10.84),(99.72,11.25),(99.88,11.68),(99.84,12.18),(99.95,12.59),(99.86,12.9),(99.9,13.11),(100.03,13.32),(100.22,13.65)]
# The dashed50m curve connects to the eastern outer boundary. It is a depth-context trace, never a focal10m contour.
deep=[(100.16,11.22),(100.66,11.46),(101.2,11.5),(101.68,11.42),(101.89,11.12),(101.99,10.55),(101.53,9.67),(103.22,7.53),(102.65,6.96),(102.26,7.39),(101.8,7.77),(100.99,8.25),(100.72,8.97),(100.27,9.49),(99.96,9.93),(99.95,10.22),(100.1,10.66),(100.16,11.22)]
whole=Polygon(outer);deepg=Polygon(deep);context=whole.difference(deepg);intersection=context.intersection(target)
controls=[('upperGulfwater',100.45,13.1,True),('westshallow',99.6,10.8,True),('southshallow',100.7,7.45,True),('eastshallow',102.17,11.6,True),('centraldeep',101,10,False),('southcentraldeep',102,8,False),('westland',98.8,10.5,False),('eastland',103,12,False)]
checked=[dict(name=n,lon=x,lat=y,expected_in_context=e,actual=context.covers(Point(x,y)))for n,x,y,e in controls]
assert all(x['expected_in_context']==x['actual']for x in checked),checked
for n,g in [('target_region',target),('contextual_0_50m_shelf_trace',context),('lineage_whole_gulf_trace',whole),('lineage_central_deep_trace',deepg)]:
 (E/f'{n}.geojson').write_text(json.dumps(dict(type='Feature',properties=dict(role=n,approximate=n!='target_region'),geometry=mapping(g)),indent=2),encoding='utf-8')
shutil.copy2(Q/'lineage_map.png',E/'source_figure14_1.png')
def draw(g,ax,color,alpha,label):
 gs=list(g.geoms)if hasattr(g,'geoms')else[g]
 for i,p in enumerate(gs):
  x,y=p.exterior.xy;ax.fill(x,y,color=color,alpha=alpha,label=label if i==0 else None)
  for ring in p.interiors:x,y=ring.xy;ax.fill(x,y,color='white')
for name,focus in [('target_region',False),('study_domain',True)]:
 fig,ax=plt.subplots(figsize=(7.5,7.1));draw(target,ax,'#2F6D95',.24,'Target LME R');draw(context,ax,'#DF9C41',.65,'Contextual0–50m shelf proxy');ax.plot(*zip(*outer),color='#555555',lw=.9);ax.plot(*zip(*deep),color='#A76120',lw=1.4,ls='--')
 for city,x,y in [('Bangkok',100.5,13.7),('Songkhla',100.6,7.2),('Trat',102.55,12.0)]:ax.plot(x,y,'ko',ms=3);ax.text(x+.06,y+.04,city,fontsize=8)
 ax.set_xlim(98.7,105.5);ax.set_ylim(5.8,14.0);ax.set_aspect(1/np.cos(np.radians(10)));ax.set_xlabel('Longitude (°E)');ax.set_ylabel('Latitude (°N)');ax.grid(alpha=.2);ax.legend(loc='lower left',fontsize=8);ax.set_title('Gulf of Thailand: target and approximate shelf context\nFocal1980 model:10–50m;10m contour unavailable',fontsize=12);fig.tight_layout();fig.savefig(E/f'{name}.png',dpi=180);plt.close(fig)
out=dict(target_area_km2=area(target),contextual_trace_area_km2=area(context),intersection_km2=area(intersection),contextual_A_percentage=100*area(intersection)/area(target),contextual_B_percentage=100*area(intersection)/area(context),reported_shallow_band_area_km2=150000,reported_whole_gulf_area_km2=350000,reported_band_to_target_percentage=100*150000/area(target),focal_domain='Christensen1998 pp130–131:10–50m shelf',proxy_domain='Pauly&Chuenpagdee2003 printed338/PDF2 Figure14-1:0–50m contextual shelf',calibration=dict(longitudes_pixels=[497,565,631,698,765,831,898,965],longitudes=list(range(98,106)),latitudes_pixels=[960,889,820,750,678,608,538,467,397,326],latitudes=list(range(6,16)),ordered_coastline=outer,ordered_50m_contour=deep),controls=checked,limits=['Lineage Fig14-1 is contextual geography, not an exact focal-study polygon.','Coastline/islands are simplified; source150000km² is approximate.','Focal10m coastal boundary is not drawn; contextual proxy includes0–10m and therefore cannot establish exact focal A.','No geographic multiplier modifies catch or PPR.'],report_A='About40% contextual upper proxy (0–50m); exact10–50m study fraction unavailable.',report_B='Approximately all of the contextual shelf domain lies within the LME; simplified trace overlap is reported separately.',no_focal_geometry_claim=True)
out['proxy_domain']='Bounded visible shelf context inside the angular boundary of lineage Figure14-1; not the complete reported0–50m band or focal10–50m polygon.'
out['limits'].append('The angular line is a jurisdiction/location boundary in the lineage map, not an independently verified complete study-area boundary. Its closure limits this illustrative trace; reported150000km² refers to a larger approximate shallow band.')
out['report_A']='Focal10–50m fraction not recoverable from available source map. Context only: traced26.5%; reported larger0–50m band/target≈38.7%.'
out['report_B']='Focal10–50m fraction not recoverable. Context only: simplified traced shelf overlaps≈91% with target.'
(E/'geographic_assessment.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2)[:1800])
