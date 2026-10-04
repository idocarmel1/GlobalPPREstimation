"""Signed model identifiers may be followed by explanatory punctuation."""
import sys,tempfile,unittest,zipfile
from pathlib import Path
from xml.etree import ElementTree as E
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from tools.project_core.validation.researcher_review import read_report

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

    def test_confidence_reference_stops_at_table_and_omits_appendix_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            report=self.report(root,MODEL)
            with zipfile.ZipFile(report) as archive:
                document=E.fromstring(archive.read('word/document.xml'))
            body=document.find(W+'body')
            def paragraph(value):
                p=E.Element(W+'p');r=E.SubElement(p,W+'r')
                E.SubElement(r,W+'t').text=value
                return p
            body.insert(1,paragraph('Taxon mapping and coverage'))
            reference=paragraph('Reference: 2019 landings.')
            run=reference.find(W+'r');E.SubElement(run,W+'br')
            E.SubElement(run,W+'t').text='Independent simple-chain PPR.'
            body.insert(2,reference)
            body.insert(3,paragraph('Method: simple trophic chain.'))
            appendix=E.Element(W+'p')
            link=E.SubElement(appendix,W+'hyperlink',{
                '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id':'appendix'})
            r=E.SubElement(link,W+'r')
            E.SubElement(r,W+'t').text='Full taxon mapping appendix and descriptive Sources sheet'
            body.insert(4,appendix)
            for value in ['Group assignment rules','Allocation weight rules',
                          'Very low decisions','Geographic evidence screenshots']:
                body.append(paragraph(value))
            with zipfile.ZipFile(report,'w') as archive:
                archive.writestr('word/document.xml',E.tostring(document))
                archive.writestr('word/_rels/document.xml.rels',
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    '<Relationship Id="appendix" Target="review_taxon_mapping_appendix.xlsx#Sources!A1"/>'
                    '</Relationships>')
            summary=read_report(root,report,MODEL)[2]
            confidence=summary['sections'][-1]
            self.assertEqual(confidence['reference'],[
                'Reference: 2019 landings.\nIndependent simple-chain PPR.',
                'Method: simple trophic chain.'])
            self.assertEqual(confidence['table'],[
                ['Overall confidence','PPR percentage'],
                *[[level,'0'] for level in ['High','Medium','Low','Very low','Unresolved']]])

if __name__=='__main__':unittest.main()
