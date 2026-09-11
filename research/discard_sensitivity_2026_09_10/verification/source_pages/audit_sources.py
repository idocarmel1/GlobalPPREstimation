"""Read frozen evidence; write only source-audit-owned outputs. Run from repository root."""
from pathlib import Path
import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parents[2]
O = R / 'verification/source_pages'
I = R / 'inputs'
sys.path.insert(0, str(O / 'vendor'))
import xlrd

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def artifact(path, role):
    return {'path': path.relative_to(R).as_posix(), 'sha256': digest(path), 'bytes': path.stat().st_size, 'role': role}

regions = I / 'PPRAtlas/archive/regions'
specs = [
    ('13_2', 'Northern Humboldt Current', '1995–1998', 165000, 'LME_013/HUM-2018/1-s2.0-S0079661117303312-main.pdf', [3], 'source_supported_destination'),
    ('34_1', 'Bay of Bengal', '1978', 6205000, 'LME_034/LME034-Guenette-2013/009031359-84f3dc3d.pdf', [7,9,24,46], 'hypothetical_destination_only'),
    ('52_1', 'Sea of Okhotsk, NE model variant', '1980s (filename label: 1980)', 1590000, 'LME_052/OKH-2004/Palomares20_FishCentResaRep28-440d8aa8.pdf', [24,25,27], 'unavailable_nonzero_harvest'),
    ('28_646', 'Guinea offshore model', '1998', 111932, 'LME_028/GUI-2004/Palomares-et-al-west-africa-ecosystems-bd6604d6.pdf', [129,147,153,157], 'hypothetical_destination_only'),
]
models = []
for mid, name, period, area, paper, pages, sr in specs:
    path = next((I / 'PPREstimation/real_models/global_cover_jsons').glob(mid + '_*.json'))
    raw = json.loads(path.read_text(encoding='utf-8'))
    groups = raw['group']
    living = [g for g in groups if g['pp'] != '2']
    catch = sum(float(g['export']) for g in living if float(g['export']) >= 0)
    detritus = [{k:g.get(k) for k in ['group_seq','group_name','biomass','ee','detritus_import','export']} for g in groups if g['pp'] == '2']
    fates = []
    for g in groups:
        dd = g.get('diet_descr')
        ds = dd.get('diet', []) if isinstance(dd, dict) else []
        ds = [ds] if isinstance(ds, dict) else ds
        for d in ds:
            if float(d.get('detritus_fate', 0)) > 0:
                fates.append({'from_group_seq':int(g['group_seq']), 'to_group_seq':int(d['prey_seq']), 'fraction':float(d['detritus_fate'])})
    models.append({'model_id':mid,'name':name,'source_period':period,'source_area_km2':area,
      'native_units':{'biomass':'t wet biomass km-2','flows':'t wet biomass km-2 year-1','pb_qb':'year-1'},
      'group_count':len(groups),'caught_living_group_count':sum(float(g['export'])>0 for g in living),
      'frozen_living_harvest_sum':catch,'harvest_excludes_detritus_export':True,
      'source_supported_sr_status':sr,'files':[artifact(path,'frozen calculator model'),artifact(regions/paper,'publication')],
      'source_pdf_pages_one_based':pages,'frozen_detritus_groups':detritus,'frozen_biological_detritus_fates':fates,
      'frozen_return_note':'Biological detritus fate is not evidence of fleet discard fate. No explicit fishery-return field is consumed by the frozen loader.',
      'processing_offal_separate_flow':None})

h = regions/'LME_013/HUM-2018'
wb = xlrd.open_workbook(h/'Supplementary material revised and final.xls')
parity = []
for name in ['Table A-resolved parameters','Table B-resolved diet','Table C-resolved detritus fate']:
    sheet = wb.sheet_by_name(name)
    rows = json.loads((h/f'extracted/work/{name}.json').read_text(encoding='utf-8'))
    errors=[]
    for i,row in enumerate(rows):
        for c,v in enumerate(row):
            original = sheet.cell_value(i,c) if i<sheet.nrows and c<sheet.ncols else ''
            if original != ('' if v is None else v): errors.append([i+1,c+1,original,v])
    assert not errors, errors
    parity.append({'sheet':name,'cells_compared_including_blank_padding':sum(map(len,rows)),'mismatches':0})
