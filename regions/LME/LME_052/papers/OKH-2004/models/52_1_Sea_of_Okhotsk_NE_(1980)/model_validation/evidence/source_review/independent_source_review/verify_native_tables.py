"""Independently inspect native chapter tables; all writes stay beside this file."""
from pathlib import Path
from decimal import Decimal
import hashlib, json, re, math
import pymupdf

OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'regions/LME_052').is_dir() and (p/'tools').is_dir())
MID='52_1_Sea_of_Okhotsk_NE_(1980)'
PDF=ROOT/'regions/LME_052/papers/OKH-2004/Palomares20_FishCentResaRep28-440d8aa8.pdf'
CANON=ROOT/'regions/LME_052/models'/MID/'model.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(PDF)=='440d8aa860813d435891b107bf85340df773df322c83fa1f9f82069e3661851d'
assert sha(CANON)=='61b6176affe6051948b3ec972fe87d95dabd8d98b66744b4c7350fcf303b9099'
model=json.loads(CANON.read_text(encoding='utf-8-sig'))
canon={int(x['group_seq']):x for x in model['group']}
assert len(canon)==29
with pymupdf.open(PDF) as pdf:
    assert len(pdf)==142
    chapter=[{'PDF_page':i+1,'printed_page':i,'text':pdf[i].get_text(sort=True)} for i in range(23,35)]
    write('native_chapter_text.json',chapter)
    grids={}
    for p,rows,cols in [(26,30,7),(28,31,14),(29,31,14)]:
        detected=pdf[p].find_tables();assert len(detected.tables)==1
        t=detected.tables[0];assert (t.row_count,t.col_count)==(rows,cols)
        grids[p+1]=t.extract()
        write(f'native_table_PDF{p+1}_grid.json',{'PDF_page':p+1,'bbox':t.bbox,'row_count':rows,'col_count':cols,'cells':grids[p+1],'cell_bboxes':t.cells,'extraction':'Native vector rules and word coordinates; visually checked against native page rendering.'})
    for p in [23,24,25,26,28,29]:pdf[p].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(OUT/f'native_PDF{p+1}.png')

basic=[];numeric_differences=[];omissions=[]
fields=['tl','biomass','pb','qb','ee','ge']
for row in grids[27][1:]:
    number=int(re.match(r'\d+',row[0]).group())
    printed_name=re.sub(r'^\d+\s*\.\s*','',row[0])
    assert printed_name==canon[number]['group_name'],(number,printed_name,canon[number]['group_name'])
    record={'id':number,'group':printed_name,'printed_cells':dict(zip(fields,row[1:])),'native_locator':'Table1 PDF27/printed26'}
    basic.append(record)
    for field,cell in zip(fields,row[1:]):
        if field=='tl':
            omissions.append({'id':number,'field':field,'printed':cell,'canonical':'not a JSON field','interpretation':'Printed source TL is retained separately; this review does not replace computed runtime or classic TL.'});continue
        actual=canon[number][field]
        if not cell:
            assert Decimal(actual)==Decimal('-9999'),(number,field,cell,actual)
        elif Decimal(actual)==Decimal('-9999'):
            omissions.append({'id':number,'field':field,'printed':cell,'canonical':actual,'interpretation':'Source field omitted/unknown in accepted JSON; do not restore or change accepted parameter.'})
        elif Decimal(actual)!=Decimal(cell):
            numeric_differences.append({'id':number,'field':field,'printed':cell,'canonical':actual})
assert not numeric_differences

source_cells=[];columns={i:{} for i in range(1,27)}
for page in [29,30]:
    grid=grids[page]
    predators=[int(x) for x in grid[1][1:]]
    assert predators==(list(range(1,14)) if page==29 else list(range(14,27)))
    for row in grid[2:]:
        prey=int(re.match(r'\d+',row[0]).group())
        for predator,cell in zip(predators,row[1:]):
            assert cell is not None
            value=Decimal(cell) if cell else Decimal(0)
            columns[predator][prey]=value
            source_cells.append({'prey_id':prey,'consumer_id':predator,'source_PDF_page':page,'source_printed_page':page-1,'printed_cell':cell,'source_state':'printed_numeric' if cell else 'blank_diet_cell','arithmetic_value':str(value)})
assert len(source_cells)==29*26==754
assert all(set(c)==set(range(1,30)) for c in columns.values())
column_checks=[];changes=[];max_normalization_error=0.
for consumer in range(1,27):
    total=sum(columns[consumer].values())
    diet=canon[consumer]['diet_descr']['diet'];assert isinstance(diet,list)
    accepted={int(x['prey_seq']):Decimal(x['proportion']) for x in diet}
    assert all(i in range(1,30) for i in accepted)
    diffs=[]
    for prey in range(1,30):
        raw=columns[consumer][prey];actual=accepted.get(prey,Decimal(0))
        assert actual>=0
        expected=raw/total
        error=abs(float(actual)-float(expected));max_normalization_error=max(max_normalization_error,error)
        assert error<1e-14,(consumer,prey,raw,total,actual,expected)
        if raw!=actual:
            diff={'consumer_id':consumer,'consumer':canon[consumer]['group_name'],'prey_id':prey,'prey':canon[prey]['group_name'],'printed_proportion':str(raw),'native_column_total':str(total),'accepted_proportion':str(actual),'interpretation':'Accepted normalization of printed rounding drift; preserved, not repaired.'}
            changes.append(diff);diffs.append(diff)
    column_checks.append({'consumer_id':consumer,'group':canon[consumer]['group_name'],'native_total':str(total),'accepted_total':str(sum(accepted.values())),'native_nonblank_cells':sum(columns[consumer][i]>0 for i in range(1,30)),'accepted_matches_native_divided_by_column_sum':True,'changed_cells':len(diffs)})

