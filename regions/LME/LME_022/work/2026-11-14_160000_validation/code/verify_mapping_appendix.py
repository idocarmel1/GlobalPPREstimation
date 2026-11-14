from pathlib import Path
import hashlib,json,math,re,subprocess,zipfile
from openpyxl import load_workbook

root=Path.cwd()
model=root/'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991'
p=model/'model_validation/taxon_mapping.xlsx'
qa=model/'model_validation/work/2026-11-14_160000_validation/qa'
audit=json.loads((root/'regions/LME/LME_022/work/2026-11-14_160000_validation/outputs/mapping_audit.json').read_text(encoding='utf8'))
w=load_workbook(p,data_only=False)
ws=w['Taxon mapping']
actual=list(ws.iter_rows(min_row=8,max_row=391,values_only=True))
assert len(actual)==384 and [x[0] for x in actual]==[x['taxon'] for x in audit['rows']]
for actual_row,expected in zip(actual,audit['rows']):
    assert actual_row[1]==(expected['tl'] if expected['tl'] is not None else '?')
    assert actual_row[2]==expected['catch_tonnes']
    assert math.isclose(actual_row[3],expected['simple_chain_ppr_tC'],rel_tol=1e-14,abs_tol=1e-10)
    assert actual_row[4:6]==('Unresolved','Unresolved')
assert math.isclose(math.fsum(r[2] for r in actual),audit['totals']['catch_tonnes'],rel_tol=1e-14)
assert math.isclose(math.fsum(r[3] for r in actual),audit['totals']['known_simple_chain_ppr_tC'],rel_tol=1e-14)
assert sum(r[1]=='?' for r in actual)==72 and all(r[2]==0 and r[3]==0 for r in actual if r[1]=='?')
assert not any(c.data_type=='e' for s in w for row in s for c in row)
assert ws.freeze_panes=='B8',ws.freeze_panes
assert len(ws.tables)==1 and next(iter(ws.tables.values())).ref=='A7:G391'
assert next(iter(ws.tables.values())).autoFilter.ref=='A7:G391'
links=[]
for s in w:
 for row in s:
  for c in row:
   if c.data_type=='f' and str(c.value).startswith('=HYPERLINK'):
    target=re.search(r'HYPERLINK\("([^"]+)',c.value).group(1)
    assert c.font.underline=='single' and c.font.color.rgb[-6:]=='0563C1',(s.title,c.coordinate,c.font)
    info={'sheet':s.title,'cell':c.coordinate,'target':target,'blue_underlined':True}
    if target.startswith('#'):
     info['kind']='internal';info['target_exists']=target.split("'")[1] in w.sheetnames
    else:
     assert not re.match(r'^(?:[A-Za-z]:|/|\\|file:|https?://localhost)',target)
     resolved=(p.parent/target).resolve()
     assert resolved.is_relative_to(root.resolve()) and resolved.exists(),target
     relative=resolved.relative_to(root).as_posix()
     tracked=subprocess.run(['git','ls-files','--error-unmatch','--',relative],capture_output=True,text=True).returncode==0
     assert tracked,relative
     info.update({'kind':'relative repository link','target_exists':True,'tracked':tracked})
    links.append(info)
current=hashlib.sha256((root/'regions/LME/LME_022/LME_022.xlsx').read_bytes()).hexdigest()
assert current==audit['regional_workbook_sha256']
assert hashlib.sha256((root/audit['comparison_mapping_availability']['appendix_path']).read_bytes()).hexdigest()==audit['comparison_mapping_availability']['appendix_sha256']
source_model=json.loads((model/'model.json').read_text(encoding='utf8'))
assert len(source_model['group'])==69
assert all(g.get('taxon_descr') is None for g in source_model['group'])
result={'verified':True,'rows':384,'numeric_sort_exact':True,'missing_tl_zero_catch_preserved':72,
        'catch_tonnes':math.fsum(r[2] for r in actual),'simple_chain_ppr_tC':math.fsum(r[3] for r in actual),
        'freeze_panes':ws.freeze_panes,'filter':'A7:G391','links':links,
        'input_workbook_unchanged':True,'scotland_appendix_unchanged':True,
        'rendered_and_visually_inspected':['mapping_top.png','mapping_bottom.png','sources.png'],
        'template_gap':'tools/templates/taxon_mapping.xlsx absent; current instructions.md seven-column layout used',
        'output_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(qa/'mapping_appendix_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
