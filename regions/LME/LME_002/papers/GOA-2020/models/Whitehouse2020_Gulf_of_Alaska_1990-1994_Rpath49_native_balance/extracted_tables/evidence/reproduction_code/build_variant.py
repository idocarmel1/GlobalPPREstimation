"""Translate a reproduced native Rpath balance into a distinct Ecopath variant.

Known native input literals remain fixed. Native solved quantities and documented
runtime zero conventions are explicit derived inputs, never source observations.
"""
from pathlib import Path
import csv,hashlib,json,os,shutil,subprocess,sys
from decimal import Decimal
import openpyxl
sys.stdout.reconfigure(encoding='utf-8')
RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
PAPER=ROOT/'regions/LME/LME_002/papers/GOA-2020'
PARENT=PAPER/'models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49'
MID='Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance'
MODEL=PAPER/'models'/MID
NATIVE=RUN/'outputs/native_balance'
STAGE=RUN/'outputs/native_variant_stage'
SCRIPTS=ROOT/'tools/skills/paper-to-ppr/resources/extraction/scripts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f))
def missing(v):return v in (None,'','NA','NaN','-9999',-9999)
def num(v):return None if missing(v) else Decimal(str(v))
def close(a,b):
    a,b=num(a),num(b)
    return a is None and b is None or a is not None and b is not None and abs(a-b)<=max(Decimal('1e-12'),Decimal('1e-12')*max(abs(a),abs(b)))
parent_sha=sha(PARENT/'model.json')
assert parent_sha=='10dfbf57dcc9c1ca2e57460637709a061c9264a7e29bf17e0028fadf4c919125'
parent=read(PARENT/'model.json')
native_rows=rows(NATIVE/'groups.csv');native=[dict(zip(native_rows[0],r)) for r in native_rows[1:] if r]
assert len(native)==49 and [r['Group'] for r in native]==[g['group_name'] for g in parent['group']]
native_byname={r['Group']:r for r in native}
ledger=[];checks=[]
alias={'Urchins, dollars, cucumbers':'Urchins dollars cucumbers'}
fields={'biomass':('biomass','Biomass'),'pb':('pb','PB'),'qb':('qb','QB'),'ee':('ee','EE'),'pq':('ge','GE'),'unassim':('gs','Unassim'),'ba':('biomass_accum','BA'),'detritus_import':('detritus_import','DetInput'),'tl':('tl','TL')}
groups=[]
for g in parent['group']:
    n=int(g['group_seq']);r=native_byname[g['group_name']]
    out={'n':n,'name':alias.get(g['group_name'],g['group_name']),'parameter_roles':{}}
    assert int(float(r['Type']))==int(g['pp'])
    for writer_key,(canonical_key,native_key) in fields.items():
        source=g.get(canonical_key);runtime=r.get(native_key)
        if missing(runtime):
            assert missing(source),(n,canonical_key,source,runtime)
            out[writer_key]=None;role='native_output_unavailable'
        elif not missing(source):
            checks.append({'group_seq':n,'field':canonical_key,'known_source_preserved':close(source,runtime),'source':source,'native_output':runtime})
            assert close(source,runtime),(n,canonical_key,source,runtime)
            out[writer_key]=source;role='unchanged_native_input'
        else:
            out[writer_key]=runtime
            role='native_balance_solution' if canonical_key in ['biomass','ee','tl','ge'] else 'native_runtime_structural_zero'
            if role=='native_runtime_structural_zero':assert num(runtime)==0,(n,canonical_key,runtime)
        out['parameter_roles'][writer_key]=role
        ledger.append({'group_seq':n,'group_name':g['group_name'],'field':canonical_key,'source_literal':source,'native_output_literal':runtime,'variant_literal':out[writer_key],'role':role})
    groups.append(out)
consumers=[int(g['group_seq']) for g in parent['group'] if g['pp']=='0']
detseq=[int(g['group_seq']) for g in parent['group'] if g['pp']=='2']
dets=[parent['group'][i-1]['group_name'] for i in detseq]
fleet=list(parent['group'][0]['landings_by_fleet'])[0]
native_diet_rows=rows(NATIVE/'diet.csv')
diet_header=native_diet_rows[0]
native_diet={r[0]:dict(zip(diet_header[1:],r[1:])) for r in native_diet_rows[1:]}
native_fate_rows=rows(NATIVE/'detritus_fate.csv')
native_fate={r[0]:dict(zip(native_fate_rows[0][1:],r[1:])) for r in native_fate_rows[1:]}
diet={}
for g in parent['group']:
    n=int(g['group_seq'])
    if n not in consumers:continue
    cells={}
    for d in g['diet_descr']['diet']:
        prey=int(d['prey_seq']);preyname=parent['group'][prey-1]['group_name']
        native_value=native_diet[preyname][g['group_name']]
        target='0' if missing(d['proportion']) else d['proportion']
        assert close(target,native_value),(n,prey,target,native_value)
        cells[str(prey)]=target
        ledger.append({'group_seq':n,'group_name':g['group_name'],'field':'diet:'+str(prey),'source_literal':d['proportion'],'native_output_literal':native_value,'variant_literal':target,'role':'native_NA_diet_zero_convention' if missing(d['proportion']) else 'unchanged_native_input'})
    assert close(g['diet_imp'],native_diet['Import'][g['group_name']])
    cells['import']=g['diet_imp'];diet[str(n)]=cells
