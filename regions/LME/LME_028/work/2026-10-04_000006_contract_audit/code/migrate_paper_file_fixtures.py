"""Move existing paper-files fixtures to the agreed canonical layout."""
from pathlib import Path
import re
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
path=ROOT/'tools/workflow_checks/maps/test_paper_files.py'
text=path.read_text(encoding='utf-8')
prefix,body=text.split('    def test_declared_article_folder_is_discovered',1)
body,count=re.subn(r"folder=root/'regions/LME/(LME_\d+)/papers/([^']+)';folder.mkdir\(parents=True\)",lambda m:"folder=paper_sources(root,'"+m[1]+"','"+m[2]+"')",body)
body=re.sub(r"(regions/LME/LME_\d+/papers/[^/'\"]+)/([^/'\"]+\.[a-z]+)",r'\1/sources/\2',body)
body=body.replace("reference=root/'common_reference_data';reference.mkdir()","reference=root/'common_reference_data';(reference/'provenance').mkdir(parents=True)")
body=body.replace("(reference/'paper_file_roles.json')","(reference/'provenance/paper_file_roles.json')")
path.write_text(prefix+'    def test_declared_article_folder_is_discovered'+body,encoding='utf-8',newline='\n')
print('Canonical paper fixtures migrated:',count)
