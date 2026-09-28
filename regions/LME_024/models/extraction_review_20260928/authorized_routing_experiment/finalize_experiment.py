from pathlib import Path
import json,pickle,hashlib,subprocess,sys
import numpy as np
import pandas as pd
from routing_adapter import RoutingExperimentCalculator
from run_experiment import OUT,ROOT,read,save,sha

c=pickle.loads((OUT/'faithful_printed_BA_state.pkl').read_bytes())
stored=c._DC.copy();effective=c.get_DC(DET_as_PP=True)
changes=[]
for i in stored.index:
 for j in stored.columns:
  if pd.isna(stored.loc[i,j]) and not pd.isna(effective.loc[i,j]):
   changes.append({'predator_seq':int(i),'prey_seq':int(j),'stored_value':'NaN','runtime_value':float(effective.loc[i,j]),'reason':'Nonfeeding basal group has no diet; structural zero permits native basal identity detection.'})
assert {(x['predator_seq'],x['prey_seq']) for x in changes}=={(51,55),(52,55),(53,55),(54,55)}
effective.to_csv(OUT/'effective_diet_after_basal_convention.csv')
save('basal_structural_zero_convention.json',{'changes':changes,'stored_source_and_runtime_state_unchanged':True,'initial_exception_cause':'NumPy row sum of basal DC rows containing NaN was NaN, so identity rows were not assigned; rank54/nullity1 left only Import55 in the basis. This is not a zero-biomass seabird issue or a column-label typo.','source_zero_biomass_groups':[1,2],'their_loaded_biomass':[float(c._groups_df.loc[i,'biomass']) for i in [1,2]]})
raw={t:read(OUT/f'diagnose_{t.replace(" ","_")}_raw.json') for t in ['GE','TE','With Egestion']}
d=pd.read_csv(OUT/'physical_budget_by_group.csv',index_col=0)
d['relative_P_residual']=abs(d.P_minus_sinks)/d.P.abs().replace(0,np.nan)
worst=d.loc[d.index<=52].sort_values('relative_P_residual',ascending=False).head(8)
worst[['name','P_minus_sinks','relative_P_residual']].to_csv(OUT/'worst_living_production_residuals.csv')
before=read(OUT/'original_hashes_before.json')
after={p:sha(ROOT/p) for p in before}
assert before==after
test=subprocess.run([sys.executable,'-X','utf8',str(OUT/'test_routing_adapter.py')],capture_output=True,text=True)
(OUT/'test_final.log').write_text(test.stdout+test.stderr,encoding='utf8')
assert test.returncode==0
save('verification_final.json',{'source_canonical_normalized_and_shared_engine_unchanged':before==after,'after_hashes':after,'focused_adapter_tests_passed':5,'test_exit_code':test.returncode,'basal_cell_conventions':changes,'all_source_biomass_retained':all(c._groups_df.loc[i,'biomass']==float(read(ROOT/'regions/LME_024/models/Hernvann_2020_Celtic_Sea_1985/model.json')['group'][i-1]['biomass']) for i in range(1,55)),'GE_and_With_Egestion_all_54_groups_no_negative_or_nonfinite_coefficients':all(not read(OUT/f'{s}_negative_audit.json')['negative_totals'] and not read(OUT/f'{s}_negative_audit.json')['negative_contributions'] and read(OUT/f'{s}_negative_audit.json')['nonfinite_contributions']==0 for s in ['GE','With_Egestion'])})
save('RESULTS.json',{'experiment':'Authorized two-pool routing with printed B4 BA retained','experimental_adapter_not_native_validation':True,'model_id':'Hernvann_2020_Celtic_Sea_1985','diagnostic_outcomes':{t:{'status':r['status'],'solve_error':r['divergence']['solve_error'],'recycling_b':r['divergence']['b'],'PP_balance_relative_gap':r['balance']['rel_gap'],'detritus_sppr':r['divergence']['sppr_det']} for t,r in raw.items()},'pool_budgets':read(OUT/'detritus_budgets.json'),'physical_accounting':read(OUT/'physical_accounting_summary.json'),'no_regional_PPR_publication_or_selection':True})
report='''# Authorized routing experiment — Celtic Sea 1985

**The proposed routing can be represented faithfully in an isolated adapter, but it does not make the published model balance.** With the printed biomass-accumulation rates retained, natural Detritus is short by **307.289756** and Discards by **0.0586823505** in the interpreted model flow units (t km⁻² year⁻¹). GE and With Egestion now run and both return **FAIL**. TE returns **FAIL with an explicit unsupported-return-equation error**, rather than a numerical coefficient result.

This is an experimental adapter result, not validation by the unmodified native calculator. No parameter was altered to force a pass. The canonical extraction, normalized source copy, paper, Word supplement and shared engine retain their original hashes. There is no regional estimate, model selection or central registration in this experiment.

## What was tested

Model `Hernvann_2020_Celtic_Sea_1985`: one 1985 Celtic Sea shelf baseline, 54 source groups (50 consumers, two phytoplankton groups, Discards53 and Detritus54). Source area is the shelf shallower than 200 m in ICES7.e/f/g/h/j.2; no numerical area or regional coverage fraction is supplied. The loader adds synthetic dietary Import55.

The authorized normalized diet was used. All fishery removals remain landings + discards in donor mortality. Each B3 discard flow enters Discards53 exactly once; natural mortality and unassimilated consumption enter Detritus54. Donor ancestry is included in the detritus recycling equations and physical-flow matrix. Internal returns are subtracted once when evaluating exports from the full system. No pools are merged. No external gap-filling flow or interpool transfer is invented. The JSON alone cannot encode this full return ledger: the adapter plus `discard_returns_by_donor.csv` are required.

Six missing multistanza PB values (groups9–14) are completed as printed P/Q × Q/B, and the missing Megrim18 EE is derived from normalized predation + catches + accumulation. These are explicit computational completions, not published fitted values. No biomass was missing or filled: both source seabird biomasses remain exactly0.00. The uncertain precision of multistanza estimates and source PQ inconsistencies remain limitations.

## Pool budgets with the printed accumulation rates

| Pool | Natural inflow | Discard return | Consumption removal | Printed BA | Shortfall |
|---|---:|---:|---:|---:|---:|
| Discards53 | 0 | 0.25591040963 | 0.214592760105 | 0.100000 | 0.058682350475 |
| Detritus54 | 2027.472199187 | 0 | 1853.641955082 | 481.120000 | 307.289755896 |

BA is interpreted as the B4 annual rate multiplied by biomass:0.40 ×0.25 for Discards and3.88 ×124 for Detritus. Using the printed B3 discard total0.2559104 instead of the donor-row sum changes the Discards shortfall to0.058682360105; the9.63e−9 difference is source rounding. Residual BA values that would close these individual pools are0.041317649525 and173.830244104412. They are shown only as arithmetic consequences and **were not adopted**.

The complete physical ledger also fails to close: PP + imported food=1887.212003650, external sinks including respiration=2146.107355216, residual=−258.895351566. This total differs from the sum of pool shortfalls because living-group balances are also inconsistent. Largest relative living production residuals are juvenile Cod14 (35.3771%), Carnivores/Necrophages41 (24.7352%), Pilchard31 (20.5827%) and Subsurface deposit feeders43 (19.9685%). Juvenile Cod relies on the explicitly derived PB; the other listed mismatches involve published rates.

## Requested direct diagnostics

Each result is the exact return of `PPRCalculator.diagnose_sppr(adapter, TE_option=..., short=False, flat=False)`. No global method, broad method inventory, Monte Carlo or balanced-model substitution was run.

| Method | Returned outcome | Recycling factor | PP balance gap | Discards / Detritus coefficients |
|---|---|---:|---:|---:|
| GE | FAIL; converges, input and PP balance fail | 0.5201202124 | 30.131275% | 529.292491 / 1.583668 |
| With Egestion | FAIL; converges, input and PP balance fail | 0.7618995011 | 5.173259% | 257.018521 / 3.576448 |
| TE | FAIL; `TE_RETURN_UNSUPPORTED` | unavailable | unavailable | unavailable |

GE and With Egestion have no negative contributions, no negative group totals and no nonfinite coefficients across all54 source groups. Both warn that Discards is extremely expensive. Group4, Toothed cetaceans / Seals, has the largest coefficient:32030.748750 (GE) and12316.172383 (With Egestion). Positive convergent coefficients do not cure the source imbalance. The near-threshold5.17% With Egestion PP gap is insufficient evidence for acceptance: its source production residual still reaches35.38%, and the natural-detritus budget is materially inconsistent.

TE's native detritus expression lacks the donor-return term. The adapter refuses that unsupported coefficient calculation, and the direct diagnostic catches and records it. The full returned TE object is preserved; its null fields must not be interpreted as zero values or a tested numerical TE result. Native footprint fields for GE/With Egestion are retained unchanged as diagnostic outputs; they use gross fishery removals L+D and are not a published regional PPR estimate.

## Loader and basis limitations found

The native initializer imposes detritus self-identity fate, clears printed detritus BA, then solves replacement BA from its natural-flow budget; it has no separate fleet-return term. This experiment restores printed BA and supplies a separate donor-return ledger. Original and reconstructed state tables document every transformation, including conventional zero migration/import defaults, source-sentinel handling, GE recomputation from P/Q, and a synthetic import-group biomass default. The unused auto-generated balanced model was discarded.

Initial GE/With Egestion runs raised `KeyError: [53,54] not found in axis`. This was traced to NaN dietary-import cells in the four nonfeeding basal groups51–54: the native NumPy row-sum test skipped their identity rows, leaving nullity1 and only Import55 as a basis source. This was not caused by the two zero-biomass seabird groups and was not a column-label typo. An isolated runtime convention converts exactly those four nonfeeding import cells to structural zero in the returned diet matrix, preserving stored/source blanks and every consumer diet. Five focused adapter tests pass. The original exceptions and matrix trace remain available alongside the successful diagnostic returns.

## Interpretation and evidence

The source-informed split is ecologically plausible and makes the previously unfed Discards pool traceable to fishery donors. It is a useful reconstruction hypothesis, but the source does not publish a numeric fate matrix and this trial does not establish a balanced model. Resolving the remaining budget and rate discrepancies needs source clarification; changing biomass, pooling detritus, injecting inflow or replacing printed accumulation with residuals would be additional assumptions and was not done.

Main evidence files:

- `diagnose_GE_raw.json`, `diagnose_With_Egestion_raw.json`, `diagnose_TE_raw.json`: complete direct diagnostic returns, with exact pickle counterparts.
- `diagnose_*_execution.json`: call configuration and execution logs; `diagnose_*_initial_basal_exception.json`: original exceptions.
- `detritus_budgets.json`, `physical_budget_by_group.csv`, `physical_accounting_summary.json`: explicit physical accounting.
- `faithful_printed_BA_state.pkl`, `faithful_printed_BA_*`, `effective_diet_after_basal_convention.csv`, `basal_structural_zero_convention.json`: loaded and effective runtime state.
- `native_predefaults_groups.csv`, `native_initializer_*`, `derived_parameters.json`: loader transformations and derived values, separate from source evidence.
- `GE_*`, `With_Egestion_*`: coefficient matrices, group coefficients, recycling systems and negative-value audits.
- `routing_adapter.py`: isolated hooks; based on the documented return-accounting approach in `original_research_archive/research/discard_sensitivity_2026_09_10/src/scenarios.py`. The frozen study's NUMERICAL_NOTES also excludes positive-return TE.
- `verification_final.json`, `test_final.log`, `artifact_hashes.json`: unchanged originals, five passing focused controls and artifact provenance.

The source extraction, visual evidence, eight EwE tables, taxonomy and3628-check round-trip verification remain in the parent review and canonical model folders. They are not replaced by this experiment.
'''
(OUT/'REPORT.md').write_text(report,encoding='utf8')
save('artifact_hashes.json',{str(p.relative_to(OUT)):sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='artifact_hashes.json'})
print(json.dumps({'source_and_engine_hashes_unchanged':before==after,'tests':test.returncode,'outcomes':{t:r['status'] for t,r in raw.items()},'report':str(OUT/'REPORT.md')},indent=2))
