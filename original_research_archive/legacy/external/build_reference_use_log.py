"""Rebuild the documented reference-use inventory without changing source records.

Run from any directory. --check compares the two deliverables without writing.
The curated annotations below are the maintenance source for references outside
the atlas catalog and for known identity corrections; no network retrieval occurs.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NPP = 'NPPExtraction/METHODS.md'
DIAGNOSTIC = 'docs/LME034_PPR_NPP_diagnostic_2026-09-10.md'
DISCARD = 'research/discard_sensitivity_2026_09_10/results/source_evidence.md'
OSU = 'https://orca.science.oregonstate.edu/references.php'


def reference(key, citation, role, support, evidence, url='', verification='Local documented use; bibliography not freshly reverified online.', limitation=''):
    return dict(id=key, citation=citation, role=role, supports=support,
                local_evidence=evidence if isinstance(evidence,list) else [evidence],
                url=url or None, verification=verification, limitation=limitation or None)


# Bibliography is deliberately no more complete than the inspected evidence.
ADDITIONAL = [
    reference('Pauly-Christensen-1995', 'Pauly, D. and Christensen, V. (1995). Primary production required to sustain global fisheries. Nature 374:255–257.', 'calculation_method',
              'Trophic-chain PPR framework and inclusion of discarded bycatch. The project retains TE=0.1 and applies its wet-equivalent-to-carbon divisor 9 once in display calculations.',
              ['PPREstimation/README.md','docs/discard-audit-2026-09-10/README.md'],
              'https://www.seaaroundus.org/wp-content/uploads/2015/04/PrimaryProductionRequiredToSustainGlobalFisheries.pdf',
              'Original article on author institution site inspected 2026-09-11.',
              'The expanded conversion-factor literature review remains deferred; this entry does not validate a universal region-specific conversion.'),
    reference('Pauly-Christensen-1986-inherited', 'Pauly & Christensen (1986): inherited method attribution; complete reference unresolved.', 'inherited_method_attribution',
              'The calculator documentation attributes a catch-weighted trophic-level approximation to this label.', 'PPREstimation/README.md',
              limitation='The local label alone does not establish a publication identity, title, or DOI. It is retained as unresolved rather than invented.'),
    reference('supplied-2020-MeanTL', 'User-supplied 2020 supplement (original filename: 2020 sup.xlsx); bibliographic identity unresolved in the inspected provenance.', 'calculation_input',
              'Supplies MeanTL reference values, frozen in SeaAroundUsExtraction/input/trophic_levels_2020.csv; its alternative SPPR regressions are not used for the simple chain.',
              ['SeaAroundUsExtraction/README.md','SeaAroundUsExtraction/input/provenance.json','SeaAroundUsExtraction/input/trophic_levels_2020.csv'],
              limitation='The original workbook hash is recorded in input/provenance.json. A year/filename is insufficient to equate it with Luong et al. (2020).'),
    reference('Antoine-Morel-1996', 'Antoine, D. and Morel, A. (1996). Oceanic primary production 1. Adaptation of a spectral light-photosynthesis model in view of application to satellite chlorophyll observations.', 'npp_algorithm',
              'Algorithm lineage for the Copernicus Antoine–Morel NPP input.', NPP, OSU, 'Bibliographic identity checked on the OSU algorithm reference page, 2026-09-11.'),
    reference('Behrenfeld-Falkowski-1997', 'Behrenfeld, M. J. and Falkowski, P. G. (1997). Photosynthetic rates derived from satellite-based chlorophyll concentration. Limnology and Oceanography 42:1–20.', 'npp_algorithm',
              'VGPM algorithm lineage.', NPP, OSU, 'Bibliographic identity checked on the OSU algorithm reference page, 2026-09-11.'),
    reference('Eppley-1972', 'Eppley, R. W. (1972). Temperature and phytoplankton growth in the sea. Fishery Bulletin 70:1063–1085.', 'npp_algorithm',
              'Temperature-response lineage for Eppley-VGPM.', NPP, OSU, 'Bibliographic identity checked on the OSU algorithm reference page, 2026-09-11.'),
    reference('Westberry-2008', 'Westberry, T., Behrenfeld, M. J., Siegel, D. A. and Boss, E. (2008). Carbon-based primary productivity modeling with vertically resolved photoacclimation.', 'npp_algorithm',
              'CbPM2 algorithm lineage.', NPP, OSU, 'Bibliographic identity checked on the OSU algorithm reference page, 2026-09-11.'),
    reference('Silsbe-2016', 'Silsbe, G. M. et al. (2016). The CAFE model: A net production model for global ocean phytoplankton. Global Biogeochemical Cycles 30:1756–1777.', 'npp_algorithm',
              'CAFE algorithm lineage.', NPP, OSU, 'Bibliographic identity checked on the OSU algorithm reference page, 2026-09-11.'),
    reference('Copernicus-GlobColour', 'E.U. Copernicus Marine Service. Global Ocean Colour (Copernicus-GlobColour), Bio-Geo-Chemical, L4. DOI:10.48670/moi-00281.', 'npp_data_product',
              'Monthly PP raster source, product OCEANCOLOUR_GLO_BGC_L4_MY_009_104, used for regional and fixed-atlas NPP.', NPP,
              'https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L4_MY_009_104/description',
              'Primary product page checked in the parent task, 2026-09-10.', 'Data product citation, not an article. Annual coverage and pixel support come from the extraction provenance, not this citation.'),
    reference('Ryan-Keogh-2023', 'Ryan-Keogh, T. J., Thomalla, S. J., Chang, N. and Moalusi, T. (2023). A new global oceanic multi-model net primary productivity data product. Earth System Science Data 15:4829–4848. DOI:10.5194/essd-15-4829-2023.', 'evaluated_alternative_not_used',
              'Documents the OC-CCI multi-model alternative considered during NPP source selection.', NPP,
              'https://essd.copernicus.org/articles/15/4829/2023/', 'Publisher bibliography checked 2026-09-11.',
              'The project did not ingest this alternative; the local methods document records download-size and resolution reasons.'),
    reference('Tam-2008', 'Tam et al. (2008). Trophic modeling of the Northern Humboldt Current Ecosystem, Part I: Comparing trophic linkages under La Niña and El Niño conditions. Progress in Oceanography 79:352–365.', 'model_mapping_lineage',
              'Explicitly adopted predecessor of Chiaverano et al.; supports species examples, hake size groups and model membership.',
              'data/LME_013/mapping/13_2_Northern_Humboldt_Current_(1995-1998).notes.md',
              'https://epic.awi.de/id/eprint/22464/', 'Institutional repository identity checked 2026-09-11; prior mapping notes record original-page inspection.'),
    reference('Christensen-1998', 'Christensen, V. (1998). Fishery-induced changes in a marine ecosystem: insight from models of the Gulf of Thailand. Journal of Fish Biology 53(Suppl. A):128–142. DOI:10.1111/j.1095-8649.1998.tb01023.x.', 'model_identity_and_mapping',
              'Table II identifies the imported Gulf model as 1980 despite its inherited 1963 filename; grouping prose supports catch mapping and the 10–50 m shelf domain.',
              'data/LME_035/mapping/35_412_Gulf_of_Thailande_(1963).notes.md', 'https://doi.org/10.1111/j.1095-8649.1998.tb01023.x',
              'Prior source audit inspected author-linked full HTML and checked 11 biomasses.', 'Publisher PDF was inaccessible; no original-PDF retrieval or complete numerical re-extraction is claimed.'),
    reference('Pauly-Chuenpagdee-2003', 'Pauly, D. and Chuenpagdee, R. (2003). Development of fisheries in the Gulf of Thailand Large Marine Ecosystem.', 'model_lineage_context',
              'Figure 14-3 supports Gulf model lineage; it does not replace the source model parameters.',
              'data/LME_035/mapping/35_412_Gulf_of_Thailande_(1963).notes.md',
              'https://www.seaaroundus.org/doc/Researcher%2BPublications/dpauly/PDF/2003/Books%26Chapters/DevelopmentFisheriesGulfThailandLargeMarineEcosystem.pdf'),
    reference('Vibunpant-2003-excluded', 'Vibunpant (2003), Gulf of Thailand model; full bibliographic identity not recovered in the inspected mapping note.', 'inspected_alternative_not_used',
              'Documents why a 40-group, 1973 model was excluded as direct evidence for the imported Gulf model.',
              'data/LME_035/mapping/35_412_Gulf_of_Thailande_(1963).notes.md', limitation='No title or DOI is inferred from the abbreviated source note.'),
    reference('CMFRI-black-pomfret', 'CMFRI black-pomfret account, repository item 7854, B139.pdf; complete citation not recovered here.', 'taxonomy_mapping_support',
              'Reconciles Formio niger with Parastromateus niger in the Karnataka mapping.',
              'data/LME_032/mapping/32_1_Arabian_Sea_off_Karnataka_(2000).notes.md', 'https://eprints.cmfri.org.in/7854/1/B139.pdf',
              'Prior use documented locally; repository recheck failed 2026-09-11 (robots endpoint unreachable).'),
    reference('Baumann-1995', 'Baumann (1995). A comment on transfer efficiencies. DOI:10.1111/j.1365-2419.1995.tb00150.x.', 'diagnostic_context',
              'Supports sensitivity of a trophic-chain PPR assessment to transfer-efficiency assumptions.', DIAGNOSTIC,
              'https://onlinelibrary.wiley.com/doi/pdf/10.1111/j.1365-2419.1995.tb00150.x', limitation='Does not establish the true transfer efficiency of any current atlas region.'),
    reference('TWAP-Bay-assessment', 'TWAP Bay of Bengal Large Marine Ecosystem assessment, LME 34; complete publication metadata not recovered in the diagnostic.', 'diagnostic_comparison',
              'Provides a historical reported-landings PPR comparison used to explain why catch definitions change the percentage.', DIAGNOSTIC,
              'https://iwlearn.net/documents/download/4348c7eb-92aa-45ac-aa62-891c35e53268',
              'Prior diagnostic used indexed assessment text under Primary Production Required.',
              'The project comparison was not an exact replication of the assessment’s NPP baseline, catch coverage or trophic assignments.'),
    reference('Kalita-Lotliker-2023', 'Kalita and Lotliker (2023). Assessment of satellite-based Net Primary Productivity models in different biogeochemical provinces over the northern Indian Ocean. DOI:10.1080/01431161.2023.2247533.', 'diagnostic_reference_identity_only',
              'Identifies a relevant regional satellite-NPP validation study.', DIAGNOSTIC, 'https://doi.org/10.1080/01431161.2023.2247533',
              'Prior diagnostic verified bibliography via INCOIS/MoES records.', 'Publisher full text was unavailable; no model-ranking conclusion was taken from it.'),
    reference('Prasanna-Kumar-2002', 'Prasanna Kumar et al. (2002). Why is the Bay of Bengal less productive during summer monsoon compared to the Arabian Sea? DOI:10.1029/2002GL016013.', 'diagnostic_context',
              'Supports freshwater-stratification and nutrient-supply mechanisms discussed for the Bay.', DIAGNOSTIC, 'https://doi.org/10.1029/2002GL016013', limitation='Contextual mechanism, not a measured correction to the exported NPP denominator.'),
    reference('Schlosser-2026', 'Schlosser, T. L., Lucas, A. J., Omand, M. and Farrar, J. T. (2026). Monsoons, plumes, and blooms: intraseasonal variability of subsurface primary productivity in the Bay of Bengal. Ocean Science 22:443–458. DOI:10.5194/os-22-443-2026.', 'diagnostic_context',
              'Autonomous observations support discussion of subsurface productivity and monsoon variability.', DIAGNOSTIC,
              'https://os.copernicus.org/articles/22/443/2026/', 'Publisher bibliography and abstract checked 2026-09-11.', 'Does not establish a uniform satellite NPP bias or provide an atlas correction factor.'),
    reference('Luong-2020', 'Luong, Dewulf and De Laender (2020). Quantifying the primary biotic resource use by fisheries: A global assessment. DOI:10.1016/j.scitotenv.2020.137352.', 'diagnostic_context',
              'Supports the point that a detailed food-web method need not yield lower PPR than a conventional trophic chain.', DIAGNOSTIC,
              'https://ilee.unamur.be/publications-1/natural-resources-characterization-and-management',
              'Prior diagnostic used author-institution evidence; DOI endpoint not retrievable in this pass.', 'The rejected discovery-service attribution to Libralato (2008) is not adopted. Linkage to the supplied 2020 MeanTL workbook remains unverified.'),
    reference('EwE-Ecopath-input', 'Ecopath with Ecosim User Guide: Ecopath Input.', 'method_documentation',
              'Defines landings, discards, mortality, discard fate and biological detritus fate as distinct inputs.', DISCARD,
              'https://pressbooks.bccampus.ca/eweguide/chapter/ecopath-input/', limitation='Documentation, not an article or evidence for any historical fleet return fraction.'),
    reference('EwE-spatial-fishery', 'Ecopath with Ecosim: Spatial fishery dynamics.', 'method_documentation',
              'Supports separate fleet landings, discards, mortality and fate fields.', [DISCARD,'docs/discard-audit-2026-09-10/README.md'],
              'https://pressbooks.bccampus.ca/ewemodel/chapter/spatial-fishery-dynamics/'),
    reference('EwE-bycatch-discards', 'Ecopath with Ecosim: Bycatch and discards.', 'method_documentation',
              'Motivates examination of scavenger/trophic effects under alternative discard scenarios.', DISCARD,
              'https://pressbooks.bccampus.ca/ewemodel/chapter/bycatch-and-discards/', limitation='Does not establish a universal return fraction.'),
    reference('Sea-Around-Us-catch-methods', 'Sea Around Us catch reconstruction methods (2016 document) and FAQ.', 'catch_data_documentation',
              'Defines reconstructed catch to include reported and unreported landed and discarded catch; provides the catch-boundary interpretation used in the atlas.',
              ['SeaAroundUsExtraction/README.md','docs/discard-audit-2026-09-10/README.md'],
              'https://www.seaaroundus.org/doc/Methods/CatchReconstructionMethod/Methods-Catch-tab-May-02-2016.pdf', limitation='Data-method documentation; original per-region reconstruction citations remain upstream, not independently verified here.'),
    reference('Sea-Around-Us-regions', 'Sea Around Us, University of British Columbia: LME, High Seas and EEZ geography and published regional metrics.', 'geography_and_reference_data',
              'Supplies ecosystem identities and polygons for regional extraction; published climatological NPP values provide a legacy comparison, not annual observations.',
              [NPP,'SeaAroundUsExtraction/README.md'], 'https://www.seaaroundus.org/',
              limitation='Measured input-polygon areas and source provenance control the extraction. The fixed LME+High-Seas union is not a claim of complete world-ocean coverage.'),
    reference('taxonomy-services', 'WoRMS, FishBase, NCBI Taxonomy, Eschmeyer’s Catalog of Fishes and IMARPE species records.', 'taxonomy_mapping_support',
              'Support nomenclature, taxonomic lineage and explicitly labeled ecological mapping inferences. Individual species citations and responses remain in each mapping taxonomy-sources.json and source-review files.',
              ['data/LME_013/mapping/13_2_Northern_Humboldt_Current_(1995-1998).notes.md','data/LME_032/mapping/32_1_Arabian_Sea_off_Karnataka_(2000).notes.md','data/LME_035/mapping/35_412_Gulf_of_Thailande_(1963).notes.md'],
              'https://www.marinespecies.org/rest/', limitation='Services are not model papers; taxonomic agreement does not establish membership or geographic model applicability.'),
]

OVERRIDES = {
    'HUM-2018': ('model_parameters_mapping_and_original_discard_audit', 'Chiaverano et al. (2018), original article and supplement, provide the Northern Humboldt model, added jellyfish groups, membership evidence and explicit fleet landings/discards/fates. Original title: Evaluating the role of large jellyfish and forage fishes as energy pathways, and their interplay with fisheries, in the Northern Humboldt Current System. The catalog title is abbreviated.', [DISCARD,'data/LME_013/mapping/13_2_Northern_Humboldt_Current_(1995-1998).notes.md']),
    'GUI-2004': ('model_parameters_mapping_and_original_discard_audit', 'The actual Guinea source is Guénette and Diallo (2004), Addendum: Modèles de la côte guinéenne, 1985 et 1998, pp.124–159 in this compilation. Tables support membership, 1998 model parameters and assumed discard amounts; fleet destination remains unknown. Compilation editors are not chapter authors.', [DISCARD,'data/LME_028/mapping/28_646_Guinea_(1998).notes.md']),
    'OKH-2004': ('model_identity_mapping_and_original_discard_audit', 'The recovered source used is Chaikina (2020), A model of the Okhotsk Sea with a focus on marine mammals, pp.23–34, FCRR 28(2), based on her unavailable 2004 thesis. Tables support group/diet evidence and the 1980s whole-Sea identity; no source catch vector was recovered. The inherited 2004 catalog record must not be mistaken for a retrieved thesis.', [DISCARD,'data/LME_052/mapping/52_1_Sea_of_Okhotsk_NE_(1980).notes.md']),
    'ARAB-2005': ('model_parameters_and_mapping', 'CMFRI Bulletin 51 supports the Karnataka model and 129 numbered members. Repository metadata labels the report 2008; mapping notes call it 2005 and the source ID retains 2005. Preserve this discrepancy. Primary repository checked 2026-09-11: https://eprints.cmfri.org.in/3945/. Geographic transfer is Karnataka shelf to Arabian Sea LME.', ['data/LME_032/mapping/32_1_Arabian_Sea_off_Karnataka_(2000).notes.md']),
    'SCS-2007': ('model_parameters_and_mapping', 'Cheung’s thesis Tables 6.1/6.2 and Appendices 6.1/6.2 support distinct 1970s/2000s models and functional-group membership. Source conflicts remain documented; models cover a northern shelf subregion.', ['data/LME_036/mapping/36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s).notes.md']),
    'ECS-2022': ('model_parameters_and_mapping', 'Xu et al. (2022) and Table S1 support separate 1997/2018 East China Sea models and species-group mapping; variants are not averaged.', ['data/LME_047/mapping/47_1_East_China_Sea_(1997).notes.md','data/LME_047/mapping/47_2_East_China_Sea_(2018).notes.md']),
    'LME034-Guenette-2013': ('model_parameters_mapping_and_original_discard_audit', 'Guénette’s December 2013, 62-page report is the direct Bay model and mapping source: Appendices A1.1–A1.3, Table 16 and catch Appendix A2.1. It supports total-catch semantics; a separate original discard split and fleet return route remain unknown.', [DISCARD,'data/LME_034/mapping/34_1_Bay_of_Bengal_(1978).notes.md']),
    'NS-2025': ('isolated_validation_not_production', 'Saygu et al. (2025) author supplements were extracted for the isolated East Coast of Scotland 1991–1995 validation; this does not authorize production pilot inclusion.', ['docs/NEW_PAPER_VALIDATION.md']),
    'KUR-2025': ('inspected_alternative_not_used', 'Gan et al. (2025) and its supplement were inspected as an alternate extraction-validation candidate. Many diet cells report only + (<0.01), so it was not selected for the exact-value validation.', ['docs/NEW_PAPER_VALIDATION.md']),
    'BOB-2014': ('companion_sought_not_obtained', 'The model user guide was sought as a possible source of the original EwE model; the host failed. It was not used to supply membership or numerical data.', ['data/LME_034/mapping/34_1_Bay_of_Bengal_(1978).notes.md']),
}


def build():
    catalog_path = ROOT / 'PPRAtlas/data/articles.csv'
    rows = list(csv.DictReader(catalog_path.open(encoding='utf-8-sig', newline='')))
    selection_path = ROOT / 'data/atlas_selection.json'
    selection = json.loads(selection_path.read_text(encoding='utf-8'))['units']
    selected = {article for item in selection.values() for article in item.get('selected_articles', [])}
    groups = {}
    for row in rows:
        groups.setdefault(row['source_article_id'] or row['article_id'], []).append(row)
    records = []
    fields = ('article_id','unit_id','authors','publication_year','title','doi','landing_page','source_urls',
              'article_dir','provenance','correction_notes','retrieval_audit','download_status','loadability_class','extraction_readiness')
    for source_id, items in sorted(groups.items()):
        is_selected = any(item['article_id'] in selected for item in items)
        role = 'selected_pilot_source_pending_model_evidence' if is_selected else 'archive_candidate_not_calculation_input'
        support = ('Selected as a pilot source; selection alone does not establish a verified mapping/model or authorize every method.' if is_selected else
                   'Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.')
        evidence = ['PPRAtlas/data/articles.csv'] + (['data/atlas_selection.json'] if is_selected else [])
        if source_id in OVERRIDES:
            role, support, extra = OVERRIDES[source_id]
            evidence += extra
        records.append({'source_article_id':source_id,'role':role,'supports':support,
                        'selected_article_ids':[item['article_id'] for item in items if item['article_id'] in selected],
                        'local_evidence':evidence,'verification':'Catalog bibliography preserved verbatim; source-audit corrections and access limits are stated in the use annotation. Catalog membership is not fresh bibliographic verification.',
                        'catalog_records':[{key:item.get(key,'') for key in fields} for item in items]})
    known_ids = {item['article_id'] for item in rows}
    assert selected <= known_ids, 'Selected article IDs must be present in the catalog'
    assert sum(len(record['catalog_records']) for record in records) == len(rows)
    evidence_paths = sorted({path for record in records + ADDITIONAL for path in record['local_evidence']})
    for relative in evidence_paths:
        assert (ROOT / relative).is_file(), f'Missing local evidence: {relative}'
    payload = {'schema_version':1,'audit_date':'2026-09-11','scope':'Documented project use; not recursive bibliography of every archived article.',
               'catalog_rows':len(rows),'catalog_source_identities':len(records),'additional_references':len(ADDITIONAL),
               'selected_article_rows':len(selected),'catalog_references':records,'additional_reference_uses':ADDITIONAL,
               'evidence_files':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in evidence_paths],
               'selection_sha256':hashlib.sha256(selection_path.read_bytes()).hexdigest()}
    lines = ['# Article reference and use log', '', 'Audit date: 11 September 2026.', '',
        f'This log covers every row in the project’s article inventory: **{len(rows)} regional records grouped under {len(records)} source IDs**, plus **{len(ADDITIONAL)} documented method, input, diagnostic and supporting references**. Source IDs are catalog identities, not a claim that all are unique or bibliographically verified publications.', '',
        'Simple trophic-chain PPR uses catch and reference trophic levels independently of this article inventory. Model-based estimates use separately verified model/mapping evidence. Satellite NPP uses the documented raster products. An archived or selected paper alone does not establish computational coverage.', '',
        'The inventory records what the project used: model inputs and mapping evidence, algorithm lineage, interpretation, or candidate discovery. It does not recursively list every reference printed inside every archived paper. Inaccessible, rejected and inherited records remain visible. The separate unfinished expanded discard study is outside this audit.', '',
        '## Calculation methods, inputs and supporting references', '']
    for record in ADDITIONAL:
        lines += [f"### {record['id']}",'',record['citation'],'',f"**Role:** {record['role']}. {record['supports']}",'',
                  f"**Evidence:** {record['verification']}"]
        if record['limitation']: lines += ['',f"**Limit:** {record['limitation']}"]
        if record['url']: lines += ['',f"[Reference / source]({record['url']})"]
        lines += ['', 'Local use: ' + '; '.join(f'[{Path(p).name}](../{p.replace(" ","%20")})' for p in record['local_evidence']) + '.', '']
    lines += ['## Complete catalog reference inventory', '',
              'Bibliographic fields below are inherited from the catalog; corrections in the use paragraphs take precedence for the stated application. Repeated source IDs preserve every regional row in the companion JSON, including different bibliography, correction notes and retrieval status. No missing author, year, title or DOI is silently completed.', '']
    for record in records:
        item = record['catalog_records'][0]
        citation = f"{item['authors'] or '[authors unavailable]'} ({item['publication_year'] or 'year unavailable'}). {item['title'] or '[title unavailable]'}."
        url = ('https://doi.org/'+item['doi']) if item['doi'] else item['landing_page']
        lines += [f"### {record['source_article_id']}",'',citation,'',
                  f"**Role:** {record['role']}. {record['supports']}",'',
                  'Regional records: '+', '.join(f"`{r['article_id']}`" for r in record['catalog_records'])+'.',
                  'Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.']
        if url: lines += ['',f'[Catalog reference link]({url})']
        lines += ['', 'Local use: ' + '; '.join(f'[{Path(p).name}](../{p.replace(" ","%20")})' for p in record['local_evidence']) + '.', '']
    lines += ['## Maintaining this log', '',
              'Update the authoritative article catalog and selection only when the underlying project evidence changes. Add a new method/context/input reference to `ADDITIONAL`, or a documented use/correction to `OVERRIDES`, in `external/build_reference_use_log.py`. State what claim or calculation it supports, its local evidence, access limits and verification date. Keep candidate-only, selected, verified computational, isolated-validation and contextual roles separate.', '',
              'Run `python external/build_reference_use_log.py`, then `python external/build_reference_use_log.py --check`. The companion `ARTICLE_REFERENCE_USE_LOG.json` retains every source row, role and evidence-file hash. Regenerate after changes to any hashed evidence document. A changed hash requests review; it does not itself verify a publication.', '',
              'Unresolved bibliography to retain explicitly: the supplied 2020 MeanTL workbook’s parent article; the inherited 1986 method attribution; incomplete contextual citations; and the CMFRI 2005/2008 year discrepancy. Do not equate a source filename with a publication identity. The conversion-factor literature review remains deferred.', '']
    return {'ARTICLE_REFERENCE_USE_LOG.md':'\n'.join(lines),
            'ARTICLE_REFERENCE_USE_LOG.json':json.dumps(payload,ensure_ascii=False,indent=2)+'\n'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = build()
    for name, content in outputs.items():
        path = Path(__file__).parent / name
        if args.check:
            assert path.read_text(encoding='utf-8') == content, f'Stale reference log: {name}'
        else:
            path.write_text(content,encoding='utf-8',newline='\n')
    print(json.dumps({'status':'ok','files':list(outputs),'check':args.check}))
