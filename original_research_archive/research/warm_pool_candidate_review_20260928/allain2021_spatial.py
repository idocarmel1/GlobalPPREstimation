"""Geodesic intersection for the explicit 2021 study rectangle across the dateline."""
import hashlib
import json
from shapely.geometry import box, shape, mapping
from shapely.ops import unary_union
from spatial_overlap import ROOT, OUT, area

domain=unary_union([box(140,-20,180,20),box(-180,-20,-150,20)])
result={'source':'Allain et al.2021 SC17-EB-IP-11, PDF page4 Methods and Figure1',
        'bounds_description':'140E–150W, 20S–20N',
        'method':'WGS84 geodesic area of explicit study rectangle intersected with actual stored region polygons; split at dateline; densified 0.05 degrees and checked at 0.01 degrees; land not subtracted',
        'computed_gross_area_km2':area(domain),'overlap':{}}
for uid, filename, rid in [('HS_071','HighSeas.geojson',71),('EEZ_941','EEZs.geojson',941)]:
    p=ROOT/'common_reference_data/geography'/filename
    raw=p.read_bytes(); feature=next(f for f in json.loads(raw)['features'] if f['properties'].get('region_id')==rid)
    target=shape(feature['geometry']); inter=domain.intersection(target); a=area(inter)
    result['overlap'][uid]={'intersection_km2':a,'percent_target_region_covered':100*a/area(target),
        'percent_gross_model_domain_in_region':100*a/area(domain),
        'area_refinement_difference_percent':100*(area(inter,.01)-a)/a,
        'target_source':p.relative_to(ROOT).as_posix(),'target_sha256':hashlib.sha256(raw).hexdigest()}
(OUT/'ALLAIN2021_SPATIAL_OVERLAP.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
for paper, geom in [('Allain-2021',domain),('Griffiths-2019',box(140,-15,180,10))]:
    footprint={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'paper_id':paper,'geometry_basis':'explicit published study rectangle; includes land; not an author-supplied habitat polygon'},'geometry':mapping(geom)}]}
    (ROOT/'regions/EEZ_941/papers'/paper/'footprint.geojson').write_text(json.dumps(footprint,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
