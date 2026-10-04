from pathlib import Path
import json,hashlib
from shapely.geometry import shape,Polygon,mapping,Point
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[4]; OUT=Path(__file__).resolve().parent/'geography';OUT.mkdir(exist_ok=True)
target=ROOT/'regions/LME_013/validation_reports/13_1_Chilean_Patagonia_(1980)/geography/target_region.geojson'
geo=json.loads(target.read_text(encoding='utf-8'));R=shape(geo['geometry']);G=Geod(ellps='WGS84')
pixels=[(209,282),(198,299),(196,315),(202,333),(214,351),(205,364),(212,380),(231,391),(250,403),(267,423),(279,448),(298,470),(310,494),(324,523),(334,550),(345,572),(360,591),(375,608),(382,634),(398,658),(415,683),(415,705),(410,719),(423,738),(442,754),(465,769),(496,791),(434,795),(411,783),(391,764),(375,743),(361,719),(348,696),(336,672),(319,646),(303,620),(288,593),(276,565),(263,538),(249,511),(235,484),(225,460),(213,436),(190,420),(176,409),(166,395),(161,377),(160,360),(160,340),(154,324),(154,306),(154,282)]
coords=[(-80+(x-252)/43.1,-(y-110)/43.1) for x,y in pixels];S=Polygon(coords)
def area(poly):
 if poly.geom_type=='Polygon':
  a=abs(G.polygon_area_perimeter(*zip(*poly.exterior.coords))[0]);return (a-sum(abs(G.polygon_area_perimeter(*zip(*h.coords))[0]) for h in poly.interiors))/1e6
 return sum(area(p) for p in poly.geoms if p.geom_type in ('Polygon','MultiPolygon'))
I=R.intersection(S); ar,as_,ai=area(R),area(S),area(I)
controls={'inside_near5S':(-81.8,-5),'inside9S':(-79.2,-9),'inside13S':(-77.05,-13),'outside_offshore9S':(-82,-9),'outside_south':(-75,-18)}
result={'source':'Chiaverano2018 Figure1 PDF2 printed29; Methods PDF3 printed30','source_figure_crop':'../source/evidence/study_figure1_crop.png','target_boundary_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'projection':'WGS84 geodesic areas; affine approximate graticule calibration','pixel_anchors':{'lon':{'x252':-80,'x470':-75,'x685':-70},'lat':{'y110':0,'y327':-5,'y541':-10,'y757':-15,'y972':-20}},'pixel_outline':pixels,'target_area_km2':ar,'traced_study_area_km2':as_,'reported_study_area_km2':165000,'intersection_km2':ai,'A_trace_percent':ai/ar*100,'B_trace_percent':ai/as_*100,'A_reported_area_ceiling_percent':165000/ar*100,'B_reported_area_sensitivity_percent':ai/165000*100,'control_points':{n:{'coordinates':c,'in_trace':S.covers(Point(c)),'in_target':R.covers(Point(c))} for n,c in controls.items()},'limitations':'Manual raster trace; tilted graticule and coarse source coastline. Target coastline differs from source raster. No invented confidence interval; source reported area is separate denominator sensitivity, not another polygon measurement.'}
result['approximate_A_range_percent']=[6,8];result['approximate_B_range_percent']=[90,100]
result['range_basis']='Source-reported165000km2 would occupy at most6.445% ofR; approximate trace gives7.558% and91.66% inclusion. Broad6-8%/90-100% brackets reflect source-area versus raster-boundary discrepancy, not statistical uncertainty. Traced overlap exceeds reported area so B_reported_area_sensitivity_percent is a rejected inconsistent denominator calculation, not an overlap estimate.'
(OUT/'target_region.geojson').write_text(json.dumps(geo),encoding='utf-8');(OUT/'study_trace.geojson').write_text(json.dumps({'type':'Feature','properties':{'method':'approximate source Figure1 shading outline'},'geometry':mapping(S)}),encoding='utf-8');(OUT/'geographic_assessment.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k.endswith('percent') or k.endswith('km2') or k=='control_points'}))
