from pathlib import Path
import sys, json, re, subprocess, hashlib
from decimal import Decimal
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'extracted' / 'work'
SKILL = Path(r'C:\Users\idoca\.agents\skills\ecopath-extraction')
sys.path.insert(0, str(SKILL / 'scripts'))
import pdfgrid
PDF = ROOT / 'Olson_Watters_2003_ETP-c037fcbc.pdf'
def boxes(page):
    # Explicit UTF-8 avoids Windows cp1255 decoding of the bilingual source.
    out = subprocess.run(['pdftotext','-bbox-layout','-f',str(page),'-l',str(page),str(PDF),'-'],capture_output=True,check=True).stdout.decode('utf-8')
    (WORK / f'page_{page}_bbox.xhtml').write_text(out,encoding='utf-8')
    return pdfgrid._parse_words(out)
def scaled(s):
    return format(Decimal(s.replace(',','')).scaleb(-6), 'f')
def serial(w):
    return {'text':w.text,'bbox':[w.x0,w.y0,w.x1,w.y1]}
names = ['Pursuit birds','Grazing birds','Baleen whales','Toothed whales','Spotted dolphin','Mesopelagic dolphins','Sea turtles','Large yellowfin tuna','Large bigeye tuna','Large marlins','Large sailfish','Large swordfish','Large dorado','Large wahoo','Large sharks','Rays','Skipjack tuna','Albacore','Auxis spp.','Bluefin tuna','Small yellowfin tuna','Small bigeye tuna','Small marlins','Small sailfish','Small swordfish','Small dorado','Small wahoo','Small sharks','Miscellaneous piscivores','Flyingfishes','Misc. epipelagic fishes','Misc. mesopelagic fishes','Cephalopods','Crabs','Mesozooplankton','Microzooplankton','Large phytoplankton','Small producers','Detritus']
fields = ['tl','biomass','pb','qb','ee','unassim']
anchors = [156,204,265,318,367,410]
words = boxes(26)
provenance = {'source_sha256': hashlib.sha256(PDF.read_bytes()).hexdigest(),'basic':[],'diet':[],'catch':[]}
groups=[]
for n,name in enumerate(names[:38],1):
    y=128.3+(n-1)*12
    row=[w for w in words if abs(w.y0-y)<3]
    label=' '.join(w.text for w in sorted(row,key=lambda w:w.x0) if w.x0<140)
    assert label==name,(n,label,name)
    vals={}
    record={'n':n,'name':name,'page':26,'printed_page':156,'raw_words':[serial(w) for w in row],'fields':{}}
    for field,x in zip(fields,anchors):
        part=sorted([w for w in row if w.x0>140 and abs(w.xc-x)<26],key=lambda w:w.x0)
        # Adjacent anchors are >=43 apart; exact column edge rules avoid spillover.
        ranges={'tl':(143,173),'biomass':(174,239),'pb':(246,289),'qb':(299,339),'ee':(347,389),'unassim':(397,426)}
        a,b=ranges[field]
        part=sorted([w for w in row if a<=w.x0<b],key=lambda w:w.x0)
        if not part: continue
        raw=' '.join(w.text for w in part)
        value=raw.split()[0]
        estimated=len(part)>1 and part[-1].text=='1'
        if n==7 and field=='biomass':
            # English typesets the marker on the baseline; Spanish Table 2b
            # clearly prints 260 superscript 1 (PDF27 / printed157).
            assert value=='2601'
            value='260'
            estimated=True
        if value.startswith('<'):
            record['fields'][field]={'raw':raw,'value':None,'censored':True,'model_estimated':estimated}
            continue
        vals[field]=scaled(value) if field=='biomass' else value.replace(',','')
        record['fields'][field]={'raw':raw,'value':vals[field],'model_estimated':estimated}
    # The paper gives B on model-area basis, not habitat-area B.
    # No habitat-area parameter is asserted, including bluefin's diet overlap.
    if n in [8,9,20,21,22]: vals['z']=vals['pb']
    groups.append({'n':n,'name':name,**vals})
    provenance['basic'].append(record)
groups.append({'n':39,'name':'Detritus'})
diet={str(n):{} for n in range(1,37)}
for page,lo,hi in [(28,1,18),(29,19,36)]:
    ws=boxes(page)
    # The landscape table is stored sideways: prey rows lie along x,
    # predator columns along decreasing y. Anchor both axes on printed IDs.
    prey={int(w.text):w.xc for w in ws if w.text.isdigit() and 1<=int(w.text)<=40 and w.y0>620}
    pred={int(w.text):w.yc for w in ws if w.text.isdigit() and lo<=int(w.text)<=hi and 98<w.x0<105 and w.y0<500}
    assert len(prey)==40,(page,prey)
    assert len(pred)==18,(page,pred)
    rows=[]
    for w in ws:
        if not re.fullmatch(r'\d\.\d{3}',w.text): continue
        if not (110<w.x0<440 and 70<w.y0<500): continue
        i=min(prey,key=lambda i:abs(prey[i]-w.xc))
        j=min(pred,key=lambda j:abs(pred[j]-w.yc))
        assert abs(prey[i]-w.xc)<0.1,(page,w,i)
        assert abs(pred[j]-w.yc)<6,(page,w,j)
        key='import' if i==40 else str(i)
        assert key not in diet[str(j)],(page,i,j)
        diet[str(j)][key]=w.text
        provenance['diet'].append({'prey':i,'consumer':j,'value':w.text,'page':page,'printed_page':page+130,'bbox':[w.x0,w.y0,w.x1,w.y1]})
    # Reviewable conventional-orientation table, including external-prey row40.
    pred_ids=list(range(lo,hi+1))
    rows.append('Prey\tName\t'+'\t'.join(map(str,pred_ids)))
    for i in range(1,41):
        label=names[i-1] if i<=39 else 'Prey from outside the ETP'
        rows.append(f'{i}\t{label}\t'+'\t'.join(diet[str(j)].get('import' if i==40 else str(i),'') for j in pred_ids))
    (WORK/f'diet_table3a_page{page}.tsv').write_text('\n'.join(rows)+'\n',encoding='utf-8')
