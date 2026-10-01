"""Signed model identifiers may be followed by explanatory punctuation."""
import sys,tempfile,unittest,zipfile
from pathlib import Path
from xml.etree import ElementTree as E
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from researcher_review import read_report

MODEL='47_2_East_China_Sea_(2018)'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

class ModelBoundaryTests(unittest.TestCase):
    def report(self,root,selected):
        document=E.Element(W+'document');body=E.SubElement(document,W+'body')
        table=E.SubElement(body,W+'tbl')
        def row(parent,values):
            tr=E.SubElement(parent,W+'tr')
            for value in values:
                tc=E.SubElement(tr,W+'tc');p=E.SubElement(tc,W+'p');r=E.SubElement(p,W+'r')
                E.SubElement(r,W+'t').text=value
        for key,value in [('Selected model',selected),('Model extraction','Reviewed extraction'),
            ('GE diagnostics','GE WARN'),('TE diagnostics','TE WARN'),
            ('SPPR calculation','No groups were removed from the calculation.'),
            ('Geographic fit','Reviewed area'),
            ('Review and reproducibility','Researcher name: Reviewer | review date: 01/10/2026\nMODEL VALIDATED')]:row(table,[key,value])
        confidence=E.SubElement(body,W+'tbl')
        row(confidence,['Overall confidence','PPR percentage'])
        for level in ['High','Medium','Low','Very low','Unresolved']:row(confidence,[level,'0'])
        report=root/'review.docx'
        with zipfile.ZipFile(report,'w') as z:
            z.writestr('word/document.xml',E.tostring(document))
            z.writestr('word/_rels/document.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
        return report

    def test_semicolon_after_exact_model_id_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);report=self.report(root,MODEL+'; static M2018, autumn survey.')
            name,date,summary=read_report(root,report,MODEL)
            self.assertEqual((name,date),('Reviewer','2026-10-01'))
            self.assertEqual(summary['model_id'],MODEL)

    def test_different_model_or_suffix_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for selected in [MODEL+'suffix; description','47_1_East_China_Sea_(1997); description']:
                with self.subTest(selected=selected):
                    with self.assertRaisesRegex(ValueError,'different model'):
                        read_report(root,self.report(root,selected),MODEL)

if __name__=='__main__':unittest.main()
