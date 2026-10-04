"""Assemble independent evidence only; does not modify any regional or shared input."""
from pathlib import Path
from decimal import Decimal
import hashlib, json

OUT = Path(__file__).resolve().parent
ROOT = next(p for p in OUT.parents if (p / 'regions/LME_052').is_dir() and (p / 'tools').is_dir())
MID = '52_1_Sea_of_Okhotsk_NE_(1980)'
E = ROOT / 'regions/LME_052/validation_reports' / MID
CANONICAL = ROOT / 'regions/LME_052/models' / MID / 'model.json'
SOURCE = ROOT / 'regions/LME_052/papers/OKH-2004/Palomares20_FishCentResaRep28-440d8aa8.pdf'
HISTORY = ROOT / 'original_research_archive/research/size_allocation_20260929/lme_east'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def rel(p):
    return p.relative_to(ROOT).as_posix()

assert sha(CANONICAL) == '61b6176affe6051948b3ec972fe87d95dabd8d98b66744b4c7350fcf303b9099'
assert sha(SOURCE) == '440d8aa860813d435891b107bf85340df773df322c83fa1f9f82069e3661851d'
basic = read(OUT / 'native_basic_parameter_ledger.json')
diet = read(OUT / 'native_diet_ledger.json')
verification = read(OUT / 'candidate_vector_verification.json')
audit = read(E / 'taxon_audit.json')
for path, expected in verification['input_hashes'].items():
    assert sha(ROOT / path) == expected, (path, 'Refresh independent verification before handoff')
assert not basic['numeric_B_PB_QB_EE_differences']
assert diet['total_cells'] == 754 and diet['changed_cell_count'] == 74

history = read(HISTORY / 'proposals.json')
pair = next(p for p in history['pairs'] if p['unit_id'] == 'LME_052')
case = next(p for p in pair['proposals'] if p['taxon'] == 'Gadus chalcogrammus')
builder = (HISTORY / 'build_proposals.py').read_text(encoding='utf-8')
lines = builder.splitlines()
locators = [{'line': i + 1, 'text': s.strip()} for i, s in enumerate(lines)
            if "prop('Gadus chalcogrammus'" in s or 'catches=[float(cg[i]' in s or "'assumed_adult_only_no_catch_basis'" in s]
assert case['rule'] == 'assumed_adult_only_no_catch_basis'
assert [x['seq'] for x in case['candidates']] == [7, 6]
assert [x['weight'] for x in case['candidates']] == [0.0, 1.0]
pollock = next(r for r in audit if r['taxon'] == 'Gadus chalcogrammus')
stage = {
    'selected_model_id': MID,
    'canonical_sha256': sha(CANONICAL),
    'native_observation': {'locator': 'Chaikina Table 1 PDF27 / printed26',
                           'adult_or_nonjuvenile_group': 6, 'juvenile_group': 7,
                           'B': [2.475, 2.119],
                           'group_catch_table_recovered': False, 'age_or_length_cutoff_recovered': False,
                           'B_not_observed_caught_mass': True},
    'accepted_export': {'all_29_groups': '0', 'observed_zero_catch_demonstrated': False},
    'historical_proxy': {'builder': rel(HISTORY / 'build_proposals.py'),
                         'builder_sha256': sha(HISTORY / 'build_proposals.py'),
                         'native_code_locators': locators,
                         'selected_proposal': case,
                         'proposals_sha256': sha(HISTORY / 'proposals.json'),
                         'search_audit_sha256': sha(HISTORY / 'online_search_audit.json'),
                         'baseline_audit_sha256': sha(HISTORY / 'LME_052_audit.json'),
                         'actual_computation': 'Reads accepted group.export and checks the loaded values; then passes hard-coded weights [0,1] in juvenile/adult order. No observed donor catch strata are selected.',
                         'interpretation': 'Adult-only is expressly assumed. Accepted export zeros cannot establish an observed all-adult catch.'},
    'reviewed_current_fallback': {'group_order': pollock['group_ids'],
                                'weights': pollock['weights'],
                                'membership': [pollock['membership_rule'], pollock['membership_confidence']],
                                'allocation': [pollock['allocation_rule'], pollock['allocation_confidence']],
                                'calculation': '2.475/(2.475+2.119) and 2.119/(2.475+2.119)',
                                'assumptions': 'Complete source biomass is the approved catch-composition/catchability proxy. Equal catchability and fixed source proportions across years/bases are assumed; no stage threshold or caught age composition is inferred.'},
    'source_search': [
        {'source': 'Native Chaikina chapter, all PDF24–35 text plus Tables1–4',
         'result': 'No stage cutoff or complete group/stage catch observation. Aggregate 1980s catch and local fishing density do not supply either stage fraction.'},
        {'source': 'Native PICES1996 Shuntov/Dulepova PDF267–275 / printed263–271 and Belyaev/Zhigalin PDF308–315 / printed304–311',
         'result': 'Regional fishery, biomass and ecosystem context. No recovered NE-stage cutoff or applicable observed adult/juvenile catch mass.'},
        {'url': 'https://www.sciencedirect.com/science/article/abs/pii/S0165783696005619',
         'doi': '10.1016/S0165-7836(96)00561-9',
         'scope_read': 'Publisher abstract indexed by search, not native full article',
         'result': '1991–94 commercial catch length/age summaries concern a later fishery and lack the source model boundary or complete stage wet-mass shares.'},
        {'url': 'https://russianpollock.com/upload/iblock/b38/summary-tinro-soo-observers-2019.pdf',
         'scope_read': 'Prior search snippets; current HTTPS byte retrieval failed certificate hostname verification',
         'result': 'No archived native observer PDF or usable group-boundary mass fraction; see primary_retrieval_attempts.json.'},
        {'url': 'https://osci.ru/ru/nauka/article/100610/view',
         'scope_read': 'Prior search snippets; current HTTPS byte retrieval failed certificate hostname verification',
         'result': 'No full native study or applicable stage fraction recovered.'},
        {'url': 'https://apps-afsc.fisheries.noaa.gov/Plan_Team/2023/EBSPollock.pdf',
         'scope_read': 'Historical query record, not independently recovered for this review',
         'result': 'Eastern Bering Sea assessment is not an Okhotsk observation and is not transferred as a measured stage split.'}],
    'query_bound_impact': verification['pollock'],
    'limitation': 'Unrecovered evidence is an availability gap, not a claim that usable catch composition never exists. No accepted parameter or export correction is proposed.'}
