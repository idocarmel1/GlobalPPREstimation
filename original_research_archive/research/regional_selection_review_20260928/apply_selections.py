"""Apply the user's top-25 selections through the regional workbook contract."""
from pathlib import Path
import copy, json, shutil, sys, math, zipfile
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
from workbooks import read_book, write_book, records, rows, overview, sha, digest_tables, validate_region
from regional import set_setting, set_result_hash
from run_region import prepare_selection
import update_project

CHOICES = {
 'LME_013': ('13_1_Chilean_Patagonia_(1980)', 'WARN', 'WARN', 'WARN',
  'User selected the available non-failing alternative after comparison with Northern Humboldt 1995-1998 (all three configurations FAIL). Chilean Patagonia 1980 has saved GE/TE/With Egestion WARN results. Geographic suitability for the Humboldt LME remains a limitation; selection does not establish spatial coverage.',
  'regions/LME_013/models/13_1_Chilean_Patagonia_(1980)/sppr_source.xlsx'),
 'LME_027': ('27_118_Northwest_Africa_(1987)', 'WARN', 'WARN', 'WARN',
  'User selected the available non-failing Northwest Africa 1987 alternative after comparison with Banc d Arguin/Mauritanian Shelf 1991 (all three configurations FAIL). Saved GE/TE/With Egestion diagnostics are WARN. Regional matching and annual results must be prepared for this selection.',
  'regions/LME_027/models/27_118_Northwest_Africa_(1987)/sppr_source.xlsx'),
 'LME_022': ('22_20251990_East_Coast_of_Scotland_(1991-1995)', 'OK', 'FAIL', 'OK',
  'User previously preferred this exact model because it has the least SPPR failures, and now authorized selecting models for all top-25 regions except LME_048 and EEZ_938. GE and With Egestion OK; TE FAIL. Documented normalization/completions remain conditional; regional integration pending. EcoBase 457 remains flagged for later flow-balance debugging.',
  'regions/LME_022/models/extraction_review_20260928/EXTRACTION_AND_SPPR_REPORT.md'),
 'LME_024': ('Hernvann_2020_Celtic_Sea_1985', 'FAIL (authorized adapter)', 'UNSUPPORTED (FAIL return)', 'FAIL (authorized adapter)',
  'Explicit user selection of the extracted failing Celtic Sea 1985 model. Canonical source JSON remains selected as the model record; it is blocked by rounded diets and missing routing. The separately authorized normalized-diet/fishery-return adapter runs GE and With Egestion but both FAIL; TE returns unsupported. Printed BA retained. The adapter is not encoded by the canonical JSON. No failed output is promoted to regional PPR.',
  'regions/LME_024/models/extraction_review_20260928/authorized_routing_experiment/REPORT.md'),
 'LME_026': ('Piroddi_2022_Mediterranean_1995', 'NOT_RUN', 'NOT_RUN', 'NOT_RUN',
  'Explicit user selection of the extracted Mediterranean 1995 model despite blocked calculation. Both Word and XLSX supplements used. Missing routing between Discards70 and Detritus71 prevents construction; GE/TE/With Egestion NOT_RUN. Conditional fin-whale catch/production conflict retained. No routing or biological repair authorized by this selection.',
  'regions/LME_026/models/Piroddi_2022_Mediterranean_1995/diagnostics/DIRECT_SPPR_REPORT.md'),
 'LME_029': ('BEN2020_Southern_Benguela_1978', 'FAIL', 'FAIL', 'FAIL',
  'Explicit user selection of the extracted Southern Benguela 1978 model despite GE/TE/With Egestion FAIL. Diagnostic P/Q completion is separate from canonical source values. Production residuals, Sardine BA/stanza interpretation and TE problems remain unresolved. Selection does not approve parameter corrections or failed annual PPR.',
  'regions/LME_029/models/BEN2020_Southern_Benguela_1978/diagnostics/DIRECT_SPPR_REPORT.md'),
 'LME_037': ('Bacalso2026_Visayan_Sea_1997_baseline', 'WARN (audited defaults)', 'WARN (audited defaults)', 'WARN (audited defaults)',
  'Selected under the user instruction to select all top-25 regions except LME_048 and EEZ_938. Available 1997 baseline reconstructed from verified 2023 diet/catch supplement lineage and matching 2026 parameter cells. GE/TE/With Egestion WARN only under documented runtime defaults and diet tolerance; source JSON preserved. Local Visayan Sea spatial suitability and exact production admission remain unresolved. The 2018 endpoint remains NOT_RUN and unselected.',
  'regions/LME_037/models/Bacalso2026_Visayan_Sea_1997_baseline/diagnostics/DIRECT_SPPR_REPORT.md'),
}

