"""Independent read-only validation; ignores table row order, compares cell content."""
from pathlib import Path
from collections import Counter
import json, zipfile, hashlib, math, sys
from lxml import etree as E
from apply_selections import CHOICES, ROOT, OUT
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,overview,validate_region,sha,rows
from regional import result_hash
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
backup=OUT/'Project_before_e078f2578c41.xlsx'

def tables(path,sheet):
    out={};table=None;header=None
    with zipfile.ZipFile(path) as z, z.open(f'xl/worksheets/sheet{sheet}.xml') as f:
        for _,r in E.iterparse(f,events=('end',),tag=NS+'row'):
            vals={}
            for c in r:
                ref=c.get('r');col=0
                for s in ref:
                    if not s.isalpha():break
                    col=col*26+ord(s)-64
                typ=c.get('t');v=c.find(NS+'v')
                if typ=='inlineStr':value=''.join(c.itertext())
                elif v is None:value=None
                elif typ=='b':value=v.text=='1'
                elif typ in ('str','e'):value=v.text
                else:
                    value=float(v.text)
                    if value.is_integer():value=int(value)
                vals[col-1]=value
            if vals:
                row=[vals.get(i) for i in range(max(vals)+1)]
                if row[0]=='@table':table=row[1];header=None;out[table]=[]
                elif table and header is None:header=row
                elif table:out[table].append({h:vals.get(i) for i,h in enumerate(header)})
            r.clear()
            while r.getprevious() is not None:del r.getparent()[0]
    return out

def canonical(row):
    d={str(k):format(float(v),'.15g') if isinstance(v,(int,float)) and not isinstance(v,bool) else v for k,v in row.items()}
    return json.dumps(d,sort_keys=True,ensure_ascii=False,separators=(',',':'))

results=[];meta={}
for sn in range(1,9):
    a=tables(backup,sn);b=tables(ROOT/'Project.xlsx',sn)
    for table,old in a.items():
        if old and 'unit_id' in old[0]:
            x=Counter(canonical(r) for r in old if r['unit_id'] not in CHOICES)
            y=Counter(canonical(r) for r in b[table] if r['unit_id'] not in CHOICES)
            assert x==y,(sn,table,'Unrelated values differ',list((x-y).elements())[:1],list((y-x).elements())[:1])
            results.append({'sheet':sn,'table':table,'unrelated_rows_preserved':sum(x.values())})
    if sn<=3:meta[sn]=b
    print(f'Verified sheet {sn}',flush=True)
top=sorted([r for r in meta[1]['Regions'] if isinstance(r.get('atlas_region_rank'),(int,float)) and r['atlas_region_rank']<=25],key=lambda r:r['atlas_region_rank'])
assert len(top)==25
assert {r['unit_id'] for r in top if not r.get('selected_model_id')}=={'LME_048','EEZ_938'}
models=meta[3]['Models'];decisions=[]
for r in top:
    selected=[m for m in models if m['unit_id']==r['unit_id'] and m.get('selected')]
    assert len(selected)==int(bool(r.get('selected_model_id'))),r['unit_id']
    if selected:
        assert selected[0]['model_id']==r['selected_model_id']
        assert (ROOT/selected[0]['model_path']).is_file()
for uid,(mid,ge,te,eg,reason,evidence) in CHOICES.items():
    path=ROOT/'regions'/uid/(uid+'.xlsx');book=read_book(path);o=validate_region(book,path)
    assert o['selected_model_id']==mid and o['calculation_result_sha256']==result_hash(book)
    assert not rows(book,'PPR','Annual') and not rows(book,'Selected model groups','Group SPPR')
    region=next(r for r in top if r['unit_id']==uid)
    assert region['sha256']==sha(path)
    model=next(m for m in models if m['unit_id']==uid and m['model_id']==mid)
    old=next(r for r in tables(backup,1)['Regions'] if r['unit_id']==uid)
    archives=list((path.parent/'models'/'previous_results').glob(f'{uid}_{old["sha256"][:12]}.xlsx'))
    assert len(archives)==1 and sha(archives[0])==old['sha256']
    source=ROOT/model['model_path'];beforebook=read_book(archives[0])
    for sheet in ['Catch','Classic PPR','NPP']:
        for table,(h,data) in beforebook[sheet].items():
            hh,dd=book[sheet][table];assert h==hh
            assert Counter(canonical(dict(zip(h,row))) for row in data)==Counter(canonical(dict(zip(hh,row))) for row in dd),(uid,sheet,table)
    decisions.append({'unit_id':uid,'model_id':mid,'previous_model_id':old.get('selected_model_id'),'model_path':model['model_path'],'source_sha256':sha(source),'GE':ge,'TE':te,'With Egestion':eg,'rationale':reason,'evidence':evidence,'status':region['status']})
    print(f'Verified regional archive and selection {uid}',flush=True)
result={'status':'PASS','top25_count':25,'selected_count':23,'unselected':['LME_048','EEZ_938'],'central_sha256':sha(ROOT/'Project.xlsx'),'decisions':decisions,'top25':top,'unrelated_records_preserved':True,'preservation_checks':results,'source_models_unchanged':'Verified during each regional selection write; no later model writes','old_model_results_archived_and_cleared':True,'new_scientific_calculations':False,'verification_note':'Initial positional comparison detected updater row sorting. Read-only verification compares records independent of row order; numbers canonicalized to 15 significant digits.'}
(OUT/'SELECTION_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: 23 of 25 selected; only LME_048 and EEZ_938 unselected.',flush=True)
