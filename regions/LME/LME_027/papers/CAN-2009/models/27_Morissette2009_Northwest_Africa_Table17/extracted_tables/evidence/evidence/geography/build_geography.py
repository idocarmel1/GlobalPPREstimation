from pathlib import Path
import json,hashlib,shutil
import fitz,numpy as np
from shapely.geometry import shape,mapping,box,Point
from shapely.ops import unary_union
from pyproj import Geod
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
base=Path('regions/LME_027/models/27_Morissette2009_Northwest_Africa_Table17/evidence/geography')
old=Path('regions/LME_027/validation_reports/27_118_Northwest_Africa_(1987)/geography')
root=Path('.')
target_obj=json.loads((old/'target_region.geojson').read_text());target=shape(target_obj['geometry']); shutil.copyfile(old/'target_region.geojson',base/'target_region.geojson')
landpath=Path('common_reference_data/geography/basemaps/ne_50m_land.geojson'); lj=json.loads(landpath.read_text()); frame=box(-34,4,5,41)
land=unary_union([shape(f['geometry']).intersection(frame) for f in lj['features'] if shape(f['geometry']).intersects(frame)])
native=box(-24.7568958072121,8.51221926574749,-5.84155099971101,36.0184436905047).difference(land)
prose=box(-30,8.5,-6.5,35.97).difference(land)
geod=Geod(ellps='WGS84')
def area(g):
 if g.geom_type in ['MultiPolygon','GeometryCollection']:return sum(area(x) for x in g.geoms)
 return abs(geod.geometry_area_perimeter(g)[0])/1e6 if g.geom_type=='Polygon' else 0
# Preserve exact previously reviewed marine polygon after confirming new native metadata bounds.
native=shape(json.loads((old/'study_area_reconstructed.geojson').read_text())['geometry'])
stats=[]
for label,g in [('Live EcoBase118 bounds; consistent with final Figure1',native),('Final2009 printed coordinate bounds',prose)]:
 ia=area(g.intersection(target));stats.append({'label':label,'study_area_km2':area(g),'intersection_km2':ia,'A_percent':100*ia/area(target),'B_percent':100*ia/area(g),'B_using_reported_area_percent_sensitivity':100*ia/3561029})
(base/'study_area_native_extent.geojson').write_text(json.dumps({'type':'Feature','properties':{'source':'Live EcoBase118 geographic_extent','relationship':'Visually consistent with final2009 Figure1; reconstructed marine extent, not digitized author polygon','source_figure':'final_source_pdf12.png','method':'Existing reviewed box-minus-NaturalEarth50m marine polygon reused after exact bounds verification'},'geometry':mapping(native)}),encoding='utf-8')
(base/'study_area_final_prose_extent.geojson').write_text(json.dumps({'type':'Feature','properties':{'source':'Final2009 PDF11 printedp7','method':'box minus NaturalEarth50m land','bounds':[-30,8.5,-6.5,35.97]},'geometry':mapping(prose)}),encoding='utf-8')
def fill(ax,g,color,alpha=1,edge=None,lw=.5):
 if g.geom_type in ['MultiPolygon','GeometryCollection']:
  for p in g.geoms:fill(ax,p,color,alpha,edge,lw)
 elif g.geom_type=='Polygon':
  x,y=g.exterior.xy;ax.fill(x,y,color=color,alpha=alpha,edgecolor=edge,linewidth=lw)
  for h in g.interiors:
   x,y=h.xy;ax.fill(x,y,color='#eef7fa')
def setup(ax):
 ax.set_facecolor('#eef7fa');fill(ax,land,'#d5d8d7',edge='#8b9394');ax.set_xlim(-33,1);ax.set_ylim(5,40);ax.set_aspect(1/np.cos(np.radians(23)));ax.set_xlabel('Longitude');ax.set_ylabel('Latitude');ax.grid(alpha=.25)
fig,ax=plt.subplots(figsize=(8,8));setup(ax);fill(ax,target,'#176c8f',.65,edge='#004e77');ax.set_title('LME 27: Canary Current target boundary');fig.tight_layout();fig.savefig(base/'target_region.png',dpi=190);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(12,7.5))
for ax,study,rec in zip(axs,[native,prose],stats):
 setup(ax);fill(ax,study,'#ed922e',.34,edge='#ae6218');fill(ax,target,'#176c8f',.65,edge='#004e77');ax.set_title(('EcoBase extent / final map interpretation' if study is native else 'Printed-bounds sensitivity')+'\n'+f"A ≈ {rec['A_percent']:.0f}%; B ≈ {rec['B_percent']:.0f}%",fontsize=11)
fig.suptitle('Canary Current LME (blue) and Northwest Africa model area (orange)',fontsize=13)
fig.text(.5,.015,'Marine reconstructions, WGS84 geodesic areas. Final Figure 1 has no coordinate grid; western boundary differs from printed prose.\nThese alternatives express boundary uncertainty, not statistical confidence intervals.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.13,1,.95]);fig.savefig(base/'comparison.png',dpi=190);plt.close(fig)
pdf=fitz.open('regions/LME_027/papers/FCRR_2009_17-2.pdf.pdf');pdf[11].get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(69,63,542,339)).save(base/'final_figure1_with_caption.png')
points=[]
for label,x,y,expected in [('Senegal shelf',-17.5,15,True),('Mauritanian shelf',-17.5,20,True),('Moroccan waters',-10,30,True),('Western extent disagreement',-28,20,False),('South of both extents',-20,7,False),('Moroccan mainland',-8,31,False)]:
 p=Point(x,y);points.append({'label':label,'lon':x,'lat':y,'land':land.covers(p),'in_target':target.covers(p),'in_native_extent':native.covers(p),'in_final_prose_extent':prose.covers(p),'expected_native':expected,'agrees':native.covers(p)==expected})
report={'source':'Final2009 Figure1 PDF12/printed8 and Study area PDF11/printed7','source_available':True,'final_figure_visual_review':'Orange domain runs north near Strait of Gibraltar to south near Guinea, western vertical boundary near Cape Verde longitude. No coordinate grid. Figure is consistent with retained/live EcoBase west bound about24.76W and not the prose30W bound; retain both because figure lacks exact georeference.','target_area_km2':area(target),'source_reported_area_km2':3561029,'comparisons':stats,'report_A_range_percent':[95,100],'report_B_range_percent':[20,35],'method':'Compatible WGS84 geodesic areas from target and land-excluded extent reconstructions. Native marine polygon reused exactly after verifying live official bounds. Prose extent freshly computed. Not a measured author polygon or comparison of screenshot pixel areas.','uncertainty':'Broad offshore model encompasses most shelf LME but substantial study water outside it. Approximate range brackets final-map/native versus printed-longitude conflict and coastline resolution; not statistical confidence. A source-area denominator is sensitivity only.','source_pdf_sha256':hashlib.sha256(Path('regions/LME_027/papers/FCRR_2009_17-2.pdf.pdf').read_bytes()).hexdigest(),'target_boundary_sha256':hashlib.sha256((base/'target_region.geojson').read_bytes()).hexdigest(),'landmask_sha256':hashlib.sha256(landpath.read_bytes()).hexdigest(),'point_controls':points,'figure_artifact':'final_figure1_with_caption.png','target_artifact':'target_region.png','comparison_artifact':'comparison.png'}
(base/'geographic_assessment.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'target_area_km2':area(target),'comparisons':stats,'point_controls_pass':all(p['agrees'] for p in points)},indent=2))
