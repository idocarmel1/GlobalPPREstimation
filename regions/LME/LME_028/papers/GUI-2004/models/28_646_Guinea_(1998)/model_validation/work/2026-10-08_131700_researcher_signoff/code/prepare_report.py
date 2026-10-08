from pathlib import Path
import sys, json, shutil, zipfile
from lxml import etree
root=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(root))
from tools.project_core.validation.validation_percentage_format import format_report,verify_report
from tools.project_core.validation.researcher_review import read_report
run=Path(__file__).resolve().parent.parent
report=run.parent.parent/'validation.docx'
baseline=run/'inputs/validation_before_percentage_format.docx'
if not baseline.exists():
    shutil.copyfile(report,baseline)
changes=format_report(report)
verify_report(report)
after=read_report(root,report,'28_646_Guinea_(1998)')
with zipfile.ZipFile(baseline) as a,zipfile.ZipFile(report) as b:
    assert a.namelist()==b.namelist()
    parts=[n for n in a.namelist() if a.read(n)!=b.read(n)]
    assert parts==['word/document.xml'],parts
    old=etree.fromstring(a.read('word/document.xml'));new=etree.fromstring(b.read('word/document.xml'))
    old_text=old.xpath('//w:t',namespaces={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
    new_text=new.xpath('//w:t',namespaces={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
    assert len(old_text)==len(new_text)
    token_changes=[]
    for x,y in zip(old_text,new_text):
        if x.text!=y.text:
            token_changes.append([x.text,y.text]);y.text=x.text
    assert token_changes==[['0.5','0.50%'],['%, EE=',', EE='],['0.3','0.30%'],['%, EE=',', EE='],['0.4','0.40%'],['%, EE=',', EE=']],token_changes
    assert etree.tostring(old)==etree.tostring(new),'Unexpected OOXML changes'
    changes=token_changes
(run/'qa/percentage_format.json').write_text(json.dumps({'changes':changes,'changed_package_parts':parts,'source_preserved_except_three_percentage_tokens':True},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'changes':changes,'changed_parts':parts,'verified':True},ensure_ascii=False))
