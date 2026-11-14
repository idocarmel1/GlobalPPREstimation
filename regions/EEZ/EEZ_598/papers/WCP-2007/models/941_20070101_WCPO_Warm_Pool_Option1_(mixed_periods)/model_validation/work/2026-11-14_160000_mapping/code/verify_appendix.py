import json, math, re, hashlib
from pathlib import Path
import openpyxl
ROOT=Path.cwd();W=Path(__file__).resolve().parents[1];V=W.parents[1]
D=json.loads((W/'inputs/appendix_data.json').read_text(encoding='utf-8'));p=V/'taxon_mapping.xlsx'
w=openpyxl.load_workbook(p,data_only=False);cached=openpyxl.load_workbook(p,data_only=True)
assert w.sheetnames==['Taxon mapping','Sources'];s=w['Taxon mapping'];src=w['Sources']
assert s.max_row==109 and s.max_column==7
actual=list(s.iter_rows(min_row=8,max_row=109,values_only=True));expected=D['rows']
for a,e in zip(actual,expected):
    assert a[:4]==tuple(e[:4]) and a[5]==e[5],(a,e)
    assert a[4]==('Unresolved' if e[5]=='Unresolved' else e[4])
    rr=e[6].split(' Sources:');reason=rr[0]+' Sources:'+rr[-1] if len(rr)>2 else e[6]
    assert a[6]==reason
assert len({r[0] for r in actual})==102
assert actual==sorted(actual,key=lambda r:(not isinstance(r[3],(int,float)),-r[3] if isinstance(r[3],(int,float)) else 0,r[0]))
assert sum(r[1]=='?' for r in actual)==47
assert all(r[2]==0 and r[3]==0 for r in actual if r[1]=='?')
assert all(isinstance(r[2],(int,float)) and isinstance(r[3],(int,float)) for r in actual)
assert math.isclose(math.fsum(r[2] for r in actual),D['summary']['total_catch_tonnes'],rel_tol=1e-15)
assert math.isclose(math.fsum(r[3] for r in actual),D['summary']['simple_chain_ppr_tC'],rel_tol=1e-15)
assert len(s.tables)==1 and len(src.tables)==1
assert s.tables['TaxonMapping'].autoFilter.ref=='A7:G109'
assert s.freeze_panes=='B8',(s.freeze_panes,src.freeze_panes)
assert src.freeze_panes=='A5'
links=[]
for sheet in w:
    for row in sheet:
        for c in row:
            if c.data_type=='f':
                assert c.value.startswith('=HYPERLINK('),c.value
                target=re.match(r'=HYPERLINK\("([^"]+)"',c.value).group(1)
                if not target.startswith(('http','#')):assert (V/target.split('#')[0]).resolve().exists(),target
                assert not re.match(r'^(?:[A-Za-z]:|file:|\\\\)',target),target
                assert c.font.color.type=='rgb' and c.font.color.rgb[-6:]=='0563C1' and c.font.u=='single',(sheet.title,c.coordinate,c.font)
                links.append({'sheet':sheet.title,'cell':c.coordinate,'target':target})
            assert c.data_type!='e',(sheet.title,c.coordinate,c.value)
for sheet in cached:
    for row in sheet:
        for c in row:assert c.data_type!='e',(sheet.title,c.coordinate,c.value)
hashes=json.loads((W/'qa/input_checks.json').read_text(encoding='utf-8'))['hashes']
preservation={k:hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items()}
assert all(preservation.values()),preservation
verification={'output_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'row_count':102,'numeric_catch_and_ppr':True,'full_precision_descending_sort':True,'zero_catch_missing_tl_count':47,'unknown_annual_ppr_count':0,'frozen_panes':{'Taxon mapping':s.freeze_panes,'Sources':src.freeze_panes},'filters':['TaxonMapping A7:G109',f'MappingSources A4:D{src.max_row}'],'formula_error_count':0,'links':links,'protected_inputs_unchanged':preservation,'visual_review':'Both sheets rendered and inspected: top/middle/bottom taxon ranges and top/bottom source ranges. Long residual group lists and reasons, zero-catch rows, unavailable TL markers, source links and totals are legible.','scientific_changes':False}
(V/'evidence/mapping/appendix_verification.json').write_text(json.dumps(verification,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in verification.items() if k not in ['links','protected_inputs_unchanged']},indent=2))
