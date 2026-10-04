"""Build source-faithful Base/M30/P30 extraction, never normalize diets."""
from pathlib import Path
import json,re,html,copy,csv,hashlib,sys,subprocess,os
from decimal import Decimal as D
import openpyxl
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[4]
SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
MODELS=ROOT/'regions/LME_027/models'; SOURCE=ROOT/'regions/LME_027/papers/CAN-2014'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(v):return None if v is None or str(v).strip()=='' else html.unescape(re.sub('<[^>]*>','',str(v))).strip()
def nd(v):return '-9999' if v is None or str(v).strip()=='' else str(v)
book=load(HERE/'Table_1-f0424c0e.xls.cells.json');cells=book['sheets'][0]['cells']
rows={}
for c in cells: rows.setdefault(c['row'],{})[c['column']]=c
tables=load(HERE/'original_docx_tables.json')['tables']
fields={3:'tl',4:'biomass',5:'z',6:'pb',7:'qb',8:'ee',9:'pq',10:'ba_rate'}
fleetcols={11:'Artisanal',12:'Industrial demersal',13:'Industrial pelagic'}
groups=[];land={};parameters=[];cross=[];reported_totals={}
for r,c in rows.items():
    v=clean(c.get(1,{}).get('value'))
    if not v or not v.isdigit():continue
    n=int(v);g={'n':n,'name':clean(c[2]['value'])}
    for col,field in fields.items():
        raw=c.get(col,{}).get('value');g[field]=clean(raw)
        parameters.append({'group':n,'field':field,'source_literal':clean(raw),'source_raw':raw,'adopted_literal':clean(raw),'source':'Table_1-f0424c0e.xls','source_sha256':book['source_sha256'],'sheet':'Table_1','cell':chr(64+col)+str(r),'pdf_page':4 if n<=36 else 5,'category':'model_estimated' if '<b>' in str(raw) else ('source_blank' if g[field] is None else 'tabulated')})
    for k in ['hab_area','unassim','detritus_import','ba','other_mort']:g[k]=None
    land[str(n)]={fleet:clean(c.get(col,{}).get('value')) for col,fleet in fleetcols.items()}
    reported_totals[str(n)]=clean(c.get(14,{}).get('value'))
    for col,fleet in fleetcols.items():parameters.append({'group':n,'field':'landings','fleet':fleet,'source_literal':land[str(n)][fleet],'adopted_literal':land[str(n)][fleet],'source':'Table_1-f0424c0e.xls','source_sha256':book['source_sha256'],'sheet':'Table_1','cell':chr(64+col)+str(r),'category':'tabulated'})
    groups.append(g);cross.append({'group_id':n,'canonical_name':g['name'],'Table_1_row':r})
assert [g['n'] for g in groups]==list(range(1,52))
diet={str(n):{} for n in range(1,48)};dietledger=[]
for ti in [1,2,3]:
    t=tables[ti];offset=2 if ti==1 else 1;heads=t[0][offset:]
    for ri,r in enumerate(t[1:],2):
        prey='import' if r[0]=='52' else r[0]
        assert len(r)==len(t[0])
        for ci,(consumer,raw) in enumerate(zip(heads,r[offset:]),offset+1):
            val=format(D(raw)/100,'f') if raw.strip() else None;diet[consumer][prey]=val
            dietledger.append({'consumer_id':int(consumer),'prey_id':prey,'source_literal_percent':raw,'adopted_literal':val,'source':'pone.0094742.s001-eb18ca66.docx','source_sha256':sha(SOURCE/'pone.0094742.s001-eb18ca66.docx'),'table':'S2','physical_table':ti+1,'row':ri,'column':ci,'retained_render_page':ti+7,'arithmetic':None if val is None else raw+'/100','status':'source_blank' if val is None else ('printed_zero' if D(val)==0 else 'printed_nonzero'),'researcher_correction':None})
