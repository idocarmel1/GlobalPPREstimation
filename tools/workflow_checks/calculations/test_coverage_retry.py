"""Explicit unavailable-method retries preserve retained science and provenance."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.project_core.calculations import coverage
from tools.project_core.workbooks.workbooks import read_book, records, sha
from tools.workflow_checks.calculations import test_coverage_preservation, test_coverage_scope


class CoverageRetryTests(unittest.TestCase):
    def package(self, root):
        return test_coverage_preservation.CoveragePreservationTests().package(root)

    def context(self, root, model, flags):
        return {'model_sha256': sha(model), 'flags': copy.deepcopy(flags), 'code_identity': {}}

    def executor(self, calls, *, value=None, status='NOT_RUN'):
        def compute(model, flags, methods, directory, progress):
            calls.append((list(methods), copy.deepcopy(flags)))
            outcomes = {}
            for method in methods:
                artifact = directory/(method+'.json')
                artifact.write_text(json.dumps({'method': method, 'value': value}))
                outcomes[method] = {'status': status, 'reason': 'fixture execution',
                    'scopes': {scope: {'Fish': value} for scope in ('all', 'inner', 'PP')},
                    'annual_status': {scope: 'ok' if status == 'ok' else 'NOT_RUN: old execution'
                                      for scope in ('all', 'inner', 'PP')},
                    'evidence': {'path': artifact.name, 'sha256': sha(artifact)}}
            constructor = directory/'constructor.json'
            constructor.write_text(json.dumps(flags))
            return {'methods': outcomes, 'constructor_evidence': {'path': constructor.name, 'sha256': sha(constructor)}}
        return compute

    def test_retry_null_method_with_new_execution_context_preserves_finite_and_mc(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model, path, _, metadata = self.package(root)
            flags = {'constructor': {'det_collapse': True}, 'diagnostics': {'det_collapse_mode': 'auto'}}
            replay = {**flags, 'audited_replay': {'runtime_sha256': 'authenticated runtime'}}
            calls = []
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration', return_value=flags), \
                 patch.object(coverage, '_context', side_effect=self.context):
                coverage._complete_model(root, metadata, ('new_GE', 'MC_new_GE', 'SPPR_1986'),
                    progress=lambda _: None, compute=self.executor(calls))
                before = read_book(path)
                manifest_path = model/'results/result_manifest.json'
                old_manifest = json.loads(manifest_path.read_text())
                old_evidence = {item['path']: (model/'results/diagnostics'/item['path']).read_bytes()
                                for item in old_manifest['method_coverage']['execution_evidence'].values()}
                calls.clear()
                coverage._complete_model(root, metadata, ('new_GE', 'SPPR_1986', 'SPPR_1995'),
                    progress=lambda _: None, compute=self.executor(calls, value=7., status='ok'),
                    retry_unavailable=True, execution_flags=replay)
            self.assertEqual(calls, [(['SPPR_1986', 'SPPR_1995'], replay)])
            after = read_book(path)
            retained = lambda book: [row for row in records(book, 'Selected model groups', 'Group SPPR')
                                     if row['method'] in ('new_GE', 'MC_new_GE')]
            self.assertEqual(retained(after), retained(before))
            for table in ('model_health', 'mc_diagnostics'):
                self.assertEqual(after['Diagnostics'][table], before['Diagnostics'][table])
            self.assertTrue(all(row['sppr'] == 7. for row in records(after, 'Selected model groups', 'Group SPPR')
                                if row['method'] == 'SPPR_1986'))
            self.assertEqual({row['status'] for row in records(after, 'PPR', 'Annual')
                              if row['method'] == 'SPPR_1986' and row['metric'] == 'ppr'
                              and row['catch_basis'] == 'landings' and row['unidentified'] == 'method'}, {'ok'})
            saved = json.loads(manifest_path.read_text())['method_coverage']
            for method in ('new_GE', 'MC_new_GE'):
                self.assertEqual(saved['methods'][method], old_manifest['method_coverage']['methods'][method])
                self.assertEqual(saved['method_contexts'][method], old_manifest['method_coverage']['context'])
            self.assertEqual(saved['methods']['SPPR_1986']['execution_context']['flags'], replay)
            for reference, contents in old_evidence.items():
                self.assertEqual((model/'results/diagnostics'/reference).read_bytes(), contents)
            self.assertTrue(all(item in saved['execution_evidence'].values()
                                for item in old_manifest['method_coverage']['execution_evidence'].values()))

    def test_retry_checks_finite_coefficients_in_every_scope_and_keeps_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model, path, _, metadata = self.package(root)
            calls = []
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration', return_value={}), \
                 patch.object(coverage, '_context', side_effect=self.context):
                executor = self.executor(calls, value=-2., status='failed')
                def partial(*args, **kwargs):
                    result = executor(*args, **kwargs)
                    result['methods']['SPPR_1986']['scopes']['all']['Fish'] = None
                    result['methods']['SPPR_1986']['scopes']['inner']['Fish'] = None
                    return result
                coverage._complete_model(root, metadata, ('new_GE', 'MC_new_GE', 'SPPR_1986'),
                    progress=lambda _: None, compute=partial)
                before = read_book(path)
                calls.clear()
                coverage._complete_model(root, metadata, ('SPPR_1986',),
                    progress=lambda _: None, compute=self.executor(calls, value=10., status='ok'), retry_unavailable=True)
            self.assertEqual(calls, [])
            self.assertEqual(read_book(path)['Selected model groups']['Group SPPR'],
                             before['Selected model groups']['Group SPPR'])
            self.assertEqual(read_book(path)['PPR']['Annual'], before['PPR']['Annual'])

    def test_all_method_initializations_are_promoted_deduplicated_and_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model, path, _, metadata = self.package(root)
            keys = ('SPPR_1986', 'SPPR_1995')
            executor = self.executor([], value=7., status='ok')
            def compute(*args, **kwargs):
                result = executor(*args, **kwargs)
                directory = args[3]
                verification = directory/'retrospective-verification.json'
                verification.write_text('distinct retrospective verification')
                for key in keys:
                    constructor = directory/(key+'-constructor.json')
                    constructor.write_text(key+' constructor')
                    ref = {'path': constructor.name, 'sha256': sha(constructor)}
                    result['methods'][key]['constructor_evidence'] = copy.deepcopy(ref)
                    result['methods'][key]['runtime_verification_evidence'] = {
                        'path': verification.name, 'sha256': sha(verification)}
                    result['constructor_evidence'] = ref
                return result
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration', return_value={}), \
                 patch.object(coverage, '_context', side_effect=self.context):
                coverage._complete_model(root, metadata, keys, progress=lambda _: None,
                    compute=compute, retry_unavailable=True)
            saved = json.loads((model/'results/result_manifest.json').read_text())['method_coverage']
            for key in keys:
                for field in ('evidence', 'constructor_evidence', 'runtime_verification_evidence'):
                    ref = saved['methods'][key][field]
                    artifact = model/'results/diagnostics'/ref['path']
                    self.assertTrue(artifact.is_file(), (key, field, ref))
                    self.assertEqual(sha(artifact), ref['sha256'])
                    self.assertIn('/execution-', ref['path'])
            first = saved['methods'][keys[0]]['constructor_evidence']
            (model/'results/diagnostics'/first['path']).unlink()
            self.assertEqual(coverage._cached_methods(model, saved, saved['context'], read_book(path), keys), [keys[0]])

    def test_missing_old_evidence_gets_honest_adoption_trace_without_new_arithmetic(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model, path, _, metadata = self.package(root)
            calls = []
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration', return_value={}), \
                 patch.object(coverage, '_context', side_effect=self.context):
                expected = ('new_GE', 'MC_new_GE', 'SPPR_1986')
                coverage._complete_model(root, metadata, expected, progress=lambda _: None,
                                         compute=self.executor(calls))
                before = read_book(path)
                manifest_path = model/'results/result_manifest.json'
                manifest = json.loads(manifest_path.read_text())
                missing = manifest['method_coverage']['methods']['new_GE']['evidence']
                (model/'results/diagnostics'/missing['path']).unlink()
                calls.clear()
                coverage._complete_model(root, metadata, expected, progress=lambda _: None,
                                         compute=self.executor(calls, value=99., status='ok'))
            self.assertEqual(calls, [])
            saved = read_book(path)
            for sheet, table in (('Selected model groups', 'Group SPPR'),
                                 ('PPR', 'Annual'), ('Diagnostics', 'model_health'),
                                 ('Diagnostics', 'mc_diagnostics')):
                self.assertEqual(saved[sheet][table], before[sheet][table])
            final = json.loads(manifest_path.read_text())['method_coverage']
            reference = final['methods']['new_GE']['evidence']
            evidence = model/'results/diagnostics'/reference['path']
            self.assertTrue(evidence.is_file(), 'Adoption must not keep a known-missing evidence reference')
            self.assertEqual(sha(evidence), reference['sha256'])
            trace = final['methods']['new_GE']['prior_method_trace']
            self.assertEqual(trace['evidence_check']['status'], 'missing')
            self.assertEqual(trace['recorded_outcome'], manifest['method_coverage']['methods']['new_GE'])

    def test_execution_extension_rejects_changed_scientific_configuration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, path, _, metadata = self.package(root)
            before = path.read_bytes()
            flags = {'constructor': {'det_collapse': True}}
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration', return_value=flags), \
                 patch.object(coverage, '_context', side_effect=self.context), \
                 self.assertRaisesRegex(ValueError, 'configuration'):
                coverage._complete_model(root, metadata, ('SPPR_1986',), progress=lambda _: None,
                    compute=self.executor([]), retry_unavailable=True,
                    execution_flags={'constructor': {'det_collapse': False}})
            self.assertEqual(path.read_bytes(), before)

    def test_retry_rejects_finite_source_coefficient_even_when_snapshot_is_null(self):
        import openpyxl
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model, path, _, metadata = self.package(root)
            calls = []
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration', return_value={}), \
                 patch.object(coverage, '_context', side_effect=self.context):
                coverage._complete_model(root, metadata, ('new_GE', 'MC_new_GE', 'SPPR_1986'),
                    progress=lambda _: None, compute=self.executor(calls))
                source = model/'sppr_source.xlsx'
                workbook = openpyxl.load_workbook(source)
                sheet = workbook['sppr_PP']
                column = [cell.value for cell in sheet[1]].index('SPPR_1986') + 1
                sheet.cell(2, column, -3.)
                workbook.save(source)
                workbook.close()
                before = {item: item.read_bytes() for item in (path, source, model/'results/result_manifest.json')}
                calls.clear()
                with self.assertRaisesRegex(ValueError, 'source|Source'):
                    coverage._complete_model(root, metadata, ('SPPR_1986',), progress=lambda _: None,
                        compute=self.executor(calls, value=7., status='ok'), retry_unavailable=True)
            self.assertEqual(calls, [])
            self.assertEqual({item: item.read_bytes() for item in before}, before)

    def test_replacing_one_source_diagnostic_preserves_other_numeric_cells_exactly(self):
        import openpyxl
        import zipfile
        from xml.etree import ElementTree as etree
        from tools.project_core.validation.researcher_review import sheet_xml, S
        from tools.workflow_checks.selection.test_snapshots import fixture
        precise = 0.12345678912345678
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)/'sppr_source.xlsx'
            workbook = openpyxl.Workbook()
            workbook.remove(workbook.active)
            for scope in ('all', 'inner', 'PP'):
                sheet = workbook.create_sheet('sppr_' + scope)
                sheet.append(['seq', 'group_name', 'new_GE', 'new_WithEgestion'])
                sheet.append([1, 'Fish', 5., None])
            health = workbook.create_sheet('model_health')
            health.append(['TE_option', 'metric'])
            health.append(['GE', precise])
            health.append(['With Egestion', None])
            workbook.save(source)
            workbook.close()
            with zipfile.ZipFile(source) as archive:
                member, sheet = sheet_xml(archive, 'model_health')
                cell = next(cell for cell in sheet.iter(f'{{{S}}}c') if cell.get('r') == 'B2')
                cell.find(f'{{{S}}}v').text = repr(precise)
                parts = [(info, etree.tostring(sheet) if info.filename == member else archive.read(info.filename))
                         for info in archive.infolist()]
            with zipfile.ZipFile(source, 'w') as archive:
                for info, contents in parts:
                    archive.writestr(info, contents)
            book = fixture()
            book['Selected model groups']['Group SPPR'][1][:] = [
                ['A', 'Fish', scope, method, value] for scope in ('all', 'inner', 'PP')
                for method, value in [('new_GE', 5.), ('new_WithEgestion', 7.)]]
            book['Diagnostics']['model_health'] = (['TE_option', 'metric'], [['GE', precise], ['With Egestion', 7.]])
            coverage._update_source(source, book, {'new_WithEgestion': {'status': 'ok'}},
                                    replace_methods={'new_WithEgestion'})
            saved = openpyxl.load_workbook(source, data_only=False)
            try:
                self.assertEqual(saved['model_health']['B2'].value, precise)
                self.assertEqual(saved['model_health']['B3'].value, 7.)
            finally:
                saved.close()


class CoverageMethodScopeTests(unittest.TestCase):
    def setUp(self):
        fixture = test_coverage_scope.CoverageScopeTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.root, self.pairs = fixture.root, fixture.pairs

    def test_requested_subset_and_pair_flags_are_forwarded(self):
        flags = {'constructor': {'det_collapse': True}, 'audited_replay': {'runtime_sha256': 'verified'}}
        with patch.object(coverage, '_complete_model', return_value=(False, {})) as complete, \
             patch('tools.scientific_helpers.sppr.method_coverage.method_inventory', return_value=('new_GE', 'SPPR_1986', 'MC_new_GE')):
            coverage.ensure_validated_coverage(self.root, lock_held=True, model_pairs={self.pairs[1]},
                method_keys=('SPPR_1986', 'new_GE'), retry_unavailable=True,
                execution_flags_by_pair={self.pairs[1]: flags})
        args, kwargs = complete.call_args
        self.assertEqual(tuple(args[2]), ('new_GE', 'SPPR_1986'))
        self.assertTrue(kwargs['retry_unavailable'])
        self.assertEqual(kwargs['execution_flags'], flags)

    def test_invalid_subset_rejects_before_model_discovery(self):
        with patch('tools.scientific_helpers.sppr.method_coverage.method_inventory', return_value=('new_GE',)), \
             patch('tools.project_core.registry.discovery.resolve_model', side_effect=AssertionError('unrequested discovery')), \
             self.assertRaisesRegex(ValueError, 'method'):
            coverage.ensure_validated_coverage(self.root, lock_held=True, all_validated=True,
                                              method_keys=('unknown',))

    def test_empty_method_subset_does_no_adapter_or_metadata_work(self):
        with patch.object(coverage, '_metadata', side_effect=AssertionError('unrequested metadata')), \
             patch('tools.scientific_helpers.sppr.method_coverage.method_inventory', side_effect=AssertionError('unrequested adapter')):
            result = coverage.ensure_validated_coverage(self.root, lock_held=True, all_validated=True, method_keys=())
        self.assertEqual(result['models'], [])


if __name__ == '__main__':
    unittest.main()