companions={}
for filename,item in parent['published_companions'].items():
    companions[filename]={'description':item.get('description','Retained exact parent source companion; not solved-state evidence.'),'rows':item['rows']}
companions['Native_balance_output.csv']={'description':'Actual pinned native Rpath output; numerical solutions and runtime conventions, not additional observations. Full native output and independent budgets are retained in evidence.','rows':native_rows}
lh=['group_seq','group_name','field','source_literal','native_output_literal','variant_literal','role']
companions['Native_completion_ledger.csv']={'description':'Source→native output→derived variant provenance, including NA-as-zero cells. Known input literals preserved.','rows':[lh]+[[str(r.get(k,'')) if r.get(k) is not None else '' for k in lh] for r in ledger]}
writer={'metadata':{**parent['metadata'],'model_number':MID},'groups':groups,'consumers':consumers,'fleets':[fleet],'detritus_groups':dets,'diet_rows':49,'landings_rows':49,'discards_rows':49,'diet':diet,'landings':{},'discards':{},'detritus_fate':{},'companions':companions,'extraction_notes':['Distinct computational variant of official Rpath49 parameters, completed by the pinned native Rpath balance.','Parent source missingness remains unchanged in its own canonical package and raw companions.','No parameter fitting, diet normalization, BA repair or PPR result adoption. Native NA diet→0, DetInput NA→0 and nonfeeding QB0 are documented native conventions.']}
for g in parent['group']:
    n=int(g['group_seq']);r=native_byname[g['group_name']]
    writer['landings'][str(n)]=g['landings_by_fleet'];writer['discards'][str(n)]=g['discards_by_fleet']
    assert close(sum(num(v) for v in g['landings_by_fleet'].values()),r['Landings'])
    assert close(sum(num(v) for v in g['discards_by_fleet'].values()),r['Discards'])
    assert close(g['export'],r['Catch'])
    writer['detritus_fate'][str(n)]={parent['group'][int(k)-1]['group_name']:v for k,v in g['detritus_fate_by_pool'].items()}
    for pool,value in writer['detritus_fate'][str(n)].items():assert close(value,native_fate[g['group_name']][pool]),(n,pool,value,native_fate[g['group_name']][pool])