# Distinguish literal zeros from source blank/default/missing fields.
exports={i:canon[i]['export'] for i in canon}
assert all(Decimal(x)==0 for x in exports.values())
BA={i:canon[i]['biomass_accum'] for i in canon}
assert all(Decimal(x)==Decimal('-9999') for x in BA.values())
pollock_fraction=Decimal('2.475')/(Decimal('2.475')+Decimal('2.119'))
text='\n'.join(x['text'] for x in chapter)
search_terms=['pollock','juvenile','catch','fisher','length','age','sardine','Sardinops','Theragra','chalcogram']
hits=[]
for page in chapter:
    for line in page['text'].splitlines():
        found=[s for s in search_terms if s.lower() in line.lower()]
        if found:hits.append({'PDF_page':page['PDF_page'],'printed_page':page['printed_page'],'terms':found,'line':line})
write('native_basic_parameter_ledger.json',{'source_sha256':sha(PDF),'source_identity':'Chaikina2020 chapter printed23–34/PDF24–35 in142-page Marine and Freshwater MiscellaneaII, FCRR28(2); explicitly based on2004BSc thesis49pages, not that original thesis.','selected_model_id':MID,'canonical_sha256':sha(CANON),'header_cells':grids[27][0],'rows':basic,'numeric_B_PB_QB_EE_differences':numeric_differences,'source_fields_not_stored_in_accepted_JSON':omissions,'blank_source_fields_retained_unknown':'QB and P/Q for producers; B/PB/QB/PQ for detritus. Printed detritusEE0.130 is source data; loader/completion behavior remains separate.','source_units':'Native biomass header literally includes t·km^-2·year^-1; biomass is presented as B and season-weighted annual means in prose. Atypical printed unit retained; no accepted unit/parameter rescaling.','source_catch':'No source Table1 catch column or29-group catch table in the full chapter. Aggregate1980s fishery catches2.4–2.6milliontonnes and local1970s WestKamchatka8–22t/km²/year do not disaggregate model groups or stages.','accepted_export_fields':exports,'export_interpretation':'Accepted zero fields lack native source-group catch support and cannot serve as complete observed/assumed source-catch composition.','accepted_BA_fields':BA,'BA_interpretation':'No numericBA or author steady-state-zero statement recovered in chapter; canonical unknowns/runtime computational completions remain protected.','pollock_native_biomass_fraction':{'adult_or_nonjuvenile':str(pollock_fraction),'juvenile':str(1-pollock_fraction),'basis':'Complete Table1 biomass2.475 and2.119; assumed common catchability and fixed spatial/temporal transfer, not observed stage caughtmass.'},'chapter_search_hits':hits})
write('native_diet_ledger.json',{'source_sha256':sha(PDF),'canonical_sha256':sha(CANON),'layout':'Table4a PDF29/printed28 predators1–13, Table4b PDF30/printed29 predators14–26; both prey1–29. Prey rows × consumer columns, not transpose.','cells':source_cells,'column_checks':column_checks,'total_cells':754,'printed_numeric_cells':sum(c['source_state']=='printed_numeric' for c in source_cells),'blank_cells':sum(c['source_state']=='blank_diet_cell' for c in source_cells),'printed_zero_cells':sum(bool(c['printed_cell']) and Decimal(c['printed_cell'])==0 for c in source_cells),'normalization_differences':changes,'changed_cell_count':len(changes),'changed_consumer_ids':[c['consumer_id'] for c in column_checks if c['changed_cells']],'maximum_accepted_normalization_absolute_error':max_normalization_error,'blank_interpretation':'Blank native diet cells are preserved as blank source observations and use zero only for matrix arithmetic. These do not establish zero source catches.','constraints':'No restoration, normalization, balancing, accepted-model mutation, SPPR computation or scientific approval. Accepted native-rounding normalization and other scientific settings are preserved exactly.'})
print(json.dumps({'groups':29,'numeric_B_PB_QB_EE_differences':len(numeric_differences),'all_diet_cells':754,'printed_numeric_cells':sum(c['source_state']=='printed_numeric' for c in source_cells),'changed_cells':len(changes),'normalized_columns':[c['consumer_id'] for c in column_checks if c['changed_cells']],'native_column_sums':{c['consumer_id']:c['native_total'] for c in column_checks},'max_normalization_error':max_normalization_error,'pollock_biomass_fraction':float(pollock_fraction)}))
