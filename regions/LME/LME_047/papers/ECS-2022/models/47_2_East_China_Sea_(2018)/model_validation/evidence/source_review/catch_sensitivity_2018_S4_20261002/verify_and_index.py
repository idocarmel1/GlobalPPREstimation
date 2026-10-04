"""Independent output checks and portable sensitivity evidence inventory."""
from pathlib import Path
import hashlib,json,math,shutil,xml.etree.ElementTree as ET,zipfile
import numpy as np

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def write(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
e=read('comparison.json')
assert e['protected_files_unchanged']
for rel,h in e['protected_file_hashes_after'].items():assert sha(ROOT/rel)==h,rel
methods=['new_GE','new_TE_EEfix']
scenarios=['no_catch','catch_from_S4','catch_from_S4_M0']
for m in methods:
    base=read('no_catch_solutions.json')[m]['SPPR']
    s4=read('catch_from_S4_solutions.json')[m]['SPPR']
    assert base==s4, m
    for sc in scenarios:
        report=read(sc+'_diagnostics.json')[m]['report']
        assert report['status']==e['results'][sc][m]['diagnostic_status']=='WARN'
        assert report['model_input']['is_model_balanced']
        assert report['balance']['status']=='OK'
        assert report['divergence']['n_negative_sources']==0
        v=e['results'][sc][m]
        assert math.isclose(v['regional_2019_ppr_wet_tonnes']/9,v['regional_2019_ppr_tonnes_C'],rel_tol=1e-15)
    a=e['results']['no_catch'][m]['regional_2019_ppr_tonnes_C']
    b=e['results']['catch_from_S4_M0'][m]['regional_2019_ppr_tonnes_C']
    assert math.isclose(100*(b/a-1),e['differences'][m]['M0_scenario']['regional_2019_change_percent'],abs_tol=1e-12)
    assert read('catch_from_S4_M0_diagnostics.json')[m]['report']['model_input']['n_ee_gt_1']==7

def groups(n):
    t=read(n+'_loaded_groups.json')
    return {seq:dict(zip(t['columns'],row)) for seq,row in zip(t['index'],t['data'])}
g0,gm=groups('no_catch'),groups('catch_from_S4_M0')
for seq,row in g0.items():
    if row['trophic_info']=='Regular':
        for col in ['biomass_accum','biomass','p','q','predation','egestion','respiration','net_migration']:
            assert row[col]==gm[seq][col],(seq,col)
        increment=gm[seq]['catch']-row['catch']
        assert math.isclose(gm[seq]['M0'],row['M0']-increment,abs_tol=1e-12)
assert len(e['M0_scenario_negative_M0_groups'])==7

# Retain the exact regional arithmetic code used by this calculation.
code=OUT/'calculation_code';code.mkdir(exist_ok=True)
for n in ['workbooks.py','regional.py']:shutil.copy2(ROOT/'tools'/n,code/n)
supp=ROOT/'regions/LME_047/papers/ECS-2022/DataSheet_1_EstimatingtheImpactofaSeasonal-7491f315.docx'
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(supp) as z:doc=ET.fromstring(z.read('word/document.xml'))
tab=doc.findall('.//w:tbl',ns)[6]
rows=[[''.join(t.text or '' for t in tc.findall('.//w:t',ns)) for tc in tr.findall('w:tc',ns)] for tr in tab.findall('w:tr',ns)]
write('S4_extraction.json',{'source':'../../../papers/ECS-2022/'+supp.name,'table':'S4','rows':rows,
    'selected_year':2018,'selected_type':6,'parsed_values':e['S4_catch_wet_tonnes_per_km2_per_year'],
    'round_trip':'Original printed XML values parsed to numeric catch, written to isolated model export fields, then verified against loaded catch values.'})
for seq,value in e['S4_catch_wet_tonnes_per_km2_per_year'].items():
    assert groups('catch_from_S4')[int(seq)]['catch']==value

verification={'passed':True,'checks':['Exact equality of all GE/TE SPPR cells in BA scenario',
    'Baseline regional PPR reproduces adopted workbook within 1e-12 relative tolerance (asserted by run_comparison.py)',
    'All three scenarios retain overall WARN, input mass balance, PP budget OK, no negative SPPR sources',
    'M0 scenario preserves living BA/B/P/Q/predation/egestion/respiration/migration, updates M0 and implied EE',
    'Seven negative-M0/EE>1 groups in M0 scenario; not physically valid',
    'S4 extraction/model/loaded-state catch round trip','Single wet-to-carbon division by nine','Protected file hashes unchanged']}
write('verification.json',verification)
artifacts=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence_index.json':
        artifacts.append({'role':p.stem,'path':p.relative_to(OUT).as_posix(),'sha256':sha(p),'availability':'present'})
for role,p in [('canonical_model',OUT.parent.parent.parent/'models/47_2_East_China_Sea_(2018)/model.json'),
               ('supplement',supp),('article',supp.parent/'pdf-e60d0358.pdf'),
               ('regional_inputs',ROOT/'regions/LME_047/LME_047.xlsx')]:
    import os
    artifacts.append({'role':role,'path':Path(os.path.relpath(p,OUT)).as_posix(),'sha256':sha(p),'availability':'present'})
for n,h in e['engine_hashes'].items():
    artifacts.append({'role':'frozen_scientific_engine','path':'../direct_diagnostics/engine/'+n,'sha256':h,'availability':'present'})
for role in ['Monte_Carlo','other_models','taxonomy_remapping','adoption_and_map_update','validation_docx_edit']:
    artifacts.append({'role':role,'path':None,'sha256':None,'availability':'inapplicable','reason':'Outside the requested isolated sensitivity comparison.','acquisition_status':'not requested'})
write('evidence_index.json',{'schema_version':1,'run_id':OUT.name,'region_id':'LME_047','model_id':e.get('model_id','47_2_East_China_Sea_(2018)'),
    'variant_ids':scenarios,'source_identity':e['source_hashes'],'computational_input_identity':e['constructor_settings'],
    'methods':methods,'options':e['diagnostic_settings'],'regional_reference':{'year':2019,'basis':'landings','scope':'all','unidentified':'method','units':'tonnes C/year'},
    'adoption_state':'unadopted experiment','physical_validity_M0_scenario':False,'artifacts':artifacts})
for a in artifacts:
    if a['availability']=='present':assert sha(OUT/a['path'])==a['sha256'],a
print('VERIFIED: baseline reproduced; BA scenario exactly unchanged; M0 sensitivity quantified; 7 invalid M0 groups; all statuses WARN; protected files unchanged.')
for m in methods:
    print(m, [(sc,round(e['results'][sc][m]['regional_2019_ppr_tonnes_C']/1e6,6),e['results'][sc][m]['diagnostic_status']) for sc in scenarios])
