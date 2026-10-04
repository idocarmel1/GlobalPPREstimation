"""Static saved-cell QA preview; not a claim of native Excel rendering."""
from pathlib import Path
import textwrap
import openpyxl
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
REGION=HERE.parents[3]
path=REGION/"52_GM2019_Fig9_Pelagic_balanced_(2000-2014)_taxon_mapping_appendix.xlsx"
w=openpyxl.load_workbook(path,data_only=True)
s=w["Taxon mappings"]
font=ImageFont.truetype("C:/Windows/Fonts/calibri.ttf",18)
bold=ImageFont.truetype("C:/Windows/Fonts/calibrib.ttf",18)
widths=[245,52,140,180,325,120,540]
headers=["Taxon","TL","Catch (t)","Simple PPR (tC)","Groups / weights","Confidence","Reason / sources"]
rows=list(s.iter_rows(min_row=3,values_only=True))
def wrapped(text,width):
    words=str(text).split();lines=[];line=""
    for word in words:
        candidate=(line+" "+word).strip()
        if font.getlength(candidate)>width and line:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    return lines or[""]
for name,selected in [("top",rows[:4]),("zero_and_unresolved",[r for r in rows if r[0]in {"Echinozoa","Cyprinidae","Haliotis"}])]:
    vals=[];heights=[]
    for row in selected:
        cells=[]
        for i,(value,width)in enumerate(zip(row,widths)):
            if i in {2,3}and isinstance(value,(int,float)):value=f"{value:,.3f}"
            cells.append(wrapped(value,width-18))
        vals.append(cells);heights.append(max(len(c)for c in cells)*23+20)
    im=Image.new("RGB",(sum(widths)+20,sum(heights)+95),"white");d=ImageDraw.Draw(im)
    d.text((10,10),"Saved XLSX cell preview • 2019 landings • PPR carbon • full reasons retained",font=bold,fill="#174C58")
    x=10;y=40
    for text,width in zip(headers,widths):d.rectangle((x,y,x+width,y+45),fill="#174C58");d.text((x+8,y+10),text,font=bold,fill="white");x+=width
    y=85
    for row,cells,height in zip(selected,vals,heights):
        x=10
        for lines,width in zip(cells,widths):
            d.rectangle((x,y,x+width,y+height),fill="#F5F9FA",outline="#CBD5DB")
            for line_index,line in enumerate(lines):d.text((x+8,y+8+23*line_index),line,font=font,fill="#172A32")
            x+=width
        y+=height
    im.save(HERE/f"appendix_{name}_qa.png")
w.close()
print("Static XLSX excerpts saved")
