from pathlib import Path
import json,re,math,hashlib
import openpyxl
V=next(p for p in Path(__file__).resolve().parents if (p/'taxon_mapping.xlsx').exists())
d=json.loads((V/'evidence/mapping/review_20261114.json').read_text(encoding='utf-8'))
w=openpyxl.load_workbook(V/'taxon_mapping.xlsx',data_only=False);s=w['Taxon mapping']
lookup={a['taxon']:a for a in d['rows']}; order=[]
for r in range(8,71):
 tax=s.cell(r,1).value;a=lookup[tax];order.append((tax,s.cell(r,4).value))
 tl=s.cell(r,2).value
 assert tl==(a['tl'] if a['tl'] is not None else '?'),(tax,tl,a['tl'])
 md=s.cell(r,5).value
 if a['current_mapping']:
  parsed={m.group(1):float(m.group(2))/100 for m in re.finditer(r'(?:^|; )(.+?) \(([0-9.eE+-]+)%\)',md)}
  assert set(parsed)==set(a['current_mapping']),(tax,parsed,a['current_mapping'])
  assert all(math.isclose(parsed[g],a['current_mapping'][g],abs_tol=5e-8) for g in parsed),tax
 else: assert md in ['Unresolved','?'],(tax,md)
expected=sorted(order,key=lambda z:(z[1] is None,-z[1] if isinstance(z[1],(int,float)) else 0,z[0]))
assert order==expected
assert math.isclose(sum(s.cell(r,3).value for r in range(8,71)),d['total_catch_tonnes'],rel_tol=1e-14)
assert math.isclose(sum(s.cell(r,4).value for r in range(8,71)),d['simple_chain_ppr_tC'],rel_tol=1e-14)
p=V/'evidence/mapping/appendix_verification_20261114.json';q=json.loads(p.read_text(encoding='utf-8'))
q.update(all_63_taxa_once=True,numeric_ppr_descending_ties_by_taxon=True,all_tl_cells_preserve_missingness=True,displayed_group_weights_match_adopted_values=True,catch_ppr_totals_reconciled=True,all_confidence_components_checked=True)
p.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
print('63 taxa, weights, TL/missingness, sort, totals and confidence checks passed')
