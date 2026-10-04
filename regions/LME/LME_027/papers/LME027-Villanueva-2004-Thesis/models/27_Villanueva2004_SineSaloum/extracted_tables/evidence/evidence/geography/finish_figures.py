from pathlib import Path
import json,fitz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import shape
base=Path(__file__).resolve().parent
root=base.parents[5]
ident=base.parent/'identity'
with fitz.open(ident/'Villanueva2004_thesis_29305.pdf') as d:
    # Page coordinates preserve complete Figure2.2 and its source caption.
    page=d[41];page.get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(90,55,555,400)).save(base/'source_thesis_Figure2_2.png')
target=json.loads((base/'target_region.geojson').read_text(encoding='utf-8'))
geom=shape(target['geometry'])
land=json.loads((root/'common_reference_data/geography/basemaps/ne_50m_land.geojson').read_text(encoding='utf-8'))
fig,ax=plt.subplots(figsize=(5.5,7))
for f in land['features']:
    g=shape(f['geometry'])
    if not (g.bounds[2]<-28 or g.bounds[0]>0 or g.bounds[3]<10 or g.bounds[1]>38):
        for p in ([g] if g.geom_type=='Polygon' else g.geoms):
            x,y=p.exterior.xy;ax.fill(x,y,color='#e7e5df',edgecolor='#c8c5bc',linewidth=.4)
for p in geom.geoms:
    x,y=p.exterior.xy;ax.fill(x,y,color='#b1d7e4',edgecolor='#286982',linewidth=.7)
ax.set_xlim(-27,-5);ax.set_ylim(11,37);ax.set_aspect('equal');ax.set_xlabel('Longitude');ax.set_ylabel('Latitude');ax.set_title('Target region R: Canary Current LME 027');ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(base/'target_region.png',dpi=180);plt.close(fig)
d=json.loads((base/'geographic_assessment.json').read_text(encoding='utf-8'))
d['figures']=['source_thesis_Figure2_2.png','target_region.png','geographic_context.png','source_map_PDF3.png']
d['QA']='Rendered source Figure2.2, source table/matrix pages, target R and context figure visually inspected. No exact water polygon inferred.'
(base/'geographic_assessment.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Source S, target R and context figures saved')