inp=RUN/'outputs/native_variant_writer_input.json';dump(inp,writer)
tool_receipts=[]
def run(script,args):
    proc=subprocess.run([sys.executable,str(SCRIPTS/script),*map(str,args)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONIOENCODING':'utf-8'})
    log=RUN/'qa'/('variant_'+script.removesuffix('.py')+'.log');log.write_text(proc.stdout+'\nSTDERR\n'+proc.stderr,encoding='utf-8')
    tool_receipts.append({'script':str((SCRIPTS/script).relative_to(ROOT)).replace('\\','/'),'sha256':sha(SCRIPTS/script),'returncode':proc.returncode,'log':log.name})
    print(script,proc.returncode,flush=True)
    return proc
p=run('write_outputs.py',[inp,'--outdir',STAGE.parent,'--dir-name',STAGE.name]);assert p.returncode==0,p.stdout+p.stderr
p=run('validate.py',[STAGE])
p=run('database_json.py',['-d',STAGE]);assert p.returncode==0,p.stdout+p.stderr
candidates=[p for p in STAGE.glob('*.json') if p.name not in ['model.json','DIET_SOURCE_SUMS.json','SOURCE_FIDELITY_CHECK.json']]
assert len(candidates)==1,candidates
canonical=read(candidates[0])
for g in canonical['group']:
    n=int(g['group_seq']);g['group_name']=parent['group'][n-1]['group_name']
    if g['pp']!='0':g['diet_imp']='0'
for entry in canonical.get('source_fidelity',{}).get('diet_sums',[]):entry['consumer_name']=parent['group'][int(entry['consumer_seq'])-1]['group_name']
MODEL.mkdir(parents=True,exist_ok=True)
target=MODEL/'model.json'
if target.exists():assert sha(target)==hashlib.sha256((json.dumps(canonical,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')).hexdigest(),'Existing differing variant requires reconciliation'
dump(target,canonical)
tables=MODEL/'extracted_tables';tables.mkdir(exist_ok=True)
ev=tables/'evidence';ev.mkdir(exist_ok=True)
for filename in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx']:shutil.copy2(STAGE/filename,tables/filename)
shutil.copytree(STAGE/'companions',tables/'companions',dirs_exist_ok=True)
if (PARENT/'extracted_tables/Taxonomy.xlsx').exists():shutil.copy2(PARENT/'extracted_tables/Taxonomy.xlsx',tables/'Taxonomy.xlsx')
if (PARENT/'MODEL_PROFILE.md').exists():shutil.copy2(PARENT/'MODEL_PROFILE.md',MODEL/'MODEL_PROFILE.md')
for name in ['SOURCE_FIDELITY_CHECK.json','DIET_SOURCE_SUMS.json','MASS_BALANCE.md','ewe_conversion.log']:
    if (STAGE/name).exists():shutil.copy2(STAGE/name,ev/name)
for item in tool_receipts:shutil.copy2(RUN/'qa'/item['log'],ev/item['log'])
receipt={'parent_model_sha256':parent_sha,'variant_model_sha256':sha(target),'variant_id':MID,'source_known_scalar_checks':checks,'known_values_preserved':all(x['known_source_preserved'] for x in checks),'tools':tool_receipts,'native_output_hashes':{p.name:sha(p) for p in NATIVE.iterdir() if p.is_file()},'source_unchanged':sha(PARENT/'model.json')==parent_sha}
dump(RUN/'qa/variant_conversion.json',receipt);dump(ev/'variant_conversion.json',receipt)
dump(RUN/'qa/native_to_variant_ledger.json',ledger);dump(ev/'native_to_variant_ledger.json',ledger)
fidelity=read(ev/'SOURCE_FIDELITY_CHECK.json');assert not fidelity['errors'] and fidelity['numeric_value_and_missing_mask_match']
notes='''# Gulf of Alaska Rpath49 — native balance computational variant

## Source identity

Whitehouse & Aydin (2020), DOI10.1016/j.ecolmodel.2020.109074. Derived from the official NOAA-EDAB/Rpath Ecosense.GOA inputs at commit fe63f6d370d942ff1786f4d649e432fbfb85f81b. The [unaltered parameter extraction](../Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49/model_notes.md) remains a separate model. This variant is the authorized native-equation completion, not another measured model.

## Modeled period and area

Inherited 1990–1994 Gulf of Alaska shelf/slope baseline, 291,840 km². Nearshore waters below50m are excluded in the original model; complete LME overlap has not been measured. The2020publication is not a2020ecosystem baseline.

## Departures from the publication

The native Rpath implementation solves previously unknown EE, detritus biomass and TL and calculates GE. Its explicit NA-diet→0 and DetInput-NA→0 conventions and nonfeeding QB0 placeholders are represented here. Known input values, BA, catch, group identities and fate fractions are preserved; no diet normalization, parameter tuning or balancing repair was applied. Standard import group31 uses its reversible comma-free alias; canonical group names are exact native names. Original raw inputs and unknown masks remain in the parent package and retained companions.

Native balance and PPR construction are separate stages. PPR diagnostics and their source→runtime ledger are retained under results/diagnostics/. Native EE values are solved values; all original source EE values were unknown. The project EE-floor eligibility check must retain that missing-source provenance, rather than treat solved values as observations. Known detritus BA0 must not be replaced to conceal native-to-PPR accounting residuals.

Primary production combines local and Outside production, and the detritus pools also combine external/returned sources. An inner or PP result from this aggregate cannot independently identify geographically local production. Catch matching, modern-year extrapolation and annual regionalPPR/NPP are not part of this run. No map update or researcher approval is implied.

## Evidence links

- [Native completion ledger](extracted_tables/evidence/native_to_variant_ledger.json)
- [Conversion and preserved-input checks](extracted_tables/evidence/variant_conversion.json)
- [Derived-table round trip](extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json)
- [Diagnostic results and evidence](results/diagnostics/)
'''
(MODEL/'model_notes.md').write_text(notes,encoding='utf-8')
print(json.dumps({'model_path':str(target.relative_to(ROOT)).replace('\\','/'),'sha256':sha(target),'groups':len(canonical['group']),'fidelity':fidelity,'known_source_checks':len(checks)},indent=2))
