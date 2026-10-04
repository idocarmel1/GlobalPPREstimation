"""Read native sources and regional audit; write only this review directory."""
from pathlib import Path
import hashlib, json, math, zipfile, xml.etree.ElementTree as ET
from decimal import Decimal
from collections import Counter

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[5]
MID = '50_502013_Coastal_Kyoto_Inoue_(2013)'
REG = ROOT / 'regions/LME_050'
REPORT = REG / 'validation_reports' / MID
WORK = OUT.parent
PDF = REG / 'papers/SOJ-2023/Inoue_et_al_2023_Sea_of_Japan-eaca3b45.pdf'
DOCX = REG / 'papers/SOJ-2023/12562_2023_1691_MOESM1_ESM-8d668bb0.docx'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(name, obj): (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(DOCX) as z:
    doc = ET.fromstring(z.read('word/document.xml'))
tables = []
for table in doc.findall('.//w:tbl', ns):
    tables.append([[''.join(t.text or '' for t in c.findall('.//w:t', ns)).strip() for c in row.findall('w:tc', ns)] for row in table.findall('w:tr', ns)])
assert len(tables)==12
fleet_table = tables[4]  # Native table 5; 2013, not preceding 1985 table 4.
assert fleet_table[0] == ['', 'Group name', 'set net', 'trawl net', 'gill net', 'dredge net', 'angling', 'other', 'Total']
catch = {i:None for i in range(1,41)}
fleet_ledger=[]
for row in fleet_table[1:]:
    if not row[0].isdigit(): continue
    i=int(row[0]); assert 1<=i<=28
    cells=[Decimal(x) if x else Decimal(0) for x in row[2:8]]
    total=sum(cells, Decimal(0)); catch[i]=total
    fleet_ledger.append({'group_id':i,'group_name':row[1],'printed_fleet_cells':row[2:8], 'fleet_sum':str(total),'printed_total':row[8], 'fleet_sum_minus_printed_total':str(total-Decimal(row[8]))})
assert len(fleet_ledger)==28 and all(catch[i]>0 for i in range(1,29))
assert catch[11]==Decimal('0.000005') and catch[23]==Decimal('0.00001')

# Independently transcribed from the native Table 1 second block on PDF5/577,
# continued PDF6/578; visually checked against retained page PNGs. The accepted
# model, source_parameter_review and allocation_provenance are not authorities
# for these literal printed values.
native_B='0.85 0.004 1.95 0.13 0.82 1.41 0.15 0.08 0.03 1.99 0.00002 0.04 0.03 0.10 0.03 0.14 0.25 0.05 0.49 0.51 1.73 0.26 0.00002 0.20 0.10 0.01 0.02 0.42 0.01 0.02 0.01 0.14 0.07 10.90 8.74 0.02 0.01 5.82 28.06 43.00'.split()
biomass={i:Decimal(v) for i,v in enumerate(native_B,1)}
model_path=REG/'models'/MID/'model.json'
model=read(model_path)
groups={int(x['group_seq']):x['group_name'] for x in model['group']}
assert len(groups)==40 and groups[29]=='Dragonet' and groups[30]=='Tongue sole'
all_group_names={**groups,41:'diet_import'}
assert sha(model_path)=='a3b008c0add95db106f9e10cf90907cc7f1f9d2ab1425cbf615745142e27330e'
for g in model['group']:
    i=int(g['group_seq']); assert Decimal(g['biomass'])==biomass[i], (i,g['biomass'],biomass[i])

# S3/S7 number order is not the accepted/Table1 order. Join actual names.
s3=[]
for row in tables[2]:
    if not row[0].isdigit():continue
    i=int(row[0]); name=row[1]
    accepted_id={'Amberjack':6,'Sole':30,'Dragonet':29}.get(name,i)
    s3.append({'printed_S3_id':i,'printed_group':name,'accepted_Table1_id':accepted_id,'accepted_group':groups[accepted_id],'native_representatives':row[2]})
assert next(x for x in s3 if x['printed_S3_id']==29)['accepted_Table1_id']==30
assert next(x for x in s3 if x['printed_S3_id']==30)['accepted_Table1_id']==29
area_row=next(row for row in tables[1] if row[0]=='area size (km2)')
bins=[Decimal(x) for x in area_row[1:8]]
assert bins==list(map(Decimal,['60','60','100','300','300','250','153']))
assert sum(bins)==1223

provenance=read(REPORT/'allocation_provenance.json')
for i in range(1,41):
    c=provenance['rawcatch'][str(i)]
    assert (None if c is None else Decimal(str(c)))==catch[i], (i,c,catch[i])
    assert Decimal(str(provenance['biomass'][str(i)]))==biomass[i]
audit=read(REPORT/'taxon_audit.json')
book=read(WORK/'current_book.json')
header,rows=book['Catch']['Catch']
catch_by_label={row[header.index('taxon')]:row for row in rows}
assert len(catch_by_label)==len(audit)==253 and {x['taxon'] for x in audit}==set(catch_by_label)
rank={'Very low':0,'Low':1,'Medium':2,'High':3}
normalized={'very_low':'Very low','low':'Low','medium':'Medium','high':'High'}
vector_checks=[]; maximum_error=0.0
for row in audit:
    label=row['taxon']; ids=row['candidate_ids']; assert ids and len(ids)==len(set(ids))
    allgroups=row['considered_all_source_groups']
    assert len(allgroups)==41 and {g['id'] for g in allgroups}==set(range(1,42)), label
    assert {g['id'] for g in allgroups if g['decision']=='included'}==set(ids), label
    assert all(g['decision'] in ['included','excluded'] and g['rationale'] for g in allgroups),label
    assert all(g['group']==all_group_names[g['id']] for g in allgroups),label
    assert set(ids)<=set(range(1,39)),label
    assert len(row['mapping'])==len(ids) and len(row['candidate_values'])==len(ids),label
    native=catch_by_label[label]
    assert row['common_name']==native[header.index('common_name')],label
    assert math.isclose(row['catch_tonnes'],native[header.index(2019)],rel_tol=1e-12,abs_tol=1e-12),label
    assert row['zero_catch']==(row['catch_tonnes']==0),label
    complete=all(catch[i] is not None for i in ids)
    assert row['source_fields_complete_catch']==complete,label
    rule=row['allocation_rule']
    if len(ids)==1:
        assert rule=='W1' and row['allocation_confidence']=='High',label
        expected={ids[0]:Decimal(1)};total=Decimal(1)
    else:
        values=catch if complete else biomass
        assert rule==('W4' if complete else 'W9'),label
        assert row['allocation_confidence']=='Medium',label
        total=sum(values[i] for i in ids);assert total>0,label
        expected={i:values[i]/total for i in ids}
    assert math.isclose(row['allocation_total'],float(total),rel_tol=1e-12,abs_tol=1e-12),label
    assert row['overall_confidence']==min([row['membership_confidence'],row['allocation_confidence']],key=rank.get),label
    for value in row['candidate_values']:
        i=value['id'];assert value['group']==groups[i] and i in ids,label
        assert (None if value['source_catch_t_km2_yr'] is None else Decimal(str(value['source_catch_t_km2_yr'])))==catch[i],(label,i)
        assert Decimal(str(value['final_table1_biomass_t_km2']))==biomass[i],(label,i)
    local=[]
    for m in row['mapping']:
        i=next(i for i in ids if groups[i]==m['group'])
        assert m['model_id']==MID and m['taxon']==label,label
        assert normalized[m['confidence']]==row['overall_confidence'],label
        assert math.isfinite(m['weight']) and m['weight']>0,label
        error=abs(m['weight']-float(expected[i]));maximum_error=max(maximum_error,error)
        assert error<1e-12,(label,i,error)
        local.append({'id':i,'group':groups[i],'native_basis_value':str((catch if rule=='W4' else biomass)[i]) if rule!='W1' else '1','expected_weight':str(expected[i]),'saved_weight':m['weight'],'absolute_error':error})
    assert math.isclose(sum(m['weight'] for m in row['mapping']),1,abs_tol=1e-12),label
    vector_checks.append({'taxon':label,'zero_catch':row['zero_catch'],'candidate_ids':ids,'all_40_source_groups_accounted_for':True,'rule':rule,'total':str(total),'overall_confidence':row['overall_confidence'],'vector':local})

# Complete residual scopes are checked independently from source organism type
# and explicit main-method pelagic designation (not reporting size tags).
bony=list(range(1,11))+list(range(12,20))+[29,30,31]
pelagic=list(range(1,11))+[14,16,17,19]
bylabel={x['taxon']:x for x in audit}
for label in ['Actinopterygii','Marine fishes not identified','Marine finfishes not identified']:
    assert bylabel[label]['candidate_ids']==bony,label
assert bylabel['Marine pelagic fishes not identified']['candidate_ids']==pelagic
tuna=bylabel['Thunnus orientalis'];assert tuna['candidate_ids']==[8] and tuna['membership_rule']=='M1' and tuna['overall_confidence']=='High'
write('native_source_numeric_ledger.json',{'source_pdf_sha256':sha(PDF),'source_supplement_sha256':sha(DOCX),'S4_locator':'Native supplement table 5, 2013, following table 4 (1985); t/km²/year, six detailed fleet columns','fleet_header':fleet_table[0],'fleet_rows':fleet_ledger,'sum_all_printed_fleet_values':str(sum(catch[i] for i in range(1,29))),'native_printed_total_sum_row':fleet_table[-1],'missing_catch_group_ids':list(range(29,41)),'printed_000_total_but_positive_detailed_fleets':[11,23],'blank_fleet_cell_treatment':'No listed mass within a supplied source group row; printed numeric 0.000 is a rounded value, not a demonstrated exact zero. Absent group rows remain unknown.','Table1_2013_biomass':{str(i):str(v) for i,v in biomass.items()},'S3_name_crosswalk':s3,'S1_2_caption':'Mean wet weight (t/km2 /year) of functional group from benthic sampling and literature. Ceff is the catch efficiency of the beam trawl net for the functional groups','S1_2_area_cells':[str(x) for x in bins],'S1_2_area_sum_km2':str(sum(bins)),'area_interpretation':'Seven native 0–240 m bins total1223km², not the main-paper reported2230km². Source biomass extrapolation/denominator inconsistency unresolved; neither is a replacement footprint or accepted-parameter correction.'})
write('allocation_vector_verification.json',{'inputs':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [PDF,DOCX,model_path,REPORT/'taxon_audit.json',REPORT/'allocation_provenance.json',REPORT/'mapping_changes.json',WORK/'current_book.json']},'labels':len(audit),'matching_rows':sum(len(x['mapping']) for x in audit),'zero_catch_labels':sum(x['zero_catch'] for x in audit),'confidence_counts':dict(Counter(x['overall_confidence'] for x in audit)),'allocation_rule_counts':dict(Counter(x['allocation_rule'] for x in audit)),'maximum_weight_absolute_error':maximum_error,'all_40_native_plus_synthetic_import_candidate_partitions_exact':True,'all_source_catch_and_biomass_fields_match_native_source':True,'weakest_confidence_rule_matches':True,'accepted_canonical_hash_matches':True,'vectors':vector_checks,'scope_limit':'Numerical reproduction of declared candidates is distinct from proof of literal membership. Very low analogues retain unobserved species/stage/caught-mass composition and geographic/model transfer uncertainty. No biological parameters, methods or shared output writes.'})
print(json.dumps({'labels':len(audit),'rows':sum(len(x['mapping']) for x in audit),'confidence_counts':dict(Counter(x['overall_confidence'] for x in audit)),'rule_counts':dict(Counter(x['allocation_rule'] for x in audit)),'max_weight_error':maximum_error,'catch_fleet_sum':str(sum(catch[i] for i in range(1,29))),'S1_area_sum':str(sum(bins)),'audit_sha256':sha(REPORT/'taxon_audit.json')}))
