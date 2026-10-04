from pathlib import Path
import json,sys,math,hashlib,copy
R=Path.cwd(); O=R/'outputs/validation_revision_20260930'
sys.path[:0]=[str(R/'tools'),str(R/'tools/skills/original_skill_resources/combined-src/scripts')]
from workbooks import records,overview
from assumed_allocation import allocate
M='36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)'
D=R/'regions/LME_036/validation_reports'/M/'adopted_revision_20260930';D.mkdir(exist_ok=True)
prior=D.parent/'adopted_revision_20260929'
b=json.loads((O/'previous_book.json').read_text(encoding='utf-8'))
a=json.loads((prior/'taxon_audit_adopted.json').read_text(encoding='utf-8')); original=copy.deepcopy(a)
model=R/'regions/LME_036'/overview(b)['model_path'];m=json.loads(model.read_text(encoding='utf-8'))
groups={int(x['group_seq']):x for x in m['group']}
sets={}
def add(taxa,ids,rule,why):
 for t in taxa:sets[t]=(ids,rule,why)
add(['Marine fishes not identified','Marine finfishes not identified'],list(range(13,34)),'M10',
    'Unknown marine-fish composition is approximated by all named and residual fish compartments, including sharks and rays. The broad fish label does not justify a residual-only mixture; shelf-model catches are only a composition proxy for the wider region.')
add(['Perciformes'],[13,14,*range(16,32)],'M10',
    'The broad historical perciform label is approximated by compatible named fish families and residual demersal, benthopelagic and pelagic compartments. Lizardfish and sharks/rays are excluded. Residual pools may contain other lineages, and modern order boundaries differ; their full catches are weak composition proxies, not exact taxonomic containment.')
add(['Marine groundfishes not identified'],[*range(13,29),32],'M10',
    'The groundfish label is approximated by named demersal/benthopelagic fish groups, residual demersal and benthopelagic pools and demersal sharks/rays. Include pomfret and melon-seed as benthopelagic candidates under the saved catch classification; exclude the pelagic pools. Exact constituent species and habitat fractions are unknown.')
add(['Marine pelagic fishes not identified'],[29,30,31,33],'M10',
    'The pelagic label is approximated by residual pelagic fish and pelagic sharks/rays. Named hairtail, pomfret and melon-seed pools were reviewed and excluded because the saved catch classification treats them as benthopelagic. This is a weak model-composition proxy; mixed habitat boundaries and the unidentified species mixture remain uncertain.')
add(['Miscellaneous aquatic invertebrates'],list(range(5,13)),'M10',
    'The saved catch classification is Other demersal invertebrates. Approximate that category with benthic invertebrate, shrimp, crab and cephalopod compartments; exclude primary producers, pelagic zooplankton and jellyfish. The generic label may span a wider mixture and cephalopods have mixed habitats. Model pool catch only proxies composition; genuine zero-catch polychaetes remain a candidate.')
add(['Chondrichthyes'],[32,33],'M10',
    'Approximate cartilaginous fishes with the represented demersal and pelagic shark/ray pools. Any unreported chimaera catch has no dedicated compartment and is absorbed by this weak analogue; its fraction is unknown.')
add(['Xiphias gladius','Istiophorus platypterus','Istiophoridae','Istiophorus','Makaira mazara','Istiompax indica','Makaira','Kajikia audax','Tetrapturus angustirostris'],[30,31],'M11',
    'The saved catch class is Large pelagics. The model lacks an explicit oceanic billfish compartment, so juvenile/adult large pelagic fish are the closest represented functional analogue. Shelf/oceanic habitat and the transferred source 18-month stage boundary are substantial mismatches. Maximum-size class does not establish adult-only catch.')
add(['Ruvettus pretiosus','Gadiformes'],[27],'M11',
    'The saved catch classification is benthopelagic. Use the single represented Benthopelagic fish compartment as a whole-catch analogue. Species/depth composition and the source small/large-pool aggregation are uncertain; this is not documented exact source membership.')
add(['Lampris guttatus','Lepidocybium flavobrunneum'],[30,31],'M11',
    'The saved catch classification is Large bathypelagics. The model has no bathypelagic compartment; juvenile/adult large pelagic fish provide the closest represented open-water size analogue. Deep-water versus shelf-pelagic habitat and the transferred 18-month stage boundary are substantial mismatches; exact source membership is not claimed.')
