"""Update generated regional tables while preserving centrally edited source metadata."""
import argparse
from pathlib import Path
from workbooks import *
from regional import comparison_tables,result_hash

def update(root, paths, all_regions=False):
    project_path=root/'Project.xlsx'; p=read_book(project_path)
    loaded=[]
    modelids={(r['unit_id'],r['model_id']) for r in records(p,'Models & coverage','Models')}
    for path in paths:
        b=read_book(path);o=validate_region(b,path)
        if o.get('calculation_result_sha256')!=result_hash(b):raise ValueError(f'{path}: generated results changed outside the regional calculation; refresh first')
        if o.get('selected_model_id') and (o['unit_id'],o['selected_model_id']) not in modelids:raise ValueError(f"{o['unit_id']}: register selected model for this region in Project.xlsx / Models & coverage first")
        loaded.append((path,b,o))
    units={o['unit_id'] for _,_,o in loaded}
    if len(units)!=len(loaded):raise ValueError('Duplicate region input')
    outputs={
      ('Regions & status','Regions'):(['unit_id','name','type','selected_model_id','selection_rationale','status','workbook','sha256','production_eligible','catch_available','classic_taxa_with_sppr','sppr_group_rows','resolved_taxa','unresolved_taxa','npp_available'],[]),
      ('Regional PPR','Annual'):(['unit_id',*ANNUAL_HEADER],[]),
      ('Regional NPP','NPP'):(['unit_id','method','units',*YEARS],[]),
      ('Regional NPP','Provenance'):(['unit_id','year','details'],[]),
      ('Method comparisons','Pairs'):(['unit_id','model_id','scope','unidentified','numerator','denominator','cohort_id'],[]),
      ('Method comparisons','Common catch totals'):(['unit_id','model_id','scope','unidentified','catch_basis','cohort_id','method','metric',*YEARS],[]),
      ('Diagnostics & sensitivity','Diagnostics'):(['unit_id','table','record'],[])}
    for path,b,o in loaded:
        unit=o['unit_id']
        catch_taxa={r['taxon'] for r in records(b,'Catch','Catch')};matched={r['taxon'] for r in records(b,'PPR','Matching') if r.get('group')}
        outputs['Regions & status','Regions'][1].append([unit,o['region_name'],o['region_type'],o.get('selected_model_id'),o.get('selection_rationale'),o.get('calculation_status'),path.relative_to(root).as_posix(),sha(path),o.get('production_eligible'),bool(catch_taxa),sum(finite(r.get('sppr')) for r in records(b,'Classic PPR','Taxa')),len(rows(b,'Selected model groups','Group SPPR')),len(matched),len(catch_taxa-matched),any(finite(v) for r in rows(b,'NPP','NPP') for v in r[2:])])
        outputs['Regional PPR','Annual'][1].extend([[unit,*r] for r in rows(b,'Classic PPR','Annual')+rows(b,'PPR','Annual')])
        outputs['Regional NPP','NPP'][1].extend([[unit,*r] for r in rows(b,'NPP','NPP')])
        outputs['Regional NPP','Provenance'][1].extend([[unit,r['year'],clean(r)] for r in records(b,'NPP','Provenance')])
        pairs,totals,_=comparison_tables(b)
        outputs['Method comparisons','Pairs'][1].extend(pairs);outputs['Method comparisons','Common catch totals'][1].extend(totals)
        for table in b.get('Diagnostics',{}):
            for r in records(b,'Diagnostics',table):outputs['Diagnostics & sensitivity','Diagnostics'][1].append([unit,table,clean(r)])
    for (sheet,table),(header,new) in outputs.items():
        old=[] if all_regions else [r for r in rows(p,sheet,table) if r[0] not in units]
        p.setdefault(sheet,{})[table]=(header,sorted(old+new,key=lambda r:tuple(str(x or '') for x in r[:7])))
    # Selection columns are derived; the rest of the central model metadata is untouched.
    choices={r[0]:(r[3],r[4]) for r in rows(p,'Regions & status','Regions')}
    h,rr=p['Models & coverage']['Models']
    for name in ['selected','selection_rationale']:
        if name not in h:h.append(name);[r.append(None) for r in rr]
    for r in rr:
        d=dict(zip(h,r));sel,reason=choices.get(d.get('unit_id'),(None,None));chosen=bool(sel and d.get('model_id')==sel)
        r[h.index('selected')]=chosen;r[h.index('selection_rationale')]=reason if chosen else None
    selected_papers={pid for r in rr if r[h.index('selected')] for pid in str(dict(zip(h,r)).get('paper_ids') or '').split(';') if pid}
    ph,pr=p.get('Papers',{}).get('Papers',([],[]))
    if 'selected' in ph and 'article_id' in ph:
        for r in pr:r[ph.index('selected')]=r[ph.index('article_id')] in selected_papers
    p['Definitions & build']['Last build']=(['field','value'],[['schema_version',1],['regional_workbooks',len(rows(p,'Regions & status','Regions'))],['mode','all' if all_regions else 'partial']])
    write_book(project_path,p)
    print(f'Updated {len(units)} regions; central source metadata preserved.',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--all',action='store_true');g.add_argument('--region',type=Path,nargs='+');ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args()
    root=a.root.resolve();paths=sorted((root/'regions').glob('*/*.xlsx')) if a.all else [p.resolve() for p in a.region]
    update(root,paths,a.all)
