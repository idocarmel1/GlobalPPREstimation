"""Retain the completed native/diagnostic evidence; never run scientific methods."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, shutil, sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
RUN = ROOT/'regions/LME/LME_002/work/2026-11-14_191000_native_balance_diagnostics'
PAPER = ROOT/'regions/LME/LME_002/papers/GOA-2020'
PARENT = PAPER/'models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49'
MODEL = PAPER/'models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance'
EV = MODEL/'extracted_tables/evidence'
DIAG = MODEL/'results/diagnostics'
sys.stdout.reconfigure(encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p, v):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def rel(p,base): return os.path.relpath(p,base).replace('\\','/')
copies=[]
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    assert sha(src)==sha(dst)
    copies.append({'source':rel(src,ROOT),'retained':rel(dst,ROOT),'sha256':sha(dst)})

summary=read(RUN/'outputs/diagnostics/diagnostic_summary.json')
independent=read(RUN/'qa/independent_diagnostics_review.json')
assert independent['status']=='PASS' and independent['artifact_qa_issue_count']==0
assert summary['status']=='diagnostics_completed'
assert all(v['reload_matches'] and v['initial_status']==v['reload_status']=='returned' for v in summary['methods'].values())
assert sha(PARENT/'model.json')=='10dfbf57dcc9c1ca2e57460637709a061c9264a7e29bf17e0028fadf4c919125'
assert sha(MODEL/'model.json')=='7d805cb293dc4b1886bd8f57f1f122595a298c129824a6cc1a9eb0cbe3244a32'
assert (EV/'native_reproduction').is_dir()
for p in (RUN/'outputs/diagnostics').rglob('*'):
    if p.is_file(): copy(p,DIAG/p.relative_to(RUN/'outputs/diagnostics'))
for name in ('diagnostic_budget_decomposition.json','DIAGNOSTIC_INTERPRETATION.md','independent_diagnostics_review.json'):
    copy(RUN/'qa'/name,DIAG/name)
for name in ('run_scope.json',): copy(RUN/'qa'/name,EV/name)
for p in (RUN/'code').glob('*.py'):
    if p.name in ('build_variant.py','finalize_handoff.py') or p.name.startswith('check_diagnostics'):
        copy(p,EV/'reproduction_code'/p.name)
conversion=read(EV/'variant_conversion.json')
for tool in conversion['tools']:
    p=ROOT/tool['script']; assert sha(p)==tool['sha256']
    copy(p,EV/'reproduction_code'/p.name)

source_manifest=read(PAPER/'source_manifest.json')
manifest_before=sha(PAPER/'source_manifest.json')
if MODEL.name not in source_manifest['models']: source_manifest['models'].append(MODEL.name)
source_manifest['native_reproduction']={
    'date':'2026-11-14','model_id':MODEL.name,
    'evidence':rel(EV/'native_reproduction',PAPER),
    'archived_rda_csv_equality':'Model, diet and pedigree identical at tolerance zero, including attributes.',
    'scope':'Computational completion and direct diagnostics; no regional selection or publication.'}
dump(PAPER/'source_manifest.json',source_manifest)
parent_notes=PARENT/'model_notes.md'
notes_before=sha(parent_notes)
old=parent_notes.read_text(encoding='utf-8')
old=old.replace('The RDA file is archived, not independently decoded.', 'At initial extraction the RDA file was archived but not independently decoded; the dated native reproduction follow-up below records the subsequent verification.')
marker='## Native reproduction follow-up — 2026-11-14'
if marker not in old:
    old += '\n'+marker+'\n\nThe official Rpath balance has now been reproduced in a [separate computational variant](../'+MODEL.name+'/model_notes.md). The archived RDA model, diet and pedigree match the native CSV reader objects exactly. The raw extraction and its unknown values remain unchanged. All three direct PPR methods returned FAIL in the current translation; see the variant results for the detritus accounting explanation. This follow-up does not select or approve either model.\n'
    parent_notes.write_text(old,encoding='utf-8')
index_path=PARENT/'extracted_tables/evidence/evidence_index.json'
index=read(index_path)
for item in index['artifacts']:
    target=(index_path.parent/item.get('path','')).resolve()
    if target in ((PAPER/'source_manifest.json').resolve(),parent_notes.resolve()): item['sha256']=sha(target)
dump(index_path,index)
dump(EV/'metadata_update_receipt.json',{
    'scope':'Local paper discovery and dated parent evidence pointer only; no workbook or map writes.',
    'source_manifest_before':manifest_before,'source_manifest_after':sha(PAPER/'source_manifest.json'),
    'parent_notes_before':notes_before,'parent_notes_after':sha(parent_notes),
    'parent_model_unchanged':sha(PARENT/'model.json')==summary['identity']['parent_sha256']})

provenance={
    'schema_version':1,'kind':'native_equation_computational_completion','parent_model_id':PARENT.name,
    'parent_path':rel(PARENT/'model.json',MODEL/'inputs'),'parent_sha256':sha(PARENT/'model.json'),
    'canonical_sha256':sha(MODEL/'model.json'),
    'native_commit':source_manifest['files'][0]['commit'],
    'native_evidence':rel(EV/'native_reproduction',MODEL/'inputs'),
    'source_and_native_ledger':rel(EV/'native_to_variant_ledger.json',MODEL/'inputs'),
    'diagnostic_identity':rel(DIAG/'run_identity.json',MODEL/'inputs'),
    'restrictions':['Native solved values are not independent source observations.','All three PPR methods returned FAIL; no valid annual estimate.','No model selection, researcher approval, regional catch mapping or map publication.']}
dump(MODEL/'inputs/provenance.json',provenance)

methods={}
for name,v in summary['methods'].items():
    methods[name]={'execution_status':v['initial_status'],'overall_grade':v['overall_grade'],
        'reproduced_from_persisted_input':v['reload_matches'],'annual_eligible':False,
        'full_return':'diagnostics/initial_'+name+'.json','reload_return':'diagnostics/reload_'+name+'.json'}
dump(MODEL/'results/result_manifest.json',{
    'schema_version':1,'unit_id':'LME_002','model_id':MODEL.name,'kind':'direct_diagnostics_only',
    'timestamp':summary['identity']['run_timestamp_utc'],'canonical_model_sha256':sha(MODEL/'model.json'),
    'parent_model_sha256':sha(PARENT/'model.json'),'snapshot_sha256':None,'coefficient_source_sha256':None,
    'effective_flags':{**summary['identity']['constructor'],**summary['identity']['effective_floor']},
    'source_EE_eligibility':'Raw parent source EE is unknown for all 49 groups; no group received the floor.',
    'method_options':summary['identity']['diagnostic_options'],'code_identity':summary['identity']['code_sha256'],
    'methods':methods,'provenance_status':'Fresh, retained direct diagnostic returns; independently checked.',
    'artifacts':{'model':'../model.json','diagnostics':'diagnostics/diagnostic_summary.json','interpretation':'diagnostics/DIAGNOSTIC_INTERPRETATION.md','snapshot':None,'coefficients':None},
    'restrictions':['FAIL methods are diagnostic evidence only.','No regional snapshot, catch-year arithmetic, selection, signoff or publication.']})

notes='''# Gulf of Alaska Rpath49 — native balance computational variant

## Source identity

Whitehouse & Aydin (2020), DOI 10.1016/j.ecolmodel.2020.109074. Official NOAA-EDAB/Rpath Ecosense.GOA inputs at commit fe63f6d370d942ff1786f4d649e432fbfb85f81b. The [raw parameter extraction](../Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49/model_notes.md) remains a separate model. This variant records the native-equation completion, not new observations.

## Modeled period and area

The baseline is 1990–1994 and covers 291,840 km² of Gulf of Alaska shelf and slope. Nearshore waters shallower than 50 m were excluded. Coverage of the complete LME has not been measured. The publication year is not the ecosystem baseline year.

## Departures from the publication

Unmodified, pinned Rpath equations solved 49 EE values, two detritus biomasses and trophic levels, and calculated GE. Native NA-diet-to-zero and missing-detritus-input-to-zero conventions and nonfeeding QB zero placeholders are explicit in the ledger. Known parameters, BA, catch, group identities and fate fractions were preserved without diet normalization, parameter fitting or balancing repair. The comma-free import alias for group 31 is reversible; the canonical name is exact. Raw inputs and missingness remain in the parent model and retained companions.

## Native balance and PPR outcomes

The native system has full rank and all 49 EE values lie between zero and one. The maximum absolute living-group balance residual is 5.68434e-14 t/km²/year. The archived RDA model, diet and pedigree exactly match the CSV reader objects. Independent native and variant verification passed 9,485 checks.

The GE, TE and With Egestion direct PPR diagnostics all returned **FAIL**, reproduced from the persisted variant. Their production-budget gaps are 100.5891%, 75.6690% and 100.4364%, respectively. The current PPR runtime forces detritus EE to one while the native solution leaves unused detritus inputs. The saved-output decomposition accounts for each entire budget gap using those two residuals. Native balance success does not establish PPR validity.

All raw source EE values were unknown. The EE-floor setting was ON at 0.1, with source missingness preserved: zero groups were modified and no external mortality sink was added. Known detritus BA values of zero were preserved. No parameters were repaired to make diagnostics pass.

## Remaining limitations

The PPR translation needs an explicit, source-consistent treatment of native detritus non-consumption before the coefficients can support an accepted annual estimate. GE and TE also warn about near-zero efficiencies; TE produces an especially large coefficient for toothed whales. An accounting correction alone would not establish ecological validity.

The single Primary production group combines local and Outside production; the detritus pools combine external production and fishery returns. Engine labels inner and PP do not recover a geographic partition. These diagnostic outputs cannot establish LME-local PPR/NPP. Candidate taxonomy still needs source review, catch mapping has not been adopted, and current-year extrapolation and study/LME overlap remain unresolved.

## Evidence links

- [Results and accounting interpretation](results/diagnostics/DIAGNOSTIC_INTERPRETATION.md)
- [Full direct diagnostic returns](results/diagnostics/direct_diagnostics.md)
- [Native reproduction](extracted_tables/evidence/native_reproduction/)
- [Native-to-variant ledger](extracted_tables/evidence/native_to_variant_ledger.json)
- [Import round trip](extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json)
- [Portable evidence index](extracted_tables/evidence/evidence_index.json)
- [Reproduction instructions](results/diagnostics/REPRODUCE.md)

The map, regional workbook, model selection and researcher approval were not changed. No annual regional PPR was calculated.
'''
(MODEL/'model_notes.md').write_text(notes,encoding='utf-8')
(DIAG/'REPRODUCE.md').write_text('''# Reproducing this diagnostic package

The immutable `initial_*.json` files contain each actual full four-part return: report, SPPR, A and L. `reload_*.json` are fresh-process replays of the persisted canonical variant. `diagnostic_summary.json` reconciles them; the independent review checks dimensions, masks, scope sums and provenance. Scientific FAIL is a retained result, not an execution error.

Use `run_identity.json` for exact Python/package versions, constructor flags, method options and executed source hashes. The `executed_code/` tree preserves the code bytes under their original repository-relative paths. Restore or verify those bytes before reproduction; do not silently substitute a newer engine. The raw parent EE provenance must be retained because solved EE values are not floor-eligible source measurements.

The original entry point was `regions/LME/LME_002/work/2026-11-14_191000_native_balance_diagnostics/code/run_diagnostics.py`, retained inside `executed_code/`. From the repository root, restore that script to a bounded work directory inside the repository (root discovery follows the script's ancestors) and invoke Python 3.11.9 with:

```text
python <restored-run_diagnostics.py> --parent regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49/model.json --variant regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance/model.json --outdir <new-bounded-work-directory>/diagnostics
```

Each of the three calls and three reproduction calls has a 180-second worker bound. The runner checks source/code identities, constructs without normalization or BA repair, applies the floor once using raw parent eligibility, and retains exact typed arrays and masks. Its path records are historical provenance; inventory paths resolve relative to the retained evidence index.

Native reproduction and its R runtime/package acquisition are documented in [the native evidence directory](../../extracted_tables/evidence/native_reproduction/). Build-variant code and maintained conversion helper bytes are under [reproduction_code](../../extracted_tables/evidence/reproduction_code/). Temporary downloaded runtime binaries and duplicate staging files are not scientific inputs and may be removed after their receipts and outputs are retained.

No forced-balance diagnostic, detritus-loss assumption, parameter repair, catch mapping, annual regional calculation or map update was executed. The accounting decomposition is arithmetic on retained results, not a new solve.
''',encoding='utf-8')
dump(EV/'promotion_receipt.json',{'schema_version':1,'files':copies,'verified':True})
print(json.dumps({'promoted_files':len(copies),'methods':methods,'parent_sha256':sha(PARENT/'model.json'),'variant_sha256':sha(MODEL/'model.json')},indent=2))
