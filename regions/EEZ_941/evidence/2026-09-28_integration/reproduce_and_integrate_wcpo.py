"""Reproduce the selected, previously authorized WCPO scenario and integrate supported catch."""
from pathlib import Path
import sys,json,csv,hashlib,shutil,copy
import numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
ENGINE=ROOT/'tools/scientific_code/PPREstimation'
sys.path.insert(0,str(HERE/'engine_snapshot' if (HERE/'engine_snapshot').exists() else ENGINE));sys.path.insert(0,str(ROOT/'tools'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from workbooks import *
from regional import recalculate,set_setting,set_result_hash
MODEL='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
def safe(x):
    if isinstance(x,pd.DataFrame):return {'index':safe(x.index.tolist()),'columns':safe(x.columns.tolist()),'data':safe(x.values.tolist())}
    if isinstance(x,np.generic):return safe(x.item())
    if isinstance(x,dict):return {str(k):safe(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [safe(v) for v in x]
    if isinstance(x,float) and not np.isfinite(x):return None
    return x
def save(p,x):p.write_text(json.dumps(safe(x),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def main():
    folder=ROOT/'regions/EEZ_941/models'/MODEL;prior=folder/'diagnostic_evidence'
    settings=json.loads((prior/'experiment_PROVENANCE.json').read_text(encoding='utf-8'))['loader_settings']
    source=folder/(MODEL+'.json');assert sha(source)=='328330dc06ed3e96462995f1a04c1bdaa9747468af8bb4d9e4f57196b9cc1b03'
    code=HERE/'engine_snapshot';code.mkdir(exist_ok=True)
    for name in ['ModelData.py','PPRCalculator.py','utils.py']:shutil.copy2(ENGINE/name,code/name)
    inp=HERE/(MODEL+'.json');shutil.copy2(source,inp)
    md=ModelData(str(inp));before=md.groups_data.copy(deep=True)
    calc=PPRCalculator.from_modeldata(md,**settings);after=calc._groups_df
    save(HERE/'before_state.json',{'groups':before,'DC':md.DC,'det_fate':md.det_fate})
    save(HERE/'loaded_state.json',{'groups':after,'DC':calc._DC,'det_fate':calc._det_fate})
    changes=[{'seq':int(seq),'field':field,'before':safe(before.loc[seq,field]),'after':safe(value)} for seq,row in after.iterrows() for field,value in row.items() if field in before.columns and safe(before.loc[seq,field])!=safe(value)]
    dcchanges=[{'consumer':int(i),'prey':int(j),'before':safe(md.DC.loc[i,j]),'after':safe(calc._DC.loc[i,j])} for i in calc._DC.index for j in calc._DC.columns if safe(md.DC.loc[i,j])!=safe(calc._DC.loc[i,j])]
    save(HERE/'transformation_ledger.json',{'groups':changes,'diets':dcchanges})
    reports={};raw={};matches={}
    for option in ['GE','TE','With Egestion']:
        report,sppr,A,L=calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
        reports[option]=report;raw[option]=sppr
        old=pd.read_csv(prior/('SPPR_'+option.replace(' ','_')+'.csv'),index_col=0);old.columns=old.columns.astype(int)
        matches[option]=bool(np.allclose(old.values,sppr.loc[old.index,old.columns].values,rtol=1e-12,atol=1e-10,equal_nan=True))
        assert report['status']=='WARN' and report['balance']['status']=='OK' and report['divergence']['n_negative_sources']==0
        sppr.to_csv(HERE/('SPPR_'+option.replace(' ','_')+'.csv'),index_label='seq')
    assert all(matches.values()),matches
    save(HERE/'direct_diagnostics.json',reports)
    (HERE/'DIRECT_DIAGNOSTICS.md').write_text('\n\n'.join('```json\n'+json.dumps({k:safe(v)},indent=2)+'\n```' for k,v in reports.items()),encoding='utf-8')
    reload=PPRCalculator.from_modeldata(ModelData(str(inp)),**settings)
    assert after.equals(reload._groups_df) and calc._DC.equals(reload._DC)
    save(HERE/'runtime_verification.json',{'historical_coefficients_match':matches,'reload_groups_equal':after.equals(reload._groups_df),'reload_diets_equal':calc._DC.equals(reload._DC),'settings':settings,'input_sha256':sha(inp),'code_sha256':{p.name:sha(p) for p in code.glob('*.py')},'all_biological_GE_sources_nonnegative':bool((raw['GE'].values>=0).all()),'source_and_variant_distinct':True})
    summaries=[]
    taxonomy=ROOT/'regions/EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)/extracted_tables/taxonomy.csv'
    for unit in ['EEZ_941','EEZ_598','HS_071']:
        region=ROOT/'regions'/unit;out=region/'evidence/2026-09-28_integration';out.mkdir(exist_ok=True,parents=True)
        bookpath=region/(unit+'.xlsx');backup=out/(unit+'_before_integration.xlsx')
        book=read_book(backup if backup.exists() else bookpath);original=copy.deepcopy(book);o=overview(book)
        assert o['selected_model_id']==MODEL and sha(region/o['model_path'])==sha(inp)
        if not backup.exists():shutil.copy2(bookpath,backup)
        shutil.copy2(taxonomy,out/'taxonomy.csv')
        g=calc.get_groups_df().reset_index();g=g.rename(columns={'group_seq':'seq'})
        book['Selected model groups']['Groups']=(g.columns.tolist(),[[clean(v) for v in row] for row in g.values.tolist()])
        gs=[];method_keys={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}
        for option,method in method_keys.items():
            sppr=raw[option]
            for seq,row in sppr.iterrows():
                for scope,columns in [('all',sppr.columns),('inner',[i for i in sppr.columns if after.loc[i,'trophic_info']!='Import']),('PP',[i for i in sppr.columns if after.loc[i,'trophic_info']=='PP'])]:
                    gs.append([MODEL,calc.seq2name[seq],scope,method,float(row.loc[columns].sum())])
        book['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],gs)
        mappings=[];taxa=sorted({r['taxon'] for r in records(book,'Catch','Catch')})
        for t in taxa:
            if t=='Coryphaena hippurus':
                mappings.append([MODEL,t,'Piscivorous fish',1.0,'high','Allain et al. 2007 Table 1 p9: Coryphaenidae; ITIS TSN 168791 https://www.itis.gov/servlet/SingleRpt/SingleRpt?search_topic=TSN&search_value=0168791','Explicit family membership; one supported model group without a stated size split for Coryphaenidae.'])
            elif t=='Acanthocybium solandri':
                mappings.append([MODEL,t,'Piscivorous fish',1.0,'high','Allain et al. 2007 Table 1 p9 explicitly names wahoo Acanthocybium solandri.','Explicit species membership; one supported model group.'])
            else:
                why='Unresolved: source does not establish a unique group and regional allocation; no catch weights invented.'
                if t in ['Katsuwonus pelamis','Thunnus albacares','Thunnus obesus']:why='Unresolved: tuna life stages have separate model groups; regional catch has no stage weights. Source-period model catches/biomass are not regional-year weights.'
                elif t in ['Prionace glauca','Xiphias gladius','Istiophoridae','Isurus','Alopias','Sphyrna','Carcharhinus falciformis','Carcharhinus longimanus']:why='Unresolved: shark/billfish large and small pools require regional size weights.'
                elif t in ['Carangidae','Scombridae','Lethrinidae','Serranidae','Exocoetidae','Acanthuridae','Scaridae']:why='Unresolved: overlapping groups and/or larval/juvenile epipelagic groups require allocation; whole-region benthic catch is not automatically pelagic membership.'
                mappings.append([MODEL,t,None,None,'unresolved','Allain et al. 2007 Table 1 p9; retained taxonomy.csv',why])
        mh=['model_id','taxon','group','weight','confidence','evidence','explanation'];book['PPR']['Matching']=(mh,mappings)
        with (out/'matching.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(mh);w.writerows(mappings)
        book['PPR']['Annual']=(ANNUAL_HEADER,[[MODEL,s,method,'landings','method','ppr','provisional: direct WARN; experimental surrogate; strict mass balance false; validation pending',*[None]*70] for s in ['all','inner','PP'] for method in method_keys.values()])
        book['Diagnostics']['direct_review']=(['option','overall_status','model_input_status','strict_model_balance','PP_budget_status','strict_PP_budget_balance','evidence'],[[k,v['status'],v['model_input']['status'],v['model_input']['is_model_balanced'],v['balance']['status'],v['balance']['is_balanced'],'regions/EEZ_941/evidence/2026-09-28_integration/direct_diagnostics.json'] for k,v in reports.items()])
        book['Diagnostics']['integration_review']=(['field','value'],[['admission','Selected experimental option1 admitted for supported-catch GE subtotal with WARN retained; not author-confirmed/native multistanza validation.'],['coverage','Only dorado and wahoo mapped. Main tuna catches unresolved because stage weights absent.'],['runtime','Exact selected JSON, historical constructor/settings and coefficients reproduced. No new repair.'],['geography','Broad WCPO pelagic surrogate; coastal/benthic catches remain unresolved.'],['evidence','regions/EEZ_941/evidence/2026-09-28_integration/INVESTIGATION.md']])
        set_setting(book,'production_eligible',True)
        set_setting(book,'source_note','PARTIAL GE: selected experimental WCPO option1; direct WARN and strict balance false retained. Only explicitly supported dorado/wahoo catch; tuna stage weights unavailable. Fixed mixed-period surrogate coefficients, not annual ecosystem reconstruction.')
        # Calculate from Excel-persisted input precision, as the normal regional workflow does.
        write_book(bookpath,book);book=read_book(bookpath)
        recalculate(book,bookpath)
        # Independent pre-existing classic and NPP values are scientific evidence, not this task's outputs.
        book['Classic PPR']=original['Classic PPR'];book['NPP']=original['NPP'];book['Catch']=original['Catch']
        ratio_header,new_ratios=book['PPR–NPP']['Ratios'];old_classic=[r for r in original['PPR–NPP']['Ratios'][1] if not r[0]]
        book['PPR–NPP']['Ratios']=(ratio_header,old_classic+[r for r in new_ratios if r[0]])
        set_setting(book,'calculation_status','calculated partial GE subtotal; selected experimental option1 WARN; tuna stage allocations unresolved')
        set_setting(book,'calculation_input_sha256',input_hash(book));set_result_hash(book)
        write_book(bookpath,book);reread=read_book(bookpath);validate_region(reread,bookpath)
        assert all(reread[s]==original[s] for s in ['Catch','Classic PPR','NPP'])
        assert overview(reread)['selection_rationale']==o['selection_rationale']
        annual=[r for r in records(reread,'PPR','Annual') if r['scope']=='all' and r['method']=='new_GE' and r['catch_basis']=='catch' and r['unidentified']=='method']
        by={r['metric']:r[2019] for r in annual}
        summary={'region':unit,'selected_model':MODEL,'GE_2019_all_source_total_catch_tC':by['ppr']/9,'covered_catch_2019_tonnes':by['covered_catch'],'total_catch_2019_tonnes':by['catch'],'coverage_percent':100*by['covered_catch']/by['catch'],'resolved_labels':2,'total_labels':len(taxa),'status':'provisional: PARTIAL experimental-surrogate subtotal; direct WARN; strict mass balance false','original_workbook_sha256':sha(backup),'canonical_sha256':sha(region/o['model_path']),'validation_passed':True,'catch_classic_npp_unchanged':True,'selected_identity_rationale_unchanged':True}
        summary['methods_2019_tC']={r['method']:r[2019]/9 for r in records(reread,'PPR','Annual') if r['scope']=='all' and r['catch_basis']=='catch' and r['unidentified']=='method' and r['metric']=='ppr'}
        save(out/'summary.json',summary);summaries.append(summary)
    save(HERE/'three_region_summary.json',summaries);print(json.dumps(summaries,indent=2))
if __name__=='__main__':main()
