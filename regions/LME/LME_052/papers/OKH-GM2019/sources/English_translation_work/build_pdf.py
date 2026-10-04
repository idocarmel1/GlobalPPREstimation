from pathlib import Path
import re, json, hashlib, html
from PIL import Image as PILImage, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, Flowable, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader
import pypdfium2 as pdfium
from support import ABSTRACT,CAPTIONS,KEYS,FIG8_CATEGORIES,FIG9_NODES,TABLE1,TABLE2,TABLE3,BIBR

HERE=Path(__file__).resolve().parent
BUNDLE=HERE.parent
SOURCE=BUNDLE/'gorbatenko_melnikov_2019.pdf'
OUT=BUNDLE/'gorbatenko_melnikov_2019_English_translation.pdf'
SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
BODY=ParagraphStyle('body',fontName='Arial',fontSize=9.5,leading=12.8,spaceAfter=7)
SMALL=ParagraphStyle('small',parent=BODY,fontSize=8.2,leading=10.5,spaceAfter=4.8)
CAP=ParagraphStyle('caption',parent=SMALL,fontName='Arial-Bold',spaceBefore=5)
NOTE=ParagraphStyle('note',parent=SMALL,textColor=colors.HexColor('#5b5141'),backColor=colors.HexColor('#f8f4e9'),borderPadding=6,spaceBefore=6,spaceAfter=10)
H1=ParagraphStyle('h1',parent=BODY,fontName='Arial-Bold',fontSize=19,leading=24,spaceAfter=14)
H2=ParagraphStyle('h2',parent=BODY,fontName='Arial-Bold',fontSize=13,leading=17,spaceBefore=7,spaceAfter=10,keepWithNext=True)
H3=ParagraphStyle('h3',parent=BODY,fontName='Arial-Bold',fontSize=11,leading=15,spaceBefore=5,spaceAfter=7,keepWithNext=True)
CELL=ParagraphStyle('cell',parent=SMALL,fontSize=7.3,leading=9.2,spaceAfter=0)
W,H=A4
WIDTH=W-84

def markup(s):
    s=s.replace('\u00ad','').replace('\ufffe','').replace('–','-').replace('—','-').replace('‑','-').replace('−','-')
    s=html.escape(s)
    s=re.sub(r'([¹²³⁴⁵⁶⁷⁸⁹⁰]+)',lambda m:'<super>'+m.group().translate(str.maketrans('¹²³⁴⁵⁶⁷⁸⁹⁰','1234567890'))+'</super>',s)
    s=re.sub(r'\b(B|N|P|A|t|TL|δ¹⁵N)_(\d|[bcent])\b',r'\1<sub>\2</sub>',s)
    return s
def p(s,sty=BODY):return Paragraph(markup(s),sty)

class SourceMarker(Flowable):
    def __init__(self,page):super().__init__();self.page=page;self.width=0;self.height=0
    def draw(self):self.canv.source_page=self.page

class FooterCanvas(canvas.Canvas):
    def __init__(self,*a,**k):super().__init__(*a,**k);self.source_page=None;self.page_states=[]
    def showPage(self):
        self.page_states.append(dict(self.__dict__));self._startPage()
    def save(self):
        total=len(self.page_states)
        for st in self.page_states:
            self.__dict__.update(st)
            self.setStrokeColor(colors.HexColor('#aab7bb'));self.setLineWidth(.4);self.line(42,40,W-42,40)
            self.setFont('Arial',7.5);self.setFillColor(colors.HexColor('#46565d'))
            source='Translation front matter' if self.source_page is None else f'Original printed p. {self.source_page} | PDF p. {self.source_page-142}'
            self.drawString(42,28,source)
            self.drawRightString(W-42,28,f'English translation {self._pageNumber}/{total}')
            self.setFont('Arial',7.2);self.drawString(42,H-25,'Gorbatenko & Melnikov (2019) | Unofficial English translation')
            super().showPage()
        super().save()

