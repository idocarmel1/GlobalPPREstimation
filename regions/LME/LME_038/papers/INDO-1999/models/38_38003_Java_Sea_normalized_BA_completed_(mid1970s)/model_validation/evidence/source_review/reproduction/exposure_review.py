from pathlib import Path
import pickle,json,sys,math,collections
Q=Path(__file__).parent;ROOT=Q.parents[4];sys.path.insert(0,str(ROOT/'tools'));import workbooks as W
MID='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)';E=ROOT/'regions/LME_038/validation_reports'/MID;b=pickle.load((Q/'adopted_book.pkl').open('rb'));a=json.loads((E/'taxon_audit.json').read_text(encoding='utf-8'));by={r['taxon']:r for r in a};cs={r['taxon']:r[2019]for r in W.records(b,'Catch','Catch')if r['catch_basis']=='landings'};results=[]
for method in ['new_GE','new_TE_EEfix','new_WithEgestion']:
 rows=[]
 for r in W.records(b,'PPR','Taxon SPPR'):
  if r['method']==method and r['scope']=='all':
   t=r['taxon'];v=r['sppr'];c=cs[t];v=0. if c==0 else c*v/9 if W.finite(v)else None;rows.append(dict(taxon=t,ppr_tC=v,coefficient_wet=r['sppr'],catch_tonnes=c,confidence=by[t]['overall_confidence'],groups=by[t]['group_names'],weights=by[t]['weights']))
 total=math.fsum(r['ppr_tC']for r in rows if r['ppr_tC']is not None);vl=math.fsum(r['ppr_tC']for r in rows if r['confidence']=='Very low'and r['ppr_tC']is not None);rows=sorted(rows,key=lambda r:-(r['ppr_tC']if r['ppr_tC']is not None else-1))
 for r in rows:r['percentage']=100*r['ppr_tC']/total if r['ppr_tC']is not None else None
 ar=next(r for r in W.records(b,'PPR','Annual')if r['method']==method and r['scope']=='all'and r['catch_basis']=='landings'and r['unidentified']=='method'and r['metric']=='ppr');assert math.isclose(total,ar[2019]/9,abs_tol=1e-6,rel_tol=1e-12)
 results.append(dict(method=method,year=2019,basis='landings',scope='all',unidentified='method',total_ppr_tC=total,very_low_ppr_tC=vl,very_low_percentage=100*vl/total,top10=rows[:10],all_taxon_contributions=rows,status=ar['status']))
(E/'method_specific_mapping_exposure.json').write_text(json.dumps(results,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');print(json.dumps([{k:r[k]for k in ['method','total_ppr_tC','very_low_percentage','top10']}for r in results],ensure_ascii=False,indent=2))
