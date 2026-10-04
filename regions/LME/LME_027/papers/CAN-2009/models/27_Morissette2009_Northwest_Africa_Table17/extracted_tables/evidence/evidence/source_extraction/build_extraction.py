"""Reproduce paper extraction using text coordinates; never import an EcoBase cell."""
from pathlib import Path
from decimal import Decimal
import csv, hashlib, json, re, sys
import fitz

OUT = Path(__file__).resolve().parent
CAND = OUT.parents[1]
ROOT = OUT.parents[5]
PDF = ROOT / 'regions/LME_027/papers/FCRR_2009_17-2.pdf.pdf'
SKILL = ROOT / 'tools/skills/original_skill_resources/claude/ecopath-extraction'
sys.path.insert(0, str(SKILL / 'scripts'))
import pdfgrid

def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

doc = fitz.open(PDF)
pdfhash = hashlib.sha256(PDF.read_bytes()).hexdigest()
ledger = []
groups = []
page = doc[40]
words = page.get_text('words')
rowstarts = sorted([w for w in words if re.fullmatch(r'\d+\.', w[4]) and 70 < w[0] < 100 and w[1] > 145], key=lambda w:w[1])
assert len(rowstarts)==27, rowstarts
fields = ['tl','biomass','pb','qb','ee','pq']
for start in rowstarts:
    row = sorted([w for w in words if abs(w[1]-start[1])<2], key=lambda w:w[0])
    n = int(start[4][:-1])
    name = ' '.join(w[4] for w in row[1:-6])
    g = {'n':n, 'name':name}
    for field,w in zip(fields,row[-6:]):
        g[field] = None if w[4]=='-' else w[4]
        ledger.append({'table':17,'pdf_page':41,'printed_page':37,'group_id':n,'group_name':name,'field':field,'source_literal':w[4],'adopted_literal':g[field], 'bbox':list(w[:4]),'status':'not_applicable' if w[4]=='-' else 'printed_value'})
    for field in ['hab_area','z','other_mort','unassim','detritus_import','ba','ba_rate']:
        g[field] = None
    groups.append(g)
assert groups[13]['name']=='Bathydeersal predators'

diet={str(i):{} for i in range(1,24)}
diet['25']={'import':None}
dietledger=[]
for pdfpage, ids in [(42,range(1,12)),(43,range(12,24))]:
    p=doc[pdfpage-1]
    words=p.get_text('words')
    save(f'pdf_{pdfpage:03d}_fitz_words.json',[{'text':w[4], 'bbox':list(w[:4])} for w in words])
    raw=pdfgrid.get_words(str(PDF),pdfpage,merge_gap=0.4)
    (OUT/f'pdfgrid_{pdfpage}_raw.txt').write_text('\n'.join(f'{i}: '+line.text+' | '+str([(c.text,c.x0,c.y0,c.x1,c.y1) for c in line.cells]) for i,line in enumerate(raw)), encoding='utf-8')
    heads=[w for w in words if w[4].isdigit() and int(w[4]) in ids and 75 < w[1]<105]
    assert len(heads)==len(ids), heads
    anchors={int(w[4]):(w[0]+w[2])/2 for w in heads}
    labels=sorted([w for w in words if re.fullmatch(r'\d+\.',w[4]) and w[0]<160 and w[1]>100],key=lambda w:w[1])
    assert len(labels)==27
    imports=next(w for w in words if w[4]=='Import')
    total=next(w for w in words if w[4]=='Total')
    for idx,label in enumerate(labels+[imports]):
        prey=str(int(label[4][:-1])) if label[4]!='Import' else 'import'
        nexty=(labels[idx+1][1] if idx<26 else imports[1]) if idx<27 else total[1]
        vals=[w for w in words if w[0]>min(anchors.values())-15 and label[1]-1<=w[1]<nexty-1 and re.fullmatch(r'\d+\.\d+',w[4])]
        seen={}
        for w in vals:
            pred=min(anchors,key=lambda j:abs((w[0]+w[2])/2-anchors[j]))
            assert abs((w[0]+w[2])/2-anchors[pred])<10
            assert pred not in seen
            seen[pred]=w
        for pred in ids:
            w=seen.get(pred)
            literal=w[4] if w else None
            if w: diet[str(pred)][prey]=literal
            elif prey=='import': diet[str(pred)][prey]='0'
            dietledger.append({'table':18,'pdf_page':pdfpage,'printed_page':pdfpage-4,'predator_id':pred,'prey_id':prey,'source_literal':literal,'adopted_literal':literal if w else ('0' if prey=='import' else None),'status':'printed_zero' if literal=='0.000' else 'printed_value' if w else 'blank_structural_zero_in_printed_matrix','bbox':list(w[:4]) if w else None,'row_bbox':list(label[:4]),'predator_anchor_x':anchors[pred]})
for prey in list(map(str,range(1,28)))+['import']:
    dietledger.append({'table':18,'pdf_pages':[42,43],'predator_id':25,'prey_id':prey,'source_literal':None,'adopted_literal':None,'status':'unknown_entire_predator_column_absent'})

