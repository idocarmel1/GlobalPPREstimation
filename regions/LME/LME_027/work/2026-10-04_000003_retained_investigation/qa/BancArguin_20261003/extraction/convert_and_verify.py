"""Audit stock converter, preserve its raw output, then restore source fields.

No source or installed/shared tool is changed. Workbook reconstruction reads
canonical database JSON only. Every source cell and standard field is checked.
"""
from pathlib import Path
import json,csv,copy,hashlib,subprocess,sys,os,shutil,re
from decimal import Decimal as D
import openpyxl
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def nd(v):return '-9999' if v is None or str(v).strip()=='' else str(v)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvread(p):return list(csv.reader(p.open(encoding='utf-8',newline='')))
files=['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx']
env=dict(os.environ,PYTHONIOENCODING='utf-8')
tool_inventory=[]
for name in ['write_outputs.py','validate.py','massbalance_check.py','database_json.py']:
    p=SKILL/name;tool_inventory.append({'name':name,'sha256':sha(p)});shutil.copyfile(p,HERE/('audited_'+name))
save(HERE/'tool_inventory.json',tool_inventory)
for v in ['Base','M30','P30']:
    d=ROOT/f'regions/LME_027/models/Guenette2014_BancArguin_{v}_1991';e=d/'extracted_tables';m=load(e/'extraction.json');raw=e/'raw_converter';raw.mkdir(exist_ok=True)
    for f in files:shutil.copyfile(e/f,raw/f)
    (raw/'REPORT.md').write_text('# Raw stock conversion audit\n\n## Mass balance\nPending.\n',encoding='utf-8')
    for script,log,args in [('validate.py','VALIDATION.txt',[str(e)]),('massbalance_check.py','MASS_BALANCE_CHECK.txt',[str(e)]),('database_json.py','STOCK_CONVERTER_LOG.txt',['-d',str(raw),'--update-report'])]:
        p=subprocess.run([sys.executable,str(SKILL/script)]+args,capture_output=True,text=True,encoding='utf-8',env=env)
        (e/log).write_text(p.stdout+p.stderr,encoding='utf-8')
        print(v,script,'exit',p.returncode)
    rp=next(p for p in raw.glob('*.json') if p.name!='DIET_SOURCE_SUMS.json');data=load(rp);before=copy.deepcopy(data)
    src={}
    for f in files:
        src[f]=csvread(e/f) if f.endswith('.csv') else [list(r) for r in openpyxl.load_workbook(e/f,data_only=False).active.iter_rows(values_only=True)]
    basic={r[0]:r for r in src['Basic_input.csv'][1:]};land={r[0]:r for r in src['Landings.csv'][1:]};disc={r[0]:r for r in src['Discards.csv'][1:]};ba={r[0]:r for r in src['Biomass_accumulation.csv'][1:]};names={g['n']:g['name'] for g in m['groups']};derived=[]
    ledger=[]
    for g in data['group']:
        n=int(g['group_seq']);seq=str(n);r=basic[seq];s=m['groups'][n-1]
        for f,col in [('habitat_area',2),('biomass_habitat_area',3),('z',4),('pb',5),('qb',6),('ee',7),('other_mort',8),('ge',9),('gs',10),('detritus_import',11)]:g[f]=nd(r[col])
        g.update(biomass=nd(s['biomass']),vbk='-9999',shadow_price='-9999',ge_input='false' if s.get('pq') is None else 'true',pp='0' if n<=47 else ('1' if n<=50 else '2'),biomass_accum=nd(ba[seq][2]),biomass_accum_rate=nd(ba[seq][3]),tl=nd(s.get('tl')))
        g['landings_by_fleet']={f:nd(m['landings'][seq].get(f)) for f in m['fleets']};g['discards_by_fleet']={f:'-9999' for f in m['fleets']}
        g['export']=nd(land[seq][-1]);g['landings_total']=g['export'];g['discards_total']='-9999';g['total_removals']='-9999'
        g['export_scope']='published catch assigned to Landings; discards unreported; not asserted complete removals'
        g['detritus_fate_by_pool']={'51':'-9999'};g['detritus_export']='-9999'
        g['source_status']=s['source_status'];g['diet_imp']='-9999'
        if n<=47:
            g['diet_imp']=nd(m['diet'][seq]['import'])
            g['diet_descr']={'diet':[{'prey_seq':str(p),'proportion':nd(m['diet'][seq][str(p)]),'detritus_fate':'-9999'} for p in range(1,52)]}
        else:g['diet_descr']=None
        if s.get('ba_rate') is not None and s.get('biomass') is not None:derived.append({'group':n,'quantity':'absolute_BA','formula':'B*BA_rate','operands':[s['biomass'],s['ba_rate']],'result':str(D(s['biomass'])*D(s['ba_rate'])),'status':'derived_arithmetic_only; not written into source canonical field'})
        old=next(x for x in before['group'] if x['group_seq']==seq)
        for k in sorted(set(old)|set(g)):
            if old.get(k)!=g.get(k):ledger.append({'group':n,'field':k,'stock_converter_value':old.get(k),'source_preserving_value':g.get(k),'reason':'Restore exact published/inherited cell or explicit unknown and source scope; no numerical repair/normalization'})
    data.update(metadata=m['metadata'],extraction_metadata=m['metadata'],extraction_source_tables=src,extraction_notes=m['extraction_notes'],stanzas=m['stanzas'],extraction_adapter={'script':'../../../validation_reports/BancArguin_20261003/extraction/convert_and_verify.py','unknown_sentinel':'-9999','diet_normalized':False,'biomass_basis':'published density per full 33,224 km2 model area; habitat area unknown','source_ba_form':'rate; absolute field unknown; arithmetic retained separately','catch_scope':'reported catch assigned to landings, not complete removals','researcher_correction_evidence':None})
    save(d/'model.json',data);save(e/'canonical_database.json',data);save(e/'CONVERSION_RESTORATIONS.json',ledger);save(e/'DERIVED_ARITHMETIC.json',derived)
    # Numeric reconstruction from canonical JSON extension, with exact formatting in source ledgers.
    reopened=load(d/'model.json');wb=openpyxl.Workbook();wb.remove(wb.active)
    for name,rs in reopened['extraction_source_tables'].items():
        ws=wb.create_sheet(Path(name).stem)
        for rowi,row in enumerate(rs,1):
            vals=[]
            for coli,val in enumerate(row,1):
                if val is None or val=='':vals.append(None);continue
                numeric=(rowi>1 and coli>=3 and name!='Metadata.xlsx')
                if numeric:
                    try:val=float(D(str(val)))
                    except:pass
                vals.append(val)
            ws.append(vals)
        ws.freeze_panes='C2';ws.auto_filter.ref=ws.dimensions;ws.column_dimensions['A'].width=8;ws.column_dimensions['B'].width=32
        for cell in ws[1]:cell.font=openpyxl.styles.Font(bold=True)
    out=e/'canonical_reconstructed.xlsx';wb.save(out);rw=openpyxl.load_workbook(out,data_only=False)
    errors=[];checked=0;maxdiff=0
    for name,rs in src.items():
        got=[list(r) for r in rw[Path(name).stem].iter_rows(values_only=True)]
        if len(got)!=len(rs):errors.append([name,'row_count']);continue
        for ri,(er,ar) in enumerate(zip(rs,got),1):
            for ci,(expected,actual) in enumerate(zip(er,ar),1):
                checked+=1
                if expected is None or expected=='':ok=actual is None
                elif isinstance(actual,(int,float)) and ri>1 and ci>=3 and name!='Metadata.xlsx':
                    delta=abs(D(str(expected))-D(str(actual)));maxdiff=max(maxdiff,float(delta));ok=delta<=D('1e-12')
                else:ok=str(expected)==str(actual)
                if not ok:errors.append([name,ri,ci,expected,actual])
    # Check standard JSON fields, not merely the embedded tables.
    for g,s in zip(reopened['group'],m['groups']):
        assert g['group_seq']==str(s['n']) and g['group_name']==s['name']
        for jf,sf in [('biomass','biomass'),('pb','pb'),('qb','qb'),('ee','ee'),('z','z'),('ge','pq'),('tl','tl'),('biomass_accum_rate','ba_rate')]:
            if g[jf]!=nd(s.get(sf)):errors.append(['canonical_scalar',s['n'],jf,g[jf],s.get(sf)])
        if s['n']<=47:
            for cell in g['diet_descr']['diet']:
                if cell['proportion']!=nd(m['diet'][g['group_seq']][cell['prey_seq']]):errors.append(['canonical_diet',g['group_seq'],cell['prey_seq']])
    result={'variant':v,'source_to_import':'parameter and diet literals preserved; %/100 exact decimal; variant unknowns explicit','source_to_database_standard_fields_equal':not errors,'all_eight_embedded_tables_equal':reopened['extraction_source_tables']==src,'workbook_numeric_tolerance':'1e-12','workbook_maximum_absolute_difference':maxdiff,'cells_checked':checked,'errors':errors,'passed':not errors,'canonical_sha256':sha(d/'model.json'),'extraction_sha256':sha(e/'extraction.json'),'reconstructed_sha256':sha(out)}
    save(e/'ROUNDTRIP_CHECK.json',result);assert not errors,errors[:5]
    print(v,'canonical ready; checks',checked,'restorations',len(ledger))
