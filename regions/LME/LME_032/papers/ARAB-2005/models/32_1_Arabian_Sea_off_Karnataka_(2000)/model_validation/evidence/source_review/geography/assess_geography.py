from pathlib import Path
import json,hashlib
import fitz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import shape,box
from shapely.ops import unary_union
from pyproj import Geod
R=Path(__file__).resolve().parent.parent
ROOT=next(p for p in R.parents if (p/'Project.xlsx').exists())
boundary=ROOT/'common_reference_data/geography/LMEs.geojson'
features=json.loads(boundary.read_text())['features'];feat=next(f for f in features if f['properties']['region_id']==32)
region=shape(feat['geometry']);geod=Geod(ellps='WGS84')
area=abs(geod.geometry_area_perimeter(region)[0])/1e6
landpath=ROOT/'common_reference_data/geography/basemaps/ne_50m_land.geojson'
land=unary_union([shape(f['geometry']) for f in json.loads(landpath.read_text())['features']])
# The source coordinate envelope is only a containment test, never the study area.
marine_envelope=box(73,12,76,15).difference(land)
overlap=marine_envelope.intersection(region)
outside=marine_envelope.difference(region)
envelope_area=abs(geod.geometry_area_perimeter(marine_envelope)[0])/1e6
outside_area=abs(geod.geometry_area_perimeter(outside)[0])/1e6
study_area=27000.
evidence={'target_boundary':str(boundary.relative_to(ROOT)).replace('\\','/'),'boundary_sha256':hashlib.sha256(boundary.read_bytes()).hexdigest(),'target_area_km2':area,'area_method':'WGS84 ellipsoidal geodesic polygon area','source_area_km2':study_area,'source_figure':'Mohamed et al. 2008, printed p.8 / PDF p.18, Habitat Area figure','source_domain':'Karnataka shelf and parts of slope, 12–15 N and 73–76 E; exploitation to200 m,300 km coast,27,000 km2. The coordinate rectangle is not the study footprint.','containment_check':{'marine_coordinate_envelope_km2':envelope_area,'outside_target_km2':outside_area,'purpose':'Checks whether the source-stated marine coordinate envelope intersects other marine regions. Not substituted for S.'},'B_pct_approx':[95,100],'A_pct_approx':[100*.95*study_area/area,100*study_area/area],'uncertainty':'Study footprint within target at regional scale. Conservatively allow up to5% boundary/coastal uncertainty because source has no digital study polygon and target/coastlines have different resolution; this is a judgement range, not a statistical interval.'}
(R/'geography/geography_assessment.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
fig,ax=plt.subplots(figsize=(8,5.6));ax.set_facecolor('#f2f7fb')
def draw(poly,face,edge,alpha=1,z=1):
 polys=[poly] if poly.geom_type=='Polygon' else list(poly.geoms)
 for p in polys:
  if p.geom_type!='Polygon':continue
  x,y=p.exterior.xy;ax.fill(x,y,facecolor=face,edgecolor=edge,alpha=alpha,linewidth=.7,zorder=z)
draw(land.intersection(box(40,4,80,32)),'#e3e5e4','#888c8d',1,1)
draw(region,'#b6d5e7','#236087',.7,2)
ax.plot([74.05,74.45,74.85,75.2],[15,14,13,12],color='#bd641f',linewidth=4,zorder=3,label='Karnataka coast near the study area')
ax.text(57,18,'Arabian Sea\nLME 032',ha='center',fontsize=14,color='#12344a')
ax.annotate('Karnataka study\n27,000 km²',xy=(74.4,13.8),xytext=(66,8.6),arrowprops={'arrowstyle':'->','color':'#964b17'},color='#964b17',fontsize=11)
ax.set(xlim=(40,80),ylim=(4,32),xlabel='Longitude east',ylabel='Latitude north');ax.set_aspect(1/__import__('math').cos(__import__('math').radians(18)))
ax.grid(alpha=.15);fig.tight_layout();fig.savefig(R/'geography/region_boundary.png',dpi=180);plt.close(fig)
pdf=next((ROOT/'regions/LME_032/papers/ARAB-2005').glob('*.pdf'));doc=fitz.open(pdf)
doc[17].get_pixmap(matrix=fitz.Matrix(2.5,2.5),clip=fitz.Rect(114,306,480,710)).save(R/'geography/source_study_area.png')
print(json.dumps(evidence,indent=2))
