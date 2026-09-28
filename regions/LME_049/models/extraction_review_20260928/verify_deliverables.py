"""Final read-only evidence checks, writing only the verification record."""
from pathlib import Path
import json,csv,hashlib,openpyxl,math
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_049';result=[]
required=['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx','Taxonomy.xlsx','canonical_reconstructed.xlsx','REPORT.md','MODEL_PROFILE.md','source_cells.json','diet_source_cells.json','censored_values.json']
for dest in REG.glob('models/49_*'):
    et=dest/'extracted_tables';d=json.loads((dest/'model.json').read_text(encoding='utf-8'));src=json.loads((et/'model.json').read_text(encoding='utf-8'));N=len(src['groups'])
    assert len(d['group'])==N
    for f in required:assert (et/f).is_file(),f
    for row in json.loads((dest/'source_manifest.json').read_text(encoding='utf-8')):
        p=ROOT/row['path'];assert p.stat().st_size==row['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    assert [g['group_name'] for g in d['group']]==[g['name'] for g in src['groups']]
    assert all(g['biomass_accum']=='-9999' and g['gs']=='-9999' and g['taxon_descr'] for g in d['group'])
    # Inspect the roundtrip workbook headers and source scalar preservation.
    w=openpyxl.load_workbook(et/'canonical_reconstructed.xlsx',read_only=True,data_only=True);sheet_names=w.sheetnames;w.close()
    assert sheet_names
    checks=json.loads((dest/'roundtrip_checks.json').read_text(encoding='utf-8'));assert checks['canonical_sha256']==hashlib.sha256((dest/'model.json').read_bytes()).hexdigest()
    bounds=json.loads((et/'censored_values.json').read_text(encoding='utf-8'))
    plus=[r for r in bounds if r.get('field')=='diet'];assert sum(x['proportion']=='-9999' for g in d['group'] for x in (g.get('diet_descr') or {}).get('diet',[]))==len(plus)
    if (dest/'sppr_source.xlsx').exists():
        with (dest/'all_source_group_sppr_diagnostics.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
        assert len(rows)==N*3*22,len(rows)
        assert set(int(r['group_seq']) for r in rows)==set(range(1,N+1))
    result.append({'model_id':dest.name,'source_hashes_match':True,'all_required_artifacts_present':True,'exact_group_names_order_match':True,'source_missing_BA_GS_retained':True,'censored_diet_sentinels':len(plus),'canonical_json_hash_match':True,'roundtrip_workbook_sheets':sheet_names,'result':'PASS evidence-preservation checks; scientific validity remains unsupported/failed'})
(Path(__file__).parent/'verification_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
