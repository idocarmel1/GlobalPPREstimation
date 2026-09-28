from pathlib import Path
import json,hashlib
import pandas as pd
P=Path(__file__).resolve().parent;M=P.parent.parent;MODEL=M/'50_502013_Coastal_Kyoto_Inoue_(2013)';EV=MODEL/'selected_pipeline';REG=M.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(REG)):sha(p) for p in [REG/'LME_050.xlsx',MODEL/'model.json',EV/'source_supported_matching.csv']}
d=pd.read_csv(EV/'all_taxa_membership_review.csv').set_index('taxon');tot19=float(d.catch_2019.sum());totall=float(d.catch_1950_2019.sum());base=d[d.group.notna()];un=d[d.group.isna()]
stats={'taxa':len(d),'mapped_taxa':len(base),'taxon_coverage_pct':len(base)/len(d)*100,'catch_2019':tot19,'mapped_catch_2019':float(base.catch_2019.sum()),'catch_coverage_2019_pct':float(base.catch_2019.sum()/tot19*100),'catch_1950_2019':totall,'mapped_catch_1950_2019':float(base.catch_1950_2019.sum()),'catch_coverage_1950_2019_pct':float(base.catch_1950_2019.sum()/totall*100)}
reasons={
'Gadus chalcogrammus':'Genuine gap: no pollock/cod or generic cold-water fish group.',
'Marine fishes not identified':'Composition/weights unresolved; includes stocks absent from the model.',
'Clupea pallasii':'Genuine gap: Pacific herring is not source Etrumeus round herring.',
'Scomber':'Strong pooled-group alias proposal: both listed Japanese mackerels share Mackerel SPPR.',
'Pectinidae':'Broader Bivalve inference possible; source lists oysters, not documented scallop membership.',
'Gadus macrocephalus':'Genuine gap: no cod group.',
'Cololabis saira':'Genuine gap: no saury group.',
'Oncorhynchus gorbuscha':'Genuine gap: no salmon group.',
'Ammodytes personatus':'Genuine gap: no sand-lance group.',
'Oncorhynchus':'Genuine gap: salmon aggregate, with no salmon group.',
'Pleuronectidae':'Not source Paralichthys; expanded flatfish guild needs evidence.',
'Pleurogrammus azonus':'Not Scomber; no documented greenling/Atka-mackerel group.'}
for label,col,total in [('2019','catch_2019',tot19),('1950_2019','catch_1950_2019',totall)]:
 t=un.nlargest(10,col).copy();t['share_of_all_catch_pct']=100*t[col]/total;t['diagnosis']=[reasons.get(n,'Additional source membership/ecological evidence required') for n in t.index];t.to_csv(P/f'TOP10_UNMATCHED_{label}.csv')
 stats['top10_unmatched_'+label+'_share_pct']=float(t[col].sum()/total*100)
gaps=['Gadus chalcogrammus','Gadus macrocephalus','Clupea pallasii','Cololabis saira','Ammodytes personatus','Oncorhynchus','Oncorhynchus gorbuscha','Oncorhynchus keta']
stats['eight_clear_gap_labels']=gaps;stats['eight_clear_gap_2019_tonnes']=float(d.loc[gaps,'catch_2019'].sum());stats['eight_clear_gap_2019_pct']=float(d.loc[gaps,'catch_2019'].sum()/tot19*100)
candidates=[]
def add(t,group,tier,recommendation,evidence):
 assert t in un.index
 candidates.append({'taxon':t,'proposed_group_or_set':group,'tier':tier,'recommendation':recommendation,'catch_2019':float(d.loc[t,'catch_2019']),'2019_coverage_gain_percentage_points':float(d.loc[t,'catch_2019']/tot19*100),'catch_1950_2019':float(d.loc[t,'catch_1950_2019']),'historical_coverage_gain_percentage_points':float(d.loc[t,'catch_1950_2019']/totall*100),'evidence_and_limit':evidence})
