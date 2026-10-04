"""Source-faithful final 46-group model extraction from main Table1 and DOCX S3/S4."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from decimal import Decimal as D
import csv,json,re,sys,subprocess,shutil,hashlib
import openpyxl

BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
MID='941_201901_Warm_Pool_(2005)'; MODEL=ROOT/'regions/EEZ_941/models'/MID
REVIEW=MODEL/'source_review';OUT=MODEL/'extracted_tables';OUT.mkdir(exist_ok=True)
SKILL=Path.home()/'.agents/skills/ecopath-extraction/scripts'
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def run(script,args,log):
    r=subprocess.run([sys.executable,str(SKILL/script),*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    log.write_text(r.stdout+'\n'+r.stderr,encoding='utf-8');print(script,r.returncode);return r
def savecsv(p,headers,rows):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)
raw=json.loads((REVIEW/'SUPPLEMENT_XML_EVIDENCE.json').read_text(encoding='utf-8'))
groups=json.loads((REVIEW/'SOURCE_ONLY_PARTIAL.json').read_text(encoding='utf-8'))['groups']
model={'metadata':{'LME':'941 EEZ Kiribati Gilbert Islands proxy','model_number':201901,'model_name':'Warm Pool','model_year':2005},
       'groups':groups,'consumers':list(range(1,43)),'fleets':['LL','PSA','PSU','PL'],
       'diet':{str(i):{} for i in range(1,43)},'landings':{},'discards':{},
       'detritus_groups':['Detritus','Fishery discards'],'detritus_fate':{},'diet_rows':46}
evidence=[]
for ti,start in [(3,2),(4,1)]:
    table=raw['tables'][ti]
    headers=[int(c['text']) for c in table[0][start:]]
    assert headers==list(range(1,20)) if ti==3 else headers==list(range(20,43))
    for ri,row in enumerate(table[1:47],2):
        prey=int(row[0]['text']);assert prey==ri-1
        for pred,c in zip(headers,row[start:]):
            s=c['text'].strip();assert not s or re.fullmatch(r'\d+\.\d+',s),s
            evidence.append({'table':'S3','xml_table':ti+1,'xml_row':ri,'grid_column':c['grid_start']+1,
                             'supplement_page':29 if ti==3 else 30,'prey':prey,'predator':pred,'printed_value':s})
            if s:model['diet'][str(pred)][str(prey)]=s
sums={pred:str(sum(map(D,col.values()),D(0))) for pred,col in model['diet'].items()}
assert len(evidence)==46*42
catch_totals=[];catch_evidence=[]
for ri,row in enumerate(raw['tables'][5][2:48],3):
    n=int(row[0]['text']);assert n==ri-2
    for key,cols,totalcol in [('landings',[2,3,4,5],6),('discards',[8,9,10,11],12)]:
        values={}
        for fleet,col in zip(model['fleets'],cols):
            s=row[col]['text'].strip()
            catch_evidence.append({'table':'S4','xml_table':6,'xml_row':ri,'grid_column':col+1,'supplement_page':31,'group':n,'kind':key,'fleet':fleet,'printed_value':s,'scale':'0.000001'})
            if s:values[fleet]=format(D(s)*D('0.000001'),'f')
        if values:model[key][str(n)]=values
        stated=row[totalcol]['text'].strip()
        if values or stated:
            calc=sum((D(v) for v in values.values()),D(0)); printed=D(stated)*D('0.000001') if stated else None
            catch_totals.append({'group':n,'name':groups[n-1]['name'],'kind':key,'fleet_sum':str(calc),'printed_total':str(printed) if printed is not None else None,'difference_fleet_minus_printed':str(calc-printed) if printed is not None else None})
for g in groups:g['ba']='0';g['net_migration']='0'

# Preserve paragraph boundaries within source membership cells, including source misspellings.
w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
src=ROOT/'regions/EEZ_941/papers/Griffiths-2019/fog12389-sup-0001-appendixs1-s4.docx'
with ZipFile(src) as z: doc=ET.fromstring(z.read('word/document.xml'))
t1=doc.find(w+'body').findall(w+'tbl')[0]
tax_evidence=[]
for g in groups:
    ri=1+(g['n']-1)*7;r=t1.findall(w+'tr')[ri];cells=r.findall(w+'tc')
    paragraphs=[''.join(e.text or '' for e in p.iter(w+'t')).strip() for p in cells[0].findall(w+'p')]
    label='; '.join(p for p in paragraphs if p)
    assert label
    if '(' in label:
        desc=label+' [Membership as printed in Appendix S1 Table S1; spelling retained, not taxonomically standardized.]'
    elif g['n']==45:desc='Non-living detrital pool. Appendix S1 Table S1; biomass source concerns abyssal open-ocean detritus.'
    elif g['n']==46:desc='Non-living fishery-discard pool, a suspended trophic pathway available to predators (main paper p99; Appendix S1 Table S1).'
    else:desc=label+'; detailed taxonomic membership not documented in Table S1. Diet-study analogues are not treated as an exhaustive membership list.'
    ages=raw['tables'][0][ri][2]['text']
    if ages and ages!='All':desc+=' Source age class: '+ages+'.'
    g['taxon_descr']=desc
    tax_evidence.append({'seq':g['n'],'group_name':g['name'],'source_membership_cell':label,'xml_table':1,'xml_row':ri+1,'age_class':ages,'taxon_descr':desc})
model['source_identity']={'model_id':MID,'doi':'10.1111/fog.12389','baseline':2005,
    'main_table':'Table1 pp98–99','diet_table':'FINAL TableS3 pp29–30','catch_table':'TableS4 p31',
    'supplement_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
    'unknowns':['GS/unassimilated fractions','numerical detritus-fate matrix','numeric fleet-discard destinations and survival/return fraction','detritus import','habitat-area fractions'],
    'source_catch_conflict':'Exact fleet components retained. Printed Total column differs for multiple rows; both retained in SOURCE_CATCH_TOTAL_AUDIT.json.',
    'net_migration_evidence':'AppendixS1 p4: net migration equals zero; does not establish separate gross immigration/emigration.',
    'ba_evidence':'AppendixS1 p4: biomass accumulation assumed zero in current model.'}
dump(REVIEW/'FINAL_EXTRACTION.json',model);dump(REVIEW/'FINAL_DIET_CELL_EVIDENCE.json',evidence)
dump(REVIEW/'CATCH_CELL_EVIDENCE.json',catch_evidence);dump(REVIEW/'SOURCE_CATCH_TOTAL_AUDIT.json',catch_totals)
dump(REVIEW/'TAXONOMY_EVIDENCE.json',tax_evidence);dump(REVIEW/'FINAL_DIET_SUMS.json',sums)
run('write_outputs.py',[REVIEW/'FINAL_EXTRACTION.json','--outdir',MODEL,'--dir-name','extracted_tables'],MODEL/'write_outputs.log')
wb=openpyxl.Workbook();ws=wb.active;ws.title='Taxonomy';ws.append(['seq','group_name','taxon_descr'])
for g in groups:ws.append([g['n'],g['name'],g['taxon_descr']])
wb.save(OUT/'Taxonomy.xlsx')
savecsv(OUT/'taxonomy.csv',['seq','group_name','taxon_descr'],list(ws.values)[1:])
run('validate.py',[OUT],OUT/'VALIDATION.txt')
run('massbalance_check.py',[OUT],OUT/'MASS_BALANCE_SOURCE.txt')
run('database_json.py',['-d',OUT,'--update-report'],OUT/'DATABASE_CONVERSION.txt')
dbs=list(OUT.glob('941_*.json'));assert len(dbs)==1
converted=json.loads(dbs[0].read_text());canonical=json.loads(json.dumps(converted));changes=[]
assert len(canonical['group'])==46
for g,s in zip(canonical['group'],groups):
    assert g['group_name']==s['name']
    for srcfield,dst in [('biomass','biomass'),('biomass','biomass_habitat_area'),('pb','pb'),('qb','qb'),('ee','ee'),('pq','ge'),('ba','biomass_accum')]:g[dst]=s.get(srcfield) if s.get(srcfield) is not None else '-9999'
    for field in ['habitat_area','vbk','shadow_price','gs','detritus_import','immigration','emigration','emigration_rate','biomass_accum_rate','other_mort','diet_imp']:g[field]='-9999'
    g['tl']=s['tl'];g['net_migration']='0';g['taxon_descr']=s['taxon_descr']
    g['pp']='0' if s['n']<=42 else '1' if s['n']<=44 else '2'
    for a,b in [('biomass','b_hab_area_input'),('pb','pb_input'),('qb','qb_input'),('ee','ee_input')]:g[b]='false' if a in s['estimated_by_ecopath'] or s.get(a) is None else 'true'
    g['ge_input']='false'
    g['diet_descr']={'diet':[{'prey_seq':k,'proportion':v,'detritus_fate':'-9999'} for k,v in model['diet'].get(str(s['n']),{}).items()]} if s['n']<=42 else None
    catches=[D(v) for kind in ['landings','discards'] for v in model[kind].get(str(s['n']),{}).values()]
    g['export']=format(sum(catches,D(0)),'f') if catches else '-9999'
canonical['_source_provenance']=model['source_identity']
canonical['_source_provenance']['canonical_status']='source-faithful extraction with unknown routing/GS/imports; not a runnable validated model'
canonical['_source_provenance']['catch_schema_note']='export records retained plus discarded mortality removal. Fate of fishery discards is not represented by this export field or natural M0+egestion routing.'
for a,b in zip(converted['group'],canonical['group']):
    for k,v in b.items():
        if a.get(k)!=v:changes.append({'seq':b['group_seq'],'field':k,'converter':a.get(k),'canonical':v})
dump(MODEL/'model.json',canonical);shutil.copy2(MODEL/'model.json',MODEL/(MID+'.json'))
dump(OUT/'converter_to_canonical_audit.json',changes)
run('database_json.py',['-j',MODEL/(MID+'.json')],OUT/'CANONICAL_RECONSTRUCTION.txt')
recon=MODEL/(MID+'_reconstructed.xlsx')
if recon.exists():shutil.move(str(recon),OUT/'CANONICAL_reconstructed.xlsx')

# Production equation needs no GS or detritus routing. Do not use its residual to repair values.
audit=[]
for g in groups[:44]:
    n=str(g['n']);P=D(g['biomass'])*D(g['pb']);available=P*D(g['ee'])
    pred=sum((D(p['biomass'])*D(p['qb'])*D(model['diet'][str(p['n'])].get(n,'0')) for p in groups[:42]),D(0))
    catch=sum((D(v) for kind in ['landings','discards'] for v in model[kind].get(n,{}).values()),D(0))
    total_alt=sum((D(r['printed_total']) for r in catch_totals if r['group']==g['n'] and r['printed_total'] is not None),D(0))
    residual=pred+catch-available
    audit.append({'seq':g['n'],'group':g['name'],'production':str(P),'available_used_production':str(available),'predation':str(pred),'fleet_catch_removal':str(catch),'printed_totals_catch_alternative':str(total_alt),'BA':'0','net_migration':'0','residual_fleet_basis':str(residual),'residual_fraction_of_production':str(residual/P),'EE_required_fleet_basis':str((pred+catch)/P),'residual_printed_total_basis':str(pred+total_alt-available)})
dump(OUT/'SOURCE_PRODUCTION_BALANCE.json',audit)
savecsv(OUT/'SOURCE_PRODUCTION_BALANCE.csv',list(audit[0]),[[r[k] for k in audit[0]] for r in audit])
summary={'groups':46,'consumers':42,'diet_cells':len(evidence),'nonzero_diet_cells':sum(bool(e['printed_value']) for e in evidence),
         'diet_sum_min':min(map(D,sums.values())).__str__(),'diet_sum_max':max(map(D,sums.values())).__str__(),
         'catch_total_conflicts':len([r for r in catch_totals if r['difference_fleet_minus_printed'] not in [None,'0','0.000000000'] and D(r['difference_fleet_minus_printed'])!=0]),
         'worst_source_production_residual':max(audit,key=lambda r:abs(D(r['residual_fraction_of_production']))),
         'canonical_sha256':hashlib.sha256((MODEL/'model.json').read_bytes()).hexdigest()}
dump(REVIEW/'EXTRACTION_SUMMARY.json',summary);print(json.dumps(summary,indent=2))
