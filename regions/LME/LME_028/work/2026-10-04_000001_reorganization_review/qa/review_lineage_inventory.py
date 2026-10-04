import os, stat, sys, json, hashlib, re, zipfile, xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path.cwd()
OUT = ROOT / 'regions/LME_028/work/2026-10-04_000001_reorganization_review/qa'
PRUNE = {'.git','node_modules','__pycache__','.venv','venv','site-packages','.pytest_cache','.mypy_cache','.agents','.codex','vendor','vendors','vendored','dependencies','deps','_deps','python_deps','.python_deps','lib','Lib','external'}

def walk(root):
    with os.scandir(root) as entries:
        for e in entries:
            if e.name in PRUNE or e.is_symlink():continue
            info=e.stat(follow_symlinks=False)
            if info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:continue
            if e.is_dir(follow_symlinks=False):yield from walk(Path(e.path))
            elif e.is_file(follow_symlinks=False):yield Path(e.path)

def table(rows):
    if rows and rows[0][0]=='@table': rows=rows[1:]
    if not rows:return []
    keys=rows[0]
    return [{str(k):v for k,v in zip(keys,row) if k is not None} for row in rows[1:] if any(v is not None for v in row)]

def xlsx_tables(path,names):
    ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    def index(coord):
        letters=re.match(r'[A-Z]+',coord)[0]
        n=0
        for a in letters:n=n*26+ord(a)-64
        return n-1
    with zipfile.ZipFile(path) as z:
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        rel=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets={r.attrib['Id']:r.attrib['Target'].lstrip('/') for r in rel}
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            shared=[''.join(t.text or '' for t in si.findall('.//x:t',ns)) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        answer={}
        for sheet in wb.findall('x:sheets/x:sheet',ns):
            name=sheet.attrib['name']
            if name not in names:continue
            target=targets[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            if not target.startswith('xl/'):target='xl/'+target
            rows=[]
            for row in ET.fromstring(z.read(target)).findall('.//x:sheetData/x:row',ns):
                values=[]
                for c in row:
                    idx=index(c.attrib['r'])
                    if len(values)<=idx:values.extend([None]*(idx+1-len(values)))
                    val=c.find('x:v',ns)
                    if c.attrib.get('t')=='inlineStr':v=''.join(t.text or '' for t in c.findall('.//x:t',ns))
                    elif val is None:v=None
                    elif c.attrib.get('t')=='s':v=shared[int(val.text)]
                    elif c.attrib.get('t')=='b':v=val.text=='1'
                    elif c.attrib.get('t') in ['str','e']:v=val.text
                    else:
                        try:v=float(val.text);v=int(v) if v.is_integer() else v
                        except:v=val.text
                    values[idx]=v
                rows.append(values)
            answer[name]=table(rows)
        return answer

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def inspect_model(p):
    result={'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p),'size':p.stat().st_size}
    try:
        obj=json.loads(p.read_text(encoding='utf-8-sig'))
        result['root_keys']=list(obj) if isinstance(obj,dict) else ['list']
    except Exception as e:result['error']=str(e)
    return result

central=xlsx_tables(ROOT/'Project.xlsx',['Papers','Models & coverage','Regions & status'])
print('central read', {k:len(v) for k,v in central.items()},flush=True)
files=[]
for r in [ROOT/'regions',ROOT/'original_research_archive']:
    files.extend(walk(r))
    print('scanned', r.name, len(files),flush=True)
model_paths=[p for p in files if p.name=='model.json' or (p.suffix.lower()=='.json' and p.parent.parent.name=='models')]
models=[inspect_model(p) for p in model_paths]
print('inspected models',len(models),flush=True)
validations=[p.relative_to(ROOT).as_posix() for p in files if p.suffix.lower() in ['.docx','.xlsx'] and ('validation' in p.name.lower() or 'appendix' in p.name.lower() or 'mapping' in p.name.lower())]
overview={}
for uid in sorted({m.get('unit_id') for m in central['Models & coverage']} | {'LME_028'}):
    if not uid:continue
    p=ROOT/'regions'/uid/(uid+'.xlsx')
    if p.exists():
        overview[uid]=xlsx_tables(p,['Overview'])['Overview']
result={'central':central,'models':models,'validation_paths':validations,'overviews':overview,'files':[p.relative_to(ROOT).as_posix() for p in files]}
(OUT/'review_lineage_inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print(json.dumps({'central_counts':{k:len(v) for k,v in central.items()},'model_files':len(models),'validation_files':len(validations),'overview_count':len(overview),'files':len(files)},indent=2))
print('MODELS CENTRAL HEADERS',list(central['Models & coverage'][0]))
print('MODELS CENTRAL IDENTITY',json.dumps([{k:v for k,v in row.items() if k in ['unit_id','model_id','article_id','model_path','source_model_id','model_year','model_years','selected','source','provenance','extraction_path']} for row in central['Models & coverage']],ensure_ascii=False,indent=2))
print('CANONICAL model.json paths',json.dumps([m['path'] for m in models if m['path'].startswith('regions/') and '/models/' in m['path']],ensure_ascii=False,indent=2))