assert set(sets)=={r['taxon'] for r in a if r['overall_confidence']=='Unresolved'}
changes=[]
for r in a:
 if r['taxon'] not in sets:continue
 ids,rule,why=sets[r['taxon']];old=copy.deepcopy(r)
 candidates=[]
 for i in ids:
  g=groups[i]
  candidates.append(dict(group_id=i,group=g['group_name'],eligibility=why,
      definition=g['taxon_descr'],catch=float(g['export']),biomass=float(g['biomass']),
      catch_field='model.json group.export',biomass_field='model.json group.biomass',
      source_units='model areal mass units; ratios are dimensionless'))
 calc=allocate(candidates);assert calc['weights'] is not None
 if len(ids)==1:
  calc=dict(field='none',values=[1.0],total=1.0,weights=[1.0],confidence='High',attempts=[],reason='Single selected analogue; no allocation split is required.')
 r.update(previous_review_confidence='Unresolved',candidate_selection=candidates,allocation_calculation=calc,
    adopted_groups=[dict(group_id=c['group_id'],name=c['group'],weight=w) for c,w in zip(candidates,calc['weights'])],
    membership_rule=rule,membership_confidence='Very low',review_confidence='Very low',overall_confidence='Very low',
    membership_rule_plain=('A broad catch label is approximated by compatible named and residual groups' if rule=='M10' else 'The closest represented ecological group is used despite a habitat or source-definition mismatch'),
    weight_rule='W1' if len(ids)==1 else 'W4',weight_confidence='High' if len(ids)==1 else 'Medium',
    weight_rule_plain=('The taxon is assigned to one group and needs no split' if len(ids)==1 else 'Model catch proportions supply an assumed allocation across eligible groups'),
    membership_source='Cheung 2007 Appendix 6.1 group definitions; saved regional Catch functional_group. Membership is an explicit broad-category or closest-analogue assumption.',
    weight_source=('No split: weight 1 in the sole selected analogue.' if len(ids)==1 else 'Selected model.json group.export divided by its sum over the recorded candidates.'),
    transfer_assumption='Assumed composition is fixed across 1950–2019 and landings, total catch and discards; source model is a 2000s northern shelf representation.',
    reason=why+(' All catch is assigned to the single analogue.' if len(ids)==1 else ' Weights use model catch proportions, assumed fixed across years and catch bases.')+' Very low membership confidence; see Sources and the regional Mapping review.')
 r['display_mapping']='; '.join(f"{x['name']} ({x['weight']:.6%})" for x in r['adopted_groups'])
 assert math.isclose(math.fsum(x['weight'] for x in r['adopted_groups']),1,abs_tol=1e-14)
 changes.append(dict(taxon=r['taxon'],old_mapping=old['adopted_groups'],new_mapping=r['adopted_groups'],old_confidence='Unresolved',new_confidence='Very low',reason=why))
for old,new in zip(original,a):
 if old['taxon'] not in sets:assert old==new
summary=json.loads((prior/'summary.json').read_text());total=summary['known_ppr_tC'];catch=summary['catch_t']
rank=['High','Medium','Low','Very low','Unresolved'];summary['categories']=[]
for confidence in rank:
 rows=[r for r in a if r['overall_confidence']==confidence]
 summary['categories'].append(dict(confidence=confidence,taxa=len(rows),catch_pct=100*math.fsum(r['catch_t'] for r in rows)/catch,ppr_pct=100*math.fsum(r['ppr_tC'] for r in rows if r['ppr_tC'] is not None)/total))
for stage in ['membership','weight']:
 table=[]
 for rule,confidence in sorted({(r[stage+'_rule_plain'],r[stage+'_confidence']) for r in a}):
  rows=[r for r in a if r[stage+'_rule_plain']==rule and r[stage+'_confidence']==confidence]
  table.append({'Plain-language rule':rule,'Confidence':confidence,'PPR percentage':100*math.fsum(r['ppr_tC'] for r in rows if r['ppr_tC'] is not None)/total,'taxa':len(rows)})
 assert math.isclose(sum(r['PPR percentage'] for r in table),100,abs_tol=1e-9);summary[stage+'_rules']=table
summary.update(newly_mapped_taxa=20,fallback_taxa=42,assumption_dependent_taxa=177,
    newly_mapped_catch_t=math.fsum(r['catch_t'] for r in a if r['overall_confidence']=='Very low'),
    mapped_catch_pct=100.0,mapped_known_ppr_pct=100.0,unresolved_taxa=0,
    geographic_allocation_used=False,geographic_allocation_reason='No retained source contains applicable taxon caught mass by geographic strata matching these groups.')
summary['fallback_basis_counts']={k:sum(r['allocation_calculation'] is not None and r['allocation_calculation']['field']==k for r in a) for k in ['catch','biomass','none']}
for name,value in [('taxon_audit_adopted.json',a),('summary.json',summary),('mapping_changes.json',changes)]:
 (D/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
identity=json.loads((prior/'input_identity.json').read_text());identity.pop('last_adopted_sha256',None)
identity['baseline_region_sha256']=hashlib.sha256((R/'regions/LME_036/LME_036.xlsx').read_bytes()).hexdigest()
identity['baseline_project_sha256']=hashlib.sha256((R/'Project.xlsx').read_bytes()).hexdigest()
if (D/'input_identity.json').exists():assert json.loads((D/'input_identity.json').read_text())==identity
else:(D/'input_identity.json').write_text(json.dumps(identity,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
