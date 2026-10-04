"""Scoped source diet restoration; never runs a scientific calculator."""
from pathlib import Path
from decimal import Decimal, localcontext
from copy import deepcopy
import hashlib, json, csv, re, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
REGION = ROOT / 'regions/LME_038'
EVIDENCE = Path(__file__).parent
SELECTED_ID = '38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
SOURCE_ID = '38_38001_Java_Sea_(mid1970s)'
SELECTED = REGION / 'models' / SELECTED_ID / 'model.json'
SOURCE = REGION / 'models' / SOURCE_ID
PDF = REGION / 'papers/BUCHARY-1991/ubc_1999-0254.pdf.pdf'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def dump(name, data):
    (EVIDENCE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def diets(g):
    d = g['diet_descr']['diet']
    return d if isinstance(d, list) else [d]
def value(g):
    return {d['prey_seq']: d['proportion'] for d in diets(g)}
def differences(a,b,p=''):
    if type(a) != type(b): return [(p,a,b)]
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        return sum((differences(a[k],b[k],p+'/'+k) for k in a),[])
    if isinstance(a,list):
        assert len(a)==len(b)
        return sum((differences(x,y,p+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    return [] if a==b else [(p,a,b)]

assert not (EVIDENCE / 'root_receipt.json').exists(), 'Do not overwrite completed audit'
protected = {rel(p):sha(p) for p in REGION.rglob('*') if p.is_file() and EVIDENCE not in p.parents and p != SELECTED}
before_bytes = SELECTED.read_bytes()
before_sha = hashlib.sha256(before_bytes).hexdigest()
before = json.loads(before_bytes)
assert before_sha == 'db0bc803ea5a068e346b82df8d8b4e4b13f8351bf61103c6507997cb6996ae35'
source = json.loads((SOURCE/'model.json').read_text(encoding='utf-8'))
extraction = json.loads((SOURCE/'extraction.json').read_text(encoding='utf-8'))
history = json.loads((SELECTED.parent/'evidence/SOURCE_TO_DERIVED.json').read_text(encoding='utf-8'))
reload = json.loads((SELECTED.parent/'evidence/DERIVED_RELOAD_VALIDATION.json').read_text(encoding='utf-8'))
assert reload['derived_sha256']==before_sha
assert reload['source_sha256']==sha(SOURCE/'model.json')
assert sha(PDF)=='eb2c504f176b230153cfd4caa0fc6671e02c5d1cdc0fd2bc0561d3590759f53d'
raw = {'1':'0.150','2':'0.290','3':'0.139','4':'0.001','5':'0.070','10':'0.010'}
assert raw==extraction['diet']['9']
g9 = before['group'][8]
assert g9['group_seq']=='9' and g9['group_name']=='Macrozoobenthos'
assert all(value(source['group'][8])[k]==v for k,v in raw.items())
hdiet = {h['prey']:h for h in history if h['seq']==9 and h['field']=='diet'}
assert all(hdiet[k]['source']==v and hdiet[k]['derived']==value(g9)[k] for k,v in raw.items())
assert all(Decimal(h['derived'])==Decimal(g['biomass_accum']) for h,g in zip([h for h in history if h['field']=='biomass_accum'],before['group']))

archive = EVIDENCE/'original_inputs'; archive.mkdir(exist_ok=True)
manifest=[]
for p in [SELECTED,SOURCE/'model.json',SOURCE/'extraction.json',SOURCE/'extracted_tables/Diet_composition.csv']:
    identity=sha(p); dest=archive/(identity+'_'+p.name)
    dest.write_bytes(p.read_bytes())
    assert sha(dest)==identity
    manifest.append({'path':rel(p),'sha256':identity,'archive':rel(dest)})
dump('original_inputs_manifest.json',manifest)

docx=next(REGION.glob('Model_validation*.docx'))
root=ET.fromstring(zipfile.ZipFile(docx).read('word/document.xml'))
paras=[''.join(p.itertext()) for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')]
dump('researcher_correction_evidence.json',{'docx':rel(docx),'sha256':sha(docx),
 'read_only_relevant_paragraphs':[p for p in paras if any(k in p.lower() for k in ['normalization','completed ba','28 signed','source/derived'])],
 'history_path':rel(SELECTED.parent/'evidence/SOURCE_TO_DERIVED.json'),
 'history_sha256':sha(SELECTED.parent/'evidence/SOURCE_TO_DERIVED.json'),
 'preserved_corrections':[h for h in history if h['field']=='biomass_accum'],
 'decision':'Prior normalization acceptance remains a historical runtime choice; latest source/canonical policy restores printed cells only. All accepted BA values retained. No new scientific trust signoff.'})

after = deepcopy(before)
ledger=[]
for i,d in enumerate(diets(after['group'][8])):
    prey=d['prey_seq']
    if prey not in raw: continue
    pointer=f'/group/8/diet_descr/diet/{i}/proportion'
    ledger.append({'consumer_id':'9','consumer_name':'Macrozoobenthos','prey_id':prey,
      'selected_json_pointer':pointer,'before_literal':d['proportion'],'printed_source_literal':raw[prey],
      'adopted_literal':raw[prey],'accepted_non_normalization_override':None,
      'source_file':rel(PDF),'source_sha256':sha(PDF),'pdf_page':81,'printed_page':72,'table':'3.10',
      'table_coordinate':f'prey row {prey}; predator column 9',
      'visual_evidence':rel(EVIDENCE/'primary_table_3_10_page81.png'),
      'retained_extraction':rel(SOURCE/'extraction.json'),'extraction_pointer':f'/diet/9/{prey}',
      'historical_transformation':hdiet[prey],
      'trust_status':'not-established by this audit; literal visually confirmed'})
    d['proportion']=raw[prey]
diff=differences(before,after)
assert len(diff)==6 and {p for p,_,_ in diff}=={x['selected_json_pointer'] for x in ledger}
# Minimal exact text replacement preserves every other byte, field and formatting.
after_bytes=before_bytes
for cell in ledger:
    old=('"proportion": "'+cell['before_literal']+'"').encode()
    new=('"proportion": "'+cell['adopted_literal']+'"').encode()
    assert after_bytes.count(old)==1
    after_bytes=after_bytes.replace(old,new,1)
assert json.loads(after_bytes)==after

all_cells=[]; sums=[]; runtime=[]
with localcontext() as ctx:
    ctx.prec=50
    for index,(g,sg,bg) in enumerate(zip(after['group'],source['group'],before['group'])):
        assert g['group_seq']==sg['group_seq']
        for j,d in enumerate(diets(g)):
            all_cells.append({'consumer_id':g['group_seq'],'prey_id':d['prey_seq'],
              'canonical_literal':d['proportion'],'retained_source_literal':value(sg).get(d['prey_seq']),
              'source_native_pointer':f'/group/{index}/diet_descr/diet'+(f'/{j}' if isinstance(sg['diet_descr']['diet'],list) else '')+'/proportion',
              'numeric_equivalent_to_retained_source':Decimal(d['proportion'])==Decimal(value(sg).get(d['prey_seq'],'0')),
              'primary_fidelity':'affected six cells directly confirmed; other cells retained and compared, not comprehensively re-extracted'})
        total=sum((Decimal(d['proportion']) for d in diets(g)),Decimal(0))+Decimal(g['diet_imp'])
        oldtotal=sum((Decimal(d['proportion']) for d in diets(bg)),Decimal(0))+Decimal(bg['diet_imp'])
        sums.append({'consumer_id':g['group_seq'],'consumer_name':g['group_name'],'diet_import_literal':g['diet_imp'],
          'canonical_diet_plus_import_sum':str(total),'before_sum':str(oldtotal),
          'retained_source_import_literal':sg['diet_imp'],'missing_cells':'source structural dashes kept as existing zero/omission; no invented prey',
          'researcher_review_state':'not-established by this audit'})
        if total and g['pp']=='0':
            factor=Decimal(1)/total
            runtime.append({'consumer_id':g['group_seq'],'raw_sum':str(total),'runtime_sum':'1',
              'factor':str(factor),'execution_status':'permitted separate-copy mathematical transform; no fresh loader/diagnostic executed',
              'nonzero_cells':[{'prey_id':d['prey_seq'],'canonical_literal':d['proportion'],'runtime_decimal':str(Decimal(d['proportion'])*factor)} for d in diets(g) if Decimal(d['proportion'])],
              'import_raw':g['diet_imp'],'import_runtime_decimal':str(Decimal(g['diet_imp'])*factor)})
dump('changed_cells_ledger.json',ledger)
dump('all_retained_diet_cells_ledger.json',{'source_file':rel(SOURCE/'model.json'),'source_sha256':sha(SOURCE/'model.json'),'cells':all_cells})
dump('consumer_sums.json',sums)
dump('runtime_transformation_ledger.json',{'runtime_normalization_always_allowed':True,'scientific_trust':'not-established by this audit',
 'historical_normalized_input_sha256':before_sha,'historical_macrozoobenthos_cells':[h for h in history if h['field']=='diet'],
 'separate_copy_mathematical_transforms':runtime})
assert sha(SELECTED)==before_sha, 'Concurrent selected input edit detected'
assert all(sha(ROOT/p)==v for p,v in protected.items()), 'Concurrent protected regional edit detected'
SELECTED.write_bytes(after_bytes)
after_sha=sha(SELECTED)
assert SELECTED.read_bytes()==after_bytes
assert differences(before,json.loads(SELECTED.read_bytes()))==diff
changed_protected=[p for p,h in protected.items() if sha(ROOT/p)!=h]
assert not changed_protected
dump('protected_files_verification.json',{'unchanged':True,'files':protected,'selected_only_changed_pointers':[p for p,_,_ in diff],
 'all_28_BA_exactly_unchanged':True,'all_detritus_fate_exactly_unchanged':True,'source_extraction_and_tables_unchanged':True})
blockers=[
 'Printed Macrozoobenthos diet sums 0.660 (deficit 0.340); table caption claims unit sums. No omitted prey/import or corrected printed values established; this audit does not explain or repair that deficit.',
 'Existing diagnostics, coefficients, regional workbook result/freshness hashes, DOCX and historical model source_audit/report describe the prior normalized input. They are preserved under their actual old hash; new canonical scientific/review/calculation freshness is not established.',
 'Prior 28 computational BA completions are preserved, not measured stock changes. No fresh loading or balance check validates them against the restored canonical diet; prior normalized runtime may reproduce the old diet state, but equivalence is not newly tested.',
 'Other diet cells numerically match retained source canonical, but this scope directly re-extracted only the six proven normalized cells. Whole-matrix primary-source fidelity and researcher trust are not newly certified.'
]
dump('canonical_staleness.json',{'canonical_before_sha256':before_sha,'canonical_after_sha256':after_sha,
 'historical_diagnostic_model_sha256':reload['derived_sha256'],'historical_reloaded_reference_sha256':reload['reference_sha256'],
 'historical_diagnostics_preserved':True,'canonical_changed':True,'results_and_reviews_current_for_new_canonical':False,
 'freshness_hashes_rewritten':False,'model_selection_changed':False,'historical_metadata_in_model_source_audit':'Preserved verbatim; normalization description is historical and superseded for canonical cell state by this evidence.',
 'precise_blockers':blockers})
receipt={'region':'LME_038','selected_model_id':SELECTED_ID,'selected_path':rel(SELECTED),
 'outcome':'corrected-restored; six printed cells; retained source fidelity limits and deficit unresolved',
 'normalization_status':'confirmed before; six nonzero prey cells restored exactly; source raw sum 0.660',
 'reextraction_performed':True,'canonical_before_sha256':before_sha,'canonical_after_sha256':after_sha,
 'changed_diet_cells':ledger,'changed_diet_cells_count':6,'changed_import_cells_count':0,
 'evidence_paths':[rel(p) for p in sorted(EVIDENCE.glob('*')) if p.is_file()],
 'precise_blockers':blockers,'protected_files_unchanged':True,'new_review_approval':False}
dump('root_receipt.json',receipt)
print(json.dumps({k:receipt[k] for k in ['region','outcome','canonical_before_sha256','canonical_after_sha256','changed_diet_cells_count','protected_files_unchanged']},indent=2))
