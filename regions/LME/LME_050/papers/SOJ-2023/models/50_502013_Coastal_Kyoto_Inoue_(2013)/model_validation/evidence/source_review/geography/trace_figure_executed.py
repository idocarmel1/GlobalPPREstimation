"""Approximate native Figure 1 boundary; never an author digital polygon."""
from pathlib import Path
import hashlib, json, io, zipfile, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from scipy.ndimage import binary_opening, binary_fill_holes, label
from shapely.geometry import Polygon, box, shape, mapping, Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[5]
native=OUT/'Figure1_native.jpg'
a=np.asarray(Image.open(native).convert('L'))
# Native tick intersections (two visible anchors per axis).
def lon(x): return 135+(x-895)*.5/(1388-895)
def lat(y): return 36-(y-75)*.5/(567-75)
# Ordered dashed 240 m outer boundary, west to east; retain its narrow loop.
north=[(767,164),(804,168),(847,172),(880,174),(920,174),(970,170),
       (998,166),(1027,154),(1046,150),(1052,155),(1063,143),(1079,135),
       (1090,136),(1099,132),(1110,136),(1120,127),(1145,118),(1166,107),
       (1183,97),(1200,87),(1217,78),(1234,75),(1252,76),(1267,80),
       (1276,86),(1280,98),(1276,109),(1263,118),(1248,128),(1236,137),
       (1240,141),(1266,134),(1290,122),(1312,110),(1339,103),(1366,98)]
envelope=Polygon(north+[(1366,910),(767,910)])
# Source grey land is separated from white water. Opening removes thin contour
# lines; fill holes inside the mainland removes text and rivers, not bay water.
roi=np.zeros(a.shape,dtype=bool);roi[46:918,596:1493]=True
dark=(a<205)&roi
opened=binary_opening(dark,structure=np.ones((5,5)))
components,n=label(opened)
sizes=np.bincount(components.ravel())
land=np.zeros_like(opened)
kept=[]
for i in range(1,n+1):
    if sizes[i]>=100:
        component=components==i
        # Genuine mainland and offshore islands: grey median, unlike black text.
        if 110<=np.median(a[component])<=170:
            land |= binary_fill_holes(component)
            kept.append({'component':i,'pixels':int(sizes[i]),'median_grey':float(np.median(a[component]))})

def pixel_geometry(mask):
    active={};rectangles=[]
    for y,row in enumerate(mask):
        changes=np.diff(np.r_[False,row,False].astype(int))
        runs=set(zip(np.flatnonzero(changes==1),np.flatnonzero(changes==-1)))
        for run in set(active)-runs:
            first,last=active.pop(run)
            rectangles.append(box(run[0]-.5,first-.5,run[1]-.5,last+.5))
        for run in runs:
            if run in active: active[run][1]=y
            else: active[run]=[y,y]
    for run,(first,last) in active.items():
        rectangles.append(box(run[0]-.5,first-.5,run[1]-.5,last+.5))
    return unary_union(rectangles)

