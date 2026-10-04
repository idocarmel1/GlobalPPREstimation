"""Bounded candidate inventory cleanup. Preserve selected science and researcher decisions."""
from pathlib import Path
import copy,hashlib,json,re,shutil,sys,zipfile
from xml.etree import ElementTree as E
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];REGION=ROOT/'regions/LME_027'
sys.path.insert(0,str(ROOT/'tools'))
from researcher_review import table_rows,sheet_xml,column,S
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
base=HERE/'baseline';base.mkdir(exist_ok=True)
project=ROOT/'Project.xlsx';oldproject=base/'Project_before_inventory.xlsx'
assert not oldproject.exists(),'One-shot mutation already started; inspect evidence before retry.'
shutil.copy2(project,oldproject)
changes={};before_records={};after_records={};removed_rows=0;updated_variants=[]
oldids={'27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991)',*[f'27_Canary_Current_27_{i}_Banc_d_Arguin_and_Mauritanian_Shelf_(1991)' for i in (1,2,3)]}
geo='Approximate overlap A ≈3% of Canary Current LME (2.5–3.5%); B ≈95–100% of study area. Source Figure1 trace and area33224km²; legacy9% unsupported. See candidate validation evidence.'
def update_row(row,headers,values):
    r=row.get('r');cells={c.get('r'):c for c in row}
    for field,value in values.items():
        address=column(headers.index(field)+1)+r;c=cells.get(address)
        if c is None:c=E.SubElement(row,'{'+S+'}c',{'r':address})
        style=c.get('s');c.clear();c.set('r',address)
        if style:c.set('s',style)
        if value is None:continue
        if isinstance(value,bool):c.set('t','b');E.SubElement(c,'{'+S+'}v').text=str(int(value))
        elif isinstance(value,(int,float)):c.set('t','n');E.SubElement(c,'{'+S+'}v').text=str(value)
        else:c.set('t','inlineStr');E.SubElement(E.SubElement(c,'{'+S+'}is'),'{'+S+'}t').text=str(value)
    row[:]=sorted(row,key=lambda c:__import__('researcher_review').column_index(c.get('r')))
with zipfile.ZipFile(project) as z:
    for sheet,table in [('Models & coverage','Models'),('Papers','Papers')]:
        target,_=sheet_xml(z,sheet);tree,headers,_,rows=table_rows(z,sheet,table)
        before_records[sheet]=[d for r,d in rows]
        if sheet=='Models & coverage':
            for row,d in rows:
                if d.get('model_id')=='27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991)':tree.find('{'+S+'}sheetData').remove(row);removed_rows+=1
                elif d.get('unit_id')=='LME_027' and d.get('variant') in ('Base','M30','P30') and 'Banc_d_Arguin' in d.get('model_id',''):
                    variant=d['variant'];updated_variants.append(variant);mid=f'Guenette2014_BancArguin_{variant}_1991';doc=REGION/f'Model_validation_{mid}.docx'
                    assert doc.exists()
                    availability=('Source-faithful extraction complete; source diet admission rejected. Separate P/Q approximation returns FAIL for GE, TE and With Egestion; provisional candidate arithmetic only.' if variant=='Base' else 'Source-faithful extraction complete; 114 unpublished variant diet cells in14consumers prevent independent GE/TE/With Egestion and regional model PPR.')
                    update_row(row,headers,dict(model_id=mid,model_path=f'regions/LME_027/models/{mid}/model.json',source_filename='model.json',selected=False,selection_rationale='Independent 2026-10-03 candidate assessment; not production eligible. No selection adoption. Existing1987selection and researcher disqualification preserved.',paper_ids='CAN-2014__LME_027',model_year=1991,variant=variant,model_area_km2=33224,availability=availability,publication_year=2014,model_years='1991 Ecopath; source Ecosim1991–2006',target_coverage_ratio=None,coverage_class='partial',doi='10.1371/journal.pone.0094742',coverage_note=geo,validation_report_path=doc.relative_to(ROOT).as_posix(),validation_report_sha256=sha(doc)))
        else:
            for row,d in rows:
                if d.get('article_id')!='CAN-2014__LME_027':continue
                updates=dict(functional_groups=51,target_coverage_ratio=None,geometry_method='Approximate georeferenced Figure1 trace, marine land exclusion, and reported-area crosscheck',geometry_confidence='approximate; uncertainty retained',full_model_loadable='Base source rejected at diet admission; M30/P30 incomplete diets. Distinct EcoBase689 companion recovered; all three direct methods FAIL on assessed experiments.',loadability_class='Extracted candidates; production ineligible',quality_rationale='Legacy numeric quality score superseded by complete2026-10-03 candidate assessment; no new aggregate score assigned.',extraction_readiness='source extraction complete; numerical restrictions documented',model_file_status='distinct authoritative EcoBase689 companion recovered',recommendation='Retain three1991source-faithful variants as assessed candidates. Resolve source/native diet and stanza conflicts before reconsidering selection.',geometry_note=geo,coverage_note=geo,loadability_evidence='regions/LME_027/validation_reports/BancArguin_20261003/evidence_index.json',documentation_evidence='regions/LME_027/papers/CAN-2014/extracted/MASTER_INDEX.md',notes='Base/M30/P30 assessed independently;512catchlabels each. No regional selection or selected-model result replacement.',correction_notes=(d.get('correction_notes') or '')+' 2026-10-03: consolidated duplicate Base; source diets/fields restored; legacy9%coverage withdrawn. Authoritative EcoBase689 differs from published variants.',provenance='Original catalog claims retained in baseline; current candidate assessment2026-10-03 supersedes loadability/coverage claims.')
                for f in ['model_loadability_score_55','documentation_score_20','spatial_fit_score_15','recency_validation_score_10','quality_score_cap','quality_score_100']:updates[f]=None
                update_row(row,headers,updates)
        changes[target]=E.tostring(tree,encoding='utf-8',xml_declaration=True)
    assert removed_rows==1 and sorted(updated_variants)==['Base','M30','P30']
    tmp=project.with_suffix('.inventory.tmp.xlsx')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as out:
        for info in z.infolist():out.writestr(info,changes.get(info.filename,z.read(info.filename)))
