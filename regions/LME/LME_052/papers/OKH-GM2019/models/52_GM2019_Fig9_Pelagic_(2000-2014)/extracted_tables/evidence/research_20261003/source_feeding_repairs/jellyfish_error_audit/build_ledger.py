from pathlib import Path
from decimal import Decimal, getcontext
from PIL import Image, ImageChops
import json
import hashlib

getcontext().prec=40
D=Decimal
OUT=Path(__file__).resolve().parent
MODEL=OUT.parents[2]
PAPERS=MODEL.parents[1]/'papers'/'OKH-GM2019'

def dump(name,x):
    (OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def n(x):
    return str(x)

def value(s):
    return D(s.replace(',','.'))

seasons=['spring','summer','autumn','winter']
columns=[f'daily_{s}_thousand_t' for s in seasons]+[f'quarter_{s}_thousand_t' for s in seasons]+['annual_thousand_t','annual_wet_mass_share_percent']
large=[
 ('Зоопланктон','Zooplankton','aggregate',['0,91','3,46','2,21','1,18','82,0','311,0','198,2','106,6','697,8','90,3']),
 ('Эвфаузииды','Euphausiids','prey',['0,42','1,36','0,87','0,54','37,6','122,4','78,0','48,9','286,9','37,1']),
 ('Копеподы','Copepods','prey',['0,36','1,52','0,97','0,47','32,7','136,8','87,2','42,5','299,2','38,8']),
 ('Амфиподы','Amphipods','prey',['0,10','0,11','0,07','0,13','8,9','9,9','6,3','11,6','36,7','4,8']),
 ('Сагитты','Chaetognaths','prey',['0,01','0,16','0,10','0,02','1,2','14,1','9,0','1,6','25,9','3,3']),
 ('Птероподы','Pteropods','prey',['0,01','0,03','0,02','0,01','0,5','2,8','1,8','0,7','5,8','0,8']),
 ('Мизиды','Mysids','prey',['0,01','0,03','0,02','0,01','0,8','2,4','1,5','1,0','5,7','0,7']),
 ('Декаподы (лич.)','Decapod larvae','prey',['0,00','0,03','0,02','0,00','0,2','2,7','1,7','0,2','4,8','0,6']),
 ('Медузы','Jellyfish','prey',['0,00','0,22','0,14','0,00','0,1','19,9','12,7','0,1','32,8','4,2']),
 ('Ихтиопланктон','Ichthyoplankton','aggregate',['0,11','0,35','0,23','0,14','9,9','31,8','20,3','12,9','74,9','9,7']),
 ('Икра рыб','Fish eggs','prey',['0,07','0,32','0,21','0,10','6,6','29,2','18,5','8,6','62,9','8,1']),
 ('Личинки рыб','Fish larvae','prey',['0,04','0,03','0,02','0,04','3,3','2,6','1,8','4,3','12,0','1,6']),
 ('Сумма','Total','total',['1,02','3,81','2,44','1,32','91,9','342,8','218,5','119,5','772,7','100,0']),
]
small=[
 ('Копеподы','Copepods','prey',['1,69','20,21','1,00','1,30','152,0','1819,3','89,9','117,0','2178,1','90,6']),
 ('Эвфаузииды','Euphausiids','prey',['0,02','0,45','0,02','0,01','1,6','40,4','2,0','1,2','45,3','1,9']),
 ('Меропланктон','Meroplankton','prey',['0,00','0,67','0,03','0,00','0,2','60,6','3,0','0,1','63,9','2,7']),
 ('Прочие','Other prey','prey',['0,07','1,13','0,06','0,06','6,2','101,1','5,0','4,8','117,1','4,8']),
 ('Сумма','Total','total',['1,78','22,46','1,11','1,37','160,0','2021,4','99,9','123,1','2404,4','100,0']),
]

def rows(data):
    return [{'source_prey':ru,'prey':en,'row_kind':kind,'source_literals':dict(zip(columns,c))} for ru,en,kind,c in data]

tables={
 'source_pdf':str(PAPERS/'gorbatenko_2018_dissertation.pdf'),
 'period':'2006-2014',
 'Table4.13':{'printed_page':124,'pdf_page_1_based':124,'caption_units':'Biomass thousand tonnes; daily ration (SPR) percent of body mass','seasons':seasons,'source_rows':[
  {'row':'Small jellyfish <20 mm*','literals':['1185','11230','555','912']},
  {'row':'Large jellyfish >20 mm**','literals':['1022','2539','1618','1329']},
  {'row':'All jellyfish (1.5-750.0 mm)','literals':['2207','13769','2173','2241']},
  {'row':'SPR percent small','literals':['0,15','0,20','0,20','0,15']},
  {'row':'SPR percent large','literals':['0,10','0,15','0,15','0,10']}],
  'notes':'The visible page retains * and ** markers but supplies no corresponding footnote text on the inspected relevant pages. No size-class reinterpretation is invented.'},
 'Table4.14':{'printed_page':124,'pdf_page_1_based':124,'caption':'Diet composition and daily ration of large jellyfish; long-term averages','columns':['winter_spring_percent','summer_autumn_percent'],'source_rows':[
  {'row':ru,'literals':x} for ru,x in [
   ('Zooplankton',['89,2','90,7']),('Euphausiids',['40,9','35,7']),('Copepods',['35,5','39,9']),('Amphipods',['9,7','2,9']),('Chaetognaths',['1,4','4,1']),('Pteropods',['0,6','0,8']),('Mysids',['0,8','0,7']),('Decapod larvae',['0,2','0,8']),('Jellyfish',['0,1','5,8']),('Ichthyoplankton',['10,8','9,3']),('Fish eggs',['7,2','8,5']),('Fish larvae',['3,6','0,8']),('SPR percent body mass',['0,10','0,15'])]],
  'source_qualification':'p124 states diet composition is best established for large forms; small forms are expert estimates because their feeding is insufficiently studied.'},
 'Table4.15':{'printed_page':125,'pdf_page_1_based':125,'size_class':'large jellyfish','caption_units':'Consumption of organisms, thousand tonnes, mean 2006-2014','mass_basis_interpretation':'Wet biomass consumption, supported by the seasonal biomass x daily ration calculation and the stated wet-mass/body-water context; the caption itself says thousand tonnes, not carbon.','column_mapping':columns,'rows':rows(large),'total_annual_thousand_t_literal':'772,7'},
 'Table4.16':{'printed_page':125,'pdf_page_1_based':125,'size_class':'small jellyfish','caption_units':'Consumption of organisms, thousand tonnes, mean 2006-2014','mass_basis_interpretation':'Wet biomass consumption, same daily-ration calculation context as Table4.15; not carbon.','column_mapping':columns,'rows':rows(small),'total_annual_thousand_t_literal':'2404,4'},
 'source_qualification_p123':'Daily rations are calculated using Winberg energy balance, 70% food assimilation and water temperature. Body-water content for investigated jellyfish is stated as 96-98%. This assimilation is supporting jellyfish-specific context; it is not a recovered full 2019 Ecopath GS input.',
 'prose_table_difference':'p124 prose reports large annual consumption 772.8 thousand t; Table4.15 total is 772.7 thousand t and its mutually exclusive annual prey rows also sum to 772.7. Both literals are retained; table controls this tabulated calculation.',
}
dump('dissertation_tables_4_13_to_4_16.json',tables)

# Aggregate mutually exclusive prey rows only; preserve aggregate rows separately above.
annual={}
for source_rows in (large,small):
    for ru,en,kind,c in source_rows:
        if kind=='prey': annual[en]=annual.get(en,D(0))+value(c[8])
large_total=value(large[-1][3][8])
small_total=value(small[-1][3][8])
total=large_total+small_total
assert sum(annual.values())==total==D('3177.1')
factors={'Copepods':D('14.0'),'Euphausiids':D('10.6'),'Chaetognaths':D('20.0'),'Jellyfish':D('285.20')}
known=[]
for prey,factor in factors.items():
    wet=annual[prey]/D(1000)
    known.append({'prey':prey,'annual_consumption_thousand_t_wet':n(annual[prey]),'annual_consumption_million_t_wet':n(wet),'prey_wet_to_carbon_multiplier':n(factor),'factor_source':'Primary 2019 Table3, printed p154 / PDF12','derived_consumption_million_tC':n(wet/factor),'derivation':f'{wet}/{factor}','conversion_scope':'Supporting 2006-2014 consumption converted with published 2000-2014 prey factors; derived cross-source comparison, not a directly tabulated 2019 flow.'})
three=sum(D(x['derived_consumption_million_tC']) for x in known if x['prey']!='Jellyfish')
four=sum(D(x['derived_consumption_million_tC']) for x in known)
wet_known=sum(annual[p] for p in factors)/D(1000)
unknown_wet=total/D(1000)-wet_known
conditional_amphi=annual['Amphipods']/D(1000)/D('14.50')
P_C=D('.144'); figure_Q=D('.0015')+D('.046')+D('.003')
P_wet=D('4.10')*D('10.0')
PC_exact=P_wet/D('285.20')
BC_exact=D('4.10')/D('285.20')
fig_Q_wet=D('.0015')*D('20.0')+D('.046')*D('14.50')+D('.003')*D('8.70')
fig_if_wet_C=D('.0015')/D('20.0')+D('.046')/D('14.50')+D('.003')/D('8.70')
calcs={
 'primary_production':{'B_wet_million_t_literal':'4,10','wet_carbon_factor_literal':'285,20','B_C_printed_million_t_literal':'0,01','PB_per_year_literal':'10,0','P_wet_million_t_per_year_literal':'41,0','P_C_million_t_per_year_literal':'0,144','P_gC_per_m2_per_year_literal':'0,10','tier_share_percent_literal':'0,80','Bwet_times_PB':n(P_wet),'Pwet_divided_by_factor':n(PC_exact),'round_to_three_decimals':'0.144','Bwet_divided_by_factor':n(BC_exact),'round_BC_to_two_decimals':'0.01','carbon_fraction_of_jelly_wet_mass_percent':n(D(100)/D('285.20')),'printed_BC_times_PB':n(D('.01')*D('10')),'rounding_warning':'Using printed B_C=0.01 as an exact stock gives 0.10 production at PB10. This is a coarse stock-rounding artifact; the wet stock and factor imply B_C=.01437587665 and P_C=.1437587665, matching the more precise PC=.144.'},
 'figure_adopted_jelly_consumption':{'Q_C_under_tentative_routes':n(figure_Q),'terms':[{'flow_id':'F24','adopted_prey':'Chaetognaths','adopted_consumer':'Jellyfish','literal':'0,0015','routing_status':'tentative'},{'flow_id':'F48','adopted_prey':'Hyperiids','adopted_consumer':'Jellyfish','literal':'0,046','routing_status':'tentative'},{'flow_id':'F50','adopted_prey':'Deep-sea smelt','adopted_consumer':'Jellyfish','literal':'0,003','routing_status':'tentative'}],'P_C_divided_by_Q_C':n(P_C/figure_Q),'Qwet_if_adopted_routes_and_prey_factors':n(fig_Q_wet),'warning':'0.0505 is a reconstructed sum of three tentative feeding routes, not an author-tabulated total jellyfish Q. All directions/endpoints remain under review.'},
 'supporting_consumption':{'large_Q_thousand_t_wet':n(large_total),'small_Q_thousand_t_wet':n(small_total),'combined_Q_thousand_t_wet':n(total),'combined_Q_million_t_wet':n(total/D(1000)),'exclusive_combined_annual_prey_rows_thousand_t_wet':{k:n(v) for k,v in annual.items()},'known_prey_carbon_conversions':known,'three_prey_C_subtotal_million_tC':n(three),'four_prey_C_subtotal_including_cannibalism_million_tC':n(four),'unconverted_residual_wet_million_t':n(unknown_wet),'unconverted_prey':[k for k in annual if k not in factors],'P_C_divided_by_three_prey_C_subtotal':n(P_C/three),'P_C_divided_by_four_prey_C_subtotal':n(P_C/four),'conditional_amphipod_C_if_all_are_hyperiids':n(conditional_amphi),'conditional_amphipod_note':'Not included in the strict subtotal: Table4.15 says Amphipods, whereas the primary factor14.50 is for Hyperiids; exact mapping has not been established here.','full_QC_status':'Not exactly recoverable from these tables alone without additional residual-prey conversion factors/crosswalks. A positive partial carbon sum already exceeds primary PC; no correction to a printed number is needed for this necessary carbon intake check.','scope_warning':'Dissertation consumption is for 2006-2014, primary Table3/Figure9 production is for 2000-2014. This is an explicit supporting variant/comparison, not an exact reconstruction of the primary period.','wet_P_over_supporting_Q':n(P_wet/(total/D(1000))),'standard_EwE_warning':'Even alternate source wet Q does not yield a standard homogeneous-wet-mass energy balance: Pwet/Qwet remains >1. The carbon comparison alone does not establish a balanced Ecopath model.'},
 'alternative_mistake_calculations':{'if_figure_arrow_numbers_were_wet_then_QC':n(fig_if_wet_C),'if_supporting_Qwet_wrongly_divided_by_jelly_body_factor':n((total/D(1000))/D('285.20')),'if_PC_decimal_reduced_tenfold':n(P_C/D(10)),'if_PB_reduced_tenfold_then_PC':n(D('4.1')*D('1.0')/D('285.2')),'if_flow046_is_0460_QC':n(D('.0015')+D('.460')+D('.003')),'if_flow003_is_0030_QC':n(D('.0015')+D('.046')+D('.030')),'if_flow0015_is_00150_QC':n(D('.0150')+D('.046')+D('.003')),'if_flow0015_is_0150_QC':n(D('.150')+D('.046')+D('.003')),'if_outgoing0006_were_reversed_and_added_to_QC':n(figure_Q+D('.0006')),'if_outgoing00001_were_reversed_and_added_to_QC':n(figure_Q+D('.00001'))},
}
dump('jellyfish_source_calculations.json',calcs)

def hypothesis(hid,kind,claim,status,evidence,test,adoption):
    return {'id':hid,'kind':kind,'hypothesis':claim,'classification':status,'source_evidence':evidence,'test_or_result':test,'adoption_recommendation':adoption}

hypotheses=[
 hypothesis('J01','production arithmetic','The Pwet41 / PC.144 pairing is internally wrong because of wet/carbon confusion.','rejected','Primary Table3 jellyfish row visibly prints B4.10, factor285.20, PB10.0, Pwet41.0, PC0.144; Figure9 independently repeats the PC literal.','4.10*10=41.0; 41.0/285.20=.1437587665, rounding to .144. The pairing itself is correct.','Preserve all primary production values. No typo repair is justified.'),
 hypothesis('J02','rounded stock','Printed BC=.01 makes PB10 inconsistent with PC=.144.','supported explanation','Primary Table3 prints BC with only two decimal places, while PC has three.','4.10/285.20=.01437587665 rounds to .01; multiplying the rounded .01 by10 loses the original precision. The same unrounded ratio gives PC=.1437587665.','Treat the apparent mismatch as source rounding; preserve printed BC and separately record any derived stock.'),
 hypothesis('J03','header/type error','The Table3 carbon-biomass column is printed with a per-year unit.','supported header issue','Primary Table3 labels the B-carbon column million tC/year while the column is biomass and values equal wet biomass/factor.','A stock should carry tonnes, not tonnes/year. This is the already documented header ambiguity; it does not make PC=.144 a consumption value.','Record stock/header interpretation separately; do not change any numeric value.'),
 hypothesis('J04','decimal/production','PC should be .0144, Pwet4.1, or PB1.0 rather than .144,41,10.','rejected as source-supported correction','Original Table3 clearly prints .144,41.0,10.0 and Figure9 .144.','A tenfold reduction would make P/Q under the tentative diagram smaller, but needs one or several uncorroborated production changes. The current production trio is internally consistent.','Do not adopt based on balance. An author calculation error in PB remains unknowable from these tables, not evidence for PB1.'),
 hypothesis('J05','production vs consumption','The jellyfish box .144 is really Q, not P.','rejected','Figure9 caption explicitly defines box numbers as production; Table3 independently labels .144 as carbon production.','Swapping the role contradicts both source labels.','Preserve .144 as production.'),
 hypothesis('J06','arrow currency','Figure9 arrow numbers are wet tonnes rather than carbon.','rejected','Figure9 caption explicitly states million tC/year for arrow consumption.','Converting .0015,.046,.003 as if wet gives QC=.003592241379..., even below the tentative carbon sum; the unit reinterpretation does not have source support.','Preserve carbon units of Figure9 arrows.'),
 hypothesis('J07','food conversion factor','Carbon Q can be obtained by dividing all jellyfish food wet mass by the jellyfish body factor285.2.','rejected','Table3 factors belong to each organism group; supporting diet consists predominantly of copepods/euphausiids rather than jellyfish tissue.','3.1771/285.2=.011140..., but this incorrectly uses consumer-body composition for heterogeneous prey. Known prey factors give a subtotal>.20958.','Convert food using each prey factor. The jellyfish factor is valid only for jellyfish prey/cannibalism.'),
 hypothesis('J08','diagram incompleteness','The .0505 diagram sum is incomplete/uncertain consumption, while supporting tables provide missing major prey.','supported discrepancy; cause may be intended generalization','Primary p157 calls the figure a generalized energy-transformation scheme. Direct Figure9 inspection found no blue head feeding jellyfish. Dissertation4.15/4.16 explicitly report copepods2477.3k, euphausiids332.2k, chaetognaths25.9k wet annually.','The three known non-jelly prey convert to .2095846226415094m tC/year using primary prey factors, already above PC=.144. No printed-number typo is needed.','Use as an explicit supporting feeding variant with period/provenance warning; do not relabel it as recovered 2000-2014 author Q.'),
 hypothesis('J09','decimal on red inflow','F48 .046 was written instead of .46.','plausible author-error hypothesis, unsupported','The source literal is clearly .046 and its route is tentative; no independent source gives this exact hyperiid-to-jelly carbon flow.','Changing to .460 gives tentative QC=.4645, which passes P<Q, but the improvement is only arithmetic and supplies no evidence of a decimal typo.','Do not adopt; retain as an unverified sensitivity hypothesis only.'),
 hypothesis('J10','decimal on other red inflows','F50 .003 or F24 .0015 lost one or two powers of ten.','plausible author-error hypothesis, unsupported','The readable labels are .003 and .0015; their exact endpoints remain tentative.','F50x10 yields QC=.0775; F24x10 yields QC=.0640; F24x100 yields QC=.199. These arbitrary alternatives show why balancing is not source evidence.','No numeric correction is selected.'),
 hypothesis('J11','direction swap','Reversing outgoing jellyfish arrows fixes the intake failure.','rejected as a sufficient repair; one small route remains ambiguous','Adopted F39 jellyfish->squidIII .00001 is tentative. F55 .0006 visibly leaves jellyfish toward predatory salmon.','Even adding .0006 to .0505 gives .0511; adding .00001 gives .05051, both below PC=.144. The F55 visible arrow direction does not support reversal.','Retain original route evidence/confidence; do not reverse a clear head to repair balance.'),
 hypothesis('J12','route attribution','One or more F24/F48/F50 endpoints were assigned to jellyfish incorrectly.','plausible unresolved visual hypothesis','All three adopted positive jellyfish inflows are tentative. The source has crossing red arcs and white label knockouts.','If the adopted endpoints are wrong, .0505 is not the jellyfish Q at all. No exact replacement route was resolved by this audit.','Keep routing uncertainty explicit. Supporting-table feeding can be evaluated without resolving or overwriting these source curves.'),
 hypothesis('J13','supporting total transcription','Large jellyfish Q is772.8k in prose but772.7k in Table4.15.','supported small source inconsistency','Original p124 prose772.8; original Table4.15 p125 total772.7. Exclusive annual rows sum772.7.','Difference .1k wet; combined total3177.1k uses table772.7+2404.4. This difference is too small to explain the diagram deficit.','Preserve both; use tabulated772.7 for tabulated calculations.'),
 hypothesis('J14','full carbon Q recovery','All supporting jellyfish carbon Q is known exactly from Tables4.13-4.16.','rejected exact-total claim; supported partial recovery','Complete wet Q and prey amounts are tabulated, but residual prey lack established carbon factors/crosswalks within this audit. Small-jelly feeding is explicitly expert-based.','Known three-prey carbon subtotal=.2095846226415094; adding known jellyfish cannibalism gives=.2096996296541321. Residual wet food=.3089m remains unconverted.','Report partial Q_C/lower bound; do not manufacture residual prey conversion or normalize away unknowns.'),
]
table71_raw=[
 ('Copepods',['14.6','14.9','42.75','53.67','.15','.15','.062','.080','16.02','12.51']),
 ('Euphausiids',['19.0','21.0','41.77','52.27','.19','.21','.079','.110','12.60','9.11']),
 ('Mysids',['15.5','19.9','37.35','40.10','.16','.20','.058','.080','17.27','12.53']),
 ('Hyperiids',['15.7','17.9','38.22','43.39','.16','.18','.060','.078','16.66','12.88']),
 ('Pteropods',['10.8','10.9','41.57','51.57','.11','.11','.045','.056','22.27','17.79']),
 ('Oikopleura',['11.2','11.3','41.10','42.20','.11','.11','.046','.048','21.72','20.97']),
 ('Chaetognaths',['10.2','10.9','42.67','51.60','.10','.11','.044','.056','22.98','17.78']),
 ('Jellyfish',['3.6','4.0','8.67','8.95','.04','.04','.003','.004','320.27','279.33']),
 ('Other',['12.6','13.9','36.80','43.0','.13','.14','.050','.064','20.14','15.66']),
]
table71={'source_pdf':str(PAPERS/'gorbatenko_2018_dissertation.pdf'),'printed_page':298,'pdf_page_1_based':298,'source_render':'dissertation2018_p298_source.png','columns_in_source_order':['dry_matter_percent_winter_spring','dry_matter_percent_summer_autumn','carbon_in_dry_matter_percent_winter_spring','carbon_in_dry_matter_percent_summer_autumn','labelled_carbon_in_1mg_dry_mass_winter_spring','labelled_carbon_in_1mg_dry_mass_summer_autumn','carbon_in_1mg_wet_mass_winter_spring','carbon_in_1mg_wet_mass_summer_autumn','carbon_to_wet_factor_winter_spring','carbon_to_wet_factor_summer_autumn'],'problem_header_literal':'Углерод в 1 мг сухой массы','rows':[],'interpretation':'All 18 values in the problematic column equal the dry/wet fraction rounded to two decimals. They do not equal carbon/dry fraction. The mismatch is established; whether the header is wrong or an unintended intermediate column was copied cannot be decided from the original alone. Final conversion factors are preserved.','qualification':'The principal copepod, euphausiid and jellyfish final factors agree closely with reciprocals of dry fraction times carbon/dry fraction. Other has an additional discrepancy between products of displayed percentages and its displayed wet-carbon/factor columns; do not generalize perfect arithmetic agreement to every row. Group averages, covariance or unreported calculation inputs may matter, but no repair is inferred.'}
for prey,x in table71_raw:
    row={'prey':prey,'source_literals':dict(zip(table71['columns_in_source_order'],x)),'checks':[]}
    for i,season in enumerate(['winter_spring','summer_autumn']):
        dry=D(x[i])/D(100); cdry=D(x[2+i])/D(100); printed=D(x[4+i]); cwet=dry*cdry; factor=D(x[8+i])
        row['checks'].append({'season':season,'dry_mass_per_1mg_wet_mass':n(dry),'dry_fraction_round_two_decimals':n(dry.quantize(D('.01'))),'printed_problem_column':n(printed),'problem_column_matches_rounded_dry_fraction':dry.quantize(D('.01'))==printed,'carbon_per_1mg_dry_mass_from_source_percent':n(cdry),'wet_carbon_fraction_product':n(cwet),'wet_carbon_fraction_printed':x[6+i],'factor_reciprocal_of_displayed_percentage_product':n(D(1)/cwet),'final_factor_printed':x[8+i],'relative_difference_final_factor_vs_percentage_product_percent':n((factor/(D(1)/cwet)-D(1))*D(100))})
    table71['rows'].append(row)
assert all(c['problem_column_matches_rounded_dry_fraction'] for r in table71['rows'] for c in r['checks'])
dump('table7_1_heading_audit.json',table71)
hypotheses.extend([
 hypothesis('J15','supporting table heading/content','Table7.1 column labelled Carbon in 1mg dry mass contains dry/wet fractions instead.','supported heading/content mismatch; exact author intent unresolved','Original dissertation printed/PDFp298: all18 entries equal dry-matter percent/100 rounded to2 decimals. Jellyfish .04/.04 is incompatible with directly printed carbon/dry fractions8.67%/8.95%, which imply .0867/.0895 mgC per mgdry.','Copepod .146*.4275=.062415 implies factor16.0217896 versus printed16.02; euphausiid .190*.4177=.079363 implies12.6003291 versus12.60; jellyfish .036*.0867=.0031212 implies320.3896 versus320.27 and .040*.0895=.00358 implies279.3296 versus279.33. These principal factors are coherent despite the intermediate-heading mismatch. Other-row displayed percentages do not exactly reproduce its final factors; that distinct discrepancy is retained without a correction.','Record a likely human table-presentation error. Preserve final Table7.1 factors, primary285.20 and production.144. Do not use the mislabelled intermediate column as carbon/dry composition.'),
 hypothesis('J16','energy vs carbon assimilation','The dissertation70% assimilation directly establishes Ecopath carbon unassimilated fractionGS=.30.','supported energy parameter; carbon equivalence is an assumption','Dissertationp123 describes Winberg energy-balance ration calculations using70% food assimilation and temperature. It does not tabulate a2019 carbonGS parameter.','1-.70=.30 is the implied unassimilated fraction on the energy basis. Applying that to carbon assumes equal or sufficiently comparable energy/carbon assimilation. The source does not independently establish that equivalence.','A derivative carbon model may useGS=.30 only with the energy-to-carbon equivalence assumption explicit; preserve it as an assumption rather than a recovered exact2019 carbon parameter.'),
])
ledger={
 'audit_date':'2026-10-03',
 'question':'Does a source-backed jellyfish typo/unit/direction/decimal repair exist, and can alternate feeding recover carbon intake without a typo claim?',
 'sources':[{'path':str(PAPERS/name),'sha256':hashlib.sha256((PAPERS/name).read_bytes()).hexdigest()} for name in ['gorbatenko_melnikov_2019.pdf','gorbatenko_2018_dissertation.pdf']],
 'classification_contract':'Supported means directly established by original source or arithmetic; plausible means a specific unresolved possibility without correction evidence; rejected means contradicted or insufficient as a source-supported correction, not proof an author could never err.',
 'verdict':'Primary Pwet41/PC.144 is internally correct. No numeric typo correction is justified. The tentative diagram sum is not complete author Q. Supporting wet prey rows recover a carbon subtotal above PC without altering a printed value; complete carbon Q remains partly unknown and the periods differ.',
 'hypotheses':hypotheses,
 'source_figure_incoming':[{'flow_id':'F24','literal':'0,0015','adopted_route':[7,14],'route_confidence':'tentative'},{'flow_id':'F48','literal':'0,046','adopted_route':[6,14],'route_confidence':'tentative'},{'flow_id':'F50','literal':'0,003','adopted_route':[11,14],'route_confidence':'tentative'}],
 'source_figure_outgoing':[{'flow_id':'F39','literal':'0,00001','adopted_route':[14,9],'route_confidence':'tentative'},{'flow_id':'F55','literal':'0,0006','adopted_route':[14,17],'route_confidence':'clear; visually downward arrow into predatory salmon'}],
 'source_figure_absence':'No labelled/unlabelled blue incoming feeding head to jellyfish found in the visible Figure9 raster. This bounded negative finding was audited previously and checked again in the current local source crop. A passing blue outer curve is not an incoming jellyfish endpoint.',
 'raw_data_policy':'No raw source, baseline/canonical/selected model, CSV or workbook is edited. All calculations and sensitivity examples live here only.',
 'evidence_files':['primary2019_p12_source.png','primary2019_table3_jelly_row_source.png','primary2019_p15_source.png','dissertation2018_p123_source.png','dissertation2018_p124_source.png','dissertation2018_p125_source.png','dissertation2018_p298_source.png','jellyfish_figure9_local_source_native.png','source_evidence.json'],
 'calculation_file':'jellyfish_source_calculations.json',
 'source_table_file':'dissertation_tables_4_13_to_4_16.json',
 'table7_1_heading_audit_file':'table7_1_heading_audit.json',
 'energy_assimilation_scope':'The dissertation70% is an energy assimilation coefficient. Any carbonGS=.30 application requires a separately stated equivalence assumption.',
}
dump('jellyfish_error_hypothesis_ledger.json',ledger)

findings=f'''Jellyfish focused source/error audit - 2026-10-03

The primary Pwet41 / PC0.144 pairing is internally correct: Bwet4.10*PB10.0=41.0, and 41.0/285.20={PC_exact}, rounding to .144. The printed BC=.01 is a coarse rounding of4.10/285.20={BC_exact}; using that rounded stock as exact explains a separate apparent PB/PC mismatch. Figure9 clearly repeats .144 as production. No production decimal, PB, unit or production/consumption swap is supported.

The adopted Figure9 jellyfish QC=.0505 is not an author-tabulated total Q. It is .0015+.046+.003 under three tentative red routes (F24/F48/F50). Outgoing F39=.00001 remains tentative; F55=.0006 visibly points from jellyfish to predatory salmon. No blue feeding arrowhead into jellyfish was found. The article explicitly calls the diagram a generalized scheme.

Original dissertation Tables4.15/4.16 (printed/PDFp125) give annual consumption772.7k wet for large jellyfish and2404.4k for small jellyfish, total3177.1k=3.1771m wet. Combined annual prey amounts include copepods2477.3k, euphausiids332.2k, chaetognaths25.9k and jellyfish32.8k. Applying primary prey factors14.0,10.6,20.0 yields carbon subtotal{three}m tC/year. Including cannibalism at285.20 yields{four}. Both are above primary PC=.144, without changing a printed number or claiming a typo.

Complete carbon Q is not exactly known from these sources alone: .3089m wet residual remains unconverted after the four mapped prey. Amphipods36.7k cannot be silently treated as hyperiids; fish eggs/larvae, meroplankton, pteropods, mysids, decapod larvae and Other need appropriate factors/crosswalks. Small-jelly feeding is described as expert-based, not fully observed. The supporting consumption period2006-2014 differs from primary production2000-2014. This is a source-derived alternative feeding comparison, not recovered author Q for the primary period.

Do not divide total jellyfish food Qwet by the jellyfish body factor285.2: prey-specific factors govern food carbon. Doing that would give only{(total/D(1000))/D('285.20')}m tC and mis-handle heterogeneous food. A standard wet-mass Ecopath balance is also not established by the carbon comparison: Pwet/Qwet={P_wet/(total/D(1000))}>1. No full balance verdict follows from a necessary carbon P<Q check.

One minor source inconsistency is real: p124 prose says large Q772.8k, while Table4.15 and its exclusive annual prey rows give772.7k. Both are retained; table controls tabulated sums. Hypothesized powers-of-ten changes in .046,.003,.0015 can alter balance but have no independent source support; no such correction is selected.

Table7.1 (original printed/PDFp298) has a supported heading/content mismatch: all18 values labelled carbon in1mgdry mass equal dry/wet fractions rounded to2 decimals. Jellyfish .04/.04 therefore cannot be read as carbon/dry composition; directly printed8.67%/8.95% implies .0867/.0895. The principal copepod/euphausiid/jellyfish final wet-carbon factors remain coherent with the percentage products. Other has a separate arithmetic discrepancy between the displayed percentage products and final columns; it is preserved without inventing a repair. See table7_1_heading_audit.json. No production correction follows from this presentation issue.

The dissertation's70% food assimilation onp123 is an energy-balance parameter. Interpreting its complement as carbonGS=.30 requires an explicit energy-to-carbon assimilation equivalence assumption; it is not a directly recovered2019 carbonGS input.

See jellyfish_error_hypothesis_ledger.json for16 supported/plausible/rejected cases; jellyfish_source_calculations.json for exact Decimal calculations; dissertation_tables_4_13_to_4_16.json for original literals and layout mapping. Native figure crops retain exact source pixels; PDF pages are original renders. All work is confined to this audit directory, with no raw/canonical/selected model edits.
'''
(OUT/'FINDINGS.txt').write_text(findings,encoding='utf-8')

qa={'json_files':['source_evidence.json','dissertation_tables_4_13_to_4_16.json','jellyfish_source_calculations.json','jellyfish_error_hypothesis_ledger.json','table7_1_heading_audit.json'],'hypothesis_count':len(hypotheses),'table7_1_all18_problem_values_match_dry_fraction':True,'exclusive_annual_prey_sum_thousand_t':n(sum(annual.values())),'table_total_thousand_t':n(total),'annual_total_matches':sum(annual.values())==total,'production_pair_correct_to_printed_precision':PC_exact.quantize(D('.001'))==P_C,'all_work_within':str(OUT),'source_hashes':ledger['sources'],'baseline_ledger_hash_at_audit_end':hashlib.sha256((MODEL/'audit'/'flow_readings.json').read_bytes()).hexdigest()}
for fname in qa['json_files']: json.loads((OUT/fname).read_text(encoding='utf-8'))
dump('verification.json',qa)
print('Source tables, Decimal calculations, 16-case error-hypothesis ledger and findings saved.')
print('Production PC rounds to:',PC_exact.quantize(D('.001')))
print('Three-prey carbon subtotal:',three,'Full wet Q:',total/D(1000))
