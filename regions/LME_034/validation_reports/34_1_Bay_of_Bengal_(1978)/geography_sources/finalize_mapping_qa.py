from pathlib import Path
import json, hashlib, datetime

root=Path.cwd()
out=root/'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/geography_sources'
audit_path=root/'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/mapping_review/audit_decisions.json'
audit=json.loads(audit_path.read_text(encoding='utf8'))
checks=json.loads((out/'independent_mapping_qa_checks.json').read_text(encoding='utf8'))
rows=audit['decisions']
assert len(rows)==315 and not checks['mechanical_concerns']
source_pdf=root/'regions/LME_034/papers/LME034-Guenette-2013/009031359-84f3dc3d.pdf'
qa={
 'schema_version':1,'review_date':'2026-09-30','model_id':audit['model_id'],'year':audit['year'],'catch_basis':audit['catch_basis'],
 'reviewed_audit_path':str(audit_path.relative_to(root)).replace('\\','/'),
 'reviewed_audit_sha256':hashlib.sha256(audit_path.read_bytes()).hexdigest(),
 'source_pdf_sha256':hashlib.sha256(source_pdf.read_bytes()).hexdigest(),
 'scope':'Independent review of all315 decisions, including High/Medium and zero-catch records; manual comparison of candidate sets/rationales against A1.1 pp37–41, A1.3 pp43–45 and provider categories, with A1.2p42 geographic criteria and A2.1p46 catch area convention. Read-only proposals review; no scientific calculator/authoritative writer invoked.',
 'status':'No unaddressed concrete candidate-set correction identified in the final reviewed snapshot; two source-exception findings affecting four catch labels were corrected by the mapping reviewer before this handoff.',
 'all_taxa_reviewed':[r['taxon'] for r in rows],
 'checks':checks,
 'candidate_set_review':{'initial_changed_sets':32,'final_changed_sets':sum(r['group_set_changed'] for r in rows),'unchanged_sets_also_reviewed':sum(not r['group_set_changed'] for r in rows),'approach':'Review exact source catch assignments together with named A1.3 members; a family/order/genus label does not establish exclusion of a conflicting named regional pool. Verify provider common_name and commercial/functional labels without treating generic tags as observed constituent composition.'},
 'resolved_concerns':[
  {'affected_taxa':['Batoidea','Elasmobranchii','Chondrichthyes'],'source':'A1.3p43 L pisc explicitly lists Pristis perotteti; original page visually inspected.','initial_finding':'The two-shark-pool union omitted a named sawfish component; Batoidea common_name explicitly includes sawfishes.','resolution':'Added2 L pisc and3 L pisc alongside Oceanic sharks/Coastal elasmobranch; membership now M9 Medium for the inferred union; allocation W4 Medium; overall Medium.','taxonomy_evidence':['WoRMS Pristis perotteti accepted as Pristis pristis; complete ancestry retained by mapping reviewer','https://www.marinespecies.org/aphia.php?p=taxlist&pid=105707&rComp=%3E%3D&tRank=220','https://www.fishbase.org/Summary/speciesSummary.php?id=8940']},
  {'affected_taxa':['Anguilliformes'],'source':'A1.3p45 ML bathy explicitly lists Nemichthys scolopaceus; original page visually inspected.','initial_finding':'Exclusive L pisc assignment omitted a named deep-water eel component; provider Eels,morays/Large demersals is not a documented species-composition exclusion.','resolution':'Added ML bathy alongside2 L pisc and3 L pisc; membership M9 Medium, allocation W4 Medium, overall Medium.','taxonomy_evidence':['Complete WoRMS ancestry retained by mapping reviewer confirms Anguilliformes/Nemichthyidae','https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=118170']}
 ],
 'M2_review':'All nine same-taxon bridges independently match accepted WoRMS AphiaIDs in retained complete authority records. No broader-rank containment is labelled M2. Scyris/Alectis ambiguity is preserved; the Rüppell1830 record supplies the matching bridge and both author alternatives remain Carangids.',
 'M3_review':'All seven M3 cases reviewed against their narrower source catch compartments and retained taxonomy. No overlooked conflicting named source pool was identified for Scomberomorus,Dendrobranchiata,Scylla serrata,Placuna placenta,Teuthida,Mytilidae orPteriomorphia. Teuthida is treated as containment within Cephalopoda, not a synonym of Loliginidae.',
 'geographic_review':{'supported_exclusion':'Region1 shelf-fish pools use the30,998km² Maldives shelf in A1.2; this shelf is outside the actual LME034 boundary.','unsupported_blanket_exclusion':'Region1 open waters overlap the southern LME; its benthos/plankton area is2,845,297km². Entire-region1 exclusion is not a geographic fact.','preserved_candidate':'Malacostraca now retains1,2,3 Zooplankton as genuine zero-catch/zero-weight candidates.','remaining_explicit_assumption':'Excluding1 Macrobenthos for landed benthic categories is a coastal-fishery scope assumption, not source-proven spatial containment. Current rationale/exclusion ledger states this limitation; do not describe the resulting set as an exact geographic partition or a direct measured composition.'},
 'allocation_review':{'rules_checked':['weakest necessary component','finite nonnegative weights','weights sum1','all W4 candidate catch values finite/nonnegative and total positive','native model catch ratios','genuine zero candidate preservation','source caught mass equals density×6,205,051km²','provider2019landings and universe match'], 'catch_density_note':'A2.1p46 states all catches are divided by the whole study area. Do not multiply candidate catches by different group habitat areas. Native/printed small density differences are explicitly retained and belong to the separate reconstruction audit.','source_transfer':'W4 is a fixed pooled1978model catch proxy across taxa, region components, years and total-catch/landings basis, assessed Medium; it is not W10 measured2019taxon-specific composition.'},
 'unresolved_concrete_concerns':[],
 'limitations':['A1.3 is a selected composition list rather than a complete species census; inferred candidate sets remain assumptions and review does not establish measured caught composition.','This review checks current proposed audit decisions. Adoption/recalculation and final Word/Excel/map agreement remain the coordinator responsibility.']
}
(out/'independent_mapping_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'reviewed_taxa':len(rows),'final_changed_sets':qa['candidate_set_review']['final_changed_sets'],'mechanical_concerns':len(checks['mechanical_concerns']),'unresolved_concrete_concerns':qa['unresolved_concrete_concerns'],'audit_sha256':qa['reviewed_audit_sha256']},ensure_ascii=False))
