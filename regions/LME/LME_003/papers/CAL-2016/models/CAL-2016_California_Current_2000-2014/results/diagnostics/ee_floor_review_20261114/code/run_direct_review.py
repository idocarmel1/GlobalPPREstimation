"""Review-only GE/TE: archived initialization and an authenticated floor-only engine.

No project/workbook writer or current adapter execution path is invoked.
The current adapter's rejected route is retained separately in inventory.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True
import ast
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.metadata
import importlib.util
import inspect
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import traceback
import warnings

RUN = Path(__file__).resolve().parent.parent
MODEL = RUN.parents[2]
ROOT = next(p for p in MODEL.parents if (p / 'tools/scientific_helpers/sppr/method_coverage.py').is_file())
OUT, INV, CODE = RUN / 'outputs', RUN / 'inventory', RUN / 'code'
CANONICAL = MODEL / 'model.json'
PUBLICATION = MODEL.parent / (MODEL.name + '__source') / 'model.json'
EXPECTED_MODEL = '18ed0ba93eb9c95ce305fc03fc36cc189b4cd365d9482fd8be30f398c2508925'
EXPECTED_PUBLICATION = '3813062f7a7f5e153ff383494426d2b56bc956075a445d87955420692bff102b'
FLOOR_HASH = '2f23261f9073d08165b8f370b4f9907e2f5b0b7cfc905db6833e30e42146e44e'
FLOOR_GIT = 'f920c5d27abb405d1d6243546950cb9e212a8534'
FLOOR_SOURCE = ROOT / 'regions/LME/LME_027/papers/CAN-2009/models/27_118_Northwest_Africa_(1987)/model_validation/work/2026-10-15_091756_ee_floor_comparison/code/executed_engine/PPRCalculator.py'
BASE_HASHES = {
    'ModelData.py': '36b2da24ee467530b867b18abd12ae478964f9106bafc78f07eb1a6de616f54e',
    'PPRCalculator.py': 'b2bb08f0564c8cd0fcc873eb1c681fd924c3dd113e22d6b388456248fc0162a7',
    'utils.py': '817f969850b250d06563cfff2e5d1be0fdf70bacb7a3c4ac317bf69c805ca07f',
}
SHARED_HASHES = {
    'tools/scientific_code/PPREstimation/PPRCalculator.py': '5bd249eb73d61c1db77279a8a527465e4673944f377c40ca9e6100a2da0cc877',
    'tools/scientific_code/PPREstimation/ModelData.py': '64c7769ed1494ccadf71dea333765989964ce8c4be9575143b6bc4cbbc6cc680',
    'tools/scientific_code/PPREstimation/create_PPRS_excel.py': '5f94a4d885643e706a57a9e8faa1bf9fa5338e8626831d74dfe59f2d833158a1',
    'tools/scientific_helpers/sppr/method_coverage.py': 'f855b88eebeb52d8814b0eb1dc8e9ed37e943fe62ed77d5bec88522b1cf19905',
}
CONSTRUCTOR = dict(underdetermined=False, zero_catch=False, zero_biomass_accum=False,
                   default_gs=True, weight_flow=1.0, weight_guess=1.0,
                   normalize_DC=False, DC_tol=0.001)
FLOOR = dict(use_ee_floor=True, ee_floor=0.1, ee_threshold=0.1)
SPPR = dict(DET_TE_vals=1, det_collapse_mode='never', det_open_mode='none',
            det_theta=1.0, det_external_sppr=0.0, fix_EE_0_cases=True)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path, containing=INV):
    return Path(os.path.relpath(path, containing)).as_posix()


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    for p in (OUT, INV, CODE / 'audited', CODE / 'floor'):
        p.mkdir(parents=True, exist_ok=True)
    if (OUT / 'GE_full_return.json.gz').exists() or (OUT / 'TE_full_return.json.gz').exists():
        raise RuntimeError('Existing direct returns: review or explicitly clear work before any repeat execution')
    assert sha(CANONICAL) == EXPECTED_MODEL
    assert sha(PUBLICATION) == EXPECTED_PUBLICATION
    for name, expected in SHARED_HASHES.items():
        assert sha(ROOT / name) == expected, name
    for name, expected in BASE_HASHES.items():
        source = MODEL / 'extracted_tables/evidence/code' / name
        assert sha(source) == expected
        shutil.copyfile(source, CODE / 'audited' / name)
    assert sha(FLOOR_SOURCE) == FLOOR_HASH
    shutil.copyfile(FLOOR_SOURCE, CODE / 'floor/PPRCalculator.py')
    shutil.copyfile(ROOT / 'tools/scientific_helpers/sppr/method_coverage.py', CODE / 'evidence_helpers.py')
    helper = module(CODE / 'evidence_helpers.py', '_lme003_evidence_helpers')
    assert helper._compatible_scientific_ast(CODE / 'audited/PPRCalculator.py', CODE / 'floor/PPRCalculator.py')
    assert not helper._compatible_scientific_ast(CODE / 'audited/PPRCalculator.py', ROOT / 'tools/scientific_code/PPREstimation/PPRCalculator.py')

    import numpy as np
    import pandas as pd
    enc = helper.encode_lossless

    def encoded(path, value):
        data = enc(value)
        raw = json.dumps(data, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')
        if str(path).endswith('.gz'):
            Path(path).write_bytes(gzip.compress(raw, mtime=0))
            assert gzip.decompress(Path(path).read_bytes()) == raw
        else:
            Path(path).write_bytes(raw)
            assert json.loads(Path(path).read_text(encoding='utf-8')) == data
        return data

    originals = [CANONICAL, PUBLICATION, MODEL/'model_notes.md',
                 MODEL/'results/result_manifest.json', MODEL/'results/regional_snapshot.xlsx',
                 MODEL/'extracted_tables/evidence/selected_groups.csv']
    originals += [MODEL/'extracted_tables/evidence'/f'{method}_{suffix}'
                  for method in ('ge', 'te') for suffix in ('direct_return.json', 'source_resolved_sppr.csv')]
    originals += [MODEL/'extracted_tables/evidence/code'/name for name in BASE_HASHES]
    original_hashes = {rel(p): sha(p) for p in originals}
    canonical = json.loads(CANONICAL.read_text(encoding='utf-8'))
    publication = json.loads(PUBLICATION.read_text(encoding='utf-8'))
    by_id = {int(g['group_seq']): g for g in canonical['group']}
    pub_by_id = {int(g['group_seq']): g for g in publication['group']}
    identity = {
        'schema_version': 1, 'run_id': RUN.name, 'region_id': 'LME_003', 'model_id': MODEL.name,
        'started': datetime.now(timezone.utc).isoformat(),
        'scope': 'User-authorized review-only GE and TE diagnostics; no scientific input edits or adoption',
        'route': 'Bounded model-local direct diagnostic runner; not the rejected current compute_methods adapter route',
        'canonical_input': {'path': rel(CANONICAL), 'sha256': EXPECTED_MODEL},
        'publication_input': {'path': rel(PUBLICATION), 'sha256': EXPECTED_PUBLICATION},
        'constructor': CONSTRUCTOR, 'floor_configuration': FLOOR, 'method_options': SPPR,
        'archived_base_engine_hashes': BASE_HASHES,
        'calculation_engine': {'sha256': FLOOR_HASH, 'git_commit': FLOOR_GIT,
                              'git_path': 'tools/scientific_code/PPREstimation/PPRCalculator.py',
                              'path': '../code/floor/PPRCalculator.py', 'upgrade': 'ee_floor_v1'},
        'shared_frozen_hashes': SHARED_HASHES,
        'compatibility': {'archived_to_pinned_floor_ast': True, 'archived_to_current_ast': False,
                          'current_gate_bypassed': False, 'scientific_code_modified': False},
        'metadata_alias': {'filename': '3_2016_Author_solved_California_Current_(2000-2014).json',
                           'lme': 3, 'role': 'Temporary byte-identical canonical input for archived filename parser'},
        'source_EE_meaning': 'EE of the selected accepted canonical author-equation variant, not a publication observation; original publication unknowns are separately retained and do not replace accepted floor eligibility inputs',
        'source_M0_meaning': 'Archived ModelData input-table M0 derived as P*(1-EE); raw other_mort remains -9999 and no observed M0 is claimed',
        'environment': {'python': sys.version, 'packages': {p: importlib.metadata.version(p) for p in ('numpy','pandas','scipy','sympy','igraph','tqdm')}},
    }
    dump(INV/'execution_identity.json', identity)
    print('Identity and compatible pinned floor engine verified; loading archived input.', flush=True)
    data_mod = helper._isolated_module(CODE/'audited/ModelData.py', '_lme003_archived_data', {})
    util_mod = helper._isolated_module(CODE/'audited/utils.py', '_lme003_archived_utils', {})
    deps = {'ModelData': data_mod, 'utils': util_mod}
    base_mod = helper._isolated_module(CODE/'audited/PPRCalculator.py', '_lme003_archived_calculator', deps)
    floor_mod = helper._isolated_module(CODE/'floor/PPRCalculator.py', '_lme003_pinned_floor_calculator', deps)
    assert base_mod.DEFAULT_DIAGNOSTIC_THRESHOLDS == floor_mod.DEFAULT_DIAGNOSTIC_THRESHOLDS
    identity['diagnostic_thresholds'] = base_mod.DEFAULT_DIAGNOSTIC_THRESHOLDS
    dump(INV/'execution_identity.json', identity)
    work_inputs = MODEL/'model_validation/work/2026-11-14_210000_validation/inputs'
    work_inputs.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='ee_floor_alias_', dir=work_inputs) as temporary:
        alias = Path(temporary)/identity['metadata_alias']['filename']
        alias.write_bytes(CANONICAL.read_bytes())
        assert sha(alias) == EXPECTED_MODEL
        md = data_mod.ModelData(str(alias))
        md.lme = 3
        raw_source = copy.deepcopy({'groups':md.groups_data, 'diet':md.DC, 'detritus_fate':md.det_fate})
        source_encoded = encoded(OUT/'source_state.json.gz', raw_source)
        with warnings.catch_warnings(record=True) as notices:
            warnings.simplefilter('always')
            model = base_mod.PPRCalculator.from_modeldata(md, **CONSTRUCTOR)
        pd.testing.assert_frame_equal(md.groups_data, raw_source['groups'])
        pd.testing.assert_frame_equal(md.DC, raw_source['diet'])
        pd.testing.assert_frame_equal(md.det_fate, raw_source['detritus_fate'])
        before = copy.deepcopy(model)
        encoded(OUT/'completed_pre_floor_state.json.gz', helper._runtime(before))
        before_groups = before.get_groups_df().copy()
        before_groups.to_csv(OUT/'completed_pre_floor_groups.csv', encoding='utf-8', index=True)
        saved = pd.read_csv(MODEL/'extracted_tables/evidence/selected_groups.csv', index_col='group_seq')
        prior_checks = {}
        for column in saved.columns:
            actual = before_groups.loc[saved.index, column]
            expected = saved[column]
            if pd.api.types.is_numeric_dtype(expected):
                np.testing.assert_allclose(actual.to_numpy(float), expected.to_numpy(float), rtol=1e-12, atol=1e-12, equal_nan=True)
            else:
                assert actual.fillna('').astype(str).tolist() == expected.fillna('').astype(str).tolist(), column
            prior_checks[column] = True
        # Rebind only after unchanged archived loading; never rerun a newer loader.
        model.__class__ = floor_mod.PPRCalculator
        model._initialization_settings = copy.deepcopy(CONSTRUCTOR)
        with warnings.catch_warnings(record=True) as floor_notices:
            warnings.simplefilter('always')
            model.apply_ee_floor(**FLOOR)
        encoded(OUT/'effective_state.json.gz', helper._runtime(model))
        model.get_groups_df().to_csv(OUT/'effective_groups.csv', encoding='utf-8', index=True)
        pd.testing.assert_frame_equal(md.groups_data, raw_source['groups'])
        pd.testing.assert_frame_equal(model._DC, before._DC)
        pd.testing.assert_frame_equal(model._det_fate, before._det_fate)
        living = before_groups.index[before_groups.trophic_info.isin(['Regular','PP'])]
        protected = {}
        for name in ('p','q','catch','predation','growth','immigration','emigration','net_migration','respiration','egestion','GS','GE','TL'):
            left,right = getattr(before,name).loc[living],getattr(model,name).loc[living]
            pd.testing.assert_series_equal(left,right)
            protected[name] = True
        for column in ('biomass','pb','qb'):
            pd.testing.assert_series_equal(before_groups.loc[living,column],model.get_groups_df().loc[living,column])
            protected[column] = True
        np.testing.assert_allclose(before.M0-model.M0, model.external_mortality_export, rtol=1e-12, atol=1e-12)
        ledger = model.ee_floor_ledger.copy()
        enriched = []
        for seq,row in ledger.iterrows():
            source,pub = by_id.get(int(seq)),pub_by_id.get(int(seq))
            item = {'group_id':int(seq),'group_name':model.seq2name[seq],**row.to_dict()}
            item.update(publication_input_EE=None if pub is None or pub['ee']=='-9999' else float(pub['ee']),
                        publication_EE_literal=pub.get('ee') if pub else None,
                        publication_EE_unknown=bool(pub and pub['ee']=='-9999'),
                        canonical_EE_literal=source.get('ee') if source else None,
                        canonical_other_mort_literal=source.get('other_mort') if source else None,
                        publication_other_mort_literal=pub.get('other_mort') if pub else None,
                        source_EE_provenance='accepted author-equation solution' if pub and pub['ee']=='-9999' else ('publication-input retained value' if pub else 'synthetic runtime group'),
                        source_M0_provenance='derived by archived ModelData as P*(1-EE); raw independent M0 unknown' if source else 'synthetic runtime group')
            enriched.append(item)
        ledger.to_csv(OUT/'ee_floor_ledger.csv',encoding='utf-8')
        encoded(OUT/'ee_floor_ledger_lossless.json',ledger)
        encoded(OUT/'ee_floor_source_provenance.json',enriched)
        detritus = []
        for seq in model.get_DET_seq():
            fate = model._det_fate[seq].reindex(model.M0.index).fillna(0)
            expected_inflow = float(((model.M0+model.egestion)*fate).sum())
            np.testing.assert_allclose(expected_inflow,model.p[seq],rtol=1e-12,atol=1e-12)
            detritus.append({'id':int(seq),'name':model.seq2name[seq],
                            'inflow_before':float(before.p[seq]),'inflow_effective':float(model.p[seq]),
                            'fate_routed_effective_mortality_plus_egestion':expected_inflow,
                            'fate_routed_removed_mortality':float((model.external_mortality_export*fate).sum()),
                            'stock_residual_before':float(before.growth[seq]),'stock_residual_effective':float(model.growth[seq]),
                            'demand_predation':float(model.predation[seq]),'catch':float(model.catch[seq]),
                            'net_migration':float(model.net_migration[seq]),
                            'negative_stock_residual':bool(model.growth[seq]<0)})
        production_residual = model.p.loc[living]-(model.predation+model.catch+model.growth+model.net_migration+model.M0+model.external_mortality_export).loc[living]
        accounting = {'floor_info':enc(model.ee_floor_info),'detritus':detritus,
                      'external_mortality_export_total':float(model.external_mortality_export.sum()),
                      'living_production_residual_max_abs':float(production_residual.abs().max()),
                      'protected_living_fields_exactly_equal':protected,
                      'source_tables_unchanged':True,'diet_and_fate_unchanged':True,
                      'completed_state_matches_retained_selected_groups':prior_checks,
                      'source_EE_meaning':identity['source_EE_meaning'],'source_M0_meaning':identity['source_M0_meaning'],
                      'loader_warnings':[str(w.message) for w in notices],
                      'floor_warnings':[str(w.message) for w in floor_notices]}
        dump(OUT/'floor_accounting.json',accounting)
        summary = {'configuration':FLOOR,'region_id':'LME_003','model_id':MODEL.name,
                   'canonical_sha256':EXPECTED_MODEL,'actual_engine_sha256':FLOOR_HASH,'engine_git_commit':FLOOR_GIT,
                   'route':identity['route'],'evidence_index':'../inventory/evidence_index.json',
                   'floor':accounting,'changed_groups':[{'id':int(i),'name':model.seq2name[i]} for i in ledger.index[ledger.applied]],
                   'skipped_groups':[{'id':int(i),'name':model.seq2name[i],'reason':str(ledger.loc[i,'reason'])} for i in ledger.index[~ledger.applied]],
                   'methods':{}}
        for option,key in [('GE','new_GE'),('TE','new_TE_EEfix')]:
            local = copy.deepcopy(model)
            started=time.monotonic()
            state_before=helper._runtime(local)
            call=dict(TE_option=option,short=False,flat=False,return_sppr=True,
                      thresholds=base_mod.DEFAULT_DIAGNOSTIC_THRESHOLDS,**SPPR)
            print(f'Running {option} ON0.1 with pinned floor-only engine.',flush=True)
            try:
                with warnings.catch_warnings(record=True) as method_notices:
                    warnings.simplefilter('always')
                    result=local.diagnose_sppr(**call)
                report,raw,*additional=result
                encoded(OUT/f'{option}_full_return.json.gz',result)
                encoded(OUT/f'{option}_direct_return.json',report)
                encoded(OUT/f'{option}_state_before.json.gz',state_before)
                encoded(OUT/f'{option}_state_after.json.gz',helper._runtime(local))
                assert state_before==helper._runtime(local), 'Direct method mutated runtime state'
                assert raw is not None, 'Method did not return source-resolved coefficients'
                assert raw.index.is_unique and raw.columns.is_unique
                encoded_matrix=encoded(OUT/f'{option}_source_matrix.json',raw)
                raw.to_csv(OUT/f'{option}_source_matrix.csv',encoding='utf-8')
                for number,value in enumerate(additional,start=2):
                    encoded(OUT/f'{option}_returned_matrix_{number}.json',value)
                values=raw.to_numpy(dtype=float)
                negatives=[{'method':option,'source_id':int(raw.columns[j]),'source_name':model.seq2name[raw.columns[j]],
                            'group_id':int(raw.index[i]),'group_name':model.seq2name[raw.index[i]],
                            'value':float(values[i,j]),'comparison':'strict value < 0 before rounding','tolerance':0.0}
                           for i,j in np.argwhere(values<0)]
                dump(OUT/f'{option}_negative_source_group_pairs.json',negatives)
                selected_sources={s:[c for c in raw.columns if s=='all' or c not in set(model.get_Import_seq())|(set(model.get_DET_seq()) if s=='PP' else set())] for s in ('all','inner','PP')}
                coefficients=pd.DataFrame({s:raw[cols].sum(axis=1,min_count=1) for s,cols in selected_sources.items()})
                encoded(OUT/f'{option}_scope_coefficients.json',coefficients)
                footprint_checks={}
                for scope,field in [('all','ppr_all'),('inner','ppr_inner'),('PP','ppr_pp_only')]:
                    actual=float((coefficients[scope]*local.catch.reindex(coefficients.index)).sum())
                    np.testing.assert_allclose(actual,report['footprint'][field],rtol=1e-12,atol=1e-12)
                    footprint_checks[field]={'from_saved_source_sums_and_unchanged_catch':actual,'direct_report':report['footprint'][field]}
                neg_columns=int((values<0).any(axis=0).sum())
                assert neg_columns==report['divergence']['n_negative_sources']
                reopened=json.loads((OUT/f'{option}_source_matrix.json').read_text(encoding='utf-8'))
                assert reopened==encoded_matrix
                sink_weights={scope:float((coefficients[scope]*local.external_mortality_export.reindex(coefficients.index)).sum()) for scope in coefficients}
                det_sppr=[{'id':int(seq),'name':model.seq2name[int(seq)],'sppr':float(value)} for seq,value in report['divergence']['sppr_det'].items()]
                method_summary={'method_key':key,'execution_status':'returned','overall_status':report['status'],
                    'rho_living':report['divergence']['rho_living'],'b':report['divergence']['b'],
                    'b_note':'TE convention, not evidence of absent recycling' if option=='TE' else 'detritus recycling loop gain',
                    'detritus_sppr':det_sppr,'negative_source_group_pairs':negatives,
                    'negative_source_columns':neg_columns,'nonfinite_entries':int((~np.isfinite(values)).sum()),
                    'matrix_shape':list(raw.shape),'source_columns':[{'id':int(c),'name':model.seq2name[c]} for c in raw.columns],
                    'model_input':enc(report['model_input']),'balance':enc(report['balance']),
                    'divergence':enc(report['divergence']),'warnings':report.get('warnings',[]),
                    'strict_flags':{'is_model_balanced':report['model_input']['is_model_balanced'],
                                    'is_sppr_balanced':report['balance']['is_balanced'],
                                    'living_converges':report['divergence']['living_converges'],
                                    'b_converges':report['divergence']['b_converges']},
                    'sppr_weighted_external_sink_by_scope':sink_weights,'footprint_reconciliation':footprint_checks,
                    'state_unchanged_by_method':True,'full_return':f'{option}_full_return.json.gz',
                    'elapsed_seconds':time.monotonic()-started,'call':call}
                summary['methods'][option]=method_summary
                dump(OUT/f'{option}_verification.json',method_summary)
                print(f'{option}: {report["status"]}; negative entries={len(negatives)}; nonfinite={method_summary["nonfinite_entries"]}',flush=True)
            except Exception as exc:
                summary['methods'][option]={'method_key':key,'execution_status':'failed','overall_status':None,
                    'exception':{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()},
                    'elapsed_seconds':time.monotonic()-started}
                dump(OUT/f'{option}_failure.json',summary['methods'][option])
    # Temporary filename adapter is removed; canonical and historical sources remain.
    protected_unchanged={name:sha((INV/name).resolve())==digest for name,digest in original_hashes.items()}
    shared_unchanged={name:sha(ROOT/name)==digest for name,digest in SHARED_HASHES.items()}
    assert all(protected_unchanged.values()) and all(shared_unchanged.values())
    dump(INV/'protected_input_verification.json',{'original_sha256':original_hashes,'unchanged':protected_unchanged,'shared_frozen_unchanged':shared_unchanged})
    summary['completed']=datetime.now(timezone.utc).isoformat()
    summary['protected_inputs_unchanged']=True
    summary['adopted_into_workbook_project_or_map']=False
    dump(OUT/'report_summary.json',summary)
    artifacts=[]
    def artifact(path,role):
        artifacts.append({'role':role,'path':rel(path),'sha256':sha(path),'availability':'present'})
    for path,role in [(CANONICAL,'canonical_input'),(PUBLICATION,'publication_input'),
                      (MODEL/'model_notes.md','source_departures'),
                      (INV/'execution_identity.json','execution_identity'),
                      (INV/'protected_input_verification.json','protected_inputs'),
                      (OUT/'source_state.json.gz','source_state'),(OUT/'completed_pre_floor_state.json.gz','completed_state'),
                      (OUT/'effective_state.json.gz','effective_state'),(OUT/'ee_floor_ledger_lossless.json','floor_ledger'),
                      (OUT/'ee_floor_source_provenance.json','source_parameter_provenance'),
                      (OUT/'floor_accounting.json','floor_accounting'),(OUT/'report_summary.json','report_summary')]:artifact(path,role)
    for path in sorted(CODE.rglob('*.py')):artifact(path,'executed_code')
    required=['canonical_input','publication_input','source_departures','execution_identity','protected_inputs','source_state','completed_state','effective_state','floor_ledger','source_parameter_provenance','floor_accounting','report_summary','executed_code']
    for option in ('GE','TE'):
        for suffix,role in [('full_return.json.gz','full_return'),('source_matrix.json','source_matrix'),('scope_coefficients.json','scope_coefficients'),('negative_source_group_pairs.json','negative_pairs'),('verification.json','reconciliation')]:
            role=option+'_'+role;required.append(role);path=OUT/f'{option}_{suffix}'
            if path.is_file():artifact(path,role)
            else:artifacts.append({'role':role,'availability':'failed','reason':'Direct method execution/reconciliation failed; see report summary','acquisition_status':'attempted in authorized direct run'})
    accounted={x['path'] for x in artifacts}
    for path in sorted(OUT.glob('*')):
        if path.is_file() and rel(path) not in accounted:artifact(path,'supporting_output')
    if (INV/'preflight_current_engine.json').is_file():artifact(INV/'preflight_current_engine.json','current_route_rejection')
    index={'schema_version':1,'run_id':RUN.name,'region_id':'LME_003','model_id':MODEL.name,
           'variant_id':MODEL.name+'__EE_floor_ON_0.1_review',
           'source_identity':identity['publication_input'],'computational_input_identity':identity['canonical_input'],
           'methods':['GE','TE'],'required_roles':required,'artifacts':artifacts,
           'reconciliation':{'protected_inputs_unchanged':True,'shared_code_unchanged':True,
                             'all_requested_methods_returned_and_reconciled':all(m['execution_status']=='returned' for m in summary['methods'].values())},
           'configuration':FLOOR,'execution_route':identity['route'],'not_adopted':True}
    dump(INV/'evidence_index.json',index)
    print('Saved report_summary.json and portable evidence_index.json.',flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        main()
    except Exception as exc:
        INV.mkdir(parents=True,exist_ok=True)
        dump(INV/'execution_failure.json',{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),'timestamp':datetime.now(timezone.utc).isoformat(),'methods_not_claimed_complete':True})
        raise
