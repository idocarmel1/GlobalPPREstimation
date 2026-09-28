"""Archive verified papers and source-only extraction; never generate a runnable model."""
import csv
import hashlib
import json
import re
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(Path.home()/'.agents/skills/ecopath-extraction/scripts'))
from pdfgrid import get_words
from write_outputs import basic_input, write_csv
from openpyxl import Workbook

def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def workbook(path, headers, rows):
    w = Workbook(); s = w.active; s.append(headers)
    for row in rows: s.append(row)
    s.freeze_panes='A2'; s.auto_filter.ref=s.dimensions
    for col in s.columns:
        s.column_dimensions[col[0].column_letter].width=min(80, max(14, max(len(str(c.value or '')) for c in col)+2))
    w.save(path)

def material(source, dest, role, url, pages):
    shutil.copy2(source, dest)
    raw=dest.read_bytes()
    assert raw.startswith(b'%PDF-') and b'%%EOF' in raw[-4096:]
    return {'relative_path':dest.relative_to(ROOT).as_posix(), 'role':role,
            'sha256':hashlib.sha256(raw).hexdigest(), 'size_bytes':len(raw),
            'source_url':url, 'pages':pages, 'status':'downloaded_verified',
            'validation':'complete PDF parsed with Poppler; title and model identity checked'}

