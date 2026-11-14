"""Independent source arithmetic and R-output audit; never tunes or solves PPR."""
from pathlib import Path
import argparse, csv, hashlib, json, math, sys
from datetime import datetime, timezone
import numpy as np

RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').is_file())
PARENT=ROOT/'regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49'
NATIVE=PARENT/'inputs/native'
VARIANT=PARENT.parent/'Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance'
SOURCE_SHA='10dfbf57dcc9c1ca2e57460637709a061c9264a7e29bf17e0028fadf4c919125'
ATOL=1e-12
RTOL=1e-12
BUDGET_ATOL=1e-10

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def records(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def number(v):
    if v is None or str(v).strip() in ('','NA','NaN','nan','-9999'):return np.nan
    return float(v)
def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(np.integer,)):return int(x)
    if isinstance(x,(np.bool_,)):return bool(x)
    if isinstance(x,(float,np.floating)) and not math.isfinite(x):return None
    return x

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--native-output',type=Path,default=RUN/'outputs/native_balance');ap.add_argument('--variant',type=Path,default=VARIANT);args=ap.parse_args()
    out=args.native_output
    checks={};failures=[];observed={}
    def check(kind,key,expected,actual,atol=ATOL):
        checks[kind]=checks.get(kind,0)+1
        if isinstance(expected,(str,bool)):
            ok=expected==actual
        else:
            expected=float(expected);actual=number(actual)
            ok=(math.isnan(expected) and math.isnan(actual)) or bool(np.isclose(expected,actual,atol=atol,rtol=RTOL,equal_nan=False))
        if not ok:failures.append({'category':kind,'key':key,'expected':clean(expected),'actual':clean(actual),'atol':atol,'rtol':RTOL})
    files=[NATIVE/'Ecosense_GOA_base.csv',NATIVE/'Ecosense_GOA_diet.csv',PARENT/'model.json']+[out/x for x in ['groups.csv','groups_with_fleet.csv','diet.csv','detritus_fate.csv','detritus_fate_with_fleet.csv','landings.csv','discards.csv']]
    for p in files:
        if not p.is_file():raise FileNotFoundError(f'Await required source/native output: {p}')
        observed[p.relative_to(ROOT).as_posix()]=sha(p)
    check('source_identity','parent canonical SHA256',SOURCE_SHA,sha(PARENT/'model.json'))
    source=records(NATIVE/'Ecosense_GOA_base.csv')
    real=[r for r in source if number(r['Type'])<3]
    living=[r for r in source if number(r['Type'])<2]
    det=[r for r in source if number(r['Type'])==2]
    fleet=[r for r in source if number(r['Type'])==3]
    names=[r['Group'] for r in real];lnames=[r['Group'] for r in living];dnames=[r['Group'] for r in det];allnames=[r['Group'] for r in source]
    source_by={r['Group']:r for r in source}
    check('source_structure','all49 raw EE cells unknown',49,sum(np.isnan(number(r['EE'])) for r in real))
    native=records(out/'groups.csv');native_by={r['Group']:r for r in native}
    fleet_native=records(out/'groups_with_fleet.csv');fleet_by={r['Group']:r for r in fleet_native}
    check('identity','49 real groups',49,len(native));check('identity','unique real names',49,len(native_by));check('identity','exact source order',json.dumps(names),json.dumps([r['Group'] for r in native]));check('identity','50 rows including fleet',50,len(fleet_native))
    field_map={'Type':'Type','Biomass':'Biomass','PB':'PB','QB':'QB','BioAcc':'BA','Unassim':'Unassim','DetInput':'DetInput','F_Fishery':'Landings','D_Fishery':'Discards'}
    for r in real:
        got=native_by[r['Group']]
        for a,b in field_map.items():
            value=number(r[a])
            if np.isfinite(value):check('source_known_scalar',r['Group']+'/'+a,value,got[b])
            elif a in ['QB','DetInput']:check('native_structural_zero',r['Group']+'/'+a,0,got[b])
        check('source_catch',r['Group'],number(r['F_Fishery'])+number(r['D_Fishery']),got['Catch'])
    diet_src=records(NATIVE/'Ecosense_GOA_diet.csv');diet_src_by={r['DIETS']:r for r in diet_src}
    diet_out=records(out/'diet.csv');diet_out_by={r['Prey']:r for r in diet_out}
    check('identity','diet prey labels',json.dumps(names+['Import']),json.dumps([r['Prey'] for r in diet_out]))
    dc=np.zeros((49,47));imports=np.zeros(47)
    blank_diets=0
    for i,prey in enumerate(names+['Import']):
        for j,predator in enumerate(lnames):
            value=number(diet_src_by[prey][predator]);blank_diets+=int(np.isnan(value));expected=0 if np.isnan(value) else value
            check('native_diet_NA_zero',prey+' -> '+predator,expected,diet_out_by[prey][predator])
            if i<49:dc[i,j]=expected
            else:imports[j]=expected
    fate_out=records(out/'detritus_fate.csv');fate_by={r['Group']:r for r in fate_out}
    fate_fleet=records(out/'detritus_fate_with_fleet.csv');fate_fleet_by={r['Group']:r for r in fate_fleet}
    check('identity','fate real names',json.dumps(names),json.dumps([r['Group'] for r in fate_out]))
    fate=np.array([[number(r['PelDetFate']),number(r['BenthDetFate'])] for r in source])
    for i,name in enumerate(allnames):
        for j,pool in enumerate(dnames):
            check('native_fate',name+' -> '+pool,fate[i,j],fate_fleet_by[name][pool])
            if i<49:check('native_fate_real',name+' -> '+pool,fate[i,j],fate_by[name][pool])
    land_src=np.array([number(r['F_Fishery']) if np.isfinite(number(r['F_Fishery'])) else 0 for r in source])
    disc_src=np.array([number(r['D_Fishery']) if np.isfinite(number(r['D_Fishery'])) else 0 for r in source])
    for name,field,values in [('landings.csv','F_Fishery',land_src),('discards.csv','D_Fishery',disc_src)]:
        rr=records(out/name);by={r['Group']:r for r in rr};cols=[c for c in rr[0] if c!='Group'];check('identity',name+' fleet count',1,len(cols))
        for i,g in enumerate(allnames):check('native_fishery_matrix',name+'/'+g,values[i],by[g][cols[0]])
    B=np.array([number(r['Biomass']) for r in living]);PB=np.array([number(r['PB']) for r in living]);QB=np.array([number(r['QB']) if np.isfinite(number(r['QB'])) else 0 for r in living]);BA=np.array([number(r['BioAcc']) for r in living]);GS=np.array([number(r['Unassim']) for r in living])
    P=B*PB;Q=B*QB;predation=dc[:47,:]@Q;catch=land_src[:47]+disc_src[:47];rhs=predation+catch+BA;EE=rhs/P
    A=np.diag(P);rank=int(np.linalg.matrix_rank(A));check('rank','living source system',47,rank)
    equation_rows=[]
    for i,name in enumerate(lnames):
        got=native_by[name];check('independent_living_EE',name,EE[i],got['EE']);residual=P[i]*number(got['EE'])-rhs[i];check('living_budget_residual',name,0,residual,BUDGET_ATOL)
        equation_rows.append({'group':name,'production':P[i],'predation':predation[i],'catch':catch[i],'BA':BA[i],'independent_EE':EE[i],'native_EE':number(got['EE']),'residual':residual})
    M0=P*(1-EE);egestion=Q*GS
    det_input=np.array([number(r['DetInput']) if np.isfinite(number(r['DetInput'])) else 0 for r in source])
    check('source_structure','all DetInput structural/default zeros',0,float(np.max(np.abs(det_input))))
    natural=(M0+egestion)@fate[:47,:];discard_returns=disc_src.sum()*fate[-1,:];first_inflow=natural+discard_returns+det_input.sum();det_demand=dc[47:49,:]@Q;unused=np.maximum(first_inflow-det_demand,0);cross_returns=unused@fate[47:49,:];inflow=first_inflow+cross_returns
    det_rows=[]
    for j,name in enumerate(dnames):
        source_pb=number(source_by[name]['PB']);expected_b=inflow[j]/source_pb;expected_ee=det_demand[j]/inflow[j];got=native_by[name]
        check('independent_DET_B',name,expected_b,got['Biomass'],BUDGET_ATOL);check('independent_DET_EE',name,expected_ee,got['EE']);check('independent_DET_turnover',name,source_pb,got['PB']);check('DET_production_inflow',name,inflow[j],number(got['Biomass'])*number(got['PB']),BUDGET_ATOL)
        det_rows.append({'group':name,'natural_M0_and_egestion_input':natural[j],'fishery_discard_input':discard_returns[j],'inter_detritus_transfer':cross_returns[j],'total_inflow':inflow[j],'consumer_demand':det_demand[j],'independent_EE':expected_ee,'independent_B':expected_b,'source_PB':source_pb})
    # Independent TL equation includes one native fleet; imports are explicitly zero.
    dietplus=np.zeros((50,50));dietplus[:49,:47]=dc/(1-imports)[None,:];totcatch=land_src+disc_src;dietplus[:,49]=totcatch/totcatch.sum();tl_A=np.eye(50)-dietplus.T;tl=np.linalg.solve(tl_A,np.ones(50))
    for i,name in enumerate(allnames):check('independent_trophic_level',name,tl[i],fleet_by[name]['TL'])
    for r in real:
        g=native_by[r['Group']];expected_ge=number(g['PB'])/number(g['QB']) if number(g['QB']) else 0;check('native_GE',r['Group'],expected_ge,g['GE'])
    variant_status='not_present_yet';variant_hash=None;table_checks={}
    variant=args.variant/'model.json'
    if variant.is_file():
        variant_status='reviewed';variant_hash=sha(variant);v=load(variant);vg=v['group'];by={g['group_name']:g for g in vg};check('variant_identity','real group count',49,len(vg));check('variant_identity','name order',json.dumps(names),json.dumps([g['group_name'] for g in vg]))
        field_map={'Biomass':'biomass','PB':'pb','QB':'qb','EE':'ee','GE':'ge','TL':'tl','BA':'biomass_accum','Unassim':'gs','DetInput':'detritus_import','Landings':'landings_total','Discards':'discards_total','Catch':'export'}
        for i,name in enumerate(names):
            g=by[name];check('variant_identity',name+' sequence',i+1,g['group_seq'])
            for native_field,canonical_field in field_map.items():check('variant_scalar',name+'/'+canonical_field,number(native_by[name][native_field]),g.get(canonical_field),BUDGET_ATOL if canonical_field=='biomass' else ATOL)
            if i<46:
                dd={int(x['prey_seq']):x['proportion'] for x in (g.get('diet_descr') or {}).get('diet',[])}
                for prey in range(49):check('variant_diet',names[prey]+' -> '+name,dc[prey,i],dd.get(prey+1))
            if i<47:
                check('variant_import',name,imports[i],g.get('diet_imp'))
            for j in range(2):check('variant_fate',name+' -> '+dnames[j],fate[i,j],g.get('detritus_fate_by_pool',{}).get(str(48+j)))
        tables=args.variant/'extracted_tables'
        for table in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx']:
            path=tables/table;table_checks[table]={'present':path.is_file(),'sha256':sha(path) if path.is_file() else None}
        if all(x['present'] for x in table_checks.values()):
            basic=records(tables/'Basic_input.csv');basic_by={int(r['']):r for r in basic if r[''].isdigit()}
            base_cols={'Biomass':'Biomass in habitat area (t/km^2)','PB':'Production / biomass (/year)','QB':'Consumption / biomass (/year)','EE':'Ecotrophic Efficiency','GE':'Production / consumption','Unassim':'Unassim. consumption','DetInput':'Detritus import (t/km^2/year)'}
            for i,name in enumerate(names,1):
                check('variant_import_label',name,' '.join(name.replace(',','').split()),basic_by[i]['Group name'])
                for native_field,column in base_cols.items():check('variant_import_basic',name+'/'+native_field,number(native_by[name][native_field]),basic_by[i][column],BUDGET_ATOL if native_field=='Biomass' else ATOL)
            for filename,native_field in [('Landings.csv','Landings'),('Discards.csv','Discards')]:
                rr=records(tables/filename)
                for row in rr:
                    if not row[''].isdigit():continue
                    i=int(row[''])-1;check('variant_import_catch',filename+'/'+names[i],number(native_by[names[i]][native_field]),row['Total']);check('variant_import_catch',filename+'/'+names[i]+'/fleet',number(native_by[names[i]][native_field]),row['Fishery/Subsistence'])
            for row in records(tables/'Biomass_accumulation.csv'):
                if row[''].isdigit():
                    i=int(row[''])-1;check('variant_import_BA',names[i],number(native_by[names[i]]['BA']),row['Biomass accumulation (t/km^2/year)'])
            for row in records(tables/'Detritus_fate.csv'):
                if row[''].isdigit():
                    i=int(row[''])-1
                    for j,pool in enumerate(dnames):check('variant_import_fate',names[i]+' -> '+pool,fate[i,j],row[pool])
            for row in records(tables/'Diet_composition.csv'):
                if row[''].isdigit():
                    i=int(row[''])-1
                    for j in range(46):check('variant_import_diet',names[i]+' -> '+lnames[j],dc[i,j],row[str(j+1)])
                elif row.get('Source / fate')=='Import':
                    for j in range(46):check('variant_import_diet_import',lnames[j],imports[j],row[str(j+1)])
            import openpyxl
            wb=openpyxl.load_workbook(tables/'TL.xlsx',read_only=True,data_only=True)
            for row in list(wb.active.iter_rows(values_only=True))[1:]:
                if row[0] is not None:
                    i=int(row[0])-1;check('variant_import_TL',names[i],number(native_by[names[i]]['TL']),row[2])
            wb.close()
            wb=openpyxl.load_workbook(tables/'Metadata.xlsx',read_only=True,data_only=True);metadata={row[0]:row[1] for row in wb.active.iter_rows(values_only=True) if row[0]};wb.close();check('variant_import_metadata','model period','1990-1994',str(metadata.get('model_year')))
        receipts=list((tables/'evidence').glob('SOURCE_FIDELITY_CHECK.json'))
        if receipts:
            fidelity=load(receipts[0]);check('variant_roundtrip','numeric values and missing masks',True,fidelity.get('numeric_value_and_missing_mask_match',fidelity.get('exact_value_and_missing_mask_match')));check('variant_roundtrip','no converter errors',0,len(fidelity.get('errors',[])))
            table_checks['source_fidelity']=fidelity
    check('source_identity','parent canonical remains unchanged',SOURCE_SHA,sha(PARENT/'model.json'))
    for path,before in observed.items():check('input_stability',path,before,sha(ROOT/path))
    report={'schema_version':1,'reviewed_at':datetime.now(timezone.utc).isoformat(),'review_scope':'Independent Python arithmetic from native source tables, comparing actual Rpath outputs; no PPR solve, tuning, or source changes. Variant checks only if persisted variant exists.','result':'pass_no_material_mismatches' if not failures else 'mismatches_found','checks':checks,'failures':failures,'tolerances':{'scalar_atol':ATOL,'rtol':RTOL,'flow_and_DET_B_atol':BUDGET_ATOL},'native_source_hashes_and_outputs':observed,'native_groups':49,'living_groups':47,'consumers':46,'detritus_groups':2,'native_blank_diet_cells_mapped_to_zero':blank_diets,'living_equation':'B*PB*EE = source-diet predation + landings + discards + BA','living_matrix_rank':rank,'living_matrix_condition_number':float(np.linalg.cond(A)),'living_budget_rows':equation_rows,'detritus_rows':det_rows,'TL_matrix_rank':int(np.linalg.matrix_rank(tl_A)),'TL_matrix_condition_number':float(np.linalg.cond(tl_A)),'source_consumer_diet_sums':{lnames[i]:float(dc[:,i].sum()+imports[i]) for i in range(46)},'admissibility':{'living_EE_min':float(EE.min()),'living_EE_max':float(EE.max()),'living_EE_outside_0_1':[lnames[i] for i,x in enumerate(EE) if not 0<=x<=1],'detritus_EE':(det_demand/inflow).tolist(),'finite_nonnegative_B':bool(all(number(r['Biomass'])>=0 and np.isfinite(number(r['Biomass'])) for r in native))},'variant_status':variant_status,'variant_sha256':variant_hash,'variant_tables':table_checks,'limits':['Fidelity/equation verification does not establish geographic applicability, local-versus-external production attribution, catch mapping, or scientific PPR diagnostic eligibility.','All 49 original EE values are unreported; computed EE values must not be reclassified as source-reported observations in downstream floor eligibility.','Native fleet detritus fate fractions are retained at their printed values; their tiny residual below one is not renormalized.']}
    dest=RUN/'qa/independent_native_variant_review.json'
    report['checker_sha256']=sha(Path(__file__))
    report['units']={'biomass':'t wet weight/km2','production_consumption_catch_BA_detritus_flows':'t wet weight/km2/year','PB_QB':'year^-1','EE_GE_GS_TL':'dimensionless'}
    if dest.exists():
        previous=load(dest)
        if previous.get('variant_status')=='not_present_yet':
            report['native_only_review']={k:previous[k] for k in ['reviewed_at','result','checks','failures','native_source_hashes_and_outputs','admissibility','variant_status']}
        elif previous.get('native_only_review'):
            report['native_only_review']=previous['native_only_review']
    dest.write_text(json.dumps(clean(report),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'result':report['result'],'checks':sum(checks.values()),'failures':len(failures),'variant_status':variant_status,'living_EE_range':[float(EE.min()),float(EE.max())],'detritus':clean(det_rows),'receipt':dest.relative_to(ROOT).as_posix()},ensure_ascii=False,indent=2))
    return 1 if failures else 0

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');raise SystemExit(main())
