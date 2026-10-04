"""Primary-source recovery only. No model changes, diet fitting, or normalization."""
from pathlib import Path
from decimal import Decimal as D, getcontext
import csv,hashlib,json,pymupdf
getcontext().prec=40
HERE=Path(__file__).resolve().parent
CANDIDATE=HERE.parents[2]
ROOT=HERE.parents[6]
PAPERS=ROOT/'regions/LME_052/papers/OKH-GM2019'
protected=[PAPERS/'gorbatenko_2018_dissertation.pdf',PAPERS/'gorbatenko_melnikov_2019.pdf',CANDIDATE/'model.json',CANDIDATE/'assumption_variants/researcher_readings_20261003/model.json',CANDIDATE/'assumption_variants/researcher_readings_20261003/carbon_reconstruction.json']
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
def save(name,obj): (HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def csvsave(name,rows):
 with (HERE/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
  w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows)
doc=pymupdf.open(PAPERS/'gorbatenko_2018_dissertation.pdf')
evidence=[]
for p in [116,117,118,161,162,163,164,165,166,168,169,170,171,297,298,307,456]:
 evidence.append(dict(source=doc.name,source_sha256=hashes[str(Path(doc.name))],pdf_page=p,printed_page=p,exact_pdf_text=doc[p-1].get_text()))
for p in [117,169,298]:doc[p-1].get_pixmap(matrix=pymupdf.Matrix(1.6,1.6)).save(str(HERE/f'dissertation_p{p}.png'))
article=pymupdf.open(PAPERS/'gorbatenko_melnikov_2019.pdf')
for p in [11,13]:evidence.append(dict(source=article.name,source_sha256=hashes[str(Path(article.name))],pdf_page=p,printed_page=p+142,exact_pdf_text=article[p-1].get_text()))
save('original_page_evidence.json',evidence)

hyper=dict(group_id=6,source='2018 dissertation Table4.11, printed/PDF p.117',period='2000–2014',scope='Whole-Sea Okhotsk epipelagic',unit='million wet tonnes/year',Q='152.5',prey_rows=[dict(source_prey='Копеподы',English='Copepods',annual_wet_Q='56.7',printed_mass_percent='37.2',model_prey_ids=[4]),dict(source_prey='Прочие',English='Other food',annual_wet_Q='95.8',printed_mass_percent='62.8',model_prey_ids=None)],ration_status='Explicit source expert estimate; no special ration studies in the Okhotsk Sea and no available subarctic ration data',seasonal_table=[dict(season=s,copepod_3month_Q=c,other_3month_Q=o,total_3month_Q=t,hyperiid_stock=b,ration_percent=q) for s,c,o,t,b,q in [('spring','7.3','10.8','18.1','3.1','6.5'),('summer','18.1','25.1','43.2','6','8.0'),('autumn','20.7','35.4','56.1','8.9','7.0'),('winter','10.5','24.6','35.1','6.5','6.0')]],complete_source_two_category_breakdown=True,complete_22_group_diet=False,normalization_performed=False,adopted_into_model=False,qualitative_other_food=['euphausiids','chaetognaths','jellyfish and other gelatinous organisms','decapod larvae','fish larvae','hyperiid young/cannibalism','phytoplankton (species-specific cited T.libellula evidence)','dead or weakened organisms'],qualitative_food_scope='pp.116–117 broad/cited Themisto diets, not quantified whole-Sea annual allocations')
save('hyperiid_table_4_11.json',hyper)

# These passages are qualitative context, not a quantitative decomposition of Other.
other_evidence = [
 dict(printed_page=116,pdf_page=116,Russian='Большинство Hyperiidae плотоядны (Sheader, Evans, 1975; Auel et al., 2002), а Themisto являются хищниками с широким спектром питания, основу рациона которых составляют копеподы, эвфаузииды, сагитты, медузы, а также личинки декапод и рыб (Sheader, Evans, 1975).',English='Most Hyperiidae are carnivorous; Themisto have a broad diet whose main foods include copepods, euphausiids, chaetognaths, jellyfish, and decapod and fish larvae.',prey_categories=['copepods','euphausiids','chaetognaths','jellyfish','decapod larvae','fish larvae'],scope='General/cited Hyperiidae and Themisto feeding, not a quantified 2000–2014 group diet.'),
 dict(printed_page=116,pdf_page=116,Russian='Гиперииды, за исключением крупных T. libellula, в большинстве случаев относятся не к настоящим хищникам, а к хищникам-трупоедам, поедающим наряду с живой пищей мертвых или ослабленных особей.',English='Except for large T. libellula, hyperiids are frequently predators and scavengers, consuming dead or weakened individuals as well as live prey.',prey_categories=['dead organisms','weakened organisms'],scope='Carrion is explicit; no mass or assignment to an Ecopath detritus pool is supplied.'),
 dict(printed_page=116,pdf_page=116,Russian='Для крупной T. libellula наиболее распространенная добыча, обнаруженная в содержимом пищеварительного тракта, – копеподы (каланусы), амфиподы (включая свой собственный вид), щетинкочелюстные и личинки рыб',English='Common prey observed in large T. libellula guts include copepods, amphipods including its own species, chaetognaths and fish larvae.',prey_categories=['copepods','amphipods','conspecifics','chaetognaths','fish larvae'],scope='Cited species-specific gut observations; no annual group allocations.'),
 dict(printed_page=116,pdf_page=116,Russian='Желетелый планктон в пище не обнаружен, хотя известно, что другие разновидности гипериид питаются медузами, гребневиками и морскими оболочниками',English='Gelatinous plankton was not observed in this diet, although other hyperiids are known to feed on jellyfish, ctenophores and marine tunicates.',prey_categories=['jellyfish','ctenophores','marine tunicates'],scope='Different hyperiid species; author discusses possible rapid digestion and suspected gelatinous feeding by T. libellula. Not a measured whole-group split.'),
 dict(printed_page=117,pdf_page=117,Russian='Следы жирных кислот у T. libellula подтвердили значение копепод как главного источника липидов, а также наличие в рационе фитопланктона и каннибализма.',English='Fatty-acid traces in T. libellula supported copepods as the main lipid source and indicated phytoplankton feeding and cannibalism.',prey_categories=['copepods','phytoplankton','conspecifics'],scope='Cited species-specific evidence continued from p.116; no annual mass.'),
 dict(printed_page=117,pdf_page=117,Russian='С одной стороны, они потребляют планктон, включая собственную молодь, с другой – сами являются важной добычей лососей, минтая и сельди.',English='Hyperiids consume plankton, including their own young, and are themselves important prey for salmon, pollock and herring.',prey_categories=['plankton','hyperiid young'],scope='Authors general whole-Sea trophic interpretation; no fraction or subtype split.'),
]
for row in other_evidence:
 row.update(source='Gorbatenko 2018 dissertation',numeric_quantity=None,allocated_Table4_11_Other_mass=None,normalization_performed=False)
save('hyperiid_other_food_evidence.json',dict(records=other_evidence,exact_passage_policy='PDF line-wrap hyphens removed; numeric information not added.',Table4_11_Other_mass_million_wet_tonnes='95.8',quantitative_decomposition_identified=False,microheterotroph_link_identified=False,detritus_pool_assignment_identified=False,Table7_1_Other_category_match_identified=False))

species=['pink','chum','sockeye','Chinook','coho','masu']
# Exactly12 source feeding rows, including the two class subtotals.
specs=[('Эвфаузииды','Euphausiids',['357.0','109.5','5.4','0.35','2.36','0.70'],'475.4','25.9',False),('Амфиподы','Amphipods',['675.3','157.2','35.3','0.02','1.49','0.58'],'869.9','47.4',False),('Копеподы','Copepods',['23.2','12.8','15.3','0.02','0.18','0.19'],'51.7','2.8',False),('Сагитты','Chaetognaths',['34.9','25.4','0.2','0.00','0.18','0.05'],'60.8','3.3',False),('Птероподы','Pteropods',['48.9','21.8','6.1','0.01','0.20','0.03'],'76.9','4.2',False),('Декаподы','Decapods',['13.7','3.8','1.6','0.12','0.32','0.11'],'19.6','1.1',False),('Ойкоплевры','Oikopleura',['21.2','40.0','0.0','0.00','0.12','0.10'],'61.5','3.3',False),('Желетелые','Gelatinous organisms',['0.7','44.0','0.1','0.00','0.08','0.15'],'45.1','2.5',False),('Планктон','Plankton subtotal',['1174.9','414.5','64.2','0.52','4.93','1.92'],'1660.9','90.4',True),('Нектон','Nekton subtotal',['98.1','38.9','6.2','5.05','15.90','11.81'],'175.9','9.6',True),('Кальмары','Squid',['29.6','12.8','4.5','2.00','4.04','1.11'],'54.0','2.9',False),('Рыбы','Fish',['68.8','26.0','1.7','3.04','11.86','10.69'],'122.1','6.6',False)]
Q8=sum(D(x) for x in ['1273.2','453.34','70.4'])
source_rows=[]
for ru,en,values,total,pct,subtotal in specs:
 source_rows.append(dict(Russian_prey=ru,English_prey=en,**dict(zip(species,values)),all_salmon_printed_total=total,all_salmon_printed_mass_percent=pct,subtotal_do_not_double_count=subtotal,source='Dissertation Table4.52 p.169',unit='thousand wet tonnes/year',derived_group8_Q=sum(D(x) for x in values[:3]).to_eng_string()))
save('salmon_table_4_52_rows.json',source_rows);csvsave('salmon_table_4_52_rows.csv',source_rows)
save('salmon_table_4_52_totals_and_scope.json',dict(total_Q_by_species=dict(zip(species,['1273.2','453.34','70.4','5.6','20.8','13.7'])),B_by_species=dict(zip(species,['476.9','225.7','37.6','3.0','9.5','5.3'])),all_salmon_printed_Q='1837.0',group8_Q_thousand_wet_tonnes=str(Q8),group8_Q_million_wet_tonnes=str(Q8/1000),group8_species=['pink','chum','sockeye'],crosswalk='2019p.155 explicitly calculates tierIII salmon production for pink/chum/sockeye; dissertationp.162 defines predatory salmon as Chinook/coho/masu',period='2000–2014',residence_scope='Annual source totals already integrate summer2-month/adults and autumn3-month/young residence; do not extrapolate to365days.',complete_native_model=False))

factor_specs=[('Copepods','16.02','12.51',[4]),('Euphausiids','12.60','9.11',[5]),('Mysids','17.27','12.53',None),('Hyperiids','16.66','12.88',[6]),('Pteropods','22.27','17.79',None),('Oikopleura','21.72','20.97',None),('Chaetognaths','22.98','17.78',[7]),('Jellyfish','320.27','279.33',[14]),('Other zooplankton','20.14','15.66',None)]
factors=[dict(source_prey=n,winter_spring_wet_per_carbon=w,summer_autumn_wet_per_carbon=s,model_prey_ids=ids,source='Dissertation Table7.1 printed/PDF p.298',unit='wet mass/carbon mass',source_SE_note='Table note: ±SE no greater than10%',adopted_into_model=False) for n,w,s,ids in factor_specs]
save('seasonal_prey_conversion_factors.json',factors);csvsave('seasonal_prey_conversion_factors.csv',factors)

crosswalk={'Euphausiids':([5],'Exact named group'), 'Amphipods':([6],'Source-supported aggregate: annual table says Amphipoda; nearby salmon prose identifies its main food as hyperiids. Amphipoda is broader than Hyperiidea; mapping all row mass is a documented taxonomic lump, not an independently measured subtype split.'),'Copepods':([4],'Exact named group'),'Chaetognaths':([7],'Exact named group'),'Pteropods':(None,'Absent from22-group network; own source category/factors available'),'Decapods':(None,'Absent from22-group network; no matched pelagic-dec apod factor recovered. Table7.1 Other zooplankton does not explicitly identify decapods.'),'Oikopleura':(None,'Absent from22-group network; own source category/factors available'),'Gelatinous organisms':(None,'Not exactly group14 jellyfish: sourcep.162 includes coelenterates, ctenophores, doliolids and salps. No numerical split recovered.'),'Squid':([9,16],'Pooled squid mass; no isotope-tier/species allocation recovered'),'Fish':(None,'Pooled fish mass; prose mentions juvenilepollock and other youngfish, but no whole-year species/size allocation recovered')}
ledger=[]
for row in source_rows:
 if row['subtotal_do_not_double_count']:continue
 ids,note=crosswalk[row['English_prey']]
 q=D(row['derived_group8_Q'])
 ledger.append(dict(prey=row['English_prey'],source_prey=row['Russian_prey'],source_Q_by_species={sp:row[sp] for sp in species[:3]},group8_Q_thousand_wet_tonnes=str(q),group8_Q_million_wet_tonnes=str(q/1000),fraction_of_independent_group8_total_Q=str(q/Q8),model_prey_ids=ids,crosswalk_status=note,source='Dissertation Table4.52 p.169',adopted_into_model=False))
leaf=sum(D(r['group8_Q_thousand_wet_tonnes']) for r in ledger)
save('salmon_group8_prey_ledger.json',dict(rows=ledger,source_group8_Q_thousand_wet_tonnes=str(Q8),sum_printed_leaf_Q_thousand_wet_tonnes=str(leaf),leaf_minus_source_total=str(leaf-Q8),fractions_sum=str(leaf/Q8),normalization_performed=False,complete_22_group_diet=False,complete_taxonomic_category_listing=True,exact_numeric_closure=False))
save('supporting_table_differences.json',dict(mysids=dict(source='Table4.47 p.166',sockeye_annual_Q_thousand_wet_tonnes='.1',included_as_named_row_in_Table4_52=False,model_prey_ids=None,factors_available='Table7.1 winter/spring17.27 summer/autumn12.53',not_silently_added_to_Table4_52=True),chum_differences_4_45_vs_4_52={'Decapods':['3.7','3.8'],'Pteropods':['21.7','21.8'],'Gelatinous':['44.1','44.0'],'Fish':['26.1','26.0'],'Plankton_subtotal':['414.4','414.5']},sockeye_total_4_47_vs_4_52=['70.3','70.4'],salmon_Table4_54_copy_error=dict(source='Dissertationp.171',salmon_copepod_million_wet_tonnes='.87',salmon_amphipod_million_wet_tonnes='.05',assessment='Opposite ofTable4.52/individualspecies: copepods≈.0517 andamphipods≈.8699. Table4.54 rows appear swapped in salmon column. Use direct species tables; do not silently import this summary.'),Oikopleura_C_percent_summer_autumn=dict(table_7_1='42.20',appendix_46_p456='40.80',assessment='Printed factors20.97/21.72 retained as source observations; Appendix46 does not exactly reconstruct theTable7.1 summer factor.')))

quant={r['prey']:D(r['group8_Q_million_wet_tonnes']) for r in ledger}
main={'Euphausiids':'10.6','Amphipods':'14.5','Copepods':'14','Chaetognaths':'20'}
cases=[('Existing2019 main factors; extra prey largest seasonal factors',dict(main,**{'Pteropods':'22.27','Oikopleura':'21.72'})),('Existing2019 main factors; extra prey summer/autumn factors',dict(main,**{'Pteropods':'17.79','Oikopleura':'20.97'})),('All six summer/autumn Table7.1 factors',{'Euphausiids':'9.11','Amphipods':'12.88','Copepods':'12.51','Chaetognaths':'17.78','Pteropods':'17.79','Oikopleura':'20.97'})]
bounds=[]
for name,fac in cases:
 comp=[dict(prey=n,Q_million_wet_tonnes=str(quant[n]),wet_per_carbon=f,Q_million_tC=str(quant[n]/D(f))) for n,f in fac.items()]
 q=sum(D(x['Q_million_tC']) for x in comp)
 ceiling=1-D('.105')/q
 bounds.append(dict(case=name,components=comp,known_carbon_Q_lower_bound=str(q),P_carbon_unchanged='.105',R_lower_bound_at_GS_0p10=str(D('.9')*q-D('.105')),GS_ceiling_guaranteed_by_known_prey_only=str(ceiling),nominal_positive_R_at_GS_0p10=D('.9')*q>D('.105'),requires_documented_Amphipoda_to_hyperiid_lump=True,uncertainty_note='Point calculations on rounded source values; conversionfactorSE does not yield a strict probabilistic guarantee. First two cases retain2019 primary prey factors; third is an independent seasonal conversion alternative.',full_Q_or_DC_identified=False,complete_native_model=False,remaining_unconverted_categories=['Decapods','Gelatinous organisms','Squid','Fish']))
save('salmon_carbon_energy_bounds.json',bounds)
known=D('56.7')/D('14')
needs=[]
for GS in ['.10','.35']:
 required=D('4.752')/(1-D(GS))-known
 needs.append(dict(GS=GS,required_other_Q_carbon_for_R_nonnegative=str(required),maximum_effective_other_wet_per_carbon=str(D('95.8')/required),positive_R_requires_strict_inequality=True))
save('hyperiid_carbon_feasibility_constraints.json',dict(known_copepod_carbon_Q=str(known),P_carbon_unchanged='4.752',other_wet_Q='95.8',constraints=needs,Table7_1_Other_factors=['20.14','15.66'],Other_crosswalk_assessment='Not an established match. Table4.11 Other food means all prey except copepods; nearby prey include groups separately enumerated inTable7.1 (euphausiids, chaetognaths, jellyfish/hyperiids). Table7.1 Other zooplankton is the residual composition category after these named groups. Identical wordOther doesnot establish identicaltaxonomic mixture.',applying_Other_factor_is_an_additional_assumption=True,full_carbon_Q_identified=False,complete_22_group_DC=False,energy_failure_resolved_from_recovered_evidence_alone=False))

# Explicit hybrid constraints preserve the article's euphausiid Figure flow inside,
# rather than on top of, the dissertation's Other wet mass.
euphC=D('.283');euphWet=euphC*D('10.6');residualOther=D('95.8')-euphWet
hybridKnown=known+euphC
hybridConstraints=[]
for GS in ['.10','.35']:
 required=D('4.752')/(1-D(GS))-hybridKnown
 hybridConstraints.append(dict(GS=GS,required_residual_other_Q_carbon_for_R_nonnegative=str(required),maximum_effective_residual_other_wet_per_carbon=str(residualOther/required),positive_R_requires_strict_inequality=True))
save('hyperiid_text_plus_figure_constraints.json',dict(group_id=6,source_total_Q_million_wet_tonnes='152.5',copepod_text_wet_Q='56.7',copepod_carbon_factor='14',copepod_carbon_Q=str(known),retained_Figure_euphausiid_arrow='F13',Figure_euphausiid_carbon_Q=str(euphC),euphausiid_carbon_factor='10.6',derived_euphausiid_wet_Q=str(euphWet),source_Other_wet_Q='95.8',remaining_Other_wet_Q=str(residualOther),known_carbon_Q=str(hybridKnown),consistency_assumption='The clear Figure9 euphausiid flow is included inside the Table4.11 Other wet mass, not added as food beyond the source total. Qualitative source prose supports euphausiid presence; the exact nesting is a documented cross-source reconciliation.',constraints=hybridConstraints,complete_22_group_DC=False,full_carbon_Q_identified=False,normalization_performed=False,adopted_into_model=False,source_Figure_other_flows_not_reclassified=True))
verification=dict(only_this_recovery_directory_written=True,canonical_originals_unchanged=all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p)] for p in protected),salmon_source_rows=12,salmon_leaf_rows=10,group8_independent_Q_thousand_wet_tonnes=str(Q8),source_leaf_minus_total_thousand_wet_tonnes=str(leaf-Q8),normalization_performed=False,hyperiid_other_unallocated=True,model_ready=False,hashes=hashes)
assert verification['canonical_originals_unchanged'] and len(source_rows)==12 and len(ledger)==10
save('verification.json',verification)
print('Saved primary tables, evidence, seasonal factors and bounded feasibility; no complete22-group diet claimed.')
