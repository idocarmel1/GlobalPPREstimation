"""Read-only audit of current selected-model mapping and classic PPR inputs."""
from pathlib import Path
import collections
import hashlib
import json
import math
from openpyxl import load_workbook

ROOT = Path.cwd()
REGION = ROOT / 'regions/LME/LME_022'
OUT = REGION / 'work/2026-11-14_160000_validation/outputs'
OUT.mkdir(parents=True, exist_ok=True)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def tables(w):
    result = {}
    for ws in w:
        name = None
        headers = None
        for row_no, row in enumerate(ws, 1):
            vals = [c.value for c in row]
            if vals[0] == '@table':
                name = vals[1]
                headers = None
                result[(ws.title, name)] = []
            elif name and headers is None:
                headers = vals
            elif name and any(v is not None for v in vals):
                d = {str(k): v for k, v in zip(headers, vals) if k is not None}
                d['_row'] = row_no
                result[(ws.title, name)].append(d)
    return result

def number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)

workbook = REGION / 'LME_022.xlsx'
wbhash = sha(workbook)
w = load_workbook(workbook, read_only=True, data_only=False)
t = tables(w)
settings = {r['field']: r.get('value') for r in t[('Overview', 'Settings')]}
model_id = settings['selected_model_id']
model_path = REGION / settings['model_path']
model = json.loads(model_path.read_text(encoding='utf-8-sig'))
groups = model['group']
year, basis = settings['taxon_detail_year'], settings['catch_basis']
catch = [r for r in t[('Catch', 'Catch')] if r['catch_basis'] == basis]
duplicates = [k for k,v in collections.Counter(r['taxon'] for r in catch).items() if v > 1]
classic = t[('Classic PPR', 'Taxa')]
classic_duplicates = [k for k,v in collections.Counter(r['taxon'] for r in classic).items() if v > 1]
assert not duplicates and not classic_duplicates
classic_index = {r['taxon']: r for r in classic}
matching = t[('PPR', 'Matching')]
assert not matching, 'This evidence-unavailable audit must not overwrite a populated mapping.'
rows = []
for r in catch:
    name = r['taxon']
    c = r.get(str(year))
    cr = classic_index.get(name, {})
    coefficient = cr.get('sppr')
    tl = cr.get('tl')
    if number(c) and c == 0:
        ppr = 0.0
    elif number(c) and number(coefficient):
        ppr = c * coefficient / 9
    else:
        ppr = None
    reason = 'No mapping or allocation for this taxon is retained for the selected ICES 1991 model (S1, S2).'
    if not number(coefficient):
        reason += ' Classic TL/coefficient unavailable (S3). ' + ('Recorded zero catch gives zero annual PPR.' if c == 0 else 'Annual simple-chain PPR is unknown.')
    rows.append({
        'taxon': name, 'common_name': r.get('common_name'), 'functional_group': r.get('functional_group'),
        'commercial_group': r.get('commercial_group'), 'unidentified': r.get('unidentified'),
        'year': year, 'catch_basis': basis, 'catch_tonnes': c, 'tl': tl, 'classic_sppr': coefficient,
        'simple_chain_ppr_tC': ppr, 'tl_source': cr.get('tl_source'), 'classic_match_method': cr.get('match_method'),
        'missing_catch': not number(c), 'missing_tl': not number(tl), 'missing_coefficient': not number(coefficient),
        'missing_annual_ppr': ppr is None,
        'input_locations': {'catch': f'Catch!{r["_row"]}', 'classic': f'Classic PPR!{cr["_row"]}' if cr else None},
        'adopted_groups': [], 'known_partial_weights': [], 'unresolved_candidates': [],
        'membership_rule': 'Not assessed: selected-model mapping unavailable', 'membership_confidence': 'Unresolved',
        'membership_source_ids': ['S1', 'S2'],
        'allocation_rule': 'Not assessed: selected-model allocation unavailable', 'allocation_confidence': 'Unresolved',
        'allocation_source_ids': ['S1'], 'transfer_assumptions': [],
        'stored_confidence': None, 'review_confidence': 'Unresolved', 'overall_confidence': 'Unresolved',
        'reason': reason, 'difference_from_stored': 'No stored selected-model mapping exists.',
        'unresolved_reason': f'No exact-model taxon-to-group decision or allocation retained for {name}.',
        'source_ids': ['S1', 'S2', 'S3', 'S4'],
    })
