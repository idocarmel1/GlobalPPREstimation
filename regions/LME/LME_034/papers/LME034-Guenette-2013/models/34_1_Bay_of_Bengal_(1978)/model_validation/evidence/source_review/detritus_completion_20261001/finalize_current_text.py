"""Write the final supporting text for the researcher's manual Word updates."""
import json,sys
import re
from collections import Counter
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
RAW=OUT.parent/'source_restoration_20261001'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import sha

def main():
    config=json.loads((OUT/'refresh_configuration.json').read_text(encoding='utf-8'))
    assert len(config['method_status'])==22 and set(config['method_status'].values())=={'ok'}
    layer=json.loads((OUT/'researcher_completion_layer.json').read_text(encoding='utf-8'))
    source=json.loads((OUT/'table17_source_ledger.json').read_text(encoding='utf-8'))
    if 'max_abs_modeldata_sum_delta' in source:source['raw_reconstruction_max_abs_sum_delta']=source.pop('max_abs_modeldata_sum_delta')
    if 'restorations' in source:source['raw_restoration_changes_from_prior_normalized_input']=source.pop('restorations')
    (OUT/'table17_source_ledger.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    grades={}
    for folder,name in [('GE','GE'),('TE','TE'),('With_Egestion','With Egestion')]:
        report=json.loads((OUT/'direct_diagnostics'/folder/'diagnostic_report.json').read_text(encoding='utf-8'))
        grades[name]={'status':report['status'],'b':report['divergence']['b'],'rho_living':report['divergence']['rho_living']}
    lines=['# Final LME034 diet correction — summary for manual validation-document updates','',
        'Selected model: **34_1_Bay_of_Bengal_(1978)**. The final canonical input preserves the printed Table17 values except the eight explicitly authorized Detritus corrections below. These corrections represent the researcher’s assumption that detritus-feeding cells were omitted from the published table; they are not literal author-reported values. Original printed values, the preceding raw reconstruction and the final researcher input remain separately traceable.','',
        '| Predator group | Printed source diet total | Final Detritus share | Final diet total including Import |',
        '|---|---:|---:|---:|']
    for c in layer['corrections']:
        s=c['predator_seq'];lines.append(f"| {s} {c['predator_name']} | {source['source_sums_exact_decimal_including_import'][str(s)]} | {c['researcher_final_proportion']} | 1 |")
    lines+=['',
        'The pre-existing group40 Meiobenthos→Detritus=1 edit was retained exactly. Source justification is strongest for the benthic/plankton groups: the region2 Detritus shares for Crustaceans=.40, Macrobenthos=.55, Meiobenthos=1 and Zooplankton=.10 exactly equal the missing portions of their region3 counterparts. Regional2 Carangids=.0092, S pelagics=.0084 and SM inv=.0327 provide supporting analogy, but differ from the final residual completions .0095/.0088/.0336. Indian mackerel=.0548 has no paired regional-predator analogue. The full report text and AppendixA3.2 supply no explicit quantitative recovery of these residuals.','',
        'Meiobenthos remains a consumer: Table16 p24 reports TL2, PB9, QB60 and P/Q=.15 for all three regional groups, consistent with the benthic-animal discussion p19. A zero printed diet does not support primary-producer classification. Table17 p26 directly assigns Detritus=1 to the other two meiobenthos groups; p27 and AppendixA3.2 p56 leave group40’s known diet entries zero.','',
        'Groups46 Bigeye tuna,47 Yellowfin tuna and48 Marlins retain their own original predator diets, including Import, with totals .99998/.9996/.99946. Their biological prey rows are explicit zeros on pp25–26 but absent on p27:45 source cells remain unknown, represented by42 canonical-9999 sentinels and3 cells within the unchanged group40 override. Loader zeros do not establish source biological zeros. The named Detritus/Import rows incorrectly numbered46/47 on p27 map to prey49/50; missing biological prey values were not reassigned to those pools.','',
        'ModelData retains the final printed-plus-researcher proportions without renormalizing them. The existing PPRCalculator configuration normalizes a separate copy. The completed eight groups now total1; loading still emits one diet warning for group2 Coastal elasmobranch=.9989 at tolerance .001. Loading does not alter the canonical JSON or original ModelData. All non-diet values, detritus-fate routing and other printed diet values remain unchanged.','',
        'All22 existing methods were refreshed with their retained scientific settings, including75 draws for each MonteCarlo method. The two MC methods initially reached180 seconds and were retried alone with600-second execution allowances; the20 completed method columns were preserved exactly. Native spawned-worker seeds remain unspecified, so MC outputs are new stochastic estimates rather than repetitions of old random draws.','',
        '| Direct diagnostic | Status | Recycling gain b | Living spectral radius |','|---|---|---:|---:|']
    for name,g in grades.items():lines.append(f"| {name} | {g['status']} | {g['b']:.9g} | {g['rho_living']:.9g} |")
    lines+=['',
        'All900 direct SPPR source contributions are finite and nonnegative. TE records structural b=0; this does not establish observed absence of ecosystem recycling. Direct matrix/source-scope sums reconcile with the final SPPR export. The native constructor still derives biomass accumulation and completes detritus EE from .332 to1, so strict computational balance does not establish author-native fidelity or observed accumulation. Method-specific negative-result/budget flags remain recorded for the other formulations. Production eligibility remains false; these are provisional researcher-scenario outputs.','',
        'Catch, ClassicPPR, NPP, mappings and allocation assumptions are preserved exactly in the regional workbook. Central records outside LME034 and the completed region32/36 reviews are protected. Validation DOCX files and notebooks are not edited; the researcher is updating Word manually. The model-folder legacy_ppr.xlsx is a historical migrated result, retained unchanged and explicitly labeled in LEGACY_OUTPUT_PROVENANCE.md; active final coefficients use sppr_source.xlsx.','',
        f"Final canonical SHA256: `{layer['final_canonical_sha256']}`.",
        f"Original PDF SHA256: `{layer['source_sha256']}`.",'',
        'Evidence: [completion layer](researcher_completion_layer.json), [source ledger](table17_source_ledger.json), [loading verification](current_source_verification.json), [all22 run configuration](refresh_configuration.json), [direct/export reconciliation](direct_current_export_reconciliation.json), [regional adoption](regional_adoption.json), [central integration](central_integration.json), [portable evidence index](evidence_index.json).']
    negatives=[i for i in config['issues'] if i['kind']=='negative_sppr']
    lines+=['','Observed symbolic-method limitations:']+[f"- `{i['method']}`: {i['detail']}." for i in negatives]
    lines+=['','TE’s structural b=0 occurs because that formulation has no detritus recycling matrix and writes mortality-derived SPPR off as lost, as captured in the engine’s health warning. This warning remains recorded despite the direct diagnostic status being OK.']
    summary='\n'.join(lines)+'\n'
    summary=re.sub(r'\b(group|region|Table|AppendixA)(\d)',r'\1 \2',summary)
    summary=re.sub(r'\b(all|All|the|The|including|by|for|and|with)(\d)',r'\1 \2',summary)
    summary=re.sub(r'\b(\d+)(source|draws|methods|cells|MonteCarlo|seconds|canonical|consumer|complete|printed|scope)',r'\1 \2',summary)
    summary=summary.replace('MonteCarlo','Monte Carlo')
    (OUT/'handoff_summary.md').write_text(summary,encoding='utf-8')
    (OUT/'README.md').write_text('# Final researcher Detritus completion —1October2026\n\nThis folder is the final adopted scenario and supersedes the preceding raw-only reconstruction stage. The source PDF and original printed values remain unchanged.\n\nSee [manual-document summary](handoff_summary.md) for all source → raw → researcher final → runtime distinctions and current evidence links. No validation DOCX or notebook is edited.\n',encoding='utf-8')
    findings=('Final LME034 source/diet findings —1October2026\n\n'+summary.replace('# Final LME034 diet correction — summary for manual validation-document updates','Final adopted researcher scenario'))
    (OUT/'source_findings.txt').write_text(findings,encoding='utf-8')
    (OUT.parent/'source_diagnostics/source_findings.txt').write_text('Current final scenario supersedes the historical raw-only audit.\n\nSee ../detritus_completion_20261001/source_findings.txt, source_audit.json, researcher_completion_layer.json and handoff_summary.md.\n\nThe source_diagnostics/source_audit.json and direct-return folders retain their historical raw-only identities. Canonical JSON now contains the explicit final researcher Detritus completions. No validation DOCX or notebook was edited.\n',encoding='utf-8')
    (OUT.parent/'source_review.md').write_text('# LME034 current source review\n\nThe final adopted scenario is documented in [the manual-document summary](detritus_completion_20261001/handoff_summary.md). The canonical model preserves original printed values except eight explicit researcher Detritus corrections; source, raw reconstruction, final researcher input and separately normalized runtime remain distinct. All22 methods have been refreshed. Direct GE/TE/With Egestion diagnostics are OK, while method-specific issues and source-fidelity limitations remain explicit. Production eligibility remains false. Validation DOCX files and notebooks are untouched.\n\nThe preceding [raw-only source restoration](source_restoration_20261001/README.md) is retained historical evidence, superseded by the final completion scenario.\n',encoding='utf-8')
    profile=ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/MODEL_PROFILE.md'
    text=profile.read_text(encoding='utf-8');parts=text.split('\n\n')
    for i,p in enumerate(parts):
        if p.startswith('Diet provenance ('):
            parts[i]='Diet provenance (final1October2026): canonical JSON preserves printed Table17 values except explicit researcher Detritus completions30=.0548,32=.0095,33=.0088,36=.0336,38=.40,39=.55,40=1 retained,41=.10. Original source values and the prior raw reconstruction remain separately recorded. All completed groups total1; PPRCalculator separately normalizes its own copy and still warns for group2=.9989. Biological prey46–48 omissions remain45 source unknowns, not biological zeros. Their own predator diets are retained. Full final evidence and source justification: ../../validation_reports/34_1_Bay_of_Bengal_(1978)/detritus_completion_20261001/handoff_summary.md.'
    parts=[p for p in parts if not p.lstrip().startswith('Historical workbook:')]
    profile.write_text('\n\n'.join(parts).rstrip(),encoding='utf-8')
    with profile.open('a',encoding='utf-8') as f:f.write('\n\nHistorical workbook: legacy_ppr.xlsx is retained previous generated output, not the active final coefficient source. See [explicit provenance](LEGACY_OUTPUT_PROVENANCE.md); current scientific outputs use sppr_source.xlsx.\n')
    reports=(OUT.parent/'reports_index.md').read_text(encoding='utf-8')
    if reports.startswith('# Final researcher diet completion'):reports=reports.split('\n\n---\n\n',1)[1]
    (OUT.parent/'reports_index.md').write_text('# Final researcher diet completion —1October2026\n\nCurrent model, scientific outputs and shared pages use the explicit eight-group Detritus completions. See the [manual-document summary](detritus_completion_20261001/handoff_summary.md), [completion layer](detritus_completion_20261001/researcher_completion_layer.json), [all22 methods](detritus_completion_20261001/refresh_configuration.json) and [current evidence index](detritus_completion_20261001/evidence_index.json). Older releases below preserve historical input hashes, returns and review context. User validation DOCX and notebooks remain under researcher editing.\n\n---\n\n'+reports,encoding='utf-8')
    info={'canonical_sha256':sha(ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json'),'direct_grades':grades,
        'all22_execution_status':config['method_status'],'issue_kinds':dict(Counter(i['kind'] for i in config['issues'])),
        'all_eight_researcher_completion_totals_one':True,'validation_docx_and_notebooks_written':False,
        'summary':'handoff_summary.md'}
    (OUT/'final_summary.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(info),flush=True)

if __name__=='__main__':main()