with zipfile.ZipFile(oldproject) as old,zipfile.ZipFile(tmp) as new:
    diff=[n for n in old.namelist() if old.read(n)!=new.read(n)]
    assert set(diff)==set(changes)
    for sheet,table in [('Models & coverage','Models'),('Papers','Papers')]:
        rows=table_rows(new,sheet,table)[3];after_records[sheet]=[d for r,d in rows]
    before1987=next(x for x in before_records['Models & coverage'] if x['model_id']=='27_118_Northwest_Africa_(1987)')
    after1987=next(x for x in after_records['Models & coverage'] if x['model_id']==before1987['model_id'])
    assert before1987==after1987
    for sheet,key in [('Models & coverage','model_id'),('Papers','article_id')]:
        a={x[key]:x for x in before_records[sheet] if (x.get(key,'') not in oldids if key=='model_id' else x[key]!='CAN-2014__LME_027')}
        b={x[key]:x for x in after_records[sheet] if (not x.get(key,'').startswith('Guenette2014_BancArguin_') if key=='model_id' else x[key]!='CAN-2014__LME_027')}
        assert a==b,(sheet,'unrelated record changed')
tmp.replace(project)
save(base/'inventory_before.json',before_records);save(HERE/'inventory_after.json',after_records)
# Paper-local catalog is current metadata, not an original publication.
paper=REGION/'papers/CAN-2014'
for name in ('metadata.json','README.md'):shutil.copy2(paper/name,base/('CAN-2014_'+name))
meta=json.loads((paper/'metadata.json').read_text(encoding='utf-8'))
newpaper=next(d for d in after_records['Papers'] if d['article_id']=='CAN-2014__LME_027')
catalog_fields=('title','authors','model_years','functional_groups','target_coverage_ratio','geometry_method','geometry_confidence','full_model_loadable','loadability_class','quality_rationale','quality_score_100','model_loadability_score_55','documentation_score_20','spatial_fit_score_15','recency_validation_score_10','quality_score_cap','extraction_readiness','recommendation','geometry_note','coverage_note','model_file_status','correction_notes','provenance','article_dir','loadability_evidence','documentation_evidence','notes')
for k in catalog_fields:meta[k]=newpaper[k]
for record in meta.get('material_files',[]):
    if record.get('local_filename'):record['relative_path']='regions/LME_027/papers/CAN-2014/'+record['local_filename']