fleets=['Local fleets','Foreign fleets','Unallocated total catch']
catch_data={12:('0.0078','0.0075',None,31),15:('0.0011','0.0004',None,33),16:('0.0010','0.0008',None,33),17:('0.0013','0.0017',None,34),19:('0.1931','0.1423',None,35),20:('0.0487','0.0924',None,36),21:(None,None,'0.0545',37),22:('0.0062','0.0014',None,37)}
landings={}
catchledger=[]
for n,(*vals,pdfpage) in catch_data.items():
    landings[str(n)]={f:v for f,v in zip(fleets,vals) if v is not None}
    catchledger.append({'group_id':n,'group_name':groups[n-1]['name'],'source':'group prose','pdf_page':pdfpage,'printed_page':pdfpage-4,'period':'1990s mean; exact baseline equivalence not established','units':'t/km^2/year','values':landings[str(n)],'published_total':'0.1410' if n==20 else str(sum(Decimal(v) for v in vals if v)),'computed_fleet_total':str(sum(Decimal(v) for v in vals if v)),'remark':'Fleet values retained despite 0.0001 disagreement with prose total' if n==20 else 'Total catch placed in Landings as import carrier; discard separation unstated'})

model={'metadata':{'LME':'27 Canary Current','model_number':'Morissette2009_Table17','model_name':'Northwest Africa','model_year':'late 1980s'},'groups':groups,'consumers':list(range(1,24))+[25],'fleets':fleets,'landings':landings,'discards':{},'detritus_groups':['Detritus'],'detritus_fate':{},'diet':diet,'diet_rows':27,'landings_rows':27,'discards_rows':27,'source_evidence':{'source_pdf':'../../papers/FCRR_2009_17-2.pdf.pdf','source_sha256':pdfhash,'table17_pdf_page':41,'table18_pdf_pages':[42,43],'catch_basis':'partial prose means for 1990s; not proven final baseline','missing_consumer_diet':[25],'unknown_fields':['BA','assimilation/GS','habitat_fraction','detritus routing','detritus import','migration','unreported group catch'],'status':'source-faithful partial; not admissible as complete executable model'}}
model['source_evidence']['source_pdf']='../../../../papers/FCRR_2009_17-2.pdf.pdf'
save('extraction.json',model)
save('table17_cells.json',ledger)
save('diet_cells.json',dietledger)
save('catch_prose.json',catchledger)
save('diet_sums.json',[{'predator_id':int(k),'prey_sum':str(sum(Decimal(v) for p,v in col.items() if p!='import' and v is not None)),'import':col.get('import'),'total':str(sum(Decimal(v) for v in col.values() if v is not None)) if k!='25' else None,'complete_source_column':k!='25','printed_total':'1.000' if k!='25' else None} for k,col in diet.items()])
save('source_identity.json',{'pdf_path':'../../../../papers/FCRR_2009_17-2.pdf.pdf','sha256':pdfhash,'pages':len(doc),'publication_year':2009,'model_period':'late 1980s','catch_period':'1990s means / time series 1987-2004','study_area_km2':3561029,'extraction_method':'coordinate word extraction (PyMuPDF) with 200 dpi rendered visual check of Tables17-18'})

# Export the catch time series as evidence only. Header numbers are old IDs;
# names crosswalk to Table17 IDs 12-23. No year or average is adopted here.
catchseries=[]
for pdfpage,fleet in [(15,'Local fleets'),(16,'Foreign fleets')]:
    p=doc[pdfpage-1]
    words=p.get_text('words')
    starts=sorted([w for w in words if re.fullmatch(r'(198[7-9]|199\d|200[0-4])',w[4]) and w[0]<100],key=lambda w:w[1])
    assert len(starts)==18
    for ri,s in enumerate(starts):
        nexty=starts[ri+1][1] if ri+1<len(starts) else s[1]+18
        rawrow=[w for w in words if w[0]>s[2]+1 and s[1]-2<=w[1]<nexty-2]
        vals=sorted([w for w in rawrow if re.fullmatch(r'\d+\.\d+',w[4])],key=lambda w:w[0])
        assert len(vals)==13,(pdfpage,s,vals)
        for ci,w in enumerate(vals):
            literal=w[4]
            tails=[t for t in rawrow if t[4].isdigit() and w[0] <= (t[0]+t[2])/2 <= w[2] and t[1]>w[1]+2]
            if tails: literal+=''.join(t[4] for t in sorted(tails,key=lambda t:t[1]))
            catchseries.append({'table':pdfpage-14,'pdf_page':pdfpage,'printed_page':pdfpage-4,'year':int(s[4]),'fleet':fleet,'group_id':ci+12 if ci<12 else 'Total','source_literal':literal,'units':'1000 tonnes/year','bbox':list(w[:4]),'adopted_as_model_input':False})
save('catch_time_series.json',catchseries)
print(json.dumps({'groups':len(groups),'diet_cells':len(dietledger),'catch_series_cells':len(catchseries),'diet_sums':[(k,str(sum(Decimal(v) for v in c.values() if v))) for k,c in diet.items()]},indent=2))