write('stage_allocation_provenance.json', stage)

pices = OUT / 'PICES_Scientific_Report6_1996_DFO197606.pdf'
pices2018 = OUT / 'PICES_2018_native_book_of_abstracts.pdf'
worm = read(OUT / 'WoRMS_Sardinops_identity_review.json')
native_ledger = {
    'selected_model_id': MID,
    'sources': [
        {'id': 'ChaikinaChapter', 'file': rel(SOURCE), 'sha256': sha(SOURCE),
         'identity': 'Chaikina 2020, Trophic structure of the Sea of Okhotsk ecosystem in the 1980s, in Palomares and Pauly (eds), Marine and Freshwater Miscellanea II, FCRR28(2), 142-page report.',
         'locators': ['PDF24 / printed23: chapter title and original thesis footnote',
                      'PDF25 / printed24: detailed NE vs simplified SD comparison; whole sea, reported1590000 km²',
                      'PDF26 / printed25: 29 detailed functional groups and seasonal annual weighting; microbial-loop exclusions',
                      'PDF27 / printed26: complete Table1 basic parameters',
                      'PDF29–30 / printed28–29: complete Table4a/b diets'],
         'read_scope': 'All 12 chapter pages extracted/read; native parameter and diet pages visually inspected.',
         'limits': 'Related 2020 chapter, not original 2004 thesis. No complete species inventory, group catch table, stage threshold or digitizable author study polygon recovered.'},
        {'id': 'OriginalThesisListing', 'url': 'https://www.seaaroundus.org/theses/',
         'read_scope': 'Readable institutional list',
         'supports': 'Chaikina2004 thesis title and49-page original-source identity.',
         'limits': 'Original thesis bytes were not recovered; no exact original-thesis parameter equivalence is claimed.'},
        {'id': 'PICES1996Native', 'url': 'https://waves-vagues.dfo-mpo.gc.ca/library-bibliotheque/197606.pdf',
         'file': pices.name, 'sha256': sha(pices), 'native_pages': 431,
         'identity': 'Entire PICES Scientific Report6 (1996), despite search returning a chapter snippet.',
         'locators': ['Shuntov/Dulepova PDF267–275 / printed263–271; prose PDF267–269 and Table3 PDF271',
                      'Belyaev/Zhigalin PDF308–315 / printed304–311; prose PDF308–309, Table1 PDF310'],
         'supports': 'Cited regional ecosystem context; crustacean zooplankton components; Far Eastern/Pacific sardine migration and fisheries context.',
         'limits': 'Different spatial/year surveys are not the NE1980 species inventory or allocation observations; no source-specific pollock catch split or sardine binomial recovered.'},
        {'id': 'PICES2018Native', 'url': 'https://meetings.pices.int/publications/book-of-abstracts/2018-PICES-Book-of-Abstracts.pdf',
         'file': pices2018.name, 'sha256': sha(pices2018),
         'locator': 'PDF201 / printed201, BIO-P30 (13836)',
         'read_scope': 'Native publisher PDF page extracted and visually inspected',
         'supports': 'Primary conference abstract explicitly pairs Far Eastern sardine with Sardinops melanostictus and northwest-Pacific/Sea-of-Japan populations.',
         'limits': 'Identity context, not exact Chaikina membership or catch data.'},
        {'id': 'WoRMSIdentity', 'url': worm['url'], 'file': 'WoRMS_Sardinops_melanostictus_response.json',
         'sha256': sha(OUT / 'WoRMS_Sardinops_melanostictus_response.json'),
         'status_code': worm['status_code'], 'records': worm.get('records', []),
         'supports': 'Primary accepted-name bridge309913→217452, S. melanostictus→S. sagax.',
         'limits': 'Taxonomy does not establish the chapter group binomial or whole reporting-label composition.'}],
    'source_parameter_summary': {'native_numeric_B_PB_QB_EE_differences': 0,
                                 'printed_PQ_not_stored_in_canonical_GE': 26,
                                 'diet_cells': diet['total_cells'], 'positive_printed_cells': diet['printed_numeric_cells'],
                                 'blank_cells': diet['blank_cells'], 'printed_numeric_zero_cells': diet['printed_zero_cells'],
                                 'preserved_normalized_consumer_ids': diet['changed_consumer_ids'],
                                 'preserved_normalization_changed_cells': diet['changed_cell_count'],
                                 'maximum_normalization_absolute_error': diet['maximum_accepted_normalization_absolute_error']},
    'geography': {'source_claim': 'Whole Sea of Okhotsk; area1590000 km²',
                  'interpretation': 'NE is the newly detailed Ecopath model, not northeast. The reported whole-sea area does not prove exact canonical LME polygon equality. No replacement footprint is proposed; shared geography belongs to the coordinator.'},
    'protection': 'Accepted B/PB/QB/EE/GE/diet/BA/export/routing/defaults are read-only. Printed source differences are recorded, not restored, normalized, rebalanced or recalculated.'}
