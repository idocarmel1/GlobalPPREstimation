"""Retain verified EE-floor evidence and discard authenticated retry duplicates."""
from pathlib import Path
import csv,gzip,hashlib,json,sys

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
from tools.project_core.calculations.ee_floor_execution import discard_execution
WORK=Path(__file__).resolve().parents[1]

def read(path):return json.loads(gzip.decompress(path.read_bytes()))
def digest(path):
    checksum=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):checksum.update(chunk)
    return checksum.hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(value,ensure_ascii=False,sort_keys=True,
                                            allow_nan=False).encode(),mtime=0))
def number(value):return 'Unavailable / restricted' if value is None else f'{value/1e6:.9g}'

def main():
    before=read(WORK/'qa/before.json.gz');after=read(WORK/'qa/after.json.gz')
    views=read(WORK/'qa/view_verification.json.gz')
    central=read(WORK/'qa/central_preservation.json.gz')
    assert central['original_capture_hash']==before['independent_project']
    assert central['unrelated_central_tables_unchanged'] is True
    assert len(after)==len(views)==len(before['identities'])==8
    assert all(row['preserved'] and row['all_method_count']==22 for row in after)
    assert all(row['method_count']==22 for row in views)
    browser=json.loads((WORK/'qa/browser_verification.json').read_text(encoding='utf-8'))
    assert len(browser['mapChecks'])==len(browser['sourceChecks'])==8
    assert all(row['visible'] for row in browser['trendChecks'])
    with (WORK/'qa/map_export_LME_047_2019.csv').open(encoding='utf-8-sig',newline='') as stream:
        exported=list(csv.DictReader(stream))
    assert exported and all(json.loads(row['calculation_provenance'])['use_ee_floor'] is True and
                            json.loads(row['calculation_provenance'])['ee_floor']==.1 for row in exported)
    with (WORK/'qa/trend_provenance_export.csv').open(encoding='utf-8',newline='') as stream:
        serialized=json.loads(next(csv.DictReader(stream))['calculation_provenance'])
    assert set(serialized)=={unit for unit,_ in before['identities']}
    assert all(settings['use_ee_floor'] is True and settings['ee_floor']==.1
               for models in serialized.values() for settings in models.values())
    removals=[];index=[]
    for report in after:
        key=report['unit']+'/'+report['model_id'];model=ROOT/before['models'][key]['model']
        directory=model/'results/diagnostics/ee_floor'
        manifest=json.loads((model/'results/result_manifest.json').read_text(encoding='utf-8'))
        assert manifest['effective_flags']['constructor']['use_ee_floor'] is True
        assert manifest['effective_flags']['constructor']['ee_floor']==.1
        assert digest(model/'sppr_source.xlsx')==manifest['coefficient_source_sha256']
        assert digest(model/'results/regional_snapshot.xlsx')==manifest['snapshot_sha256']
        certificate_path=directory/'execution_cache_cleanup.json.gz'
        cache_certificates=read(certificate_path) if certificate_path.is_file() else []
        for prior in cache_certificates:
            for promoted in prior['promoted_files']:
                assert digest(model/promoted['path'])==promoted['sha256']
        for pending in sorted((model/'model_validation/work').glob('*_ee_floor_execution*/outputs/pending.json.gz')):
            package=read(pending);receipt=json.loads(pending.with_name('receipt.json').read_text(encoding='utf-8'))
            assert digest(pending)==receipt['sha256']
            assert package['context']==manifest['method_coverage']['context']
            assert set(package['methods'])<=set(manifest['method_coverage']['methods'])
            promoted=[]
            for relative,evidence in package['files'].items():
                destination=(model/'results/diagnostics/method_coverage'/relative).resolve()
                assert destination.is_relative_to((model/'results/diagnostics/method_coverage').resolve())
                assert digest(destination)==evidence['sha256']
                promoted.append({'path':destination.relative_to(model).as_posix(),'sha256':evidence['sha256']})
            certificate={'receipt':receipt,'context_matches_adopted_manifest':True,
                         'promoted_files':promoted,'role':'Authenticated duplicate removal after whole-batch publication and verification'}
            cache_certificates.append(certificate);removals.append((model,receipt))
        save(directory/'execution_cache_cleanup.json.gz',cache_certificates)
        rows=[]
        for change in report['changes']:
            outcome=manifest['method_coverage']['methods'][change['method']]
            status=str(change['after_status']).replace('|','\\|').replace('\n',' ')
            delta='—' if change['percent_change'] is None else f"{change['percent_change']:+.9g}%"
            rows.append(f"| {change['method']} | {number(change['before_2019_tC'])} | {number(change['after_2019_tC'])} | {delta} | {outcome['status']} | {status} |")
        text=f"""# EE-floor calculation evidence: {report['unit']}

Model: `{report['model_id']}`. The user authorized implementation, scientific reruns and adoption/publication of EE-floor calculations on 2026-10-14. The saved setting is `use_ee_floor=True`, `ee_floor=0.1`. Explicit OFF restores the audited baseline. This is a hypothetical calculation assumption, not a published parameter correction or a new researcher approval.

The floor is applied once after audited initialization. Source EE/M0 and completed pre-floor EE/M0 remain separate from effective EE/M0. The removed mortality is an explicit nonfishery external sink counted by production and both SPPR balance branches. Only reduced M0 plus unchanged egestion enter the existing detritus fate matrix. Catch, fishery weighting, living biological flows, migration and living biomass accumulation remain preserved. Negative detritus residuals and existing diagnostic restrictions remain limitations.

The audited loader dependencies, model-specific settings and recorded Monte Carlo policies remain recorded in [the result manifest](../../result_manifest.json). Humboldt retains `det_collapse_mode='auto'`. Compatible unaffected methods retain their actual earlier provenance; affected methods were executed with complete return evidence. An inventory outcome can be failed, timed out, restricted or unavailable while the model retains its historical researcher validation. Original signed Word documents and source diagnostics were preserved.

Before/after below: 2019 landings, all sources, all model groups, **million tonnes carbon equivalent**. The native regional Annual `ppr` values are wet-weight equivalent; existing regional ratio and view arithmetic divide by 9. Raw and converted values both remain in the machine-readable report. Researcher exclusions from displayed PPR remain separate and unchanged. Monte Carlo differences include new draws under the recorded unseeded policies where applicable; compatible unaffected Monte Carlo results were not redrawn.

| Method | Before (Mt C) | After (Mt C) | Change | Execution/retention | Scientific availability / restriction |
|---|---:|---:|---:|---|---|
"""+'\n'.join(rows)+"""

Evidence:

- [Full 22-method manifest](../../result_manifest.json) and [actual method returns](../method_coverage/).
- [Source/completed/effective runtime ledger](runtime.json.gz); `*.baseline.json.gz` files retain lossless outgoing calculation packages and historical manifests without relabeling them as floor-enabled.
- [OFF and saved experiment reconciliation](experiment_reconciliation.json.gz). The Eastern Tropical Pacific experiment also floored a group with unknown source EE; the production setting excludes it. Replaying the experiment with the same valid-input eligibility agrees without changing source parameters or tolerances.
- [Input and result preservation](publication_verification.json.gz), [view/workbook equality](view_verification.json.gz), and [authenticated duplicate-removal receipts](execution_cache_cleanup.json.gz).

Supporting whole-project audit code, original preservation capture, native pre-publication Project.xlsx, test output, browser evidence and the eight-model index are retained under the Humboldt model's `results/diagnostics/ee_floor/verification/` directory. The broader legacy engine test suite remains blocked by absent historical engine-local ToyModels/Black Sea fixture paths; no scientific inputs were substituted. Root `structure.md` remains absent; the applicable structure guide is `explainers/structure.md`.
"""
        (directory/'README.md').write_text(text,encoding='utf-8')
        index.append({'unit_id':report['unit'],'model_id':report['model_id'],
                      'evidence':(directory/'README.md').relative_to(ROOT).as_posix(),
                      'methods':len(report['changes']),'retry_duplicates':len(cache_certificates)})
    # Every model is checked before the first deletion.
    for model,reference in removals:discard_execution(model,reference)
    save(WORK/'qa/finalization.json.gz',{'models':index,
                                     'authenticated_retry_duplicates':sum(row['retry_duplicates'] for row in index),
                                     'removed_authenticated_retry_duplicates_this_run':len(removals),
                                     'all_publication_checks_passed':True})
    print(json.dumps({'models':len(index),'methods_per_model':22,'retry_duplicates_removed':len(removals)},indent=2))

if __name__=='__main__':main()