# Rasterize the original graphics at 216 dpi; the graphics are preserved,
# and all interpretive text is supplied separately in English.
figure_specs={1:(146,None),2:(148,(.122,.181,.878,.461)),3:(150,(.094,.10,.61,.327)),4:(150,None),5:(151,(.116,.058,.887,.389)),6:(151,(.119,.550,.881,.865)),7:(152,(.097,.472,.905,.693)),8:(153,(.097,.064,.908,.365)),9:(157,None),10:(158,(.123,.068,.891,.262))}
doc_source=pdfium.PdfDocument(str(SOURCE))
reader_source=PdfReader(SOURCE)
for num,(page,box) in figure_specs.items():
    if num in [1,4,9]:
        im=reader_source.pages[page-143].images[1 if num==4 else 0].image.convert('RGB')
    else:
        im=doc_source[page-143].render(scale=3).to_pil().convert('RGB')
        im=im.crop(tuple(round(x*(im.width if n%2==0 else im.height)) for n,x in enumerate(box)))
    im.save(HERE/f'figure_{num}_original.png')

def make_table(data,widths,header_rows=1,small=False):
    sty=CELL if not small else ParagraphStyle('tiny',parent=CELL,fontSize=7,leading=8.7)
    rows=[[p(str(x),sty) for x in row] for row in data]
    tbl=Table(rows,colWidths=widths,repeatRows=header_rows,hAlign='LEFT')
    tbl.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,header_rows-1),colors.HexColor('#e6eff1')),('LINEBELOW',(0,header_rows-1),(-1,header_rows-1),.7,colors.HexColor('#53767e')),('ROWBACKGROUNDS',(0,header_rows),(-1,-1),[colors.white,colors.HexColor('#f5f7f7')]),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LINEBELOW',(0,header_rows),(-1,-1),.2,colors.HexColor('#d2dadc'))]))
    return tbl

def table(num):
    if num==1:
        rows=[['Group','Winter','','','Spring','','','Summer','','','Autumn','',''],['','B','P','P/B','B','P','P/B','B','P','P/B','B','P','P/B']]+TABLE1
        tbl=make_table(rows,[79]+[(WIDTH-79)/12]*12,2,True)
        tbl.setStyle(TableStyle([('SPAN',(1,0),(3,0)),('SPAN',(4,0),(6,0)),('SPAN',(7,0),(9,0)),('SPAN',(10,0),(12,0))]))
        return [p('Table 1. Long-term mean (2000-2014) biomass (B) and production (P) of dominant plankton groups in the epipelagic layer of the Okhotsk Sea, million tonnes.',CAP),tbl,p('Note: ±SE did not exceed 10% of the biomasses presented.',SMALL),Spacer(1,8)]
    if num==2:
        return[p('Table 2. Shares of annual zooplankton production and that of its dominant groups consumed by predatory plankton and nekton in the epipelagic layer of the Okhotsk Sea, %. ',CAP),make_table([['Food component','Predatory plankton','Nekton','Total']]+TABLE2,[195,(WIDTH-195)/3,(WIDTH-195)/3,(WIDTH-195)/3]),Spacer(1,10)]
    headers=['TL','Ecosystem component','B wet','Wet/C','B C*','P/B C','P wet','P C','P/area','Share %']
    return[p('Table 3. Principal production parameters of the pelagic community of the Okhotsk Sea in 2000-2014.',CAP),p('B wet: biomass, million tonnes wet matter. Wet/C: wet-matter/carbon coefficient. B C*: biomass, million tC/year as printed. P/B C: P/B ratio in carbon. P wet: production, million tonnes wet matter. P C: production, million tC/year. P/area: production, g/C/m² as printed. Share: component importance at its trophic level in carbon, %. TL: trophic level.',SMALL),make_table([headers]+TABLE3,[24,105]+[(WIDTH-129)/8]*8,1,True),p('* Other small fish.\n** Predatory fish and seabirds.\n*** Toothed whales and pinnipeds.\n**** Sharks, daggertooth, lancetfish, and other predatory fish, including halibuts with pelagic feeding.',SMALL),p('Translation note: the source labels carbon biomass with /year. This header and all printed values, including discrepancies with prose and Figure 9, have been retained.',NOTE)]

