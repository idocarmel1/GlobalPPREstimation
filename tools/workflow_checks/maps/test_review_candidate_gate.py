"""Isolated tests for proposed exact-pair/candidate bounded review gate.
Install in tools/workflow_checks/validation/test_review_candidate_gate.py.
"""
import copy
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
from tools.project_core.registry import review_candidates as candidate_row
from tools.project_core.maps import build_html as build
from tools.workflow_checks.validation.test_researcher_disqualification import report_fixture, REASON
from tools.project_core.validation.researcher_review import _register_review, table_rows, sha, approved_review
from tools.project_core.workbooks.workbooks import write_book, read_book, records
from tools.project_core.registry.publication import publication_transaction
PAIRS=[('LME_001','m'),('LME_001','candidate')]

class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.project=self.root/'Project.xlsx';self.prior=self.root/'before.xlsx'
        self.pages=self.root/'interactive_map';self.pages.mkdir()
        self.sources={};self.reports={}
        for model in ['m','candidate']:
            source=self.root/f'regions/LME/LME_001/papers/P/models/{model}/model.json'
            source.parent.mkdir(parents=True);source.write_text('{}')
            report_dir=source.parent/'model_validation';report_dir.mkdir()
            report=report_fixture(report_dir,identity_label='Candidate model' if model=='candidate' else 'Selected model')
            with zipfile.ZipFile(report) as z:parts={n:z.read(n) for n in z.namelist()}
            parts['word/document.xml']=parts['word/document.xml'].replace(b'm; exact reviewed model',(model+'; exact reviewed model').encode())
            with zipfile.ZipFile(report,'w') as z:
                for n,value in parts.items():z.writestr(n,value)
            self.sources[model]=source;self.reports[model]=report
        self.regional=self.root/'regions/LME/LME_001/LME_001.xlsx'
        write_book(self.regional,{'Overview':{'Settings':(['field','value'],[['selected_model_id','m'],['results_model_id','m'],['selection_rationale','Keep this exact manual rationale'],['calculation_input_sha256','actual-input']])},'Selected model groups':{'Groups':(['seq','group_name'],[[1,'Fish']])}})
        self.row={'unit_id':'LME_001','model_id':'candidate','model_path':self.sources['candidate'].relative_to(self.root).as_posix(),'selected':False,'paper_ids':'P','model_year':1995,'model_years':'1995','publication_year':2022,'doi':'10.example/exact','variant':'Explicit candidate'}
        headers=list(self.row)
        original={**self.row,'model_id':'m','model_path':self.sources['m'].relative_to(self.root).as_posix(),'selected':True}
        write_book(self.project,{'Models & coverage':{'Models':(headers,[[original[h] for h in headers]])},'Papers':{'Papers':(['article_id','unit_id','publication_year','doi'],[['P','LME_001',2022,'10.example/exact']])},'Science':{'Values':(['value'],[[1.2345],[None],[0]])}})
        shutil.copyfile(self.project,self.prior)
        self.candidates=[{'row':self.row,'canonical_sha256':sha(self.sources['candidate'])}]
        model={'id':'m','values':[1.2345,None,0],'verified':True,'scopes':{'all':{'GE':[1,None]}}}
        self.payloads={'DB':{'network':{'units':{'LME_001':{'models':[copy.deepcopy(model)],'default_model':0}}},'untouched':[None,0]},'SERIES_DB':{'units':{'LME_001':{'models':[copy.deepcopy(model)],'default_model':'m'}},'untouched':[None,0]}}
        for page,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
            (self.pages/page).write_text('<head><meta name="ppr-project-sha256" content="'+sha(self.prior)+'"></head><script>const '+var+'='+json.dumps(self.payloads[var])+';</script>',encoding='utf-8')
        self.protected={p:sha(p) for p in [self.regional,*self.sources.values(),*self.reports.values()]}
        self.layout=patch.object(build,'linked_layout',side_effect=lambda value:value);self.layout.start();self.addCleanup(self.layout.stop)

    def register(self,candidate=True):
        if candidate:candidate_row.add_review_candidate(self.project,self.root,self.row,self.candidates[0]['canonical_sha256'])
        for unit,model in PAIRS if candidate else PAIRS[:1]:_register_review(self.project,self.reports[model],unit,model,[])

    def refresh(self,**kwargs):
        return build._refresh_reviews(self.project,self.prior,[],self.pages,model_pairs=PAIRS,candidate_rows=self.candidates,**kwargs)

    def payload(self,page,var):
        text=(self.pages/page).read_text(encoding='utf-8');start=text.index('const '+var+'=')+len('const '+var+'=')
        return json.JSONDecoder().raw_decode(text,start)[0]

    def test_two_exact_models_and_candidate_preserve_default_and_science(self):
        self.register();self.refresh()
        metadata={r['model_id']:r for r in records(read_book(self.project),'Models & coverage','Models')}
        for page,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
            payload=self.payload(page,var);original=copy.deepcopy(self.payloads[var])
            unit=(payload['network']['units'] if var=='DB' else payload['units'])['LME_001']
            self.assertEqual(unit['default_model'],0 if var=='DB' else 'm')
            self.assertEqual(len(unit['models']),2)
            for model in unit['models']:
                self.assertEqual(model['researcher_review']['reason'],REASON)
                self.assertEqual(model['display_ppr_excluded_group_ids'],[])
                self.assertEqual(model['researcher_review']['sections'],[])
                self.assertNotIn('recorded_review_pending',model)
                expected=approved_review(self.root,metadata[model['id']],read_book(self.regional))
                self.assertEqual(model['researcher_review'],expected)
            candidate=unit['models'].pop();self.assertFalse(candidate['verified']);self.assertEqual(candidate['scopes'],{})
            self.assertEqual(candidate['source'],self.row['model_path']);self.assertNotIn('values',candidate)
            self.assertEqual(candidate['researcher_review']['review_scope'],'model_source')
            for field in ['researcher_review','display_ppr_excluded_group_ids']:unit['models'][0].pop(field)
            self.assertEqual(payload,original)
        self.assertFalse(metadata['candidate']['reviewed_calculation_input_sha256'])
        self.assertEqual({p:sha(p) for p in self.protected},self.protected)
        with zipfile.ZipFile(self.prior) as a,zipfile.ZipFile(self.project) as b:
            from tools.project_core.validation.researcher_review import sheet_xml
            path,_=sheet_xml(a,'Science');self.assertEqual(a.read(path),b.read(path))

    def test_legacy_selected_api(self):
        self.register(False)
        build._refresh_reviews(self.project,self.prior,['LME_001'],self.pages)
        self.assertEqual(self.payload('index.html','DB')['network']['units']['LME_001']['models'][0]['researcher_review']['verdict'],'MODEL DISQUALIFIED')

    def test_unrelated_xml_change_rejected(self):
        self.register()
        with zipfile.ZipFile(self.project) as z:parts=[(i,z.read(i.filename)) for i in z.infolist()]
        with zipfile.ZipFile(self.project,'w') as z:
            for info,data in parts:z.writestr(info,data+b' ' if info.filename=='docProps/core.xml' else data)
        with self.assertRaisesRegex(ValueError,'beyond the targeted'):self.refresh(publish=False)

    def test_wrong_page_baseline_rejected(self):
        self.register();page=self.pages/'index.html';page.write_text(page.read_text().replace(sha(self.prior),'0'*64))
        with self.assertRaisesRegex(ValueError,'pre-registration'):self.refresh(publish=False)

    def test_scope_rejections(self):
        self.register()
        with self.assertRaisesRegex(ValueError,'unique'):build._refresh_reviews(self.project,self.prior,[],self.pages,model_pairs=PAIRS+PAIRS[:1])
        with self.assertRaisesRegex(ValueError,'not both'):build._refresh_reviews(self.project,self.prior,['LME_001'],self.pages,model_pairs=PAIRS)
        with self.assertRaisesRegex(ValueError,'exact reviewed pairs'):build._refresh_reviews(self.project,self.prior,[],self.pages,model_pairs=PAIRS[:1],candidate_rows=self.candidates)

    def test_new_candidate_requires_source_only_negative(self):
        self.register()
        original=build.approved_review
        def altered(root,row,book):
            review=original(root,row,book)
            if row['model_id']=='candidate':review['status']='Validated by researcher'
            return review
        with patch.object(build,'approved_review',side_effect=altered):
            with self.assertRaisesRegex(ValueError,'source-only disqualification'):self.refresh(publish=False)

    def test_second_page_failure_rolls_back_project_and_pages(self):
        paths=[self.project,self.pages/'index.html',self.pages/'trends.html'];before={p:p.read_bytes() for p in paths}
        original=build.atomic_text
        def fail_second(path,text):
            if path.name=='trends.html':raise RuntimeError('induced second-page failure')
            return original(path,text)
        with self.assertRaisesRegex(RuntimeError,'induced'):
            with publication_transaction(self.root) as publication:
                self.register();publication.checkpoint([self.project])
                with patch.object(build,'atomic_text',side_effect=fail_second):self.refresh()
        self.assertEqual({p:p.read_bytes() for p in paths},before)
        self.assertEqual({p:sha(p) for p in self.protected},self.protected)

if __name__=='__main__':unittest.main()
