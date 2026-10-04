import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.project_core.validation.runtime_equivalence import verified_runtime_equivalence


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RuntimeEquivalenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.region = Path(self.tmp.name) / 'regions/LME/LME_001'
        self.project = Path(self.tmp.name)
        from tools.project_core.workbooks.workbooks import write_book
        write_book(self.project/'Project.xlsx',{'Models & coverage':{'Models':(['unit_id','model_id'],[])}})
        self.model = self.region / 'papers/P/models/m/model.json'
        self.model.parent.mkdir(parents=True)
        self.evidence = self.region / 'evidence'
        self.evidence.mkdir()
        before = {'group': [{'group_seq': '1', 'pb': '2', 'diet_imp': '0.2',
                            'diet_descr': {'diet': [{'prey_seq': '2', 'proportion': '0.8', 'detritus_fate': '1'}]}},
                           {'group_seq': '2', 'pb': '3', 'diet_imp': '0', 'diet_descr': None}]}
        after = copy.deepcopy(before)
        after['group'][0]['diet_imp'] = '0.18'
        after['group'][0]['diet_descr']['diet'][0]['proportion'] = '0.72'
        self.old = self.evidence / 'old.json'
        self.old.write_text(json.dumps(before))
        self.model.write_text(json.dumps(after))
        self.certificate = {'schema_version': 1, 'model_path': 'papers/P/models/m/model.json',
                            'before_model': {'path': 'evidence/old.json', 'sha256': sha(self.old)},
                            'after_model_sha256': sha(self.model),
                            'settings': {'normalize_DC': True}, 'atol': 1e-12, 'rtol': 0,
                            'components': {}, 'evidence_files': []}
        for component in ['normalized_DC', 'loaded_groups', 'detritus_fate']:
            pair = []
            for variant in ['before', 'after']:
                p = self.evidence / ('runtime_' + variant) / (component + '.csv')
                p.parent.mkdir(exist_ok=True)
                p.write_text('id,value\n1,0.8\n2,NaN\n')
                pair.append({'path': p.relative_to(self.region).as_posix(), 'sha256': sha(p)})
            self.certificate['components'][component] = {'before': pair[0], 'after': pair[1]}
        code = self.project / 'tools/loader.py'
        code.parent.mkdir()
        code.write_text('loader identity')
        self.certificate['code_files'] = [{'path': 'tools/loader.py', 'sha256': sha(code)}]
        proof = self.evidence / 'proof.json'
        proof.write_text(json.dumps({'settings': self.certificate['settings'],
                                     'canonical_before_sha256': sha(self.old),
                                     'canonical_after_sha256': sha(self.model),
                                     'actual_loader_path': 'tools/loader.py',
                                     'loader_code_hashes': {'loader.py': sha(code)},
                                     'runtime_files': {str(p.relative_to(self.evidence)).replace('\\', '/'): sha(p)
                                                       for p in self.evidence.glob('runtime_*/*.csv')}}))
        self.certificate['execution_evidence_root'] = 'evidence'
        self.certificate['settings_evidence'] = {'path': 'evidence/proof.json', 'sha256': sha(proof)}
        self.certificate['evidence_files'] = [self.certificate['settings_evidence']]
        self.certpath = self.model.parent / 'runtime_equivalence.json'
        self.save_certificate()

    def tearDown(self):
        self.tmp.cleanup()

    def save_certificate(self):
        self.certpath.write_text(json.dumps(self.certificate))

    def verify(self):
        return verified_runtime_equivalence(self.region, self.model, sha(self.old))

    def update_proof(self):
        path = self.evidence / 'proof.json'
        proof = json.loads(path.read_text())
        proof['canonical_after_sha256'] = sha(self.model)
        proof['runtime_files'] = {str(p.relative_to(self.evidence)).replace('\\', '/'): sha(p)
                                  for p in self.evidence.glob('runtime_*/*.csv')}
        path.write_text(json.dumps(proof))
        self.certificate['settings_evidence']['sha256'] = sha(path)
        self.save_certificate()

    def test_verified_equivalence_retains_historical_identity(self):
        old_bytes = self.old.read_bytes()
        self.assertTrue(self.verify())
        self.assertEqual(self.old.read_bytes(), old_bytes)

    def test_changed_rate_cannot_use_equivalence_claim(self):
        data = json.loads(self.model.read_text())
        data['group'][0]['pb'] = '2.01'
        self.model.write_text(json.dumps(data))
        self.certificate['after_model_sha256'] = sha(self.model)
        self.update_proof()
        self.assertFalse(self.verify())

    def test_biomass_accumulation_and_predation_changes_are_exempt(self):
        data = json.loads(self.model.read_text())
        data['group'][0].update(biomass_accum='0.25', biomass_accum_rate='0.05', predation='4.2')
        self.model.write_text(json.dumps(data))
        self.certificate['after_model_sha256'] = sha(self.model)
        for variant, values in [('before', '0,0,0,1'), ('after', '0.25,0.05,0.25,4.2')]:
            p = self.evidence / f'runtime_{variant}/loaded_groups.csv'
            p.write_text('id,biomass_accum,biomass_accum_rate,growth,predation,p\n1,' + values + ',2\n')
            self.certificate['components']['loaded_groups'][variant]['sha256'] = sha(p)
        self.update_proof()
        self.assertTrue(self.verify())
        p = self.evidence / 'runtime_after/loaded_groups.csv'
        p.write_text(p.read_text().replace(',2\n', ',2.01\n'))
        self.certificate['components']['loaded_groups']['after']['sha256'] = sha(p)
        self.update_proof()
        self.assertFalse(self.verify())

    def test_ignored_group_field_name_cannot_exempt_diet_matrix_column(self):
        for variant, value in [('before', '0.8'), ('after', '0.7')]:
            p = self.evidence / f'runtime_{variant}/normalized_DC.csv'
            p.write_text('id,predation\n1,' + value + '\n')
            self.certificate['components']['normalized_DC'][variant]['sha256'] = sha(p)
        self.update_proof()
        self.assertFalse(self.verify())

    def test_changed_runtime_diet_cannot_use_claim(self):
        data = json.loads(self.model.read_text())
        data['group'][0]['diet_imp'] = '0.17'
        self.model.write_text(json.dumps(data))
        self.certificate['after_model_sha256'] = sha(self.model)
        self.update_proof()
        self.assertFalse(self.verify())

    def test_mutated_runtime_evidence_or_code_is_rejected(self):
        (self.evidence / 'runtime_after/normalized_DC.csv').write_text('id,value\n1,0.7\n')
        self.assertFalse(self.verify())

    def test_path_escape_and_loose_tolerance_rejected(self):
        self.certificate['before_model']['path'] = '../../../outside.json'
        self.save_certificate()
        self.assertFalse(self.verify())
        self.certificate['before_model']['path'] = 'evidence/old.json'
        self.certificate['atol'] = .01
        self.save_certificate()
        self.assertFalse(self.verify())

    def test_updated_csv_hash_cannot_hide_runtime_difference(self):
        p = self.evidence / 'runtime_after/loaded_groups.csv'
        p.write_text('id,value\n1,0.81\n2,NaN\n')
        self.certificate['components']['loaded_groups']['after']['sha256'] = sha(p)
        self.update_proof()
        self.assertFalse(self.verify())

    def test_mismatched_historical_input_rejected(self):
        self.assertFalse(verified_runtime_equivalence(self.region, self.model, '0' * 64))

    def test_loader_code_and_settings_changes_rejected(self):
        code = self.project / 'tools/loader.py'
        code.write_text('changed loader')
        self.assertFalse(self.verify())
        self.certificate['code_files'][0]['sha256'] = sha(code)
        self.save_certificate()
        self.assertFalse(self.verify())

    def test_missing_execution_binding_rejected(self):
        self.certificate['code_files'] = []
        self.save_certificate()
        self.assertFalse(self.verify())

    def test_unrelated_equal_components_cannot_substitute_for_actual_state(self):
        p = self.evidence / 'unrelated.csv'
        p.write_text('id,value\n1,0.8\n2,NaN\n')
        self.certificate['components']['normalized_DC']['after'] = {'path': 'evidence/unrelated.csv', 'sha256': sha(p)}
        self.save_certificate()
        self.assertFalse(self.verify())

    def test_freshness_and_recalculation_preserve_original_identity(self):
        from tools.workflow_checks.calculations.test_workflow import fixture
        from tools.project_core.workbooks.workbooks import overview, validate_region
        from tools.project_core.calculations.regional import recalculate, set_setting
        book = fixture()
        path = self.region / 'LME_001.xlsx'
        set_setting(book, 'selection_rationale', 'Selected by researcher')
        set_setting(book, 'results_model_sha256', sha(self.old))
        recalculate(book, path)
        validate_region(book, path)
        self.assertEqual(overview(book)['results_model_sha256'], sha(self.old))
        self.certpath.unlink()
        with self.assertRaisesRegex(ValueError, 'model JSON changed'):
            validate_region(book, path)

    def test_settings_and_non_numeric_labels_fail_closed(self):
        self.certificate['settings']['normalize_DC'] = False
        self.save_certificate()
        self.assertFalse(self.verify())

    def test_copied_loader_cannot_substitute_for_executed_path(self):
        import shutil
        project = self.project
        (project / 'copies').mkdir()
        shutil.copyfile(project / 'tools/loader.py', project / 'copies/loader.py')
        self.certificate['code_files'][0]['path'] = 'copies/loader.py'
        self.save_certificate()
        (project / 'tools/loader.py').write_text('changed actual loader')
        self.assertFalse(self.verify())

    def test_copied_runtime_root_cannot_substitute_for_execution_root(self):
        import shutil
        shutil.copytree(self.evidence, self.region / 'copy')
        self.certificate['execution_evidence_root'] = 'copy'
        for component in self.certificate['components'].values():
            for record in component.values():
                record['path'] = record['path'].replace('evidence/', 'copy/')
        self.save_certificate()
        self.assertFalse(self.verify())


if __name__ == '__main__':
    unittest.main()