supp_url='https://www.researchgate.net/profile/Shane-Griffiths/publication/325700136_Griffiths_FOG-17-1431_Early_View_Supp_Info/data/5b9feef0299bf13e6038a3f9/Warm-Pool-Ecopath-FAD-Griffiths-et-al-2018-APPENDICES.pdf'
specs=[
    dict(key='Griffiths2019', paper_id='Griffiths-2019', model_id='941_201901_Warm_Pool_(2005)',
         title='Just a FAD? Ecosystem impacts of tuna purse-seine fishing associated with fish aggregating devices in the western Pacific Warm Pool Province',
         authors='Griffiths, S.P.; Allain, V.; Hoyle, S.D.; Lawson, T.A.; Nicol, S.J.',
         publication_year=2019, baseline=2005, functional_groups=46, living_groups=44,
         doi='10.1111/fog.12389', landing_page='https://doi.org/10.1111/fog.12389',
         url='https://www.bmis-bycatch.org/system/files/zotero_attachments/library_1/MQDAAXEY%20-%20Griffiths%20et%20al.%20-%202019%20-%20Just%20a%20FAD%20Ecosystem%20impacts%20of%20tuna%20purse-seine%20.pdf',
         pages=19, coverage={'HS_071':29.09639,'EEZ_941':99.71577},
         blockers=['Final balanced diet matrix (Appendix S1 Table S3, supplementary PDF pages 29–30) not coordinate-verifiable: direct publisher and author-upload downloads returned HTTP 403; flattened web text loses blank-cell positions.',
                   'Fleet landings/discards (Table S4, supplementary PDF page 31) not column-verifiable; header scaling 1e-6 t/km² must be preserved.',
                   'Unassimilated fractions, numerical detritus fate/discard routing and imports remain unverified. Qualitative discard pathway is not a numeric allocation.',
                   'Full functional-group membership in supplementary Table S1 remains to be verified.']),
    dict(key='Allain2021', paper_id='Allain-2021', model_id='941_202101_Western_Tropical_Pacific_(2013)',
         title='Tuna fisheries bycatch and climate change in the western tropical Pacific Ocean',
         authors='Allain, V.; Griffiths, S.; MacDonald, J.; Wabnitz, C.; Pilling, G.M.; Nicol, S.',
         publication_year=2021, baseline=2013, functional_groups=65, living_groups=63,
         doi=None, landing_page='https://meetings.wcpfc.int/node/12403',
         url='https://meetings.wcpfc.int/file/8826/download', pages=4,
         coverage={'HS_071':74.4854973493263,'EEZ_941':100.0},
         blockers=['The complete four-page SC17-EB-IP-11 leaflet contains model structure and results but no complete numbered 65-group list, B/PB/QB/EE table, diet matrix, catch ledger, biomass accumulation or routing inputs.',
                   'No supplementary/native model file is linked on the official publication page; primary-source searches and cited EcoSEA2020 report did not yield the final numerical model.',
                   'The 2021 model is a substantial 65-group/2013/domain update. Neither Griffiths2019 nor WCP2007 can be substituted.'])
]
proposal=[]
for spec in specs:
    paper=ROOT/'regions/EEZ_941/papers'/spec['paper_id']; paper.mkdir(parents=True, exist_ok=True)
    review=ROOT/'regions/EEZ_941/models'/spec['model_id']/'source_review'; review.mkdir(parents=True, exist_ok=True)
    materials=[material(BASE/spec['key']/(spec['key']+'_complete.pdf'),paper/'main.pdf','main',spec['url'],spec['pages'])]
    if spec['key']=='Allain2021':
        materials.append(material(BASE/'Allain2021/EcoSEA2020_context.pdf',paper/'EcoSEA2020_context.pdf','context_only','https://meetings.wcpfc.int/file/7748/download',24))
    for name in (['main_text.txt','page05.png','page06.png'] if spec['key']=='Griffiths2019' else ['source_text.txt','page02.png','page04.png']):
        shutil.copy2(BASE/spec['key']/name, review/name)
    meta={k:spec[k] for k in ['paper_id','model_id','title','authors','publication_year','doi','landing_page','functional_groups','living_groups']}
    meta.update(article_id=spec['paper_id']+'__EEZ_941',unit_id='EEZ_941',model_years=str(spec['baseline']),
        coverage_class='basin_proxy',target_coverage_ratio=spec['coverage']['EEZ_941']/100,
        geographic_applicability='Broad pelagic, mixed-jurisdiction proxy; target-region coverage does not establish representativeness of all regional fisheries.',
        geometry_method='WGS84 geodesic intersection of explicitly stated study rectangle with stored regional polygons; densified 0.05 degrees and checked at 0.01 degrees',
        main_file_status='downloaded_verified',download_status='downloaded_verified',model_file_status='not_found',
        supplement_status='identified_access_blocked' if spec['key']=='Griffiths2019' else 'not_linked_on_official_page',
        extraction_readiness='partial_source_extraction' if spec['key']=='Griffiths2019' else 'insufficient_numerical_inputs',
        full_model_loadable='Not tested: missing verified model inputs',diagnostic_status='NOT_RUN_MISSING_SOURCE_INPUTS',
        selected=False, material_files=materials, blockers=spec['blockers'],
        review_path=review.relative_to(ROOT).as_posix(), assessed_on='2026-09-28',
        later_selection_context='Review HS_071, EEZ_941 and EEZ_598 jointly later. EEZ_598 is also linked to WCP-2007 (Allain et al.2007). No EEZ_598 overlap was calculated here, no new extraction was requested, and no model choice is authorized.')
    dump(paper/'metadata.json',meta)
    dump(review/'ADMISSION_STATUS.json',{'status':'BLOCKED_MISSING_VERIFIED_INPUTS','blockers':spec['blockers'],
        'requested_methods':['GE','TE','With Egestion'],'global_excluded':True,
        'diagnostic_call':'PPRCalculator.diagnose_sppr(short=False, flat=False)',
        'diagnostic_results':None,'diagnostic_status':'NOT_RUN',
        'imports_status':'Complete eight-file bundle not generated; missing values were not replaced with zeros or defaults.',
        'canonical_json_status':'Not generated; no loadable model is claimed.',
        'reconstruction_validation_status':'Not runnable without verified diets, catches and routing.',
        'taxonomy_status':'Exact source group labels available for Griffiths2019; full membership unverified. No numbered Allain2021 membership list available.'})
    report='# Source admission and limitations\n\n'+spec['title']+'\n\n'
    report+='The main PDF is complete and its identity verified. This is a source review, not a runnable Ecopath model. No SPPR result is claimed.\n\n'
    report+='\n'.join('- '+b for b in spec['blockers'])+'\n\n'
    report+='All three requested diagnostics (GE, TE, With Egestion) are **not run**, not FAIL. No global diagnostic was run. No file posing as direct diagnostic output was created.\n\n'
    report+='Unknown inputs remain unknown. No diet normalization, pooling, migration repair, borrowed matrix, default unassimilated fraction or invented routing has been applied. The eight-file bundle, canonical database JSON and reconstruction validation await the listed source inputs.\n\n'
    if spec['key']=='Griffiths2019':
        report+='Table 1 (printed pp98–99; PDF pp5–6) supplies 46 exact labels and B/PB/QB/EE/PQ/TL. PDF page/cell coordinates and printed decimal precision are retained. Source dashes become null, not zero. B is t wet weight/km²; PB and QB are annual rates. EE and PQ are dimensionless despite the table’s year label. Bold values are Ecopath estimates, not direct field measurements.\n\n'
        report+='The web-readable author supplement distinguishes initial Table S2 from final balanced Table S3. Its page4 explicitly states net migration=0 and biomass accumulation=0. These prose facts are recorded separately from the locally archived parameter table. Catch Table S4 uses 1e-6 t/km². Main-paper ocean area is 11,543,000km², while some supplement derivations use 12,086,900km²; no published density was rescaled. Main p99 describes multistanza reconciliation and a distinct suspended fishery-discard pool but does not provide a numerical allocation.\n\n'
        report+='Supplement source: '+supp_url+'\n\n'
        report+='Recovery requirement: obtain the original AppendixS1-S4 DOCX/PDF or native model, inspect final Table S3 and Table S4 by coordinates, verify missing routing/GS/import inputs and membership, then finish imports, canonical JSON, reconstruction and the exact three diagnostic calls.\n'
    else:
        report+='PDF p4 explicitly states average annual 2013, 140E–150W/20N–20S, 65 groups and five fisheries. The pictured categories total 63 living groups plus detritus and fishery discards. The cited EcoSEA2020 report is context only: Section5/printed pp11–13 describes development, and its June2020 status is not a final balanced input set. Its stated 38,000,040km² differs from geodesic area of the 2021 stated rectangle; the discrepancy is retained, not forced to agree.\n\n'
        report+='Recovery requirement: obtain the final 65-group 2013 native model or full parameter, membership, diet, fleet catch, biomass accumulation, import and fate tables. The four-page leaflet cannot reconstruct them.\n'
    (review/'SOURCE_ADMISSION.md').write_text(report,encoding='utf-8')
    (paper/'README.md').write_text('# '+spec['title']+'\n\n'+spec['authors']+f" ({spec['publication_year']}).\n\n"+spec['landing_page']+'\n\nArchived under EEZ_941 because coverage of the target region is more complete than HS_071. It remains a broad pelagic proxy. This is paper registration, not model selection.\n\nSee metadata.json and the model source_review/SOURCE_ADMISSION.md for exact source limitations.\n',encoding='utf-8')
    proposal.append(meta)