def figure(num):
    im=PILImage.open(HERE/f'figure_{num}_original.png');ww=WIDTH;hh=ww*im.height/im.width
    maxh=525 if num==9 else 310 if num==1 else 365
    if hh>maxh:ww*=maxh/hh;hh=maxh
    out=[Image(str(HERE/f'figure_{num}_original.png'),width=ww,height=hh),p(CAPTIONS[num],CAP)]
    if num in KEYS:out.append(p('English figure key: '+KEYS[num],SMALL))
    if num==8:
        d=[['No.','English category','No.','English category','No.','English category']]
        half=16
        for idx in range(half):
            r=[]
            for col in range(3):
                nxt=idx+col*half
                r+=([str(nxt+1),FIG8_CATEGORIES[nxt]] if nxt<len(FIG8_CATEGORIES) else ['',''])
            d.append(r)
        out.extend([p('Figure 8: ordered English category key',H3),make_table(d,[22,WIDTH/3-22]*3)])
    return out

def fig9key():
    rows=[['English node','Production','English node','Production']]
    for i in range(11):rows.append(list(FIG9_NODES[i])+list(FIG9_NODES[i+11]))
    return[p('Figure 9: complete English node key',H3),p('Production is in million tC/year, exactly as shown in the boxes. Detritus has no printed production value. Vertical axis: trophic levels I-V. Colours identify the original flow categories; arrows and numerical labels have not been altered or reinterpreted.',SMALL),make_table(rows,[WIDTH*.35,WIDTH*.15,WIDTH*.35,WIDTH*.15]),p('The published English caption describes the line numbers as "underlined numbers" and the next link as the "next higher trophic level." The Russian caption instead says numbers on the line and the subsequent trophic link; its wording is used in the translated caption above.',NOTE)]

def english_refs(page):
    text=(HERE/f'source_{page}.txt').read_text(encoding='utf8')
    if page==161:text=text.split('References',1)[1]
    text=text.split('Поступила',1)[0]
    text=re.sub(r'^\s*'+str(page)+r'\s*\n','',text)
    lines=text.splitlines();out=[];buf=[]
    for line in lines:
        if re.match(r'^[A-Z][A-Za-z’\-]+,\s+(?:[A-Z]\s*\.|Yu\.|Ch\.)',line) and buf:
            out.append(' '.join(buf));buf=[]
        line=line.strip()
        if line:buf.append(line)
    if buf:out.append(' '.join(buf))
    clean=[]
    for txt in out:
        txt=txt.replace(' - ','-').replace('V .','V.').replace('V ol.','Vol.').replace('summer- autumn','summer-autumn')
        txt=txt.replace('2018. — 48 с.','2018. - 48 pp.')
        txt=re.sub(r'(\w)- (\w)',r'\1\2',txt)
        clean.append(txt)
    return clean

