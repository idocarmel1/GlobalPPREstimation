"""Keep canonical catalog geometry and future map rebuilds consistent with the assessment."""
from pathlib import Path
import ast,copy,gzip,hashlib,json,re,shutil,sys,zipfile
from xml.etree import ElementTree as E
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from researcher_review import table_rows,sheet_xml,S
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
project=ROOT/'Project.xlsx';feature=load(HERE/'context/study_area_figure_trace.geojson');value=json.dumps(feature['geometry'],separators=(',',':'))
assert len(value)<28000
with zipfile.ZipFile(project) as z:
    target,_=sheet_xml(z,'Map geography');tree,headers,_,rows=table_rows(z,'Map geography','Geometry')
    candidates=[(r,d) for r,d in rows if d['geometry_id']=='article:CAN-2014__LME_027'];assert len(candidates)==1
    row,old=candidates[0];assert old['part']=='0';save(HERE/'baseline/CAN-2014_Project_geometry.json',old)
    cell=row.find('{'+S+'}c[@r="C'+row.get('r')+'"]');assert cell is not None
    v=cell.find('.//{'+S+'}t');assert v is not None;v.text=value
    replacement=E.tostring(tree,encoding='utf-8',xml_declaration=True);tmp=project.with_suffix('.geometry.tmp.xlsx')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as out:
        for info in z.infolist():out.writestr(info,replacement if info.filename==target else z.read(info.filename))
tmp.replace(project)
paper=ROOT/'regions/LME_027/papers/CAN-2014';shutil.copy2(paper/'footprint.geojson',HERE/'baseline/CAN-2014_footprint.geojson');shutil.copy2(HERE/'context/study_area_figure_trace.geojson',paper/'footprint.geojson')
with zipfile.ZipFile(HERE/'baseline/Project_before_inventory.xlsx') as old,zipfile.ZipFile(project) as new:
    diff=[n for n in old.namelist() if old.read(n)!=new.read(n)]
    assert set(diff)=={'xl/worksheets/sheet2.xml','xl/worksheets/sheet3.xml','xl/worksheets/sheet8.xml'}
    a={d['geometry_id']:d for _,d in table_rows(old,'Map geography','Geometry')[3] if d['geometry_id']!='article:CAN-2014__LME_027'}
    b={d['geometry_id']:d for _,d in table_rows(new,'Map geography','Geometry')[3] if d['geometry_id']!='article:CAN-2014__LME_027'}
    assert a==b
    registered={(d['unit_id'],d['model_id']) for _,d in table_rows(new,'Models & coverage','Models')[3]}
reconciliation=load(HERE/'inventory_reconciliation.json');reconciliation['changed_project_parts']=diff;reconciliation['after_project_sha256']=sha(project);reconciliation['all_other_geography_records_unchanged']=True
for name in ('index.html','trends.html'):
    p=ROOT/'interactive_map'/name;t=p.read_text(encoding='utf-8');before=t
    t=re.sub(r'(<meta name="ppr-project-sha256" content=")[0-9a-f]{64}(">)',lambda m:m.group(1)+sha(project)+m.group(2),t)
    p.write_text(t,encoding='utf-8',newline='\n');reconciliation['map_cleanup'][name]['sha256']=sha(p)
reconciliation['catalog_changes'].append('CAN-2014/footprint.geojson');save(HERE/'inventory_reconciliation.json',reconciliation)
# The same inventory filter added to datasets changes only the obsolete candidate.
checks=[]
for name in ('catalog','time_series'):
    with gzip.open(ROOT/f'common_reference_data/atlas_source_context/{name}.json.gz','rt',encoding='utf-8') as f:d=json.load(f)
    units=d['network']['units'] if name=='catalog' else d['units'];removed=[]
    for unit,payload in units.items():
        models=payload.get('models',[]);kept=[m for m in models if (unit,m['id']) in registered]
        removed += [(unit,m['id']) for m in models if m not in kept]
    assert removed==[('LME_027','27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991)')]
    checks.append({'source':name,'removed':removed,'all_other_model_objects_unchanged':True})
ast.parse((ROOT/'tools/original_atlas_data.py').read_text(encoding='utf-8'))
save(HERE/'qa/map_inventory_filter.json',{'passed':True,'checks':checks,'code_sha256':sha(ROOT/'tools/original_atlas_data.py')})
print('Bounded geography reconciliation and frozen-candidate filter checks passed.')
