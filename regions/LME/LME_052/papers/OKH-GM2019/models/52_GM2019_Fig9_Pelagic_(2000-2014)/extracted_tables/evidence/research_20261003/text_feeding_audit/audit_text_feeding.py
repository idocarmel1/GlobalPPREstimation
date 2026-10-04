"""Exhaustive 21-page 2019-only prose audit, with no model mutation."""
from pathlib import Path
from decimal import Decimal as D
import csv,hashlib,json,re,pymupdf

HERE=Path(__file__).resolve().parent
CANDIDATE=HERE.parents[1]
ROOT=HERE.parents[5]
PAPERS=ROOT/'regions/LME_052/papers/OKH-GM2019'
SOURCE=PAPERS/'gorbatenko_melnikov_2019.pdf'
doc=pymupdf.open(SOURCE)
assert len(doc)==21
sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
raw={i+1:p.get_text() for i,p in enumerate(doc)}
def clean(s):
 s=s.replace('\u00ad\n','').replace('\u00ad','')
 s=re.sub(r'(?<=[а-яА-Я])\n(?=[а-яА-Я])','',s)
 return ' '.join(s.split())
flat={p:clean(t) for p,t in raw.items()}
def save(name,obj): (HERE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def excerpt(page,start,end):
 t=flat[page];i=t.find(start);j=t.find(end,i+len(start))
 assert i>=0 and j>i,(page,start,end)
 return t[i:j]
passages={
 'P143_diet':(1,'Среди кормовых объектов в годовом рационе нектона','Доля минтая'),
 'P144_detritus':(2,'В водных экосистемах выделение','Таким образом,'),
 'P145_earlier_information':(3,'различия, связанные','Существует несколько'),
 'P149_filterfeeders':(7,'В зоопланктонных сообществах','Для всего моря'),
 'P149_predation':(7,'Данные по питанию хищного зоопланктона','Таблица 2'),
 'P150_nekton':(8,'2016], уходит','Рис. 3.'),
 'P152_pollock':(10,'Так, у минтая трофический уровень','Аналогичная динамика'),
 'P152_herring':(10,'Например, в отличие от минтая','Так как качественный'),
 'P153_copepod':(11,'По нашим оценкам','Продукция эвфаузиид'),
 'P153_primaryfood':(11,'Суммарно на обеспечение','Перенос энергии'),
 'P153_euphausiid':(11,'Годовое потребление корма эвфаузиидами','Суммарно на обеспечение'),
 'P153_chaetognath':(11,'В работе К.М. Горбатенко','Стандартные расчеты'),
 'P153_hyperiid':(11,'Стандартные расчеты','Суммарно хищный'),
 'P154_other':(12,'В составе нектона','Остальные представители'),
 'P155_herring':(13,'Как показали наши исследования','Лососи.'),
 'P155_squid':(13,'Кальмары. В питании','Согласно изотопным'),
 'P155_smelt':(13,'По нашим данным среднемноголетнее суммарное потребление ею','Мойва'),
 'P156_capelin':(14,'Среднемноголетнее суммарное потребление кормовых объектов мойвой','Молодь минтая'),
 'P156_small_pollock':(14,'По нашим данным среднемноголетнее суммарное годовое потребление','На IV трофическом'),
 'P156_medium_pollock':(14,'Суммарное воздействие минтая','Величина среднего'),
 'P156_squidIV':(14,'На долю пелагических кальмаров','Доля хищных'),
 'P157_generalized':(15,'На основании представленных выше материалов','Рис. 9.'),
 'P157_caption':(15,'Рис. 9.','Fig. 9.'),
 'P158_functional':(16,'По доминированию животной','Для всего моря'),
 'P158_predation':(16,'Хищный зоопланктон выедал','На основании накопленной'),
}
evidence=[]
for key,(page,start,end) in passages.items():
 quote=excerpt(page,start,end)
 evidence.append(dict(passage_id=key,source_filename=SOURCE.name,source_sha256=sha,pdf_page=page,printed_page=page+142,russian_quote=quote,quote_format='Whitespace and discretionary line-break hyphens cleaned for readability. Exact raw page text retained in original_2019_all_pages.json.'))
quotes={e['passage_id']:e['russian_quote'] for e in evidence}
translation_file=PAPERS/'English_translation_work/translation.txt'
translation_text=translation_file.read_text(encoding='utf-8')
translation_pages={int(p):t.strip() for p,t in re.findall(r'@@(\d+)\s*(.*?)(?=@@\d+|\Z)',translation_text,re.S)}
assert set(range(143,164)).issubset(translation_pages)
for e in evidence:
 e['matching_english_translation_page_text']=translation_pages[e['printed_page']]
 e['translation_filename']='English_translation_work/translation.txt'
 e['translation_status']='Previously prepared English translation of the same2019 article; Russian original is authoritative. Matching whole-page text is provided; the Russian excerpt identifies the actual claim.'
save('original_2019_all_pages.json',[dict(pdf_page=p,printed_page=p+142,exact_pdf_text=t,review_scope='Bibliography/final received dates' if p>=18 else 'Article abstract/body/tables/figure captions') for p,t in raw.items()])

qualifiers=[
 dict(passage_id='P157_generalized',directly_addresses_Figure9=True,author_language='генерализованная схема',translation_by_audit='On the basis of the material presented above, a generalized diagram of energy transformation in the Okhotsk Sea pelagic community was constructed (Fig.9), emphasizing the established view that the principal transfer of matter and energy occurs at low and intermediate trophic levels.',assessment='Explicit generalization of the diagram; not an explicit statement about completeness of feeding connections. Does not say any particular feeding connection is omitted or only dominant links are shown.',explicit_all_links_exclusion=False),
 dict(passage_id='P157_caption',directly_addresses_Figure9=True,author_language='схема потоков энергии; ... с дополнениями',translation_by_audit='Diagram of energy flows ... Numbers in boxes are production; numbers on lines are energy consumed by the following trophic link, million tC/year; fromGorbatenko2018, with additions.',assessment='Defines units and states with additions. Gives no explicit exhaustive/nonexhaustive list and no minimum flow cutoff: smallest width category is less than1million tC/year.',explicit_all_links_exclusion=False),
 dict(passage_id='P145_earlier_information',directly_addresses_Figure9=False,author_language='отсутствием полной информации ...',translation_by_audit='Earlier models differed because complete information on abundance of all ecosystem components, particularly lower trophic levels, and their roles in trophic flows was lacking. Radchenko2011 had noted that reliable diets and autotroph/heterotroph proportions could not then be provided.',assessment='Historical limitations of prior models and cited2011 work; not an explicit exclusion statement about presentFig9.',explicit_all_links_exclusion=False),
 dict(passage_id='P143_diet',directly_addresses_Figure9=False,author_language='зообентос — 1,7 % по биомассе',translation_by_audit='In the annual nekton diet, zooplankton accounted for85.5%, nekton12.8%, and zoobenthos1.7% by biomass.',assessment='Concrete primary-source outside-network prey class; Fig9 has no zoobenthos node. This is source/figure scope evidence, not an author sentence saying arrows are omitted.',explicit_all_links_exclusion=False),
]
for q in qualifiers:
 e=next(e for e in evidence if e['passage_id']==q['passage_id']);q.update({k:e[k] for k in ['pdf_page','printed_page','russian_quote','source_sha256','matching_english_translation_page_text','translation_filename','translation_status']})
save('figure9_completeness_passages.json',qualifiers)

ledger=[]
def link(pid,consumer,prey,consumer_ids,prey_ids,value=None,unit=None,basis=None,certainty='explicit named feeding link',notes='',period='2000–2014 mean or article2000s context',english=None):
 e=next(e for e in evidence if e['passage_id']==pid)
 ledger.append(dict(link_id=f'T{len(ledger)+1:02}',passage_id=pid,source_consumer=consumer,source_prey=prey,consumer_group_ids=consumer_ids,prey_group_ids=prey_ids,explicit_numeric_value=value,unit=unit,numeric_denominator=basis,period=period,pdf_page=e['pdf_page'],printed_page=e['printed_page'],russian_quote=e['russian_quote'],english_translation=english,english_evidence_reference='passage_evidence.json:'+pid,interpretation_status=certainty,crosswalk_notes=notes,source_sha256=sha,adopted_into_model=False))

link('P143_diet','Nekton aggregate','Zooplankton',None,[4,5,6,7,14],'85.5','percent wet biomass diet','consumer total annual food Q',notes='Aggregate includes other plankton absent from figure; no allocation among nekton consumers.')
link('P143_diet','Nekton aggregate','Nekton',None,None,'12.8','percent wet biomass diet','consumer total annual food Q',notes='Aggregate prey/consumer categories; cannot allocate species arrows.')
link('P143_diet','Nekton aggregate','Zoobenthos',None,None,'1.7','percent wet biomass diet','consumer total annual food Q',notes='Outside22-group network. No named benthic prey group or consumer-specific fraction.')
link('P144_detritus','Many aquatic species, particularly invertebrates','Detritus',None,[22],certainty='general ecological statement, not model-specific diet',notes='Do not map generic invertebrates to copepods/euphausiids or invent proportions.',period='General aquatic ecosystems')
link('P149_filterfeeders','Predatory plankton','Filter feeders',None,None,certainty='qualitative functional feeding class',notes='Predatory-plankton and filter-feeder aggregates; no species allocation.')
link('P149_predation','Predatory plankton aggregate','All zooplankton',None,None,'424','million wet tonnes/year','prey annual consumption',notes='Predators mainlychaetognaths, but424 not assigned wholly to group7.')
link('P149_predation','Predatory plankton aggregate','All zooplankton',None,None,'50.5','approximately percent','prey gross stock',notes='Gross stock percentage, not consumer diet fraction.')
link('P149_predation','Predatory plankton aggregate','All zooplankton',None,None,'16.2','percent','prey annual production',notes='Production eaten, not consumer diet fraction.')
link('P149_predation','Predatory plankton aggregate','Copepods',None,[4],'19.7','percent','prey annual production',notes='Production eaten, not consumer diet fraction.')
for prey,ids,value in [('Euphausiids',[5],'15.7'),('Copepods',[4],'2.7'),('Hyperiids',[6],'26.0'),('Chaetognaths',[7],'1.1')]:
 link('P150_nekton','Nekton aggregate',prey,None,ids,value,'percent','prey annual production',notes='195million wet-tonne annual ration context. No distribution among consumer groups.')
for prey,ids in [('Plankton',None),('Benthos',None),('Nekton',None)]:
 link('P152_pollock','Pollock across sizes',prey,[12,15,19],ids,certainty='qualitative aggregate feeding class',notes='Across ontogeny; no class fraction or size-specific allocation.')
link('P152_herring','Herring','Euphausiids',[10],[5],certainty='qualitative principal prey',notes='No numerical fraction in this passage.')
link('P152_herring','Herring','Copepods',[10],[4],certainty='qualitative principal prey',notes='No numerical fraction in this passage.')
link('P153_copepod','Copepods','Phytoplankton',[4],[1],'76.8','percent wet biomass diet','copepod total annual food Q')
link('P153_copepod','Copepods','Microheterotrophs',[4],[2,3],'21.5','percent wet biomass diet','copepod total annual food Q',notes='Pooled bacteria/protozoa; do not split this fraction or assert both separately positive.')
link('P153_euphausiid','Euphausiids','Phytoplankton',[5],[1],'78.9','percent wet biomass diet','euphausiid total annual food Q')
link('P153_euphausiid','Euphausiids','Microheterotrophs',[5],[2,3],'19.4','percent wet biomass diet','euphausiid total annual food Q',notes='Pooled bacteria/protozoa fraction; no separate split.')
link('P153_primaryfood','Copepods and euphausiids aggregate','Primary food (phytoplankton and microheterotrophs)',[4,5],[1,2,3],'28.9','percent','prey aggregate annual production',notes='Aggregate prey-production eaten, not consumer DC; no bacteria/protozoa separation or individual-consumer allocation.')
link('P153_chaetognath','Chaetognaths','Copepods',[7],[4],'281.4','million wet tonnes/year','prey annual consumption')
link('P153_chaetognath','Chaetognaths','Copepods',[7],[4],'87.9','percent wet biomass diet','chaetognath total annual food Q')
link('P153_chaetognath','Chaetognaths','Copepods',[7],[4],'64.7','percent','prey gross stock',notes='Gross stock percentage is not a diet fraction.')
link('P153_chaetognath','Chaetognaths','Euphausiids',[7],[5],'2.2','percent','ambiguous shorthand following gross copepod stock percentage',certainty='feeding link explicit; percentage denominator requires clarification',notes='Do not store2.2% asDC. Parallel syntax suggests gross prey-stock basis; English translation can obscure this denominator.')
link('P153_chaetognath','Chaetognaths','Chaetognaths',[7],[7],'2.0','percent','ambiguous shorthand following gross copepod stock percentage',certainty='feeding link explicit; percentage denominator requires clarification',notes='Cannibalism presence supported; not enough to setDC=.02. Existing figure missing-arrow-zero self-cell conflicts with text.')
link('P153_hyperiid','Hyperiids','Copepods',[6],[4],'56.7','million wet tonnes/year','prey annual consumption')
link('P153_hyperiid','Hyperiids','Copepods',[6],[4],'13.0','percent','prey gross stock',notes='Gross stock percentage is notDC.')
link('P155_herring','Herring','Zooplankton',[10],None,'35.9','million wet tonnes/year','prey annual consumption')
link('P155_herring','Herring','Zooplankton',[10],None,'97.3','percent wet biomass diet','herring total annual food Q',notes='Prey class includes taxa absent from figure; no numerical copepod/euphausiid split.')
link('P155_herring','Herring','Zooplankton',[10],None,'4.2','percent','prey gross stock',notes='Gross stock percentage, not consumer DC.')
link('P155_squid','Small and medium squid','Macroplankton',None,None,certainty='qualitative prey class',notes='Size categories do not exactly determine species/tierIII9 versusIV16.')
link('P155_squid','Larger adult squid','Nekton',None,None,certainty='qualitative principal prey',notes='Age/size categories differ from isotope-based tier split.')
link('P155_squid','All squid','Plankton',[9,16],None,'64','percent wet biomass diet','aggregate squid total annual food Q',notes='Does not assign64% separately to each squid group.')
link('P155_squid','All squid','Nekton',[9,16],None,'36','percent wet biomass diet','aggregate squid total annual food Q',notes='Does not allocate prey species.')
link('P155_smelt','Deep-sea smelt','Euphausiids',[11],[5],'46.1','percent wet biomass diet','smelt total annual food Q10.29million wet tonnes/year')
link('P155_smelt','Deep-sea smelt','Copepods',[11],[4],'40.7','percent wet biomass diet','smelt total annual food Q10.29million wet tonnes/year',notes='Definite numeric22-group link absent from adoptedFigure9 routes.')
link('P156_capelin','Capelin','Zooplankton',[13],None,'14.3','million wet tonnes/year','prey annual consumption')
link('P156_capelin','Capelin','Zooplankton',[13],None,'97.9','percent wet biomass diet','capelin total annual food Q',notes='14.3/14.74 differs from printed97.9%; preserve both source readings.')
link('P156_small_pollock','Pollock<30cm','Zooplankton',[12],None,'98.9','percent wet biomass diet','small-pollock total annual food Q')
link('P156_medium_pollock','Pollock30–60cm','Euphausiids',[15],[5],'47','approximately million wet tonnes/year','prey annual consumption',notes='Explicitly approximately47; do not raise precision.')
link('P156_medium_pollock','Pollock30–60cm','Euphausiids',[15],[5],'20','more than percent','prey gross stock',notes='Inequality>20%, notDC.')
link('P156_squidIV','Pelagic squid at tierIV','Nekton',[16],None,certainty='qualitative principal prey',notes='Species within aggregate nekton unspecified.')
link('P157_generalized','Copepods','Phytoplankton',[4],[1],certainty='qualitative strongest energy flow',notes='DirectFig9 discussion, supports existing link; no numeric fraction stated here.')
link('P158_predation','Nekton aggregate','All zooplankton',None,None,'6.2','percent','prey annual production',notes='Aggregate constraint, not consumer-specific DC.')
link('P158_predation','Predatory plankton and nekton aggregate','All zooplankton',None,None,'22.4','percent','prey annual production',notes='Combined aggregate constraint; cannot allocate among consumer groups.')
for r in ledger:
 if r['english_translation'] is None:
  fact=f"{r['source_consumer']} consumes {r['source_prey']}."
  if r['explicit_numeric_value'] is not None:fact+=f" Printed value: {r['explicit_numeric_value']} {r['unit']}; denominator: {r['numeric_denominator']}."
  r['english_translation']=fact+' This is an audit paraphrase of the claim; the matching full English page is retained in passage_evidence.json.'
save('primary_prose_feeding_links.json',ledger)
save('aggregate_production_eaten_constraints.json',[r for r in ledger if r['numeric_denominator'] in ['prey annual production','prey aggregate annual production']])
with (HERE/'primary_prose_feeding_links.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(ledger[0]));w.writeheader();w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v for k,v in r.items()} for r in ledger)

totals=[('Nekton aggregate',None,'159',1),('Nekton aggregate',None,'195',7),('Copepods',[4],'2945',11),('Euphausiids',[5],'1445.6',11),('Chaetognaths',[7],'320',11),('Hyperiids',[6],'152.5',11),('Herring',[10],'36.9',13),('Squid aggregate',[9,16],'32.4',13),('Deep-sea smelt',[11],'10.29',13),('Capelin',[13],'14.74',14),('Pollock<30cm',[12],'16.5',14),('Pollock30–60cm',[15],'80.8',14)]
save('consumer_total_Q_2019.json',[dict(source_consumer=name,consumer_group_ids=ids,Q=value,unit='million wet tonnes/year',pdf_page=p,printed_page=p+142,period='2000–2014 / article2000s means',source_sha256=sha,role='Independent total Q; not a diet cell; competing159/195 source readings retained.') for name,ids,value,p in totals])

partial=[
 dict(consumer='Nekton aggregate',consumer_ids=None,known_wet_fractions=[dict(prey='Zooplankton aggregate',prey_ids=None,fraction='.855'),dict(prey='Nekton aggregate',prey_ids=None,fraction='.128'),dict(prey='Zoobenthos outside network',prey_ids=None,fraction='.017')],sum_known='1.000',unallocated_remainder='0',Qwet=None,competing_source_Qwet=['159','195'],source='p.143 andpp.149–150; completecategorytotalsbutindividualconsumer/preyallocationunknown'),
 dict(consumer='Copepods',consumer_ids=[4],known_wet_fractions=[dict(prey='Phytoplankton',prey_ids=[1],fraction='.768'),dict(prey='Microheterotrophs pooled',prey_ids=[2,3],fraction='.215')],sum_known='.983',unallocated_remainder='.017',Qwet='2945',source='p.153'),
 dict(consumer='Euphausiids',consumer_ids=[5],known_wet_fractions=[dict(prey='Phytoplankton',prey_ids=[1],fraction='.789'),dict(prey='Microheterotrophs pooled',prey_ids=[2,3],fraction='.194')],sum_known='.983',unallocated_remainder='.017',Qwet='1445.6',source='p.153'),
 dict(consumer='Chaetognaths',consumer_ids=[7],known_wet_fractions=[dict(prey='Copepods',prey_ids=[4],fraction='.879')],sum_known='.879',unallocated_remainder='.121',Qwet='320',source='p.153',separately_printed_copepod_Qwet='281.4',precision_note='281.4/320=.879375, compatible with rounded87.9%. The separately printed2.2%euphausiids/2.0%chaetognaths have unresolved denominators and are not diet cells.'),
 dict(consumer='Hyperiids',consumer_ids=[6],known_wet_fractions=[dict(prey='Copepods',prey_ids=[4],fraction=str(D('56.7')/D('152.5')),derivation='56.7millionwettonnescopepodQ /152.5millionwettonnestotalQ; fractionderived,notprintedDC')],sum_known=str(D('56.7')/D('152.5')),unallocated_remainder=str(D(1)-D('56.7')/D('152.5')),Qwet='152.5',source='p.153',precision_note='Ratio of rounded printed consumption values. Prey identities in remainder unknown.'),
 dict(consumer='Deep-sea smelt',consumer_ids=[11],known_wet_fractions=[dict(prey='Euphausiids',prey_ids=[5],fraction='.461'),dict(prey='Copepods',prey_ids=[4],fraction='.407')],sum_known='.868',unallocated_remainder='.132',Qwet='10.29',source='p.155'),
 dict(consumer='Herring',consumer_ids=[10],known_wet_fractions=[dict(prey='Zooplankton aggregate',prey_ids=None,fraction='.973')],sum_known='.973',unallocated_remainder='.027',Qwet='36.9',source='p.155'),
 dict(consumer='Capelin',consumer_ids=[13],known_wet_fractions=[dict(prey='Zooplankton aggregate',prey_ids=None,fraction='.979')],sum_known='.979',unallocated_remainder='.021',Qwet='14.74',source='p.156; printed absolutezooplanktonQ14.3 doesnotreconcileprecisely'),
 dict(consumer='Pollock<30cm',consumer_ids=[12],known_wet_fractions=[dict(prey='Zooplankton aggregate',prey_ids=None,fraction='.989')],sum_known='.989',unallocated_remainder='.011',Qwet='16.5',source='p.156'),
 dict(consumer='Squid aggregate',consumer_ids=[9,16],known_wet_fractions=[dict(prey='Plankton aggregate',prey_ids=None,fraction='.64'),dict(prey='Nekton aggregate',prey_ids=None,fraction='.36')],sum_known='1.00',unallocated_remainder='0',Qwet='32.4',source='p.155; categorytotalcompletebutindividualpreys/groupIIIIVsplitunknown'),
]
for p in partial:
 p.update(currency='wet prey biomass proportions',currency_evidence='Fractions are printed by biomass/mass, or in the same annual diet paragraph; wet mass is inferred from the food-consumption and Table3 context. Fractions are not carbon DC.',complete_22_group_diet=False,source_sha256=sha,unknown_prey_policy='Leave unspecified individual prey unresolved; unallocated remainder is not zero and is not distributed or normalized.',adopted_into_model=False)
 if p['consumer']=='Deep-sea smelt':
  p['dc_wet_by_prey_group_id']={'4':'0.407','5':'0.461'}
  p['unallocated_fraction']='0.132'
  p['Qwet_million_tonnes_per_year']='10.29'
  p['source_pdf_page']=13
  p['source_printed_page']=155
  p['numeric_precision']='Rounded printed fractions/Q; arithmetic preserves them without normalization.'
save('partial_numeric_diets.json',partial)
derived=[]
for prey,fraction,factor,ids in [('Euphausiids','.461','10.6',[5]),('Copepods','.407','14',[4])]:
 wet=D('10.29')*D(fraction);carbon=wet/D(factor)
 derived.append(dict(prey=prey,prey_ids=ids,consumer='Deep-sea smelt',consumer_id=11,source_fraction_wet=fraction,source_Qwet_million_t_per_year='10.29',derived_wet_flow_million_t_per_year=str(wet),source_prey_wet_per_carbon=factor,derived_carbon_flow_million_tC_per_year=str(carbon),source='2019p.155dietfraction/Q;2019Table3p.154factor',precision='Exact arithmetic on rounded printed inputs; derived digits are not additional measurement precision.',adopted_into_model=False))
save('derived_smelt_text_flows.json',dict(flows=derived,unallocated_wet_fraction='.132',unallocated_wet_Q_million_t_per_year=str(D('10.29')*D('.132')),unallocated_carbon_Q=None,not_normalized=True))
save('passage_evidence.json',evidence)

patterns=[r'рис\.?\s*9',r'генерализ',r'обобщ',r'упрощ',r'непол',r'не\s+(?:все|всех)',r'только\s+(?:основ|глав|доминир)',r'не\s+(?:показан|включ|учитыв)',r'вс[её]\s+(?:связ|поток)',r'основн\w*\s+трофодинамическ\w*\s+связ']
hits=[]
for p,t in flat.items():
 for pat in patterns:
  for m in re.finditer(pat,t,re.I):hits.append(dict(pdf_page=p,printed_page=p+142,pattern=pat,text=t[max(0,m.start()-100):min(len(t),m.end()+220)]))
save('completeness_keyword_sweep.json',dict(pages_swept=21,page_counts=[dict(pdf_page=p,printed_page=p+142,characters=len(raw[p])) for p in raw],patterns=patterns,hits=hits,manual_body_and_caption_review=True,reference_pages_reviewed_not_used_as_model_claims=[18,19,20,21]))
flow_readings=json.loads((CANDIDATE/'audit/flow_readings.json').read_text(encoding='utf-8'))
newlinks=[dict(prey_id=4,consumer_id=11,link='Copepods→smelt',presence_explicit=True,numeric_wet_DC='0.407',numeric_ambiguous_percent=None,DC_usable=True,source='2019p.155'),dict(prey_id=7,consumer_id=7,link='Chaetognaths→chaetognaths',presence_explicit=True,numeric_wet_DC=None,numeric_ambiguous_percent='2.0',DC_usable=False,source='2019p.153',reason='Percentage follows64.7%grosscopepodstock; denominator unresolved, so it is not stored as DC=.02.')]
for r in newlinks:
 r['matching_current_figure_readings']=[f['flow_id'] for f in flow_readings if f['prey_id']==r['prey_id'] and f['consumer_id']==r['consumer_id']]
 assert not r['matching_current_figure_readings']
 r['adopted_into_model']=False
save('candidate_additional_22group_links.json',newlinks)
save('summary.json',dict(source_pdf_sha256=sha,pages_reviewed=21,prose_link_records=len(ledger),distinct_named_source_consumer_prey_pairs=len(set((r['source_consumer'],r['source_prey']) for r in ledger)),passage_records=len(evidence),partial_diet_records=len(partial),aggregate_production_eaten_records=len([r for r in ledger if r['numeric_denominator'] in ['prey annual production','prey aggregate annual production']]),direct_Figure9_generalization_statement=True,explicit_all_feeding_links_exclusion_statement_found=False,candidate_new_individual22group_links=newlinks,outside_network_or_aggregate_qualitative_links_preserved=True,model_written=False,zero_rule_changed=False,source_hash_reverified=hashlib.sha256(SOURCE.read_bytes()).hexdigest()==sha))
print('Saved 21-page primary-only text audit;',len(ledger),'feeding records')
