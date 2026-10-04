"""Significant-digit percentages and narrow Word table edits."""
import sys,tempfile,unittest,zipfile
from pathlib import Path
from xml.etree import ElementTree as E
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from tools.project_core.validation.validation_percentage_format import format_percent,format_report

W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

class PercentageFormatTests(unittest.TestCase):
    def test_two_significant_digits_and_percent_suffix(self):
        for value,expected in [('44.56','45%'),('0.0043312','0.0043%'),
            ('0.2036%','0.20%'),('99.9999','100%'),('0.0000%','0%'),
            ('48.5275%','49%'),('3.3265','3.3%'),('1.25','1.3%')]:
            with self.subTest(value=value):
                self.assertEqual(format_percent(value),expected)
                self.assertEqual(format_percent(expected),expected)

    def test_rounding_carries_and_small_range_endpoints(self):
        self.assertEqual(format_percent('9.999%'),'10%')
        self.assertEqual(format_percent('0.09999%'),'0.10%')

    def test_only_percentage_cells_in_summary_and_rule_tables_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=Path(tmp)/'review.docx'
            doc=E.Element(W+'document');body=E.SubElement(doc,W+'body')
            def table(rows):
                t=E.SubElement(body,W+'tbl')
                for row in rows:
                    tr=E.SubElement(t,W+'tr')
                    for value in row:
                        cell=E.SubElement(tr,W+'tc');p=E.SubElement(cell,W+'p')
                        r=E.SubElement(p,W+'r');E.SubElement(r,W+'t').text=value
            table([['Review and reproducibility','Signed 44.56%']])
            table([['Overall confidence','Taxa','Catch (%)','PPR percentage'],
                   ['High','123','44.56%','0.0043312']])
            table([['Plain-language rule','Confidence','PPR percentage'],
                   ['Rule text 44.56%','Medium','0.2036%']])
            with zipfile.ZipFile(report,'w') as z:
                z.writestr('word/document.xml',E.tostring(doc))
                z.writestr('word/styles.xml',b'unchanged styles')
            changes=format_report(report)
            with zipfile.ZipFile(report) as z:
                self.assertEqual(z.read('word/styles.xml'),b'unchanged styles')
                result=E.fromstring(z.read('word/document.xml'))
            texts=[t.text or '' for t in result.iter(W+'t')]
            self.assertEqual(texts,['Review and reproducibility','Signed 45%',
                'Overall confidence','Taxa','Catch (%)','PPR percentage',
                'High','123','45%','0.0043%',
                'Plain-language rule','Confidence','PPR percentage',
                'Rule text 45%','Medium','0.20%'])
            self.assertEqual(len(changes),5)
            before=report.read_bytes()
            self.assertEqual(format_report(report),[])
            self.assertEqual(report.read_bytes(),before)

if __name__=='__main__':unittest.main()
