"""Add profile and candidate taxonomy without changing canonical model bytes."""
import csv,json,subprocess,sys
from decimal import Decimal
from aggregated_extract import MODEL,RUN,ROOT,MODEL_ID,COMMIT,CITATION,PDF,dump,sha,relative,rows

def main():
    canonical=MODEL/'model.json';before=sha(canonical)
    data=json.loads(canonical.read_text(encoding='utf-8'));groups=data['group']
    tables=MODEL/'extracted_tables';ev=tables/'evidence'
    source=tables/'companions/Aggregation_membership_Table1.csv'
    membership=rows(source);head=membership[0]
    source_records={int(r[0]):dict(zip(head,r)) for r in membership[1:]}
    candidate=[['seq','group_name','taxon_descr']]
    evidence=[]
    for g in groups:
        seq=int(g['group_seq']);r=source_records[seq]
        assert g['group_name']==r['rpath_group']
        # These are explicit source functional groups, not invented Latin taxa.
        description='Source functional groups: '+r['original_groups_Table1']
        candidate.append([str(seq),g['group_name'],description])
        evidence.append({'seq':seq,'group_name':g['group_name'],'candidate_taxon_descr':description,
          'membership_scope':'Original functional-group membership in aggregate; not an exhaustive species inventory',
          'source_url':PDF,'source_locator':'Whitehouse and Aydin 2020 Table 1, GOA column, pp.5-7',
          'retained_source_path':'../companions/Aggregation_membership_Table1.csv','retained_source_sha256':sha(source),
          'verification':'Indexed PDF text transcription; visual verification pending',
          'taxonomic_authority_status':'pending; no accepted synonyms, AphiaIDs or new scientific names assigned',
          'stage_bounds':'Numeric age/length cutoffs not documented in inspected aggregate sources',
          'canonical_taxon_descr_present':g.get('taxon_descr') is not None,
          'applied_to_canonical':False})
    csvpath=ev/'candidate_taxonomy.csv'
    with csvpath.open('w',encoding='utf-8',newline='') as f:csv.writer(f,lineterminator='\r\n').writerows(candidate)
    destination=tables/'Taxonomy.xlsx'
    proc=subprocess.run([sys.executable,str(ROOT/'tools/skills/paper-to-ppr/scripts/write_taxonomy.py'),str(csvpath),str(destination)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    (ev/'candidate_taxonomy_writer.log').write_text(proc.stdout+proc.stderr,encoding='utf-8')
    assert proc.returncode==0,proc.stdout+proc.stderr
    import openpyxl
    wb=openpyxl.load_workbook(destination,data_only=False)
    actual=[list(r) for r in wb.active.iter_rows(values_only=True)]
    checks={'one_sheet':len(wb.sheetnames)==1,'three_columns':wb.active.max_column==3,'all_49_groups':len(actual)==50,
      'exact_rows_labels_descriptions':actual==candidate,'group31_native_punctuation':actual[31][1]=='Urchins, dollars, cucumbers',
      'no_blank_descriptions':all(r[2] for r in actual[1:]),'canonical_unchanged':sha(canonical)==before}
    wb.close();assert all(checks.values()),checks
    evidence_doc={'schema_version':1,'model_id':MODEL_ID,'canonical_sha256':before,'candidate_only':True,
      'source_scope':'2020 Table 1 original functional-group membership; inherited species-level Appendix A membership has not been transferred to this aggregate.',
      'authority_status':'pending','canonical_taxon_descr_count':sum(g.get('taxon_descr') is not None for g in groups),
      'canonical_modified':False,'records':evidence}
    dump(ev/'candidate_taxonomy_evidence.json',evidence_doc)
    dump(ev/'candidate_taxonomy_check.json',{'schema_version':1,'checks':checks,'all_passed':all(checks.values()),'canonical_sha256_before':before,'canonical_sha256_after':sha(canonical),'taxonomy_sha256':sha(destination),'rows_including_header':50,'columns':['seq','group_name','taxon_descr'],'writer':'tools/skills/paper-to-ppr/scripts/write_taxonomy.py','writer_sha256':sha(ROOT/'tools/skills/paper-to-ppr/scripts/write_taxonomy.py')})
    catch_groups=[g['group_name'] for g in groups if Decimal(g['landings_total'])+Decimal(g['discards_total'])>0]
    profile=f'''# Gulf of Alaska official Rpath aggregate (1990–1994)

**Model:** `{MODEL_ID}`. **Source:** {CITATION}

**Structure:** Mixed taxonomic and functional/guild aggregation: marine mammals and seabirds; fish taxa and feeding/habitat guilds; pelagic and benthic invertebrates; microbes; primary production and detrital pools. Native types are 46 consumers (Type 0), one producer (Type 1), two detritus pools (Type 2) and one separate fleet (Type 3). The native group names and type codes below are exact. Ecological labels are source group labels, not new membership rules.

**Life stage and size:** Native `Salmon returning` and `Salmon outgoing` remain separate. Juvenile/adult pollock and cod, and several other original juvenile/adult groups, are combined in the 2020 Table 1 aggregate. The official Ecosense.GOA documentation explicitly states **no stanzas**. Numeric age, length or size cutoffs are not supplied by the inspected aggregate parameter files. `Lg.-mouth` and `Sm.-mouth` are source functional labels, not numerical length boundaries.

**Spatial prefixes:** None in the native 49-group labels. The documentation's “west/central” title describes the model context; it does not assign separate spatial strata to the native groups. Original west/central Steller sea-lion groups are not separately retained. No allocation between geographic pools is inferred.

**Period and area:** The 1990s source documentation inherits the original Aydin et al. 2007 base period, 1990–1994. Publication in 2020 is distinct from that base period. The 2020 article §2.2.3 (p.4) reports shelf waters from 140°W to 170°W and **291,840 km²**. Biomass and annual flow inputs are standardized to the whole modeled area. Relation to the current LME catch boundary and coverage percentage remains unmeasured; no equality with the entire LME catch unit is assumed.

**Single named stocks and pools:** `Gray whale`, `Walleye pollock` and `Pacific cod` are named taxa/stock groups. Labels such as `Toothed whales`, `Other pinnipeds`, `Pelagic forage fish`, `Other demersals`, `Other crabs` and `Other zooplankton` identify aggregated pools. Primary production combines the source production compartments; pelagic and benthic detritus combine source detrital compartments. The Table 1 membership companion records the source group constituents; it does not resolve every species or every original model version.

**Catch:** One source fleet, `Fishery/Subsistence`. Landings and discards are retained for all 49 biological rows. The list below records positive native removals only; zero catch is not a biological exclusion rule, and no regional catch assignment has been made.

Positive native removals: { '; '.join(catch_groups) }.

**Lineage caveat:** The official repository, pinned at `{COMMIT}`, identifies Ecosense.GOA as an aggregate of Aydin et al. (2007). The 2020 paper says the original GOA model had 138 groups, whereas the separate published Appendix C extraction contains 133 biological compartments. These counts do not establish a bijection or exact native-version equivalence. The Table 1 wording also does not resolve all west/central Steller sea-lion subdivisions. No native data from a different CGOA/EBS model was substituted.

**Candidate taxonomy and authority:** [Taxonomy.xlsx](extracted_tables/Taxonomy.xlsx) contains exactly `seq`, `group_name`, `taxon_descr`, with one row for every native biological group. Descriptions retain only Table 1's original functional-group membership. They are not an exhaustive scientific-name list. PDF visual verification and taxonomic-authority reconciliation are **pending**; no accepted names, synonym replacements or authority identifiers have been invented. [Candidate evidence](extracted_tables/evidence/candidate_taxonomy_evidence.json) records these limits per group. Canonical `taxon_descr` remains null for all 49 groups and the canonical hash is unchanged; this candidate workbook has not been applied to the model.

**Naming:** The candidate workbook uses exact native names, including group 31 `Urchins, dollars, cucumbers`. The strict eight imports use the documented representation-only alias `Urchins dollars cucumbers`. Any later authorized taxonomy import must use the [label crosswalk](extracted_tables/companions/Group_label_crosswalk.csv); no unreviewed converter rerun is implied.

**Evidence:** [Native provenance](inputs/provenance.json); [Table 1 membership](extracted_tables/companions/Aggregation_membership_Table1.csv); [candidate workbook checks](extracted_tables/evidence/candidate_taxonomy_check.json); [extraction report](extracted_tables/evidence/REPORT.md). The candidate workbook has a separate shape/content verification and is not part of the original eight-import reconstruction count.

| Native group ID | Exact native name | Native type |
| --- | --- | --- |
'''
    for g in groups:profile+=f"| {g['group_seq']} | {g['group_name']} | {g['pp']} |\n"
    profile+='| 50 (fleet only) | Fishery/Subsistence | 3 |\n'
    profile_path=MODEL/'MODEL_PROFILE.md';profile_path.write_text(profile,encoding='utf-8')
    notes=MODEL/'model_notes.md';text=notes.read_text(encoding='utf-8')
    addition='\n\n## Candidate group structure and taxonomy\n\n[MODEL_PROFILE.md](MODEL_PROFILE.md) records source guild/stage/spatial structure and the period/area basis. [Candidate Taxonomy.xlsx](extracted_tables/Taxonomy.xlsx) retains the source Table 1 functional-group membership for all 49 exact native labels, with visual and taxonomic-authority review pending. It has not been applied to canonical taxon_descr, which remains null. The canonical model bytes and numerical extraction are unchanged. See [candidate evidence](extracted_tables/evidence/candidate_taxonomy_evidence.json).\n'
    if '## Candidate group structure and taxonomy' not in text:notes.write_text(text+addition,encoding='utf-8')
    report=ev/'REPORT.md';text=report.read_text(encoding='utf-8')
    addition='\n\n## Candidate taxonomy handoff\n\nMODEL_PROFILE.md is retained beside the extracted_tables directory. Candidate Taxonomy.xlsx has one sheet and exactly the columns seq, group_name, taxon_descr, with all 49 native biological groups. It preserves the group 31 native comma punctuation. Descriptions are source functional-group constituents from the retained 2020 Table 1 evidence, not newly resolved species taxonomy. Visual verification and taxonomic authority are pending. The canonical JSON retains null taxon_descr and its previous hash. The candidate workbook is independently checked and has not changed the eight-import/seven-companion reconstruction.\n'
    if '## Candidate taxonomy handoff' not in text:report.write_text(text+addition,encoding='utf-8')
    indexpath=ev/'evidence_index.json';index=json.loads(indexpath.read_text(encoding='utf-8'))
    additions=[('model_profile',profile_path),('candidate_taxonomy',destination),('candidate_taxonomy_evidence',ev/'candidate_taxonomy_evidence.json'),('candidate_taxonomy_check',ev/'candidate_taxonomy_check.json'),('candidate_taxonomy_input',csvpath),('supporting_evidence',ev/'candidate_taxonomy_writer.log'),('reproduction_code',Path(__file__).resolve())]
    for role,p in additions:
        rel=relative(p,ev);index['artifacts']=[a for a in index['artifacts'] if a.get('path')!=rel]
        index['artifacts'].append({'role':role,'path':rel,'sha256':sha(p),'availability':'present'})
    for a in index['artifacts']:
        if a.get('path') in [relative(notes,ev),relative(report,ev)]:a['sha256']=sha(ev/a['path'])
    for role in ['model_profile','candidate_taxonomy','candidate_taxonomy_evidence','candidate_taxonomy_check']:
        if role not in index['required_roles']:index['required_roles'].append(role)
    index['reconciliation']['candidate_taxonomy_labels_and_shape']=all(checks.values())
    index['reconciliation']['canonical_hash_unchanged_after_candidate_taxonomy']=sha(canonical)==before
    dump(indexpath,index)
    proc=subprocess.run([sys.executable,str(ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py'),str(indexpath),'--output',str(ev/'completeness.json')],capture_output=True,text=True,encoding='utf-8',errors='replace')
    assert proc.returncode==0,proc.stdout+proc.stderr
    print(json.dumps({'profile':relative(profile_path,ROOT),'candidate_taxonomy':relative(destination,ROOT),'checks':checks,'canonical_sha256':sha(canonical),'evidence_complete':True},indent=2))

if __name__=='__main__':
    from pathlib import Path
    main()
