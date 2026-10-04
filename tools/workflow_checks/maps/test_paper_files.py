import sys,tempfile,unittest,shutil,subprocess,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from tools.project_core.maps import original_atlas_data as atlas


def paper_sources(root,unit_id,paper_id):
    region=atlas.region_directory(root,unit_id)
    region.mkdir(parents=True,exist_ok=True)
    (region/(unit_id+'.xlsx')).write_bytes(b'canonical region discovery fixture')
    folder=region/'papers'/paper_id/'sources'
    folder.mkdir(parents=True,exist_ok=True)
    return folder


class PaperFileTests(unittest.TestCase):
    def test_canonical_sources_manifest_and_current_models_are_navigable_without_reassessment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_035','P')
            (folder/'main.pdf').write_bytes(b'%PDF-primary')
            (folder/'supplement.xlsx').write_bytes(b'supplement')
            context=folder/'related.pdf';context.write_bytes(b'%PDF-context')
            (folder/'metadata.json').write_text('{}')
            paper_dir=folder.parent
            (paper_dir/'source_manifest.json').write_text('{"administrative_only":true}')
            (paper_dir/'obsolete_extraction.json').write_text('{}')
            model=paper_dir/'models'/'P_current';model.mkdir(parents=True)
            (model/'model.json').write_text('{"groups":[]}')
            (model/'model_notes.md').write_text('Unknown source parameter retained.')
            (model/'extracted_tables').mkdir();(model/'extracted_tables'/'derived.csv').write_text('derived')
            provenance=root/'common_reference_data/provenance';provenance.mkdir(parents=True)
            override={'path':context.relative_to(root).as_posix(),'sha256':atlas.sha(context),'role':'context',
                      'file_label':'Reviewed contextual publication','evidence':'Previously reviewed exact bytes.'}
            (provenance/'paper_file_roles.json').write_text(json.dumps({'schema_version':1,'files':[override]}))
            paper={'article_id':'P__LME_035','unit_id':'LME_035','article_dir':paper_dir.relative_to(root).as_posix(),
                   'material_files':[{'relative_path':'../regions/LME/LME_035/papers/P/source_manifest.json',
                                      'filename':'source_manifest.json','role':'model','file_label':'Model source JSON'},
                                     {'relative_path':'../regions/LME/LME_035/papers/P/obsolete_extraction.json',
                                      'filename':'obsolete_extraction.json','role':'model'}],
                   'quality_score_100':17,'loadability_class':'Printed input not admitted','scientific_value':None}
            atlas.reconcile_paper_files(root,[paper])
            files={f['relative_path']:f for f in paper['material_files']}
            self.assertEqual(set(files),{
                '../regions/LME/LME_035/papers/P/sources/main.pdf',
                '../regions/LME/LME_035/papers/P/sources/supplement.xlsx',
                '../regions/LME/LME_035/papers/P/sources/related.pdf',
                '../regions/LME/LME_035/papers/P/source_manifest.json',
                '../regions/LME/LME_035/papers/P/models/P_current/model.json',
                '../regions/LME/LME_035/papers/P/models/P_current/model_notes.md'})
            self.assertEqual(files['../regions/LME/LME_035/papers/P/sources/related.pdf']['role'],'context')
            self.assertEqual(files['../regions/LME/LME_035/papers/P/source_manifest.json']['role'],'metadata')
            self.assertEqual(files['../regions/LME/LME_035/papers/P/source_manifest.json']['file_label'],'Source manifest JSON')
            self.assertEqual(files['../regions/LME/LME_035/papers/P/models/P_current/model.json']['file_label'],'Current model JSON: P_current')
            self.assertEqual(files['../regions/LME/LME_035/papers/P/models/P_current/model_notes.md']['file_label'],'Model notes: P_current')
            for key in ['main_file_status','supplement_status','model_file_status']:
                self.assertEqual(paper[key],'local_file_present')
            self.assertEqual(paper['quality_score_100'],17)
            self.assertEqual(paper['loadability_class'],'Printed input not admitted')
            self.assertIsNone(paper['scientific_value'])
            before=json.loads(json.dumps(paper));atlas.reconcile_paper_files(root,[paper]);self.assertEqual(paper,before)

    def test_declared_article_folder_is_discovered_when_source_id_is_an_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_038','BUCHARY-1991')
            path=folder/'thesis1999.pdf';path.write_bytes(b'%PDF-thesis')
            paper={'article_id':'INDO-1999__LME_038','unit_id':'LME_038','source_article_id':'INDO-1999',
                   'article_dir':folder.relative_to(root).as_posix(),'material_files':[]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['main_file_status'],'local_file_present')
            self.assertEqual([f['relative_path'] for f in paper['material_files']],['../'+path.relative_to(root).as_posix()])

    def test_declared_article_folder_follows_relocation_and_rejects_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_038','Buchary')
            (folder/'thesis.pdf').write_bytes(b'%PDF-thesis')
            provenance=root/'common_reference_data/provenance';provenance.mkdir(parents=True)
            (provenance/'source_paths.csv').write_text('original_path,retained_path\nold-thesis-folder,'+folder.relative_to(root).as_posix()+'\n')
            paper={'article_id':'P__LME_038','unit_id':'LME_038','article_dir':'old-thesis-folder'}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['main_file_status'],'local_file_present')
            with self.assertRaisesRegex(ValueError,'outside the repository'):
                atlas.reconcile_paper_files(root,[{'article_id':'P__LME_038','unit_id':'LME_038','article_dir':'../outside'}])

    def test_file_discovery_preserves_a_specific_current_loadability_assessment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_038','P')
            (folder/'thesis.pdf').write_bytes(b'%PDF-thesis')
            assessment='Printed source fails strict admission; accepted derived model selected'
            paper={'article_id':'P__LME_038','unit_id':'LME_038','loadability_class':assessment,
                   'quality_rationale':'E — no verified downloadable file. Historical score; source assessed later.'}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['loadability_class'],assessment)
            self.assertNotIn('E — no verified downloadable file',paper['quality_rationale'])
            self.assertIn('Historical score',paper['quality_rationale'])

    def test_file_discovery_preserves_missing_scientific_assessments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_038','P')
            (folder/'thesis.pdf').write_bytes(b'%PDF-thesis')
            paper={'article_id':'P__LME_038','unit_id':'LME_038','loadability_class':None,'quality_rationale':None}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['main_file_status'],'local_file_present')
            self.assertIsNone(paper['loadability_class'])
            self.assertIsNone(paper['quality_rationale'])

    def test_reviewed_context_role_follows_the_source_relocation_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_035','P')
            path=folder/'related.pdf';path.write_bytes(b'%PDF-context')
            reference=root/'common_reference_data';provenance=reference/'provenance';provenance.mkdir(parents=True)
            old='old/source-context.pdf';new=path.relative_to(root).as_posix()
            (provenance/'source_paths.csv').write_text('original_path,retained_path\n'+old+','+new+'\n')
            override={'path':old,'sha256':atlas.sha(path),'role':'context',
                      'file_label':'Reviewed context','evidence':'Exact original source identity.'}
            (reference/'provenance/paper_file_roles.json').write_text(json.dumps({'schema_version':1,'files':[override]}))
            paper={'article_id':'P__LME_035','unit_id':'LME_035','material_files':[
                {'relative_path':'../'+old,'role':'main','sha256':atlas.sha(path)}]}
            paper=atlas.SourcePaths(root).rewrite(paper)
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['material_files'][0]['relative_path'],'../'+new)
            self.assertEqual(paper['material_files'][0]['role'],'context')
            self.assertEqual(paper['main_file_status'],'not_found')

    def test_reviewed_context_pdf_does_not_count_as_missing_focal_article(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_035','Christensen-1998')
            path=folder/'Pauly-Chuenpagdee-2003.pdf';path.write_bytes(b'%PDF-related-publication')
            reference=root/'common_reference_data';(reference/'provenance').mkdir(parents=True)
            override={'path':path.relative_to(root).as_posix(),'sha256':atlas.sha(path),
                      'role':'context','file_label':'Context: Pauly and Chuenpagdee (2003)',
                      'evidence':'Different publication, retained only for geographical context.'}
            (reference/'provenance/paper_file_roles.json').write_text(json.dumps({'schema_version':1,'files':[override]}))
            paper={'article_id':'Christensen-1998__LME_035','unit_id':'LME_035'}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['material_files'][0]['role'],'context')
            self.assertEqual(paper['material_files'][0]['file_label'],override['file_label'])
            self.assertEqual(paper['main_file_status'],'not_found')
            self.assertEqual(paper['downloaded_file_count'],1)
            before=paper.copy();atlas.reconcile_paper_files(root,[paper]);self.assertEqual(paper,before)

    def test_changed_context_bytes_cannot_inherit_review_or_become_focal_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_035','P')
            path=folder/'related.pdf';path.write_bytes(b'%PDF-old')
            reference=root/'common_reference_data';(reference/'provenance').mkdir(parents=True)
            override={'path':path.relative_to(root).as_posix(),'sha256':atlas.sha(path),
                      'role':'context','file_label':'Reviewed context','evidence':'Reviewed original bytes.'}
            (reference/'provenance/paper_file_roles.json').write_text(json.dumps({'schema_version':1,'files':[override]}))
            path.write_bytes(b'%PDF-changed')
            paper={'article_id':'P__LME_035','unit_id':'LME_035'}
            atlas.reconcile_paper_files(root,[paper]);record=paper['material_files'][0]
            self.assertEqual(record['role'],'source')
            self.assertEqual(record['identity_status'],'not_reassessed')
            self.assertEqual(paper['main_file_status'],'not_found')
            self.assertIn('changed',record['validation'])

    def test_retrieval_logs_are_excluded_from_new_and_existing_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_022','P')
            names=['accession_retrieval.json','supplement_retrieval_log.json']
            for name in names:(folder/name).write_text('{}')
            paper={'article_id':'P__LME_022','unit_id':'LME_022','material_files':[
                {'relative_path':'../regions/LME/LME_022/papers/P/sources/accession_retrieval.json','role':'model'}]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['material_files'],[])
            self.assertEqual(paper['model_file_status'],'not_found')

    def test_changed_bytes_downgrade_verification_and_preserve_prior_assessment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_001','P')
            path=folder/'paper.pdf';path.write_bytes(b'%PDF-original')
            old_hash=atlas.sha(path)
            paper={'article_id':'P__LME_001','unit_id':'LME_001','material_files':[
                {'relative_path':'../regions/LME/LME_001/papers/P/sources/paper.pdf','role':'main',
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
            root=Path(tmp);folder=paper_sources(root,'LME_001','P')
            paper={'article_id':'P__LME_001','unit_id':'LME_001','main_file_status':'local_file_present',
                'supplement_status':'local_file_present','model_file_status':'local_file_present',
                'material_files':[{'relative_path':'../regions/LME/LME_001/papers/P/sources/missing.pdf','role':'main'}]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['downloaded_file_count'],0)
            for key in ['main_file_status','supplement_status','model_file_status']:
                self.assertEqual(paper[key],'not_found')

    def test_native_eweaccdb_attachment_is_discovered_as_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_014','PAT-2023')
            (folder/'native.eweaccdb').write_bytes(b'native-model-fixture')
            paper={'article_id':'PAT-2023__LME_014','unit_id':'LME_014','material_files':[]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['downloaded_file_count'],1)
            self.assertEqual(paper['material_files'][0]['role'],'model')
            self.assertEqual(paper['model_file_status'],'local_file_present')

    def test_original_model_json_is_linked_but_administrative_json_is_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_027','CAN-2009')
            for name in ['27_118_Northwest_Africa_(1987).json','metadata.json','retrieval.json','source-facts.json']:
                (folder/name).write_text('{}')
            paper={'article_id':'CAN-2009__LME_027','unit_id':'LME_027','material_files':[]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['downloaded_file_count'],1)
            self.assertEqual(paper['material_files'][0]['role'],'model')
            self.assertEqual(paper['model_file_status'],'local_file_present')

    @unittest.skipUnless(shutil.which('node'),'Node.js optional display check')
    def test_map_total_includes_discovered_sources_and_deduplicates_shared_files(self):
        from tools.project_core.maps.build_html import linked_layout
        template=Path(__file__).resolve().parents[2]/'project_core/maps/original_html_layout/index.html'
        page=linked_layout(template.read_text(encoding='utf-8'))
        code=next(line for line in page.splitlines() if line.startswith("document.querySelector('#kpiArticles').textContent="))
        script="const elements={}; const document={querySelector:s=>elements[s]??={}}; const articles=[],regions=[]; const files=[{status:'downloaded_verified',sha256:'a'},{status:'local_file_present',sha256:'b'},{status:'local_file_present',sha256:'b'}];\n"+code+"\nconsole.log(elements['#kpiFiles'].textContent);"
        result=subprocess.run([shutil.which('node'),'-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'2')

    def test_same_publication_can_link_source_archived_under_another_region(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_049','KUR-2019')
            (folder/'paper.pdf').write_bytes(b'%PDF-test')
            paper={'article_id':'KUR-2019__LME_051','unit_id':'LME_051','source_article_id':'KUR-2019','material_files':[]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(paper['downloaded_file_count'],1)
            self.assertEqual(paper['material_files'][0]['relative_path'],'../regions/LME/LME_049/papers/KUR-2019/sources/paper.pdf')

    def test_downloads_replace_stale_empty_inventory_without_changing_scores(self):
        self.assertTrue(hasattr(atlas,'reconcile_paper_files'))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=paper_sources(root,'LME_049','KUR-2025')
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
            root=Path(tmp);folder=paper_sources(root,'LME_001','P')
            (folder/'paper.pdf').write_bytes(b'%PDF-test')
            paper={'article_id':'P__LME_001','unit_id':'LME_001','source_article_id':'P','material_files':[
                {'relative_path':'../regions/LME/LME_001/papers/P/sources/paper.pdf','filename':'paper.pdf','role':'main','identity_status':'consistent'},
                {'relative_path':'../regions/LME/LME_001/papers/P/sources/missing.pdf','filename':'missing.pdf','role':'main'}]}
            atlas.reconcile_paper_files(root,[paper])
            self.assertEqual(len(paper['material_files']),1)
            self.assertEqual(paper['material_files'][0]['identity_status'],'consistent')

if __name__=='__main__':unittest.main()
