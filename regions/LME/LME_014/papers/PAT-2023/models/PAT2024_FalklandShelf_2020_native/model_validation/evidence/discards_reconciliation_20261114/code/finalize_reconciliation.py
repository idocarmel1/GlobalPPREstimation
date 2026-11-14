"""Package the completed, model-local reconciliation. No scientific solves or publication."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil

WORK = Path(__file__).resolve().parents[1]
MODEL = WORK.parents[2]
ROOT = next(p for p in MODEL.parents if (p / 'Project.xlsx').exists())
DEST = MODEL / 'model_validation/evidence/discards_reconciliation_20261114'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def relative(p, base=DEST):
    return Path(os.path.relpath(p, base)).as_posix()

def main():
    comp = read(WORK / 'outputs/diagnostics/comparison_summary.json')
    ledger = read(WORK / 'outputs/source/source_fisheries_ledger.json')
    native = read(WORK / 'outputs/source/native_sdk_probe.json')
    qa = read(WORK / 'qa/independent/diagnostic_array_verification.json')
    assert all(comp['checks'].values())
    assert qa['status'] == 'All independent saved-array and input/hash checks passed.', qa['status']
    assert native['loaded'] and native['native_engine_run_performed'] and native['run_return']
    assert native['source_unchanged'] and native.get('failure') is None
    assert sha(MODEL/'model.json') == '9880e521a406974367530ffb06f13392714dba57b9645c38a1b1448926d83d17'
    assert (WORK/'outputs/source/native_probe_verification.json').exists()
    # All computations are complete. Copy only portable evidence and executed code,
    # not native working databases, lock files, caches, or installation assemblies.
    assert not DEST.exists(), 'Destination exists: inspect rather than overwrite an evidence package.'
    for folder in ['code','outputs','qa','inputs/official_ewe_source']:
        for p in (WORK/folder).rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:
                continue
            if p.suffix.lower() not in {'.py','.ps1','.json','.txt','.log','.xml','.vb'}:
                continue
            target = DEST/p.relative_to(WORK)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, target)
    versions = {
        'native_original_saved_version': '6.6.8.18072',
        'native_installer_label': '6.7.0.18865_64-bit',
        'native_executed_assembly_file_version': native['assembly_file_version'],
        'native_executed_assembly_sha256': native['assembly_sha256'],
        'native_probe_executed_script_sha256': sha(WORK/'code/native_sdk_probe.ps1'),
        'native_probe_original_source_unchanged': native['source_unchanged'],
        'native_probe_copy_hash_after_process_exit': sha(WORK/'qa/source/native_sdk_probe.eweaccdb'),
        'native_probe_copy_hash_during_finalizer': 'unavailable: task copy remained locked until native process exited',
        'native_attempts': [
            'Sandboxed script launch rejected before model loading; registry access prevented a complete policy query. No policy changed.',
            'First approved normal invocation stopped before loading on indexed Autosave setter syntax; attempt1 JSON retained.',
            'Second approved invocation stopped before loading on optional get_Version call; attempt2 JSON retained.',
            'Third approved invocation reached native operations but result capture failed on the still-locked task copy; no success claim relies on that attempt.',
            'Final approved invocation loaded and calculated successfully and retained full native results; finalizer recorded the copy-lock limitation without losing results.'
        ],
        'native_log_note': 'Headless logger emitted empty-path messages; native RunEcopath returned true and complete requested arrays were retained. The task copy contains an EwE log. No UI session was used.',
        'public_source_limit': 'Retained official current VB source explains export semantics but is not asserted byte-identical to either historical binary.',
    }
    write(DEST/'qa/native_execution_receipt.json', versions)
    old, new = comp['summaries']
    table=[]
    metrics=[]
    for a,b in zip(old['methods'],new['methods']):
        da,db=a['diagnostic'],b['diagnostic']
        assert a['method']==b['method']
        pa,pb=da['footprint']['ppr_all'],db['footprint']['ppr_all']
        metrics.append({'method':a['method'],'status':db['status'],'control_ppr_all':pa,'source_return_ppr_all':pb,
                        'relative_change_percent':100*(pb/pa-1),'strict_balance':db['balance']['is_balanced'],
                        'strict_relative_gap':db['balance']['rel_gap'],'b_control':da['divergence']['b'],
                        'b_with_returns':db['divergence']['b']})
        table.append(f"| {a['method']} | {pa:.10f} | {pb:.10f} | {100*(pb/pa-1):+.4f}% | {db['status']} |")
    report = f'''# LME_014 Discards reconciliation

The focused GE/TE checks are complete with EE floor **ON, 0.1**. Restoring the native fleet returns changes PPR slightly and leaves the Discards (35) deficit unchanged. The original Ecopath database already contains that deficit as a **negative calculated Export**; the reconstruction expresses it as negative detritus accumulation. Neither field establishes an observed external food supply.

## Native source and Ecopath verification

A fresh read-only query verified all 72 group/fleet catch records and their identifiers. The two fleets route **0.005859524956463247 t/km² during 2020** to **Detritus (36)** and zero to **Discards (35)**. All recorded discard mortality fractions are one. Natural mortality/egestion routing is a separate matrix. [Source ledger](outputs/source/source_fisheries_ledger.json) · [Independent source arithmetic](qa/independent/source_arithmetic_verification.json)

The installed EwE engine loaded and ran an isolated copy with all autosave components disabled. `RunEcopath` and `IsModelBalanced` both returned true. Its Discards output was:

| Native Discards term | t/km²/year |
|---|---:|
| Incoming flow (`InputToDet`) | 0 |
| Consumed (`DetEaten`) | 0.20750363171100616 |
| Calculated export (`Ex`) | −0.20750363171100616 |
| Biomass accumulation (`BA`) | 0 |
| Explicit detritus import | 0 |

The calculated export exactly matches the value stored in the original database. The official Ecopath calculation derives detritus export from incoming flow minus consumption, accumulation, onward transfer and respiration. Thus the negative export is a closure residual, not a newly documented import. Ecopath's balanced flag coexists with this unsupplied pool. [Native results](outputs/source/native_sdk_probe.json) · [Independent native verification](outputs/source/native_probe_verification.json) · [Official-source context](outputs/source/web_context.json)

The source was saved by EwE **6.6.8.18072**; the installed calculation assembly reports **{native['assembly_file_version']}** (installer label 6.7.0.18865). This is a later-version native reproduction, not an execution of the exact original binary. Both native detritus export outputs reproduce the source-stored values exactly. The original database hash remained unchanged. This native check used the original source settings; EE floor ON applies to the separate GE/TE comparisons below.

A related source clarification emerged: native Detritus has stored input EE=0, but its calculated EE is **0.04784027114510536**, which rounds to the paper's **0.05**. Comparing the stored input directly with the printed calculated output had overstated this as a source disagreement.

## What was lost in the reconstruction

Both retained JSON variants contain export=0 for the two detritus pools, so the source-stored native Export values were lost before the archived loader. That loader also clears detritus catch/export and derives accumulation from the residual. The old calculation omitted fleet-return supply as well. These are distinct transformations. [Native-to-canonical trace](qa/independent/native_export_trace.json)

The new controlled comparison restores only the independently verified donor-to-recipient fleet return matrix. It preserves accepted living biomass, production, consumption, diets, predation, catch and migration. No return was redirected to group 35, no additional offal/import was invented, and no detritus groups were pooled.

## Focused PPR results

The two scenarios use identical pinned calculation code and audited completed initialization. The no-return control reproduces the previously saved floor-ON SPPR, A and L matrices exactly. Each fresh restored scenario receives the floor once, followed by one GE and one TE diagnostic call, with `det_collapse_mode=never` and `det_open_mode=none`.

| Method | Model-catch PPR: control | Model-catch PPR: native returns | Change | Overall status |
|---|---:|---:|---:|---|
{chr(10).join(table)}

These are source-model catch-weighted, all-source PPR values in the engine's model-mass/area/year convention, not regional LME catch totals or carbon estimates. The source reports tonnes per km² for 2020 but does not explicitly establish wet versus dry mass; the project's assumed wet-weight convention is retained as a separate limitation.

All four calls pass their strict weighted balance checks and return finite SPPR matrices with no negative entries. All 37 recipient groups and five source columns were checked. Only the Detritus (36) source column changes; PP-only footprints remain unchanged. Discards (35) remains a zero source column and has an unexplained physical residual of **−0.20750363203745528 t/km²/year**. Returned catch is credited internally once and excluded from external removals; total-catch fishery PPR retains its original catch vector. [Comparison and complete diagnostics](outputs/diagnostics/comparison_summary.json) · [Independent matrix and budget verification](qa/independent/diagnostic_array_verification.json)

Native source BA=0, historical loader-derived pre-floor BA, and floor-effective residual are recorded separately. The floor intentionally recomputes effective detritus closure; this is not a source-parameter correction. The source-BA-zero comparisons are conditional arithmetic with unchanged coefficients, not an additional source-preserving solve or a diagnosis of the original native Ecopath model.

## Remaining scientific question

The reconstructed demand from Discards is **35.413 times** the recorded annual fisheries discards. Seabirds account for **86.6%** of that demand. Even a hypothetical redirection of all recorded discards to group 35 would leave about **0.2016441 t/km²/year** unexplained; that redirection was not run or adopted.

The main paper describes birds eating fish guts and heads. Its cited albatross study distinguishes unwanted fish from processing offal and uses fishery catches as a relative index of discard availability; it does not establish the annual offal amount missing here. The remaining question is whether the intended Discards pool includes processing waste absent from Table S4, or whether the final diet/routing specification requires clarification. A negative calculated export cannot supply the missing provenance. [Paper and related primary-source evidence](outputs/source/web_context.json)

The current reconstruction therefore remains **WARN with unresolved discard-source attribution**. The numerical omission of fleet returns has been isolated and quantified; the ecological supply discrepancy remains. The next evidence needed is the authors' intended final Discards inflow/routing and, if applicable, a quantified processing-offal ledger. A new import, changed diet or pooled-detritus scenario would require a separate justified scientific choice.

## Scope and preservation

This package is a model-local investigation for researcher review. The canonical model, accepted parameters, regional workbook, coefficient workbook, snapshots, taxon appendix and researcher DOCX were not overwritten. No decision was registered and this task performed no Project.xlsx, map, trends or sources-page writes. Shared code remained unchanged by this task; the coordinator confirmed the pinned engine identity and that floor-effective detritus closure is intentional. Concurrent shared-file changes by the coordinator, if any, are distinguished in the protection receipt.

[Evidence index](evidence_index.json) · [Execution provenance](outputs/diagnostics/run_provenance.json) · [Preservation receipt](qa/protected_final.json)
'''
    (DEST/'discards_reconciliation.md').write_text(report,encoding='utf-8')
    write(DEST/'result_summary.json',{'run_id':comp['run_id'],'model_id':MODEL.name,'methods':metrics,
           'floor':{'use_ee_floor':True,'ee_floor':0.1},'native_probe':{'balanced':True,'input_to_discards':0.0,
           'discard_export':native['after_run_flow_arrays']['Ex']['flat_values'][35],
           'original_source_unchanged':True,'executed_assembly_version':native['assembly_file_version']},
           'remaining_residual':-0.20750363203745528,'input_adoption':False,'review_registration':False,'publication':False})
    before=read(WORK/'qa/protected_before.json')
    checks=[]
    for item in before['files']:
        p=ROOT/item['path']
        try:
            digest=sha(p)
            checks.append({**item,'sha256_after':digest,'bytes_equal':item.get('sha256')==digest})
        except Exception as e:
            checks.append({**item,'after_availability':'unavailable','after_reason':str(e)})
    local=[x for x in checks if x['path'].startswith('regions/')]
    assert all(x.get('bytes_equal') for x in local), 'Protected local file changed: inspect before finalizing.'
    write(DEST/'qa/protected_final.json',{'model_local_protected_files_unchanged':True,'files':checks,
            'writes_by_this_task':'Only model-local work and this evidence package. No original source, canonical model, DOCX, workbook or shared-file writes.',
            'shared_file_caveat':'Other authorized coordinator work may change shared files concurrently; observed drift is not attributed to this run.'})
    rolemap={
        'discards_reconciliation.md':'scientific_interpretation',
        'outputs/source/source_fisheries_ledger.json':'source_fisheries',
        'outputs/source/native_sdk_probe.json':'native_engine_result',
        'outputs/source/native_probe_verification.json':'native_verification',
        'outputs/diagnostics/control_no_returns/GE_full_return.json':'control_GE',
        'outputs/diagnostics/control_no_returns/TE_full_return.json':'control_TE',
        'outputs/diagnostics/source_exact_returns_to_36/GE_full_return.json':'returns_GE',
        'outputs/diagnostics/source_exact_returns_to_36/TE_full_return.json':'returns_TE',
        'qa/independent/diagnostic_array_verification.json':'independent_diagnostics_verification',
        'qa/protected_final.json':'protected_verification',
        'outputs/diagnostics/run_provenance.json':'execution_provenance',
        'code/run_discard_comparison.py':'executed_runner'
    }
    artifacts=[]
    for p in sorted(DEST.rglob('*')):
        if p.is_file():
            rel=p.relative_to(DEST).as_posix()
            artifacts.append({'role':rolemap.get(rel,'support:'+rel),'path':rel,'sha256':sha(p),'availability':'present'})
    for p,role in [(MODEL/'model.json','canonical_input'),(ROOT/ledger['source_identity']['path'],'original_native_source'),
                   (MODEL/'model_validation/evidence/ee_floor_on_review/initialization_and_floor.json','audited_initialization')]:
        artifacts.append({'role':role,'path':relative(p),'sha256':sha(p),'availability':'present'})
    artifacts.append({'role':'original_EwE_6.6.8_binary','availability':'missing',
                      'reason':'Exact historical executable was not installed; later installed6.7 assembly used and identified explicitly.',
                      'acquisition_status':'Not acquired; not required to claim this later-version comparison.'})
    index={'schema_version':1,'run_id':comp['run_id'],'region_id':'LME_014','model_id':MODEL.name,
           'variant_id':'audited_completed_floor_on_control_vs_source_exact_fleet_returns',
           'source_identity':ledger['source_identity'],
           'computational_input_identity':{'canonical_sha256':sha(MODEL/'model.json'),
             'initialization':'audited completed_before_floor state; exact preservation verified',
             'return_matrix':'native 72-row group/fleet ledger; recipient36 only','floor':0.1},
           'methods':['GE','TE'],'required_roles':list(rolemap.values())+['canonical_input','original_native_source','audited_initialization'],
           'artifacts':artifacts,'reconciliation':{'four_calls_returned':True,'independent_matrix_QA_passed':True,
             'native_outputs_verified':True,'model_local_protected_files_unchanged':True},
           'scientific_limit':'Inventory completeness is not scientific approval; unexplained Discards supply remains.',
           'created_utc':datetime.now(timezone.utc).isoformat()}
    write(DEST/'evidence_index.json',index)
    print(json.dumps({'destination':str(DEST),'artifacts':len(artifacts),'metrics':metrics},ensure_ascii=False))

if __name__ == '__main__':
    main()
