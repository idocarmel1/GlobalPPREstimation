"""Summarize the actual native execution without changing source/model values."""
from pathlib import Path
import csv,hashlib,json,shutil,sys
sys.stdout.reconfigure(encoding='utf-8')
RUN=Path(__file__).resolve().parents[1];OUT=RUN/'outputs/native_balance';QA=RUN/'qa'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(name):return list(csv.DictReader((OUT/name).open(encoding='utf-8',newline='')))
execution=read(QA/'native_execution.json');assert execution['returncode']==0 and execution['all_source_bytes_unchanged']
metrics={x['metric']:float(x['value']) for x in rows('metrics.csv')}
rda=rows('rda_csv_comparison.csv');assert all(x['equal']=='TRUE' for x in rda)
groups=rows('groups.csv');assert len(groups)==49 and len({r['Group'] for r in groups})==49
assert metrics['rank_svd']==metrics['dimension']==47 and metrics['EE_outside_zero_one']==0
assert metrics['nonfinite_group_parameters']==0
report={
 'stage':'native_balance_reproduction','status':'completed_source_faithful_native_execution',
 'source_model_id':'Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49',
 'derived_model_id':'Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance',
 'official_Rpath_commit':execution['official_Rpath_commit'],
 'runtime':{'R':'4.5.1','data.table':'1.18.6.1','MASS':'7.3-65','OS':'Windows 11 x64','locale':'English_United States.utf8','scope':'Sourced official pinned read.rpath.params and rpath functions unchanged; full package and Ecosim simulations not executed'},
 'source_object_identity':{'RDA_model_diet_pedigree_exactly_equal_to_CSV_reader':True,'tolerance':0,'attributes_checked':True},
 'numerical_checks':metrics,
 'native_source_conventions':['1810 NA diet cells become runtime zero, including nonfeeding producer cells; no diet normalization','Living EE solved from fixed source B/PB/QB, diet, catch and BA','Detritus EE is consumption/inflow; detritus biomass is inflow/source PB (0.5 in both pools)','TL is solved by native trophic-level equations','DetInput NA becomes zero in native code; native nonfeeding QB and GE become zero','Source fishery removals remain landings plus discards; fleet discard returns use the native two-pool fractions unchanged'],
 'admissibility':{'all_biological_EE_finite_and_in_0_1':True,'all_living_B_positive':True,'all_exported_group_parameters_finite':True,'rank_unique':True},
 'parameter_modifications':'None to source values; source unknowns completed only by pinned native equations/conventions. No fitted parameter adjustment or normalization.',
 'units':{'Biomass':'t wet weight/km2','PB_QB':'year^-1','Catch_Landings_Discards_BA_DetInput_and_budgets':'t wet weight/km2/year','EE_GE_Unassim_diet_fate':'dimensionless','TL':'trophic level'},
 'matrix_axes':{'diet.csv':'Prey rows (49 biological groups plus Import), predator columns (47 living groups incl nonfeeding Primary production)','detritus_fate.csv':'49 biological donor rows, two exact native detritus-pool destination columns','detritus_fate_with_fleet.csv':'50 donor rows including fleet; last row governs fleet discard return','landings.csv_and_discards.csv':'50 exact native group rows including zero fleet row, one native fleet column','living_A.csv':'47 living group equations by47 unknown livingEE; diagonal source B*PB'},
 'precision':'All numeric CSV fields exported with17significantdigits; native_balanced.rds preserves exact R object and was reopened with identical() true.',
 'warnings':['data.table binary built under R4.5.3, run under R4.5.1; no native balance warnings; independent R formulations agree to reported precision'],
 'setup_issue_resolved':'Inherited LC_ALL=C.UTF-8 is unsupported by Windows R and caused fallback ASCII locale to miss Hebrew library paths. Child-process-only Windows UTF-8 locale fixed this. Prior startup/probe logs retained; no R source or global setting changed.',
 'remaining_limits':['This reproduces the retained official source commit, not the unavailable exact historical2020 software environment','Large raw living equation condition number reflects disparate production scales; diagonal direct-form comparison agrees to2.22e-16 EE','Native balance is not PPR diagnostic validity, researcher approval, regional catch mapping, temporal representativeness or LME boundary suitability','Outside production/detritus were pooled in the aggregate, so local-versus-external production support remains unresolved'],
 'source_bytes_unchanged':True,'map_selection_registry_writes':False,
 'files':[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ('native_summary.json','NATIVE_BALANCE_REPORT.md')]
}
(OUT/'native_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
text=f'''# Native Gulf of Alaska Rpath balance reproduction

The official 49-group Ecosense.GOA parameter set was balanced by the unchanged native reader and Ecopath functions at commit `{execution['official_Rpath_commit']}`. This executed R 4.5.1, data.table 1.18.6.1 and MASS 7.3-65 in an isolated portable runtime; no global R installation was made. The exact archived RDA model, diet and pedigree components agree with the CSV-built parameter object at zero tolerance, including attributes.

The 47 living EE equations have rank 47. The largest absolute living-budget residual is {metrics['max_living_abs_residual']:.6g} t/km²/year; native EE differs from direct per-group division by at most {metrics['max_living_EE_difference']:.6g}. Both detritus budgets and biomass formulas reconcile with zero recorded difference. All 49 EE values are finite and within [0,1], ranging from {metrics['min_EE']:.12g} to {metrics['max_EE']:.12g}. No source-known biological rate, biomass, BA, diet or fishery value was fitted or repaired.

Native Rpath converts 1,810 raw diet NA cells to zero on its runtime copy, computes living and detrital EE, derives both detritus biomasses from inflow and the explicit source turnover 0.5/year, and calculates TL. It preserves the source diet sums rather than normalizing them. Group and matrix exports retain exact native names and order; the full 50-row views retain the fleet. CSV numbers use 17 significant digits, and the exact native R object is retained in `native_balanced.rds` with a successful identical-object reload check.

Natural detrital inputs and fishery discard returns are separated in `detritus_balance_audit.csv`. The source fleet fractions sum to 0.9999999 and are retained without adjustment. Source JSON, CSVs, RDA and pinned R files are byte-for-byte unchanged. The matrix condition number is about {metrics['condition_number']:.6g}, reflecting large differences in production scale; the diagonal direct-equation check provides an independent numerical reconciliation.

The runtime emitted one package-build warning (data.table was compiled under R 4.5.3); the native balance itself emitted no warnings. An initial environment-only startup failure was traced to unsupported inherited `LC_ALL=C.UTF-8`. A child-process Windows UTF-8 locale resolved Hebrew path handling. The failed startup and diagnostic probes are retained in work QA; R equations and global settings were not changed.

This is a native mass-balance result, not a PPR diagnostic or annual regional estimate. The pinned code includes changes after the 2020 publication; the run identifies its actual source commit and environment. The aggregate still combines internal and outside primary production/detritus, and the historical period, geographic overlap, species mapping and researcher approval limitations remain. No map, selection or registry was changed by this stage.

See `native_summary.json`, `metrics.csv`, `living_balance_audit.csv`, `detritus_balance_audit.csv`, `source_runtime_parameter_ledger.csv`, `source_runtime_diet_ledger.csv` and `rda_csv_comparison.csv` for the numerical evidence.
'''
(OUT/'NATIVE_BALANCE_REPORT.md').write_text(text,encoding='utf-8')
print(json.dumps({'status':report['status'],'biological_groups':len(groups),'summary':str((OUT/'native_summary.json').relative_to(RUN)),'max_living_residual':metrics['max_living_abs_residual']},indent=2))
