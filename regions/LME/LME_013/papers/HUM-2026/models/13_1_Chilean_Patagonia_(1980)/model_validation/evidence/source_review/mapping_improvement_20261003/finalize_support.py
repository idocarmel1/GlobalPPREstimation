from pathlib import Path
import json,sys,hashlib
sys.stdout.reconfigure(encoding='utf-8');OUT=Path(__file__).parent
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def save(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def plain(s):return s.replace('W9Medium','a biomass proxy with Medium allocation confidence').replace('sourceSmall pelagic fish','the source Small pelagic fish pool')
ledger=load('decision_ledger.json');review=load('reconciled_decisions.json');updates=load('appendix_updates.json')
for r in ledger:
    r['appendix_reason']=plain(r['appendix_reason']);review[r['taxon']]['appendix_reason']=r['appendix_reason']
for a,s in updates['Taxon mapping'].items():
    if a.startswith('G'):updates['Taxon mapping'][a]=plain(s)
save('decision_ledger.json',ledger);save('reconciled_decisions.json',review);save('appendix_updates.json',updates)
summary=load('comparison_summary.json')
coverage={'mapped_labels':218,'all_labels':218,'mapped_label_percentage':100.0,'mapped_2019_landings_percentage':100.0,'classic_coefficient_available_labels':184,'classic_coefficient_label_percentage':100*184/218,'missing_classic_coefficients':34,'classic_coefficient_covered_2019_landings_percentage':100.0,'known_annual_simple_chain_contribution_labels':218,'missing_coefficients_all_zero_2019_landings':True,'ecological_validity_inferred_from_coverage':False}
summary['coverage']={'baseline':coverage,'revised':coverage}
summary['regional_2019_carbon_comparison']=[dict(scope=r['scope'],method=r['method'],basis=r['basis'],unidentified=r['unidentified'],baseline_tC=r['baseline']/9 if r['baseline'] is not None else None,revised_tC=r['revised']/9 if r['revised'] is not None else None,conversion='Saved regional PPR is wet tonnes; divide by 9 once here.') for r in summary['regional_2019_comparison'] if r['metric']=='ppr' and r['basis']=='landings' and r['unidentified']=='method']
summary['shared_update']='This task has not written Project, map, trends, archive or knowledge graph; LME_013 shared integration is deferred and no researcher approval is registered. Concurrent shared-file changes since baseline are separately recorded.'
summary['concurrent_shared_file_notice']='concurrent_protected_file_changes.json'
summary['decision_change_partition']={'numerical':sum(r['numerical_mapping_changed'] for r in ledger),'confidence_only':sum(r['confidence_changed'] and not r['numerical_mapping_changed'] for r in ledger),'rule_only':sum(r['rules_changed'] and not r['numerical_mapping_changed'] and not r['confidence_changed'] for r in ledger),'retained':sum(not any([r['numerical_mapping_changed'],r['confidence_changed'],r['rules_changed']]) for r in ledger)}
save('comparison_summary.json',summary)
print(json.dumps(summary['decision_change_partition'],indent=2))
