"""Keep bundled conversion reviewable, restore source values, verify round trip."""
from pathlib import Path
import json,csv,sys,shutil,copy
from decimal import Decimal
from openpyxl import Workbook,load_workbook
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work'
MODEL=ROOT/'HS_077_1_Eastern_tropical_Pacific_1993-1997'
SKILL=Path(r'C:\Users\idoca\.agents\skills\ecopath-extraction\scripts')
sys.path.insert(0,str(SKILL))
from database_json import EwEConverter
DB=next(p for p in MODEL.glob('HS_077_Pacific_*.json'))
RAW=WORK/'raw_converter'
RAW.mkdir(exist_ok=True)
for p in [DB,MODEL/'ewe_conversion.log',MODEL/'MASS_BALANCE.md',DB.with_name(DB.stem+'_reconstructed.xlsx')]:
    if p.exists() and not (RAW/p.name).exists(): shutil.copy2(p,RAW/p.name)
def read(name):
    with (MODEL/name).open(encoding='utf-8',newline='') as f:return list(csv.reader(f))
basic=read('Basic_input.csv')
diet=read('Diet_composition.csv')
fate=read('Detritus_fate.csv')
ba=read('Biomass_accumulation.csv')
land=read('Landings.csv')
disc=read('Discards.csv')
unknown='-9999'
def src(s):return s if s!='' else unknown
def flg(s):return 'true' if s!='' else 'false'
raw=json.loads(DB.read_text(encoding='utf-8'))
template=raw['group'][0]
raw_by={g['group_seq']:g for g in raw['group']}
groups=[]
for row in basic[1:]:
    n=row[0]
    g=copy.deepcopy(raw_by.get(n,template))
    g.update(group_seq=n,group_name=row[1],habitat_area=src(row[2]),
        biomass_habitat_area=src(row[3]),biomass=src(row[3]),
        b_hab_area_input=flg(row[3]),pb=src(row[5]),pb_input=flg(row[5]),
        qb=src(row[6]),qb_input=flg(row[6]),ee=src(row[7]),ee_input=flg(row[7]),
        other_mort=src(row[8]),ge=src(row[9]),ge_input=flg(row[9]),gs=src(row[10]),
        detritus_import=src(row[11]),biomass_accum=unknown,biomass_accum_rate=unknown,
        vbk=unknown,shadow_price=unknown,
        pp='2' if n=='39' else ('1' if n in ['37','38'] else '0'))
    # Publication B is already a model-area density; preserve it directly.
    # Unknown habitat fraction never authorizes a multiplication by 1.
    known_catch=[r[-1] for t in [land,disc] for r in t[1:] if r[0]==n and r[-1]!='']
    g['export']=format(sum(map(Decimal,known_catch)),'f') if known_catch else unknown
    g['diet_imp']=unknown
    entries=[]
    if n in diet[0]:
        c=diet[0].index(n)
        for rowd in diet[1:]:
            if rowd[1]=='Import':g['diet_imp']=src(rowd[c])
            elif rowd[0].isdigit() and rowd[c]!='':
                entries.append({'prey_seq':rowd[0],'proportion':rowd[c],'detritus_fate':unknown})
    # Carry the explicitly identified detritus pool even when no fate is known.
    # Null proportions are unknown; no fraction is allocated by default.
    if not any(e['prey_seq']=='39' for e in entries):
        entries.append({'prey_seq':'39','proportion':unknown,'detritus_fate':unknown})
    g['diet_descr']={'diet':entries}
    g['taxon_descr']=None
    groups.append(g)
