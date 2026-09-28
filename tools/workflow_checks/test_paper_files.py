import sys,tempfile,unittest,shutil,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import original_atlas_data as atlas


class PaperFileTests(unittest.TestCase):
    def test_retrieval_logs_are_excluded_from_new_and_existing_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'regions/LME_022/papers/P';folder.mkdir(parents=True)
            names=['accession_retrieval.json','supplement_retrieval_log.json']
            for name in names:(folder/name).write_text('{}')
            paper={'article_id':'P__LME_022','unit_id':'LME_022','material_files':[
                {'relative_path':'../regions/LME_022/papers/P/accession_retrieval.json','role':'model'}]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['material_files'],[])
            self.assertEqual(paper['model_file_status'],'not_found')

    def test_changed_bytes_downgrade_verification_and_preserve_prior_assessment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'regions/LME_001/papers/P';folder.mkdir(parents=True)
            path=folder/'paper.pdf';path.write_bytes(b'%PDF-original')
            old_hash=atlas.sha(path)
            paper={'article_id':'P__LME_001','unit_id':'LME_001','material_files':[
                {'relative_path':'../regions/LME_001/papers/P/paper.pdf','role':'main',
                 'status':'downloaded_verified','sha256':old_hash,'size_bytes':path.stat().st_size,
                 'identity_status':'consistent','validation':'Previous exact bytes checked'}]}
            path.write_bytes(b'%PDF-replacement-with-different-content')
            atlas.reconcile_paper_files(root,[paper]);record=paper['material_files'][0]
            self.assertEqual(record['sha256'],atlas.sha(path))
            self.assertEqual(record['size_bytes'],path.stat().st_size)
            self.assertEqual(record['status'],'local_file_present')
            self.assertEqual(record['identity_status'],'not_reassessed')
            self.assertEqual(record['prior_file_assessment']['sha256'],old_hash)

    def test_removing_last_file_clears_all_presence_statuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'regions/LME_001/papers/P';folder.mkdir(parents=True)
            paper={'article_id':'P__LME_001','unit_id':'LME_001','main_file_status':'local_file_present',
                'supplement_status':'local_file_present','model_file_status':'local_file_present',
                'material_files':[{'relative_path':'../regions/LME_001/papers/P/missing.pdf','role':'main'}]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['downloaded_file_count'],0)
            for key in ['main_file_status','supplement_status','model_file_status']:
                self.assertEqual(paper[key],'not_found')

    def test_native_eweaccdb_attachment_is_discovered_as_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'regions/LME_014/papers/PAT-2023';folder.mkdir(parents=True)
            (folder/'native.eweaccdb').write_bytes(b'native-model-fixture')
            paper={'article_id':'PAT-2023__LME_014','unit_id':'LME_014','material_files':[]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['downloaded_file_count'],1)
            self.assertEqual(paper['material_files'][0]['role'],'model')
            self.assertEqual(paper['model_file_status'],'local_file_present')

    def test_original_model_json_is_linked_but_administrative_json_is_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'regions/LME_027/papers/CAN-2009';folder.mkdir(parents=True)
            for name in ['27_118_Northwest_Africa_(1987).json','metadata.json','retrieval.json','source-facts.json']:
                (folder/name).write_text('{}')
            paper={'article_id':'CAN-2009__LME_027','unit_id':'LME_027','material_files':[]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['downloaded_file_count'],1)
            self.assertEqual(paper['material_files'][0]['role'],'model')
            self.assertEqual(paper['model_file_status'],'local_file_present')

    @unittest.skipUnless(shutil.which('node'),'Node.js optional display check')
    def test_map_total_includes_discovered_sources_and_deduplicates_shared_files(self):
        from build_html import linked_layout
        template=Path(__file__).resolve().parents[1]/'original_html_layout/index.html'
        page=linked_layout(template.read_text(encoding='utf-8'))
        code=next(line for line in page.splitlines() if line.startswith("document.querySelector('#kpiArticles').textContent="))
        script="const elements={}; const document={querySelector:s=>elements[s]??={}}; const articles=[],regions=[]; const files=[{status:'downloaded_verified',sha256:'a'},{status:'local_file_present',sha256:'b'},{status:'local_file_present',sha256:'b'}];\n"+code+"\nconsole.log(elements['#kpiFiles'].textContent);"
        result=subprocess.run([shutil.which('node'),'-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'2')

    def test_same_publication_can_link_source_archived_under_another_region(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'regions/LME_049/papers/KUR-2019';folder.mkdir(parents=True)
            (folder/'paper.pdf').write_bytes(b'%PDF-test')
            paper={'article_id':'KUR-2019__LME_051','unit_id':'LME_051','source_article_id':'KUR-2019','material_files':[]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['downloaded_file_count'],1)
            self.assertEqual(paper['material_files'][0]['relative_path'],'../regions/LME_049/papers/KUR-2019/paper.pdf')

    def test_downloads_replace_stale_empty_inventory_without_changing_scores(self):
        self.assertTrue(hasattr(atlas,'reconcile_paper_files'))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'regions/LME_049/papers/KUR-2025';folder.mkdir(parents=True)
            for name in ['main.pdf','mmc1.docx','metadata.json','README.md','footprint.geojson']:
                (folder/name).write_text('source bytes')
            (folder/'extracted').mkdir();(folder/'extracted/derived.csv').write_text('derived')
            paper={'article_id':'KUR-2025__LME_049','unit_id':'LME_049','source_article_id':'KUR-2025',
                   'material_files':[],'download_status':'no_verified_file','downloaded_file_count':0,
                   'download_failure_reason':'No source file verified in this archive.',
                   'loadability_class':'E — no verified downloadable file','quality_score_100':25,
                   'quality_rationale':'E — no verified downloadable file. Loadability 0/55; cap 25.'}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['downloaded_file_count'],2)
            self.assertEqual({f['filename'] for f in paper['material_files']},{'main.pdf','mmc1.docx'})
            self.assertEqual(paper['download_status'],'local_files_available')
            self.assertFalse(paper['download_failure_reason'])
            self.assertNotIn('no verified downloadable file',paper['quality_rationale'])
            self.assertEqual(paper['quality_score_100'],25)
            for f in paper['material_files']:
                self.assertTrue((root/'interactive_map'/f['relative_path']).is_file())
            before=paper.copy();atlas.reconcile_paper_files(root,[paper]);self.assertEqual(paper,before)

    def test_retains_verified_provenance_deduplicates_and_drops_missing_links(self):
        self.assertTrue(hasattr(atlas,'reconcile_paper_files'))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'regions/LME_001/papers/P';folder.mkdir(parents=True)
            (folder/'paper.pdf').write_bytes(b'%PDF-test')
            paper={'article_id':'P__LME_001','unit_id':'LME_001','source_article_id':'P','material_files':[
                {'relative_path':'../regions/LME_001/papers/P/paper.pdf','filename':'paper.pdf','role':'main','identity_status':'consistent'},
                {'relative_path':'../regions/LME_001/papers/P/missing.pdf','filename':'missing.pdf','role':'main'}]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(len(paper['material_files']),1)
            self.assertEqual(paper['material_files'][0]['identity_status'],'consistent')

if __name__=='__main__':unittest.main()
