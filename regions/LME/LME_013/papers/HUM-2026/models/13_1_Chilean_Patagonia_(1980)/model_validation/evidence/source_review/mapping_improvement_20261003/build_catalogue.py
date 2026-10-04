from pathlib import Path
import json,sys,re
sys.stdout.reconfigure(encoding='utf-8');OUT=Path(__file__).parent
prefix='validation_reports/13_1_Chilean_Patagonia_(1980)/mapping_improvement_20261003/'
rows=[
 {'description':'Current keyed old/new decision ledger for all 218 catch labels','supports':'Final memberships, component confidence, allocation assumptions, retained and changed decisions; fixed 2019 confidence universe.','label':'Complete reassessment ledger','target':prefix+'decision_ledger.json'},
 {'description':'Baseline and revised confidence, coverage and regional PPR','supports':'Full-precision confidence/rule percentages and arithmetic changes across saved methods, source scopes and catch bases.','label':'Comparison and denominator evidence','target':prefix+'comparison_summary.json'},
 {'description':'Fish and squid primary-source review','supports':'Provider scope, synonyms, habitat and size; exact source Table 1 candidates; all assigned fish and squid including zero landings.','label':'Fish and squid evidence','target':prefix+'fish_squid_review.json'},
 {'description':'Cartilaginous fish and invertebrate primary-source review','supports':'Named Skates stock, other rays/sharks/chimaeras and generic Benthos; historical reporting conflicts and habitat evidence.','label':'Ray shark and invertebrate evidence','target':prefix+'elasm_invertebrate_review.json'},
 {'description':'Observed-allocation search and source-proxy review','supports':'All pooled/stage candidate sets, raw provider catch strata, native source missing values, rejected incomplete catches and complete catch/biomass proxies.','label':'Allocation and reporting evidence','target':prefix+'allocation_residual_review.json'},
 {'description':'Retained direct diagnostics and coefficient identity verification','supports':'Actual GE, TE EEfix and With Egestion WARN returns; all source/group coefficients verified without a new solver run.','label':'Diagnostic evidence','target':prefix+'diagnostic_verification.json'},
 {'description':'Saved-deliverable and protected-input verification','supports':'Weights, freshness, denominator, exact decision lists, local links and manual document preservation.','label':'Verification evidence','target':prefix+'verification.json'},
 {'description':'Neira et al. source supplementary S1 and S2','supports':'S1 corrected catch time series for six groups; S2 calibrated vulnerabilities. Neither establishes an expanded species inventory or observed Hoki stage masses.','label':'Source supplement S1 S2','target':'papers/HUM-2026/1-s2.0-S0079661125002198-mmc1.docx'},
 {'description':'Neira et al. source supplementary S3 through S7','supports':'Parameter, diet and catch pedigree/index options; reviewed separately from frozen selected-model/runtime inputs.','label':'Source supplement S3 S7','target':'papers/HUM-2026/1-s2.0-S0079661125002198-mmc2.docx'}]
seen={r['target'] for r in rows}
def walk(obj,context=''):
    if isinstance(obj,dict):
        url=obj.get('url',obj.get('source_url',obj.get('link')))
        title=obj.get('title',obj.get('source_title',obj.get('citation',obj.get('description',obj.get('locator')))))
        if title is None and obj.get('exact_support'):
            title=context.replace('_',' ')+' — '+obj.get('material_read','regional evidence')
        if isinstance(url,str) and 'marinespecies.org/' in url:return
        if isinstance(url,str) and re.match(r'https?://',url) and isinstance(title,str) and url not in seen:
            locator=obj.get('locator',obj.get('pages',obj.get('page','')));checked=obj.get('checked',obj.get('supports',obj.get('finding',obj.get('evidence',obj.get('exact_support','')))))
            if not isinstance(checked,str):checked='Regional taxonomy, ecology or allocation evidence; detailed applicability in the linked review.'
            scope=obj.get('applicability_disposition',obj.get('disposition',obj.get('applicability','')))
            support='; '.join(str(v) for v in [locator,checked,scope] if v)
            if len(support)>330:support=support[:327].rsplit(' ',1)[0]+'…'
            rows.append({'description':title,'supports':support or context,'label':'Primary source','target':url});seen.add(url)
        for k,v in obj.items():walk(v,k)
    elif isinstance(obj,list):
        for x in obj:walk(x,context)
for file in ['fish_squid_review.json','elasm_invertebrate_review.json','allocation_residual_review.json','root_additional_review.json']:walk(json.loads((OUT/file).read_text(encoding='utf-8')),file)
for item in rows:item['date']='2026-10-03'
(OUT/'source_catalogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('New descriptive source rows',len(rows))
