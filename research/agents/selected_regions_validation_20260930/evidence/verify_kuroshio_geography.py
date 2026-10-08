"""Independent coordinator checks of the evidence-supported Kuroshio trace."""
from pathlib import Path
import hashlib, json, math, io
import pymupdf
import numpy as np
from PIL import Image
from shapely.geometry import shape, Point
from shapely.geometry.polygon import orient
from pyproj import Geod

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
QA=BASE/'work/LME_049/independent_source_review'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=ROOT/'regions/LME_049/papers/KUR-2019/Watari-Ecosystemmodelingwestern-2019.pdf'
assessment=json.loads((QA/'geography_trace_assessment.json').read_text(encoding='utf-8'))
geometry=QA/'Figure1_colored_study_trace_draft.geojson'
assert sha(geometry)=='35dbb8509d69cabccd4ae096d518ac6cd4074a5846113f19893960708ef6508d'
doc=pymupdf.open(source)
native=np.asarray(Image.open(io.BytesIO(doc.extract_image(18)['image'])).convert('RGB'))
assert np.array_equal(native,np.asarray(Image.open(QA/'Figure1_native.png').convert('RGB')))
s=shape(json.loads(geometry.read_text(encoding='utf-8'))['geometry'])
before=shape(json.loads((QA/'Figure1_colored_study_trace_draft_before_overlay_edge_repair.geojson').read_text(encoding='utf-8'))['geometry'])
layer=ROOT/'common_reference_data/geography/LMEs.geojson'
r=shape(next(f['geometry'] for f in json.loads(layer.read_text(encoding='utf-8'))['features'] if f['properties']['region_id']==49))
g=Geod(ellps='WGS84')
def area(x):
    if x.is_empty:return 0.
    if x.geom_type=='Polygon':return abs(g.geometry_area_perimeter(orient(x,sign=1))[0])/1e6
    return sum(area(p) for p in x.geoms)
assert s.is_valid and before.difference(s).is_empty
S,R,I=area(s),area(r),area(s.intersection(r))
expected=next(x for x in assessment['scenarios'] if x['buffer_degrees']==0)
for calculated,key in [(S,'study_area_km2'),(I,'overlap_km2'),(100*I/R,'A_overlap_over_target_percent'),(100*I/S,'B_overlap_over_traced_study_percent')]:
    assert math.isclose(calculated,expected[key],rel_tol=1e-12,abs_tol=1e-8)
controls=[]
for c in assessment['ordered_water_land_controls']:
    actual=s.covers(Point(c['longitude'],c['latitude']))
    assert actual==c['expected_inside_trace']
    controls.append({**c,'coordinator_actual_inside':actual})
repairs=assessment['bounded_decorative_edge_repair']
assert math.isclose(area(s)-area(before),repairs['added_study_area_km2'],rel_tol=1e-9)
record={
    'status':'PASS coordinator source/visual/calibration/geometry check; regional adoption and shared display pending',
    'source_prose_review':'Coordinator read main PDF3/printed296 Figure1 caption and PDF4/printed297 methods2.2–2.4. Three colored blocks define displayed study domain; prose30–50N/150E is an enclosing description and does not establish a full rectangle.',
    'visual_review':'Coordinator inspected native Figure1 and corrected target/trace overlay. Preserve stepped KC/OF edges, islands and coastline; five bounded decorative crossings restored only source-supported water.',
    'source_raster_pixel_exact':True,'source_pdf_page':3,'source_image_xref':18,
    'independent_geodesic_results':{'target_area_km2':R,'study_area_km2':S,'intersection_km2':I,'A_percent':100*I/R,'B_percent':100*I/S},
    'water_land_controls':controls,
    'bounded_repair_check':{'removed_area_km2':area(before.difference(s)),'difference_of_full_polygon_areas_km2':area(s)-area(before),'separately_measured_added_pieces_km2':area(s.difference(before)),'area_measurement_note':'Planar clipping changes geodesic edge partitioning. Full polygon area difference is the stated1971.459366km²; separately measuring added pieces gives1971.646581km². Both use WGS84 and differ well below graphical uncertainty.','reported_repair':repairs},
    'reported_source_area_km2':913102,
    'limits':'Low confidence approximate colored-domain trace, not author GIS. Published area retained separately; ±.10degree sensitivity is not a confidence interval. Source Table4 reverses KC/OYC labels relative to consistent Figure1/methods; retain both source observations. No PPR/catch multiplier or scientific parameter change.',
    'evaluated_geometry_sha256':sha(geometry),
    'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [source,geometry,QA/'Figure1_native.png',QA/'target_trace_controls.png',QA/'geography_trace_assessment.json']],
}
(BASE/'verification/LME_049_geography_coordinator_review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record['independent_geodesic_results']))
