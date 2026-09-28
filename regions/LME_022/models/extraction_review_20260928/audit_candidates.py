"""Independent source-to-database checks and diagnostic summaries."""
from extract_candidates import *
import math
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
MIDS=['22_20251890_East_Coast_of_Scotland_(1890-1895)','22_20251990_East_Coast_of_Scotland_(1991-1995)','22_20071991_North_Sea_report_Table_3.3_(1991)','457_457_North_Sea_(1991)']
def vals(ws):
    rr=list(ws.values);return [dict(zip(rr[0],r)) for r in rr[1:] if r[0] is not None]
allsummary=[]
for mid in MIDS:
    dest=REG/'models'/mid;et=dest/'extracted_tables';db=json.loads((dest/'model.json').read_text(encoding='utf-8'));byseq={g['group_seq']:g for g in db['group']}
    audit={'candidate_folder':mid,'group_count':len(byseq),'checks':[]}
    if et.exists():
        source=json.loads((et/'model.json').read_text(encoding='utf-8'));count=0;dietcount=0
        for g in source['groups']:
            out=byseq[str(g['n'])];assert g['name']==out['group_name']
            for f,d in [('biomass','biomass_habitat_area'),('pb','pb'),('qb','qb'),('ee','ee'),('unassim','gs')]:
                if f in g:assert math.isclose(float(g[f]),float(out[d]),rel_tol=1e-14,abs_tol=1e-14),(mid,g['n'],f,g[f],out[d]);count+=1
                elif f=='unassim':assert out['gs']=='-9999'
            assert out['biomass_accum']=='-9999' and out['biomass_accum_rate']=='-9999'
            assert out['taxon_descr']
            rawdiet=source['diet'].get(str(g['n']),{})
            entries=(out.get('diet_descr') or {}).get('diet',[])
            if isinstance(entries,dict):entries=[entries]
            outdiet={x['prey_seq']:float(x['proportion']) for x in entries}
            for prey,value in rawdiet.items():
                actual=float(out['diet_imp']) if prey=='import' else outdiet.get(prey,0)
                assert math.isclose(float(value),actual,rel_tol=1e-14,abs_tol=1e-14),(mid,g['n'],prey,value,actual);dietcount+=1
            expectedcatch=sum(float(v) for kind in ['landings','discards'] for v in source.get(kind,{}).get(str(g['n']),{}).values())
            assert math.isclose(expectedcatch,float(out['export']),rel_tol=1e-12,abs_tol=1e-12)
        roundtrip=next(et.glob('*_reconstructed.xlsx'));wr=openpyxl.load_workbook(roundtrip,data_only=True,read_only=True)
        audit['roundtrip_sheets']=wr.sheetnames
        rebuilt={str(r[0]):r for r in list(wr['Basic input'].values)[1:]}
        roundtrip_cells=0
        for seq,g in byseq.items():
            r=rebuilt[seq];assert r[1]==g['group_name']
            for col,key in [(2,'habitat_area'),(3,'biomass_habitat_area'),(4,'pb'),(5,'qb'),(6,'ee'),(8,'gs')]:
                v=float(g[key])
                if v==-9999:assert r[col] is None
                else:assert math.isclose(float(r[col]),v,rel_tol=1e-13,abs_tol=1e-13),(mid,seq,key,r[col],v)
                roundtrip_cells+=1
        dr=list(wr['Diet composition'].values);heads=dr[0];dd={str(r[0]):r for r in dr[1:]}
        for seq,g in byseq.items():
            col=heads.index(seq);entries=(g.get('diet_descr') or {}).get('diet',[])
            if isinstance(entries,dict):entries=[entries]
            expected={str(x['prey_seq']):float(x['proportion']) for x in entries}
            for prey in byseq:
                assert math.isclose(float(dd[prey][col] or 0),expected.get(prey,0),rel_tol=1e-13,abs_tol=1e-13),(mid,seq,prey)
                roundtrip_cells+=1
        audit['roundtrip_core_and_diet_cells_verified']=roundtrip_cells
        wr.close()
        audit['checks']=[f'{count} printed core values matched database JSON',f'{dietcount} source diet slots including zeros/import matched without normalization','All group names, source BA unknowns and taxonomy carried through','All database exports equal retained fleet landings plus discards','Eight import tables and database round-trip workbook retained']
        audit['known_conversion_conventions']=['Blank habitat fraction becomes1 in converter; source CSV remains blank','Blank diet/import/catch becomes0 in converter representation; source CSV distinguishes blank and zero','Printed rounded P/Q retained in source basic-input CSV; converter GE=-9999 so engine derives PB/QB','Only diagnostic loader normalizes diets and supplies missing defaults/flow completion; not a source correction']
        strict_path=next(p for p in et.glob('*.json') if p.name!='model.json')
    else:
        src=REG/'papers/LME022-Mackinson-2007/EcoBase_457_original.json';orig=json.loads(src.read_text())
        assert all({k:v for k,v in a.items() if k!='taxon_descr'}=={k:v for k,v in b.items() if k!='taxon_descr'} for a,b in zip(orig['group'],db['group']))
        audit['checks']=['All original repository numerical fields unchanged; only taxon_descr attached by exact group_seq']
        strict_path=dest/'457_457_North_Sea_(1991).json';shutil.copy2(dest/'model.json',strict_path)
    try:
        md=ModelData(str(strict_path));ModelData.validate_DC(md.DC,md.groups_data,normalize=False,tol=.001);audit['strict_diet_admission']='PASS'
    except Exception as e:audit['strict_diet_admission']='FAIL: '+str(e)
    if not et.exists():strict_path.unlink()
    sp=dest/'sppr_source.xlsx'
    if sp.exists():
        w=openpyxl.load_workbook(sp,read_only=True,data_only=True);health=vals(w['model_health']);mc=vals(w['mc_diagnostics']);gg=vals(w['groups_df']);ss=vals(w['sppr_all']);notes=vals(w['run_notes'])
        catch={g['group_name']:g['catch'] for g in gg};negative={}
        for r in ss:
            for k,v in r.items():
                if k not in ['seq','group_name'] and isinstance(v,(int,float)) and v<0:
                    negative.setdefault(k,[]).append({'group':r['group_name'],'sppr':v,'catch':catch.get(r['group_name'])})
        summary={'candidate_folder':mid,'model_json_sha256':hashlib.sha256((dest/'model.json').read_bytes()).hexdigest(),'source_admission':audit['strict_diet_admission'],'config':{'method_timeout_seconds':180,'mc_samples':100,'underdetermined':True,'zero_biomass_accum':False,'normalize_DC':True,'DC_tol':.001,'det_collapse_mode':'never','det_external_sppr':0,'det_open_mode':'none','det_theta':1},'health':health,'mc':mc,'negative_group_totals_all_scope':negative,'run_notes':notes,'limitations':['Diagnostic calculations are conditional on loader defaults/normalization/completed unknown flows','No catch matching or annual regional PPR performed; footprint rows are model-internal diagnostics, not LME annual results','No production model selected']}
        dump(dest/'SPPR_DIAGNOSTICS.json',summary);allsummary.append(summary)
        csvout(dest/'loaded_groups.csv',list(gg[0]),[list(r.values()) for r in gg])
        changes=[]
        for g in gg:
            raw=byseq.get(str(g['seq']))
            if raw is None:continue
            for key,outkey in [('biomass','biomass'),('pb','pb'),('qb','qb'),('ee','ee'),('gs','gs'),('biomass_accum','biomass_accum'),('export','catch')]:
                a=raw.get(key);b=g.get(outkey)
                if a is not None and b is not None and (float(a)==-9999 or not math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-12)):
                    changes.append([g['seq'],g['group_name'],key,a,b,'loader-derived/defaulted; not paper statement'])
        csvout(dest/'LOADER_TRANSFORMATIONS.csv',['seq','group','field','source_json','loaded_value','authority'],changes)
        w.close()
    dump(dest/'EXTRACTION_AUDIT.json',audit)
    print(mid,audit['strict_diet_admission'][:60], 'SPPR retained' if sp.exists() else 'SPPR pending')
dump(OUT/'DIAGNOSTICS_SUMMARY.json',allsummary)
# Compare exact paper reconstruction to separately attributed repository values.
paper=json.loads((REG/'models/22_20071991_North_Sea_report_Table_3.3_(1991)/model.json').read_text(encoding='utf-8'))
repo=json.loads((REG/'models/457_457_North_Sea_(1991)/model.json').read_text(encoding='utf-8'));rseq={g['group_seq']:g for g in repo['group']}
comparisons=[]
for p in paper['group']:
    r=rseq[p['group_seq']]
    for field in ['biomass','pb','qb','ee','gs','biomass_accum','export']:
        if float(p[field])!=float(r[field]):comparisons.append([p['group_seq'],p['group_name'],field,p[field],r[field]])
csvout(OUT/'paper_vs_ecobase457.csv',['seq','paper_group','field','printed_report_json','repository457'],comparisons)
