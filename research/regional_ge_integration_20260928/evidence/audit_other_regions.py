import json,sys,pathlib,math
sys.path.insert(0,'tools')
from workbooks import read_book,overview,records,validate_region,input_hash,sha
from regional import result_hash
outdir=pathlib.Path('original_research_archive/research/regional_ge_integration_20260928')
inv=json.loads((outdir/'fast_overview_inventory.json').read_text())
out=[]
for entry in inv:
 if not entry.get('selected_model_id') or entry['unit_id'] in ['LME_022','LME_027','HS_077']:continue
 p=pathlib.Path(entry['path']);b=read_book(p);o=overview(b)
 a={'unit_id':entry['unit_id'],'overview':o,'workbook_sha256':sha(p),'model_sha256':sha(p.parent/o['model_path'])}
 try:validate_region(b,p);a['freshness_validation']='PASS'
 except Exception as e:a['freshness_validation']=str(e)
 a['result_fingerprint_matches']=o.get('calculation_result_sha256')==result_hash(b)
 a['table_counts']={s:{t:len(v[1]) for t,v in tabs.items()} for s,tabs in b.items()}
 a['diagnostics']={k:[dict(zip(h,r)) for r in rr] for k,(h,rr) in b.get('Diagnostics',{}).items()}
 a['ge_annual_2019']=[{str(k):v for k,v in r.items() if not isinstance(k,int) or k==2019} for r in records(b,'PPR','Annual') if r.get('method')=='new_GE' and r.get('scope')=='all' and r.get('catch_basis')=='catch' and r.get('unidentified_treatment')=='method']
 matching=records(b,'PPR','Matching');catch=records(b,'Catch','Catch');resolved={r.get('taxon') for r in matching if r.get('group') and isinstance(r.get('weight'),(int,float)) and r['weight']>0}
 cr=[r for r in catch if r.get('catch_basis')=='catch'];total=math.fsum(r[2019] for r in cr if isinstance(r.get(2019),(int,float)));covered=math.fsum(r[2019] for r in cr if r.get('taxon') in resolved and isinstance(r.get(2019),(int,float)))
 a['mapping_coverage_2019']={'total_catch_tonnes':total,'mapped_catch_tonnes':covered,'fraction':covered/total if total else None,'resolved_taxa':len(resolved),'catch_taxa':len(cr),'mapping_rows':len(matching)}
 a['matching_evidence_samples']=matching[:4]
 a['largest_unresolved_2019']=[{'taxon':r['taxon'],'tonnes':r.get(2019)} for r in sorted(cr,key=lambda r:r.get(2019) or 0,reverse=True) if r['taxon'] not in resolved][:8]
 a['ge_group_coefficients']={'rows':len([r for r in records(b,'Selected model groups','Group SPPR') if r.get('method')=='new_GE']),'all_finite_nonnegative':all(isinstance(r.get('sppr'),(int,float)) and math.isfinite(r['sppr']) and r['sppr']>=0 for r in records(b,'Selected model groups','Group SPPR') if r.get('method')=='new_GE')}
 out.append(a);(outdir/'other_regions_raw_audit.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
 print(entry['unit_id'],a['freshness_validation'],a['table_counts']['PPR'].get('Annual'),a['mapping_coverage_2019'],flush=True)
print('DONE',len(out))
