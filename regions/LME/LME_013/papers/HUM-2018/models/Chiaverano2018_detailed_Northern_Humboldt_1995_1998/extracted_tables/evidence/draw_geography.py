from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
OUT=Path(__file__).resolve().parent/'geography'
R=json.loads((OUT/'target_region.geojson').read_text())['geometry'];S=json.loads((OUT/'study_trace.geojson').read_text())['geometry']
im=Image.new('RGB',(1500,1250),'white');d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21);title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',30)
d.text((45,25),'Humboldt Current boundary and Northern Humboldt study',fill='black',font=title)
def panel(rect,bounds,label):
 x0,y0,x1,y1=rect;lo,la,hi,ha=bounds
 def point(p):return (x0+(p[0]-lo)/(hi-lo)*(x1-x0),y1-(p[1]-la)/(ha-la)*(y1-y0))
 d.rectangle(rect,fill='#f3f6f8',outline='#777777',width=2)
 for lon in range(int(lo)+1,int(hi)+1,2):
  x,y=point((lon,la));d.line((x,y0,x,y1),fill='#dddddd');d.text((x-20,y1+8),str(lon),fill='black',font=small)
 for lat in range(int(la)+1,int(ha)+1,5):
  x,y=point((lo,lat));d.line((x0,y,x1,y),fill='#dddddd');d.text((x0-52,y-12),str(lat),fill='black',font=small)
 layer=Image.new('RGBA',im.size,(0,0,0,0));ld=ImageDraw.Draw(layer)
 for poly in R['coordinates']:
  ld.polygon([point(p) for p in poly[0]],fill='#bfd4e3',outline='#416c8b')
  for hole in poly[1:]:ld.polygon([point(p) for p in hole],fill='#f3f6f8')
 ld.polygon([point(p) for p in S['coordinates'][0]],fill='#dfa557',outline='#915710',width=3)
 mask=Image.new('L',im.size,0);ImageDraw.Draw(mask).rectangle(rect,fill=255);mask=ImageChops.multiply(mask,layer.getchannel('A'));im.paste(layer,(0,0),mask)
 d.rectangle(rect,outline='#777777',width=2)
 d.text((x0,y0-40),label,fill='black',font=font)
panel((100,140,630,1120),(-84,-59,-66,2),'Target region LME_013')
panel((815,140,1410,1120),(-83,-18,-73,-2),'Northern study and target coast')
d.rectangle((805,1180,832,1203),fill='#bfd4e3');d.text((843,1178),'Target region',font=small,fill='black')
d.rectangle((1080,1180,1107,1203),fill='#dfa557');d.text((1118,1178),'Approximate study trace',font=small,fill='black')
d.text((45,1200),'Coordinates in degrees; source Figure 1 shading traced approximately. Reported study area 165,000 km2.',fill='black',font=small)
im.save(OUT/'target_study_comparison.png')