s8={int(r[0]):r for r in tables[9] if r and r[0].strip().isdigit()}
assert list(s8)==list(range(1,52))
for c in cross:c['S8_name']=s8[c['group_id']][1].strip()
save(HERE/'group_crosswalk.json',cross)
conflicts=[]
for g in groups:
    r=s8[g['n']]
    for f,i in [('biomass',7),('ee',8)]:
        if g[f] is not None and D(g[f])!=D(r[i]):conflicts.append({'group_id':g['n'],'name':g['name'],'field':f,'Table_1':g[f],'S8_Base':r[i],'adopted':g[f],'decision':'Table 1 is dedicated Base input/output table; preserve disagreement; S8 used for explicitly labelled variants'})
save(HERE/'Table1_S8_conflicts.json',conflicts)
stanzas=[{'stock':s,'adult_group':a,'juvenile_group':j,'juvenile_age_years':'0-1','transition_age_months':12,'leading_stanza':'adult','vbk':None,'evidence':'article p2; supplement Text S1 The model','equation_caveat':'Native linked stanzas calculate production/consumption/growth; no reported VBK. P/B=Z only under equilibrium, not universally established.'} for s,a,j in [('Meagre',3,4),('Croakers',14,15),('Seabreams',16,17),('Catfish',18,19),('Groupers',23,24),('Sparids',25,26)]]
save(HERE/'stanza_evidence.json',stanzas)
base={'metadata':{'LME':'27 Canary Current','model_number':'Guenette2014_Base','model_name':'Banc d Arguin and Mauritanian Shelf Base','model_year':1991,'variant':'Base','model_area_km2':'33224','source_doi':'10.1371/journal.pone.0094742'},'groups':groups,'consumers':list(range(1,48)),'fleets':list(fleetcols.values()),'landings':land,'discards':{},'detritus_groups':['Detritus'],'detritus_fate':{},'diet':diet,'diet_rows':51,'landings_rows':51,'discards_rows':51,'stanzas':stanzas}
summary=[]
for variant,bi,ei,pi in [('Base',7,8,3),('M30',5,6,2),('P30',9,10,4)]:
    model=copy.deepcopy(base);model['metadata'].update(variant=variant,model_number='Guenette2014_'+variant,model_name='Banc d Arguin and Mauritanian Shelf '+variant)
    directory=MODELS/f'Guenette2014_BancArguin_{variant}_1991';directory.mkdir(exist_ok=True);out=directory/'extracted_tables';out.mkdir(exist_ok=True)
    led=copy.deepcopy(dietledger);pl=copy.deepcopy(parameters);uncertain=[];constraints=[]
    for g in model['groups']:
        n=g['n'];r=s8[n]
        if n<=47:constraints.append({'group_id':n,'Base_pBA':r[3].strip(),'variant_pBA':r[pi].strip(),'source':'S8','meaning':'aggregate proportion of Banc benthic/pelagic invertebrates; insufficient to reconstruct each prey cell'})
        if variant!='Base':
            for field,i in [('biomass',bi),('ee',ei)]:
                g[field]=r[i].strip()
                pl.append({'group':n,'field':field,'adopted_literal':g[field],'source_literal':g[field],'source':'pone.0094742.s001-eb18ca66.docx','table':'S8','physical_table':10,'row':3+n,'column':i+1,'category':'variant_tabulated','variant':variant})
            g['tl']=None
            if n<=47 and r[pi].strip() and D(r[pi])!=D(r[3]):
                uncertain.append(n)
                for ba,sh in [(32,38),(33,39),(34,40),(35,41),(36,42),(37,43),(46,44),(47,45)]:
                    if D(diet[str(n)].get(str(ba)) or '0') or D(diet[str(n)].get(str(sh)) or '0'):
                        model['diet'][str(n)][str(ba)]=None;model['diet'][str(n)][str(sh)]=None
            for entry in led:
                if entry['consumer_id']==n:
                    k=entry['prey_id'];entry['adopted_literal']=model['diet'][str(n)][k]
                    if entry['adopted_literal'] is None and entry['source_literal_percent'].strip():entry['status']='variant_unpublished';entry['decision']='S8 aggregate constraint does not provide a unique prey redistribution'
                    else:entry['status']='inherited_Base_'+entry['status']
        g['source_status']='Table1_Base' if variant=='Base' else 'S8_B_EE_with_Base_other_parameters_inherited'
    model['extraction_notes']={'incomplete_diet_consumers':uncertain,'pBA_constraints':constraints,'variant_inheritance':None if variant=='Base' else 'Only B/EE and pBA are supplied by S8. Other scalar parameters, catches and unchanged diet components are inherited Base inputs; not independently published variant values. TL unknown. Changing prey pairs unknown.','source_blank_diet_cells':[{'consumer':x['consumer_id'],'prey':x['prey_id']} for x in dietledger if x['status']=='source_blank'],'accepted_corrections':[]}
    save(out/'extraction.json',model);save(out/'DIET_CELL_LEDGER.json',led);save(out/'PARAMETER_CELL_LEDGER.json',pl);save(out/'SOURCE_CONFLICTS.json',conflicts);save(out/'STANZAS.json',stanzas);save(out/'GROUP_CROSSWALK.json',cross)
    env=dict(os.environ,PYTHONIOENCODING='utf-8')
    r=subprocess.run([sys.executable,str(SKILL/'write_outputs.py'),str(out/'extraction.json'),'--outdir',str(directory),'--dir-name','extracted_tables'],text=True,encoding='utf-8',capture_output=True,env=env)
    (out/'WRITER_LOG.txt').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
    # The stock writer labels partial known-cell sums as complete totals. Correct only derived summary rows.
    dp=out/'Diet_composition.csv';dr=list(csv.reader(dp.open(encoding='utf-8',newline='')))
    sr=next(r for r in dr if r[1]=='Sum'); rr=next(r for r in dr if r[1]=='(1 - Sum)')
    for n in uncertain:sr[dr[0].index(str(n))]='';rr[dr[0].index(str(n))]=''
    with dp.open('w',encoding='utf-8',newline='') as f:csv.writer(f,lineterminator='\r\n').writerows(dr)
    sums=[]
    for n in range(1,48):
        vals=model['diet'][str(n)];ss=sum((D(v) for v in vals.values() if v is not None),D(0));unknown=[k for k,v in vals.items() if v is None]
        sums.append({'consumer_id':n,'consumer_name':groups[n-1]['name'],'sum_of_published_or_inherited_cells':str(ss),'diet_plus_import_complete_sum':None if n in uncertain else str(ss),'source_blanks':[x['prey_id'] for x in dietledger if x['consumer_id']==n and x['status']=='source_blank'],'variant_unknown_cells':[x['prey_id'] for x in led if x['consumer_id']==n and x['status']=='variant_unpublished'],'all_missing_cells':unknown,'normalization_applied':False,'researcher_review':'unverified_source_conflicts'})
    save(out/'DIET_SOURCE_SUMS.json',{'source_table_sha256':sha(dp),'consumers':sums})
    counts={'variant':variant,'directory':str(directory.relative_to(ROOT)).replace('\\','/'),'groups':51,'consumers':47,'fleets':3,'incomplete_consumers':uncertain,'unknown_variant_diet_cells':sum(x['status']=='variant_unpublished' for x in led),'original_blank_diet_cells':4,'source_bird_sum':'0.980331','source_adult_grouper_crustacean':'1.34','source_adult_grouper_sum':'2.2006','status':'partial_source_extraction'}
    summary.append(counts)
    save(out/'EXTRACTION_STATUS.json',counts)
    save(HERE/f'{variant}_vectors.json',{'groups':model['groups'],'landings':model['landings'],'reported_total_catches':reported_totals,'incomplete_diet_consumers':uncertain})
save(HERE/'extraction_summary.json',summary)
print(json.dumps(summary,indent=2))
