"""A reviewed Word category absent from the selected model must not be claimed removed."""
import json, sys, tempfile, unittest, zipfile
from pathlib import Path
from xml.etree import ElementTree as E

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from researcher_review import register_review,sha
from workbooks import write_book

ROOT=Path(__file__).resolve().parents[2]
MODEL='34_1_Bay_of_Bengal_(1978)'
REPORT=ROOT/'regions/LME_034'/('Model_validation_'+MODEL+'.docx')
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

class AbsentExclusionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);folder=self.root/'regions/LME_034';folder.mkdir(parents=True)
        (folder/'model.json').write_text('{}')
        self.region=folder/'LME_034.xlsx'
        self.project=self.root/'Project.xlsx'
        write_book(self.project,{'Models & coverage':{'Models':(['unit_id','model_id','model_path'],[['LME_034',MODEL,'regions/LME_034/model.json']])}})
        self.report=folder/'review.docx'
        with zipfile.ZipFile(REPORT) as source:
            document=E.fromstring(source.read('word/document.xml'))
            relationships=source.read('word/_rels/document.xml.rels')
        # Fixture links are deliberately removed; original scientific and review text stays.
        for parent in document.iter():
            for child in list(parent):
                if child.tag==W+'hyperlink':
                    i=list(parent).index(child)
                    for n in list(child):parent.insert(i,n);i+=1
                    parent.remove(child)
        with zipfile.ZipFile(self.report,'w') as target:
            target.writestr('word/document.xml',E.tostring(document))
            target.writestr('word/_rels/document.xml.rels',relationships)
        self.put_groups([[1,'Oceanic sharks'],[2,'Coastal elasmobranch'],[5,'Jellyfish']])

    def put_groups(self,groups):
        write_book(self.region,{'Overview':{'Settings':(['field','value'],[['selected_model_id',MODEL],['calculation_input_sha256','fixture-input']])},
            'Selected model groups':{'Groups':(['seq','group_name'],groups)}})

    def test_actual_absent_seabirds_with_explicit_empty_exclusions_preserves_source_and_applies_none(self):
        report_sha,region_sha=sha(self.report),sha(self.region)
        result=register_review(self.project,self.report,'LME_034',MODEL,[])
        summary=json.loads(result['researcher_review_summary'])
        self.assertIn('seabirds (GE<0.01%',summary['sections'][2]['rows'][0]['text'])
        self.assertEqual(summary['excluded_group_ids'],[])
        self.assertIn('contains no matching group',summary['note'])
        self.assertIn('No model groups are excluded from displayed PPR',summary['note'])
        self.assertNotIn('seabirds are excluded from displayed PPR',summary['note'])
        self.assertEqual((sha(self.report),sha(self.region)),(report_sha,region_sha))

    def test_explicit_empty_override_does_not_claim_absence_when_source_group_exists(self):
        self.put_groups([[1,'Oceanic sharks'],[34,'Seabirds']])
        summary=json.loads(register_review(self.project,self.report,'LME_034',MODEL,[])['researcher_review_summary'])
        self.assertNotIn('no matching group',summary['note'])

    def test_unknown_requested_sequence_still_fails_before_modifying_project(self):
        before=sha(self.project)
        with self.assertRaisesRegex(ValueError,'do not resolve uniquely'):
            register_review(self.project,self.report,'LME_034',MODEL,[999])
        self.assertEqual(sha(self.project),before)

if __name__=='__main__':unittest.main()
