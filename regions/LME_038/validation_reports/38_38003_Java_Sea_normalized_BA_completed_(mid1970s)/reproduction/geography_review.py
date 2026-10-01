from pathlib import Path
import json,sys,math,shutil
import numpy as np,matplotlib.pyplot as plt,pymupdf
from shapely.geometry import shape,box,mapping,Point
from shapely.ops import unary_union
from pyproj import Geod
Q=Path(__file__).parent;ROOT=Q.parents[4];R=ROOT/'regions/LME_038';MID='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)';E=R/'validation_reports'/MID/'geography';E.mkdir(exist_ok=True)
fc=json.loads((ROOT/'common_reference_data/geography/LMEs.geojson').read_text(encoding='utf-8'));ft=next(f for f in fc['features']if str(f['properties'].get('region_id'))=='38');target=shape(ft['geometry']);geod=Geod(ellps='WGS84')
def area(g):return abs(geod.geometry_area_perimeter(g)[0])/1e6
landfc=json.loads((ROOT/'common_reference_data/geography/basemaps/ne_50m_land.geojson').read_text(encoding='utf-8'));land=unary_union([shape(f['geometry'])for f in landfc['features']if shape(f['geometry']).intersects(box(104,-9,120,1))])
scenarios=[]
for east in [116.5,117.5]:
 env=box(105+50/60,-6-50/60,east,-3);study=env.difference(land);inter=study.intersection(target);scenarios.append(dict(east=east,study=study,intersection=inter,area=area(study),intersection_area=area(inter),A=100*area(inter)/area(target),B=100*area(inter)/area(study)))
study=scenarios[-1]['study'];checks=[]
for n,x,y,expected in [('central Java Sea',111,-5,True),('western offshore water',107,-4.5,True),('eastern offshore water',116,-5.5,True),('north of approximate bounds',111,-2.5,False),('Banda Sea outside',125,-5,False),('Java land',110,-7.5,False),('Sumatra land',105,-4.5,False)]:checks.append(dict(name=n,longitude=x,latitude=y,expected=expected,actual=bool(study.covers(Point(x,y)))))
assert all(x['expected']==x['actual']for x in checks),checks
for n,g in [('target_region',target),('reconstructed_study_bounds',study)]:
 (E/f'{n}.geojson').write_text(json.dumps(dict(type='Feature',properties=dict(role=n,approximate=n!='target_region',source='Buchary1999 PDF29/printed20 text bounds; no explicit study polygon in Figure2.1'),geometry=mapping(g)),indent=2),encoding='utf-8')
def draw(g,ax,color,alpha,label):
 gs=list(g.geoms)if hasattr(g,'geoms')else[g]
 for i,p in enumerate(gs):
  if p.geom_type!='Polygon':continue
  x,y=p.exterior.xy;ax.fill(x,y,color=color,alpha=alpha,label=label if i==0 else None)
  for ring in p.interiors:ax.fill(*ring.xy,color='#EEEEEB')
fig,ax=plt.subplots(figsize=(8.0,5.4));draw(land,ax,'#EEEEEB',1,'Land');draw(target,ax,'#3D7897',.45,'Indonesian Sea LME R');draw(study,ax,'#D89039',.65,'Study bounds, east117.5°E');draw(scenarios[0]['study'],ax,'#BD5732',.35,'Study bounds, east116.5°E')
for c in checks:ax.plot(c['longitude'],c['latitude'],'o'if c['expected']else'x',color='#1C6035'if c['expected']else'#9C1E2B',markersize=5)
for n,x,y in [('Java',110,-7.5),('Kalimantan',113,-1.7),('Sumatra',102,-4.0),('Sulawesi',122,-2),('Java Sea',111,-5)]:ax.text(x,y,n,fontsize=9,ha='center')
ax.set_xlim(100,135);ax.set_ylim(-10,4);ax.set_aspect(1);ax.grid(alpha=.25);ax.set_xlabel('Longitude °E');ax.set_ylabel('Latitude');ax.legend(loc='upper right',fontsize=8);ax.set_title('Indonesian Sea LME and approximate Java Sea study bounds');fig.tight_layout();fig.savefig(E/'target_region.png',dpi=180);plt.close(fig)
d=pymupdf.open(R/'papers/BUCHARY-1991/ubc_1999-0254.pdf.pdf');d[29].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5).prerotate(90)).save(str(E/'source_figure2_1_landscape.png'))
out=dict(source='Buchary1999, PDF29/printed20 domain prose and PDF30/printed21 Figure2.1',method='Approximate prose-bounds reconstruction with Natural Earth 1:50 million land removal and WGS84 geodesic polygon areas. Two source eastern-bound scenarios116.5/117.5E; no pixel-area comparison.',target_area_km2=area(target),reported_study_area_km2=471000,scenarios=[{k:v for k,v in x.items()if k not in ['study','intersection']}for x in scenarios],controls=checks,A_range=[min(x['A']for x in scenarios),max(x['A']for x in scenarios)],B_range=[min(x['B']for x in scenarios),max(x['B']for x in scenarios)],limits=['Source gives approximate regional extent, not a digitized study boundary. Figure2.1 shows bathymetry and bordering provinces, with no explicit polygon.','The northern/southern text bounds can truncate local coast-following water; source471000km² is separate reported-area context. The traced approximation is not exact coverage.','No geographic multiplier is applied to catch or PPR.','Natural Earth coastline is generalized; two east scenarios are source bounds sensitivity, not statistical confidence intervals.'])
(E/'geographic_assessment.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
