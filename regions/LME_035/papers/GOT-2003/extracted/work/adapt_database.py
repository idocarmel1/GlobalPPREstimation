"""Article-local lossless correction of bundled database converter output.
No source/installed skill modifications. Database entries are rebuilt from the
eight import files; no normalization or derived Q/B is written into source fields.
"""
from pathlib import Path
import csv,json,shutil,hashlib
from decimal import Decimal as D
import openpyxl
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work'; M=ROOT/'35_1_Gulf_of_Thailand_1973'
DB=M/'35_Gulf_of_Thailand_35_1_Gulf_of_Thailand_(1973).json'
def rows(name):
    with (M/name).open(encoding='utf-8',newline='') as f:return list(csv.reader(f))
def value(s):return s if s!='' else '-9999'
def cell(v):return None if v in [None,'-9999',''] else v
def main():
    for p in [DB,M/'MASS_BALANCE.md',M/'ewe_conversion.log',DB.with_name(DB.stem+'_reconstructed.xlsx')]:
        target=WORK/('bundled_'+p.name)
        if not target.exists():shutil.copyfile(p,target)
    raw=json.loads((WORK/('bundled_'+DB.name)).read_text(encoding='utf-8'))
    basic=rows('Basic_input.csv');diet=rows('Diet_composition.csv');ba=rows('Biomass_accumulation.csv');land=rows('Landings.csv');disc=rows('Discards.csv')
    supplement={'metadata':dict(openpyxl.load_workbook(M/'Metadata.xlsx',data_only=True).active.values),'fleets':land[0][2:-1],'source_files':{},'landings_by_fleet':{},'discards_by_fleet':{},'diet_import_source':'not reported; bundled import-file writer emits 0 by format convention','classification':'consumers 1-27 and 29-38; primary producers 28 and 39; detritus 40','biomass_basis':'Published t/km^2 density retained without scaling; habitat fraction not reported.'}
    for name in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx']:
        supplement['source_files'][name]=hashlib.sha256((M/name).read_bytes()).hexdigest()
    for i,g in enumerate(raw['group'],1):
        b=basic[i]; n=b[0]; assert n==g['group_seq']
        for idx,key in [(2,'habitat_area'),(3,'biomass_habitat_area'),(5,'pb'),(6,'qb'),(7,'ee'),(8,'other_mort'),(9,'ge'),(10,'gs'),(11,'detritus_import')]:g[key]=value(b[idx])
        g['biomass']=value(b[3])
        g['ge_input']='true' if b[9] else 'false'
        g['pp']='2' if n=='40' else '1' if n in ['28','39'] else '0'
        g['vbk']=g['shadow_price']='-9999'
        g['biomass_accum']=value(ba[i][2]);g['biomass_accum_rate']=str(D(ba[i][2])/D(b[3])) if ba[i][2] and b[3] else '-9999'
        g['export']=value(land[i][-1]);g['diet_imp']='-9999'
        entries=[]
        if n in diet[0]:
            c=diet[0].index(n)
            for r in diet[1:41]:
                if r[c]!='':entries.append({'prey_seq':r[0],'proportion':r[c],'detritus_fate':'-9999'})
        g['diet_descr']={'diet':entries} if entries else None
        supplement['landings_by_fleet'][n]={f:value(v) for f,v in zip(supplement['fleets'],land[i][2:-1])}
        supplement['discards_by_fleet'][n]={f:value(v) for f,v in zip(supplement['fleets'],disc[i][2:-1])}
    # Keep atlas model_number and model identity explicit in the final database.
    raw['metadata']=json.loads((M/'model.json').read_text(encoding='utf-8'))['metadata']
    DB.write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding='utf-8')
    (M/'source_parameters.json').write_text(json.dumps(supplement,ensure_ascii=False,indent=2),encoding='utf-8')
    wb=openpyxl.Workbook();wb.remove(wb.active)
    def sheet(name,data):
        ws=wb.create_sheet(name)
        for r in data:ws.append(r)
        ws.freeze_panes='C2';ws.auto_filter.ref=ws.dimensions
        ws.column_dimensions['B'].width=32
        for c in ws[1]:c.font=openpyxl.styles.Font(bold=True)
    sheet('Metadata',[[k,v] for k,v in supplement['metadata'].items()])
    mappings=['habitat_area','biomass_habitat_area',None,'pb','qb','ee','other_mort','ge','gs','detritus_import']
    sheet('Basic input',[basic[0]]+[[g['group_seq'],g['group_name']]+[cell(g[k]) if k else None for k in mappings] for g in raw['group']])
    consumers=[g for g in raw['group'] if g['pp']=='0']
    matrix=[['','Source / fate']+[g['group_seq'] for g in consumers]]
    maps={g['group_seq']:{v['prey_seq']:v['proportion'] for v in (g['diet_descr'] or {}).get('diet',[])} for g in consumers}
    for g in raw['group']:matrix.append([g['group_seq'],g['group_name']]+[cell(maps[c['group_seq']].get(g['group_seq'])) for c in consumers])
    matrix.append(['','Import']+[cell(g['diet_imp']) for g in consumers])
    matrix.append(['','Sum']+[str(sum((D(v) for v in maps[g['group_seq']].values()),D(0))) for g in consumers])
    sheet('Diet composition',matrix)
    sheet('Biomass accumulation',[ba[0]]+[[g['group_seq'],g['group_name'],cell(g['biomass_accum']),cell(g['biomass_accum_rate'])] for g in raw['group']])
    sheet('Landings totals',[['','Group name','Reported catch total']]+[[g['group_seq'],g['group_name'],cell(g['export'])] for g in raw['group']])
    for title,key in [('Landings fleet','landings_by_fleet'),('Discards fleet','discards_by_fleet')]:
        sheet(title,[['','Group name']+supplement['fleets']]+[[g['group_seq'],g['group_name']]+[cell(supplement[key][g['group_seq']][f]) for f in supplement['fleets']] for g in raw['group']])
    sheet('Detritus fate',[['','Source / fate','Detritus','Export']]+[[g['group_seq'],g['group_name'],None,None] for g in raw['group']])
    sheet('TL',[[None,None,'TL']]+[[g['group_seq'],g['group_name'],None] for g in raw['group']])
    sheet('Read me',[
        ['Provenance','This workbook is reconstructed from the corrected database JSON; fleet sheets use source_parameters.json because the DB schema retains only catch totals.'],
        ['Unknowns','-9999 in JSON becomes a blank cell. Explicit dietary zeros are retained. Diet import blank reflects source silence; import CSV writer emits conventional 0.'],
        ['Derived','The BA rate is derived as the source BA divided by source biomass; it is not entered in the import CSV.'],
        ['Limits','Q/B remains unknown where dashed. Stated P/Q is carried in ge. No diet is normalized. Full source reconstruction is not import-ready.']])
    out=DB.with_name(DB.stem+'_reconstructed.xlsx');wb.save(out)
    # Independent reopen and compare the final DB/workbook to every source cell.
    j=json.loads(DB.read_text(encoding='utf-8'));w=openpyxl.load_workbook(out,data_only=True)
    assert j['metadata']==json.loads((M/'model.json').read_text(encoding='utf-8'))['metadata']
    checks=0
    for i,g in enumerate(j['group'],1):
        for idx,key in [(2,'habitat_area'),(3,'biomass_habitat_area'),(5,'pb'),(6,'qb'),(7,'ee'),(8,'other_mort'),(9,'ge'),(10,'gs'),(11,'detritus_import')]:
            assert g[key]==value(basic[i][idx]);assert w['Basic input'].cell(i+1,idx+1).value==cell(g[key]);checks+=2
        assert g['biomass_accum']==value(ba[i][2]);checks+=1
        assert g['pp']==('2' if i==40 else '1' if i in [28,39] else '0');checks+=1
        if str(i) in diet[0]:
            c=diet[0].index(str(i));dm={x['prey_seq']:x['proportion'] for x in (g['diet_descr'] or {}).get('diet',[])}
            for r in diet[1:41]:
                assert dm.get(r[0])== (r[c] if r[c] else None);checks+=1
    assert len(j['group'])==40
    (M/'ROUNDTRIP_CHECK.md').write_text(f'# Round-trip audit\n\nPASS: {checks} source/JSON/workbook cell checks; 40 groups; correct 37 consumer + 2 producer + 1 detritus classifications; exact original diet values (including explicit zero and -0); unknown Q/B, GS and habitat retained; P/Q carried in ge.\n\nFleet detail is reconstructed from source_parameters.json because the core database schema retains only catch totals. BA rate is explicitly derived. Diet import remains unknown in the DB despite the writer convention in the import CSV.\n',encoding='utf-8')
    with (M/'ewe_conversion.log').open('a',encoding='utf-8') as f:f.write('\nFINAL LOSSLESS ADAPTER: adapt_database.py overrides earlier bundled normalization/defaults/producer inference. Raw bundled outputs archived under extracted/work/bundled_*. Final diets use exact CSV strings; ge retains stated P/Q; pp from established group list; unknown habitat, import, detritus fate, vbk, shadow_price and absent catch -> -9999. BA rate is explicitly derived from source BA/B. Final workbook is rebuilt and independently audited.\n')
    print('Corrected DB and round-trip workbook; checks',checks)
if __name__=='__main__':main()
