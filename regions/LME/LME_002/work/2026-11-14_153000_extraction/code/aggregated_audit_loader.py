"""Narrow source-to-ModelData ledger; no calculator or parameter solving."""
import contextlib, csv, io, json, math, sys
from decimal import Decimal
from aggregated_extract import ROOT,RUN,MODEL,MODEL_ID,dump,sha

def main():
    ev=MODEL/'extracted_tables/evidence';path=MODEL/'model.json'
    before=sha(path);raw=json.loads(path.read_text(encoding='utf-8'))
    sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
    from ModelData import ModelData
    buffer=io.StringIO()
    with contextlib.redirect_stdout(buffer),contextlib.redirect_stderr(buffer):loaded=ModelData(str(path))
    mappings={'biomass':'biomass','pb':'pb','qb':'qb','ee':'ee','ge':'ge','gs':'gs','tl':'tl','biomass_accum':'biomass_accum','detritus_import':'detritus_import','export':'catch'}
    records=[];differences=[]
    for group in raw['group']:
        seq=int(group['group_seq'])
        for source,dest in mappings.items():
            literal=group.get(source,'-9999');value=loaded.groups_data.loc[seq,dest]
            source_unknown=literal=='-9999';runtime_unknown=bool(__import__('pandas').isna(value))
            same=source_unknown and runtime_unknown or not source_unknown and not runtime_unknown and abs(Decimal(str(value))-Decimal(literal))<=max(Decimal('1e-12'),abs(Decimal(literal))*Decimal('1e-14'))
            record={'group_id':seq,'group_name':group['group_name'],'source_field':source,'runtime_field':dest,'source_literal':literal,'runtime_value':None if runtime_unknown else float(value),'source_unknown':source_unknown,'runtime_unknown':runtime_unknown,'same_numeric_and_missingness':same}
            if not same:
                record['explanation']='Loader default DetInput0; nativeRpath also explicitly converts DetInputNA to0 (Rpath_ecopath.R). Source canonical remains−9999.' if source=='detritus_import' and source_unknown and value==0 else 'Runtime difference requires review; no source value changed.'
                differences.append(record)
            records.append(record)
    dietchecks=[]
    for group in raw['group']:
        if not group.get('diet_descr'):continue
        seq=int(group['group_seq'])
        for entry in group['diet_descr']['diet']:
            prey=int(entry['prey_seq']);literal=entry['proportion'];v=loaded.DC.loc[seq,prey]
            missing=bool(__import__('pandas').isna(v))
            same=(literal=='-9999' and missing) or (literal!='-9999' and not missing and abs(Decimal(str(v))-Decimal(literal))<=Decimal('1e-12'))
            dietchecks.append({'consumer_id':seq,'prey_id':prey,'source_literal':literal,'runtime_value':None if missing else float(v),'same_numeric_and_missingness':same})
    loaded.DC.to_csv(ev/'loader_diet_matrix.csv',index=True)
    loaded.det_fate.to_csv(ev/'loader_detritus_fate_matrix.csv',index=True)
    audit={'schema_version':1,'model_id':MODEL_ID,'canonical_sha256':before,'canonical_unchanged':before==sha(path),'scope':'ModelData constructor only; no PPRCalculator or native Rpath balance','fields':records,'differences':differences,'all_source_unknown_EE_preserved':all(r['runtime_unknown'] for r in records if r['source_field']=='ee'),'diet_checks':dietchecks,'diet_all_values_and_missingness_match':all(r['same_numeric_and_missingness'] for r in dietchecks),'runtime_logs':buffer.getvalue(),'matrix_orientation':'Diet rows=consumers, columns=prey; synthetic diet_import=50. Detritus fate rows=source groups, columns=detritus groups. CSV blanks preserve runtimeNaN.','limitations':'These runtime views are audit evidence only and are not canonical source model inputs.'}
    dump(ev/'source_to_loader_ledger.json',audit)
    print(json.dumps({'canonical_unchanged':audit['canonical_unchanged'],'fields_checked':len(records),'field_differences':len(differences),'diet_cells_checked':len(dietchecks),'diet_masks_and_values_match':audit['diet_all_values_and_missingness_match']},indent=2))

if __name__=='__main__':main()
