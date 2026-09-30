from __future__ import annotations
import sys, re, json, hashlib
from pathlib import Path
from decimal import Decimal
import numpy as np
import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
MODEL = ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json'
SOURCE = ROOT/'regions/LME_034/papers/LME034-Guenette-2013/009031359-84f3dc3d.pdf'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
model=json.loads(MODEL.read_text(encoding='utf-8'))
groups={int(g['group_seq']):g for g in model['group']}
reader=PdfReader(SOURCE)
texts={i+1:reader.pages[i].extract_text() or '' for i in [8,10,18,19,20,21,22,23,24,25,26,45,53,54,55]}
for page,text in texts.items(): (OUT/f'source_page_{page:02d}.txt').write_text(text,encoding='utf-8')

# Table 16 has eight numeric trailing fields for consumers and seven for producers.
parameter_rows=[]
fields=['tl','habitat_area','biomass_habitat_area','biomass_printed','pb','qb','ee','pq']
for line in texts[24].splitlines():
    m=re.match(r'^\s*(\d+)\s+(.+)$',line)
    if not m: continue
    seq=int(m[1])
    if seq not in groups or seq==49: continue
    parts=m[2].split(); n=7 if seq in [42,43,44,45] else 8
    vals=parts[-n:]; name=' '.join(parts[:-n])
    try: numbers=list(map(float,vals))
    except ValueError: continue
    row={'seq':seq,'printed_name':name,'pdf_page':24,'table':'16'}
    row.update(dict(zip(fields[:n],numbers)))
    row['printed_strings']=dict(zip(fields[:n],vals)); parameter_rows.append(row)
assert len(parameter_rows)==48
parameter_rows.append({'seq':49,'printed_name':'Detritus','pdf_page':24,'table':'16',
                       'tl':1.,'habitat_area':1.,'biomass_habitat_area':137.,'biomass_printed':137.,'ee':.332,
                       'printed_strings':{'tl':'1','habitat_area':'1','biomass_habitat_area':'137','biomass_printed':'137','ee':'0.332'}})
param_checks=[]
for row in parameter_rows:
    g=groups[row['seq']]
    for field in ['habitat_area','biomass_habitat_area','pb','qb','ee']:
        if field not in row: continue
        actual=float(g[field]); expected=row[field]
        param_checks.append({'seq':row['seq'],'group':g['group_name'],'field':field,'source':expected,
                             'canonical':actual,'difference':actual-expected,'match':abs(actual-expected)<1e-12,
                             'locator':f'Table16 p24 row {row["seq"]} {field}'})
    product=row['habitat_area']*row['biomass_habitat_area']
    param_checks.append({'seq':row['seq'],'group':g['group_name'],'field':'biomass',
                         'source':row['biomass_printed'],'canonical':float(g['biomass']),
                         'source_derived_product':product,'difference_to_printed':float(g['biomass'])-row['biomass_printed'],
                         'match_to_product':abs(float(g['biomass'])-product)<1e-12,
                         'locator':f'Table16 p24 row {row["seq"]} habitat fraction × B_hab'})

# Table17 continued last block misnumbers Detritus/Import as 46/47; identities own the crosswalk.
diet=np.zeros((50,49)); locators={}; crosswalk=[]
for page,predators in [(25,list(range(1,16))),(26,list(range(16,30))),(27,list(range(30,42))+[46,47,48])]:
    nr=0
    for line in texts[page].splitlines():
        m=re.match(r'^\s*(\d+)\s+(.+)$',line)
        if not m: continue
        original_seq=int(m[1]);parts=m[2].split(); n=len(predators)
        if len(parts)<=n: continue
        name=' '.join(parts[:-n]); vals=parts[-n:]
        try: floats=[float(v) for v in vals]
        except ValueError: continue
        seq=49 if name=='Detritus' else 50 if name=='Import' else original_seq
        if not 1<=seq<=50: continue
        if seq!=original_seq: crosswalk.append({'pdf_page':page,'printed_seq':original_seq,'verified_seq':seq,'name':name})
        for pred,value,raw in zip(predators,floats,vals):
            diet[seq-1,pred-1]=value
            locators[(seq,pred)]={'page':page,'printed_row':original_seq,'name':name,'printed_value':raw}
        nr+=1
    assert nr==(47 if page==27 else 50),(page,nr)
canonical=np.zeros((50,49))
for pred,g in groups.items():
    entries=(g.get('diet_descr') or {}).get('diet',[])
    if isinstance(entries,dict): entries=[entries]
    for d in entries: canonical[int(float(d['prey_seq']))-1,pred-1]=float(d['proportion'])
    canonical[49,pred-1]=float(g['diet_imp'])