rows.sort(key=lambda r: (r['simple_chain_ppr_tC'] is None, -(r['simple_chain_ppr_tC'] or 0), r['taxon']))
catch_total = math.fsum(r['catch_tonnes'] for r in rows if number(r['catch_tonnes']))
ppr_total = math.fsum(r['simple_chain_ppr_tC'] for r in rows if number(r['simple_chain_ppr_tC']))
missing = [r for r in rows if r['missing_annual_ppr']]
missing_catch = math.fsum(r['catch_tonnes'] for r in missing if number(r['catch_tonnes']))
summary = []
for label in ['High', 'Medium', 'Low', 'Very low', 'Unresolved']:
    q = [r for r in rows if r['overall_confidence'] == label]
    ct = math.fsum(r['catch_tonnes'] for r in q if number(r['catch_tonnes']))
    pt = math.fsum(r['simple_chain_ppr_tC'] for r in q if number(r['simple_chain_ppr_tC']))
    summary.append({'confidence': label, 'taxa': len(q), 'catch_tonnes': ct, 'catch_percentage': 100*ct/catch_total,
                    'simple_chain_ppr_tC': pt, 'ppr_percentage': 100*pt/ppr_total})
annual = [r for r in t[('Classic PPR','Annual')] if r['scope']=='all' and r['method']=='simple trophic chain' and r['catch_basis']==basis and r['unidentified']=='method']
annual_check = {r['metric']: {'stored_2019_value': r.get(str(year)), 'status': r['status']} for r in annual}
if 'ppr' in annual_check:
    annual_check['ppr'].update({'stored_tC_after_single_division_by_9': annual_check['ppr']['stored_2019_value']/9,
                              'audit_minus_saved_tC': ppr_total-annual_check['ppr']['stored_2019_value']/9})
components = collections.defaultdict(dict)
for r in t[('Catch','Catch')]: components[r['taxon']][r['catch_basis']] = r.get(str(year))
component_deltas = [{'taxon':k,'catch_minus_landings_discards':v['catch']-v['landings']-v['discards']} for k,v in components.items()
                    if all(number(v.get(x)) for x in ['catch','landings','discards']) and not math.isclose(v['catch'],v['landings']+v['discards'],rel_tol=1e-12,abs_tol=1e-8)]
prov_path = ROOT/'common_reference_data/taxonomy/references/provenance.json'
prov = json.loads(prov_path.read_text(encoding='utf-8-sig'))
source_records=[]
def walk(x):
    if isinstance(x,dict):
        if 'LME_022' in str(x.get('path','')) or 'trophic_levels_2020' in str(x.get('path','')): source_records.append(x)
        for v in x.values(): walk(v)
    elif isinstance(x,list):
        for v in x:walk(v)
