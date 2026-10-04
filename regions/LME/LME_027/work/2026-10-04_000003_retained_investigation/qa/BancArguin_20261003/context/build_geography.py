from pathlib import Path
import sys,json,hashlib
out=Path(__file__).resolve().parent
sys.path.insert(0,str(out/'_deps'))
import numpy as np,fitz
from PIL import Image
from shapely.geometry import shape,mapping,Polygon,box,Point
from shapely.ops import unary_union
from pyproj import Geod,Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
root=out.parents[4]
paper=root/'regions/LME_027/papers/CAN-2014'
# Coordinates below refer to this explicit 1358 x 1824 rendition of the original TIFF.
im=Image.open(paper/'Figure_1-78156383.tif').convert('RGB').resize((1358,1824))
im.save(out/'source_figure1_digitizing_grid.png')
anchors=np.array([[662,197,-18,22],[1050,202,-16,22],[261,604,-20,20],[655,612,-18,20],[1048,617,-16,20],[249,1019,-20,18],[647,1028,-18,18],[1044,1036,-16,18],[238,1434,-20,16],[639,1442,-18,16],[1041,1448,-16,16]],float)
design=np.c_[anchors[:,:2],np.ones(len(anchors))]
coeff=np.linalg.lstsq(design,anchors[:,2:],rcond=None)[0]
residual=design@coeff-anchors[:,2:]
def geo(xy):return (np.c_[np.asarray(xy),np.ones(len(xy))]@coeff).tolist()
# Trace the western 200-m contour, not the much larger black EEZ outline or 20-m contour.
western=[[721,455],[717,485],[717,529],[733,553],[723,576],[726,597],[738,617],[758,633],[794,651],[818,662],[831,681],[840,704],[850,726],[865,747],[891,766],[895,785],[889,804],[896,825],[899,850],[908,875],[925,886],[936,866],[922,887],[923,913],[935,943],[930,958],[940,991],[943,1018],[967,1015],[947,1031],[939,1053],[934,1080],[932,1105],[923,1140],[908,1181],[887,1225],[891,1245],[882,1266],[902,1275],[887,1289],[884,1310],[880,1325],[891,1341],[880,1356],[878,1378],[870,1411],[856,1429]]
# Figure's north EEZ boundary bends from Cap Blanc toward the onshore national boundary.
trace_px=western+[[941,1430],[1120,1430],[1120,339],[865,339],[844,455],[721,455]]
raw=Polygon(geo(trace_px)).buffer(0)
lmepath=root/'common_reference_data/geography/LMEs.geojson'
target_obj=next(f for f in json.loads(lmepath.read_text(encoding='utf8'))['features'] if f['properties']['region_id']==27)
R=shape(target_obj['geometry'])
landpath=root/'common_reference_data/geography/basemaps/ne_50m_land.geojson'
land=unary_union([shape(f['geometry']) for f in json.loads(landpath.read_text(encoding='utf8'))['features'] if shape(f['geometry']).intersects(box(-30,5,0,40))])
S=raw.difference(land)
legacy=shape(json.loads((paper/'footprint.geojson').read_text(encoding='utf8'))['geometry'])
geod=Geod(ellps='WGS84')
def area(g):
 if g.geom_type in ['MultiPolygon','GeometryCollection']:return sum(area(p) for p in g.geoms)
 return abs(geod.geometry_area_perimeter(g)[0])/1e6 if g.geom_type=='Polygon' else 0
def metrics(s):
 ov=area(s.intersection(R));return {'study_area_km2':area(s),'intersection_km2':ov,'A_percent':100*ov/area(R),'B_percent':100*ov/area(s)}
stats=metrics(S)
for name,g,props in [('target_region',R,target_obj['properties']),('study_area_figure_trace',S,{'source':'Figure 1, PDF page 3; manual 200 m contour and figure north/south boundaries, Natural Earth50m land excluded','approximate':True}),('study_area_trace_before_land_exclusion',raw,{'approximate':True})]:
 (out/(name+'.geojson')).write_text(json.dumps({'type':'Feature','properties':props,'geometry':mapping(g)}),encoding='utf8')
def fill(ax,g,c,a=1,edge=None,lw=.5):
 if g.geom_type in ['MultiPolygon','GeometryCollection']:
  for p in g.geoms:fill(ax,p,c,a,edge,lw)
 elif g.geom_type=='Polygon':
  x,y=g.exterior.xy;ax.fill(x,y,color=c,alpha=a,edgecolor=edge,linewidth=lw)
  for h in g.interiors:
   x,y=h.xy;ax.fill(x,y,color='#eaf4f8')
def setup(ax,xlim,ylim):
 ax.set_facecolor('#eaf4f8');fill(ax,land,'#e3ddd2',edge='#938f86');ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.set_aspect(1/np.cos(np.deg2rad(np.mean(ylim))));ax.set_xlabel('Longitude');ax.set_ylabel('Latitude');ax.grid(alpha=.25)
