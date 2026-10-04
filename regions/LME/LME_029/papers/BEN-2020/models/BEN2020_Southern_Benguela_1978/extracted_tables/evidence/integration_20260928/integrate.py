"""Provisional display of already selected model arithmetic; no ecological repairs."""
from pathlib import Path
import sys,json,csv,shutil,copy,re,math
from collections import defaultdict
import pandas as pd
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'Project.xlsx').exists())
REGION=HERE.parents[2];MODEL=HERE.parent.name;UNIT=REGION.name;PATH=REGION/(UNIT+'.xlsx')
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate,set_setting,set_result_hash
def dump(name,v):(HERE/name).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def csvout(name,h,rr):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(h);w.writerows(rr)
if __name__=='__main__':
    backup=HERE/(UNIT+'_before_integration.xlsx')
    if not backup.exists():shutil.copy2(PATH,backup)
    base=read_book(backup);book=copy.deepcopy(base);before_source=sha(HERE.parent/'model.json')
    assert overview(base)['selected_model_id']==MODEL
    raw=json.loads((HERE.parent/'model.json').read_text(encoding='utf-8'))
    source_groups={g['group_name']:g for g in raw['group']}
    rr=pd.read_csv(HERE/'runtime_groups.csv',keep_default_na=False).to_dict('records')
    groups=[]
    for r in rr:
        r={k:(None if v=='' else v) for k,v in r.items()}
        if r['group_name'] in source_groups:r['taxon_descr']=source_groups[r['group_name']].get('taxon_descr')
        groups.append(r)
    book['Selected model groups']={'Groups':table_dict(groups),'Group SPPR':(['model_id','group','scope','method','sppr'],[])}
    coefficients=pd.read_csv(HERE/'direct_group_sppr.csv').to_dict('records')
    methods=sorted(set(r['method'] for r in coefficients))
    book['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],[[MODEL,r['group'],r['scope'],r['method'],r['sppr']] for r in coefficients])
    if UNIT=='LME_024':
        issue='source model balance FAIL; GE/With Egestion PP balance FAIL; authorized routing experiment; partial LME and stage coverage'
        evidence='models/Hernvann_2020_Celtic_Sea_1985/extracted_tables/taxonomy.csv; Supplement B1/B4; models/extraction_review_20260928/authorized_routing_experiment/REPORT.md'
        manual={'Pecten maximus':('Commercial bivalves','Pectinid bivalve; B1 explicitly includes commercially exploited Pectinids'),'Aequipecten opercularis':('Commercial bivalves','Pectinid bivalve; B1 explicitly includes commercially exploited Pectinids'),'Pectinidae':('Commercial bivalves','B1 explicitly includes commercially exploited Pectinids')}
        alias={}
    else:
        issue='source model balance FAIL; incomplete native stanza/BA representation; defaulted inputs; partial southern LME and stage coverage'
        evidence='models/BEN2020_Southern_Benguela_1978/extracted_tables/Taxonomy.xlsx; main Table1 and supplement S2; source REPORT.md'
        manual={}
        alias={'Etrumeus whiteheadi':('Etrumeus whiteheadii','Source spelling whiteheadii; accepted spelling Etrumeus whiteheadi verified in ITIS TSN551211 / FAO https://www.fao.org/4/ac482e/ac482e08.pdf'),
               'Trichiurus lepturus':('Trichuiurus lepturus','Source genus transposition; Trichiurus lepturus verified WoRMS AphiaID127089 https://www.marinespecies.org/CaRMS/aphia.php?id=127089&p=taxdetails')}
    descriptions={r['group_name']:(r.get('taxon_descr') or '') for r in groups if r.get('trophic_info')=='Regular'}
    # Named matches outrank generic genus examples. Stage duplicates and contradictory sources never get weights.
    catch=records(book,'Catch','Catch');unique={r['taxon']:r for r in catch};mapping=[];mapped={}
    for taxon,r in sorted(unique.items()):
        needle=alias.get(taxon,(taxon,''))[0]
        # Only species/higher labels explicitly present as entire tokens qualify; a bare genus does not match all species.
        exact=set()
        for name,desc in descriptions.items():
            if desc.startswith('Source conflict:'):continue
            if ' ' in needle and re.search(r'(?<![A-Za-z])'+re.escape(needle)+r'(?![A-Za-z])',desc):exact.add(name)
        why='Explicit named species in source composition/definition; no between-group allocation'
        if alias.get(taxon):why+='; '+alias[taxon][1]
        if UNIT=='LME_029' and taxon=='Austroglossus pectoralis':exact={'Agulhas Sole'};why='Dedicated main Table1 group takes precedence over overlapping S2 example'
        if taxon in manual:exact={manual[taxon][0]};why=manual[taxon][1]
        if not exact:
            genus=needle.split()[0];generic=set()
            for name,desc in descriptions.items():
                if desc.startswith('Source conflict:'):continue
                if re.search(r'\b'+re.escape(genus)+r' spp?\.?\b',desc):generic.add(name)
            if generic:
                other={name for name,desc in descriptions.items() if re.search(r'\b'+re.escape(genus)+r' [a-z]',desc)}
                if len(generic|other)==1:exact=generic;why='Explicit genus sp./spp. in source and no competing named model group'
        if len(exact)==1:
            group=next(iter(exact));mapped[taxon]=group;mapping.append([MODEL,taxon,group,1.,'medium',evidence,why])
        else:
            why='Species spans life stages or source groups; regional allocation weights unavailable' if len(exact)>1 else 'No unique documented membership or supported allocation; unresolved'
            mapping.append([MODEL,taxon,None,None,'unresolved',evidence,why])
    book['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],mapping)
    csvout('matching_review.csv',book['PPR']['Matching'][0],mapping)
    reports=json.loads((HERE/'direct_reports.json').read_text(encoding='utf-8'))
    book.setdefault('Diagnostics',{})['provisional_direct_review']=table_dict([dict(model_id=MODEL,method=k,status=v['status'],model_input_grade=v['model_input']['status'],model_strict_balanced=v['model_input']['is_model_balanced'],divergence_grade=v['divergence']['status'],balance_grade=v['balance']['status'],balance_strict_balanced=v['balance'].get('is_balanced'),balance_relative_gap=v['balance'].get('rel_gap'),evidence=str(HERE.relative_to(REGION)).replace('\\','/')+'/DIRECT_DIAGNOSTICS.md',note='Provisional numeric display requested by user; diagnostic grades unchanged') for k,v in reports.items()])
    book['PPR']['Annual']=(ANNUAL_HEADER,[[MODEL,s,m,'catch','method','ppr','provisional: '+issue,*[None]*70] for s in ['all','inner','PP'] for m in methods])
    set_setting(book,'results_model_id',MODEL);set_setting(book,'results_model_sha256',before_source)
    recalculate(book,PATH)
    book['Classic PPR']=copy.deepcopy(base['Classic PPR'])
    old_ratios=[r for r in rows(base,'PPR–NPP','Ratios') if not r[0]]
    h,rr=book['PPR–NPP']['Ratios'];book['PPR–NPP']['Ratios']=(h,old_ratios+[r for r in rr if r[0]])
    coverage=[]
    for basis in ['landings','catch','discards']:
        for year in YEARS:
            rr=[r for r in catch if r['catch_basis']==basis];total=math.fsum(r[year] for r in rr if finite(r[year]));covered=math.fsum(r[year] for r in rr if r['taxon'] in mapped and finite(r[year]))
            coverage.append(dict(year=year,basis=basis,total_catch_t=total,covered_catch_t=covered,coverage_pct=100*covered/total if total else None))
    book['Diagnostics']['mapping_coverage']=table_dict(coverage)
    c19=next(r for r in coverage if r['year']==2019 and r['basis']=='catch')
    p19={r[2]:r[76]/9 if finite(r[76]) else None for r in rows(book,'PPR','Annual') if r[1]=='all' and r[3:6]==['catch','method','ppr']}
    set_setting(book,'production_eligible',False)
    set_setting(book,'source_note','PROVISIONAL arithmetic for user-selected model; scientific validation deferred. '+issue+'. Canonical model untouched; runtime evidence in '+str(HERE.relative_to(REGION)).replace('\\','/')+'. Unmapped catch omitted; model-period coefficients over historical catch are not yearly ecosystem reconstructions.')
    set_setting(book,'calculation_status',f'PROVISIONAL numeric SPPR-to-catch mapping and annual results; diagnostics FAIL unchanged; 2019 supported catch {c19["coverage_pct"]:.6f}%; life-stage/coarse allocations unresolved')
    set_result_hash(book);write_book(PATH,book);saved=read_book(PATH);validate_region(saved,PATH)
    for sheet in ['Catch','Classic PPR','NPP']:assert digest_tables(list(saved[sheet].items()))==digest_tables(list(base[sheet].items())),sheet
    for key in ['selected_model_id','selection_rationale']:assert overview(saved)[key]==overview(base)[key]
    assert [r for r in rows(saved,'PPR–NPP','Ratios') if not r[0]]==old_ratios
    assert sha(HERE.parent/'model.json')==before_source
    unresolved=sorted([dict(taxon=r['taxon'],catch_2019_t=r[2019]) for r in catch if r['catch_basis']=='catch' and r['taxon'] not in mapped],key=lambda r:-(r['catch_2019_t'] or 0))
    dump('integration_verification.json',dict(model_id=MODEL,canonical_sha256=before_source,backup_sha256=sha(backup),workbook_sha256=sha(PATH),provisional_2019_all_catch_tC=p19,coverage_2019=c19,mapped_taxa=len(mapped),historical_taxa=len(unique),unresolved_top20=unresolved[:20],regional_validation_passed=True,preserved=['canonical','selection','rationale','Catch','Classic PPR','NPP','classic ratios']))
    print(json.dumps(dict(unit=UNIT,provisional_2019_all_catch_tC=p19,coverage=c19,mapped=len(mapped),total=len(unique))))