hsheet=wb.sheet_by_name('Table A-resolved parameters')
landings=sum(float(hsheet.cell_value(row,col)) for row in range(5,44) for col in [8,9])
discards=sum(float(hsheet.cell_value(row,col)) for row in range(5,44) for col in [10,11])
hg=models[0]
hg.update({'source_landings':landings,'source_discards':discards,'source_discard_fraction_of_catch':discards/(landings+discards),
 'discard_evidence_status':'published model assumptions and precise supplement values, not direct observation of every flow',
 'source_fleet_return':[{'fleet':'Artisanal','to_group_seq':37,'fraction':1,'cell':'Table C-resolved detritus fate!D43'}, {'fleet':'Commercial','to_group_seq':37,'fraction':1,'cell':'Table C-resolved detritus fate!D44'}],
 'source_offal_onward_fate':{'pelagic_detritus':0.1,'benthic_detritus':0.9,'cells':'Table C!E40:F40'},
 'source_offal_direct_consumers':[], 'offal_diet_evidence':'Table B!B40:AN40 consists of zeros; Table A!H42 EE=0',
 'original_xls_parity':parity,
 'source_fidelity_caveats':[
   'Paper PDF3/printed30 says sardine landings reduced from5.65 to1.4; original supplement J14=5.6513425. Preserve frozen table-based H; do not silently repair.',
   'Original Table C fleet rows are43–44; frozen fleet sidecar source string incorrectly says44–45.',
   'Frozen rendered Table C PNG/PDF omits fleet rows. The original XLS cells, independently read, are authoritative.',
   'Anchovy eggs are represented by pp=2 in the calculator although publication counts them among living groups; preserve baseline convention.',
   'Table A biomass column carries a per-year label; biomass is a standing stock dimensionally. Catch/production flows are annual.',
   'No separate processing-offal quantity was recovered. The named Fishery offal compartment receives the documented fleet discard route; do not add a second offal subsidy.',
   'Frozen ModelData ignores fleet split fields and source_tables; explicit original fleet return is not restored by merely loading this JSON.'
 ]})
hg['files'] += [artifact(h/'Supplementary material revised and final.xls','original numeric supplement'),artifact(h/'extracted/13_2_Northern_Humboldt_Current_1995-1998/FLEET_DETRITUS_FATE.json','derived fleet sidecar; off-by-one locator caveat')]

# Spatial extraction of the 1998 half of printed Table16, visually checked against PDF157.
words=[(float(n.attrib['xMin']),float(n.attrib['yMin']),n.text) for n in ET.parse(O/'guinea-pdf-157-bbox.html').iter() if n.tag.endswith('word')]
anchors=sorted((int(t),y) for x,y,t in words if 89<x<100 and 131<y<472 and t.isdigit())
rows=[]
for seq,y in anchors:
    cells=[[],[],[],[]]; names=[]
    for x,yy,t in words:
        if abs(yy-y)<2:
            if 110<=x<190:names.append((x,t))
            if 375<=x<550:
                col=0 if x<411 else 1 if x<478 else 2 if x<515 else 3
                cells[col].append((x,t))
    texts=[' '.join(t for _,t in sorted(c)) for c in cells]
    values=[float(t) if t else None for t in texts]
    rows.append(dict(zip(['group_seq','group_name','landings_artisanal','landings_industrial','landings_total','discards_industrial','bbox_y'],[seq,' '.join(t for _,t in sorted(names)),*values,y])))