walk(prov)
sources = [
 {'id':'S1','title':'LME_022 regional workbook: current selection, Catch and empty selected-model mapping tables', 'path':workbook.relative_to(ROOT).as_posix(),'locator':'Overview / Settings; Catch / Catch, 2019 catch basis; PPR / Matching, Mapping review and Allocation assumptions','supports':'Exact selected model, universe, catch and unavailable adopted mapping','sha256':wbhash},
 {'id':'S2','title':'ICES 2015 North Sea deposited Rpath port: canonical ecological group inventory','path':model_path.relative_to(ROOT).as_posix(),'locator':'group[].group_seq, group_name, taxon_descr','supports':'69 source ecological groups; all taxon_descr fields null; does not supply a catch-taxon crosswalk','sha256':sha(model_path)},
 {'id':'S3','title':'LME_022 frozen Classic PPR taxon lookup','path':workbook.relative_to(ROOT).as_posix(),'locator':'Classic PPR / Taxa: taxon, tl, sppr, tl_source, match_method','supports':'Saved independent simple-chain coefficients and actual missingness; no coefficients filled','sha256':wbhash},
 {'id':'S4','title':'Current project convention for simple-chain PPR and confidence reporting','path':'tools/templates/instructions.md','locator':'Taxon mapping and coverage summary; Confidence rules and examples','supports':'Catch × saved SPPR / 9 tonnes C, zero-catch treatment, universe and separate component confidence'},
 {'id':'S5','title':'Sea Around Us North Sea source catch download','path':'regions/LME/LME_022/raw/catch/LME_022-catch.zip','locator':'Retained provider catch download; source URL retained in provenance','supports':'Catch provider provenance', 'url':next((x.get('source_url') for x in source_records if str(x.get('path','')).endswith('LME_022-catch.zip')),None)},
 {'id':'S6','title':'Sea Around Us exploited organisms for LME 22','path':'regions/LME/LME_022/raw/catch/LME_022-exploited.json','locator':'Retained exploited-organism records','supports':'One stated source of frozen taxon TL values','url':next((x.get('source_url') for x in source_records if str(x.get('path','')).endswith('LME_022-exploited.json')),None)},
 {'id':'S7','title':'Retained 2020 trophic-level supplement','path':'common_reference_data/taxonomy/references/trophic_levels_2020.csv','locator':'Taxon/MeanTL entries; frozen lookup provenance is recorded per taxon','supports':'Other stated source of frozen TL inputs'},
 {'id':'S8','title':'ICES North Sea model group profile and stage boundaries','path':(model_path.parent/'extracted_tables/MODEL_PROFILE.md').relative_to(ROOT).as_posix(),'locator':'1991 static base state and five juvenile/adult stanza pairs','supports':'Group/stage structure only; exhaustive species membership was not independently extracted'},
]
for s in sources:
    p=ROOT/s['path']
    if p.exists() and 'sha256' not in s:s['sha256']=sha(p)
comparison_id='22_20251990_East_Coast_of_Scotland_(1991-1995)'
comparison_dir=REGION/'papers/NS-2025/models'/comparison_id
comparison_appendix=comparison_dir/'model_validation/taxon_mapping.xlsx'
comparison = {'model_id':comparison_id,'appendix_path':comparison_appendix.relative_to(ROOT).as_posix(),
              'appendix_present':comparison_appendix.exists(),'reuse_for_selected_model':False,
              'reason':'Different model identity and group inventory. This appendix cannot become an ICES-model mapping.'}
if comparison_appendix.exists():
    comparison['appendix_sha256']=sha(comparison_appendix)
    cw=load_workbook(comparison_appendix,read_only=True,data_only=False)
    comparison['sheets']={s.title:{'max_row':s.max_row,'max_column':s.max_column} for s in cw}
    comparison['first_rows']={s.title:[list(x) for x in list(s.values)[:8]] for s in cw}
    crows=[r for r in list(cw['Taxon mapping'].values)[7:] if r and r[0] is not None]
    comparison['taxon_count']=len(crows)
    comparison['catch_ppr_inputs_match_current_universe']=all(
        any(r['taxon']==c[0] and r['catch_tonnes']==c[2] and math.isclose(r['simple_chain_ppr_tC'],c[3],rel_tol=1e-12,abs_tol=1e-8) for r in rows)
        for c in crows)
    comparison['stored_confidence_summary']=[]
    for category in ['High','Medium','Low','Very low','Unresolved']:
        cgroup=[r for r in crows if r[5]==category]
        ct=math.fsum(r[2] for r in cgroup if number(r[2]))
        pt=math.fsum(r[3] for r in cgroup if number(r[3]))
        comparison['stored_confidence_summary'].append({'confidence':category,'taxa':len(cgroup),'catch_tonnes':ct,'catch_percentage':100*ct/catch_total,'ppr_tC':pt,'ppr_percentage':100*pt/ppr_total})
    comparison['confidence_review_scope']='Read directly from the preserved candidate appendix; not a renewed taxon-by-taxon source reassessment.'
    cw.close()
