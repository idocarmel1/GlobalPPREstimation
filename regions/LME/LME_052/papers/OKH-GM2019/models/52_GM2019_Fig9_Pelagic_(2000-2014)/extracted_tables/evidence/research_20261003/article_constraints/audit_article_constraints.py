"""Read-only source audit; writes only beside this script. No model fitting."""
from pathlib import Path
from decimal import Decimal as D
import csv, importlib.util, json, hashlib, pymupdf

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parents[1]
ROOT = CANDIDATE.parents[3]
PAPERS = ROOT/'regions/LME_052/papers/OKH-GM2019'
spec = importlib.util.spec_from_file_location('source_readings', CANDIDATE/'figure9_data.py')
data = importlib.util.module_from_spec(spec); spec.loader.exec_module(data)
table = {r[-1]:r for r in data.TABLE3 if r[-1] is not None}
flows = json.loads((CANDIDATE/'audit/flow_readings.json').read_text(encoding='utf-8'))
existing = {r['group_id']:r for r in json.loads((CANDIDATE/'audit/flow_budget_checks.json').read_text())}
names = {g[0]:g[1] for g in data.GROUPS}
def literal(v): return str(v) if v is not None else None
def save_json(name,value): (HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def save_csv(name,rows):
    with (HERE/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

factors=[]
for n,name,ru,P,box,tier in data.GROUPS:
    r=table.get(n)
    status='primary_table3_direct' if r else 'not_reported'
    value=r[3] if r else None
    provenance='2019 Table 3, printed p.154 / PDF p.12' if r else None
    alternative=None
    note='Wet tonnes per tonne carbon; carbon fraction is reciprocal.'
    if n==2:
        value='9.4';status='supporting_source_explicit'
        provenance='2018 dissertation, printed/PDF p.60'
        note='Explicit bacterial conversion factor. 2019 Table 3 reports 9.4 for pooled microheterotrophs, not separately for bacteria.'
    if n==3:
        status='supporting_source_derived_but_conflicting';alternative='10'
        provenance='2018 dissertation, printed/PDF p.60'
        note='270 g wet/m² / 27 gC/m² implies 10. Separate coefficient is not printed. Same paragraph gives total 0.33e9 t wet, inconsistent with per-area total 416.88e6 t over 1.544e6 km². Applying pooled 9.4 to protozoa is an explicit separation assumption.'
    if n==20:
        status='primary_table3_tentative_crosswalk'
        note='Tier V Other**** includes sharks, daggertooth, lancetfish and other predatory fish including pelagic-feeding halibut. Figure Predatory fish is broader/ambiguous; table P=.005, figure P=.004.'
    if n==22:
        note='No detritus stock, organic-carbon fraction or wet/C coefficient is reported. Detritus quality cannot be copied from living microbes.'
    factors.append(dict(group_id=n,group=name,source_name=ru,wet_per_carbon=value,carbon_fraction=literal(1/D(value)) if value else None,status=status,source=provenance,flagged_supporting_derived_alternative=alternative,notes=note))
save_json('conversion_factors_22.json',factors);save_csv('conversion_factors_22.csv',factors)

checks=[]
for n,name,ru,P,box,tier in data.GROUPS:
    if n==22: continue
    r=table.get(n)
    figP=D(P)
    e=existing[n]
    Q=D(e['conservative_Q_carbon']) if e['conservative_Q_carbon'] else None
    outs=[f for f in flows if f['prey_id']==n]
    clear=sum((D(f['readable_carbon_flow']) for f in outs if f['routing_status']=='clear'),D(0))
    readable=sum((D(f['readable_carbon_flow']) for f in outs if f['readable_carbon_flow'] is not None),D(0))
    unknown=[f['flow_id'] for f in outs if f['readable_carbon_flow'] is None]
    full=D(e['hypothesis_predation_carbon'])
    wetQ=D(e['conservative_Q_wet']) if e['conservative_Q_wet'] else None
    p_wet=D(r[2])*D(r[5]) if r else None
    checks.append(dict(group_id=n,group=name,figure_P_C=P,Q_C_readable_routes=literal(Q),R_C_at_GS_0_2=literal(D('.8')*Q-figP) if Q is not None else None,Q_C_min_for_nonnegative_R_at_GS_0_2=literal(figP/D('.8')),max_GS_for_nonnegative_R=literal(1-figP/Q) if Q else None,M2_C_clear_lower_bound=literal(clear),M2_C_readable_adopted_routes=literal(readable),unknown_outflow_labels=';'.join(unknown),M2_C_illustrative_labels=literal(full),max_catch_plus_living_BA_plus_net_export_C_readable_routes=literal(figP-readable),max_combined_sink_C_illustrative_labels=literal(figP-full),fails_predation_even_clear_routes=clear>figP,source_table_Bwet_times_PB=literal(p_wet),source_table_Pwet=r[6] if r else None,source_table_Pcarbon=r[7] if r else None,source_table_Bcarbon_times_PB=literal(D(r[4])*D(r[5])) if r else None,source_Bwet_divided_factor_times_PB_C=literal(p_wet/D(r[3])) if r else None,Q_wet_readable_routes=literal(wetQ),R_wet_source_BPB_at_GS_0_2=literal(D('.8')*wetQ-p_wet) if wetQ is not None and p_wet is not None else None,route_scope='Current inherited provisional arrows; statuses preserved. Illustrative labels are F62=.023 and F67=.05, not accepted source readings.'))
save_json('mathematical_constraints.json',checks);save_csv('mathematical_constraints.csv',checks)

annual=[(4,'2945',153),(5,'1445.6',153),(6,'152.5',153),(7,'320',153),(10,'36.9',155),(11,'10.29',155),(13,'14.74',156),(12,'16.5',156),(15,'80.8',156)]
consumption=[]
for n,q,page in annual:
    r=table[n];qw=existing[n]['conservative_Q_wet']
    consumption.append(dict(group_id=n,group=names[n],source_Qwet_million_t_per_year=q,source_Bwet_million_t=r[2],derived_QBwet_per_year=literal(D(q)/D(r[2])),source=f'2019 prose printed p.{page} / PDF p.{page-142}',figure_Qwet_current_routes=qw,fraction_reproduced=literal(D(qw)/D(q)) if qw else None,role='Independent total-consumption check; does not supply missing diet composition. Do not multiply total prey wet Q by consumer carbon fraction.'))
consumption.append(dict(group_id='9+16',group='Squid III + Squid IV',source_Qwet_million_t_per_year='32.4',source_Bwet_million_t='1.000',derived_QBwet_per_year='32.4',source='2019 prose printed p.155 / PDF p.13',figure_Qwet_current_routes=literal(sum(D(existing[n]['conservative_Q_wet']) for n in [9,16])),fraction_reproduced=literal(sum(D(existing[n]['conservative_Q_wet']) for n in [9,16])/D('32.4')),role='Aggregate squid Q/B only. Separate III and IV Q/B are not identified; equal Q/B would be an additional assumption.'))
save_json('independent_QB_targets.json',consumption);save_csv('independent_QB_targets.csv',consumption)

tiers=[]
printed={'I':'831.0','II':'177.4','III':'18.302','IV':'0.653','V':'0.015'}
abstract={'I':'831.0','II':'177.400','III':'18.100','IV':'0.740','V':'0.016'}
for tier in printed:
    rows=[r for r in data.TABLE3 if r[0]==tier]
    fg=[g for g in data.GROUPS if g[-1]==tier and g[3] is not None]
    tiers.append(dict(tier=tier,table3_reported_Pcarbon=printed[tier],sum_table3_component_Pcarbon=literal(sum((D(r[7]) for r in rows),D(0))),abstract_Pcarbon=abstract[tier],sum_figure9_Pcarbon=literal(sum((D(g[3]) for g in fg),D(0))),unit='million tC/year',scope_note='Figure omits Other rows of tiers II–IV; source conflicts retained; categorical tiers are not solved Ecopath trophic levels.'))
save_json('production_targets_by_tier.json',tiers);save_csv('production_targets_by_tier.csv',tiers)

targets=[
dict(target='Source stock/production rows',source='2019 Table 3 p.154',test='Reproduce printed stocks, factors, PB and P independently, then report B*PB and wet/C arithmetic residuals.',identifies='B/PB/P according to chosen source variant',does_not_identify=['catch','living BA','net migration/export','GS','EE']),
dict(target='Figure 9 carbon flows',source='2019 Fig.9 p.157',test='Reproduce each readable carbon arrow and each box; derive diet from incoming arrows, not production boxes.',identifies='Diet and Q in carbon only if endpoints/exhaustiveness/readings accepted',does_not_identify=['catch','living BA','migration','unshown external imports','respiration independently']),
dict(target='Annual consumption by group',source='2019 pp.153–156',test='Compare sum(F_C*prey wet/C) to independently printed wet Q; use Qwet/Bwet for a separate QB target.',identifies='Total Qwet and QBwet for nine groups plus pooled squid',does_not_identify=['missing prey proportions','separate squid III/IV QB','catch','BA','migration']),
dict(target='Zooplankton P=2616; predatory consumption=424; 16.2%+6.2%=22.4%',source='2019 pp.149–150, Table 2, conclusion p.158',test='424/2616=.1620795; 2616*.062=162.192; combined %.224 yields585.984. Check prey-group sums and source rounding.',identifies='Consumption/production aggregates under stated taxonomic scope',does_not_identify=['catch','living BA','migration','mortality remainder fate']),
dict(target='Nekton annual Q=195 vs159',source='2019 Russian abstract p.143, English abstract p.144, prose p.150 and Fig.3',test='Use competing target variants. Listed herring/squid Q and species shares support195, not159; Russian159 is wet tonnes while English159 tC is a unit error.',identifies='Contradictory independent consumption totals',does_not_identify=['catch','BA','export; these cannot repair fixed-Q inconsistency']),
dict(target='Fish-available zooplankton production 163.5 million tC/year or2230 million t wet/year',source='2019 p.155',test='Must define groups and subtract predatory plankton consumption. 2616−424=2192, not2230, so broad community number is not exact reconstruction target without source-scope clarification.',identifies='Aggregate consumption-derived remainder with unresolved scope',does_not_identify=['fishing catch','catch allocation','living BA','migration']),
dict(target='Total summed production1027.4 vs1027.2',source='2019 pp.143,157,159 and Table3',test='Table3 tiers sum1027.370; figure boxes sum computed separately; preserve .2 discrepancy and omitted rows.',identifies='Summed group production, including recycled carbon',does_not_identify=['net ecosystem production','external new carbon input','catch','BA','export']),
dict(target='Seasonal salmon/squid migration',source='2019 p.155',test='Salmon occur part-year; squid ascend to feed at night. These are qualitative migration observations, not numerical annual net migration estimates.',identifies='Need to consider seasonal/spatial model boundary',does_not_identify=['net migration amount','annual BA','catch']),
]
save_json('testable_targets_and_identifiability.json',targets)

source_ledger={}
for filename in ['gorbatenko_melnikov_2019.pdf','gorbatenko_2018_dissertation.pdf','gorbatenko_melnikov_2016_herring.pdf','gorbatenko_levitskaya_2016_pollock.pdf']:
    path=PAPERS/filename; source_ledger[filename]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
save_json('audit_metadata.json',dict(source_ledger=source_ledger,unchanged_baseline=True,source_numbers_changed=False,balanced_model_created=False,units='Million tonnes wet or carbon for original totals; /year for flows; QB/PB year^-1.',formulae={'consumer_energy':'R_i=(1−GS_i)Q_i−P_i >=0','living_production':'P_i=M2_i+Y_i+BA_i+E_i+M0_flow_i; E is net outward migration/export, negative for net import','sink_feasibility':'−M2_i <= Y_i+BA_i+E_i <= P_i−M2_i if0<=EE<=1 and M0=P(1−EE)','detritus':'BA_D=Σ_i[GS_i*Q_i+M0_flow_i]−Q_D under sole-detritus routing and zero detritus import/export','whole_carbon_balance':'BA_D=P_primary−Σ_consumers R_i−Σ_living(Y_i+BA_i+E_i); subject to specified discard convention'},warnings=['Bounds are mathematical constraints, not source inferred catch/EE/BA.','Predation bounds assume current inherited routes; uncertain labels remain separate.','Negative living BA or inward migration can support predation exceeding P; neither can fix a negative consumer respiration at fixed P/Q/GS.','No per-group living catch, annual BA, migration or EE value has been recovered.']))

snippets=[]
for filename,page,printed,start,end,meaning in [
    ('gorbatenko_2018_dissertation.pdf',60,60,'Следовательно,','Микрозоопланктон','Explicit bacterial wet/carbon 9.4; per-area and whole-sea production totals are internally inconsistent.'),
    ('gorbatenko_2018_dissertation.pdf',60,60,'На основании лите-','Входящие','Protozoa per-area 27gC and270g wet imply10; no separately printed coefficient; whole-sea total contradicts per-area arithmetic.'),
    ('gorbatenko_melnikov_2019.pdf',5,147,'образования половых','Продукцию надпопуляционных','Production includes losses, not only observed surviving biomass growth. Printed grouping of the subsequent Be equation is preserved in the original.'),
    ('gorbatenko_melnikov_2016_herring.pdf',6,190,'Зная среднесуточные','Данные расчетов','Seasonal stock differences explicitly attributed mainly to survey undercount; expert whole-sea stock2.5million t; spring feeding duration2months.'),
    ('gorbatenko_levitskaya_2016_pollock.pdf',8,201,'Среднемноголетние данные','Таблица 5','Supporting total nekton consumption194.9million wet tonnes, pollock98.88million and50.7% share.'),
]:
    doc=pymupdf.open(PAPERS/filename);raw=doc[page-1].get_text();i=raw.find(start);j=raw.find(end,i+1)
    assert i>=0 and j>i,(filename,page,start,end)
    snippets.append(dict(source_filename=filename,pdf_page=page,printed_page=printed,source_sha256=source_ledger[filename]['sha256'],exact_pdf_text=raw[i:j],assessment=meaning))
save_json('source_evidence_snippets.json',snippets)
print('Saved scientific audit artifacts to',HERE)