pixel_candidates=envelope.difference(pixel_geometry(land)).simplify(1,preserve_topology=True)
components=list(pixel_candidates.geoms) if hasattr(pixel_candidates,'geoms') else [pixel_candidates]
# Only the water connected to the main dashed study domain; disconnected
# southern inlets enter from east of the author's eastern border.
pixel_study=max(components,key=lambda g:g.area)
excluded_components=[g.area for g in components if g!=pixel_study]
from shapely.ops import transform
study=transform(lambda x,y,z=None:(lon(x),lat(y)),pixel_study)
layer=ROOT/'common_reference_data/geography/LMEs.geojson'
target=shape(next(f['geometry'] for f in json.loads(layer.read_text(encoding='utf-8'))['features'] if f['properties']['region_id']==50))
project_bytes=(ROOT/'Project.xlsx').read_bytes()
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(io.BytesIO(project_bytes)) as z:
    wb=ET.fromstring(z.read('xl/workbook.xml'))
    sheet=next(s for s in wb.find('m:sheets',ns) if s.get('name')=='Map geography')
    rid=sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    sheet_path=next(x.get('Target') for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels')) if x.get('Id')==rid).lstrip('/')
    if not sheet_path.startswith('xl/'):sheet_path='xl/'+sheet_path
    strings=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        strings=[''.join(t.text or '' for t in item.findall('.//m:t',ns)) for item in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    chunks=[]
    for row in ET.fromstring(z.read(sheet_path)).find('m:sheetData',ns):
        vals=[]
        for cell in row:
            if cell.get('t')=='inlineStr':value=''.join(t.text or '' for t in cell.findall('.//m:t',ns))
            else:
                node=cell.find('m:v',ns);value=node.text if node is not None else None
                if cell.get('t')=='s':value=strings[int(value)]
            vals.append(value)
        if vals and vals[0]=='LME_050':chunks.append((int(vals[1]),vals[2]))
    project_geometry=shape(json.loads(''.join(v for _,v in sorted(chunks))))
assert project_geometry.equals(target)
controls=[]
for name,x,y,expected in [
    ('Open shelf water',1000,230,True),('Tango Bay middle',1200,450,True),
    ('Tango Bay shallow sampling water',1195,536,True),
    ('Near western inside edge',771,300,True),('Near eastern inside edge',1360,250,True),
    ('Water inside northern bathymetric loop',1200,100,True),
    ('West of dashed study boundary',750,260,False),('East of dashed study boundary',1380,250,False),
    ('North of outer240m edge',1200,65,False),('Tango Peninsula land',1050,450,False),
    ('Offshore island',1310,385,False),('Southern mainland',1000,650,False)
]:
    actual=bool(pixel_study.covers(Point(x,y)))
    controls.append({'name':name,'pixel':[x,y],'longitude':lon(x),'latitude':lat(y),'expected_inside':expected,'actual_inside':actual})
    assert actual==expected,(name,actual,expected)
geod=Geod(ellps='WGS84')
def area(g):
    if g.is_empty: return 0.
    if g.geom_type=='Polygon':return abs(geod.geometry_area_perimeter(orient(g,sign=1))[0])/1e6
    return sum(area(p) for p in g.geoms)

def contours(ax,g,**kwargs):
    if g.geom_type=='Polygon':
        ax.plot(*g.exterior.xy,**kwargs)
        for r in g.interiors: ax.plot(*r.xy,**kwargs)
    elif hasattr(g,'geoms'):
        for p in g.geoms:contours(ax,p,**kwargs)

fig,ax=plt.subplots(figsize=(13,9));ax.imshow(a,cmap='gray',vmin=0,vmax=255)
contours(ax,pixel_study,color='#d62728',linewidth=1.1)
ax.set_xlim(700,1420);ax.set_ylim(600,40);ax.set_title('Approximate study boundary on native Figure 1; source coastline retained')
fig.tight_layout();fig.savefig(OUT/'native_trace_overlay.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,8));contours(ax,target,color='#15749b',linewidth=.9);contours(ax,study,color='#d66816',linewidth=1.2)
ax.set_xlim(134.7,135.7);ax.set_ylim(35.3,36.15);ax.grid(alpha=.25);ax.set_aspect(1/np.cos(np.deg2rad(35.7)));ax.set_title('Kyoto source trace and target Sea of Japan LME50');fig.tight_layout();fig.savefig(OUT/'target_trace_overlay.png',dpi=160);plt.close(fig)
scenarios=[]
for delta in [-.005,0,.005]:
    s=study.buffer(delta) if delta else study
    A=area(s.intersection(target));S=area(s);R=area(target)
    scenarios.append({'buffer_degrees':delta,'study_area_km2':S,'intersection_km2':A,'target_area_km2':R,'A_percent':100*A/R,'B_percent':100*A/S})
source=ROOT/'regions/LME_050/papers/SOJ-2023/Inoue_et_al_2023_Sea_of_Japan-eaca3b45.pdf'
record={'source':str(source.relative_to(ROOT)).replace('\\','/'),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_figure_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'source_locator':'Figure 1, PDF2/printed574; methods PDF4/printed576','calibration':{'longitude_anchors':[[895,135],[1388,135.5]],'latitude_anchors':[[75,36],[567,35.5]],'limits':'Only two ticks per axis; no independent graticule residual.'},'ordered_northern_boundary_pixels':north,'retained_land_components':kept,'scenarios':scenarios,'reported_area_km2':2230,'confidence':'Low','proposal_only':True,'limits':['Approximate graphical reconstruction; no author digital boundary or independently sourced 240m bathymetry.','Coastline segmented from native raster grey land; five-pixel opening removes thin contour lines and may alter tiny coastal features.','Two visible graticule ticks per axis; manual pixel calibration is approximate.','The reported2230km² remains separate and was not used to fit the polygon.','Buffers are graphical sensitivity scenarios, not confidence intervals; no PPR or catch multiplier.']}
record['project_snapshot_sha256']=hashlib.sha256(project_bytes).hexdigest()
record['canonical_target_layer_sha256']=hashlib.sha256(layer.read_bytes()).hexdigest()
record['canonical_layer_equals_Project_Map_LME050']=True
record['ordered_water_land_controls']=controls
record['excluded_disconnected_water_component_pixel_areas']=excluded_components
record['reported_vs_trace_difference_km2']=2230-area(study)
record['reported_vs_trace_difference_percent']=100*(2230-area(study))/2230
record['limits'].append('Graphical central area is about25% smaller than the published2230km². This unresolved source/graphical discrepancy exceeds the small buffer sensitivity and must accompany any displayed overlap.')
(OUT/'trace_assessment_draft.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
(OUT/'Figure1_study_trace_draft.geojson').write_text(json.dumps({'type':'Feature','properties':{'geometry_method':'Approximate native Figure1 dashed240m/coastline graphical trace','geometry_confidence':'Low','proposal_only':True},'geometry':mapping(study)})+'\n',encoding='utf-8')
print(json.dumps(scenarios))