audit={
 'schema_version':1, 'operation':'report-only full catch-universe audit; no scientific adoption',
 'region_id':'LME_022','selected_model_id':model_id,'reference_year':year,'catch_basis':basis,
 'basis_definition':'Recorded total catch (landings plus discards), used once; no component re-addition',
 'method':'simple trophic chain','carbon_divisor':9,'transfer_efficiency':settings['transfer_efficiency'],
 'source_group_count':len(groups),'source_group_ids':[g['group_seq'] for g in groups],
 'synthetic_import_in_source_count':False,'model_sha256':sha(model_path),'regional_workbook_sha256':wbhash,
 'source_identity_matches_extraction_index':sha(model_path)==json.loads((model_path.parent/'extracted_tables/evidence/evidence_index.json').read_text())['computational_input_identity']['canonical_model_sha256'],
 'mapping_state':'No adopted selected-model mapping exists. Unresolved denotes missing mapping evidence, not a conclusion that biological assignment is impossible.',
 'review_scope_limitation':'No scientific M8/W8 rejection is claimed: no completed selected-model mapping handoff is available. Proposed future assignments require a separately evidenced mapping stage.',
 'tables_row_counts':{f'{k[0]}/{k[1]}':len(v) for k,v in t.items()},
 'totals':{'taxa':len(rows),'positive_catch_taxa':sum(number(r['catch_tonnes']) and r['catch_tonnes']>0 for r in rows),
           'zero_catch_taxa':sum(r['catch_tonnes']==0 for r in rows),'missing_catch_taxa':sum(r['missing_catch'] for r in rows),
           'catch_tonnes':catch_total,'known_simple_chain_ppr_tC':ppr_total,'ppr_total_is_complete':not missing,
           'missing_tl_taxa':sum(r['missing_tl'] for r in rows),'missing_coefficient_taxa':sum(r['missing_coefficient'] for r in rows),
           'unknown_annual_ppr_taxa':len(missing),'unknown_annual_ppr_known_catch_tonnes':missing_catch,
           'unknown_annual_ppr_catch_percentage':100*missing_catch/catch_total},
 'confidence_summary':summary,
 'membership_rules':[{'rule':'No selected-model assignment retained','confidence':'Unresolved','ppr_percentage':100.0,'taxa':len(rows),'not_scientific_M8':True}],
 'allocation_rules':[{'rule':'No selected-model allocation retained','confidence':'Unresolved','ppr_percentage':100.0,'taxa':len(rows),'not_scientific_W8':True}],
 'very_low_decisions':[],'unresolved_taxa':[{'taxon':r['taxon'],'reason':r['unresolved_reason']} for r in rows],
 'checks':{'duplicate_catch_basis_taxa':duplicates,'duplicate_classic_taxa':classic_duplicates,
           'classic_taxa_unmatched_to_universe':sorted(set(classic_index)-{r['taxon'] for r in rows}),
           'catch_component_mismatches':component_deltas,'annual_reconciliation':annual_check,
           'confidence_taxa_sum':sum(r['taxa'] for r in summary),'membership_rules_ppr_sum_pct':100,'allocation_rules_ppr_sum_pct':100},
 'sources':sources,'retained_source_provenance':source_records,'comparison_mapping_availability':comparison,'rows':rows,
}
assert sha(workbook)==wbhash
(OUT/'mapping_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
template={'template_available':(ROOT/'tools/templates/taxon_mapping.xlsx').exists(),
          'layout_authority':'tools/templates/instructions.md: seven columns and separate Sources sheet'}
(OUT/'mapping_template_inspection.json').write_text(json.dumps(template,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'totals':audit['totals'],'annual':annual_check,'comparison':comparison['sheets'],'template':template},indent=2,ensure_ascii=False))
