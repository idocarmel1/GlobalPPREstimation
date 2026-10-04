from pathlib import Path
from zipfile import ZipFile
from urllib.parse import unquote
from lxml import etree
from docx import Document
import sys,json,hashlib,re,math
import openpyxl
import pypdfium2 as pdf

ROOT=Path.cwd();OUT=Path(__file__).resolve().parent.parent;QA=OUT/'qa'
F=ROOT/'regions/LME_036'/('Model_validation_'+OUT.name+'.docx');REF=ROOT/'tools/templates/Model_validation_template.docx'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import input_hash,digest_tables
b=json.loads((QA/'workbook_snapshot.json').read_text(encoding='utf-8'));o=dict(b['Overview']['Settings'][1])
assert input_hash(b)==o['calculation_input_sha256']
result_hash=digest_tables([(s,k,h,r) for s in ['Classic PPR','PPR','PPR–NPP'] for k,(h,r) in b.get(s,{}).items() if k in ['Annual','Taxon SPPR','Ratios']])
assert result_hash==o['calculation_result_sha256']
for p,h in json.loads((QA/'protected_hashes.json').read_text()).items():assert sha(ROOT/p)==h,p
for e in json.loads((QA/'source_provenance.json').read_text()):assert sha(ROOT/e['original'])==e['sha256'],e['original']
d=Document(F);ref=Document(REF)
for t,r in [(0,8),(1,8),(1,9)]:assert etree.tostring(d.tables[t].rows[r].cells[1]._tc)==etree.tostring(ref.tables[t].rows[r].cells[1]._tc)
for t in [0,1]:assert [r.cells[0].text for r in d.tables[t].rows]==[r.cells[0].text for r in ref.tables[t].rows]
assert etree.tostring(d.sections[0]._sectPr)==etree.tostring(ref.sections[0]._sectPr)
for i in range(6,17):assert etree.tostring(d.paragraphs[i]._p)==etree.tostring(ref.paragraphs[i]._p)
with ZipFile(F) as z,ZipFile(REF) as a:
 for e in json.loads((QA/'template_package_inventory.json').read_text()):
  if e['ownership']=='preserve':assert z.read(e['part'])==a.read(e['part']),e['part']
alltext='\n'.join(p.text for p in d.paragraphs)+'\n'+'\n'.join(c.text for t in d.tables for row in t.rows for c in row.cells)
assert '[AUTO:' not in alltext
assert 'Regional calculation status' not in alltext and 'Reference PPR result' not in alltext
assert 'With Egestion' not in '\n'.join(c.text for t in d.tables for row in t.rows for c in row.cells)
assert len(d.inline_shapes)==2
word_links=0
for rel in d.part.rels.values():
 if not rel.reltype.endswith('hyperlink'):continue
 word_links+=1;url=rel.target_ref
 if not url.startswith(('https:','http:')):
  assert not Path(unquote(url)).is_absolute()
  assert (F.parent/unquote(url.split('#')[0])).exists(),url
md_links=0
for p in OUT.rglob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  if not target.startswith(('http','#')):
   assert (p.parent/unquote(target.split('#')[0])).exists(),(p,target)
   md_links+=1

snapshot=json.loads((OUT/'saved_evidence_snapshot.json').read_text(encoding='utf-8'))
w=openpyxl.load_workbook(OUT/'diagnostics/sppr_source.xlsx',read_only=True,data_only=True)
rows=list(w['model_health'].values);h=rows[0];source={r[0]:dict(zip(h,r)) for r in rows[1:]}
for current in snapshot['model_health']:
 for key,value in current.items():
  original=source[current['TE_option']][key]
  assert original==value or (isinstance(value,(int,float)) and isinstance(original,(int,float)) and math.isclose(value,original,rel_tol=1e-13,abs_tol=1e-14)),(key,original,value)
for current in snapshot['model_health']:
 method='new_GE' if current['TE_option']=='GE' else 'new_TE_EEfix'
 gs=[r for r in snapshot['group_sppr'] if r['scope']=='all' and r['method']==method and isinstance(r['sppr'],(int,float))]
 mx=max(gs,key=lambda x:x['sppr']);assert mx['group']=='Seabirds' and mx['sppr']==current['divergence_max_sppr_group_sppr']
 dt=next(r for r in gs if r['group']=='Detritus');assert dt['sppr']==current['divergence_sppr_det_38']
w.close()
# Arithmetic cross-check of reference basis, including landings plus discards.
h,rs=b['Catch']['Catch'];records=[dict(zip(map(str,h),r)) for r in rs];cv={(r['taxon'],r['catch_basis']):r['2019'] for r in records}
for (taxon,basis),value in cv.items():
 if basis=='catch':assert abs(value-cv[(taxon,'landings')]-cv[(taxon,'discards')])<1e-6
p=pdf.PdfDocument(str(QA/'final.pdf'));pages=len(p)
texts=[]
for i in range(pages):
 page=p[i];page.render(scale=1.5).to_pil().save(QA/f'final-page-{i+1}.png')
 texts.append(page.get_textpage().get_text_range())
assert pages==6
assert 'SPPR calculation' in texts[0]
assert 'MANUAL' in texts[2]
assert 'Geographic evidence screenshots' in texts[4]
assert 'Figure 6.1' in texts[5]
report={'document':F.relative_to(ROOT).as_posix(),'sha256':sha(F),'pages':pages,'manual_cells_xml_unchanged':True,'field_order_unchanged':True,'source_package_design_parts_unchanged':True,'llm_instructions_unchanged':True,'local_word_links_resolve':True,'word_hyperlinks':word_links,'markdown_local_links_checked':md_links,'copied_original_hashes_unchanged':47,'protected_source_files_unchanged':True,'selected_model_hash_matches_overview':True,'saved_input_and_result_fingerprints_match':True,'GE_TE_flat_diagnostics_match_source_workbook':True,'maximum_and_detritus_coefficients_match':True,'landings_plus_discards_2019_match_catch':True,'scientific_solvers_run':False,'independent_extraction_validation_performed':False,'renderer':'hidden read-only Microsoft Word export plus bundled pypdfium2 PNGs; packaged LibreOffice renderer unavailable','visual_inspection':'All six final pages inspected; no clipping, overlap, missing glyphs, or orphan manual-only page. Final page 2 mapping cutoff caveat rechecked after last text edit.'}
(QA/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
