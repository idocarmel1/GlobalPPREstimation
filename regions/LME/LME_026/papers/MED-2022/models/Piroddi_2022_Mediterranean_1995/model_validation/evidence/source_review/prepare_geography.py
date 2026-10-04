from pathlib import Path
import json,hashlib,math
from PIL import Image,ImageDraw,ImageFont
import pypdfium2 as pdfium
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
G=OUT/'geography';G.mkdir(exist_ok=True)
Q=OUT/'qa';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Rasterization extracts source pixels; it does not alter model geography.
src=ROOT/'regions/LME_026/papers/MED-2022/s41598-022-18017-x-75a92a71.pdf'
pdf=pdfium.PdfDocument(src)
page=pdf[8];im=page.render(scale=3).to_pil();im.save(G/'source_page_9.png')
w,h=im.size
im.crop((int(w*.565),int(h*.446),int(w*.86),int(h*.59))).save(G/'study_area_figure_4h.png')
im.crop((int(w*.238),int(h*.055),int(w*.545),int(h*.19))).save(G/'study_domain_figure_4a.png')
gj=ROOT/'common_reference_data/geography/LMEs.geojson'
f=next(f for f in json.loads(gj.read_text(encoding='utf-8'))['features'] if f['properties'].get('region_id')==26)
(G/'target_region.geojson').write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf-8')
coords=f['geometry']['coordinates'];polys=coords if f['geometry']['type']=='MultiPolygon' else [coords]
pts=[p for poly in polys for ring in poly for p in ring]
extent=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
W,H=1500,760;canvas=Image.new('RGB',(W,H),'white');draw=ImageDraw.Draw(canvas)
try: font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
except OSError:font=small=ImageFont.load_default()
box=(90,85,1440,650);xmin,xmax=-7,37;ymin,ymax=29,47
def xy(p):return(box[0]+(p[0]-xmin)/(xmax-xmin)*(box[2]-box[0]),box[3]-(p[1]-ymin)/(ymax-ymin)*(box[3]-box[1]))
for x in range(-5,36,5):
 px,_=xy((x,0));draw.line((px,box[1],px,box[3]),fill='#dddddd');draw.text((px-15,665),str(x),font=small,fill='black')
for y in range(30,46,5):
 _,py=xy((0,y));draw.line((box[0],py,box[2],py),fill='#dddddd');draw.text((35,py-10),str(y),font=small,fill='black')
for poly in polys:
 for i,ring in enumerate(poly):draw.polygon([xy(p) for p in ring],fill='#d9e8f4' if i==0 else 'white',outline='#155480' if i==0 else '#888888',width=2)
draw.rectangle(box,outline='black',width=2)
draw.text((90,25),'Mediterranean Sea LME 026 target marine boundary',font=font,fill='black')
draw.text((650,710),'Longitude (degrees east)',font=small,fill='black')
label=Image.new('RGBA',(330,32),(255,255,255,0));ImageDraw.Draw(label).text((0,0),'Latitude (degrees north)',font=small,fill='black');label=label.rotate(90,expand=True);canvas.paste(label,(3,215),label)
for txt,lon,lat in [('Western Mediterranean',2,38),('Adriatic',17,44),('Ionian',17,36),('Aegean',25,39),('Levantine',28,33)]:draw.text(xy((lon,lat)),txt,font=small,fill='#174C58')
canvas.save(G/'target_region.png')
record={'region_id':'LME_026','target_boundary_source':'../../../../../common_reference_data/geography/LMEs.geojson','target_source_sha256':sha(gj),'feature_properties':f['properties'],'extent_degrees':extent,'study_source':'../../../papers/MED-2022/s41598-022-18017-x-75a92a71.pdf#page=9','source_sha256':sha(src),'study_locators':['Article pp.7-8: baseline1995 entire Mediterranean basin','Figure4a and4h p.9: ocean mask and four sub-basins'],'study_boundary_polygon_available':False,'inherited_footprint_not_independent':True,'method':'Visual geographic comparison of identical named basin and Figure4 marine extent with LME026 boundary, using Gibraltar, Gulf of Lions, Adriatic, Aegean and Levantine landmarks. Ocean masks compared geographically, not raw screenshot pixels.','A_region_covered_by_study_percent':[95,100],'B_study_covered_by_region_percent':[95,100],'estimate_qualifier':'approximately','uncertainty':'Coastal raster cells, Strait of Gibraltar boundary and Sea of Marmara boundary; no author-cell polygon or independent exact area fraction.','images':['target_region.png','study_area_figure_4h.png','study_domain_figure_4a.png','source_page_9.png']}
(G/'geographic_assessment.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
template_pdf=Q/'template-render/template.pdf'
if template_pdf.exists():
 tp=pdfium.PdfDocument(template_pdf)
 for i in range(len(tp)):tp[i].render(scale=1.6).to_pil().save(Q/f'template-render/page-{i+1}.png')
print(json.dumps({'geography':record,'template_pages':len(tp) if template_pdf.exists() else None},ensure_ascii=True))
