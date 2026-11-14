from pathlib import Path
import json,hashlib,math,sys,collections
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
RUN=Path(__file__).resolve().parents[1];BASE=RUN.parents[1]
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.validation_percentage_format import format_percent
source=BASE/'evidence/mapping/mapping_decisions.json'
data=json.loads(source.read_text(encoding='utf8'));rows=data['rows']
assert len(rows)==384 and len({r['taxon'] for r in rows})==384
catch=math.fsum(r['catch_tonnes'] for r in rows)
ppr=math.fsum(r['simple_chain_ppr_tC'] for r in rows if r['simple_chain_ppr_tC'] is not None)
assert math.isclose(catch,data['totals']['catch_tonnes'],rel_tol=1e-12)
assert math.isclose(ppr,data['totals']['simple_chain_ppr_tC'],rel_tol=1e-12)
levels=['High','Medium','Low','Very low','Unresolved']
by={v:[r for r in rows if r['overall_confidence']==v] for v in levels}
confidence=[]
for v in levels:
    cp=100*math.fsum(r['catch_tonnes'] for r in by[v])/catch
    pp=100*math.fsum(r['simple_chain_ppr_tC'] or 0 for r in by[v])/ppr
    given=next(s for s in data['confidence_counts_shares'] if s['confidence']==v)
    assert given['taxa']==len(by[v]) and math.isclose(cp,given['catch_percent'],abs_tol=1e-9) and math.isclose(pp,given['ppr_percent'],abs_tol=1e-9)
    confidence.append([v,str(len(by[v])),format_percent(cp),format_percent(pp)])
rule_rows={}
for component in ['membership','allocation']:
    result=[]
    for item in sorted(data[component+'_rule_summaries'],key=lambda q:-q['ppr_percent']):
        matches=[r for r in rows if r[component+'_rule']==item['rule'] and r[component+'_confidence']==item['confidence']]
        share=100*math.fsum(r['simple_chain_ppr_tC'] or 0 for r in matches)/ppr
        assert len(matches)==item['taxa'] and math.isclose(share,item['ppr_percent'],abs_tol=1e-9)
        result.append([item['plain_language_rule'],item['confidence'],format_percent(share)])
    assert math.isclose(sum(x['ppr_percent'] for x in data[component+'_rule_summaries']),100,abs_tol=1e-8)
    rule_rows[component]=result
vl=[];seen=[]
for group in data['very_low_decisions']:
    taxa=group['taxa'];seen.extend(taxa)
    for start in range(0,len(taxa),10):vl.append(['; '.join(taxa[start:start+10]),group['reason']])
assert sorted(seen)==sorted(r['taxon'] for r in by['Very low']) and len(seen)==len(set(seen))
vlrow=confidence[3]
unresolved='Unresolved taxa: none.' if not by['Unresolved'] else 'Unresolved taxa: '+'; '.join(r['taxon']+' — '+str(r['unresolved_reason']) for r in by['Unresolved'])+'.'
mapping_summary='384 assessed labels: '+', '.join(f'{len(by[v])} {v}' for v in levels)+'. '+f'Proposed Very low decisions account for {vlrow[3]} of simple-chain PPR. Mappings are available for review and remain unadopted.'
result={
 'mapping_decisions_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'reference':'Reference: 2019 total catch (landings plus discards); all recorded catch labels, including zero-catch labels.',
 'comparison_mapping':mapping_summary,
 'confidence_rows':confidence,
 'membership_rule_rows':rule_rows['membership'],
 'allocation_rule_rows':rule_rows['allocation'],
 'membership_evidence':'Membership evidence: focal ICES group definitions, explicitly linked predecessor definitions and catch crosswalk, provider reporting scope, and taxonomic/ecological evidence. Predecessor transfers and conflicting placements retain their own confidence.',
 'allocation_evidence':'Weights and assumptions: single groups receive the full taxon catch. Splits use the exact 1991 model total-catch proportions, including discards, as a fixed proxy for 2019. Stage cutoffs, pooled-species mixtures and spatial/temporal transfers remain assumptions; source quantities and search outcomes are linked in the appendix.',
 'uncertainty':f'{unresolved} {len(by["Very low"])} Very low decisions account for {vlrow[2]} of catch and {vlrow[3]} of simple-chain PPR. These broad-category and analogue placements provide explicit proposals rather than evidence that the source model represents every taxon well.',
 'very_low_rows':vl,
 'mapping_evidence_target':'evidence/mapping/mapping_decisions.json'
}
exposure_path=RUN/'qa/proposed_mapping_method_exposure.json'
if exposure_path.exists():
    exposure=json.loads(exposure_path.read_text(encoding='utf8'))
    assert exposure['mapping_sha256']==result['mapping_decisions_sha256']
    percentages={m['method']:format_percent(m['confidence_ppr_shares']['Very low']) for m in exposure['methods']}
    result['uncertainty']+=f' With the proposed weights, their share of 2019 all-source PPR is {percentages["new_GE"]} for GE and {percentages["new_TE_EEfix"]} for TE.'
(RUN/'outputs/report_mapping_content.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'mapping_sha256':result['mapping_decisions_sha256'],'confidence_rows':confidence,'rule_rows':{k:len(v) for k,v in rule_rows.items()},'very_low_table_rows':len(vl),'denominators':{'catch':catch,'ppr':ppr}},indent=2))
