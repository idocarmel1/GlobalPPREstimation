"""Bounded supporting-source recovery, without changing existing model inputs."""
from pathlib import Path
from decimal import Decimal as D
import json, hashlib, pymupdf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
PAPERS=ROOT/'regions/LME_052/papers/OKH-GM2019'
dissertation=PAPERS/'gorbatenko_2018_dissertation.pdf'
doc=pymupdf.open(dissertation)
sha=hashlib.sha256(dissertation.read_bytes()).hexdigest()
def save(name,obj): (HERE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def num(x): return str(x)

species=[
 ('Pink salmon','1273.2','476.9','III'),
 ('Chum salmon','453.34','225.7','III'),
 ('Sockeye salmon','70.4','37.6','III'),
 ('Chinook salmon','5.6','3.0','IV hypothesis'),
 ('Coho salmon','20.8','9.5','IV hypothesis'),
 ('Masu salmon','13.7','5.3','IV hypothesis'),
]
salmon=[]
for name,q,b,group in species:
 salmon.append(dict(species=name,annual_consumption_thousand_wet_t=q,stock_thousand_wet_t=b,tentative_figure_crosswalk=group,QB_using_this_stock_per_year=num(D(q)/D(b)),source='2018 dissertation Table 4.52, printed/PDF p.169',scope='2000–2014 means for presence/residence in the Okhotsk Sea, not year-round extrapolation'))
q3=sum((D(r[1]) for r in species if r[3]=='III'),D(0))
b3=sum((D(r[2]) for r in species if r[3]=='III'),D(0))
q4=sum((D(r[1]) for r in species if r[3]!='III'),D(0))
b4=sum((D(r[2]) for r in species if r[3]!='III'),D(0))
salmon_targets=dict(source_sha256=sha,species_rows=salmon,reported_all_salmon_Q_thousand_wet_t='1837.0',reported_all_salmon_B_thousand_wet_t='758.0',sum_species_Q_thousand_wet_t=num(q3+q4),sum_species_B_thousand_wet_t=num(b3+b4),crosswalkIII=dict(Q_thousand_wet_t=num(q3),B_thousand_wet_t=num(b3),QB_with_dissertation_stock=num(q3/b3),QB_with_2019_Table3_B_800kt=num(q3/D(800)),basis='2019 p.155 / PDF p.13 and dissertation p.318 explicitly identify III salmon production as pink+chum+sockeye',status='Independently source-supported species aggregate; distinct from Figure9 arrow-implied Q'),crosswalkIV=dict(Q_thousand_wet_t=num(q4),B_thousand_wet_t=num(b4),QB_with_dissertation_stock=num(q4/b4),QB_with_2019_Table3_B_20kt=num(q4/D(20)),basis='Chinook/coho/masu nekton-feeding species; consistent approximately with Table3 predatory-salmon biomass20kt, but species-to-figure crosswalk remains an interpretation'),residence_evidence='Dissertation p.163 explicitly calculates consumption during the entire period of presence in the sea. Table4.43 p.164 uses pink-salmon summer2months and autumn3months. No multiplying residence Q by365days.',carbon_Q_complete=False,carbon_Q_limitation='Table4.52 includes pteropods, decapods, appendicularians, gelatinous organisms, squid and unspecified fish. Several are absent from Figure9 and lack exact matched prey conversion/group allocation. Consumer factor8.2 must not convert total prey wet Q.',adopted_into_model=False)
save('followup_salmon_recovery.json',salmon_targets)

large=[('Euphausiids','286.9','10.6'),('Copepods','299.2','14'),('Amphipods','36.7',None),('Chaetognaths','25.9','20'),('Pteropods','5.8',None),('Mysids','5.7',None),('Decapod larvae','4.8',None),('Jellyfish','32.8',None),('Fish eggs','62.9',None),('Fish larvae','12.0',None)]
small=[('Copepods','2178.1','14'),('Euphausiids','45.3','10.6'),('Meroplankton','63.9',None),('Other','117.1',None)]
preys=[]
for label,rows in [('large>20mm',large),('small<20mm',small)]:
 for name,q,f in rows:
  preys.append(dict(consumer_subset=label,prey=name,annual_Q_thousand_wet_t=q,matched_2019_prey_wet_per_carbon=f,partial_carbon_Q_million_tC_per_year=num(D(q)/D(1000)/D(f)) if f else None,factor_status='Direct matching taxonomic factor from2019Table3' if f else 'Not assigned: extra group or uncertain crosswalk'))
known=sum((D(r['partial_carbon_Q_million_tC_per_year']) for r in preys if r['partial_carbon_Q_million_tC_per_year']),D(0))
largeB=sum(map(D,['1022','2539','1618','1329']))/4
smallB=sum(map(D,['1185','11230','555','912']))/4
jelly=dict(source_sha256=sha,source_period='2006–2014',source='Dissertation Tables4.13–4.16, pp.124–125',consumer_scope='Both small<20mm mostly hydromedusae and large>20mm mostly scyphomedusae in whole-Sea epipelagic network',reported_large_Q_thousand_wet_t='772.7',prose_large_Q_thousand_wet_t='772.8',reported_small_Q_thousand_wet_t='2404.4',combined_Q_thousand_wet_t='3177.1',source_seasonal_large_B_thousand_wet_t=['1022','2539','1618','1329'],source_seasonal_small_B_thousand_wet_t=['1185','11230','555','912'],equal_season_mean_large_B_thousand_wet_t=num(largeB),equal_season_mean_small_B_thousand_wet_t=num(smallB),equal_season_mean_combined_B_thousand_wet_t=num(largeB+smallB),QB_from_same_table_equal_season_B=num(D('3177.1')/(largeB+smallB)),mixed_scope_QB_using_2019_Table3_B_4100kt=num(D('3177.1')/4100),same_scope_P_not_recovered=True,alignment='Period differs from2000–2014. Tables4.13 stock average5.0975million wet tonnes differs from2019Table3B4.1million. No independent matching P41million t/y for these size subsets found. Keep as alternate target.',source_internal_stock_note='Dissertation Table3.9 p.88 gives small summer11953/autumn703/winter974kt instead of11230/555/912 in Table4.13; Table4.13 is the stock linked explicitly to feeding calculation. Do not harmonize.',prey_rows=preys,independently_converted_known_prey_carbon_lower_bound_million_tC_per_year=num(known),partial_R_using_2019_P_0_144_and_user_GS_0_2=num(D('.8')*known-D('.144')),energy_scope_note='Known copepod/euphausiid/chaetognath consumption alone exceeds0.18million tC/y, but comparison to2019P is mixed period/stock scope and is not a validation.',complete_carbon_Q=None,complete_conversion_missing='Pteropods,mysids,decapod larvae,meroplankton,other,fish eggs/larvae and uncertain amphipod/jellyfish crosswalks. No automatic assignment to source nodes.',source_assimilation_fraction='0.70',source_assimilation_scope='Dissertation pp.120,123 calculates jellyfish daily rations using70% assimilation and energy balance; not an independent assimilation measurement.',user_GS_0_2_unchanged=True,small_jelly_consumption_quality='Explicitly predominantly expert estimates because small-jellyfish feeding is insufficiently studied, pp.124–125.',figure9_conflict='Independent prey consumption includes copepods and euphausiids absent from adopted Figure9 jellyfish diet. Do not add arrows or rescale existing Figure9 values.',adopted_into_model=False)
save('followup_jellyfish_recovery.json',jelly)

snippets=[]
for page in [59,60,120,123,124,125,157,158,163,164,169,318]:
 snippets.append(dict(source='gorbatenko_2018_dissertation.pdf',pdf_page=page,printed_page=page,source_sha256=sha,exact_page_text=doc[page-1].get_text()))
save('followup_original_page_text.json',snippets)
save('followup_recovery_verification.json',dict(original_hash_unchanged=hashlib.sha256(dissertation.read_bytes()).hexdigest()==sha,original_written=False,baseline_written=False,balanced_model_created=False,salmonIII_Q_thousand_wet_t=num(q3),jellyfish_known_carbon_Q_lower_bound=num(known),microbial_annual_B_PB='No independently recovered separate whole-Sea2000–2014 annualB/PB. Only local summer bacteria stocks/PB0.2–0.9 adjacent to daily production and pooled stock64.0/PB20 remain.'))
print('Saved bounded recovery artifacts')
