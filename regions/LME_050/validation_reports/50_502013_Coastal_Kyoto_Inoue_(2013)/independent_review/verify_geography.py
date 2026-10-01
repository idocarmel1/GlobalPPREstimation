"""Independent read-only reproduction of saved Kyoto trace; writes here only."""
from pathlib import Path
import io, hashlib, json, zipfile, xml.etree.ElementTree as ET
import numpy as np
import pymupdf
from PIL import Image
from scipy.ndimage import binary_opening, binary_fill_holes, label
from shapely.geometry import shape, Polygon, Point, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, transform
from pyproj import Geod
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[5]
GEO=OUT.parent/'coordinator_geography'
PDF=ROOT/'regions/LME_050/papers/SOJ-2023/Inoue_et_al_2023_Sea_of_Japan-eaca3b45.pdf'
LAYER=ROOT/'common_reference_data/geography/LMEs.geojson'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def area(g):
    if g.is_empty:return 0.
    if g.geom_type=='Polygon':return abs(Geod(ellps='WGS84').geometry_area_perimeter(orient(g,sign=1))[0])/1e6
    return sum(area(p) for p in g.geoms)
record=read(GEO/'trace_assessment_draft.json')
with pymupdf.open(PDF) as pdf:
    images=[x for x in pdf[1].get_images(full=True) if x[2:4]==(1500,923)]
    assert len(images)==1
    native=pdf.extract_image(images[0][0])['image']
native_sha=hashlib.sha256(native).hexdigest()
assert native_sha==sha(GEO/'Figure1_native.jpg')==record['native_figure_sha256']
(OUT/'Figure1_native_independently_extracted.jpg').write_bytes(native)
assert sha(PDF)==record['source_sha256']
a=np.asarray(Image.open(io.BytesIO(native)).convert('L'))
assert record['calibration']['longitude_anchors']==[[895,135],[1388,135.5]]
assert record['calibration']['latitude_anchors']==[[75,36],[567,35.5]]
def lon(x):return 135+(x-895)*.5/493
def lat(y):return 36-(y-75)*.5/492

# Native land segmentation is independently recalculated from extracted bytes;
# source-controlled manual north-boundary vertices are retained without fitting
# to either area claim. Root's writer is neither imported nor executed.
roi=np.zeros(a.shape,dtype=bool);roi[46:918,596:1493]=True
opened=binary_opening((a<205)&roi,structure=np.ones((5,5)))
components,n=label(opened);sizes=np.bincount(components.ravel())
land=np.zeros(a.shape,dtype=bool);kept=[]
for i in range(1,n+1):
    if sizes[i]>=100:
        pixels=components==i;median=float(np.median(a[pixels]))
        if 110<=median<=170:
            land |= binary_fill_holes(pixels)
            kept.append({'component':i,'pixels':int(sizes[i]),'median_grey':median})
assert kept==record['retained_land_components']
rectangles=[];active={}
for y,row in enumerate(land):
    switches=np.diff(np.r_[False,row,False].astype(int))
    runs=set(zip(np.flatnonzero(switches==1),np.flatnonzero(switches==-1)))
    for run in set(active)-runs:
        first,last=active.pop(run);rectangles.append(box(run[0]-.5,first-.5,run[1]-.5,last+.5))
    for run in runs:
        if run in active:active[run][1]=y
        else:active[run]=[y,y]
for run,(first,last) in active.items():rectangles.append(box(run[0]-.5,first-.5,run[1]-.5,last+.5))
north=record['ordered_northern_boundary_pixels']
envelope=Polygon(north+[[1366,910],[767,910]])
water=envelope.difference(unary_union(rectangles)).simplify(1,preserve_topology=True)
pixel_study=max(list(water.geoms) if hasattr(water,'geoms') else [water],key=lambda g:g.area)
independent_study=transform(lambda x,y,z=None:(lon(x),lat(y)),pixel_study)
saved_study=shape(read(GEO/'Figure1_study_trace_draft.geojson')['geometry'])
assert independent_study.equals(saved_study)
assert saved_study.is_valid and not saved_study.is_empty
feature=next(f for f in read(LAYER)['features'] if f['properties']['region_id']==50)
target=shape(feature['geometry']);assert target.is_valid

