from pathlib import Path,PureWindowsPath
from urllib.parse import unquote
import zipfile,json,shutil,tempfile,hashlib
from lxml import etree as E
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
R=Path(__file__).resolve().parent.parent;region=R.parent.parent
dest=Path(tempfile.mkdtemp(prefix='lme032-portable-'))/'repository'
out=[]
for name in ['Model_validation_32_1_Arabian_Sea_off_Karnataka_(2000).docx','LME032_taxon_mapping_appendix.xlsx']:
 original=region/name;clone=dest/original.relative_to(ROOT);clone.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,clone)
 targets=[]
 with zipfile.ZipFile(original) as z:
  for part in z.namelist():
   if part.endswith('.rels'):
    targets.extend(x.get('Target') for x in E.fromstring(z.read(part)) if x.get('Type','').endswith('/hyperlink'))
   if part.startswith(('word/','xl/')) and part.endswith('.xml'):
    raw=z.read(part).decode('utf-8')
    assert 'HYPERLINK is not implemented' not in raw
   if part in ['docProps/custom.xml','docProps/app.xml']:
    xml=E.fromstring(z.read(part))
    assert not any(E.QName(x).localname=='HyperlinkBase' and x.text for x in xml.iter())
 local=[]
 for target in targets:
  if target.startswith(('https://','http://')):continue
  clean=unquote(target.split('#',1)[0]);assert not PureWindowsPath(clean).drive and not Path(clean).is_absolute() and '://' not in clean
  source=(original.parent/clean).resolve();assert source.is_relative_to(ROOT) and source.is_file()
  new=dest/source.relative_to(ROOT);new.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,new)
  resolved=(clone.parent/clean).resolve();assert resolved==new and resolved.is_file()
  digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==hashlib.sha256(resolved.read_bytes()).hexdigest()
  local.append({'target':target,'repository_path':source.relative_to(ROOT).as_posix(),'sha256':digest,'relocated_resolution_passed':True})
 out.append({'deliverable':name,'local_links':local,'public_links':len(targets)-len(local),'all_passed':True})
(R/'qa/portable_links.json').write_text(json.dumps({'all_passed':True,'method':'Copied current artifacts and all local destinations into an independently named repository root; reopened packages, resolved original stored links and checked identical destination hashes.','checks':out},ensure_ascii=False,indent=2),encoding='utf-8')
(R/'work/relocated_repository.txt').write_text(str(dest),encoding='utf-8')
print('Relocated current report/appendix: all relative links passed')
