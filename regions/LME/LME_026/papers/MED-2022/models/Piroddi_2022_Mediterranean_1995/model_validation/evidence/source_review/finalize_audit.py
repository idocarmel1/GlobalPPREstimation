from pathlib import Path
from decimal import Decimal
import json,sys
OUT=Path(__file__).parent;ROOT=OUT.parents[3];REGION=OUT.parents[1];sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,sha
audit=json.loads((OUT/'adopted_taxon_audit.json').read_text(encoding='utf-8'))
for r in audit:
    r['appendix_reason']=r['appendix_reason'].split(' Locators:')[0]
    locs=['S2 group '+str(e.get('group_id'))+', DOCX table 2 row '+str(e.get('row_one_based')) for e in r['membership_evidence'] if e.get('source_table')=='S2']
    r['appendix_reason']+=' Locators: '+('; '.join(locs) if locs else 'authoritative taxonomy/ecology in retained taxon audit')+'; Sources S2/TAXONOMY/ALLOC. Exact quantities and all candidates: allocation_evidence.json, taxon key.'
    if r.get('authority_url'):r['appendix_reason']+=' Authority: '+r['authority_url']+'.'
(OUT/'adopted_taxon_audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=True),encoding='utf-8')
am={r['taxon']:r for r in audit};d=json.loads((OUT/'allocation_evidence.json').read_text(encoding='utf-8'))
for r in d['records']:
    if r['allocation_rule']=='W1':r['allocation_denominator']='1';r['allocation_field']='structural sole-group assignment (not a biological measurement)'
    elif r['allocation_rule']=='W9':r['allocation_denominator']=str(sum((Decimal(c['accepted_biomass_raw']) for c in r['candidates']),Decimal(0)));r['allocation_field']='accepted group.biomass';r['allocation_units']='t/km2'
    elif r['retained_prior_stage_weights']:r['allocation_denominator']=str(sum((Decimal(c['source_total_removals_raw']) for c in r['candidates']),Decimal(0)));r['allocation_field']='accepted group.export = retained source landings plus discards';r['allocation_units']='t/km2 per annual baseline time step'
    else:r['allocation_denominator']=str(sum((Decimal(c['source_landings_sum']) for c in r['candidates']),Decimal(0)));r['allocation_field']='source_fisheries.landings: sum of all37 source fleets';r['allocation_units']='t/km2 per annual baseline time step'
    r['candidate_inclusion_evidence']=am[r['taxon']]['membership_evidence'];r['candidate_inclusion_rationale']=am[r['taxon']]['membership_reason'];r['zero_candidates_retained']=True;r['loader_defaults_used_as_observed_catch']=False
(OUT/'allocation_evidence.json').write_text(json.dumps(d,indent=2,ensure_ascii=True),encoding='utf-8')
previous=OUT/'qa/relocated_repository/regions/LME_026/LME_026.xlsx'
if previous.exists():
    old={r['seq']:r for r in records(read_book(previous),'Selected model groups','Groups')};new={r['seq']:r for r in records(read_book(REGION/'LME_026.xlsx'),'Selected model groups','Groups')}
    changes=[{'key':{'unit_id':'LME_026','model_id':'Piroddi_2022_Mediterranean_1995','seq':seq},'field':k,'old':old[seq][k],'adopted':v,'reason':'Decode immutable accepted UTF-8 source bytes correctly; source text inventory repair only'} for seq,r in new.items() for k,v in r.items() if old[seq].get(k)!=v]
    assert {(r['key']['seq'],r['field']) for r in changes}=={(62,'taxon_descr'),(69,'taxon_descr')}
    (OUT/'qa/encoding_correction.json').write_text(json.dumps({'source_bytes_changed':False,'numeric_fields_changed':False,'all_active_json_reads_explicit_utf8':True,'changes':changes,'corrected_workbook_sha256':sha(REGION/'LME_026.xlsx')},indent=2,ensure_ascii=True),encoding='utf-8')
print(json.dumps({'finalized_taxa':len(audit),'allocations':len(d['records'])}))
