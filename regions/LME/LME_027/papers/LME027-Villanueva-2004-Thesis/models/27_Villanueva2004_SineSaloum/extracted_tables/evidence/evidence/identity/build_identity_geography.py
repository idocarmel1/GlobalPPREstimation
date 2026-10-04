import json, hashlib, shutil, sys
from pathlib import Path
import fitz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import shape, Point, box
from pyproj import Geod

root=Path(__file__).resolve().parents[6]
candidate=root/'regions/LME_027/models/27_Villanueva2004_SineSaloum'
identity=candidate/'evidence/identity'; geo=candidate/'evidence/geography'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
source=root/'regions/LME_027/papers/LME027-Villanueva-2004/010056023-adc18d15.pdf'
targetpath=root/'common_reference_data/geography/LMEs.geojson'
alltarget=json.loads(targetpath.read_text(encoding='utf-8'))
target=next(f for f in alltarget['features'] if int(f['properties'].get('region_id',-1))==27)
save(geo/'target_region.geojson',target)
geom=shape(target['geometry']); geod=Geod(ellps='WGS84')
area=abs(geod.geometry_area_perimeter(geom)[0])/1e6
report_area=546.; upper=100*report_area/area
landpath=root/'common_reference_data/geography/basemaps/ne_50m_land.geojson'
landdata=json.loads(landpath.read_text(encoding='utf-8'))
lands=[shape(f['geometry']) for f in landdata['features']]
def polygons(g): return list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
def draw(ax,g,**kwargs):
    for p in polygons(g):
        if p.geom_type=='Polygon':
            x,y=p.exterior.xy; ax.fill(x,y,**kwargs)
fig,(ax,detail)=plt.subplots(1,2,figsize=(11,6),gridspec_kw={'width_ratios':[1,1]})
for a in [ax,detail]:
    for land in lands:
        if land.intersects(box(-28,10,0,38)): draw(a,land,color='#e7e5df',edgecolor='#c8c5bc',linewidth=.4)
    draw(a,geom,color='#b1d7e4',edgecolor='#286982',alpha=.8,linewidth=.65)
    a.set_xlabel('Longitude');a.set_ylabel('Latitude');a.grid(alpha=.2)