write('primary_source_ledger.json', native_ledger)

taxonomy = read(ROOT / 'regions/LME_052/models' / MID / 'source_evidence/mapping' / f'{MID}.taxonomy-sources.json')
selected = read(E / 'taxon_source_links.json')
ambiguous = []
for name, values in taxonomy['queries'].items():
    exact = [r for r in values if r.get('scientificname', '').casefold() == name.casefold()]
    if len(exact) > 1 and name in selected:
        ids = selected[name]
        records = [{k: r.get(k) for k in ['AphiaID', 'scientificname', 'rank', 'status', 'valid_name', 'family', 'phylum']} for r in exact]
        chosen = [r for r in exact if 'Taxon' + str(r['AphiaID']) in ids]
        assert len(chosen) == 1
        assert chosen[0].get('phylum') == 'Chordata', (name, 'Non-fish homonym selected')
        if name == 'Scaridae':
            assert chosen[0]['AphiaID'] == 125557 and chosen[0]['rank'] == 'Family'
        ambiguous.append({'reported_taxon': name, 'exact_name_records': records,
                          'selected': ids, 'source_usage_check': 'Historical fish reporting scope; correct fish lineage/rank retained, not a non-fish homonym or misspelled genus.'})
write('taxonomy_ambiguity_review.json', {'saved_authority_sha256': sha(ROOT / 'regions/LME_052/models' / MID / 'source_evidence/mapping' / f'{MID}.taxonomy-sources.json'),
                                       'selection_link_sha256': sha(E / 'taxon_source_links.json'),
                                       'ambiguities': ambiguous,
                                       'limitation': 'Saved primary records support taxonomy only. Their ordering alone is not the selection rule.'})

