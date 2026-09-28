"""Independent source-supported taxonomy preparation; no numeric-method adoption."""
from pathlib import Path
import sys,json,csv,math
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_049';MID='49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)';DEST=REG/'models'/MID;EV=DEST/'evidence'
sys.path.insert(0,str(ROOT/'tools'));from workbooks import read_book,records,YEARS,finite
b=read_book(REG/'LME_049.xlsx');catch=records(b,'Catch','Catch');taxa=sorted({r['taxon'] for r in catch});g=json.loads((DEST/'model.json').read_text(encoding='utf-8'))['group']
members={x['taxon_descr'].split(';')[0]:x for x in g[:35] if isinstance(x['taxon_descr'],str) and 'not documented' not in x['taxon_descr']}
# The source explicitly identifies this stock; bracketed gloss is not its name.
members['Gadus chalcogrammus']=g[16]
out=[]
for t in taxa:
    x=members.get(t);e='Watari2019 main Table1 and Section2.3, printed pp297–298; retained canonical taxon_descr' if x else 'Available main-article membership insufficient for exact assignment; supplement unavailable'
    out.append({'model_id':MID,'taxon':t,'group':x['group_name'] if x else None,'group_seq':int(x['group_seq']) if x else None,'weight':1.0 if x else None,'confidence':'direct source membership' if x else 'unresolved','evidence':e,'explanation':'Exact published single-species stock; coefficient/publication approval remains separate' if x else 'No assumed pooled membership, synonym equivalence or spatial weights'})
with (EV/'source_supported_matching_preparation.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
resolved={r['taxon'] for r in out if r['group']};coverage=[]
for basis in ['landings','catch','discards']:
    rr=[r for r in catch if r['catch_basis']==basis]
    for y in YEARS:
        total=math.fsum(r[y] for r in rr if finite(r.get(y)));covered=math.fsum(r[y] for r in rr if r['taxon'] in resolved and finite(r.get(y)));complete=all(finite(r.get(y)) for r in rr)
        coverage.append({'year':y,'catch_basis':basis,'available_total_tonnes':total,'exact_member_tonnes':covered,'share_of_available_tonnage':covered/total if total else None,'all_basis_rows_present':complete,'note':'Evidence-preparation coverage; not accepted numerical model PPR coverage'})
with (EV/'exact_membership_coverage.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=coverage[0].keys());w.writeheader();w.writerows(coverage)
top=sorted([{'taxon':r['taxon'],'catch_2019':r.get(2019),'reason':'unresolved source membership/spatial apportionment; no guessed mapping'} for r in catch if r['catch_basis']=='catch' and r['taxon'] not in resolved],key=lambda r:r['catch_2019'] or 0,reverse=True)
summary={'n_taxa':len(taxa),'exact_source_memberships_prepared':len(resolved),'resolved_taxa':sorted(resolved),'unresolved_taxa':len(taxa)-len(resolved),'coverage_2019':[r for r in coverage if r['year']==2019],'top_unresolved_2019':top[:25],'regional_matching_published':False,'model_annual_PPR_published':False,'reason':'Independent taxonomy evidence retained; no complete accepted mapping or numerical adoption implied'}
(EV/'matching_preparation_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
