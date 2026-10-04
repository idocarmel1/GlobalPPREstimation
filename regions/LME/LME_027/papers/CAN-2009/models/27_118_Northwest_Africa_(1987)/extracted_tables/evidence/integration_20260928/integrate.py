"""Integrate evidence-backed partial GE results; preserve the original workbook."""
from pathlib import Path
import sys, json, re, csv, shutil, math, copy, hashlib
from collections import defaultdict
import pandas as pd
import openpyxl
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'Project.xlsx').is_file())
REGION=ROOT/'regions/LME_027'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate,set_setting,set_result_hash

MODEL=HERE.parent.name
PATH=REGION/'LME_027.xlsx'
def dump(name,v): (HERE/name).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def writecsv(name,header,data):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(data)

if __name__=='__main__':
    backup=HERE/'LME_027_before_integration.xlsx'
    if not backup.exists(): shutil.copy2(PATH,backup)
    baseline=read_book(backup);book=copy.deepcopy(baseline)
    raw=json.loads((HERE.parent/'model.json').read_text(encoding='utf-8'))
    assert sha(HERE.parent/'model.json')==sha(HERE/(MODEL+'.json'))
    byseq={int(g['group_seq']):g for g in raw['group']}
    txt=(REGION/'papers/CAN-2009/Morissette_2008_preliminary.txt').read_text(encoding='utf-8')
    text=txt[txt.index('Table 1: List'):txt.index('PDF PAGE 24')]
    hits=list(re.finditer(r'(?m)^(\d+)\. ([^\n]+)\s*\n',text))
    assert len(hits)==27
    # Table 1 whale order differs: use a verified identity crosswalk, never positions.
    cross={1:1,2:2,3:3,4:5,5:4,6:8,7:9,8:6,9:7,**{i:i for i in range(10,28)}}
    taxa_descriptions={};member_groups=defaultdict(set);generic_groups=defaultdict(set);member_rows=[];cross_rows=[]
    for n,m in enumerate(hits):
        source_seq=int(m[1]);seq=cross[source_seq];name=byseq[seq]['group_name']
        s=text[m.end():hits[n+1].start() if n+1<len(hits) else len(text)]
        s=re.sub(r'(?m)^PDF PAGE \d+\s*$','',s);s=re.sub(r'(?m)^\d+\s*$','',s);s=' '.join(s.split())
        taxa_descriptions[seq]='Precursor Table 1 (2008), not final 2009 membership confirmation: '+s
        page=20 if source_seq<=14 else 21 if source_seq<=17 else 22 if source_seq<=20 else 23
        cross_rows.append([source_seq,m[2].strip(),seq,name,page,'precursor composition; identity crosswalk only'])
        if seq>=24:continue
        for member in s.split(','):
            member=' '.join(member.strip().split())
            if not member:continue
            member_rows.append([source_seq,seq,name,member,page,'precursor composition; key species not equated with all members'])
            key=member.casefold();member_groups[key].add(name)
            if re.fullmatch(r'[A-Z][a-z]+ sp\.?',member):generic_groups[member.split()[0].casefold()].add(name)
    # Genus labels spanning documented groups must not be assigned using an arbitrary pool.
    for genus in generic_groups:
        for name,groups in member_groups.items():
            if name.startswith(genus+' '):generic_groups[genus].update(groups)
    writecsv('taxonomy.csv',['seq','group_name','taxon_descr'],[[i,byseq[i]['group_name'],taxa_descriptions[i]] for i in sorted(byseq)])
    writecsv('source_membership_table.csv',['source_seq','runtime_seq','runtime_group','source_member','pdf_page','scope'],member_rows)
    writecsv('source_group_crosswalk.csv',['source_seq','source_group','runtime_seq','runtime_group','pdf_page','scope'],cross_rows)
    groups=pd.read_csv(HERE/'runtime_groups.csv',keep_default_na=False)
    group_records=[]
    for r in groups.to_dict('records'):
        r={k:(None if v=='' else v) for k,v in r.items()}
        r['taxon_descr']=taxa_descriptions.get(int(r['seq']),'Synthetic Import; not a source biological group')
        group_records.append(r)
    book['Selected model groups']['Groups']=table_dict(group_records)
    coefficients=pd.read_csv(HERE/'direct_group_sppr.csv')
    # Independent compare by exact name to retained exporter tables in all source scopes.
    w=openpyxl.load_workbook(HERE.parent/'sppr_source.xlsx',read_only=True,data_only=True)
    maxdiff=0.
    for scope in ['all','inner','PP']:
        a=list(w['sppr_'+scope].values);ix=a[0].index('new_GE');retained={r[1]:r[ix] for r in a[1:]}
        for r in coefficients[(coefficients.scope==scope)&(coefficients.method=='new_GE')].to_dict('records'):
            old=retained[r['group']];new=r['sppr'];assert math.isclose(old,new,rel_tol=1e-11,abs_tol=1e-9)
            maxdiff=max(maxdiff,abs(old-new))
    w.close()
    coeff_rows=[[MODEL,r['group'],r['scope'],r['method'],r['sppr']] for r in coefficients.to_dict('records') if r['method']=='new_GE']
    assert all(math.isfinite(r[-1]) and r[-1]>=0 for r in coeff_rows)
    book['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],coeff_rows)
    catch=records(book,'Catch','Catch');unique={r['taxon']:r for r in catch}
    # Source labels with demonstrated cross-group ambiguity remain unresolved even if printed once.
    ambiguous={'elasmobranchii','gadiformes','scombridae','carangidae','pristidae','centrolophidae','scomberomorus'}
    mapped={};mapping=[]
    evidence='papers/CAN-2009/Morissette_2008_preliminary.pdf Table 1 pp20–23; '+str(HERE.relative_to(REGION)).replace('\\','/')+'/source_membership_table.csv'
    for taxon,r in sorted(unique.items()):
        key=taxon.casefold();gs=member_groups.get(key,set());why='exact label in precursor composition table'
        if not gs and key in generic_groups:gs=generic_groups[key];why='genus explicitly listed as sp. in precursor; no competing listed group'
        if not gs and taxon.split()[0].casefold() in generic_groups:
            gs=generic_groups[taxon.split()[0].casefold()];why='contained in explicitly listed genus sp.; no competing listed group'
        if not gs and r['functional_group']=='Cephalopods':gs={'Cephalopods'};why='catch classifier Cephalopods is contained in explicitly documented Cephalopoda; one model pool'
        if key in ambiguous:gs=set();why='source contains cross-group taxonomic overlap; allocation not supported'
        if len(gs)==1:
            group=next(iter(gs));mapped[taxon]=group
            mapping.append([MODEL,taxon,group,1.,'medium',evidence,why+'; precursor membership transfer, not final-version confirmation; full within-pool weight 1, no between-pool weights inferred'])
        else:
            mapping.append([MODEL,taxon,None,None,'unresolved',evidence,why if key in ambiguous else 'No unique supported precursor membership or allocation; no catch-share weights inferred'])
    book['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],mapping)
    writecsv('matching_review.csv',book['PPR']['Matching'][0],mapping)
    reports=json.loads((HERE/'direct_reports.json').read_text(encoding='utf-8'))
    book['Diagnostics']['direct_review']=table_dict([dict(model_id=MODEL,method=k,status=v['status'],model_input_grade=v['model_input']['status'],model_strict_balanced=v['model_input']['is_model_balanced'],divergence_grade=v['divergence']['status'],balance_grade=v['balance']['status'],balance_strict_balanced=v['balance']['is_balanced'],balance_relative_gap=v['balance']['rel_gap'],evidence=str(HERE.relative_to(REGION)).replace('\\','/')+'/DIRECT_DIAGNOSTICS.md') for k,v in reports.items()])
    book['PPR']['Annual']=(ANNUAL_HEADER,[[MODEL,s,'new_GE','catch','method','ppr','provisional: GE WARN; strict balance false; precursor taxonomy; partial catch coverage',*[None]*70] for s in ['all','inner','PP']])
    set_setting(book,'results_model_id',MODEL);set_setting(book,'results_model_sha256',sha(HERE.parent/'model.json'))
    recalculate(book,PATH)
    # The request preserves classic results including prior sensitivity evidence and its ratio rows.
    book['Classic PPR']=copy.deepcopy(baseline['Classic PPR'])
    h,rr=book['PPR–NPP']['Ratios']
    old_classic=[r for r in rows(baseline,'PPR–NPP','Ratios') if not r[0]]
    book['PPR–NPP']['Ratios']=(h,old_classic+[r for r in rr if r[0]])
    coverage=[]
    for basis in ['landings','catch','discards']:
        for year in YEARS:
            rr=[r for r in catch if r['catch_basis']==basis];total=math.fsum(r[year] for r in rr if finite(r[year]));covered=math.fsum(r[year] for r in rr if r['taxon'] in mapped and finite(r[year]))
            coverage.append(dict(year=year,basis=basis,total_catch_t=total,covered_catch_t=covered,coverage_pct=100*covered/total if total else None))
    book['Diagnostics']['mapping_coverage']=table_dict(coverage)
    c19=next(r for r in coverage if r['year']==2019 and r['basis']=='catch')
    p19=next(r[7+69]/9 for r in rows(book,'PPR','Annual') if r[1:6]==['all','new_GE','catch','method','ppr'])
    set_setting(book,'production_eligible',False)
    set_setting(book,'source_note','Partial supported-catch GE subtotal; source composition comes from recovered 2008 precursor Table 1, not verified final 2009 inventory. EcoBase 118 source differs in period/version; no numerical source values replaced. Geography is broader offshore Northwest Africa, not exact LME boundary. Canonical source unchanged; selected loader bookkeeping documented separately.')
    set_setting(book,'calculation_status',f'GE direct WARN; partial supported-catch 2019 coverage {c19["coverage_pct"]:.6f}%; precursor taxonomy limitation and strict balance flags retained. TE and With Egestion diagnostics retained only. Unresolved labels have no GE estimate.')
    set_result_hash(book)
    write_book(PATH,book)
    saved=read_book(PATH);validate_region(saved,PATH)
    for sheet in ['Catch','Classic PPR','NPP']:assert digest_tables(list(saved[sheet].items()))==digest_tables(list(baseline[sheet].items())),sheet
    assert overview(saved)['selected_model_id']==overview(baseline)['selected_model_id']
    assert overview(saved)['selection_rationale']==overview(baseline)['selection_rationale']
    assert [r for r in rows(saved,'PPR–NPP','Ratios') if not r[0]]==old_classic
    unresolved=sorted([dict(taxon=r['taxon'],catch_2019_t=r[2019]) for r in catch if r['catch_basis']=='catch' and r['taxon'] not in mapped],key=lambda r:-(r['catch_2019_t'] or 0))
    dump('integration_verification.json',dict(model_id=MODEL,canonical_sha256=sha(HERE.parent/'model.json'),backup_sha256=sha(backup),workbook_sha256=sha(PATH),GE_2019_all_catch_tC=p19,coverage_2019=c19,mapped_taxa=len(mapped),all_catch_taxa=len(unique),GE_max_absolute_difference_from_retained=maxdiff,preserved=['Catch','Classic PPR','NPP','selection','classic PPR–NPP ratios'],unresolved_top20=unresolved[:20],regional_validation_passed=True))
    print(json.dumps(dict(GE_2019_all_catch_tC=p19,coverage=c19,mapped_taxa=len(mapped),total_taxa=len(unique))))