ax.set_xlim(-27,-5);ax.set_ylim(11,37);ax.set_aspect('equal');ax.set_title('Project target: Canary Current LME 027')
detail.set_xlim(-17.6,-15.85);detail.set_ylim(13.35,14.65);detail.set_aspect('equal');detail.set_title('Sine-Saloum location context')
# The documented thesis bbox is geographic context only; no study polygon is inferred.
reference_bounds=[-17.0,13+35/60,-16-50/60,14+10/60]
b=box(*reference_bounds)
x,y=b.exterior.xy;detail.plot(x,y,'--',color='#973e34',linewidth=1.4,label='Printed thesis bounds; not model water footprint')
detail.plot(-16.8,13.95,'o',color='#973e34',markersize=4)
detail.annotate('Sine-Saloum estuary\nlocation only',(-16.8,13.95),xytext=(-16.6,14.32),arrowprops={'arrowstyle':'->','color':'#973e34'},fontsize=8)
detail.legend(loc='lower right',fontsize=7)
fig.suptitle('Preferred thesis 37-group model (1991–1992): reported estuary area 546 km²',fontsize=13)
fig.text(.5,.015,'Printed longitude bounds and schematic figure differ. The rectangle is context only; no modeled water polygon is inferred.',ha='center',fontsize=8)
fig.tight_layout(rect=[0,.055,1,.95]);fig.savefig(geo/'geographic_context.png',dpi=180);plt.close(fig)
with fitz.open(source) as d:
    d[2].get_pixmap(matrix=fitz.Matrix(2,2)).save(geo/'source_map_PDF3.png')
    for i in [0,11,12]: d[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(identity/f'chapter_identity_PDF{i+1}.png')
with fitz.open(identity/'Villanueva2004_thesis_29305.pdf') as d:
    for i in [40,41,137,234,235]: d[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(identity/f'thesis_PDF{i+1}.png')
with fitz.open(identity/'Villanueva2005_2171.pdf') as d:
    for i in [0,3,4,5]: d[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(identity/f'followup_PDF{i+1}.png')
assessment={
 'review_date':'2026-10-03','candidate_model_id':candidate.name,
 'preferred_source':'Villanueva2004 thesis37groups1991–1992',
 'source_reported_area_km2':report_area,'source_area_locator':'thesis printed17/PDF41 topography and Table2.1;38groupchapter separately reports543km²',
 'target_area_km2':area,'target_boundary_source':'common_reference_data/geography/LMEs.geojson region_id27','target_boundary_sha256':sha(targetpath),
 'A_definition':'100 × intersection area / target region area','B_definition':'100 × intersection area / modeled study area',
 'A_percent':None,'B_percent':None,'A_upper_bound_percent':upper,'A_bound':[0,upper],
 'recommended_short_cell':'A ≤ 0.049% (area bound); B not determined',
 'bound_interpretation':'Mathematical upper bound using reported546km², even if all study waters were insideLME. It is not a measured or digitized overlap; no lower estimate beyond0 is asserted.',
 'study_polygon_status':'No defensible exact37group model water polygon recovered. Figure2.2 is a schematic river-channel map with10km scale and north arrow but no geographic graticule. The enclosing frame is not the model boundary; the rectangle is not substituted.',
 'thesis_bounds':{'west':reference_bounds[0],'south':reference_bounds[1],'east':reference_bounds[2],'north':reference_bounds[3],'reported_area_km2':546,'locator':'thesis printed17/PDF41 and Figure2.2 printed18/PDF42','use':'reference location only. Bounding rectangle is not used as modeled water polygon or overlap denominator'},
 'source_figure_review':'Figure2.2 thesis PDF42 inspected: shaded mainchannels Saloum/Diomboss/Bandiala plus complex black bolong outlines and open ocean. No enclosing modeled water boundary or coordinate anchors. Printed longitudes16°50′–17°W describe a western strip that does not encompass the full eastward estuary shown in map; source inconsistency preserved.',
 'fit_assessment':'Poor basis for whole-LME representation. Hypersaline estuarine nursery trophic structure and localized fishing patterns do not establish open shelf/offshore food-web coverage. Geographic adjacency and occasional shared taxa do not establish representativeness.',
 'limitations':'Project LME geometry contains several main estuary channels, but coastline and channel detail differ from schematic. Accurate B needs compatible author water polygon/calibrated reconstruction; nearby point inclusion is not whole-estuary inclusion. Even B=100% would coexist with A below0.05%; containment does not imply regional coverage.',
 'figures':['../identity/thesis_PDF42.png','geographic_context.png','source_map_PDF3.png'],
 'hashes':{'chapter_pdf':sha(source),'thesis_pdf':sha(identity/'Villanueva2004_thesis_29305.pdf'),'land_context':sha(landpath)},
 'reference_points_inside_target':{str(pt):bool(geom.covers(Point(*pt))) for pt in [(-16.8,13.95),(-17.0,13.7),(-16.7,14.0),(-17.2,13.8)]}
}
save(geo/'geographic_assessment.json',assessment)
manifest=[]
for f,url in [('Villanueva2004_thesis_29305.pdf','https://archimer.ifremer.fr/doc/00180/29122/29305.pdf'),('Villanueva2005_2171.pdf','https://archimer.ifremer.fr/doc/00000/2554/2171.pdf'),('ecobase612_official_input.xml','https://ecobase.ecopath.org/php/webser/soap-client.php?no_model=612'),('ecobase612_metadata.html','https://ecobase.ecopath.org/php/protect/base_model.php?action=base&ident=&lang=&model=612&pass=&provenance=web')]:
    p=identity/f; item={'file':f,'url':url,'access_date':'2026-10-03','bytes':p.stat().st_size,'sha256':sha(p),'role':'related source evidence; no38group computational adoption'}
    if p.suffix=='.pdf': item['pdf_pages']=len(fitz.open(p))
    manifest.append(item)
save(identity/'retrieval_manifest.json',manifest)
print(json.dumps({'target_area_km2':area,'upper_A_percent':upper,'reference_points':assessment['reference_points_inside_target']},indent=2))
