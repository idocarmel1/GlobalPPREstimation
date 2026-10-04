from pathlib import Path
import json,hashlib,pymupdf,zipfile,xml.etree.ElementTree as ET
root=Path.cwd();out=root/'regions/HS_071/diet_reextraction_20261002';reg=root/'regions/HS_071';mid='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)';base=reg/'models'/mid
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(root).as_posix()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
write=lambda n,x:(out/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
pdf=reg/'papers/WCP-2007/download-0adcf55e.pdf';doc=pymupdf.open(pdf)
src=root/'regions/EEZ_941/papers/WCP-2007/extraction_evidence'
selected=read(base/(mid+'.json'));names={g['group_name']:g for g in selected['group']}
cells=[c for c in read(src/'cell_evidence.json') if c['table']==4 and c['column'].endswith('|Final') and c['column'].split('|')[0] in names and c['row'] in names]
checks=[]
for c in cells:
    p=doc[c['page']-1]
    matches=[]
    for w in p.get_text('words'):
        bbox=list(pymupdf.Rect(w[:4])*p.rotation_matrix)
        if max(abs(a-b) for a,b in zip(bbox,c['bbox']))<=1e-5:matches.append(w[4])
    g=names[c['column'].split('|')[0]]
    prey_seq=names[c['row']]['group_seq']
    native=next((x['proportion'] for x in g['diet_descr']['diet'] if x['prey_seq']==prey_seq),None)
    checks.append({'source_page':c['page'],'source_table':4,'prey':c['row'],'consumer':g['group_name'],'source_bbox':c['bbox'],'retained_source_literal':c['text'],'actual_HS071_pdf_tokens':matches,'selected_literal':native,'pdf_coordinate_and_selected_exact':matches==[c['text']] and native==c['text']})
assert len(checks)==252 and all(c['pdf_coordinate_and_selected_exact'] for c in checks)
page7=doc[6].get_text();(out/'source_pdf7_text.txt').write_text(page7,encoding='utf-8')
original=root/'regions/EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)/model.json'
old=read(original);deltas=[]
for i,(a,b) in enumerate(zip(old['group'],selected['group'])):
    for k in sorted(set(a)|set(b)):
        if a.get(k)!=b.get(k):deltas.append({'seq':b['group_seq'],'group':b['group_name'],'field':k,'source_value':a.get(k),'accepted_selected_value':b.get(k)})
write('primary_source_verification.json',{'region':'HS_071','local_pdf':rel(pdf),'local_pdf_sha256':sha(pdf),'shared_original_pdf_sha256':sha(src.parent/'download-0adcf55e.pdf'),'same_exact_source_pdf':sha(pdf)==sha(src.parent/'download-0adcf55e.pdf'),'reextraction_performed':False,'operation':'Read-only coordinate confirmation of retained transcription; no new extraction or canonical restoration','table4_final_printed_cell_count':len(checks),'all_local_primary_coordinates_match':all(c['pdf_coordinate_and_selected_exact'] for c in checks),'source_pages_visually_inspected':[12,13],'source_render_paths':[rel(src/'page_12.png'),rel(src/'page_13.png')],'page7_import_evidence':'Section2.2 explicitly says no imports and exports were considered; no external living input, diet import0 retained under original extraction. Exact page text saved locally.','original_source_model_path':rel(original),'original_source_model_sha256':sha(original),'all_source_to_accepted_group_field_differences':deltas,'checks':checks})
write('source_inventory.json',{'schema_version':1,'region':'HS_071','selected_model_id':mid,'artifacts':[{'path':rel(p),'sha256':sha(p)} for p in [pdf,src/'source_tables.json',src/'cell_evidence.json',src/'final_extraction.json',src/'extract_source.py',original,original.parent/'extracted_tables/Diet_composition.csv',original.parent/'extracted_tables/converter_to_canonical_audit.json',base/'SELECTION_AND_PROVENANCE.json',base/'diagnostic_evidence/experiment_PROVENANCE.json',base/'diagnostic_evidence/loaded_groups.csv']],'source_native_limit':'No author-native EwE file in selected bundle. Printed-source retention verified. Existing sparse blank cells are retained structural absence conventions, not newly measured zeros; no independent all-cell diet signoff established.'})
print(json.dumps({'local_pdf_cells_verified':len(checks),'source_to_accepted_differences':[(d['seq'],d['field']) for d in deltas]}))