findings = {
    'status': 'Bounded independent source and candidate review complete; scientific limitations preserved',
    'selected_model_id': MID,
    'reviewed_input_hashes': verification['input_hashes'],
    'adopted_workbook_matching_verified': verification.get('adopted_workbook_matching_verified', False),
    'resolved_review_findings': [
        {'id': 'PerciformesCompleteness', 'result': 'Added group8 to8/9/14/15/16/19 through the same weak herring analogue used for eligible mackerel members of the historical reporting union. Herring is not taxonomically Perciformes and no exact NE membership is claimed. Very low membership remains.'},
        {'id': 'CrustaceanAnalogueAlternatives', 'result': 'Panulirus and Squillidae retain20+23 rather than a unique named crab/shrimp placement. Both residual carnivorous benthos and represented crustacean proximity are explicit weak analogues; complete biomass fallback remains Medium.'},
        {'id': 'SalmonPoolDescription', 'result': 'The source Salmon pool is not a defined large-pelagic-piscivore guild. The reviewed rationale now states predominantly zooplankton diet and unknown species/size composition; mobile marine water-column fish use remains a Very low ecological analogue.'}],
    'native_source_findings': [
        'Available primary source is the2020 Chaikina chapter based on the2004 thesis, not the original thesis.',
        'Detailed whole-sea NE29-group model is distinct from the9-group simplified SD comparison; NE does not mean northeast.',
        'All printed B/PB/QB/EE match the accepted JSON.26 printed P/Q values are absent from GE and remain protected source differences.',
        'Complete754-cell native diet audit reproduces preserved normalization in8 columns and74 changed cells;580 blanks are retained as source blanks separately from arithmetic zeros.',
        'No complete native group catch observations or pollock age/length threshold were recovered. All accepted export0 values are not demonstrated observed zero catches.',
        'The historical adult-only pollock proxy was hard-coded after reading accepted zero exports; it has no measured caught-mass composition basis.',
        'Current complete native B2.475/2.119 allocation is53.87461906835002%/46.12538093164998%, an approved Medium assumption, not measured age composition.',
        'The chapter Pacific Sardine lacks a binomial. Retained primary regional and accepted-name evidence supports the existing Medium inferred Sardinops connection without an exact inventory claim.'],
    'numeric_verification': {k: verification[k] for k in ['taxa', 'zero_catch_taxa', 'split_taxa', 'confidence_counts', 'maximum_W9_vector_absolute_error_vs_native_Decimal_B', 'pollock', 'unresolved']},
    'scientific_limits': [
        'Unknown original-thesis details, guild species composition, source catch and pollock threshold remain gaps.',
        'Broad residual and analogue vectors use whole pooled biomass including non-target co-members; they are not observed caught composition.',
        'Fixed1980s annual source proportions transfer across1950–2019 landings, catch and discards without reconstructing annual stage/guild composition.',
        'Whole-sea intention and reported1590000 km² do not demonstrate exact polygon overlap.',
        'Cyprinidae remains unresolved; numerical diagnostics, FAIL/warnings and production eligibility belong to the lead/coordinator and are not changed or approved here.',
        'No solver, Monte Carlo, parameter restoration, balancing, normalization, pipeline writer, production or Git mutation was performed by this reviewer.'],
    'ownership': 'Only independent_source_review scratch was written. No children were spawned.'}
write('findings.json', findings)

