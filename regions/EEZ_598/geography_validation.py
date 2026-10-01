"""Boundary evidence only; scientific coefficients are untouched."""
import json,hashlib
from pathlib import Path
import numpy as np,matplotlib.pyplot as plt
from shapely.geometry import shape,box,Polygon,MultiPolygon
from shapely.ops import unary_union
from pyproj import Geod
import pymupdf
REG=Path(__file__).resolve().parent;ROOT=REG.parents[1]
MID='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)';OUT=REG/'validation_reports'/MID;OUT.mkdir(parents=True,exist_ok=True)
geo=ROOT/'common_reference_data/geography/EEZs.geojson';landfile=ROOT/'common_reference_data/geography/basemaps/ne_50m_land.geojson'
f=next(f for f in json.loads(geo.read_text(encoding='utf-8'))['features'] if f['properties']['unit_id']=='EEZ_598');R=shape(f['geometry']);S=box(110,-15,180,15)
land=unary_union([shape(f['geometry']) for f in json.loads(landfile.read_text(encoding='utf-8'))['features']]);wetS=S.difference(land);wetR=R.difference(land);I=wetR.intersection(wetS)
G=Geod(ellps='WGS84')
def area(p):
 if p.geom_type=='Polygon':
  exterior=abs(G.geometry_area_perimeter(Polygon(p.exterior))[0]);holes=sum(abs(G.geometry_area_perimeter(Polygon(h))[0]) for h in p.interiors);return (exterior-holes)/1e6
 if hasattr(p,'geoms'):return sum(area(x) for x in p.geoms)
 return 0
# Densify constant-latitude rectangle edges to avoid treating them as a long geodesic.
def dense(poly):
 def ring(coords):
  out=[]
  for a,b in zip(coords[:-1],coords[1:]):
   n=max(1,int(max(abs(b[0]-a[0]),abs(b[1]-a[1]))/.1)+1)
   out.extend([(a[0]+(b[0]-a[0])*t/n,a[1]+(b[1]-a[1])*t/n) for t in range(n)])
  return out+[out[0]]
 if poly.geom_type=='Polygon':return Polygon(ring(list(poly.exterior.coords)),[ring(list(h.coords)) for h in poly.interiors])
 if poly.geom_type=='MultiPolygon':return MultiPolygon([dense(x) for x in poly.geoms])
 return poly
ar,ass,ai=[area(dense(p)) for p in (wetR,wetS,I)]
raw_a=100*ai/ar
assert S.covers(R), 'PNG EEZ containment must be checked geometrically.'
result={'boundary_properties':f['properties'],'region_area_km2':ar,'study_rectangle_wet_area_km2':ass,'intersection_km2':ai,'A_region_in_study_percentage':100*ai/ar,'B_study_in_region_percentage':100*ai/ass,'B_using_published_26964000_km2_percentage':100*ai/26964000,'study_area_published_km2':26964000,'study_bounds':[110,-15,180,15],'method':'WGS84 ellipsoidal polygon area, coordinate-linear densification ≤0.1 degree; Natural Earth 1:50m land removed consistently. Study domain is Section 2.2 PDF7 fixed rectangle, distinct from warm-pool Figure1 PDF3. Approximate due SAU repaired EEZ polygon, coarse land, and published-area disagreement.','input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [geo,landfile]}}
result['A_region_in_study_percentage']=100.0
result['A_raw_area_ratio_percentage']=raw_a
result['A_containment_evidence']='Fixed source rectangle geometrically covers the full target polygon; area-ratio +5.05e-8 percentage-point tail comes from independent edge densification. Report geometric containment as100%.'
(OUT/'geographic_estimate.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
def plot_poly(ax,p,**kw):
 if hasattr(p,'geoms'):
  for q in p.geoms:plot_poly(ax,q,**kw)
 elif p.geom_type=='Polygon':
  x,y=p.exterior.xy;ax.fill(x,y,**kw)
for name,extent in [('region_boundary',(138,162,-17,3)),('study_domain',(105,184,-19,19))]:
 fig,ax=plt.subplots(figsize=(9,4.9),dpi=180)
 plot_poly(ax,S,facecolor='#e8f3f5',edgecolor='#24656f',linewidth=1.4,alpha=.8)
 plot_poly(ax,land.intersection(box(*[extent[0],extent[2],extent[1],extent[3]])),facecolor='#d2d2c9',edgecolor='#94948b',linewidth=.3)
 plot_poly(ax,R,facecolor='#e9a33e',edgecolor='#84551c',linewidth=1.2,alpha=.8)
 ax.set_xlim(extent[:2]);ax.set_ylim(extent[2:]);ax.set_xlabel('Longitude (°E)');ax.set_ylabel('Latitude (°)');ax.grid(alpha=.25)
 ax.set_title('Papua New Guinea EEZ and WCP-2007 fixed study rectangle',fontsize=12)
 ax.text(.01,.01,'Orange: EEZ_598  |  Blue: 110–180°E, 15°S–15°N\nSAU polygon; Natural Earth land. Approximate boundary comparison.',transform=ax.transAxes,fontsize=8,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none'})
 fig.tight_layout();fig.savefig(OUT/(name+'.png'));plt.close(fig)
pdf=pymupdf.open(REG/'papers/WCP-2007/download-0adcf55e.pdf');pdf[2].get_pixmap(matrix=pymupdf.Matrix(1.6,1.6)).save(OUT/'article_figure1_pdf3.png')
pdf[2].get_pixmap(matrix=pymupdf.Matrix(2.5,2.5),clip=pymupdf.Rect(85,378,560,594)).save(OUT/'article_figure1_crop.png')
print(json.dumps(result,indent=2))
