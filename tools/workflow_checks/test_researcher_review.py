import copy, gzip, json, sys, tempfile, unittest, zipfile
from pathlib import Path
from xml.etree import ElementTree as etree
import openpyxl
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from researcher_review import (FIELDS, HEADINGS, NOTE, STATUS, approved_review, read_report,
                              register_review, sha, table_rows)
from workbooks import read_book, records, write_book
from regional import recalculate, set_setting
from test_workflow import fixture
from update_project import update
from build_html import linked_layout, relayout, refresh_reviews

ROOT = Path(__file__).resolve().parents[2]
MODEL = '36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)'
REPORT = ROOT / 'regions/LME_036' / ('Model_validation_' + MODEL + '.docx')
ARABIAN_MODEL = '32_1_Arabian_Sea_off_Karnataka_(2000)'
ARABIAN_REPORT = ROOT/'regions/LME_032'/('Model_validation_'+ARABIAN_MODEL+'.docx')

class ResearcherReviewTests(unittest.TestCase):
    def test_word_manual_breaks_tabs_and_hyperlinks_preserve_visible_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);report=root/'regions/LME_032/review.docx';report.parent.mkdir(parents=True)
            w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            r='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
            with zipfile.ZipFile(ARABIAN_REPORT) as source:
                document=etree.fromstring(source.read('word/document.xml'))
                relationships=etree.fromstring(source.read('word/_rels/document.xml.rels'))
            for parent in document.iter():
                for link in list(parent):
                    if link.tag==w+'hyperlink':
                        index=list(parent).index(link)
                        for child in list(link):parent.insert(index,child);index+=1
                        parent.remove(link)
            cell=next(row.findall(w+'tc')[1] for row in document.iter(w+'tr')
                      if len(row.findall(w+'tc'))==2 and ''.join(t.text or '' for t in row.findall(w+'tc')[0].iter(w+'t'))=='GE diagnostics')
            cell[:]=[];p=etree.SubElement(cell,w+'p')
            def run(parent,items):
                run=etree.SubElement(parent,w+'r')
                for tag,value in items:
                    element=etree.SubElement(run,w+tag);element.text=value
            run(p,[('t','basal-source columns.'),('br',None)])
            run(p,[('t','rho_living = 0.32 ')])
            link=etree.SubElement(p,w+'hyperlink',{r+'id':'rIdBreakFixture'})
            run(link,[('t','Source'),('br',None),('t','detail')])
            run(p,[('tab',None),('t','End'),('cr',None),('t','Last')])
            etree.SubElement(relationships,'{http://schemas.openxmlformats.org/package/2006/relationships}Relationship',
                Id='rIdBreakFixture',Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
                Target='https://example.org/evidence#exact',TargetMode='External')
            with zipfile.ZipFile(report,'w') as target:
                target.writestr('word/document.xml',etree.tostring(document))
                target.writestr('word/_rels/document.xml.rels',etree.tostring(relationships))
            summary=read_report(root,report,ARABIAN_MODEL)[2]
            row=summary['sections'][1]['rows'][0]
            expected='basal-source columns.\nrho_living = 0.32 Source\ndetail\tEnd\nLast'
            self.assertEqual(row['text'],expected)
            self.assertEqual(''.join(s['text'] for s in row['paragraphs'][0]),expected)
            self.assertEqual(next(s for s in row['paragraphs'][0] if s.get('href')),
                             {'text':'Source\ndetail','href':'https://example.org/evidence#exact'})

    def test_arabian_review_identity_appendix_and_exclusion_note_are_source_specific(self):
        protected=sha(ARABIAN_REPORT)
        name,date,summary=read_report(ROOT,ARABIAN_REPORT,ARABIAN_MODEL)
        self.assertEqual((name,date),('Ido Carmel','2026-10-01'))
        self.assertEqual(summary['sections'][-1]['appendix_path'],'regions/LME_032/LME032_taxon_mapping_appendix.xlsx')
        self.assertTrue((ROOT/summary['sections'][-1]['appendix_path']).is_file())
        self.assertEqual(summary['note'],'Following researcher review, marine mammals are excluded from displayed PPR. Model loading, diagnostics and saved workbook calculations retain all groups.')
        self.assertIn('basal-source columns.\nrho_living',summary['sections'][1]['rows'][0]['text'])
        self.assertIn('b = 0.52\nDetritus',summary['sections'][1]['rows'][0]['text'])
        self.assertIn('\nB. Study area covered',summary['sections'][3]['rows'][0]['text'])
        self.assertEqual(sha(ARABIAN_REPORT),protected)
        with self.assertRaisesRegex(ValueError,'different model'):
            read_report(ROOT,ARABIAN_REPORT,ARABIAN_MODEL+'suffix')

    def test_actual_review_preserves_rounded_text_and_fixed_reference(self):
        name, date, summary = read_report(ROOT, REPORT, MODEL)
        self.assertEqual((name, date), ('Ido Carmel', '2026-09-30'))
        self.assertEqual([s['heading'] for s in summary['sections']], HEADINGS)
        self.assertIn('rounding errors.\nmax error',summary['sections'][0]['rows'][0]['text'])
        self.assertIn('rho_living = 0.32\n', summary['sections'][1]['rows'][0]['text'])
        self.assertIn('GE<0.01%', summary['sections'][2]['rows'][0]['text'])
        self.assertEqual(summary['sections'][4]['table'][1], ['High', '142', '39.0208%', '31.8829%'])
        self.assertTrue(any('2019 landings' in p for p in summary['sections'][4]['reference']))
        self.assertEqual(summary['note'], NOTE)

    def test_registered_metadata_and_green_font_survive_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); region = root / 'regions/LME_001/LME_001.xlsx'
            model = region.parent / 'models/m/model.json'; model.parent.mkdir(parents=True); model.write_text('{}')
            b = fixture(); set_setting(b, 'region_name', 'Test region'); set_setting(b, 'region_type', 'LME')
            b['Selected model groups']['Groups'] = (['seq', 'group_name'], [[1, 'A'], [2, 'B'], [34, 'Seabirds'], [35, 'Pinnipeds'], [36, 'Other mammals'], [37, 'Marine turtles']])
            recalculate(b, region); write_book(region, b)
            project = root / 'Project.xlsx'
            write_book(project, {'Models & coverage': {'Models': (['unit_id','model_id','model_path','selected','selection_rationale'], [['LME_001','m','regions/LME_001/models/m/model.json',True,'test']])}, 'Papers': {'Papers': (['article_id','unit_id','selected'],[])}, 'Definitions & build': {}})
            report = region.parent / 'review.docx'
            with zipfile.ZipFile(REPORT) as source:
                document = etree.fromstring(source.read('word/document.xml'))
                relationships = etree.fromstring(source.read('word/_rels/document.xml.rels'))
                ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                for parent in document.iter():
                    for link in list(parent):
                        if link.tag != '{'+ns['w']+'}hyperlink': continue
                        if ''.join(t.text or '' for t in link.findall('.//w:t',ns)) == 'source reconstruction report':
                            rid=link.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                            next(r for r in relationships if r.get('Id')==rid).set('Target','evidence.txt#page%3D185')
                            (report.parent/'evidence.txt').write_text('test evidence')
                            continue
                        index = list(parent).index(link)
                        for child in list(link): parent.insert(index, child); index += 1
                        parent.remove(link)
                for text in document.findall('.//w:t', ns):
                    if text.text and MODEL in text.text: text.text = text.text.replace(MODEL, 'm')
                with zipfile.ZipFile(report,'w') as target:
                    target.writestr('word/document.xml', etree.tostring(document))
                    target.writestr('word/_rels/document.xml.rels', etree.tostring(relationships))
            protected = sha(region)
            original = read_book(project)
            registered = register_review(project, report, 'LME_001', 'm', [34,35,36,37])
            p = read_book(project); row = records(p, 'Models & coverage', 'Models')[0]
            self.assertEqual({k:row[k] for k in FIELDS}, registered)
            self.assertEqual({k:row[k] for k in original['Models & coverage']['Models'][0]}, dict(zip(*[original['Models & coverage']['Models'][0], original['Models & coverage']['Models'][1][0]])))
            review = approved_review(root, row, b)
            hrefs=[segment.get('href','') for segments in review['sections'][0]['rows'][0]['paragraphs'] for segment in segments]
            self.assertIn('regions/LME_001/evidence.txt#page%3D185',hrefs)
            self.assertEqual(review['excluded_group_ids'], ['Seabirds','Pinnipeds','Other mammals','Marine turtles'])
            self.assertEqual(sha(region), protected)
            workbook = openpyxl.load_workbook(project, read_only=True)
            self.assertEqual(workbook['Models & coverage']['B3'].font.color.rgb, 'FF187344'); workbook.close()
            context=root/'common_reference_data/atlas_source_context'; context.mkdir(parents=True)
            with gzip.open(context/'catalog.json.gz','wt') as f: json.dump({'curated_region_ids':[]},f)
            update(root,[region]); refreshed=records(read_book(project),'Models & coverage','Models')[0]
            self.assertEqual({k:refreshed[k] for k in FIELDS}, registered)
            workbook=openpyxl.load_workbook(project,read_only=True)
            self.assertTrue(workbook['Models & coverage']['B3'].font.color.rgb.endswith('187344'));workbook.close()
            self.assertEqual(sha(region), protected)
            model.write_text('{"changed":true}')
            with self.assertRaisesRegex(ValueError,'review source changed'): approved_review(root, refreshed, b)
            model.write_text('{}'); original_report=report.read_bytes(); report.write_bytes(original_report+b'changed')
            with self.assertRaisesRegex(ValueError,'review source changed'): approved_review(root, refreshed, b)

    def test_layout_uses_shared_filter_and_does_not_edit_frozen_templates(self):
        for name in ['index.html','trends.html']:
            path=ROOT/'tools/original_html_layout'/name; before=path.read_bytes()
            page=linked_layout(before.decode('utf-8'))
            self.assertIn('catch_indices',page);self.assertIn('check.disabled=',page)
            self.assertIn('Excluded from displayed PPR by researcher',page)
            self.assertIn('researcher-validated-name',page)
            self.assertEqual(path.read_bytes(),before)

    def test_review_presentation_removes_legacy_model_prose_and_prefixes(self):
        map_page=linked_layout((ROOT/'tools/original_html_layout/index.html').read_text(encoding='utf-8'))
        panel=map_page[map_page.index('const modelUnit=network.units[r.unit_id]'):map_page.index('function updateLegend()')]
        self.assertIn('const reviewModel=modelUnit?.models[idx]',panel)
        self.assertIn('PPRResearcherReview.append(panel,reviewModel)',panel)
        self.assertNotIn('network-status',panel)
        self.assertNotIn('Diagnosis / review flags:',panel)
        self.assertNotIn('Retained selection rationale:',panel)
        self.assertNotIn('const notes=',panel)
        self.assertNotIn('Validated by researcher · ',panel)
        self.assertNotIn('independent?null:modelUnit?.models[chosenModels[r.unit_id]]',panel)
        for name in ['index.html','trends.html']:
            page=linked_layout((ROOT/'tools/original_html_layout'/name).read_text(encoding='utf-8'))
            self.assertIn('.researcher-review-pending{color:#b42318',page)
            self.assertNotIn("m.researcher_review?'Validated by researcher · '",page)
        trend_page=linked_layout((ROOT/'tools/original_html_layout/trends.html').read_text(encoding='utf-8'))
        coverage=trend_page[trend_page.index('function renderCoverage()'):trend_page.index('function renderSensitivityReadout()')]
        self.assertIn('PPRResearcherReview.append(li,model)',coverage)
        self.assertNotIn('Diagnosis / review flags:',coverage)
        self.assertNotIn('if(model?.review_note)',coverage)
        self.assertNotIn('if(model?.workbook)',coverage)

    def test_layout_only_refresh_preserves_data_and_rejects_stale_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);project=root/'Project.xlsx';project.write_bytes(b'fingerprinted fixture')
            payload='{\n"value":1.23456789,"text":"kept  spaces"\n}'
            for name in ['index.html','trends.html']:
                template=(ROOT/'tools/original_html_layout'/name).read_text(encoding='utf-8')
                page=linked_layout(template).replace('__PPR_DATA__',payload)
                page=page.replace('</head>',f'<meta name="ppr-project-sha256" content="{sha(project)}"></head>',1)
                (root/name).write_text(page,encoding='utf-8')
            relayout(project,root)
            for name in ['index.html','trends.html']:
                self.assertEqual((root/name).read_text(encoding='utf-8').count(payload),1)
            saved=(root/'index.html').read_bytes();project.write_bytes(b'changed fixture')
            with self.assertRaisesRegex(ValueError,'does not match Project'):relayout(project,root)
            self.assertEqual((root/'index.html').read_bytes(),saved)

    def test_metadata_refresh_preserves_numerics_and_rejects_other_central_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);project=root/'Project.xlsx';prior=root/'previous.xlsx'
            book={'Models & coverage':{'Models':(['unit_id','model_id']+FIELDS,[['LME_001','m']+[None]*len(FIELDS)])},
                  'Definitions & build':{'Scientific':(['value'],[[1.23456789012345]])}}
            write_book(prior,book)
            changed=copy.deepcopy(book);changed['Models & coverage']['Models'][1][0][2]=STATUS
            changed['Models & coverage']['Models'][1][0][2+FIELDS.index('validation_report_path')]='review.docx'
            write_book(project,changed)
            registered_bytes=project.read_bytes()
            region=root/'regions/LME_001/LME_001.xlsx'
            write_book(region,{'Overview':{'Settings':(['field','value'],[['selected_model_id','m']])},
                              'Selected model groups':{'Groups':(['seq','group_name'],[[1,'Excluded']])}})
            unit={'models':[{'id':'m','values':[1.23456789012345,None,-.000001]}],'catch':[100.00000001]}
            payloads={'DB':{'network':{'units':{'LME_001':unit}}},'SERIES_DB':{'units':{'LME_001':unit}}}
            for name,variable in [('index.html','DB'),('trends.html','SERIES_DB')]:
                page=linked_layout((ROOT/'tools/original_html_layout'/name).read_text(encoding='utf-8'))
                page=page.replace('__PPR_DATA__',json.dumps(payloads[variable]))
                page=page.replace('</head>',f'<meta name="ppr-project-sha256" content="{sha(prior)}"></head>',1)
                (root/name).write_text(page,encoding='utf-8')
            review={'model_id':'m','excluded_group_ids':['Excluded'],'sections':[],'note':'Approved'}
            # The registration replay is isolated here; actual Word extraction,
            # source identities and bounded registration are covered above.
            def registration(path,*args):Path(path).write_bytes(registered_bytes)
            with patch('build_html.approved_review',return_value=review),patch('build_html.register_review',side_effect=registration):
                refresh_reviews(project,prior,['LME_001'],root)
            for name,variable in [('index.html','DB'),('trends.html','SERIES_DB')]:
                page=(root/name).read_text(encoding='utf-8');start=page.index('const '+variable+'=')+len('const '+variable+'=')
                refreshed,_=json.JSONDecoder().raw_decode(page,start)
                units=refreshed['network']['units'] if variable=='DB' else refreshed['units']
                model=units['LME_001']['models'][0]
                self.assertEqual(model.pop('researcher_review'),review)
                self.assertEqual(model.pop('display_ppr_excluded_group_ids'),['Excluded'])
                self.assertEqual(refreshed,payloads[variable])
                self.assertIn(f'content="{sha(project)}"',page)
            saved=(root/'index.html').read_bytes()
            changed['Definitions & build']['Scientific'][1][0][0]=2
            write_book(project,changed)
            with patch('build_html.approved_review',return_value=review),patch('build_html.register_review',side_effect=registration):
                with self.assertRaisesRegex(ValueError,'beyond the targeted'):
                    refresh_reviews(project,prior,['LME_001'],root)
            self.assertEqual((root/'index.html').read_bytes(),saved)

if __name__ == '__main__': unittest.main()
