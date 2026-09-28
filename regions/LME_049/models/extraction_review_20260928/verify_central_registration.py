from pathlib import Path
import json,zipfile,hashlib,xml.etree.ElementTree as ET
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());OUT=Path(__file__).parent
# Reuse only the reviewed helper's read-only function definitions.
exec((OUT/'register_central_metadata.py').read_text(encoding='utf-8').split('proposal=json.loads')[0])
audit=json.loads((OUT/'CENTRAL_REGISTRATION_VERIFICATION.json').read_text(encoding='utf-8'));assert audit['status']=='APPLIED'
before=ROOT/audit['backup'];after=ROOT/'Project.xlsx';assert sha(after)==audit['after_sha256']
def read(target,part):
    global SHARED
    with zipfile.ZipFile(target) as z:
        SHARED=[''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
        return parse(ET.fromstring(z.read(part)))
checked_lme022=0
for part in ['xl/worksheets/sheet2.xml','xl/worksheets/sheet3.xml']:
    _,bh,br=read(before,part);_,ah,ar=read(after,part);assert bh==ah
    before_rows=[dict(zip(bh,r)) for r in br];after_rows=[dict(zip(ah,r)) for r in ar]
    unit_index=bh.index('unit_id');key='article_id' if 'article_id' in bh else 'model_id';by_key={r[key]:r for r in after_rows}
    for r in before_rows:
        if r['unit_id']=='LME_022':assert by_key[r[key]]==r;checked_lme022+=1
        assert by_key[r[key]]['selected']==r['selected']
    if key=='model_id':
        ids=[(r['unit_id'],r['model_id']) for r in after_rows];assert len(ids)==len(set(ids))
        added=[r for r in after_rows if r['unit_id']=='LME_049'];assert len(added)==2
        for r in added:
            assert r['selected'] is False and r['selection_rationale'] is None
            assert (ROOT/r['model_path']).is_file()
            assert r['paper_ids'] in ['KUR-2019__LME_049','KUR-2025__LME_049']
    else:
        p2019=by_key['KUR-2019__LME_049'];p2025=by_key['KUR-2025__LME_049']
        assert p2025['authors']=='Chen et al.' and p2025['legacy_authors']=='Gan et al.'
        assert 'USER-PREFERRED SOURCE' in p2019['notes'] and 'Exact model not selected' in p2019['notes']
        assert 'Gan Chen' in p2025['correction_notes']
        for p in [p2019,p2025]:assert p['region_rank']==20 and p['atlas_region_rank']==12
for mid in ['49_20192013_Western_North_Pacific_Watari_(2013)','49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023)']:
    dest=ROOT/'regions/LME_049/models'/mid
    for m in json.loads((dest/'source_manifest.json').read_text(encoding='utf-8')):assert sha(ROOT/m['path'])==m['sha256']
    text=(dest/'extracted_tables/REPORT.md').read_text(encoding='utf-8');text=text.replace('Central metadata registration is staged for parent-agent serialization.','Central metadata registration was applied to Project.xlsx on 2026-09-28; two unselected model rows and the corresponding paper records are registered.');(dest/'extracted_tables/REPORT.md').write_text(text,encoding='utf-8')
original_proposal=OUT/'metadata_registration_proposal.json';p=json.loads(original_proposal.read_text(encoding='utf-8'));p['central_registration_status']='APPLIED; two unselected model rows; CENTRAL_REGISTRATION_VERIFICATION.json records backup and exact changes';original_proposal.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
result={'status':'PASS','unrelated_LME022_paper_and_model_records_byte_value_unchanged':checked_lme022,'all_existing_selected_flags_unchanged':True,'two_new_models_unselected':True,'new_model_links_exist':True,'correct_central_paper_ids':True,'Chen_citation_corrected_prior_citation_retained':True,'Watari_source_preference_only':True,'paper_historical_region_rank_preserved':20,'atlas_region_rank_preserved':12,'original_source_hashes_unchanged':True,'package_parts_modified':audit['modified_package_parts'],'native_tables_and_filters':len(audit['tables_verified']),'other_package_parts_byte_identical':audit['other_package_parts_byte_identical'],'Project_after_sha256':sha(after)}
(OUT/'CENTRAL_REGISTRATION_POSTCHECK.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
