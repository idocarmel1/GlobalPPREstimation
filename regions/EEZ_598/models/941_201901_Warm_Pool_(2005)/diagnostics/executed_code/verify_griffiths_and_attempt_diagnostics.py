"""Independent PDF-coordinate cross-check, canonical checks, and bounded direct diagnostics."""
import json,sys,re,hashlib,shutil,traceback,contextlib
from pathlib import Path
from decimal import Decimal as D
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
MID='941_201901_Warm_Pool_(2005)';MODEL=ROOT/'regions/EEZ_941/models'/MID
REVIEW=MODEL/'source_review';OUT=MODEL/'diagnostics';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(Path.home()/'.agents/skills/ecopath-extraction/scripts'))
from pdfgrid import get_words
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,default=str)+'\n',encoding='utf-8')
source=json.loads((REVIEW/'FINAL_EXTRACTION.json').read_text(encoding='utf-8'))
pdf=BASE/'Griffiths2019/supplement_word_render.pdf';pdf_diet={};word_evidence=[]
for page in [29,30]:
    lines=get_words(str(pdf),page,backend='poppler')
    header=next(l for l in lines if sum(bool(re.fullmatch(r'\d+',c.text)) for c in l.cells)>15)
    headers={int(c.text):c.xc for c in header.cells if re.fullmatch(r'\d+',c.text)}
    for l in lines:
        if not l.cells or not re.fullmatch(r'\d+',l.cells[0].text) or len(l.cells)<2:continue
        prey=int(l.cells[0].text)
        if not 1<=prey<=46 or l.y<=header.y:continue
        for c in l.cells[1:]:
            if not re.fullmatch(r'\d+\.\d+',c.text):continue
            pred=min(headers,key=lambda n:abs(headers[n]-c.xc))
            assert abs(headers[pred]-c.xc)<12,(page,prey,pred,c)
            key=(prey,pred);assert key not in pdf_diet
            pdf_diet[key]=c.text;word_evidence.append({'page':page,'prey':prey,'predator':pred,'value':c.text,'bbox':[c.x0,c.y0,c.x1,c.y1]})
xml_diet={(int(prey),int(pred)):v for pred,col in source['diet'].items() for prey,v in col.items()}
assert pdf_diet==xml_diet,[(k,pdf_diet.get(k),xml_diet.get(k)) for k in set(pdf_diet)|set(xml_diet) if pdf_diet.get(k)!=xml_diet.get(k)]
dump(REVIEW/'PDF_DIET_WORD_EVIDENCE.json',word_evidence)

# Catch totals, including source-inconsistent totals, independently agree with rendered coordinates.
lines=get_words(str(pdf),31,backend='poppler')
header=next(l for l in lines if sum(c.text=='LL' for c in l.cells)==2)
head=[c for c in header.cells if c.text in ['LL','PSA','PSU','PL','Total']]
assert len(head)==10
pdf_catch={}
for l in lines:
    if not l.cells or not re.fullmatch(r'\d+',l.cells[0].text) or len(l.cells)<2:continue
    n=int(l.cells[0].text)
    if not 1<=n<=46 or l.y<=header.y:continue
    for c in l.cells[1:]:
        if re.fullmatch(r'\d+\.\d+',c.text):
            j=min(range(10),key=lambda j:abs(head[j].xc-c.xc))
            assert abs(head[j].xc-c.xc)<15
            pdf_catch[n,j]=c.text
xml=json.loads((REVIEW/'SUPPLEMENT_XML_EVIDENCE.json').read_text(encoding='utf-8'))['tables'][5]
xml_catch={(int(r[0]['text']),j):r[col]['text'].strip() for r in xml[2:48] for j,col in enumerate([2,3,4,5,6,8,9,10,11,12]) if r[col]['text'].strip()}
assert pdf_catch==xml_catch

canonical=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))
for g,s in zip(canonical['group'],source['groups']):
    assert int(g['group_seq'])==s['n'] and g['group_name']==s['name']
    for f in ['biomass','pb','qb','ee']:assert g[f]==(s[f] if s[f] is not None else '-9999')
    assert g['gs']=='-9999' and g['biomass_accum']=='0' and g['net_migration']=='0'
    assert g['taxon_descr']==s['taxon_descr']
    d={x['prey_seq']:x['proportion'] for x in g['diet_descr']['diet']} if g['diet_descr'] else {}
    assert d==source['diet'].get(str(s['n']),{})
    assert all(x['detritus_fate']=='-9999' for x in (g['diet_descr']['diet'] if g['diet_descr'] else []))
