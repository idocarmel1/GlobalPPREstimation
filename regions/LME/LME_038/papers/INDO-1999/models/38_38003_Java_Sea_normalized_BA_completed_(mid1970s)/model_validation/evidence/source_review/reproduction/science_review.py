from pathlib import Path
import sys,json,pickle,math,collections,csv,gzip,hashlib,shutil
import numpy as np
import fitz
Q=Path(__file__).parent;ROOT=Q.parents[4];sys.path.insert(0,str(ROOT/'tools'));import workbooks as W
R=ROOT/'regions/LME_038';MID='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)';E=R/'validation_reports'/MID;b=pickle.load((Q/'book.pkl').open('rb'))
def dump(n,x):(E/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
snap=json.loads((Q.parents[1]/'central_source_metadata_current.json').read_text(encoding='utf-8'))
print('snap tables',[(k,type(v).__name__)for k,v in snap['tables'].items()])
sel={sn:[x for x in rs if x.get('unit_id')=='LME_038']for sn,rs in snap['tables'].items()}
dump('central_metadata_snapshot.json',dict(project_sha256=snap['project_sha256'],tables=sel,purpose='Authenticated regional read-only metadata provenance; expected-old proposals only.'))
g={int(x['seq']):x for x in W.records(b,'Selected model groups','Groups')};gn={s:x['group_name']for s,x in g.items()}
new=json.loads((E/'direct_diagnostics/loaded_groups.json').read_text(encoding='utf-8'));diff=[]
for s,v in zip(new['index'],new['data']):
 row=dict(zip(new['columns'],v))
 for f in ['biomass','pb','qb','p','q','ee','catch','M0','gs','egestion','respiration','biomass_accum','emigration','immigration','net_migration','predation','flow_to_det','detritus_import']:
  a=g[int(s)][f];c=row[f]
  if not math.isclose(a,c,rel_tol=1e-10,abs_tol=1e-9):diff.append(dict(seq=s,field=f,old=a,new=c))
assert not diff,diff
reports=json.loads((E/'direct_diagnostics/direct_reports.json').read_text(encoding='utf-8'));sol=json.loads((E/'direct_diagnostics/direct_solutions.json').read_text(encoding='utf-8'));methods=[];negs=[];scopediff=[]
for option,z in sol.items():
 m=z['SPPR'];a=np.asarray(m['data'],dtype=float);ix=list(map(int,m['index']));cols=list(map(int,m['columns']));assert a.shape==(len(ix),len(cols))and len(ix)==len(set(ix))and len(cols)==len(set(cols))
 pp=[s for s in cols if g[s]['group_type']=='PP'];inn=[s for s in cols if g[s]['group_type']!='Import'];r=reports[option];dd=r['divergence'];meth={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}[option]
 for i,s in enumerate(ix):
  for j,c in enumerate(cols):
   if a[i,j]<0:negs.append(dict(method=option,source_id=c,source_name=gn[c],recipient_id=s,recipient_name=gn[s],value=float(a[i,j])))
  for scope,ids in [('all',cols),('inner',inn),('PP',pp)]:
   ex=math.fsum(a[i,cols.index(c)]for c in ids);old=next(x['sppr']for x in W.records(b,'Selected model groups','Group SPPR')if x['group']==gn[s]and x['method']==meth and x['scope']==scope)
   if not math.isclose(ex,old,rel_tol=1e-10,abs_tol=1e-8):scopediff.append(dict(option=option,scope=scope,seq=s,new=ex,old=old))
 methods.append(dict(method=option,grade=r.get('status'),rows=len(ix),columns=len(cols),row_ids=ix,source_ids=cols,source_names=[gn[s]for s in cols],all_entries_finite=bool(np.isfinite(a).all()),entries=int(a.size),negative_entries=int((a<0).sum()),negative_source_columns=int((a<0).any(axis=0).sum()),saved_negative_source_columns=dd['n_negative_sources'],rho_living=dd['rho_living'],b=dd['b'],detritus_sppr={str(k):v for k,v in dd['sppr_det'].items()},warnings=r['warnings'],min_sppr=float(a.min()),max_sppr=float(a.max()),null_mask=np.isnan(a).tolist(),positive_inf_mask=np.isposinf(a).tolist(),negative_inf_mask=np.isneginf(a).tolist()))
assert not scopediff,scopediff
dump('matrix_inspection.json',dict(canonical_sha256=W.sha(R/'models'/MID/'model.json'),loaded_state_matches=True,loaded_state_differences=diff,methods=methods,scope_coefficients_match=True,scope_differences=scopediff,inspection='Every recipient and every basal source, including unfished biological groups and computational Import. Strict sign test <0 without rounding.',units='SPPR wet weight requirement per catch mass; matrix rows recipients, columns basal sources.'))
dump('negative_source_entries.json',negs)
pdf=R/'papers/BUCHARY-1991/ubc_1999-0254.pdf.pdf';geo=E/'geography';geo.mkdir(exist_ok=True);d=fitz.open(pdf)
for page in [1,30,55,58,59,80,81]:d[page-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(geo/f'original_pdf_page_{page}.png'))
print('methods',[(x['method'],x['grade'],x['rows'],x['columns'],x['rho_living'],x['b'],x['detritus_sppr'])for x in methods])
with gzip.open(R/'raw/LME_038.csv.gz','rt',encoding='utf-8-sig')as f:rd=csv.DictReader(f);print('rawheaders',rd.fieldnames);print('rawfirst',next(rd))
print('labels',len([x for x in W.records(b,'Catch','Catch')if x['catch_basis']=='landings']))
