from pathlib import Path
from decimal import Decimal, getcontext
import sys,json,csv,re,hashlib
from pypdf import PdfReader
import pypdfium2 as pdfium

getcontext().prec=40
HERE=Path(__file__).resolve().parent
REGION=HERE.parents[4]
SOURCE=REGION/'papers/OKH-GM2019/gorbatenko_2018_dissertation.pdf'
SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction')
sys.path.insert(0,str(SKILL/'scripts'))
from pdfgrid import get_words
D=Decimal
def jsdump(name,obj):
    (HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str),encoding='utf8')
def csvdump(name,rows):
    with (HERE/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

EXPECTED_SOURCE_HASH='a26ef69acf1c00b32f49772e52b66f85baa79cf1e0ba3fecefe3800827787d45'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED_SOURCE_HASH
reader=PdfReader(SOURCE)
text={str(p):reader.pages[p-1].extract_text() for p in [19,20,86,88,89,118,119,120,123,124,125,126,295,297,298,299,421,422,456,457,459,460,461,467]}
jsdump('source_page_text.json',text)
geometries={}
for p in [124,125,298]:
    lines=get_words(str(SOURCE),p,merge_gap=.4)
    geometries[str(p)]=[{'y':line.y,'text':line.text,'cells':[{'text':c.text,'x0':c.x0,'x1':c.x1,'y0':c.y0,'y1':c.y1} for c in line.cells]} for line in lines]
jsdump('source_coordinate_lines.json',geometries)

def extract(page,ymin,ymax,count,identifiers):
    rows=[]
    for line in geometries[str(page)]:
        if not ymin<line['y']<ymax:continue
        nums=[c['text'] for c in line['cells'] if re.fullmatch(r'\d+(?:[,.]\d+)?',c['text'])]
        if len(nums)!=count:continue
        full=line['text']
        key=next((a for a in identifiers if full.startswith(a+' ') or full.startswith(a+' |') or full.startswith(a)),None)
        if key is None:continue
        rows.append({'source_name':key,'values':nums,'y_center_pt':line['y'],'source_page':page})
    return rows

large_ids=['Зоопланктон','Эвфаузииды','Копеподы','Амфиподы','Сагитты','Птероподы','Мизиды','Декаподы','Медузы','Ихтиопланктон','Икра','Личинки','Сумма']
small_ids=['Копеподы','Эвфаузииды','Меропланктон','Прочие','Сумма']
large=extract(125,170,333,10,large_ids)
small=extract(125,400,465,10,small_ids)
assert len(large)==13 and len(small)==5,(len(large),len(small))
labels={'Зоопланктон':'Zooplankton subtotal','Эвфаузииды':'Euphausiids','Копеподы':'Copepods','Амфиподы':'Amphipods','Сагитты':'Chaetognaths','Птероподы':'Pteropods','Мизиды':'Mysids','Декаподы':'Decapod larvae','Медузы':'Jellyfish','Ихтиопланктон':'Ichthyoplankton subtotal','Икра':'Fish eggs','Личинки':'Fish larvae','Сумма':'Total','Меропланктон':'Meroplankton','Прочие':'Other'}
cols=['daily_spring','daily_summer','daily_autumn','daily_winter','season_spring','season_summer','season_autumn','season_winter','annual','percent_wet']
all_table_rows=[]
for size,rows in [('large',large),('small',small)]:
    for row in rows:
        row.update({'consumer_subset':size,'prey':labels[row['source_name']],'source_table':'4.15' if size=='large' else '4.16','source_units':'thousand wet tonnes; last column %'})
        row.update({k:v.replace(',','.') for k,v in zip(cols,row['values'])})
        all_table_rows.append({k:v for k,v in row.items() if k!='values'})
jsdump('source_tables_4_15_4_16.json',all_table_rows)
csvdump('source_tables_4_15_4_16.csv',all_table_rows)

# Exact text copies of Tables 4.13 and 4.14, including all stocks/rations and percentages.
stocks=[{'subset':'small <20 mm*','spring':'1185','summer':'11230','autumn':'555','winter':'912'}, {'subset':'large >20 mm**','spring':'1022','summer':'2539','autumn':'1618','winter':'1329'}, {'subset':'total (1.5-750.0 mm)','spring':'2207','summer':'13769','autumn':'2173','winter':'2241'}]
rations=[{'subset':'small','spring':'0.15','summer':'0.20','autumn':'0.20','winter':'0.15'},{'subset':'large','spring':'0.10','summer':'0.15','autumn':'0.15','winter':'0.10'}]
diet_large=[['Zooplankton subtotal','89.2','90.7'],['Euphausiids','40.9','35.7'],['Copepods','35.5','39.9'],['Amphipods','9.7','2.9'],['Chaetognaths','1.4','4.1'],['Pteropods','0.6','0.8'],['Mysids','0.8','0.7'],['Decapod larvae','0.2','0.8'],['Jellyfish','0.1','5.8'],['Ichthyoplankton subtotal','10.8','9.3'],['Fish eggs','7.2','8.5'],['Fish larvae','3.6','0.8'],['Daily ration (% body weight)','0.10','0.15']]
jsdump('source_tables_4_13_4_14.json',{'page':124,'period':'2006-2014','stock_units':'thousand wet tonnes','biomass_rows':stocks,'ration_rows_percent_of_body_weight':rations,'winter_spring_and_summer_autumn_diet_percent':diet_large,'footnote_markers':'* and ** appear after size classes, but no explanations are printed on pp.124-125. Do not fabricate.'})
footnote_file=HERE/'source_tables_4_13_4_14.json'
stock_evidence=json.loads(footnote_file.read_text(encoding='utf8'))
stock_evidence['earlier_table3_9_footnote_evidence']={'page':88,'asterisk':'BSD plankton-net plus trawl catches','double_asterisk':'trawl catches','scope':'Printed under earlier Table3.9; not explicitly repeated under Table4.13.'}
jsdump('source_tables_4_13_4_14.json',stock_evidence)

factor_vals={
'Copepods':('16.02','12.51'),'Euphausiids':('12.60','9.11'),'Mysids':('17.27','12.53'),'Hyperiids':('16.66','12.88'),'Pteropods':('22.27','17.79'),'Oikopleura':('21.72','20.97'),'Chaetognaths':('22.98','17.78'),'Jellyfish':('320.27','279.33'),'Other zooplankton':('20.14','15.66')}
primary_factor={'Copepods':'14.0','Euphausiids':'10.6','Hyperiids':'14.5','Chaetognaths':'20.0','Jellyfish':'285.2'}
factor_rows=[{'prey':k,'winter_spring_wet_per_carbon':v[0],'summer_autumn_wet_per_carbon':v[1],'source':'dissertation Table 7.1, p.298','period':'2006-2014 chemical sampling, p.295','scope':'taxonomic group means; Appendix46 p.456 species list','use':'Match to same prey category and season; do not substitute generic Other for unidentified composition.'} for k,v in factor_vals.items()]
csvdump('table7_1_carbon_factors.csv',factor_rows);jsdump('table7_1_carbon_factors.json',factor_rows)

map22={'Copepods':4,'Euphausiids':5,'Chaetognaths':7,'Jellyfish':14}
leaves=[r for r in all_table_rows if r['prey'] not in ['Zooplankton subtotal','Ichthyoplankton subtotal','Total']]
total_q=D('772.7')+D('2404.4')
wet_rows=[]
for r in leaves:
    prey=r['prey']; annual=D(r['annual']); seasons=[D(r[c]) for c in ['season_spring','season_summer','season_autumn','season_winter']]
    sf=factor_vals.get(prey)
    carbon_source=sum(q/D(sf[0 if i in (0,3) else 1])/1000 for i,q in enumerate(seasons)) if sf else None
    pf=primary_factor.get(prey)
    carbon_primary=annual/D(pf)/1000 if pf else carbon_source if prey in ['Mysids','Pteropods'] else None
    status='source_taxonomic_group_mean_match; prey_stage_composition_not_proven' if prey in map22 else 'source_factor_match_but_absent_from_22_groups' if prey in ['Mysids','Pteropods'] else 'unresolved_factor_and_or_group'
    wet_rows.append({'consumer_subset':r['consumer_subset'],'prey':prey,'source_table':r['source_table'],'source_page':125,'annual_wet_thousand_t':str(annual),'annual_wet_t':str(annual*1000),'reported_subset_percent':r['percent_wet'],'full_aggregate_wet_DC':str(annual/total_q),'source_seasonal_wet_thousand_t':[str(v) for v in seasons],'season_sum_minus_annual_thousand_t':str(sum(seasons)-annual),'model22_prey_id':map22.get(prey),'factor_status':status,'source2018_carbon_Q_million_tC_per_year':str(carbon_source) if carbon_source is not None else None,'mixed_2019_anchor_carbon_Q_million_tC_per_year':str(carbon_primary) if carbon_primary is not None else None,'exact_carbon_DC':None,'reason_carbon_DC_unknown':'Full carbon Q is unknown; never normalize known prey alone.'})
jsdump('wet_prey_flows_and_carbon_contributions.json',wet_rows)
csvdump('wet_prey_flows_and_carbon_contributions.csv',[{k:json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v for k,v in r.items()} for r in wet_rows])

aggregates=[]
for prey in dict.fromkeys(r['prey'] for r in wet_rows):
    rows=[r for r in wet_rows if r['prey']==prey]
    agg={'prey':prey,'annual_wet_thousand_t':str(sum(D(r['annual_wet_thousand_t']) for r in rows)),'wet_DC_in_full_source_category_set':str(sum(D(r['full_aggregate_wet_DC']) for r in rows)),'model22_prey_id':map22.get(prey)}
    for key in ['source2018_carbon_Q_million_tC_per_year','mixed_2019_anchor_carbon_Q_million_tC_per_year']:
        agg[key]=str(sum(D(r[key]) for r in rows)) if all(r[key] is not None for r in rows) else None
    aggregates.append(agg)
jsdump('aggregated_source_prey_categories.json',aggregates);csvdump('aggregated_source_prey_categories.csv',aggregates)

remaining=[r for r in aggregates if r['source2018_carbon_Q_million_tC_per_year'] is None]
known_source=sum(D(r['source2018_carbon_Q_million_tC_per_year']) for r in aggregates if r['source2018_carbon_Q_million_tC_per_year'] is not None)
known_mixed=sum(D(r['mixed_2019_anchor_carbon_Q_million_tC_per_year']) for r in aggregates if r['mixed_2019_anchor_carbon_Q_million_tC_per_year'] is not None)
remaining_wet=sum(D(r['annual_wet_thousand_t']) for r in remaining)
source_Bcarbon=sum((D(stocks[2][s])/D(factor_vals['Jellyfish'][0 if s in ['spring','winter'] else 1]))/1000 for s in ['spring','summer','autumn','winter'])/4
amphi=[r for r in leaves if r['prey']=='Amphipods'][0]
amphi_hyp_source=sum(D(amphi[k])/D(factor_vals['Hyperiids'][0 if i in [0,3] else 1])/1000 for i,k in enumerate(['season_spring','season_summer','season_autumn','season_winter']))
amphi_hyp_primary=D(amphi['annual'])/D(primary_factor['Hyperiids'])/1000

summary={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'period':'2006-2014','coverage':'whole Okhotsk Sea epipelagic jellyfish, size subsets separately; chemical samples 2006-2014','large_Q_thousand_wet_t':'772.7','prose_large_Q_thousand_wet_t':'772.8','small_Q_thousand_wet_t':'2404.4','combined_Q_thousand_wet_t':str(total_q),'leaf_rows':len(leaves),'source_category_count':len(aggregates),'combined_full_wet_DC_sum':str(sum(D(r['wet_DC_in_full_source_category_set']) for r in aggregates)),'source_assimilation':'0.70','derived_GS':'0.30','GS_source_pages':[120,123],'GS_scope':'assumption explicitly used to estimate daily ration of large and small jellyfish; not independently measured GE','season_equal_mean_combined_B_thousand_wet_t':str(sum(D(stocks[2][s]) for s in ['spring','summer','autumn','winter'])/4),'source_QB_wet_equal_season_mean':str(total_q/(sum(D(stocks[2][s]) for s in ['spring','summer','autumn','winter'])/4)),'source2018_equal_season_carbon_B_million_tC':str(source_Bcarbon),'source2018_known_carbon_Q_lower_bound_million_tC_per_year':str(known_source),'mixed_2019_anchor_known_carbon_Q_lower_bound_million_tC_per_year':str(known_mixed),'strict_missing_factor_wet_thousand_t':str(remaining_wet),'strict_missing_factor_wet_fraction':str(remaining_wet/total_q),'remaining_factor_categories':remaining,'conditional_amphipod_to_hyperiid_assumption':{'status':'scenario_only','source_support':'p.118 describes large jellyfish eating hyperiids; Appendix14 p.422 lists Themisto plus explicit Other in the Amphipoda row. Full allocation is not source-determined.','source2018_additional_Q_carbon':str(amphi_hyp_source),'mixed2019_additional_Q_carbon':str(amphi_hyp_primary),'remaining_wet_if_assumption_adopted_thousand_t':str(remaining_wet-D('36.7'))},'complete_carbon_DC_available':False,'complete_22_group_wet_DC_available':False,'complete_source_category_wet_DC_available':True,'unmapped_22_group_wet_thousand_t':str(sum(D(r['annual_wet_thousand_t']) for r in aggregates if r['model22_prey_id'] is None)),'positive_respiration_test_against_2019_P_0_144_million_tC_only_mixed_scope':{'known_mixed_Q_min_assimilation_minus_P':str(D('.7')*known_mixed-D('.144')),'known_source2018_Q_min_assimilation_minus_P':str(D('.7')*known_source-D('.144')),'meaning':'Feeding reconstruction no longer forces negative energy balance in carbon using the 2019 production, but this mixes source periods/stocks and does not establish native Ecopath balance.'},'no_normalization_or_canonical_edits':True}
jsdump('summary.json',summary)

summary['carbon_conversion_scope']='Seasonal taxonomic group means from Table7.1. Exact prey stage/species weighting is unavailable; the positive missing-prey lower bound is conditional on these aggregate-factor approximations. Jellyfish prey in particular is not size-partitioned.'
summary['GS_carbon_mapping_scope']='Source 70% assimilation belongs to a calorie-based ration calculation (p.20). Using its complement as carbon-currency Ecopath GS assumes energy/carbon assimilation equivalence.'
summary['stock_carbon_scope']='Equal four-season mean of Table4.13 stocks converted using all-jellyfish group-mean factors. Net jellyfish are mainly Aglantha (>90%, p.86), while trawl jellyfish are mainly scyphozoans; source group mean is not proven to be biomass-weighted for these subsets.'
summary['full_source_wet_DC_scope']='Computed from all annual wet prey flows divided by full combined source Q; excludes subtotal rows. It is complete for 12 source categories, but cannot serve as a carbon diet.'
summary['season_duration_note']='Table4.15/4.16 seasonal consumption is consistent with approximately 90-day seasons (360-day arithmetic); rounded source cells are preserved, not rescaled to 365 days.'
summary['table7_1_uncertainty']='Source table note: SE does not exceed 10%; many computed decimal digits are arithmetic audit precision, not measurement precision.'
jsdump('summary.json',summary)

# Original PDF page rendering for reproducible visual verification.
doc=pdfium.PdfDocument(str(SOURCE))
for page in [123,124,125,298,422,456]:
    doc[page-1].render(scale=2.3).to_pil().save(HERE/f'dissertation_p{page}_source.png')

# Exact numeric cell check using independent pypdf line extraction of the two feeding tables.
def compare_table(marker,next_marker,want):
    block=text['125'].split(marker,1)[1].split(next_marker,1)[0]
    actual=[]
    for line in block.splitlines():
        vals=re.findall(r'\d+,\d+',line)
        if len(vals)==10:actual.append(vals)
    assert actual==[r['values'] for r in want],(marker,actual,want)
    return len(actual)*10
checks={'tables_4_15_4_16_numeric_cells_independent_text_match':compare_table('Таблица 4.15','Таблица 4.16',large)+compare_table('Таблица 4.16','При сопоставлении',small),'large_leaf_sum_equals_total':sum(D(r['annual']) for r in large if r['prey'] not in ['Zooplankton subtotal','Ichthyoplankton subtotal','Total'])==D('772.7'),'small_leaf_sum_equals_total':sum(D(r['annual']) for r in small if r['prey']!='Total')==D('2404.4'),'all_source_category_wet_DC_sum_one':abs(sum(D(r['full_aggregate_wet_DC']) for r in wet_rows)-1)<D('1e-35'),'source_sha256':summary['source_sha256'],'all_unknown_carbon_DC_preserved':all(r['exact_carbon_DC'] is None for r in wet_rows),'original_PDF_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==summary['source_sha256']}
def numeric_cells(line):
    return [c['text'].replace(',','.') for c in line['cells'] if re.fullmatch(r'\d+(?:[,.]\d+)?',c['text'])]
stock_lines=[line for line in geometries['124'] if 110<line['y']<169]
stock_actual=[numeric_cells(line)[-4:] for line in stock_lines]
stock_wanted=[[r[s] for s in ['spring','summer','autumn','winter']] for r in stocks+rations]
assert stock_actual==stock_wanted
diet_lines=[line for line in geometries['124'] if 305<line['y']<472]
assert [numeric_cells(line) for line in diet_lines]==[r[1:] for r in diet_large]
factor_lines=[line for line in geometries['298'] if 145<line['y']<250]
factor_actual=[numeric_cells(line)[-2:] for line in factor_lines]
assert factor_actual==[list(v) for v in factor_vals.values()]
checks.update({'table4_13_source_numeric_cells_verified':20,'table4_14_source_numeric_cells_verified':26,'table7_1_conversion_factor_cells_verified':18,'original_sha256_matches_prior_evidence':summary['source_sha256']==EXPECTED_SOURCE_HASH,'source_pages_visually_inspected':[123,124,125,298,422,456]})
assert all(v for k,v in checks.items() if k!='source_sha256')
jsdump('verification.json',checks)
print(json.dumps(summary,ensure_ascii=False,indent=2))

