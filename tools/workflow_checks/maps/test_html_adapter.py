import copy,gzip,hashlib,json,shutil,subprocess,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from tools.project_core.maps.original_atlas_data import fill_annual,detail_from_book
from tools.project_core.maps import original_atlas_data
from tools.project_core.maps.build_html import atomic_text,linked_layout
from tools.project_core.workbooks.workbooks import YEARS

class HtmlAdapterTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_map_researcher_validation_filter(self):
        root=Path(__file__).resolve().parents[3]
        rendered=linked_layout((root/'tools/project_core/maps/original_html_layout/index.html').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as directory:
            page=Path(directory)/'index.html';atomic_text(page,rendered)
            result=subprocess.run([shutil.which('node'),str(Path(__file__).with_name('check_map_validation_filter.js')),str(page)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)

    def test_group_efficiencies_use_current_selection_and_retained_alternative(self):
        from tools.project_core.workbooks.workbooks import write_book
        import openpyxl
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);region=root/'regions/LME/LME_001';region.mkdir(parents=True)
            write_book(region/'LME_001.xlsx',{
                'Overview':{'Settings':(['field','value'],[['selected_model_id','current']])},
                'Selected model groups':{'Groups':(['group_name','ge','ee'],[['Fish',.25,0],['Missing',None,None]])}})
            for mid in ['current','alternative','absent']:
                model=region/'papers/P/models'/mid/'model.json';model.parent.mkdir(parents=True);model.write_text('{}')
            source=region/'papers/P/models/alternative/sppr_source.xlsx'
            book=openpyxl.Workbook();sheet=book.active;sheet.title='groups_df'
            sheet.append(['group_name','ge','ee']);sheet.append(['Fish',.4,.8]);book.save(source);book.close()
            units={'LME_001':{'models':[
                {'id':'current','group_data':{'groups':[{'id':'Fish','te':0},{'id':'Missing','te':None}]}},
                {'id':'alternative','group_data':{'groups':[{'id':'Fish','te':.32}]}},
                {'id':'absent','group_data':{'groups':[{'id':'Fish','te':None}]}},
            ]}}
            before=copy.deepcopy(units)
            original_atlas_data.add_group_efficiencies(root,units)
            current,alternative,absent=units['LME_001']['models']
            self.assertEqual((current['group_data']['groups'][0]['ge'],current['group_data']['groups'][0]['ee']),(.25,0))
            self.assertEqual((alternative['group_data']['groups'][0]['ge'],alternative['group_data']['groups'][0]['ee']),(.4,.8))
            self.assertIsNone(current['group_data']['groups'][1]['ge'])
            self.assertIsNone(absent['group_data']['groups'][0]['ee'])
            for model in units['LME_001']['models']:
                for group in model['group_data']['groups']:
                    group.pop('ge');group.pop('ee')
            self.assertEqual(units,before,'Enrichment preserves TE and all existing data')

    @unittest.skipUnless(shutil.which('node'), 'Node required for calculation boundary')
    def test_reviewed_source_mapping_without_coefficients_keeps_group_controls(self):
        book={
            'Catch':{'Catch':(['taxon','catch_basis','unidentified',*YEARS],[['fish','landings',False,*([1.]*70)]])},
            'Classic PPR':{'Taxa':(['taxon','tl','sppr'],[['fish',2.,90.]])},
            'Selected model groups':{'Groups':(['group_name'],[['Fish'],['Producer']]),'Group SPPR':(['model_id','group','scope','method','sppr'],[])},
            'PPR':{'Matching':(['model_id','taxon','group','weight'],[['m','fish','Fish',1.]])},
            'Diagnostics':{'model_health':(['config_TE_option','status'],[['GE','NOT_RUN']])}}
        inputs,model=detail_from_book(book,'U','m')
        self.assertTrue(model['verified'],'Verified mapping controls must not require invented coefficients')
        self.assertEqual(model['group_data']['methods'],[])
        self.assertEqual(model['group_data']['mappings'],[[[0,1.]]])
        self.assertEqual(model['health']['GE']['status'],'NOT_RUN')
        payload={'unit':{**inputs,'models':[model]},'state':{'unit_id':'U','mode':'ppr','scope':'all','year':2019,'catch_basis':'landings','unidentified':'method','group_selections':{'U::m':['Fish']}}}
        script="""const fs=require('node:fs'),assert=require('node:assert/strict');
const metrics=require(process.argv[1]),p=JSON.parse(fs.readFileSync(0,'utf8'));
const blocked=metrics.evaluate(p.unit,0,{...p.state,method:'new_GE'});
assert.equal(blocked.value,null);assert.doesNotMatch(blocked.status,/Mapping workbook not verified/);
const classic=metrics.evaluate(p.unit,0,{...p.state,method:'simple trophic chain'});
assert.equal(classic.value,10);assert.equal(classic.group_selection.active,true);
"""
        module=Path(__file__).resolve().parents[2]/'project_core/maps/original_html_layout/calculation_modules/network_metrics.js'
        result=subprocess.run([shutil.which('node'),'-e',script,str(module)],input=json.dumps(payload),capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)

    def test_flattened_diagnostic_config_keeps_method_identity(self):
        book={'Diagnostics':{'model_health':(['config_TE_option','status','divergence_b','divergence_rho_living','model_input_is_model_balanced','balance_is_balanced'],[['TE','FAIL',1.2,1.1,False,False]])}}
        _,model=detail_from_book(book,'U','m')
        self.assertEqual(model['health']['TE']['b'],1.2)
        self.assertEqual(model['health']['TE']['rho_living'],1.1)
        self.assertIn('TE: FAIL',original_atlas_data.review_flags(book))

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_provisional_display_is_numeric_and_flagged(self):
        root=Path(__file__).resolve().parents[3]
        rendered=linked_layout((root/'tools/project_core/maps/original_html_layout/index.html').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as directory:
            page=Path(directory)/'index.html';atomic_text(page,rendered)
            trend=Path(directory)/'trends.html';atomic_text(trend,linked_layout((root/'tools/project_core/maps/original_html_layout/trends.html').read_text(encoding='utf-8')))
            result=subprocess.run([shutil.which('node'),str(Path(__file__).with_name('check_provisional.js')),str(page),str(trend)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)
    @unittest.skipUnless(shutil.which('node'),'Node is required for the map selection check')
    def test_map_reference_selection_preserves_metric_ranks(self):
        check=Path(__file__).with_name('check_map_selection.js')
        result=subprocess.run([shutil.which('node'),str(check)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)

    @unittest.skipUnless(shutil.which('node'),'Node is required for the model-switch check')
    def test_map_model_switch_preserves_open_selection(self):
        check=Path(__file__).with_name('check_map_model_switch.js')
        result=subprocess.run([shutil.which('node'),str(check)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)

    @unittest.skipUnless(shutil.which('node'),'Node is required for the simple-chain model-switch check')
    def test_simple_chain_model_switch_keeps_selector_and_saved_groups(self):
        root=Path(__file__).resolve().parents[3]
        check=Path(__file__).with_name('check_map_simple_model_switch.js')
        rendered=linked_layout((root/'tools/project_core/maps/original_html_layout/index.html').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as directory:
            page=Path(directory)/'index.html';atomic_text(page,rendered)
            result=subprocess.run([shutil.which('node'),str(check),str(page)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)

    def test_bundled_basemap_embeds_geometry_and_keeps_scientific_payload(self):
        root=Path(__file__).resolve().parents[3]
        template=root/'tools/project_core/maps/original_html_layout/index.html';before=template.read_bytes()
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
        root=Path(__file__).resolve().parents[3]
        template=(root/'tools/project_core/maps/original_html_layout/index.html').read_text(encoding='utf-8')
        rendered=linked_layout(template).replace('__PPR_DATA__','{"regions":[],"articles":[],"files":[]}')
        with tempfile.TemporaryDirectory() as directory:
            page=Path(directory)/'index.html';atomic_text(page,rendered)
            result=subprocess.run([shutil.which('node'),str(root/'tools/workflow_checks/maps/check_basemap.js'),str(page)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)
    def test_basemap_original_bytes_match_provenance(self):
        directory=Path(__file__).resolve().parents[3]/'common_reference_data/geography/basemaps'
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
            provenance=root/'common_reference_data/provenance';provenance.mkdir(parents=True)
            (provenance/'source_paths.csv').write_text(
                'original_path,retained_path\n'
                'PPRAtlas/archive/regions/LME/LME_001/paper.pdf,original_research_archive/legacy/PPRAtlas/paper.pdf\n'
                'PPRAtlas/obsolete.html,\n'
                'original_research_archive/legacy/PPRAtlas/paper.pdf,research/study/inputs/paper.pdf\n'
                'original_research_archive/legacy/data/LME_001.xlsx,research/pre_reorganization/inputs/LME_001.xlsx\n'
                'original_research_archive/legacy/PPRAtlas/index.html,\n')
            resolver=original_atlas_data.SourcePaths(root)
            data={'material_files':[{'relative_path':'archive/regions/LME/LME_001/paper.pdf'},
                                    {'relative_path':'obsolete.html'}],
                  'source_region_workbook':'original_research_archive/legacy/data/LME_001.xlsx',
                  'source':'original_research_archive/legacy/PPRAtlas/index.html',
                  'ppr':[1.25,None]}
            result=resolver.rewrite(data)
            self.assertEqual(result['material_files'],[{'relative_path':'../research/study/inputs/paper.pdf'}])
            self.assertEqual(result['source_region_workbook'],'research/pre_reorganization/inputs/LME_001.xlsx')
            self.assertIsNone(result['source'])
            self.assertEqual(result['ppr'],[1.25,None])
            self.assertEqual(data['source_region_workbook'],'original_research_archive/legacy/data/LME_001.xlsx')
    def test_source_context_replaces_historical_html_dependency(self):
        self.assertTrue(hasattr(original_atlas_data,'source_context'), 'load compressed reference payloads instead of historical HTML shells')
        root=Path(__file__).resolve().parents[3]
        catalog,series=original_atlas_data.source_context(root)
        self.assertEqual(len(catalog['regions']),366)
        self.assertEqual(len(series['units']),366)
        self.assertIn('network',catalog)
        self.assertIn('HS_018',series['units'])
        self.assertIn('LME_064',series['units'])
    def test_retained_payload_bytes_match_extraction_evidence(self):
        root=Path(__file__).resolve().parents[3]
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
