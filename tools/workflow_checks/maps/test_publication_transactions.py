"""A failed page build restores owned outputs without overwriting author edits."""
import tempfile
import unittest
from pathlib import Path

from tools.project_core.registry.publication import publication_transaction
from tools.project_core.maps.build_html import atomic_text
from tools.project_core.workbooks.workbooks import write_book,sha


class PublicationTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.project=self.root/'Project.xlsx'
        write_book(self.project,{'Models & coverage':{'Models':(['unit_id','model_id'],[])}})
        self.region=self.root/'regional.xlsx';self.region.write_bytes(b'original regional')
        self.page=self.root/'interactive_map/index.html';self.page.parent.mkdir();self.page.write_text('original page')

    def test_partial_page_failure_restores_owned_science_and_central_state(self):
        paths=[self.project,self.region,self.page];before={path:path.read_bytes() for path in paths}
        with self.assertRaisesRegex(RuntimeError,'page failure'):
            with publication_transaction(self.root,[self.region]) as transaction:
                self.region.write_bytes(b'calculated');transaction.checkpoint([self.region])
                self.project.write_bytes(b'updated central');transaction.checkpoint([self.project])
                atomic_text(self.page,'partially generated page')
                atomic_text(self.page.parent/'trends.html','new output')
                raise RuntimeError('page failure')
        self.assertEqual({path:path.read_bytes() for path in paths},before)
        self.assertFalse((self.page.parent/'trends.html').exists())

    def test_concurrent_author_edit_is_preserved(self):
        with self.assertRaisesRegex(RuntimeError,'concurrent author edits were preserved'):
            with publication_transaction(self.root,[self.region]):
                self.project.write_bytes(b'concurrent researcher edit')
                raise ValueError('input changed before central write')
        self.assertEqual(self.project.read_bytes(),b'concurrent researcher edit')

    def test_other_region_edit_is_not_adopted_by_a_central_checkpoint(self):
        with self.assertRaisesRegex(RuntimeError,'concurrent author edits were preserved'):
            with publication_transaction(self.root,[self.region]) as transaction:
                self.region.write_bytes(b'concurrent regional edit')
                self.project.write_bytes(b'generated central')
                transaction.checkpoint([self.project])
                raise ValueError('later publication failed')
        self.assertEqual(self.region.read_bytes(),b'concurrent regional edit')

    def package(self):
        region=self.root/'regions/LME/LME_001'
        model=region/'papers/p/models/m';model.mkdir(parents=True)
        (model/'model.json').write_text('{}')
        (region/'LME_001.xlsx').write_bytes(b'regional workbook')
        source=model/'sppr_source.xlsx';source.write_bytes(b'original source')
        evidence=model/'results/diagnostics/method_coverage/owned.json'
        evidence.parent.mkdir(parents=True)
        write_book(self.project,{'Models & coverage':{'Models':(
            ['unit_id','model_id','researcher_review_status'],[['LME_001','m','Validated by researcher']])}})
        return source,evidence

    def test_owned_package_rolls_back_but_unrelated_new_evidence_survives(self):
        source,evidence=self.package();other=evidence.with_name('researcher-note.txt')
        with self.assertRaisesRegex(RuntimeError,'page failure'):
            with publication_transaction(self.root) as transaction:
                source.write_bytes(b'generated source');evidence.write_text('generated evidence')
                transaction.checkpoint([source,evidence])
                other.write_text('concurrent researcher note')
                raise RuntimeError('page failure')
        self.assertEqual(source.read_bytes(),b'original source')
        self.assertFalse(evidence.exists())
        self.assertEqual(other.read_text(),'concurrent researcher note')

    def test_concurrent_edit_to_owned_package_or_new_evidence_is_preserved(self):
        source,evidence=self.package()
        with self.assertRaisesRegex(RuntimeError,'concurrent author edits were preserved'):
            with publication_transaction(self.root) as transaction:
                source.write_bytes(b'generated source');evidence.write_text('generated evidence')
                transaction.checkpoint([source,evidence])
                source.write_bytes(b'new researcher source');evidence.write_text('new researcher evidence')
                raise RuntimeError('page failure')
        self.assertEqual(source.read_bytes(),b'new researcher source')
        self.assertEqual(evidence.read_text(),'new researcher evidence')

    def test_produced_hash_does_not_adopt_later_author_edit(self):
        source,evidence=self.package()
        with self.assertRaisesRegex(RuntimeError,'concurrent author edits were preserved'):
            with publication_transaction(self.root) as transaction:
                source.write_bytes(b'generated source');produced=sha(source)
                source.write_bytes(b'new researcher source')
                transaction.checkpoint([source],fingerprints={str(source):produced})
                raise RuntimeError('page failure')
        self.assertEqual(source.read_bytes(),b'new researcher source')

    def test_page_writer_preserves_concurrent_edit_before_replace(self):
        with self.assertRaisesRegex(RuntimeError,'concurrent author edits were preserved'):
            with publication_transaction(self.root):
                self.page.write_text('new researcher page')
                atomic_text(self.page,'generated page')
        self.assertEqual(self.page.read_text(),'new researcher page')

    def test_nested_publisher_rollback_remains_owned_by_outer_transaction(self):
        with self.assertRaisesRegex(RuntimeError,'outer failure'):
            with publication_transaction(self.root):
                atomic_text(self.page,'outer generated page')
                with self.assertRaisesRegex(RuntimeError,'inner failure'):
                    with publication_transaction(self.root):
                        atomic_text(self.page,'inner generated page')
                        raise RuntimeError('inner failure')
                self.assertEqual(self.page.read_text(),'outer generated page')
                raise RuntimeError('outer failure')
        self.assertEqual(self.page.read_text(),'original page')


if __name__=='__main__':unittest.main()
