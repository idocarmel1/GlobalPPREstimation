"""Independent arithmetic and retained-evidence checks for the selected regional run."""
from pathlib import Path
import sys,json,csv,math,shutil,platform
import pandas as pd
import numpy as np
MODEL=Path(__file__).resolve().parent;REGION=MODEL.parents[1];ROOT=REGION.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import set_setting
E=MODEL/'selection_20260928';MID=MODEL.name

def equal(a,b):
    return a is None and b is None or finite(a) and finite(b) and math.isclose(a,b,rel_tol=2e-12,abs_tol=1e-8)

def main():
    path=REGION/'LME_014.xlsx';b=read_book(path)
    prior=read_book(next(E.glob('LME_014_before_selection_*.xlsx')))
    provenance=json.loads((E/'selection_provenance.json').read_text())
    assert sha(MODEL/'model.json')==provenance['source_model_sha256']
    computational=REGION/overview(b)['model_path']
    assert sha(computational)==provenance['computational_input_sha256']==provenance['diagnostic_input_sha256']
    unchanged=[]
    for row in json.loads((MODEL.parent/'extraction_review_20260928/evidence/source_manifest.json').read_text()):
        assert sha(ROOT/row['path'])==row['sha256'];unchanged.append(row['path'])
    # Compare original numerical inputs; NPP provenance links are resolved below.
    for sheet,table in [('Catch','Catch'),('Classic PPR','Taxa'),('NPP','NPP')]:
        assert digest_tables([b[sheet][table]])==digest_tables([prior[sheet][table]])
    old=pd.read_csv(MODEL/'loader_completed_groups.csv').set_index('group_seq')
    now=pd.DataFrame(records(b,'Selected model groups','Groups')).set_index('seq')
    numeric=[c for c in old.select_dtypes(include='number').columns if c in now]
    assert set(old.index)==set(now.index)
    assert np.allclose(old[numeric].to_numpy(float),now.loc[old.index,numeric].to_numpy(float),rtol=1e-12,atol=1e-12,equal_nan=True)
    health={r['TE_option']:r['status'] for r in records(b,'Diagnostics','model_health')}
    assert health=={'GE':'WARN','TE':'WARN','With Egestion':'WARN'}
    groups={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(b,'Selected model groups','Group SPPR')}
    assert len(groups)==333 and all(finite(v) and v>=0 for v in groups.values())
    assert {k[2] for k in groups}=={'new_GE','new_TE_EEfix','new_WithEgestion'}
    mapping={}
    for r in records(b,'PPR','Matching'):
        if r['group']:mapping.setdefault(r['taxon'],[]).append((r['group'],r['weight']))
    coeff={}
    for r in records(b,'PPR','Taxon SPPR'):
        assignments=mapping.get(r['taxon'],[])
        expected=round(math.fsum(w*groups[g,r['scope'],r['method']] for g,w in assignments),6) if assignments else None
        assert equal(expected,r['sppr'])
        coeff[r['taxon'],r['scope'],r['method']]=expected
    catch={(r['taxon'],r['catch_basis']):r for r in records(b,'Catch','Catch')}
    flags={r['taxon']:r['unidentified'] for r in records(b,'Catch','Catch')}
    simple={r['taxon']:r['sppr'] for r in records(b,'Classic PPR','Taxa')}
    checked=0
    for r in records(b,'PPR','Annual'):
        for y in YEARS:
            terms=[]
            for (taxon,basis),c in catch.items():
                if basis!=r['catch_basis']:continue
                v=coeff.get((taxon,r['scope'],r['method']))
                if flags[taxon] and r['unidentified']=='zero':v=0.
                if flags[taxon] and r['unidentified']=='simple':v=simple.get(taxon)
                if finite(c[y]) and (finite(v) or r['metric']=='catch'):
                    terms.append(c[y]*v if r['metric']=='ppr' else c[y])
            expected=math.fsum(terms) if terms and (r['status']=='ok' or r['metric']=='catch') else None
            assert equal(expected,r[y]),(r['method'],r['scope'],r['metric'],y,expected,r[y])
            checked+=1
    annual={(r['model_id'],r['scope'],r['method'],r['catch_basis'],r['unidentified']):r for sheet in ['PPR','Classic PPR'] for r in records(b,sheet,'Annual') if r['metric']=='ppr'}
    npp={r['method']:r for r in records(b,'NPP','NPP')}
    ratio_checks=0
    for r in records(b,'PPR–NPP','Ratios'):
        p=annual[r['model_id'],r['scope'],r['method'],r['catch_basis'],r['unidentified']]
        for y in YEARS:
            den=npp[r['npp_method']][y]
            expected=100*p[y]/9/den if finite(p[y]) and finite(den) and den>0 else None
            assert equal(expected,r[y]);ratio_checks+=1
    relocation=list(csv.DictReader((ROOT/'common_reference_data/provenance/archive_relocation.csv').open(encoding='utf-8-sig')))
    # Resolve historic adopted NPP provenance through the authoritative relocation map;
    # only the link changes, and the archived bytes must match its recorded hash.
    links_file=E/'npp_provenance_links.json'
    relocations=json.loads(links_file.read_text(encoding='utf-8')) if links_file.exists() else []
    header,data=b['NPP']['Provenance'];ix=header.index('provenance')
    for row in data:
        oldpath=row[ix]
        if not oldpath:continue
        if (ROOT/str(oldpath)).is_file():continue
        candidates=[r for r in relocation if r.get('source')=='original_research_archive/legacy/'+str(oldpath) or r.get('source')==str(oldpath)]
        # Read the actual map schema, which may label paths old/new.
        if not candidates:
            candidates=[r for r in relocation if list(r.values())[0]=='original_research_archive/legacy/'+str(oldpath)]
        if candidates:
            candidate=candidates[0];values=list(candidate.values());newpath=values[1]
            assert (ROOT/newpath).is_file()
            actual=sha(ROOT/newpath)
            assert actual==values[4]
            row[ix]=newpath;relocations.append({'old':oldpath,'new':newpath,'sha256':actual})
        else:raise AssertionError('Unresolved NPP provenance: '+str(oldpath))
    set_setting(b,'production_eligible',True)
    set_setting(b,'source_note','User-selected native Falkland shelf model; audited derived B/EE completion; GE/TE/With Egestion WARN. PPR covers mapped catch only (2019 landings 64.41%); missing taxa remain missing. Source report is a frozen preselection audit; see selection_report.md for current status.')
    set_setting(b,'calculation_status','Selected native model calculated and validated; GE/TE/With Egestion WARN; partial catch coverage; central consolidation queued')
    b['Diagnostics']['Scientific review']=(['topic','finding','evidence'],[
      ['Selection','Exact user-selected ID retained; did not FAIL is not equivalent to OK','models/'+MID+'/selection_report.md'],
      ['Computational input','Coupled B/EE completion reproduces the audited diagnostics; no diet normalization or pooling','models/'+MID+'/selection_20260928/selection_provenance.json'],
      ['Native detritus boundary','Native fleet discards go to Detritus, not Discards; loader forces identity fate, EE=1, detritus accumulation; original source preserved','models/'+MID+'/source_report.md'],
      ['Mapping','29/250 taxa; 72.75% historical landings and 64.41% 2019 landings; no forced unsupported memberships','models/'+MID+'/selection_20260928/mapping_review.csv'],
      ['Time and geography','2020 Falkland shelf coefficients transferred to regional 1950–2019 covered catches; temporal and spatial representativeness uncertain','models/'+MID+'/selection_report.md'],
      ['NPP','Original values and missing years preserved; historical provenance paths resolve via archive relocation manifest','models/'+MID+'/selection_20260928/npp_provenance_links.json'],
    ])
    write_book(path,b);validate_region(read_book(path),path)
    (E/'npp_provenance_links.json').write_text(json.dumps(relocations,indent=2),encoding='utf-8')
    snapshot=E/'executed_code';snapshot.mkdir(exist_ok=True)
    sources=[* (ROOT/'tools/scientific_code/PPREstimation').glob('*.py'),*[ROOT/'tools'/n for n in ['run_region.py','regional.py','workbooks.py']],ROOT/'tools/scientific_helpers/ppr_scopes.py',MODEL/'run_selected_sppr.py',MODEL/'prepare_catch_mapping.py',Path(__file__)]
    hashes=[]
    for p in sources:
        target=snapshot/p.name;shutil.copy2(p,target);hashes.append({'path':p.relative_to(ROOT).as_posix(),'snapshot':target.relative_to(MODEL).as_posix(),'sha256':sha(p)})
    audit={'selected_model_id':MID,'regional_workbook_sha256':sha(path),'canonical_source_sha256':sha(MODEL/'model.json'),'computational_input_sha256':sha(computational),'source_files_unchanged':unchanged,'original_catch_classic_taxa_npp_values_unchanged':True,'audited_loader_numeric_cells_reproduced':len(old)*len(numeric),'all_source_groups_nonnegative':True,'diagnostics':health,'taxon_coefficient_checks':len(coeff),'annual_cell_checks':checked,'ratio_cell_checks':ratio_checks,'npp_provenance_links_resolved':len(relocations),'regional_validation':'PASS','central_writes':False,'python':platform.python_version(),'executed_code':hashes}
    (E/'selected_results_validation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k not in ['executed_code','source_files_unchanged']},indent=2))

if __name__=='__main__':main()