assert len(rows)==36
assert next(x for x in rows if x['group_seq']==16)['landings_industrial']==0.0403
assert next(x for x in rows if x['group_seq']==9)['landings_industrial']==0.0001
(O/'guinea-table16-1998-transcription.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
gu=models[3]
gu.update({'discard_evidence_status':'separate source-model assumptions published; not separate fields in frozen JSON',
 'source_discards':None,'source_discards_sum_of_nonblank_rounded_table16_cells':sum(x['discards_industrial'] for x in rows if x['discards_industrial'] is not None),
 'source_discard_fraction_of_catch':None,'source_table16_1998':rows,
 'published_split_note':'Visible published D cells sum0.090762 t/km2 in the1998 annual table. This is not a precision-matched full total; blank cells remain unknown/not printed. Do not infer exact original D by subtracting rounded L from precise JSON H.',
 'source_fleet_return':None,'source_fidelity_caveats':[
   'The proper source is Guenette & Diallo2004 Addendum printed124–159/PDF128–163, not the neighboring Guinea-Bissau or Gambia chapters.',
   'Printed149/PDF153: discard data were nearly absent; small-capitaine D estimated as30% of industrial landings, generalized to other commercial species. This is D/L, not D/(L+D). Artisanal discards assumed negligible.',
   'Additional noncommercial-group D assumptions are described; never apply30% uniformly to all H as an observed source fraction.',
   'No explicit fleet destination or return fraction recovered from the chapter. One generic detritus group and biological fate1 do not establish a fleet return of1.',
   'Raw detritus export1670.48071 is an ecosystem outflow, not catch; frozen loader zeros detritus catch.',
   'Area111932km2 in Table1, approximately112000 in prose, extends beyond Guinea EEZ. It is not the Guinea Current LME polygon.',
   'Printed Table16 units omit year;1998 annual model and rate definitions establish annual flows. Preserve original caption alongside interpretation.',
   'Authors flag underestimated illegal catches, uncertain shark/tuna biomass and catch, and incomplete discard composition. Model assumptions are reference evidence, not empirical truth.'
 ]})
models[1].update({'source_discards':None,'source_discard_fraction_of_catch':None,'source_fleet_return':None,
 'discard_evidence_status':'catch explicitly includes landings plus discards, split not published in recovered model input',
 'source_fidelity_caveats':[
   'PDF/printed9 Catch section explicitly combines all landings including IUU with discards for Ecopath1978; AppendixA2.1 PDF46 gives total catch per fleet/group, not a discard split.',
   'No source fleet fate or separately quantified processing offal recovered. Generic detritus is not proof of fishery-return routing.',
   'PDF7 area6205000km2 includes northern Sumatra and Maldives; model extends beyond named LME. AppendixA2.1 normalizes catches to the entire study area.',
   'Table16 PDF24 distinguishes biomass in habitat area from area-adjusted biomass; use frozen area-adjusted biomass consistently.',
   'A hypothetical full return to group49 is implementable as an assumption only; absence of observed D does not block designated fH experiments.'
 ]})
models[2].update({'source_discards':None,'source_discard_fraction_of_catch':None,'source_fleet_return':None,
 'discard_evidence_status':'published group catch/discard inputs unavailable; frozen H identically zero',
 'source_fidelity_caveats':[
   'Frozen paper is Chaikina2020 chapter printed23–34 based on a2004 thesis; it is not the original49-page thesis.',
   'PDF25/printed24 uses NE for its new Ecopath variant, contrasted with SD; do not expand NE as a northeastern subregion.',
   'Source period1980s and wholeSea area1590000km2; filename1980 is a catalog convention.',
   'Table1 PDF27/printed26 reproduces29-group parameters but has no catch/discard column. All raw group exports=0; this does not establish a real-world zero fishery.',
   'For the frozen input H=0 so D=fH=0 for every fraction; retain as no-harvest/invariance case and do not infer a nonzero discard sensitivity.',
   'Generic detritus fate1 in JSON is not documented fleet fate. No processing-offal flow recovered.',
   'Table1 biomass header erroneously includes year-1, although biomass is stock. Detritus biomass is blank; raw sentinel-9999 is unknown, not0.'
 ]})
evidence={'schema_version':1,'audit_date':'2026-09-10','scope':'Four frozen source-model evidence audits; no production or frozen-input edits',
 'epistemic_policy':'Published parameter assumptions, frozen conversion fields, and hypothetical routes are distinct. Null means unavailable/not established; no blanket zero filling. Source-supported routing does not make a hypothetical fraction observed.',
 'guidance':[
  {'title':'EwE User Guide: Ecopath Input','url':'https://pressbooks.bccampus.ca/eweguide/chapter/ecopath-input/','sections':['Landings','Discards','Discard Mortality','Discard Fate','Detritus Import'],
   'claims':'Catch comprises landings and discards. Rates use total model area. Discard mortality and fate are separate inputs; fate allocates discards to detritus or export. A dedicated discard pool is supported. Biological detritus fate is distinct from fishery discard fate.'},
  {'title':'Ecosystem Modelling with EwE: Spatial fishery dynamics','url':'https://pressbooks.bccampus.ca/ewemodel/chapter/spatial-fishery-dynamics/','claims':'Fleet specification distinguishes landings, discards, discard mortality and discard fate.'},
  {'title':'Ecosystem Modelling with EwE: Bycatch and discards','url':'https://pressbooks.bccampus.ca/ewemodel/chapter/bycatch-and-discards/','claims':'Discard changes can affect scavengers and subsequent trophic pathways. This supports scenario analysis, not a universal quantitative return fraction.'}
 ],'loader_evidence':{'file':artifact(I/'PPREstimation/ModelData.py','frozen calculator loader'), 'locations':['313–314 detritus catch forced0','410 export renamed catch','850–893 selected fields and M0/egestion flow; no fleet discard parse','919 export renamed catch'],
 'inference':'Source fleet return is not an explicit input path in this loader. Audit solved detritus balances separately before adding routes; original EE/diets can reflect author balancing even when fleet return metadata was omitted.'},
 'models':models}
manifest=json.loads((R/'input_manifest.json').read_text(encoding='utf-8'))
expected={entry['path']:entry['sha256'] for entry in manifest['files']}
checked=[]
for record in [f for model in models for f in model['files']] + [evidence['loader_evidence']['file']]:
    relative=record['path'].removeprefix('inputs/')
    assert expected[relative]==record['sha256'], relative
    checked.append(relative)
evidence['verification']={
 'referenced_frozen_files_hash_matched_manifest':len(checked),
 'input_manifest_sha256':digest(R/'input_manifest.json'),
 'publication_pages_visually_reviewed':['humboldt:3','bay:7,9,24,46','okhotsk:24,25,27','guinea:129,147,153,157'],
 'rendered_evidence':[artifact(p,'visually reviewed publication page' if '-pdf-' in p.name else 'original-XLS cell transcription, not original screenshot') for p in sorted(O.glob('*.png'))],
 'guinea_table_extraction':'Poppler -bbox coordinates; all36 table rows visually checked; blank cells preserved as null',
 'humboldt_xls_reader':'xlrd2.0.2 installed into private verification/source_pages/vendor; no shared environment changes',
 'reproduce':'python research/discard_sensitivity_2026_09_10/verification/source_pages/audit_sources.py',
}
(R/'results').mkdir(exist_ok=True)
(R/'results/source_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
fields=['model_id','name','source_period','source_area_km2','group_count','caught_living_group_count','frozen_living_harvest_sum','source_supported_sr_status','discard_evidence_status']
with (R/'results/model_inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:m[k] for k in fields} for m in models)
print(json.dumps({'models':len(models),'humboldt_xls_parity':parity,'humboldt_discard_fraction':discards/(landings+discards),'guinea_visible_D_sum':gu['source_discards_sum_of_nonblank_rounded_table16_cells']},indent=2))
