"""List exact central table changes against the pre-publication native workbook."""
from pathlib import Path
import json,sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book
WORK=Path(__file__).resolve().parents[1]
before=read_book(WORK/'qa/Project.before.xlsx');after=read_book(ROOT/'Project.xlsx')
generated={'Regions & status','Regional PPR','Regional NPP','Method comparisons','Diagnostics & sensitivity','Definitions & build'}
changes=[]
for sheet,tables in before.items():
    if sheet in generated:continue
    for table,(header,rows) in tables.items():
        new_header,new_rows=after[sheet][table]
        if header!=new_header:changes.append({'sheet':sheet,'table':table,'headers_before':header,'headers_after':new_header});continue
        if len(rows)!=len(new_rows):changes.append({'sheet':sheet,'table':table,'row_counts':[len(rows),len(new_rows)]});continue
        for old,new in zip(rows,new_rows):
            values={name:{'before':a,'after':b} for name,a,b in zip(header,old,new) if a!=b and 'rank' not in str(name).lower()}
            if values:changes.append({'sheet':sheet,'table':table,'identity':{name:old[header.index(name)] for name in ('unit_id','model_id','paper_id') if name in header},'values':values})
(WORK/'qa/central_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(changes,ensure_ascii=False,indent=2))
import verify_migration as audit
units={unit for unit,_ in audit.read(WORK/'qa/before.json.gz')['identities']}
old_independent=audit.independent_project(before,units)
new_independent=audit.independent_project(after,units)
differences=[]
for sheet,tables in old_independent.items():
    for table,(header,rows) in tables.items():
        new_header,new_rows=new_independent[sheet][table]
        if (header,rows)==(new_header,new_rows):continue
        examples=[]
        for old,new in zip(rows,new_rows):
            if old==new:continue
            examples.append({'identity':{name:old[header.index(name)] for name in ('unit_id','model_id','method') if name in header},
                             'fields':{name:{'before':a,'after':b} for name,a,b in zip(header,old,new) if a!=b}})
            if len(examples)==3:break
        differences.append({'sheet':sheet,'table':table,'headers_changed':header!=new_header,'row_counts':[len(rows),len(new_rows)],'examples':examples})
(WORK/'qa/central_generated_changes.json').write_text(json.dumps(differences,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(differences,ensure_ascii=False,indent=2))
from tools.project_core.workbooks.workbooks import digest_tables
import copy
unmasked=copy.deepcopy(old_independent)
unmasked['Models & coverage']=copy.deepcopy(before['Models & coverage'])
hashes={'captured':audit.read(WORK/'qa/before.json.gz')['independent_project'],
        'before_with_current_rank_exclusion':digest_tables(old_independent),
        'after_with_current_rank_exclusion':digest_tables(new_independent),
        'before_without_rank_exclusion':digest_tables(unmasked)}
(WORK/'qa/central_digest_diagnosis.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
print(json.dumps(hashes,indent=2))
