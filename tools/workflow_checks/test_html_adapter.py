import gzip,hashlib,json,shutil,subprocess,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from original_atlas_data import fill_annual,detail_from_book
import original_atlas_data
from build_html import atomic_text,linked_layout
from workbooks import YEARS

class HtmlAdapterTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'),'Node is required for the map selection check')
    def test_map_reference_selection_preserves_metric_ranks(self):
        check=Path(__file__).with_name('check_map_selection.js')
        result=subprocess.run([shutil.which('node'),str(check)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)

    def test_bundled_basemap_embeds_geometry_and_keeps_scientific_payload(self):
        root=Path(__file__).resolve().parents[2]
        template=root/'tools/original_html_layout/index.html';before=template.read_bytes()
        payload={'regions':[],'articles':[],'files':[],'sentinel':[None,1.23456789012345]}
        rendered=linked_layout(before.decode('utf-8')).replace('__PPR_DATA__',json.dumps(payload))
        with tempfile.TemporaryDirectory() as directory:
            page=Path(directory)/'index.html';atomic_text(page,rendered)
            self.assertEqual(original_atlas_data.embedded(page,'DB')[0],payload)
            expected=json.loads((root/'common_reference_data/geography/basemaps/ne_50m_land.geojson').read_text(encoding='utf-8'))
            self.assertEqual(original_atlas_data.embedded(page,'BASEMAP_LAND')[0],expected)
        self.assertNotIn('https://{s}.tile.openstreetmap.org',rendered)
        initialization=rendered[rendered.index('const map=L.map('):rendered.index('const regionGroup=')]
        self.assertNotIn('fetch(',initialization)
        self.assertEqual(template.read_bytes(),before)
    @unittest.skipUnless(shutil.which('node'), 'Node.js optional JavaScript smoke check')
    def test_basemap_modes_and_failure_fallback(self):
        root=Path(__file__).resolve().parents[2]
        template=(root/'tools/original_html_layout/index.html').read_text(encoding='utf-8')
        rendered=linked_layout(template).replace('__PPR_DATA__','{"regions":[],"articles":[],"files":[]}')
        with tempfile.TemporaryDirectory() as directory:
            page=Path(directory)/'index.html';atomic_text(page,rendered)
            result=subprocess.run([shutil.which('node'),str(root/'tools/workflow_checks/check_basemap.js'),str(page)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)
    def test_basemap_original_bytes_match_provenance(self):
        directory=Path(__file__).resolve().parents[2]/'common_reference_data/geography/basemaps'
        provenance=json.loads((directory/'provenance.json').read_text(encoding='utf-8'))
        payload=(directory/provenance['file']).read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(),provenance['sha256'])
        self.assertEqual(json.loads(payload)['type'],'FeatureCollection')
    def test_generated_page_uses_lf_and_keeps_embedded_source_newlines(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'page.html'
            payload={'source':'original\r\ncontent '}
            text='<script>\nconst DB='+json.dumps(payload)+';\n</script>\n'
            atomic_text(path,text)
            self.assertEqual(path.read_bytes(),text.encode('utf-8'))
            self.assertEqual(original_atlas_data.embedded(path,'DB')[0],payload)
    def test_historical_paths_follow_relocation_and_removed_links_are_omitted(self):
        self.assertTrue(hasattr(original_atlas_data,'SourcePaths'), 'resolve retained and intentionally removed source paths')
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'original_research_archive').mkdir()
            (root/'original_research_archive/migration.csv').write_text(
                'original_path,retained_path\n'
                'PPRAtlas/archive/regions/LME_001/paper.pdf,original_research_archive/legacy/PPRAtlas/paper.pdf\n'
                'PPRAtlas/obsolete.html,\n')
            provenance=root/'common_reference_data/provenance';provenance.mkdir(parents=True)
            (provenance/'archive_relocation.csv').write_text(
                'old_path,new_path\n'
                'original_research_archive/legacy/PPRAtlas/paper.pdf,original_research_archive/research/study/paper.pdf\n'
                'original_research_archive/legacy/data/LME_001.xlsx,original_research_archive/research/pre_reorganization/data/LME_001.xlsx\n'
                'original_research_archive/legacy/PPRAtlas/index.html,\n')
            resolver=original_atlas_data.SourcePaths(root)
            data={'material_files':[{'relative_path':'archive/regions/LME_001/paper.pdf'},
                                    {'relative_path':'obsolete.html'}],
                  'source_region_workbook':'original_research_archive/legacy/data/LME_001.xlsx',
                  'source':'original_research_archive/legacy/PPRAtlas/index.html',
                  'ppr':[1.25,None]}
            result=resolver.rewrite(data)
            self.assertEqual(result['material_files'],[{'relative_path':'../original_research_archive/research/study/paper.pdf'}])
            self.assertEqual(result['source_region_workbook'],'original_research_archive/research/pre_reorganization/data/LME_001.xlsx')
            self.assertIsNone(result['source'])
            self.assertEqual(result['ppr'],[1.25,None])
            self.assertEqual(data['source_region_workbook'],'original_research_archive/legacy/data/LME_001.xlsx')
    def test_source_context_replaces_historical_html_dependency(self):
        self.assertTrue(hasattr(original_atlas_data,'source_context'), 'load compressed reference payloads instead of historical HTML shells')
        root=Path(__file__).resolve().parents[2]
        catalog,series=original_atlas_data.source_context(root)
        self.assertEqual(len(catalog['regions']),366)
        self.assertEqual(len(series['units']),366)
        self.assertIn('network',catalog)
        self.assertIn('HS_018',series['units'])
        self.assertIn('LME_064',series['units'])
    def test_retained_payload_bytes_match_extraction_evidence(self):
        root=Path(__file__).resolve().parents[2]
        context=root/'common_reference_data/atlas_source_context'
        provenance=json.loads((context/'provenance.json').read_text())
        for record in provenance['files']:
            payload=(context/record['file']).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(),record['file_sha256'])
            if record['file'].endswith('.gz'):
                self.assertEqual(hashlib.sha256(gzip.decompress(payload)).hexdigest(),record['payload_sha256'])
    def test_current_values_replace_old_series(self):
        row={'unidentified':'method','catch_basis':'landings','metric':'ppr','status':'ok',**{y:float(y) for y in YEARS}}
        r=fill_annual([row],{'ppr':[999]*70,'status':'ok','sensitivity':[{'min_tC':123}]*70})
        self.assertEqual(r['ppr'][0],1950);self.assertNotIn('sensitivity',r)
        self.assertEqual(r['catch_bases']['catch']['status'],'unavailable')
        self.assertIsNone(r['catch_bases']['catch']['ppr'][0])
    def test_scope_sensitivity_is_preserved_only_with_current_bounds(self):
        base={'sensitivity':[{'route_evidence':'documented','min_tC':1,'max_tC':2} for _ in YEARS]}
        row={'unidentified':'method','catch_basis':'landings','metric':'min_tC','status':'assessed',**{y:10 for y in YEARS}}
        r=fill_annual([row],base)
        self.assertEqual(r['sensitivity'][0]['min_tC'],10)
        self.assertEqual(r['sensitivity'][0]['route_evidence'],'documented')

if __name__=='__main__':unittest.main()