# Coordinate extraction of all published Table 1 cells.
spec=specs[0]; review=ROOT/'regions/EEZ_941/models'/spec['model_id']/'source_review'
pdf=BASE/'Griffiths2019/Griffiths2019_complete.pdf'; groups=[]; evidence=[]
for page in (5,6):
    for line in get_words(str(pdf),page,backend='poppler'):
        cells=line.cells
        if not cells or not re.fullmatch(r'\d+',cells[0].text) or len(cells)<8: continue
        n=int(cells[0].text)
        if not (1<=n<=46) or (page==6 and n<45): continue
        name=' '.join(c.text for c in cells[1:-6]); marker=None
        if re.search(r' [TBD]$',name): name,marker=name[:-2],name[-1]
        if n==34: name+=' crustaceans'
        vals=[None if c.text=='–' else c.text for c in cells[-6:]]
        assert all(v is None or re.fullmatch(r'\d+\.\d+',v) for v in vals)
        g={'n':n,'name':name,**dict(zip(['tl','biomass','pb','qb','ee','pq'],vals)),
           'fishery_class_marker':marker,'taxon_descr':None,
           'group_type':'consumer' if n<=42 else 'producer' if n<=44 else 'detritus',
           'estimated_by_ecopath':[('biomass' if n in [23,24,25,26,28,29,30,31,32,33] else 'ee')]+(['pq'] if n<=42 else [])}
        groups.append(g)
        for field,c in zip(['tl','biomass','pb','qb','ee','pq'],cells[-6:]):
            evidence.append({'group':n,'name':name,'parameter':field,'printed_value':c.text,'pdf_page':page,'printed_page':page+93,'table':'Table 1','bbox':[c.x0,c.y0,c.x1,c.y1]})
assert [g['n'] for g in groups]==list(range(1,47))
partial={'artifact_type':'source_only_partial_extraction_NOT_CANONICAL','metadata':{'paper_id':spec['paper_id'],'baseline':2005,'model_groups':46},'groups':groups,
         'unverified_fields':['diet','landings','discards','unassim','detritus_fate','detritus_import','hab_area','taxon_descr'],
         'separate_prose_evidence':{'net_migration':0,'biomass_accumulation':0,'source_url':supp_url,'supplement_pdf_page':4,'verification':'web parsed prose; supplement bytes inaccessible'}}
dump(review/'SOURCE_ONLY_PARTIAL.json',partial); dump(review/'TABLE1_CELL_EVIDENCE.json',evidence)
write_csv(review/'Basic_input_PARTIAL.csv',basic_input(partial))
workbook(review/'TL_source.xlsx',['Seq','Group name','TL'],[[g['n'],g['name'],g['tl']] for g in groups])
workbook(review/'Taxonomy_unverified.xlsx',['Seq','Group name','taxon_descr'],[[g['n'],g['name'],None] for g in groups])
dump(review/'SOURCE_VALIDATION.json',{'group_count':46,'unique_contiguous_ids':True,'source_table_cells':len(evidence),'source_numeric_cells':sum(e['printed_value']!='–' for e in evidence),'null_source_dash_cells':sum(e['printed_value']=='–' for e in evidence),'visual_review':'Both local Table 1 page renders inspected; superscript T/B/D isolated from names and wrapped group 34 continued correctly. Bold estimate provenance retained.','precision':'Exact printed strings; no rounding or numeric repair.','partial_csv_rows':47,'model_validation':'NOT_RUN_MISSING_INPUTS'})
dump(BASE/'REGISTRATION_PROPOSAL.json',{'status':'ready_for_parent_central_metadata_integration_only','selected':False,'records':proposal,'workbook_writes_performed':False})
dump(BASE/'PROGRESS_STATUS.json',{'as_of':'2026-09-28','stage':'source_review_complete_with_documented_input_blockers','paper_archives_created':[s['paper_id'] for s in specs],'main_pdfs_verified':2,'full_extractions_completed':0,'diagnostics_run':0,'next_action':'Supply verified supplementary/native numerical inputs described in SOURCE_ADMISSION.md; parent integrates candidate metadata without selecting models.'})
print(json.dumps({'archived_papers':2,'table1_groups':len(groups),'source_cells':len(evidence),'full_models_generated':0,'diagnostics_run':0}))