text = f'''# Independent LME052 source and mapping review

The accepted `{MID}` is the detailed **29-group NE model of the whole Sea of Okhotsk**, distinct from the simplified 9-group SD comparison. NE does not mean northeastern. The available source is Chaikina's **2020 chapter**, PDF 24–35 / printed 23–34, in the 142-page report. Its footnote identifies a 49-page 2004 thesis; those original thesis bytes were not recovered.

Native Table 1 (PDF 27 / printed 26) matches accepted B/PB/QB/EE wherever printed. The 26 printed P/Q values are absent from accepted GE. Printed blank fields, annual weighting and the atypical printed biomass unit header are retained without a parameter or unit repair. Full Table 4a/b (PDF 29–30 / printed 28–29) has 754 cells, 174 positive printed values and 580 blanks. The accepted model preserves normalization of 8 source column totals (.998/.999/1.001), changing 74 nonzero cells. Both complete grids, native bounding boxes and source/canonical cell comparisons are retained in JSON.

No complete group catch table or pollock age/length boundary was recovered. Accepted export zeros have unverified observational provenance. The historical 20260929 builder explicitly supplied juvenile/adult weights 0/1 after reading those zeros; it did not reconstruct observed donor strata. The reviewed pollock fallback uses complete source B 2.475/2.119, giving 53.87461906835002%/46.12538093164998% with **Medium allocation confidence**. Equal catchability and fixed source composition are assumptions. In the exact 2019 all-source landings query, pollock is 48.91566270806395% of catch; this is distinct from the earlier coordinator estimate.

All 151 labels, including 27 zero-catch labels, were independently checked for source-group partitions, exact reporting names, weakest confidence and complete native biomass vectors. The revised Perciformes set includes herring group 8 only through the weak analogue used for eligible schooling mackerels; it does not claim herring is taxonomically Perciformes. Lobster and mantis-shrimp labels retain both groups 20 and 23 as weak crustacean/carnivorous-benthos analogues. The native Salmon pool has predominantly zooplankton diet and no species/size inventory; its analogue wording now reflects that limitation. Source Sardinops identity remains a **Medium regional inference**: primary PICES context and WoRMS synonymy strengthen it without supplying the chapter's binomial.

The reported 1,590,000 km² whole-sea domain is not proof of exact canonical LME overlap. Source species inventories, native catches and stage boundaries remain unresolved; Cyprinidae remains unmapped. No accepted model parameter, diagnostic status or shared scientific approval is changed by this review.

Exact reviewed bytes and checks are in [findings.json](findings.json), [candidate_vector_verification.json](candidate_vector_verification.json), [stage_allocation_provenance.json](stage_allocation_provenance.json) and [primary_source_ledger.json](primary_source_ledger.json). Reproduce from a relocated repository with `python -u -Xutf8 -B verify_native_tables.py`, then `python -u -Xutf8 -B verify_candidate_vectors.py --verify-adopted` once the regional lead has adopted the reviewed mapping. These scripts write only beside themselves.
'''
(OUT / 'source_identity_review.md').write_text(text, encoding='utf-8')

selected_files = [
    'source_identity_review.md', 'findings.json', 'primary_source_ledger.json',
    'stage_allocation_provenance.json', 'taxonomy_ambiguity_review.json',
    'native_basic_parameter_ledger.json', 'native_diet_ledger.json', 'native_chapter_text.json',
    'native_table_PDF27_grid.json', 'native_table_PDF29_grid.json', 'native_table_PDF30_grid.json',
    'native_PDF24.png', 'native_PDF25.png', 'native_PDF26.png', 'native_PDF27.png', 'native_PDF29.png', 'native_PDF30.png',
    'verify_native_tables.py', 'verify_candidate_vectors.py', 'build_review_handoff.py',
    'candidate_vector_verification.json', 'primary_retrieval_attempts.json',
    'PICES_Scientific_Report6_1996_DFO197606.pdf', 'PICES_Report6_native_text.txt',
    'PICES6_native_PDF267.png', 'PICES6_native_PDF271.png', 'PICES6_native_PDF308.png',
    'PICES_2018_native_book_of_abstracts.pdf', 'PICES2018_sardine_identity.json', 'PICES2018_native_PDF201.png',
    'WoRMS_Sardinops_melanostictus_response.json', 'WoRMS_Sardinops_identity_review.json']
manifest = {'copy_not_move': True, 'source_directory': rel(OUT),
            'scope': 'Selected portable primary/native review evidence; production inputs remain outside reviewer ownership.',
            'files': [{'file': n, 'sha256': sha(OUT / n), 'bytes': (OUT / n).stat().st_size} for n in selected_files]}
write('selected_evidence_manifest.json', manifest)
write('delivery_hashes.json', {'reviewed_inputs': verification['input_hashes'],
                             'selected_manifest_sha256': sha(OUT / 'selected_evidence_manifest.json'),
                             'review_file_hashes': {n: sha(OUT / n) for n in ['findings.json', 'source_identity_review.md', 'primary_source_ledger.json', 'stage_allocation_provenance.json', 'candidate_vector_verification.json', 'taxonomy_ambiguity_review.json']},
                             'reviewer_owned_directory': rel(OUT), 'ownership_released_to_coordinator_on_final_message': True,
                             'no_scientific_approval_claim': True})
print(json.dumps({'findings_sha256': sha(OUT / 'findings.json'),
                  'manifest_sha256': sha(OUT / 'selected_evidence_manifest.json'),
                  'adopted_matching_verified': verification.get('adopted_workbook_matching_verified', False),
                  'files_for_copy': len(selected_files)}, indent=2))