story=[p('UNOFFICIAL ENGLISH TRANSLATION',H2),p('Trophodynamics of marine organisms in the epipelagic layer of the Okhotsk Sea in the 2000s',H1),p('K. M. Gorbatenko and I. V. Melnikov',H2),p('Izvestiya TINRO (2019), volume 198, pages 143-163. DOI: 10.26428/1606-9919-2019-198-143-163.'),Spacer(1,12),p('Prepared for research reading on 3 October 2026. This is an unofficial AI-assisted translation from Russian, not an author-approved or publisher-issued English edition. The original PDF is authoritative. All main text, three tables, ten figures and their captions, author statements, both bibliographies, and publication dates are included. The existing English abstract and English reference list are retained, with typographic normalization.'),p('Each section and footer identifies the original printed page and PDF page. The English translation uses a new page layout and is longer than the 21-page source. Sentence continuations across original page boundaries are marked by ellipses. Original figure graphics retain their numerical values and Russian labels; accompanying English keys translate all labels and legends. Figure 9 is reproduced from its original embedded image and has a complete English node key.'),p('Printed numerical and scientific inconsistencies are preserved rather than corrected. A small number of clearly marked translation notes explain apparent source inconsistencies or wording differences. In particular, the published English abstract gives annual nekton consumption in tC, while the Russian abstract gives tonnes of food. The two abstracts are both retained.'),p('Source PDF: https://izvestiya.tinro-center.ru/jour/article/download/497/467',SMALL),p('Source SHA-256: '+SHA,SMALL),p('Citation: Gorbatenko, K. M., and Melnikov, I. V. (2019). Trophodynamics of marine organisms in the epipelagic layer of the Okhotsk Sea in 2000s. Izvestiya TINRO, 198, 143-163. https://doi.org/10.26428/1606-9919-2019-198-143-163',SMALL)]
source_markers=[]
text=(HERE/'translation.txt').read_text(encoding='utf8')
for chunk in re.split(r'^@@',text,flags=re.M)[1:]:
    first,*lines=chunk.splitlines();page=int(first);source_markers.append(page)
    story.extend([PageBreak(),SourceMarker(page),p(f'Original page {page} (source PDF page {page-142})',H2)])
    for line in lines:
        if not line.strip():continue
        if line.startswith('!FIG|'):story.extend(figure(int(line.split('|')[1])))
        elif line.startswith('!TABLE|'):story.extend(table(int(line.split('|')[1])))
        elif line.startswith('!KEY|'):story.extend(fig9key())
        elif line.startswith('!BIBR|'):story.extend(p(s,SMALL) for s in BIBR[page])
        elif line.startswith('!BIBE|'):story.extend(p(s,SMALL) for s in english_refs(page))
        elif line.startswith('!ABSTRACT'):story.extend(p(s) for s in ABSTRACT.split('\n\n'))
        elif line.startswith('!NOTE|'):story.append(p('Translation note: '+line.split('|',1)[1],NOTE))
        elif line.startswith('!EQ|'):story.append(p(line.split('|',1)[1],BODY))
        elif line.startswith('### '):story.append(p(line[4:],H3))
        elif line.startswith('## '):story.append(p(line[3:],H2))
        elif line.startswith('# '):story.append(p(line[2:],H1))
        else:story.append(KeepTogether([p(line)]))

doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=43,bottomMargin=53,title='Gorbatenko and Melnikov 2019 - Unofficial English translation',author='Original authors: K. M. Gorbatenko and I. V. Melnikov',subject='Complete unofficial English translation; original figures retained with English keys')
doc.build(story,canvasmaker=FooterCanvas)

# Reopen and perform reproducible coverage and numerical checks.
reader=PdfReader(OUT)
full='\n'.join(q.extract_text() for q in reader.pages)
checks={'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA,'source_pages':source_markers,'all_source_pages':source_markers==list(range(143,164)),'figures':{str(n):f'Figure {n}.' in full for n in range(1,11)},'tables':{str(n):f'Table {n}.' in full for n in range(1,4)},'translated_russian_references':sum(len(v) for v in BIBR.values()),'original_english_references':sum(len(english_refs(pn)) for pn in [161,162,163]),'table3_rows_including_subtotals':len(TABLE3),'table1_data_rows':len(TABLE1),'figure8_category_count':len(FIG8_CATEGORIES),'figure9_node_count':len(FIG9_NODES),'output_pages':len(reader.pages),'output_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()}
assert checks['source_unchanged'] and checks['all_source_pages']
assert all(checks['figures'].values()) and all(checks['tables'].values())
assert checks['translated_russian_references']==52
assert checks['original_english_references']==52
(HERE/'verification.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
(HERE/'English_translation_extracted.txt').write_text(full,encoding='utf8')
outdoc=pdfium.PdfDocument(str(OUT))
for idx,pg in enumerate(outdoc):
    im=pg.render(scale=1.4).to_pil().convert('RGB');im.save(HERE/f'english_page_{idx+1:02d}.png')
for start in range(0,len(outdoc),8):
    contact=PILImage.new('RGB',(1200,900),'#ddd');d=ImageDraw.Draw(contact)
    for idx in range(start,min(start+8,len(outdoc))):
        im=PILImage.open(HERE/f'english_page_{idx+1:02d}.png');im.thumbnail((285,410))
        x=((idx-start)%4)*300;y=((idx-start)//4)*450
        contact.paste(im,(x,y+22));d.text((x+10,y+5),f'English page {idx+1}',fill='black')
    contact.save(HERE/f'contact_english_{start+1:02d}.png')
print(json.dumps(checks,indent=2))