source_metadata=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))['metadata']
DB.write_text(json.dumps({'metadata':source_metadata,'group':groups},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
supp={'basis':'B is published model-area density; habitat fraction unknown; no scaling performed.',
      'fleets':land[0][2:-1],'landings':land,'discards':disc,
      'z_by_group':{r[0]:src(r[4]) for r in basic[1:]},
      'trophic_levels':list(load_workbook(MODEL/'TL.xlsx',data_only=True).active.values),
      'metadata':list(load_workbook(MODEL/'Metadata.xlsx',data_only=True).active.values)}
(MODEL/'source_parameters.json').write_text(json.dumps(supp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
changes=['Post-conversion source-preserving adapter: work/adapt_database.py.',
'Raw bundled outputs preserved in work/raw_converter.',
'Restored source diet proportions without normalization, including all 315 populated cells.',
'Retained detritus group39 omitted by the bundled converter.',
'Blank habitat, import, catch, fate, vbk and shadow price retained as -9999.',
'B carried as published model-area density; no unknown habitat-area multiplication.',
'Reconstructed workbook rebuilt from corrected JSON; source_parameters.json supplements fields absent from database schema (fleet catches, Z, TL and metadata).',
'Published diet defects and all unknown BA remain unchanged.']
with (MODEL/'ewe_conversion.log').open('a',encoding='utf-8') as f:f.write('\nSOURCE-PRESERVING ADAPTER\n'+'\n'.join(changes)+'\n')
# Rerun the bundled equations using the corrected database's values.
converter=EwEConverter(log_file=str(MODEL/'adapter_massbalance.log'))
total_disc=sum((Decimal(r[-1]) for r in disc[1:] if r[-1]),Decimal(0))
findings=converter.check_mass_balance(groups,float(total_disc),0.05)
converter.report_mass_balance(findings,'Eastern tropical Pacific ETP7 (1993-1997)',str(MODEL/'MASS_BALANCE.md'))
mb=(MODEL/'MASS_BALANCE.md').read_text(encoding='utf-8')
mb=mb.replace('ewe_model_json_creator.py','database_json.py (corrected JSON via local adapter)')
mb=mb.replace('which is a lower bound on what the model may actually contain, not a steady-state result.','which is a conditional diagnostic, not a steady-state result or a bound when the sign of BA is unknown.')
mb=mb.replace('Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.','Migration (E): source assumes immigration balances emigration (printed pp.137 and 146); no separate numeric gross migration rates are provided. No migration rate was synthesized.')
(MODEL/'MASS_BALANCE.md').write_text(mb,encoding='utf-8')
with (MODEL/'MASS_BALANCE.md').open('a',encoding='utf-8') as f:
    f.write('\n## Scope of this arithmetic verdict\n\nThe bundled arithmetic verdict does not check unit diet sums, completeness of detritus routing, or all unknown fields. Nine source diet columns fail structural validation. This extraction is **PARTIAL / NOT IMPORT-READY**, even when its EE arithmetic is consistent. Detritus routing and BA are unknown; the reported pooled-detritus result is indicative and does not establish closure of the unpublished routing.\n')
# Reconstruct each source-shaped sheet from corrected database parameters.
by={g['group_seq']:g for g in groups}
rb=[basic[0]]
mp={2:'habitat_area',3:'biomass_habitat_area',5:'pb',6:'qb',7:'ee',8:'other_mort',9:'ge',10:'gs',11:'detritus_import'}
def blank(v):return '' if v==unknown else v
for r in basic[1:]:
    vals=[r[0],r[1]]+['']*10
    for col,key in mp.items():vals[col]=blank(by[r[0]][key])
    vals[4]=blank(supp['z_by_group'][r[0]])
    rb.append(vals)
rd=[diet[0]]
for r in diet[1:]:
    vals=r[:2]
    for n in diet[0][2:]:
        g=by[n]
        entries=g['diet_descr']['diet']
        if r[0].isdigit():v=next((blank(e['proportion']) for e in entries if e['prey_seq']==r[0]),'')
        elif r[1]=='Import':v=blank(g['diet_imp'])
        elif r[1]=='Sum':v=format((sum((Decimal(e['proportion']) for e in entries if e['proportion']!=unknown),Decimal(0))+(Decimal(g['diet_imp']) if g['diet_imp']!=unknown else Decimal(0))).normalize(),'f')
        else:v='0'
        vals.append(v)
    rd.append(vals)
assert rb==basic
assert rd==diet
sheets={'Basic_input':rb,'Diet_composition':rd,'Landings':supp['landings'],'Discards':supp['discards'],'Detritus_fate':fate,'Biomass_accumulation':ba,'TL':supp['trophic_levels'],'Metadata':supp['metadata']}
wb=Workbook()
wb.remove(wb.active)
from openpyxl.styles import Font,PatternFill,Alignment
for name,rows in sheets.items():
    ws=wb.create_sheet(name)
    for rr in rows:
        ws.append([None if v in ['',None] else v for v in rr])
    ws.freeze_panes='C2'
    for c in ws[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='234957')
    ws.column_dimensions['A'].width=9;ws.column_dimensions['B'].width=32
    for c in list(ws.columns)[2:]:ws.column_dimensions[c[0].column_letter].width=16
    ws.row_dimensions[1].height=45
    for c in ws[1]:c.alignment=Alignment(wrap_text=True,vertical='center')
    ws.auto_filter.ref=ws.dimensions
    ws.sheet_view.showGridLines=True
notes=wb.create_sheet('Reconstruction notes')
for t in changes:notes.append([t])
notes.column_dimensions['A'].width=110
for row in notes:row[0].alignment=Alignment(wrap_text=True);notes.row_dimensions[row[0].row].height=36
xlsx=DB.with_name(DB.stem+'_reconstructed.xlsx')
wb.save(xlsx)
reopened=load_workbook(xlsx,data_only=True)
checked=0
for name,rows in sheets.items():
    ws=reopened[name]
    for i,row in enumerate(rows,1):
        for j,value in enumerate(row,1):
            expected=None if value in ['',None] else value
            assert ws.cell(i,j).value==expected,(name,i,j,expected,ws.cell(i,j).value)
            checked+=1
audit={'database_group_count':len(groups),'source_diet_values':315,'source_and_reconstructed_cells_checked':checked,
       'all_unknown_ba_preserved':all(g['biomass_accum']==unknown and g['biomass_accum_rate']==unknown for g in groups),
       'all_unknown_habitat_preserved':all(g['habitat_area']==unknown for g in groups),
       'no_diet_normalization':True,'numeric_verdict':findings.get('verdict'),'limitations':changes}
(MODEL/'roundtrip_verification.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
print(json.dumps(audit,indent=2))
