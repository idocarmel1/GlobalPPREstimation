"""Report-only aggregation of completed verified evidence; no scientific engine."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True
QA=Path(__file__).resolve().parent
ROOT=next(p for p in QA.parents if (p/'Project.xlsx').exists())
I=ROOT/'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991'
S=ROOT/'regions/LME/LME_022/papers/NS-2025/models/22_20251990_East_Coast_of_Scotland_(1991-1995)'
P=I/'results/diagnostics/2026-11-14_193500_pooled_detritus'
F=S/'results/diagnostics/2026-11-14_184500_ee_floor_on_control'
REPORT=I/'model_validation'
HASHES={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):HASHES[p]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
def close(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-7)
def reference(p):return {'path_from_handoff':os.path.relpath(p,QA).replace('\\','/'),'path_from_report_directory':os.path.relpath(p,REPORT).replace('\\','/'),'path_from_repository':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}

def main():
    comparison=read(QA/'model_comparison_ge_te.json')
    diagnostic=read(QA/'diagnostic_review.json')
    pooled_mapping=read(QA/'pooled_detritus_mapping_comparability.json')
    pooled=read(P/'qa/comparison_summary.json')
    floor=read(F/'qa/comparison_summary.json')
    imapping=read(I/'model_validation/evidence/mapping/mapping_decisions.json')
    smapping=read(S/'model_validation/evidence/source_review/taxon_audit.json')
    common=set(comparison['common_support_taxa']);assert len(common)==372
    scope_analysis=read(QA/'ices_recommendation_scope_analysis.json')
    data={
        'ICES_primary':read(P/'outputs/control_never_2019_ppr.json'),
        'ICES_pooled_sensitivity':read(P/'outputs/pooled_always_2019_ppr.json'),
        'Scotland_OFF_sensitivity':read(F/'outputs/control_off_2019_ppr.json'),
        'Scotland_ON_sensitivity':read(F/'outputs/ee_floor_on_2019_ppr.json')}
    cases=[]
    for key,raw in data.items():
        is_ices=key.startswith('ICES');is_pool=key=='ICES_pooled_sensitivity'
        on=key!='Scotland_OFF_sensitivity'
        name={'ICES_primary':'ICES: separate detritus pools, EE floor ON0.1 (primary)',
            'ICES_pooled_sensitivity':'ICES: shared detritus scaling, EE floor ON0.1 (sensitivity)',
            'Scotland_OFF_sensitivity':'Scotland: corrected reviewed runtime, EE floor OFF (sensitivity)',
            'Scotland_ON_sensitivity':'Scotland: same corrected runtime, EE floor ON0.1 (sensitivity)'}[key]
        row_by_taxon={r['taxon']:r for r in raw['rows']};assert common<=set(row_by_taxon)
        mapped=[r for r in raw['rows'] if is_ices or r['mapping_resolved']]
        assert close(sum(row_by_taxon[t]['catch_tonnes'] for t in common),comparison['common_catch_tonnes'])
        methods={}
        for method in ('GE','TE'):
            if is_ices:
                d=pooled['diagnostics'][('pooled_always' if is_pool else 'control_never')+'_'+method]
                grade=d['status'];model_balance=d['strict_model_balanced'];sppr_balance=d['strict_SPPR_balanced']
                dref=P/f'outputs/{"pooled_always" if is_pool else "control_never"}_{method}.json'
            else:
                d=floor['diagnostic_summary'][('ee_floor_on' if on else 'control_off')+'_'+method]
                grade=d['status'];model_balance=d['strict_model_balanced'];sppr_balance=d['strict_sppr_balanced']
                dref=F/f'outputs/{"ee_floor_on" if on else "control_off"}_{method}.json'
            scopes={}
            for scope in ('all','PP'):
                selected=[row_by_taxon[t] for t in comparison['common_support_taxa']]
                total=sum(r['methods'][method][scope]['ppr_tC'] for r in selected)
                full=sum(r['methods'][method][scope]['ppr_tC'] for r in mapped)
                if key=='ICES_primary':expected=comparison['cases']['ICES_floor_ON']['new_GE' if method=='GE' else 'new_TE_EEfix'][scope]['common_catch_ppr_tC']
                elif key=='ICES_pooled_sensitivity':expected=pooled_mapping['pooled_totals'][method][scope]['common372_tC']
                else:expected=comparison['cases']['Scotland_ee_floor_on' if on else 'Scotland_historical_floor_OFF'][method][scope]['common_catch_ppr_tC']
                assert close(total,expected),(key,method,scope,total,expected)
                exposure={}
                for support,rows in [('common372',selected),('all_mapped',mapped)]:
                    den=sum(r['methods'][method][scope]['ppr_tC'] for r in rows)
                    by=defaultdict(float)
                    for r in rows:by[r.get('overall_confidence',r.get('confidence'))]+=r['methods'][method][scope]['ppr_tC']
                    exposure[support]={'denominator_tC':den,'ppr_tC_by_overall_confidence':dict(by),'percent_by_overall_confidence':{k:v/den*100 for k,v in by.items()}}
                scopes[scope]={'common372_tC':expected,'common372_MtC':expected/1e6,'full_mapped_tC':full,'confidence_exposure':exposure}
            methods[method]={'grade':grade,'strict_model_balanced':model_balance,'strict_SPPR_balanced':sppr_balance,
                'rho_living':d['rho_living'],'original_coupled_b':d.get('diagnostic_b_original_coupled_rho_B',d.get('b')),
                'pooled_b':d.get('pooling_info',{}).get('collapse_b'),'shared_detritus_SPPR':d.get('pooling_info',{}).get('collapse_scalar'),
                'warnings':d['warnings'],'scopes':scopes,'direct_return':reference(dref)}
        cases.append({'case_id':key,'label':name,'role':'primary' if key=='ICES_primary' else 'sensitivity',
            'model_id':I.name if is_ices else S.name,'EE_floor_ON':on,'ee_floor':.1,'methods':methods,
            'common_support_taxa':372,'model_mapped_taxa':len(mapped),'mapping_remains_current_frozen_evidence':True})
    source_notes={
        'preferred_primary':'ICES with separate DOM, sediment POM and Discards and EE floor ON0.1 is the user-selected primary model. Its declared North Sea domain better matches LME_022, and keeping distinct detritus costs preserves the source compartment structure and avoids adding the common-cost assumption.',
        'source_port_limitation':'This is the published North Sea Rpath port snapshot. It materially differs from the accepted native ICES EwE Key Run, whose database was not obtained; native numerical equivalence is not established. Better geographic coverage and closed runtime budgets do not resolve this source-version limitation.',
        'geography':'The declared IVa-IVb-IVc footprint covers approximately87% of LME_022, compared with approximately40% for East Coast Scotland (37–42% source-map sensitivity). These are boundary interpretations, not statistical confidence intervals or recovered native grids.',
        'time_transfer':'ICES static1991 and Scotland1991–1995 coefficients are applied to2019 catch. This is a historical-model transfer comparison, not an independently fitted2019 ecosystem reconstruction.',
        'source_scopes':'All-source sums the returned PP, detritus and synthetic-import columns. PP-only is the within-model primary-producer column contribution and is a component of all-source, not an alternative full-budget total. Do not label all-source as purely photosynthetic production demand or conclude that ICES is lower/higher without stating the scope.',
        'pooling':'The supported always-collapse option calculates one shared detritus SPPR a/(1-b) for DOM67, POM68 and Discards69. It retains all70 runtime IDs, diets, fate routing and internal discard returns. It neither merges the canonical groups nor assumes a simple average of their former coefficients. Treat it as a common-cost sensitivity.',
        'floor':'EE floor0.1 is a hypothetical nonfishery mortality-export assumption applied after audited initialization, with effective detritus stock closure and operational detritus EE1. It is not a source correction or renewed researcher approval.',
        'diagnostics':'All four cases pass strict model mass-balance and SPPR-budget checks. ICES GE/TE remain WARN: the separate diet-normalization check fails at max deviation8.32503e-5; GE detritus feedback remains high, and TE has five near-zero-efficiency groups. Do not describe strict model balance as false because a separate diet check warns.',
        'confidence':'Confidence exposure here weights existing overall mapping categories by the same method-specific PPR denominator. It is not a probability or confidence interval. Scotland’s coarser groups have fewer stage splits; its larger High share does not establish whole-North-Sea applicability or superior source equivalence.',
        'scotland_structure':'Scotland has one detritus pool and no explicit internal-discard return matrix, whereas ICES retains separate coupled detritus and source-backed catch returns. Scotland’s historical TE b0 is a no-recycling convention and is not comparable to the ICES coupled rho_B.',
        'settings_comparability':'The fresh Scotland floorON/OFF controls use the same frozen38cb75d engine as ICES; OFF SPPR/A/L exactly reproduce the historical corrected matrices. Historical engine-version confounding has therefore been checked, while model structure, source-specific initialization, geography and mappings still differ.',
        'scotland_signature':'The preserved Scotland review says MODEL VALIDATED, Ido Carmel14/11/2026, and excludes Seabirds, Seals and Cetaceans, all due to GE<0.01. No current mapped catch uses those recipients, so applying these exclusions removes0regional catch/PPR. The trophic nodes remain; this is not a post-exclusion network solve and the signature does not approve the new floorON sensitivity.',
        'coverage':'Common support is372taxa and2,717,197.2863294235t catch. ICES maps all384taxa and2,717,260.6982051707t. Scotland has12unresolved labels,8with positive catch totaling63.4118757471t; their model PPR stays unknown. Zero-catch unresolved labels have annual contribution0 but unknown coefficients.',
        'decision_scope':'Local primary-model choice is separate from researcher signature, mapping adoption and central publication. Project.xlsx, map and trends updates remain deferred by the user; this evidence handoff performs none of those actions.'}
    prose_spacing={'ON0.1':'ON at 0.1','approximately87%':'approximately 87%','approximately40%':'approximately 40%',
        'static1991':'static 1991','Scotland1991':'Scotland 1991','to2019':'to 2019','fitted2019':'fitted 2019',
        'DOM67':'DOM (67)','POM68':'POM (68)','Discards69':'Discards (69)','all70':'all 70',
        'EE floor0.1':'EE floor 0.1','EE1':'EE = 1','deviation8.32503e-5':'deviation 8.32503e-5',
        'TE b0':'TE b = 0','floorON/OFF':'floor ON/OFF','frozen38cb75d':'frozen 38cb75d',
        'Carmel14/11/2026':'Carmel, 14/11/2026','GE<0.01':'GE < 0.01','removes0regional':'removes zero regional',
        'new floorON':'new floor ON','is372taxa and2,717,197.2863294235t':'is 372 taxa and 2,717,197.2863294235 t',
        'all384taxa and2,717,260.6982051707t':'all 384 taxa and 2,717,260.6982051707 t',
        'has12unresolved labels,8with':'has 12 unresolved labels, 8 with','totaling63.4118757471t':'totaling 63.4118757471 t',
        'contribution0':'contribution zero'}
    for old,new in prose_spacing.items():
        source_notes={key:value.replace(old,new) for key,value in source_notes.items()}
        for case in cases:case['label']=case['label'].replace(old,new)
    case_map={c['case_id']:c for c in cases}
    effects={}
    for label,a,b in [('ICES_pooling','ICES_primary','ICES_pooled_sensitivity'),('Scotland_floor','Scotland_OFF_sensitivity','Scotland_ON_sensitivity')]:
        effects[label]={}
        for method in ('GE','TE'):
            effects[label][method]={}
            for scope in ('all','PP'):
                before=case_map[a]['methods'][method]['scopes'][scope]['common372_tC'];after=case_map[b]['methods'][method]['scopes'][scope]['common372_tC']
                effects[label][method][scope]={'before_tC':before,'after_tC':after,'difference_tC':after-before,'difference_percent':(after/before-1)*100}
    artifacts=[QA/'model_comparison_ge_te.json',QA/'pooled_detritus_mapping_comparability.json',QA/'pooled_detritus_source_contributions.json',
        QA/'diagnostic_review.json',QA/'ices_recommendation_scope_analysis.json',P/'evidence_index.json',P/'qa/independent_pooled_review.json',
        F/'evidence_index.json',F/'qa/independent_ee_floor_review.json',I/'results/diagnostics/2026-11-14_loader_repair/run_manifest.json',
        I/'model_notes.md',I/'model_validation/evidence/geography/source_area_passage.txt',S/'model_validation/validation.docx']
    report={'schema_version':1,'created_at_utc':datetime.now(timezone.utc).isoformat(),'operation':'Saved-evidence report aggregation only; no solver, workbook or report writes',
        'primary_decision':'User chooses ICES separate detritus, EE floor ON0.1; local selection verified by separate owner',
        'year':2019,'catch_basis':'catch = landings plus discards','units':'tonnes carbon/year; displayed MtC divides by1e6',
        'formula':'sum(catch_tonnes * sum(mapping_weight * scope_SPPR_wet)) /9 exactly once',
        'common372_catch_tonnes':comparison['common_catch_tonnes'],'full384_catch_tonnes':comparison['total_catch_tonnes'],
        'common_support_taxa':comparison['common_support_taxa'],'cases':cases,'effects_on_common372':effects,
        'report_ready_prose':source_notes,'source_context':diagnostic['ices']['source_context'],
        'geography':{'ICES':diagnostic['ices']['geography'],'Scotland':diagnostic['scotland']['geography']},
        'mapping_counts':{'ICES':dict(Counter(r['overall_confidence'] for r in imapping['rows'])),'Scotland':dict(Counter(r['overall_confidence'] for r in smapping))},
        'ICES_full384_assumed_allocation_exposure':{r['method']:{scope:r['scopes'][scope]['allocation_assumed_percent'] for scope in ('all','PP')} for r in scope_analysis['methods']},
        'narrative_corrections_to_older_evidence':['Do not repeat earlier no-common-engine caveat as unresolved: new same-engine ScotlandOFF control exactly matches historical matrices.',
            'Both strict balance flags are true in latest ICES and Scotland cases; ICES diet-row normalization is a distinct failed check.',
            'Execution status ok is not diagnostic grade OK: ICES GE/TE are WARN.',
            'Pooling preserves group IDs and routing; shared-cost scalar differs from original coupled diagnostic b.',
            'Confidence shares must name their PPR method/scope and full384 versus common372 denominator.'],
        'artifacts':[reference(p) for p in artifacts],
        'report_link_base':'ICES model_validation directory; use path_from_report_directory for links from validation.docx',
        'source_inputs_unchanged':all(sha(p)==v for p,v in HASHES.items())}
    assert report['source_inputs_unchanged']
    out=QA/'report_comparison_handoff.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'path':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'cases':[{'id':c['case_id'],'GE_all_tC':c['methods']['GE']['scopes']['all']['common372_tC'],'TE_all_tC':c['methods']['TE']['scopes']['all']['common372_tC']} for c in cases]},ensure_ascii=False))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