add('Scomber australasicus','Mackerel','source_spelling_review','Recommend explicit editorial correction in mapping evidence only; preserve source spelling','S3 prints Scomber austlasicus; WoRMS accepts S. australasicus and FAO identifies that species in Japanese mixed mackerel catches. This is a documented spelling inference, not an exact WoRMS synonym hit.')
add('Scomber','Mackerel','strong_pooled_group_alias','Recommend first extension with regional genus scope and spelling correction documented','S3 Mackerel pools S. japonicus and printed S. austlasicus. FAO Japan fisheries documents co-reported japonicus/australasicus. Both use the same coefficient, so their proportions are not needed; this is not permission to assign unrelated mackerels such as Pleurogrammus.')
add('Auxis','Frigate tuna','strong_pooled_group_alias','Recommend pooled alias','S3 explicitly places Auxis rochei and Auxis thazard together; catch label is bullet and frigate tunas. No between-group weights needed.')
add('Thunnus orientalis','Tuna','source_conflict_review','Review main-text precedence before adopting','Main p585 explicitly says Tuna represented by T. orientalis; S3 says T. thynnus. WoRMS treats the bare names as distinct; only T. thynnus orientalis is a synonym. Preserve conflict; do not call this a synonym fix.')
for t,g,reason in [
 ('Trachurus','Jack mackerel','S3 representative T. japonicus; catch genus scope must be checked rather than assumed exhaustive.'),
 ('Seriola','Yellowtail','S3 group label Amberjack corresponds to main Yellowtail, with representative S. quinqueradiata. Genus catch can include other amberjacks; group-name alias does not prove all species membership.'),
 ('Octopus','Octopus','S3 representative O. vulgaris; main p576 places Octopus among benthic invertebrates. Genus-level broader membership is plausible but requires explicit group-scope review.'),
 ('Crassostrea','Bivalve','Both S3 examples are oyster names, but genus catch is broader than an exact species match.'),
 ('Bivalvia','Bivalve','Group label is taxonomically broad and S3 is representative, so exact-only exclusion is conservative. Author membership and geographic/functional representativeness should be documented.'),
 ('Pectinidae','Bivalve','Taxonomic containment in bivalves, but oyster representatives do not independently validate scallop membership or Kyoto coefficients for northern scallop fisheries.'),
 ('Octopodidae','Octopus','Potential broader benthic octopus family match; confirm source group scope.'),
 ('Teuthida','Flying squid | Other squids','Source has a focal flying-squid group and a residual other-squids group. A supported closed candidate set and explicit between-group weights are necessary.'),
 ('Octopoda','Octopus or unresolved subcomponents','Catch label explicitly includes argonauts, while source group is benthic Octopus; composition must separate incompatible members.'),
 ('Miscellaneous marine crustaceans','Shrimp | Prawn | Crab or unresolved subcomponents','Source Prawn is Metapenaeus ensis while Shrimp includes other penaeids and Crangon. SAU Shrimp label alone does not determine these source-specific weights.'),
 ('Marine fishes not identified','No currently closed supported set','Cannot split all unidentified demersals among Kyoto species groups while pollock/cod and other major regional stocks lack groups.')]:
 add(t,g,'broader_membership_or_composite_review','Conditional potential only; do not adopt automatically',reason)
c=pd.DataFrame(candidates);c.to_csv(P/'PROPOSED_EXTENSIONS.csv',index=False)
first=['Scomber','Auxis','Scomber australasicus']
stats['recommended_first_extension_taxa']=first;stats['recommended_first_extension_count']=len(base)+len(first);stats['recommended_first_extension_2019_pct']=float((base.catch_2019.sum()+d.loc[first,'catch_2019'].sum())/tot19*100);stats['recommended_first_extension_historical_pct']=float((base.catch_1950_2019.sum()+d.loc[first,'catch_1950_2019'].sum())/totall*100)
stats['with_reviewed_main_text_tuna_2019_pct']=stats['recommended_first_extension_2019_pct']+float(d.loc['Thunnus orientalis','catch_2019']/tot19*100)
audit=json.loads((P/'source_name_taxonomy_audit.json').read_text());stats['source_binomials_queried']=len(audit);stats['names_with_records']=sum(bool(x['records']) for x in audit);stats['unrecognized_exact_names']=[x['source_name'] for x in audit if not x['records']]
new=[r['valid_name'] for x in audit for r in x['records'] if r.get('valid_name') in un.index];assert new==[];stats['additional_unambiguous_accepted_name_matches']=new
stats['no_production_edits']=before=={k:sha(REG/k) for k in before};assert stats['no_production_edits']
(P/'REVIEW_NUMBERS.json').write_text(json.dumps(stats,indent=2),encoding='utf8')
print(json.dumps(stats,indent=2));print(c[['taxon','2019_coverage_gain_percentage_points','historical_coverage_gain_percentage_points']].to_string(index=False))