# Authenticate canonical target against a fresh, complete Project byte snapshot.
project_bytes=(ROOT/'Project.xlsx').read_bytes()
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(io.BytesIO(project_bytes)) as z:
    wb=ET.fromstring(z.read('xl/workbook.xml'))
    sheet=next(s for s in wb.find('m:sheets',ns) if s.get('name')=='Map geography')
    rid=sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    path=next(s.get('Target') for s in ET.fromstring(z.read('xl/_rels/workbook.xml.rels')) if s.get('Id')==rid).lstrip('/')
    if not path.startswith('xl/'):path='xl/'+path
    strings=[''.join(t.text or '' for t in item.findall('.//m:t',ns)) for item in ET.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
    chunks=[]
    for row in ET.fromstring(z.read(path)).find('m:sheetData',ns):
        values=[]
        for cell in row:
            if cell.get('t')=='inlineStr':value=''.join(t.text or '' for t in cell.findall('.//m:t',ns))
            else:
                v=cell.find('m:v',ns);value=v.text if v is not None else None
                if cell.get('t')=='s':value=strings[int(value)]
            values.append(value)
        if values and values[0]=='LME_050':chunks.append((int(values[1]),values[2]))
    assert chunks
    project_target=shape(json.loads(''.join(v for _,v in sorted(chunks))))
assert project_target.equals(target)
controls=[]
for c in record['ordered_water_land_controls']:
    x,y=c['pixel'];p=Point(lon(x),lat(y))
    actual=saved_study.covers(p)
    assert actual==c['expected_inside']==c['actual_inside'],c['name']
    assert abs(lon(x)-c['longitude'])<1e-12 and abs(lat(y)-c['latitude'])<1e-12
    controls.append({**c,'independently_reproduced_inside':actual,'source_pixel_grayscale':int(a[y,x])})
assert len(controls)==12
scenarios=[]
for expected in record['scenarios']:
    delta=expected['buffer_degrees'];s=saved_study.buffer(delta) if delta else saved_study
    intersection=area(s.intersection(target));S=area(s);R=area(target)
    actual={'buffer_degrees':delta,'study_area_km2':S,'intersection_km2':intersection,'target_area_km2':R,'A_percent':100*intersection/R,'B_percent':100*intersection/S}
    assert all(abs(actual[k]-expected[k])<1e-7 for k in actual), (actual,expected)
    scenarios.append(actual)

def outlines(ax,g,**kwargs):
    if g.geom_type=='Polygon':
        ax.plot(*g.exterior.xy,**kwargs)
        for ring in g.interiors:ax.plot(*ring.xy,**kwargs)
    elif hasattr(g,'geoms'):
        for part in g.geoms:outlines(ax,part,**kwargs)
fig,ax=plt.subplots(figsize=(13,9));ax.imshow(a,cmap='gray',vmin=0,vmax=255)
outlines(ax,pixel_study,color='#d62728',linewidth=1)
for i,c in enumerate(controls,1):
    x,y=c['pixel'];ax.scatter(x,y,color='#008855' if c['expected_inside'] else '#722088',s=22);ax.annotate(str(i),(x,y),xytext=(4,4),textcoords='offset points',fontsize=8)
ax.set_xlim(720,1410);ax.set_ylim(690,40)
ax.set_title('Independent native raster/trace check; numbered source water/land controls')
fig.tight_layout();fig.savefig(OUT/'native_trace_controls_independent.png',dpi=160);plt.close(fig)
result={'inputs':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [PDF,GEO/'Figure1_native.jpg',GEO/'trace_assessment_draft.json',GEO/'Figure1_study_trace_draft.geojson',GEO/'trace_figure.py',LAYER]},'fresh_Project_snapshot_sha256':hashlib.sha256(project_bytes).hexdigest(),'canonical_target_actual_properties':feature['properties'],'canonical_target_equals_fresh_Project_Map':True,'native_embedded_raster_byte_identity':True,'independently_reconstructed_native_landmask_trace_equals_saved':True,'ordered_water_land_controls':controls,'scenarios':scenarios,'reported_main_area_km2':2230,'native_supplement_seven_depth_bin_area_sum_km2':1223,'central_trace_area_km2':area(saved_study),'main_minus_central_trace_km2':2230-area(saved_study),'main_minus_central_trace_percent_of_main':100*(2230-area(saved_study))/2230,'scope':'Independent native-image identity, source graphical inspection, read-only mask reconstruction, exact saved polygon/Project target authentication, WGS84 arithmetic and all12controls. No coordinator writer imported/executed and no production mutations.','graphical_review':'Visually checked native Figure1, ordered240m bend including its narrow loop, TangoBay coast/peninsula and offshore islands; source-supported water on both border sides and northern/coastal controls retained. No demonstrated bounded defect found.','limits':['Two calibration ticks per axis; no independent graticule residual, author digital boundary or independently sourced240m bathymetry.','Grey land segmentation and one-pixel simplification are approximate, particularly tiny coast/island features.','The central1680.96km² trace is24.62% smaller than the reported2230km²; seven supplement bins separately sum1223km². These are distinct source/graphical quantities, not a confidence interval or correction.','Degree buffers are graphical sensitivity only, not independent statistical bounds. The coordinator descriptive A≈.15–.23/B≈95–100 Low range is an indicative display, not exact calibration or an extrapolation multiplier.','This verification does not establish a whole-LME model or scientific approval.']}
(OUT/'geography_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'native_identity':True,'mask_trace_equality':True,'target_Project_equality':True,'controls':len(controls),'central':scenarios[1],'main_area_difference_percent':result['main_minus_central_trace_percent_of_main'],'Project_sha256':result['fresh_Project_snapshot_sha256']}))