fig,ax=plt.subplots(figsize=(7.1,8));setup(ax,(-26,-5),(10,37));fill(ax,R,'#4d92b8',.7,edge='#1c587e');fill(ax,S,'#e97929',1,edge='#9c4514');ax.set_title('Canary Current LME 27 and the Mauritanian shelf');ax.legend(handles=[Patch(color='#4d92b8',label='LME 27 target region'),Patch(color='#e97929',label='Study shelf: approximate figure trace')],loc='lower left',fontsize=9);fig.tight_layout();fig.savefig(out/'target_region.png',dpi=200);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(12,8))
setup(axs[0],(-26,-5),(10,37));fill(axs[0],R,'#4d92b8',.7,edge='#1c587e');fill(axs[0],S,'#e97929',1,edge='#9c4514');axs[0].set_title('Target LME and study location')
setup(axs[1],(-19,-15),(15.5,22));fill(axs[1],R,'#4d92b8',.35,edge='#1c587e');fill(axs[1],S,'#e97929',.75,edge='#9c4514');axs[1].set_title('Shelf trace, with land excluded')
for label,x,y in [('Cap Blanc',-17.05,20.77),('Cap Timiris',-16.5,19.35),('Nouakchott',-15.98,18.08)]:axs[1].plot(x,y,'ko',ms=3);axs[1].annotate(label,(x,y),xytext=(4,3),textcoords='offset points',fontsize=8)
fig.suptitle('Guénette, Meissa & Gascuel (2014): source model domain',fontsize=14)
fig.text(.5,.022,'Orange: approximate coast-to-200 m shelf from Figure 1. Blue: project LME 27 boundary.\nAreas use WGS84 geodesic geometry; these are geographical approximations, not statistical confidence limits.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.09,1,.95]);fig.savefig(out/'geographic_comparison.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,12));ax.imshow(im);xy=np.array(trace_px);ax.plot(xy[:,0],xy[:,1],color='red',lw=1.3);ax.scatter(anchors[:,0],anchors[:,1],c='blue',s=12);ax.set_axis_off();fig.tight_layout(pad=0);fig.savefig(out/'trace_overlay.png',dpi=170);plt.close(fig)
pdf=fitz.open(paper/'file-e30dfe50.pdf');pdf[2].get_pixmap(matrix=fitz.Matrix(2,2)).save(out/'source_figure1_pdf3_with_caption.png')
controls=[]
for label,x,y,expected in [('Baie d Arguin waters',-16.65,20.25,True),('Cap Blanc shelf west of cape',-17.3,20.6,True),('Nouakchott nearshore shelf',-16.2,18.1,True),('Offshore deeper water',-18.1,19,False),('Mauritania inland',-15.6,19.0,False),('South of study border',-16.4,15.7,False)]:
 p=Point(x,y);controls.append({'label':label,'lon':x,'lat':y,'expected_in_study':expected,'in_study_trace':S.covers(p),'land':land.covers(p),'in_region':R.covers(p),'agrees':S.covers(p)==expected})
result={'schema_version':1,'model_family':'Guénette Meissa Gascuel 2014 Base/M30/P30','source_reported_area_km2':33224,'source_latitude_prose':[16+4/60,20+46/60],'target_area_km2':area(R),'trace':stats,'reported_area_ratio_percent':100*33224/area(R),'legacy_unclipped_rectangle':metrics(legacy),'legacy_rectangle_without_land':metrics(legacy.difference(land)),'raw_trace_area_km2':area(raw),'land_excluded_km2':area(raw)-area(S),'grid_anchors_pixels_lonlat':anchors.tolist(),'pixel_frame':[1358,1824],'source_original_pixels':[3555,4772],'georeference_affine':coeff.tolist(),'anchor_max_abs_residual_degrees':np.max(abs(residual),axis=0).tolist(),'western_200m_contour_pixels':western,'full_polygon_pixels':trace_px,'point_controls':controls,'source_pdf_sha256':hashlib.sha256((paper/'file-e30dfe50.pdf').read_bytes()).hexdigest(),'source_tiff_sha256':hashlib.sha256((paper/'Figure_1-78156383.tif').read_bytes()).hexdigest(),'lme_geojson_sha256':hashlib.sha256(lmepath.read_bytes()).hexdigest(),'landmask_sha256':hashlib.sha256(landpath.read_bytes()).hexdigest(),'uncertainty':'Manual contour tracing, schematic source bathymetry and Natural Earth 1:50m coastline; north latitude prose does not encompass all marine embayment pixels in Figure 1. Do not interpret legacy box as author polygon. Reported-area comparison is an area-denominator sensitivity, not a second measured polygon.'}
(out/'geographic_assessment.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k in ['target_area_km2','trace','reported_area_ratio_percent','legacy_unclipped_rectangle','legacy_rectangle_without_land','point_controls']},indent=2))