fleets=['Longliners','Baitboats','Purse-seine unassociated','Purse-seine floating-object','Purse-seine dolphin']
catch_maps={}
for page,kind in [(45,'landings'),(47,'discards')]:
    ws=boxes(page)
    catch_maps[kind]={}
    expected_y=136.1 if page==45 else 140.0
    right_edges=[205,258.3,301,343,385,427]
    for n,name in enumerate(names[:34],1):
        row=[w for w in ws if abs(w.y0-(expected_y+(n-1)*12))<.3]
        label=' '.join(w.text for w in sorted(row,key=lambda w:w.x0) if w.x0<167)
        assert label==name,(page,n,label)
        vals={}
        raw_vals={}
        for w in row:
            if w.x0<167: continue
            c=min(range(6),key=lambda c:abs(right_edges[c]-w.x1))
            assert abs(right_edges[c]-w.x1)<2,(page,n,w,c)
            assert c not in raw_vals,(page,n,c)
            raw_vals[c]=w.text
            if c==5 or w.text.startswith('<'): continue
            vals[fleets[c]]=scaled(w.text)
        if vals: catch_maps[kind][str(n)]=vals
        provenance['catch'].append({'kind':kind,'n':n,'name':name,'page':page,'printed_page':page+130,'raw':{(fleets[c] if c<5 else 'Published total'):v for c,v in raw_vals.items()},'values':vals,'words':[serial(w) for w in row]})
model={
    'metadata':{'LME':'HS_077 Pacific Eastern Central high seas','model_number':'HS_077_1','model_name':'Eastern tropical Pacific','model_year':'1993-1997'},
    'groups':groups,'consumers':list(range(1,37)),'fleets':fleets,
    'landings':catch_maps['landings'],'discards':catch_maps['discards'],
    'detritus_groups':['Detritus'],'detritus_fate':{},'diet':diet,
    'diet_rows':39,'landings_rows':34,'discards_rows':34,
    'source_context':{'published_version':'ETP7','publication_year':2003,'model_area_km2':'32800000','biomass_and_fisheries_original_units':'tons per million km2; yearly rates','density_conversion':'divide by 1000000','basic_table_living_groups':38,'diet_detritus_row':39,'diet_external_prey_row':40,'metadata_unit_id':'HS_077','habitat_basis_note':'Published B is density across model area; habitat fractions not reported as input parameters. Bluefin 7% is explicitly applied within diet adjustment (Table4a footnote10).'}
}
(WORK/'model_source.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(WORK/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(WORK/'diet_sums.json').write_text(json.dumps({n:str(sum(map(Decimal,values.values()))) for n,values in diet.items()},indent=2)+'\n',encoding='utf-8')
# Independent bilingual duplication check using the same printed-ID geometry.
spanish={}
for page,lo,hi in [(30,1,18),(31,19,36)]:
    ws=boxes(page)
    prey={int(w.text):w.xc for w in ws if w.text.isdigit() and 1<=int(w.text)<=40 and w.y0>620}
    pred={int(w.text):w.yc for w in ws if w.text.isdigit() and lo<=int(w.text)<=hi and 98<w.x0<105 and w.y0<510}
    assert len(prey)==40 and len(pred)==18
    for w in ws:
        if not re.fullmatch(r'\d\.\d{3}',w.text) or not (110<w.x0<440 and 70<w.y0<510): continue
        i=min(prey,key=lambda i:abs(prey[i]-w.xc))
        j=min(pred,key=lambda j:abs(pred[j]-w.yc))
        assert abs(prey[i]-w.xc)<.1 and abs(pred[j]-w.yc)<6
        spanish[(i,j)]=w.text
english={(v['prey'],v['consumer']):v['value'] for v in provenance['diet']}
assert english==spanish,[(k,english.get(k),spanish.get(k)) for k in set(english)|set(spanish) if english.get(k)!=spanish.get(k)]
(WORK/'bilingual_diet_comparison.txt').write_text('315 populated cells and all blank cells match between English Table3a (PDF28-29) and Spanish Table3b (PDF30-31). All nine non-unit diet sums are reproduced in both versions.\n',encoding='utf-8')
boxes(27)
print(json.dumps({'groups':len(groups),'consumers':len(diet),'diet_values':len(provenance['diet']),'diet_sums':{n:str(sum(map(Decimal,v.values()))) for n,v in diet.items()}},indent=2))
