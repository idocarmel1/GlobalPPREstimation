"""Read-only delivery checks; authoring is handled by Artifact Tool."""
from pathlib import Path
import json, hashlib, re, copy
import openpyxl
from PIL import Image, ImageChops

root=Path.cwd()
v=root/'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991/model_validation'
w=v/'work/2026-11-14_200000_ices_full_review'
d=json.loads((v/'evidence/mapping/mapping_decisions.json').read_text(encoding='utf8'))
identities={}
for relative,expected in d['input_sha256'].items():
    actual=hashlib.sha256((root/relative).read_bytes()).hexdigest()
    assert actual==expected,relative
    identities[relative]=actual
before=openpyxl.load_workbook(w/'inputs/taxon_mapping_before.xlsx',data_only=False)
final=openpyxl.load_workbook(v/'taxon_mapping.xlsx',data_only=False)
assert before.sheetnames==final.sheetnames
bd=before['SPPR diagnostics'];fd=final['SPPR diagnostics']
assert bd.max_row==fd.max_row and bd.max_column==fd.max_column
for row in bd:
    for c in row:
        f=fd[c.coordinate]
        assert c.value==f.value,(c.coordinate,'value')
        # openpyxl may renumber equivalent custom number formats on read.
        # Compare observable style properties; original raw style slots are
        # separately verified in appendix_package_preservation.json.
        for attr in ['font','fill','border','alignment','protection','number_format']:
            assert copy.copy(getattr(c,attr))==copy.copy(getattr(f,attr)),(c.coordinate,attr)
        assert c.hyperlink==f.hyperlink,(c.coordinate,'hyperlink')
        assert c.comment==f.comment,(c.coordinate,'comment')
assert bd.freeze_panes==fd.freeze_panes
assert str(bd.merged_cells)==str(fd.merged_cells)
assert {k:str(v) for k,v in bd.row_dimensions.items()}=={k:str(v) for k,v in fd.row_dimensions.items()}
assert {k:str(v) for k,v in bd.column_dimensions.items()}=={k:str(v) for k,v in fd.column_dimensions.items()}
original=Image.open(w/'qa/diagnostics_before.png').convert('RGBA')
current=Image.open(w/'qa/diagnostics_final.png').convert('RGBA')
assert original.size==current.size
assert ImageChops.difference(original,current).getbbox() is None,'Diagnostic rendering changed'
sheet=final['Taxon mapping']
assert [sheet.cell(i+8,1).value for i in range(384)]==[r['taxon'] for r in d['rows']]
assert sheet.freeze_panes=='B8'
assert any(t.ref=='A7:G391' for t in sheet.tables.values())
links=[]
for i,s in enumerate(d['sources'],5):
    cell=final['Sources'].cell(i,3)
    target=s.get('path') or s.get('url')
    assert target in cell.value,(s['id'],'link')
    assert cell.font.underline=='single' and cell.font.color.rgb=='FF0563C1',(s['id'],'style')
    if s.get('path'):assert (v/target).resolve().is_file(),target
    links.append({'source_id':s['id'],'target':target})
result={'status':'PASS','final_appendix_sha256':hashlib.sha256((v/'taxon_mapping.xlsx').read_bytes()).hexdigest(),'unchanged_consumed_input_hashes':identities,'diagnostics_all_cells_values_styles_links_comments_preserved':True,'diagnostics_dimensions_freeze_merges_preserved':True,'diagnostics_render_pixel_identical':True,'exact_taxon_order_preserved_from_decisions':True,'source_links_and_visual_styles_valid':links,'visually_inspected':['mapping_top.png','mapping_mid.png','mapping_bottom.png','mapping_sources_1.png','mapping_sources_2.png','mapping_largest_split_final.png','diagnostics_final.png','mapping_sources_2_final.png'],'visual_result':'No clipping, overlaps or unreadable content in inspected ranges; largest 36-group split fully visible.'}
(w/'qa/final_mapping_package_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'status':result['status'],'sha256':result['final_appendix_sha256'],'diagnostic_pixels_identical':True,'input_hashes_unchanged':len(identities),'taxa':len(d['rows']),'source_links':len(links)}))
