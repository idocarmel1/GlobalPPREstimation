import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration


class AuditedConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.model = Path(self.temporary.name) / 'test_model'
        self.model.mkdir()
        (self.model / 'model.json').write_text('{}', encoding='utf-8')
        self.source_hash = hashlib.sha256(b'{}').hexdigest()
        self.engine_hashes = {}
        self.engine_paths = {}
        for name in ('PPRCalculator.py', 'ModelData.py', 'utils.py'):
            path = self.model / 'retained_engine' / name
            path.parent.mkdir(exist_ok=True)
            path.write_text('# audited ' + name, encoding='utf-8')
            self.engine_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            self.engine_paths[name] = path.relative_to(self.model).as_posix()
        self.book = {'Overview': {'Settings': (['field', 'value'], [
            ['results_model_id', self.model.name], ['results_model_sha256', self.source_hash]])}}

    def evidence(self, folder, **extra):
        path = self.model / 'model_validation/evidence/source_review' / folder / 'execution_evidence.json'
        path.parent.mkdir(parents=True)
        data = {'canonical_sha256': self.source_hash,
                'constructor_settings': {'underdetermined': True, 'zero_biomass_accum': False},
                'diagnostic_settings': {'det_collapse_mode': 'never'},
                'engine_hashes': self.engine_hashes}
        data.update(extra)
        path.write_text(json.dumps(data), encoding='utf-8')
        return path

    def test_missing_or_wrong_model_evidence_never_supplies_defaults(self):
        self.evidence('stale', canonical_sha256='old_source')
        with self.assertRaisesRegex(ValueError, 'audited configuration'):
            resolve_audited_configuration(self.model, self.book, {})

    def test_matching_evidence_preserves_supplied_kwargs_and_pins_bytes(self):
        path = self.evidence('current')
        self.evidence('stale', canonical_sha256='old_source',
                      diagnostic_settings={'det_collapse_mode': 'auto'})
        flags = resolve_audited_configuration(self.model, self.book, {})
        self.assertEqual(flags['constructor'], {'underdetermined': True, 'zero_biomass_accum': False})
        self.assertEqual(flags['diagnostics']['det_collapse_mode'], 'never')
        self.assertIn({
            'relative_path': path.relative_to(self.model).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'original_source_hash': self.source_hash}, flags['configuration_evidence'])
        self.assertEqual(flags['engine_source_hashes'], self.engine_hashes)
        self.assertEqual(flags['engine_sources'], self.engine_paths)

    def test_conflicting_current_configuration_is_rejected(self):
        self.evidence('one')
        self.evidence('two', diagnostic_settings={'det_collapse_mode': 'auto'})
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            resolve_audited_configuration(self.model, self.book, {})

    def test_methods_only_overview_does_not_hide_matching_manifest(self):
        self.book['Overview']['Settings'][1].append([
            'sppr_configuration', json.dumps({'GE': {'det_collapse_mode': 'never'}})])
        flags = {'constructor': {'underdetermined': True},
                 'diagnostics': {'det_collapse_mode': 'auto'}}
        manifest = {'canonical_model_sha256': self.source_hash, 'effective_flags': flags,
                    'code_identity': self.engine_hashes}
        resolved = resolve_audited_configuration(self.model, self.book, manifest)
        self.assertEqual(resolved['constructor'], flags['constructor'])
        self.assertEqual(resolved['diagnostics'], flags['diagnostics'])
        self.assertEqual(resolved['engine_source_hashes'], self.engine_hashes)

    def test_legacy_matching_input_hash_manifest_preserves_actual_auto_mode(self):
        self.evidence('older_direct', diagnostic_settings={'det_collapse_mode': 'never'})
        manifest = {'input_sha256': self.source_hash,
                    'constructor': {'underdetermined': True},
                    'diagnostics': {'det_collapse_mode': 'auto'},
                    'engine_hashes': self.engine_hashes}
        flags = resolve_audited_configuration(self.model, self.book, manifest)
        self.assertEqual(flags['diagnostics']['det_collapse_mode'], 'auto')
        self.assertEqual(flags['engine_source_hashes'], self.engine_hashes)

    def test_missing_audited_dependency_hash_is_not_inferred(self):
        self.evidence('current', engine_hashes={
            key: value for key, value in self.engine_hashes.items() if key != 'utils.py'})
        with self.assertRaisesRegex(ValueError, 'audited engine.*utils.py'):
            resolve_audited_configuration(self.model, self.book, {})

    def test_missing_exact_source_is_explicit_configuration_failure(self):
        self.evidence('current')
        (self.model / self.engine_paths['PPRCalculator.py']).unlink()
        with self.assertRaisesRegex(ValueError, 'audited engine source.*PPRCalculator.py'):
            resolve_audited_configuration(self.model, self.book, {})

    def test_changed_pinned_source_is_rejected(self):
        self.evidence('current')
        flags = resolve_audited_configuration(self.model, self.book, {})
        (self.model / self.engine_paths['PPRCalculator.py']).write_text('# changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'evidence changed|engine hash mismatch'):
            resolve_audited_configuration(self.model, self.book, {
                'canonical_model_sha256': self.source_hash, 'effective_flags': flags})

    def test_conflicting_audited_engine_hashes_are_rejected(self):
        self.evidence('one')
        self.evidence('two', engine_hashes={**self.engine_hashes, 'PPRCalculator.py': 'f' * 64})
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            resolve_audited_configuration(self.model, self.book, {})

    def test_explicit_active_run_supersedes_stale_legacy_manifest_engine(self):
        run = self.model / 'model_validation/work/accepted/outputs/run_manifest.json'
        run.parent.mkdir(parents=True)
        call = {'det_collapse_mode': 'auto'}
        run.write_text(json.dumps({'input_sha256': self.source_hash,
            'constructor': {'underdetermined': True}, 'method_call': call,
            'engine': self.engine_hashes}), encoding='utf-8')
        code = run.parent / 'executed_code'
        code.mkdir()
        for name, path in self.engine_paths.items():
            (code / name).write_bytes((self.model / path).read_bytes())
        snapshot = self.model / 'results/regional_snapshot.xlsx'
        snapshot.parent.mkdir()
        snapshot.write_bytes(b'recorded snapshot')
        manifest = {'input_sha256': self.source_hash, 'constructor': {'underdetermined': True},
            'diagnostics': call, 'engine_hashes': {'PPRCalculator.py': 'f' * 64},
            'snapshot_sha256': hashlib.sha256(snapshot.read_bytes()).hexdigest(),
            'evidence': run.relative_to(self.model).as_posix()}
        flags = resolve_audited_configuration(self.model, self.book, manifest)
        self.assertEqual(flags['engine_source_hashes'], self.engine_hashes)
        self.assertEqual(flags['diagnostics'], call)
        self.assertEqual(flags['engine_sources']['PPRCalculator.py'],
            (code / 'PPRCalculator.py').relative_to(self.model).as_posix())
        snapshot.write_bytes(b'changed snapshot')
        with self.assertRaisesRegex(ValueError, 'snapshot'):
            resolve_audited_configuration(self.model, self.book, manifest)

    def test_engine_only_reconstruction_complements_recorded_settings(self):
        self.evidence('current', engine_hashes={
            key: value for key, value in self.engine_hashes.items() if key != 'utils.py'})
        path = self.model / 'results/diagnostics/audited_engine/dependency_identity.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'canonical_model_sha256': self.source_hash,
            'engine_source_hashes': {'utils.py': self.engine_hashes['utils.py']},
            'basis': 'Verified immutable Git dependency reconstruction'}), encoding='utf-8')
        flags = resolve_audited_configuration(self.model, self.book, {})
        self.assertEqual(flags['engine_source_hashes'], self.engine_hashes)

    def test_manifest_is_preferred_and_changed_evidence_invalidates_it(self):
        path = self.evidence('current')
        flags = resolve_audited_configuration(self.model, self.book, {})
        manifest = {'canonical_model_sha256': self.source_hash, 'effective_flags': flags}
        self.assertEqual(resolve_audited_configuration(self.model, self.book, manifest), flags)
        path.write_text(path.read_text(encoding='utf-8') + '\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'evidence changed'):
            resolve_audited_configuration(self.model, self.book, manifest)

    def test_completed_flags_do_not_merge_superseded_legacy_engine_hashes(self):
        self.evidence('current')
        flags = resolve_audited_configuration(self.model, self.book, {})
        manifest = {'canonical_model_sha256': self.source_hash, 'effective_flags': flags,
                    'code_identity': self.engine_hashes,
                    'engine_hashes': {**self.engine_hashes, 'PPRCalculator.py': 'f' * 64}}
        self.assertEqual(resolve_audited_configuration(self.model, self.book, manifest), flags)
        self.book['Overview']['Settings'][1].append(['effective_loader_flags', json.dumps(flags)])
        self.assertEqual(resolve_audited_configuration(self.model, self.book, manifest), flags)

    def test_actual_mc_samples_and_timeout_are_retained(self):
        self.evidence('current', mc_samples=75, method_timeout_seconds=180,
                      method_timeout_overrides_seconds={'MC_new_GE': 600, 'MC_new_TE_EEfix': 600})
        self.book['Selected model groups'] = {'Group SPPR': (
            ['model_id', 'group', 'scope', 'method', 'sppr'],
            [[self.model.name, 'group', 'all', 'MC_new_GE', 2]])}
        self.book['Diagnostics'] = {'mc_diagnostics': (
            ['method', 'n_samples'], [['MC_new_GE', 75], ['unregistered_method', 999]])}
        flags = resolve_audited_configuration(self.model, self.book, {})
        self.assertEqual(flags['mc']['n_samples'], 75)
        self.assertEqual(flags['method_timeout_seconds'], 180)
        self.assertEqual(flags['method_timeout_overrides_seconds']['MC_new_GE'], 600)

    def test_conflicting_mc_samples_do_not_silently_replace_actual_run(self):
        self.evidence('current', mc_samples=75)
        self.book['Selected model groups'] = {'Group SPPR': (
            ['model_id', 'group', 'scope', 'method', 'sppr'],
            [[self.model.name, 'group', 'all', 'MC_new_GE', 2]])}
        self.book['Diagnostics'] = {'mc_diagnostics': (
            ['method', 'n_samples'], [['MC_new_GE', 100]])}
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            resolve_audited_configuration(self.model, self.book, {})


if __name__ == '__main__':
    unittest.main()
