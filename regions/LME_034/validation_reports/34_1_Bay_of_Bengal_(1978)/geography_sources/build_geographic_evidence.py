from pathlib import Path
import sys, json, hashlib

root = Path.cwd()
out = root/'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/geography_sources'
sys.path.insert(0, str(out/'_libs'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPolygon
from shapely.geometry import shape, box
from shapely.ops import transform
from pyproj import Geod, Transformer

def read_json(path): return json.loads(path.read_text(encoding='utf8'))
region_path = root/'common_reference_data/geography/LMEs.geojson'
land_path = root/'common_reference_data/geography/basemaps/ne_50m_land.geojson'
target = next(f for f in read_json(region_path)['features'] if f['properties']['region_id']==34)
R = shape(target['geometry'])
assert R.is_valid
geod = Geod(ellps='WGS84')
area_R = abs(geod.geometry_area_perimeter(R)[0])/1e6
project = Transformer.from_crs('EPSG:4326', '+proj=laea +lat_0=12 +lon_0=87 +datum=WGS84 +units=m +no_defs', always_xy=True).transform
laea_R = transform(project,R).area/1e6
area_S = 6205051
figure, ax = plt.subplots(figsize=(10.6,9.0),dpi=190)
ax.set_facecolor('#e9f3f8')
domain=box(66,-6,106,27)
for feature in read_json(land_path)['features']:
    geom=shape(feature['geometry'])
    if not geom.intersects(domain): continue
    geoms=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
    for poly in geoms:
        ax.add_patch(PlotPolygon(np.array(poly.exterior.coords),facecolor='#e5dfce',edgecolor='#98958c',linewidth=0.4,zorder=2))
for poly in R.geoms:
    ax.add_patch(PlotPolygon(np.array(poly.exterior.coords),facecolor='#b5d9f3',edgecolor='#175f9a',linewidth=1.8,zorder=3))
    for interior in poly.interiors:
        ax.add_patch(PlotPolygon(np.array(interior.coords),facecolor='#e5dfce',edgecolor='#98958c',linewidth=0.3,zorder=4))

labels=[('India',77.6,20.0),('Bangladesh',90.5,25.0),('Myanmar',99.2,20.9),('Thailand',102.2,14.5),('Malaysia',103.1,7.0),('Sri Lanka',78.1,8.9),('Northern\nSumatra',101.5,1.6),('Maldives',71.1,5.0)]
for label,x,y in labels: ax.text(x,y,label,fontsize=10,color='#343738',ha='center',zorder=5)
ax.plot(73.1,4.2,'o',color='#77746b',ms=3,zorder=5)
ax.text(84.0,14.2,'Bay of Bengal\nLME_034',fontsize=16,color='#175f9a',ha='center',va='center',weight='bold',zorder=5)
ax.text(68,-4.6,'Blue boundary and fill: target R\nMaldives is outside this target',fontsize=10,color='#243a47',bbox={'facecolor':'white','edgecolor':'none','alpha':0.9},zorder=5)
ax.set_xlim(67,106); ax.set_ylim(-6,27)
ax.set_aspect(1/np.cos(np.radians(12)))
ax.set_xticks(range(70,107,5));ax.set_yticks(range(-5,28,5))
ax.set_xticklabels([f'{v}°E' for v in range(70,107,5)])
ax.set_yticklabels([f'{abs(v)}°'+('S' if v<0 else 'N' if v>0 else '') for v in range(-5,28,5)])
ax.grid(alpha=0.25,linewidth=0.5,zorder=1)
ax.set_title('Target region: Bay of Bengal LME (R)',fontsize=18,loc='left',pad=15,weight='bold')
figure.text(0.12,0.035,'Boundary: project Sea Around Us LMEs.geojson, region_id 34. Land: Natural Earth 1:50m (display only).',fontsize=9,color='#48545b')
figure.subplots_adjust(bottom=0.095,top=0.91,left=0.1,right=0.97)
figure.savefig(out/'target_LME034_boundary.png',facecolor='white')
plt.close(figure)

evidence={
 'definitions':{'R':'Bay of Bengal target LME_034, region_id 34 in common_reference_data/geography/LMEs.geojson','S':'Selected Guénette (December 2013) 1978 model study area, including Maldives, northern Sumatra and adjacent high seas (p7, Figure1 p8)'},
 'target_boundary_path':str(region_path.relative_to(root)).replace('\\','/'),
 'target_boundary_sha256':hashlib.sha256(region_path.read_bytes()).hexdigest(),
 'R_geometry_type':R.geom_type,'R_geometry_valid':R.is_valid,'R_bbox_degrees':list(R.bounds),
 'R_area_WGS84_geodesic_km2':area_R,
 'R_area_Lambert_azimuthal_equal_area_km2':laea_R,
 'S_area_table1_km2':area_S,
 'estimated_overlap_km2':area_R,
 'A_region_covered_by_study_percent':100,
 'B_study_covered_by_region_percent':area_R/area_S*100,
 'report_display':'A ≈ 100%; B ≈ 59%',
 'approximation_method':'Source-defined containment, visually checked against Figure1 and the actual target boundary; WGS84 geodesic area of R divided by the numerical S area in Table1. No raw pixel areas were compared. A is an approximate source-domain/visual assessment, and B is a conditional area ratio, not a measurement of an exact digital author polygon.',
 'containment_evidence':'p7 explicitly defines the study area as LME Bay of Bengal extended to northern Sumatra and Maldives. Figure1 shows its outer boundary west of R around Maldives and south of the Bay/Andaman area, with both Bay shore systems represented. The current target excludes Maldives and much of the added southwest high seas.',
 'uncertainty':'The 2013 author boundary is not available as a verified digital polygon; the project article footprint is a target-boundary placeholder, explicitly not an author boundary. Minor historical SAUP/current boundary and coastline differences prevent an exact overlap claim. No statistical confidence interval is asserted.',
 'source_table1':{'total_study_area_km2':6205051,'shelf_area_km2':936168,'Maldives_km2':915423,'high_seas_km2':1929874,'regions2_plus3_from_total_km2':3359754,'regions2_plus3_printed_rows_sum_km2':3359755},
 'source_discrepancies':[{'location':'p7 prose versus Table1 p8','finding':'p7 says 12% continental shelf; Table1 shelf936168 / total6205051 equals15.09%. Use numerical study area for overlap, not that prose percentage.'},{'location':'Table1 p8','finding':'Printed EEZ country rows sum6205052, one km² above printed total6205051; consistent with aggregate rounding, immaterial to displayed overlap.'}],
 'figures':{
  'target':{'path':str((out/'target_LME034_boundary.png').relative_to(root)).replace('\\','/'),'caption':'Target region R: Bay of Bengal LME_034. Boundary from project Sea Around Us LMEs.geojson (region_id34); Natural Earth1:50m land is a display basemap. Maldives is outside R.'},
  'source':{'path':str((out/'source_figure1_p08.png').relative_to(root)).replace('\\','/'),'caption':'Guénette (December2013), Figure1, PDF/printed page8: Map of the study area, the Bay of Bengal LME and the Maldives. Source UBC SAUP. Read together with study-area definition p7 and Table1 p8.','pdf_page':8,'printed_page':8,'figure_number':1,'original_pdf':'regions/LME_034/papers/LME034-Guenette-2013/009031359-84f3dc3d.pdf'}
 }
}
(out/'geographic_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:evidence[k] for k in ['R_area_WGS84_geodesic_km2','R_area_Lambert_azimuthal_equal_area_km2','S_area_table1_km2','report_display']},ensure_ascii=False,indent=2))