diet_changes=[];norm_rows=[]
for pred,g in groups.items():
    s=float(diet[:,pred-1].sum());factor=1/s if s else 1.
    normalized=diet[:,pred-1]*factor
    mismatch=np.abs(normalized-canonical[:,pred-1]); maxdiff=float(mismatch.max())
    norm_rows.append({'seq':pred,'group':g['group_name'],'source_sum':s,'factor':factor,
                     'canonical_sum':float(canonical[:,pred-1].sum()),'normalization_max_abs_difference':maxdiff,
                     'reproducible_as_source_normalization':maxdiff<1e-12})
    for prey in range(1,51):
        delta=float(canonical[prey-1,pred-1]-diet[prey-1,pred-1])
        if delta:
            diet_changes.append({'predator_seq':pred,'predator_name':g['group_name'],'prey_seq':prey,
              'prey_name':groups.get(prey,{}).get('group_name','diet_import'),'source':float(diet[prey-1,pred-1]),
              'canonical':float(canonical[prey-1,pred-1]),'difference':delta,'factor':factor,
              'locator':locators.get((prey,pred),{'page':27,'reason':'omitted biological prey row implies zero in final block'})})

# Read Table15 and catch A2.1 by word position: retains blank and zero distinctions.
with pdfplumber.open(SOURCE) as pdf:
    page=pdf.pages[22]
    words=page.extract_words(x_tolerance=1,y_tolerance=3)
    (OUT/'source_table15_words.json').write_text(json.dumps(words,ensure_ascii=False,indent=2),encoding='utf-8')
    original_rows=[]
    bounds=[(170,220,'habitat_area'),(220,274,'biomass_habitat_area'),(274,314,'pb'),(314,351,'qb'),
            (351,384,'ee'),(384,414,'pq'),(414,475,'gs'),(475,540,'detritus_import')]
    numbered=[x for x in words if x['x0']<85 and x['text'].isdigit() and 1<=int(x['text'])<=49 and x['top']>150]
    for marker in numbered:
        line=[x for x in words if abs(x['top']-marker['top'])<2]
        row={'seq':int(marker['text']),'locator':f'Table15 p23 row{marker["text"]}',
             'fields':{field:None for _,_,field in bounds},'field_states':{field:'blank unknown source input' for _,_,field in bounds}}
        for x in line:
            center=(x['x0']+x['x1'])/2
            for left,right,field in bounds:
                if left<=center<right:
                    try:row['fields'][field]=float(x['text']);row['field_states'][field]='printed zero' if float(x['text'])==0 else 'printed known value'
                    except ValueError:pass
        original_rows.append(row)
    assert len(original_rows)==49
    gs_checks=[{'seq':row['seq'],'source_gs':row['fields']['gs'],'canonical_gs':float(groups[row['seq']]['gs']),
                'match':row['fields']['gs']==float(groups[row['seq']]['gs'])} for row in original_rows]
    (OUT/'source_table16_words.json').write_text(json.dumps(pdf.pages[23].extract_words(extra_attrs=['fontname']),ensure_ascii=False,indent=2),encoding='utf-8')
    for page_no in [23,24,27,46,56]:
        pdf.pages[page_no-1].to_image(resolution=145).save(OUT/f'source_page_{page_no:02d}.png')

catch_rows=[]
for line in texts[46].splitlines():
    m=re.match(r'^\s*(\d+)\s+(.+)$',line)
    if not m or int(m[1]) not in groups:continue
    seq=int(m[1]);parts=m[2].split()
    try:vals=list(map(float,parts[-9:]))
    except ValueError:continue
    row={'seq':seq,'group':groups[seq]['group_name'],'printed_name':' '.join(parts[:-9]),
         'fleets':dict(zip(['Region1','Region3','Region2_industrial','Region2_small_scale','Hilsa','BET','YFT','Marlins'],vals[:-1])),
         'source_displayed_total':vals[-1],'source_displayed_fleet_sum':sum(vals[:-1]),
         'canonical_catch':float(groups[seq]['export']),'units':'t wet weight per entire study area km² per year',
         'denominator_km2':6205051,'catch_year':1978,'locator':f'AppendixA2.1 p46 row{seq}',
         'total_difference':float(groups[seq]['export'])-vals[-1],
         'fleet_sum_difference':float(groups[seq]['export'])-sum(vals[:-1])}
    catch_rows.append(row)
assert len(catch_rows)==49

