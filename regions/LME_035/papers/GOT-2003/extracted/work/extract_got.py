from pathlib import Path
import sys,json,re,subprocess,xml.etree.ElementTree as ET
from decimal import Decimal
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'extracted'/'work'
SKILL=Path(r'C:\Users\idoca\.agents\skills\ecopath-extraction\scripts')
sys.path.insert(0,str(SKILL))
import pdfgrid
PDF=ROOT/'content-d78aa261.pdf'
ORIGINAL=pdfgrid.bbox_xml
def rotated_bbox(pdf,page):
    xml=ORIGINAL(pdf,page)
    (WORK/f'page_{page}_bbox_original.xml').write_text(xml,encoding='utf-8')
    root=ET.fromstring(xml)
    for e in root.iter():
        if e.tag.endswith('word'):
            x0,y0,x1,y1=[float(e.attrib[a]) for a in ['xMin','yMin','xMax','yMax']]
            for k,v in zip(['xMin','yMin','xMax','yMax'],[792-y1,x0,792-y0,x1]):e.set(k,str(v))
    xml=ET.tostring(root,encoding='unicode')
    (WORK/f'page_{page}_bbox_clockwise.xml').write_text(xml,encoding='utf-8')
    return xml
def setup_rotation():
    pdfgrid.bbox_xml=rotated_bbox
    for p,dpi in [(8,300),(9,300),(13,220)]:
        src=WORK/f'content-d78aa261_page_{p}_{dpi}dpi.png'
        Image.open(src).transpose(Image.Transpose.ROTATE_270).save(WORK/f'page_{p}_upright.png')
def inspect():
    setup_rotation()
    for p in [8,9,13]:
        lines=pdfgrid.get_words(str(PDF),p,merge_gap=.4)
        (WORK/f'page_{p}_raw.txt').write_text('\n'.join(f'{i}: y={l.y:.2f} {l.text}' for i,l in enumerate(lines)),encoding='utf-8')
        print(p)
        for i,l in enumerate(lines):print(f'{i}: y={l.y:.2f} {l.text}')
def clean_num(s):
    if s in ['-','–','']:return None
    return s.strip('()').replace(' ','')
def canonical(s):
    return s.lower().replace(',','').replace('lutjanidae','lutianidae').replace('ponyfishes','pony fishes')
def extract():
    pdfgrid.bbox_xml=ORIGINAL
    groups=[]; provenance=[]
    for p,lo,hi in [(4,28,40),(5,4,30)]:
        lines=pdfgrid.get_words(str(PDF),p)
        (WORK/f'page_{p}_raw.txt').write_text('\n'.join(f'{i} {l.text}' for i,l in enumerate(lines)),encoding='utf-8')
        for line in lines[lo:hi+1]:
            vals=[c.text for c in line.cells]
            assert len(vals)==7,vals
            name=vals[0].replace(',','')
            n=len(groups)+1
            g={'n':n,'name':name}
            for field,raw in zip(['biomass','pb','qb','ee','pq','ba'],vals[1:]):
                g[field]=clean_num(raw)
                provenance.append({'group':n,'name':name,'parameter':field,'printed':raw,'value':g[field],'source':f'Table 1 PDF p.{p}; printed p.{364+p}','category':'model-estimated' if raw.startswith('(') else 'tabulated'})
            groups.append(g)
    assert len(groups)==40
    assert Decimal(groups[1]['pb'])/Decimal(groups[1]['qb'])==Decimal(groups[1]['pq'])
    (WORK/'GROUPS.json').write_text(json.dumps(groups,indent=2),encoding='utf-8')
    names={canonical(g['name']):g['n'] for g in groups}
    fleets=['Otter board trawl','Pair trawl','Beam trawl','Pushnet','Purse seine','Other gear']
    landings={};source_totals={}
    lines=pdfgrid.get_words(str(PDF),7)
    for line in lines[3:34]:
        vals=[c.text for c in line.cells]
        assert len(vals)==8,vals
        n=names[canonical(vals[0])]
        landings[str(n)]={f:v for f,v in zip(fleets,vals[1:7])}
        source_totals[str(n)]=vals[7]
    pdfgrid.bbox_xml=rotated_bbox
    diet={};matrix=[]
    columns=list(range(1,26))+list(range(29,35))
    for p,anchor in [(8,5),(9,2)]:
        lines=pdfgrid.get_words(str(PDF),p,merge_gap=.4)
        grid=pdfgrid.build_grid(lines,anchor_line=anchor)
        (WORK/f'page_{p}_grid.tsv').write_text(pdfgrid.grid_to_tsv(grid),encoding='utf-8')
        for row in grid:
            mt=re.match(r'^(\d+)\s+(.+)',row[0])
            if not mt:continue
            n=int(mt.group(1));label=mt.group(2)
            if not (1<=n<=40):continue
            if n not in [23,24]:assert names[canonical(label)]==n,(n,label)
            assert len(row)==32,(n,len(row),row)
            matrix.append({'prey':n,'name':groups[n-1]['name'],'page':p,'printed':dict(zip(map(str,columns),row[1:]))})
            for c,v in zip(columns,row[1:]):
                diet.setdefault(str(c),{})
                if v not in ['','–','-']:
                    Decimal(v)
                    diet[str(c)][str(n)]=v
    assert len(matrix)==40,len(matrix)
    assert len({r['prey'] for r in matrix})==40
    model={'metadata':{'LME':'35 Gulf of Thailand','model_number':'35_1','model_name':'Gulf of Thailand','model_year':1973},'groups':groups,'consumers':[g['n'] for g in groups if g['n'] not in [28,39,40]],'fleets':fleets,'landings':landings,'discards':{},'detritus_groups':['Detritus'],'detritus_fate':{},'diet':diet,'diet_rows':40,'landings_rows':40,'discards_rows':40}
    (WORK/'model.json').write_text(json.dumps(model,indent=2,ensure_ascii=False),encoding='utf-8')
    (WORK/'source_cells.json').write_text(json.dumps({'basic':provenance,'diet_matrix':matrix,'catch_printed_row_totals':source_totals},indent=2,ensure_ascii=False),encoding='utf-8')
    print('Groups:',len(groups),'diet columns printed',columns)
    print('Diet sums:',{c:str(sum((Decimal(v) for v in d.values()),Decimal(0))) for c,d in diet.items()})
    print('Catch fleet sums',{f:str(sum((Decimal(d[f]) for d in landings.values()),Decimal(0))) for f in fleets})
    print('Source-estimated fields:',len([x for x in provenance if x['category']=='model-estimated']))
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='extract':extract()
    else:inspect()