def same(x, y):
    if isinstance(x, (int,float)) and isinstance(y,(int,float)):
        return math.isclose(x,y,rel_tol=2e-15,abs_tol=1e-12)
    return x == y

if __name__ == '__main__':
    project = ROOT / 'Project.xlsx'
    initial = sha(project)
    backup = OUT / f'Project_before_{initial[:12]}.xlsx'
    shutil.copy2(project, backup)
    print('Reading current registry', flush=True)
    before = read_book(project)
    after = copy.deepcopy(before)
    decisions = []
    for uid, (mid,ge,te,eg,reason,evidence) in CHOICES.items():
        candidates = [r for r in records(before,'Models & coverage','Models') if r['unit_id']==uid and r['model_id']==mid]
        assert len(candidates)==1, (uid,mid)
        model = ROOT/candidates[0]['model_path']
        assert model.is_file() and (ROOT/evidence).is_file()
        model_hash=sha(model)
        path=ROOT/'regions'/uid/(uid+'.xlsx')
        book=read_book(path); old=copy.deepcopy(book); prev=overview(book)
        set_setting(book,'selected_model_id',mid)
        set_setting(book,'model_path',model.relative_to(path.parent).as_posix())
        set_setting(book,'selection_rationale',reason)
        prepare_selection(book,path)
        status = ('selected by user; source construction blocked; GE/TE/With Egestion NOT_RUN' if uid=='LME_026' else
                  'selected by user; conditional GE/Egestion FAIL; TE unsupported; regional PPR unavailable' if uid=='LME_024' else
                  'selected by user; GE/TE/With Egestion FAIL; regional PPR unavailable' if uid=='LME_029' else
                  f'selected; retained diagnostics GE {ge}, TE {te}, With Egestion {eg}; regional matching and model PPR pending')
        set_setting(book,'calculation_status',status)
        set_setting(book,'production_eligible',False)
        book['Diagnostics']['selection_review']=(['model_id','GE','TE','With Egestion','evidence','note'],[[mid,ge,te,eg,evidence,reason]])
        set_result_hash(book)
        write_book(path,book)
        check=read_book(path); validate_region(check,path)
        assert overview(check)['selected_model_id']==mid
        assert not rows(check,'PPR','Annual') and not rows(check,'Selected model groups','Group SPPR')
        for sheet in ['Catch','Classic PPR','NPP']:
            assert digest_tables(old[sheet])==digest_tables(check[sheet]),(uid,sheet)
        assert sha(model)==model_hash
        decisions.append({'unit_id':uid,'model_id':mid,'previous_model_id':prev.get('selected_model_id'),'model_path':model.relative_to(ROOT).as_posix(),'source_sha256':model_hash,'GE':ge,'TE':te,'With Egestion':eg,'rationale':reason,'evidence':evidence,'status':status})
        print(f'{uid}: selected and verified; previous results archived',flush=True)

    real_read=update_project.read_book; captured=[]
    update_project.read_book=lambda p: after if Path(p).resolve()==project.resolve() else real_read(p)
    update_project.write_book=lambda p,b:captured.append(b)
    update_project.update(ROOT,[ROOT/'regions'/u/(u+'.xlsx') for u in CHOICES])
    assert len(captured)==1;after=captured[0]
    # Preserve all unrelated metadata, including deliberately retained candidate preferences.
    for sheet,table,key in [('Papers','Papers','article_id'),('Models & coverage','Models','model_id')]:
        oldrows={(r['unit_id'],r[key]):r for r in records(before,sheet,table)}
        h,rr=after[sheet][table]
        for row in rr:
            d=dict(zip(h,row));old=oldrows[(d['unit_id'],d[key])]
            if d['unit_id'] not in CHOICES:
                for k,v in old.items():row[h.index(k)]=v
            elif sheet=='Models & coverage' and not d.get('selected'):
                row[h.index('selection_rationale')]=old.get('selection_rationale')
    h,rr=after['Models & coverage']['Models']
    for dec in decisions:
        row=next(r for r in rr if r[h.index('unit_id')]==dec['unit_id'] and r[h.index('model_id')]==dec['model_id'])
        row[h.index('availability')]=dec['status']+'; evidence: '+dec['evidence']
    # Retain historical paper notes, appending the new decision instead of erasing provenance.
    ph,pr=after['Papers']['Papers']
    for d in decisions:
        model=next(r for r in records(after,'Models & coverage','Models') if r['unit_id']==d['unit_id'] and r['model_id']==d['model_id'])
        aids=set(str(model.get('paper_ids') or '').split(';'))
        for row in pr:
            if row[ph.index('unit_id')]==d['unit_id'] and row[ph.index('article_id')] in aids:
                note=str(row[ph.index('notes')] or '')
                row[ph.index('notes')]=note+'\n[2026-09-28 user selection update] '+d['rationale']
    assert sha(project)==initial,'Registry changed concurrently'
    print('Writing consolidated registry',flush=True)
    write_book(project,after)
    print('Verifying registry readback',flush=True)
    check=read_book(project)
    for sheet,blocks in before.items():
        for table,(h,_) in blocks.items():
            if 'unit_id' not in h:continue
            a=[r for r in records(before,sheet,table) if r.get('unit_id') not in CHOICES]
            b=[r for r in records(check,sheet,table) if r.get('unit_id') not in CHOICES]
            a.sort(key=lambda r:json.dumps({str(k):v for k,v in r.items()},sort_keys=True,default=str))
            b.sort(key=lambda r:json.dumps({str(k):v for k,v in r.items()},sort_keys=True,default=str))
            assert len(a)==len(b),(sheet,table)
            assert all(all(same(v,y.get(k)) for k,v in x.items()) for x,y in zip(a,b)),(sheet,table)
    top=sorted([r for r in records(check,'Regions & status','Regions') if isinstance(r.get('atlas_region_rank'),(int,float)) and r['atlas_region_rank']<=25],key=lambda r:r['atlas_region_rank'])
    assert len(top)==25
    assert {r['unit_id'] for r in top if not r.get('selected_model_id')}=={'LME_048','EEZ_938'}
    for r in top:
        selected=[m for m in records(check,'Models & coverage','Models') if m['unit_id']==r['unit_id'] and m.get('selected')]
        assert len(selected)==int(bool(r.get('selected_model_id'))),r['unit_id']
        if selected:
            assert selected[0]['model_id']==r['selected_model_id']
            assert (ROOT/selected[0]['model_path']).is_file()
    for d in decisions:
        r=next(r for r in top if r['unit_id']==d['unit_id'])
        assert r['selected_model_id']==d['model_id'] and r['sha256']==sha(ROOT/r['workbook'])
        assert sha(ROOT/d['model_path'])==d['source_sha256']
    with zipfile.ZipFile(project) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.startswith('xl/tables/') and n.endswith('.xml')])==13
    result={'status':'PASS','top25_count':25,'selected_count':23,'unselected':['LME_048','EEZ_938'],'central_sha256':sha(project),'decisions':decisions,'top25':top,'unrelated_records_preserved':True,'source_models_unchanged':True,'old_model_results_archived_and_cleared':True,'new_scientific_calculations':False}
    (OUT/'SELECTION_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','selected_count','unselected','central_sha256']},indent=2),flush=True)