meta['assessment_index']='../../validation_reports/BancArguin_20261003/evidence_index.json'
save(paper/'metadata.json',meta)
oldtext=(paper/'README.md').read_text(encoding='utf-8');sources=oldtext[oldtext.index('## Source files'):]
(paper/'README.md').write_text('# Banc d’Arguin and Mauritanian Shelf — Guénette, Meissa and Gascuel(2014)\n\nDOI: https://doi.org/10.1371/journal.pone.0094742\n\nThree1991parameterizations have been re-extracted and independently assessed. Base source admission is rejected; its separate runtime approximation fails all direct methods. M30/P30 retain114unpublished diet cells each and have no independent SPPR/PPR. All are currently ineligible for production.\n\nApproximate overlap: A≈3%of LME; B≈95–100%of study area. The former9%claim is unsupported. Ecosim1991–2006does not establish applicability to all regional catch years.\n\n[Current extraction and validation index](extracted/MASTER_INDEX.md) · [Assessment evidence](../../validation_reports/BancArguin_20261003/evidence_index.json) · [Superseded catalog](../../validation_reports/BancArguin_20261003/baseline/CAN-2014_README.md)\n\n'+sources,encoding='utf-8')
# Remove only the obsolete embedded candidate, retaining selected-model object and all numeric payloads.
mapcheck={}
for name,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
    p=ROOT/'interactive_map'/name;t=p.read_text(encoding='utf-8');i=t.index('const '+var+'=')+len('const '+var+'=');d,end=json.JSONDecoder().raw_decode(t,i);before=copy.deepcopy(d)
    u=d['network']['units']['LME_027'] if var=='DB' else d['units']['LME_027'];bu=copy.deepcopy(u)
    oldid='27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991)';removed=[m for m in u['models'] if m['id']==oldid]
    save(base/(name+'_removed_candidate.json'),removed)
    selected_id=u['models'][u['default_model']]['id'] if isinstance(u['default_model'],int) else u['default_model']
    u['models']=[m for m in u['models'] if m['id']!=oldid]
    if isinstance(u['default_model'],int):u['default_model']=next(k for k,m in enumerate(u['models']) if m['id']==selected_id)
    assert next(m for m in bu['models'] if m['id']==selected_id)==next(m for m in u['models'] if m['id']==selected_id)
    old_article=None
    if var=='DB':
        article=next(a for a in d['articles'] if a.get('article_id')=='CAN-2014__LME_027');old_article=copy.deepcopy(article)
        save(base/'map_CAN-2014_article_before.json',old_article)
        for k in catalog_fields:article[k]=newpaper[k]
        article['functional_groups']=51
        article['geometry']=json.loads((HERE/'context/study_area_figure_trace.geojson').read_text(encoding='utf-8'))['geometry']
        article['geometry_method']='Approximate source Figure1 trace, georeferenced and land-excluded; not an author-supplied polygon'
    restored=copy.deepcopy(d);ru=restored['network']['units']['LME_027'] if var=='DB' else restored['units']['LME_027'];ru.clear();ru.update(bu)
    if old_article is not None:
        ra=next(a for a in restored['articles'] if a.get('article_id')=='CAN-2014__LME_027');ra.clear();ra.update(old_article)
    assert restored==before,'Unexpected payload changes'
    payload=json.dumps(d,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('</',r'<\/')
    updated=t[:i]+payload+t[end:]
    updated=re.sub(r'(<meta name="ppr-project-sha256" content=")[0-9a-f]{64}(">)',lambda m:m.group(1)+sha(project)+m.group(2),updated)
    p.write_text(updated,encoding='utf-8',newline='\n')
    mapcheck[name]={'removed_candidate_ids':[m['id'] for m in removed],'selected_id':selected_id,'selected_object_unchanged':True,'CAN2014_article_metadata_updated':old_article is not None,'all_other_payload_values_unchanged':True,'sha256':sha(p)}
save(HERE/'inventory_reconciliation.json',{'changed_project_parts':diff,'all_other_project_parts_byte_identical':True,'researcher1987record_unchanged':True,'before_project_sha256':sha(oldproject),'after_project_sha256':sha(project),'map_cleanup':mapcheck,'selection_adopted':False,'catalog_changes':['CAN-2014/README.md','CAN-2014/metadata.json'],'source_publications_unchanged':True})
print('Candidate inventory reconciled; selected science and researcher1987record preserved.')
