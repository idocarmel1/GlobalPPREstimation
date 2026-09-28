"""Operate on a single regional workbook. Research matching is performed by the regional skill."""
import argparse,sys,tempfile,shutil,csv
from pathlib import Path
from workbooks import *
from regional import recalculate,taxon_detail,set_setting,set_result_hash

def prepare_selection(book,path):
    """Keep the old workbook as evidence, and clear only model-dependent results."""
    o=overview(book)
    if not o.get('selected_model_id'):raise ValueError('Enter selected_model_id, model_path and selection_rationale in Overview first')
    model=(path.parent/str(o.get('model_path',''))).resolve()
    if not model.is_relative_to(path.parent.resolve()) or not model.is_file():raise ValueError('Selected JSON must exist inside the region directory')
    if not o.get('selection_rationale'):raise ValueError('Enter a selection rationale in Overview')
    if o.get('results_model_id')==o['selected_model_id'] and o.get('results_model_sha256')==sha(model):
        raise ValueError('This selection already has results; use calculate or sppr for a refresh')
    archive=path.parent/'models'/'previous_results';archive.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,archive/f'{path.stem}_{sha(path)[:12]}.xlsx')
    for sheet in ['Selected model groups','PPR','Diagnostics']:
        book[sheet]={name:(header,[]) for name,(header,data) in book[sheet].items()}
    book['PPR–NPP']['Ratios']=(book['PPR–NPP']['Ratios'][0],[r for r in rows(book,'PPR–NPP','Ratios') if not r[0]])
    set_setting(book,'results_model_id',None);set_setting(book,'results_model_sha256',None)
    set_setting(book,'calculation_status','selected; SPPR, matching and model PPR not yet calculated')
    set_setting(book,'calculation_input_sha256',input_hash(book));set_result_hash(book)

def export_taxon(book,output):
    from regional import inputs
    taxa,catch,_,_=inputs(book);o=overview(book);basis=o.get('catch_basis','landings')
    status={(r[1],r[2]):r[6] for r in rows(book,'PPR','Annual') if r[3]==basis and r[4]=='method' and r[5]=='ppr'}
    with output.open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['model_id','taxon','scope','method','catch_basis','status',*YEARS])
        for r in records(book,'PPR','Taxon SPPR'):
            st=status.get((r['scope'],r['method']),'unavailable');v=r['sppr']
            writer.writerow([r['model_id'],r['taxon'],r['scope'],r['method'],basis,st,*[c*v if st=='ok' and finite(c) and finite(v) else None for c in catch.get((r['taxon'],basis),[None]*70)]])

def sppr(book,path,timeout):
    o=overview(book);selected=o.get('selected_model_id')
    if not selected:raise ValueError('Select a model in Overview first')
    model=path.parent/o['model_path']
    engine=Path(__file__).resolve().parent/'scientific_code/PPREstimation'
    sys.path.insert(0,str(engine))
    import create_PPRS_excel as cpe
    with tempfile.TemporaryDirectory() as tmp:
        inp=Path(tmp)/'models';inp.mkdir();shutil.copy2(model,inp/f'{selected}.json')
        out=Path(tmp)/'out';out.mkdir()
        summary=cpe.run_directory(str(inp),str(out),method_timeout=timeout)
        if summary['n_written']!=1:raise ValueError('SPPR model export failed')
        w=openpyxl.load_workbook(out/f'{selected}.xlsx',read_only=True,data_only=True)
        rr=list(w['groups_df'].values);book['Selected model groups']['Groups']=(list(rr[0]),[list(r) for r in rr[1:]])
        group_rows=[]
        for scope in ['all','inner','PP']:
            rr=list(w['sppr_'+scope].values);group_rows.extend([[selected,r[1],scope,m,r[i]] for r in rr[1:] for i,m in enumerate(rr[0]) if i>=2])
        book['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],group_rows)
        for name in ['model_health','mc_diagnostics','run_notes']:
            rr=list(w[name].values);book['Diagnostics'][name]=(list(rr[0]),[list(r) for r in rr[1:]])
        w.close()
        # Copy the exact numerical source before recording its model identity.
        dest=model.parent/'sppr_source.xlsx';shutil.copy2(out/f'{selected}.xlsx',dest)
    # Health policy is the existing integration implementation, applied to exact configurations.
    sys.path.insert(0,str(Path(__file__).parent/'scientific_helpers'))
    from ppr_scopes import read_health,method_health_flags
    methods=list(dict.fromkeys(r[3] for r in group_rows));gg={}
    for r in group_rows:
        if r[2]=='all':gg.setdefault(r[1],{})[r[3]]=r[4]
    # Preserve statuses conservatively until PPR recomputation examines all groups.
    health=read_health(dest); rr=[]
    failed={k for k,v in health.items() if v.get('status')=='FAIL'}
    exact={'new_GE':'GE','new_TE_EEfix':'TE','new_WithEgestion':'With Egestion'}
    for scope in ['all','inner','PP']:
        for method in methods:
            values=[r[4] for r in group_rows if r[2]==scope and r[3]==method]
            status='ok' if any(finite(v) for v in values) else 'unavailable'
            if exact.get(method) in failed:status='FAIL: configuration diagnostic'
            rr.append([selected,scope,method,'landings','method','ppr',status,*[None]*70])
    book['PPR']['Annual']=(ANNUAL_HEADER,rr)
    set_setting(book,'results_model_id',selected);set_setting(book,'results_model_sha256',sha(model));set_setting(book,'calculation_status','SPPR complete; matching/PPR refresh required')
    set_setting(book,'calculation_input_sha256',None);set_result_hash(book)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--region',type=Path,required=True);ap.add_argument('--stage',choices=['validate','prepare-selection','calculate','inspect-year','export-taxon-ppr','sppr'],required=True);ap.add_argument('--year',type=int);ap.add_argument('--basis',choices=['landings','catch','discards']);ap.add_argument('--output',type=Path);ap.add_argument('--timeout',type=float,default=180);a=ap.parse_args()
    path=a.region.resolve()
    if path.is_dir():path=path/(path.name+'.xlsx')
    b=read_book(path)
    if a.stage=='validate':validate_region(b,path);print('Region is ready for consolidation');return
    if a.year:
        if a.year not in YEARS:raise ValueError('Year must be 1950–2019')
        set_setting(b,'taxon_detail_year',a.year)
    if a.basis:set_setting(b,'catch_basis',a.basis)
    if a.stage=='export-taxon-ppr':
        validate_region(b,path)
        output=a.output or path.parent/'taxon_ppr_export.csv';export_taxon(b,output);print(f'Exported {output}');return
    if a.stage=='prepare-selection':prepare_selection(b,path)
    elif a.stage=='calculate':recalculate(b,path)
    elif a.stage=='sppr':sppr(b,path,a.timeout)
    else:taxon_detail(b)
    write_book(path,b);print(f'Updated {path.name}: {a.stage}')
if __name__=='__main__':main()