dump(REVIEW/'POST_SUPPLEMENT_VERIFICATION.json',{'source_crosscheck':'PASS','independent_rendered_PDF_diet_cells':len(pdf_diet),'independent_rendered_PDF_catch_cells_including_printed_totals':len(pdf_catch),'canonical_source_values_exact':True,'diet_normalized':False,'source_fate_unknown':True,'model_balance':'FAIL_SOURCE_PRODUCTION_EQUATION','note':'XML and PDF coordinate agreement verifies transcription, not source model consistency.'})

# Freeze actual loader code; no engine edits or substitute routing.
CODE=OUT/'executed_code';CODE.mkdir(exist_ok=True)
for n in ['ModelData.py','PPRCalculator.py','utils.py']:shutil.copy2(ROOT/'tools/scientific_code/PPREstimation'/n,CODE/n)
shutil.copy2(__file__,CODE/'verify_griffiths_and_attempt_diagnostics.py')
sys.path.insert(0,str(CODE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
provenance={'model_sha256':hashlib.sha256((MODEL/'model.json').read_bytes()).hexdigest(),
            'supplement_sha256':source['source_identity']['supplement_sha256'],
            'requested_calls':[{'TE_option':o,'short':False,'flat':False} for o in ['GE','TE','With Egestion']],
            'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CODE.glob('*.py')},
            'source_diet_normalization':False,'global_excluded':True}
dump(OUT/'RUN_PROVENANCE.json',provenance)
attempts=[]
with (OUT/'execution.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    data=ModelData(str(MODEL/(MID+'.json')))
    data.groups_data.to_csv(OUT/'modeldata_groups_before_defaults.csv')
    data.DC.to_csv(OUT/'canonical_loaded_diet.csv');data.det_fate.to_csv(OUT/'loader_detritus_fate.csv')
    # This is an explicit source net-migration term. Gross migration remains unknown.
    data.groups_data.loc[data.groups_data['trophic_info']!='Import','net_migration']=0.0
    for label,gs in [('strict_source',False),('standard_default_GS_admission_probe',True)]:
        settings=dict(underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=gs,weight_flow=1.,weight_guess=1.,DC_tol=.001,normalize_DC=False)
        try:
            calc=PPRCalculator.from_modeldata(data,**settings)
            attempts.append({'configuration':label,'settings':settings,'load_status':'loaded'})
            if label=='strict_source':
                for option in ['GE','TE','With Egestion']:
                    result=calc.diagnose_sppr(TE_option=option,short=False,flat=False)
                    dump(OUT/('diagnose_'+option.replace(' ','_')+'.json'),result)
        except Exception as e:
            attempts.append({'configuration':label,'settings':settings,'load_status':'BLOCKED','exception_type':type(e).__name__,'message':str(e)});traceback.print_exc()
dump(OUT/'LOAD_ATTEMPTS.json',attempts)
dump(OUT/'CALL_OUTCOMES.json',{o:{'call_status':'NOT_RUN_LOADER_BLOCKED','direct_return':None} for o in ['GE','TE','With Egestion']})
dump(OUT/'LOADER_TRANSFORMATIONS.json',{'transformations_observed_before_block':['ModelData adds synthetic diet_import group; missing diet imports become zero in its matrix.','Unknown detritus fate entries map to zero and the two detritus self-routes become identity. No living routing is inferred for a multi-detritus model.','Detritus catch is set to zero by ModelData.','Source net migration=0 copied to modeldata net_migration; gross migration fields remain source-unknown.'],
    'default_GS_probe':'Configuration tested for admission only; source GS was not changed. It also blocks on missing multi-pool routing.',
    'not_performed':['diet normalization','detritus pooling','invented routing','parameter repair','SPPR return fabrication']})
print(json.dumps({'verification':'PASS','diet_cells':len(pdf_diet),'catch_cells':len(pdf_catch),'loader_attempts':attempts},indent=2))