report={'schema_version':1,'model_id':'34_1_Bay_of_Bengal_(1978)',
 'model_sha256':sha(MODEL),'source_sha256':sha(SOURCE),'source_pdf':str(SOURCE.relative_to(ROOT)),
 'selected_parameter_table':'Table16 balanced p24','competing_table':'Table15 unbalanced p23; never merged into balanced biological parameters',
 'group_count':49,'parameter_rows':parameter_rows,'parameter_checks':param_checks,
 'parameter_mismatches':[x for x in param_checks if x.get('match') is False],
 'biomass_product_mismatches':[x for x in param_checks if x.get('match_to_product') is False],
 'diet_orientation':'prey rows × predator columns','diet_axis_prey':list(range(1,51)),
 'diet_axis_predator':list(range(1,50)),'source_diet':diet.tolist(),'canonical_diet':canonical.tolist(),
 'diet_crosswalk':crosswalk,'diet_normalization':norm_rows,'diet_changed_cells':diet_changes,
 'unbalanced_original_parameter_rows':original_rows,'unbalanced_gs_checks':gs_checks,'catch_rows':catch_rows,
 'catch_total_comparison':{'canonical_sum':sum(x['canonical_catch'] for x in catch_rows),
                         'sum_displayed_group_totals':sum(x['source_displayed_total'] for x in catch_rows),
                         'max_abs_group_total_difference':max(abs(x['total_difference']) for x in catch_rows)},
 'material_diet_source_conflicts':[x for x in norm_rows if x['seq'] not in [42,43,44,45,49] and abs(x['source_sum']-1)>.001],
 'missing_source_fields':{'biomass_accum':'not reported in Tables15/16; canonical -9999',
 'migration':'not reported in Tables15/16; canonical -9999','detritus_fate':'not reported; canonical zero routing values, loader assumes closed single-pool routing'},
 'gs_source':'Table15 explicitly reports 0.2 for consumers and 0 for producers/detritus; canonical agrees',
 'source_qb_basis':'Table16 balanced outputs; Table15 predominantly leaves QB blank and supplies P/Q',
 'source_identity_notes':['Table17 p27 omits separate biological prey46/47/48 rows and misnumbers named Detritus/Import49/50 as46/47',
 'Table16 printed whole-area biomass is a rounded display; canonical uses printed habitat-area biomass × habitat fraction',
 'Benthic plants printed B0.784 versus product0.784771 (ordinary nearest three-decimal product would0.785), recorded as source display inconsistency'],
 'appendix_A32_comparison':'Original diet matrix finalblock p56 repeats malformed region3 detritus/import row zeros; does not recover missing balanced diets. Predator46/47/48 columns exist, biological prey46/47/48 rows omitted.',
 'correction_eligibility':'No evidence-supported numerical diet correction recovered; retain canonical as existing normalized assumption variant only, with source limitations',
 'audit_state':'Balanced Table16 parameters/habitat products and all Table17 cells checked; Table15 fields/blanks/GS/detritus imports retained separately; all49 A2.1 catch totals/fleet components compared; native recovery pending'}
closure=[]
consumer_q=np.array([float(groups[i]['biomass'])*float(groups[i]['qb']) if int(groups[i]['pp'])==0 else 0 for i in range(1,50)])
for label,dc in [('source_diet',diet),('canonical_diet',canonical)]:
    predation=dc@consumer_q
    for seq in range(1,49):
        g=groups[seq];production=float(g['biomass'])*float(g['pb']);catch=float(g['export'])
        remainder=production*float(g['ee'])-catch-predation[seq-1]
        closure.append({'diet_state':label,'seq':seq,'name':g['group_name'],'production':production,
             'ecotrophic_production':production*float(g['ee']),'predation':float(predation[seq-1]),'catch':catch,
             'closure_BA_with_zero_migration':float(remainder),'production_relative_residual':float(remainder/production),
             'source_BA_available':False})
report['independent_production_closure']=closure
report['steady_state_limitation']='Loaded strict balance is achieved with constructor-derived BA; source printed parameters/diets do not supply observed BA. Diet normalization materially increases residuals (max77.3% production) relative to unnormalized printed diets (~0.37% for groups1–45).'
(OUT/'source_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'parameter_mismatches':report['parameter_mismatches'],'biomass_product_mismatches':report['biomass_product_mismatches'],
 'diet_normalization_nonmatching':[x for x in norm_rows if not x['reproducible_as_source_normalization']],
 'source_diet_sum_range':[min(x['source_sum'] for x in norm_rows if x['source_sum']),max(x['source_sum'] for x in norm_rows)],
 'max_diet_abs_change':max(abs(x['difference']) for x in diet_changes),'changed_cells':len(diet_changes)},ensure_ascii=False))
