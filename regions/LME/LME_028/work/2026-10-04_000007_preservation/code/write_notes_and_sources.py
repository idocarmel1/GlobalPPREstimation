"""Document retained evidence and exact representation differences; no scientific edits."""
import csv,hashlib,json,os,re,sys,zipfile
from pathlib import Path
from collections import defaultdict
from xml.etree import ElementTree as E
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
QA=Path(__file__).parent.parent/'qa';BQ=ROOT/'regions/LME_028/work/2026-10-04_000002_reorganization/qa'
inventory=json.loads((BQ/'canonical_models.json').read_text('utf8'))
review=json.loads((ROOT/'regions/LME_028/work/2026-10-04_000001_reorganization_review/qa/review_lineage_dispositions.json').read_text('utf8'))
metadata={(r['unit_id'],r['model_id']):r for r in review['registered_model_mapping']}
moves=list(csv.DictReader((BQ/'file_moves.csv').open(encoding='utf8',newline='')))
bynew={r['retained_path']:r for r in moves if r['retained_path']};lookup={(r['unit_id'],r['model_id']):ROOT/r['directory']for r in inventory['destinations']}
roles=json.loads((ROOT/'common_reference_data/provenance/paper_file_roles.json').read_text('utf8')).get('files',[])
byrole={r['path']:r for r in roles}
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def link(home,p,label=None):
 rel=os.path.relpath(p,home).replace('\\','/')
 return '['+(label or p.name)+']('+rel.replace(' ','%20')+')'
def known_evidence(home):
 possible=['inputs/provenance.json','model_validation/validation.docx','model_validation/evidence/source_review/source_review.md','extracted_tables/REPORT.md','extracted_tables/evidence/REPORT.md','extracted_tables/evidence/source/REPORT.md','extracted_tables/evidence/SELECTED_REGIONAL_REPORT.md','extracted_tables/ROUNDTRIP_CHECK.json','extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json','extracted_tables/SOURCE_FIDELITY_CHECK.json','extracted_tables/thesis/converter_transformation_ledger.json','extracted_tables/evidence/TRANSFORMATION_LEDGER.json','extracted_tables/evidence/source_to_final_ledger.json','extracted_tables/evidence/runtime_provenance.json','results/result_manifest.json']
 return [home/p for p in possible if(home/p).is_file()]
def extraction_text(home):
 p=home/'model_validation/validation.docx'
 if not p.exists():return None
 with zipfile.ZipFile(p)as z:doc=E.fromstring(z.read('word/document.xml'))
 for tr in doc.iter('{'+W+'}tr'):
  cells=tr.findall('{'+W+'}tc');texts=[' '.join(t.text or ''for t in c.iter('{'+W+'}t'))for c in cells]
  if texts and 'model extraction' in texts[0].lower():return '\n'.join(texts[1:]).replace('Retained departures and evidence limits: model notes','').strip()
 return None
def groups(p):
 d=json.loads(p.read_text('utf8'));return {str(g['group_seq']):g for g in d['group']}
fields=['group_name','habitat_area','biomass','b_hab_area_input','pb','pb_input','qb','qb_input','ee','ee_input','biomass_accum','biomass_accum_rate','gs','pp','detritus_import','immigration','emigration','emigration_rate','other_mort','export','diet_imp']
def exact_diff(home,source,label):
 before=groups(source/'model.json');after=groups(home/'model.json');rows=[]
 for gid in sorted(set(before)&set(after),key=lambda x:int(x)):
  for field in fields:
   a=before[gid].get(field);b=after[gid].get(field)
   if a!=b:rows.append({'group_seq':gid,'group_name':after[gid].get('group_name'),'field':field,'source':a,'retained':b})
 aggregate=defaultdict(list)
 for row in rows:aggregate[(row['field'],str(row['source']),str(row['retained']))].append(row['group_seq'])
 text='\nThe following exact input differences compare this JSON with '+link(home,source/'model.json',label)+'. The source representation is an evidence locator; it is not proof that every source field is a published measurement. `-9999` remains an unknown sentinel, and absent fields are shown as `None`. No difference was introduced by this reorganization.\n\n| Group IDs | Field | Source representation | Retained representation |\n|---|---|---|---|\n'
 for (field,a,b),ids in aggregate.items():text+='| '+', '.join(ids)+' | `'+field+'` | `'+a.replace('|','\\|')+'` | `'+b.replace('|','\\|')+'` |\n'
 if not rows:text+='| All shared groups | listed scalar inputs | identical | identical |\n'
 if set(before)!=set(after):text+='\nGroup IDs present only in the source: '+', '.join(sorted(set(before)-set(after)))+'; only in this representation: '+', '.join(sorted(set(after)-set(before)))+'.\n'
 return text,rows
special={
 'CAL-2016_California_Current_2000-2014':'''This is the accepted author-equation computational variant, rather than the publication-input reconstruction. The source Appendix B and parameter files leave 26 biomasses and 67 EEs unresolved. The retained author-equation solution completes the 26 B values and living EEs; these are solved values, not new observed measurements. The source variant remains a distinct canonical model under `__source`. The retained extraction REPORT records a maximum production-equation residual of 2.84e-14 and author detritus accounting excluding egestion; reorganization did not rerun that solution.

GS is not parameterized in the source. The recorded diagnostic loader supplies GS=0.2 for consumers, extends sole-detritus routing to egestion, sets detritus EE to 1, completes detritus inflow and appends a diet-import helper. Those are runtime conventions, not recovered source GS/EE/import measurements. Total Yield includes bycatch/discards (article PDF p.2, Eq.1); separate discard return remains unknown. Source diets were not normalized. The retained diagnostics are WARN and production eligibility remains false. Historical source_review text calling the former canonical source-only describes the earlier two-file arrangement; the identities are now two separate canonical models.''',
 'CAL-2016_California_Current_2000-2014__source':'''This is the publication-input reconstruction, retaining 26 unknown biomasses, 67 unknown EEs and unknown GS/TL where unreported. Source `-1` denotes a parameter to be solved, represented as the supported unknown sentinel rather than a negative observation. Author total Yield includes bycatch/discards; the Landings.csv column is a format carrier and does not establish a separate landings/discards split. Habitat area 1 is an export convention for whole-model biomass, not a measured habitat fraction. Source diets are not normalized. Appendix B, the author parameter files and the retained REPORT provide locators. The distinct accepted author-equation solution is the sibling model; its completed B/EE must not be attributed to this input reconstruction.''',
 'Chiaverano2018_detailed_Northern_Humboldt_1995_1998':'''The native detailed supplement has 41 nodes: 39 stock/pool nodes plus two fleet nodes. This computational representation retains the 39 stocks and native biological values/diets, while recording habitat area=1, BA=0, migration=0 and external-detritus-import=0 as execution conventions. Source habitat fractions, numerical BA/migration/import remain unreported. Eggs group36 is operationally a nonfeeding pool (`pp=2`), because its source rates are blank; the prose 25% egg-production statement is not an annual P/B input. Fleet landings/discards and export fates remain in companions because stock JSON cannot encode complete fleet ancestry.

Native Table A J14 supplies Sardine landings=5.6513425, whereas article PDF p.3/printed p.30 says 1.4 after balancing. The supplement branch is retained without a catch repair. Table B H4/H7/H8/H9/H39 sums to 1.045 for large jellyfish; this is an unresolved 4.5% excess. Small-gelatinous Table A C11/D11/E11/H11 values are B=0.009068332612514496, PB=0.5839999914169312, QB=2.919999837875366 and EE=0.949999988079071. Predation implies EE about4409.97 under the retained arithmetic convention; no biomass magnitude correction was made.

The diagnostic loader separately normalizes 161 diet cells and replaces eight native pool-fate cells with identity routing. These are diagnostic transformations, not canonical source corrections. All direct methods remain FAIL; native missingness and source conflicts do not become scientific approval.''',
 'Chiaverano2018_detailed_Northern_Humboldt_1995_1998__source':'''The native detailed Table A/B/C representation retains native precision and missingness, with 39 stock/pool nodes and fisheries evidence in companions. Eggs36 is an operational nonfeeding pool; the source prose 25% egg statement is not an annual rate. GS for the33 feeding consumers is the exact complement1−AE, not a default0.2. Unreported BA, migration, habitat and detritus import remain unknown. Native Table A J14 Sardine landings=5.6513425 conflicts with the printed 1.4 statement. Table B large-jellyfish diet totals1.045 and small-gelatinous production is insufficient; neither was repaired. The accepted computational conventions are in the sibling model. Reconstructing the source cells does not establish ecological balance.''',
 '52_GM2019_Fig9_Pelagic_balanced_(2000-2014)':'''This is the explicitly authorized scientific assumption model, not an author-confirmed Ecopath export. Native stocks/flows use tC/km² and annual rates. Table3 implies area1,544,000km²; this is not a measured regional-overlap fraction. The retained production totals and source wet stocks/carbon factors determine B/PB. Microbial stock splitting gives6.81million tC and65.067million wet tonnes versus rounded source6.8million tC/64million wet tonnes; protozoa's carbon factor10 is an explicit estimate.

Twelve Figure9 arrows use low-confidence10×/100× decimal hypotheses. These have not been established as publication errors. Accepted F62=0.023, F67=0.05 and F77's medium-pollock origin remain unchanged. The food ledger retains74 components, including hyperiid residual assumptions40% chaetognaths/50% absent larvae and tunicates/10% gelatinous, squid unresolved food splitting, imported prey, jellyfish2006–2014 versus overall2000–2014 periods, and salmon's0.14kt rounded-total discrepancy.

Living BA is zero by assumption. GS is unknown for20 consumers and solved by the standard LIM, not supplied as0.2. Detritus import/export are zero, all living mortality/egestion routes to the sole pool, and its assumed inventory15.5million tC represents18.25days turnover. The retained diagnostic detritus BA=242.50886238380988tC/km²/year is an imposed nonsteady residual, not measured burial or a stock trend. A native import helperB=1 is nonbiological. All direct methods remain WARN. Runtime settings and source-to-final ledger record the accepted decisions; reorganization introduces none.''',
 '52_GM2019_Fig9_Pelagic_(2000-2014)':'''This is the Figure9 source reconstruction, retained separately from the authorized balanced assumption model. Source arrow readings, endpoint ambiguity, food composition and stock/conversion limitations remain as documented. The sibling balanced variant applies twelve decimal-reduction hypotheses and additional food/accounting choices; those are not source corrections to this representation. Unknown source GS, missing food components and unpublished equations remain unknown where recorded. Figure9 alone cannot establish a uniquely balanced Ecopath model or a measured regional overlap.''',
 'Guenette2014_BancArguin_Base_1991':'''Published Table1 and supplementS2/S8 are the source authorities. P/B is explicitly zero for juvenile/adult groups3/4 and unreported for14–19,23–26; P/B=Z or QB×PQ has not been adopted as a native stanza solution. Absolute BA remains unknown;50/51 source BA rates are retained, including negative trends. GS, habitat fractions, discard information, routing, migration and detritus import are unreported.

SupplementS2 physical tables2–4 supply diets. Published blank cells predator/prey14/36,15/36,2/39,15/39 remain blank/-9999. Coastal birds' literal sum0.980331 has an unexplained0.019669 deficit. Adult groupers' Banc large-crustacean entry is134%=1.34 and column sum2.2006; the older0.1347275 correction has no established researcher decision and was not adopted. Table1 Banc-phytoplankton EE0.260 conflicts with S8 Base0.40; Table1 is retained. Reported P/Q0.150 for mackerel/sardine conflicts with prose0.2. This source model remains NOT_RUN. The approximation and EcoBase689 deposit are distinct variants, not replacement evidence.''',
 'Guenette2014_BancArguin_M30_1991':'''M30 uses its publishedS8 B/EE variant, preserving native publication identity. In addition to Base's missing stanza production and unresolved published diet defects,114 prey cells across14 consumers are unpublished; they remain unknown, not Base substitutes or zero. S2 literal134%=1.34 adult-grouper feeding and the0.980331 coastal-bird sum remain unresolved. GS, routing, migration, separate discard inputs and absolute BA are not invented. This incomplete published variant remains NOT_RUN, separately from the Base/P30/EcoBase deposit and the Base approximation experiment.''',
 'Guenette2014_BancArguin_P30_1991':'''P30 uses its publishedS8 B/EE variant, preserving native publication identity. In addition to Base's missing stanza production and unresolved published diet defects,114 prey cells across14 consumers are unpublished; they remain unknown, not Base substitutes or zero. S2 literal134%=1.34 adult-grouper feeding and the0.980331 coastal-bird sum remain unresolved. GS, routing, migration, separate discard inputs and absolute BA are not invented. This incomplete published variant remains NOT_RUN, separately from the Base/M30/EcoBase deposit and the Base approximation experiment.''',
 'Guenette2014_BancArguin_Base_1991__approximation':'''This is an existing explicit runtime experiment retained as a distinct scientific variant. The published Base source remains a separate NOT_RUN model. The experiment uses its recorded P/Q production approximation and other execution conventions; this is not a recovered multistanza solution or an authorized correction of source values. The exact scalar differences below identify the retained input choices. All direct GE/TE/With Egestion results are FAIL. The historical experiment path and hash are recorded in inputs/provenance.json and the source-disposition ledger. Exact human authorization beyond the retained experiment record remains unknown; no new approval is inferred.''',
 'EcoBase689_native_1991':'''The recovered EcoBase689 native deposit differs in diets, precision, fleet/stanza and biological fields from published Base/M30/P30. It is a separate native scientific variant. Its fields cannot silently replace missing or defective publication cells. All retained direct methods are FAIL. No numerical repair, ecological admission or new human approval is made during reorganization.''',
 '27_Morissette2009_Northwest_Africa_Table17':'''This is the paper-onlyTable17 source representation, scientifically distinct from the selected EcoBase118 native representation in the same lineage. Printed missingness and catch differences are preserved. Native companion groups match the selected native objects, but that does not turn paper missingness into observed native values. The final2009 publication is unavailable where the retained preliminary2008 source is context; no citation/version equivalence is invented. This source reconstruction remains NOT_RUN.''',
 '27_Villanueva2004_SineSaloum':'''The37-group thesisTable6.5 (PDFp.138/printedp.114) and AnnexII.A (PDFpp.235–236/printedpp.211–212) are retained. Group20 is Epinephelus aeneus* inTable6.5 but Hemichromis fasciatus inAnnexII.A;70 canonical diet cells covering preyrow20/consumercolumn20 are withheld, while original numbered annex evidence is retained. No positional identity guess is made. Group27's Mugilidés pooling is supported separately. Source consumer sums are0.999 for2/5/10 and1.000 for the other31; the conflicting percent caption was not used to rescale fractions.

BA, GS, habitat fractions, migration, routing, detritus imports, separate discards and selected catches remain unknown. Y is unknown for12/31–37; group22 Y=0.000 is known. The source detritusPB=1.700 remains evidence, not a biological detritus-production claim. PublishedY is carried in a Reported total catch column without asserting separate discards zero.

Reorganization promotes the pre-existing supported37-group Ecopath converter output (SHA2564ac551c7a5b6c601b401d92912ab5595c4776a076e172302a092232928cae90b) without changing any parameter. Retained fidelity verification records23,172 equal cells/missing masks and maximum difference0. This proves preservation of partial source evidence, not construction readiness; group20 and missing GS/BA/routing still block construction and all scientific/direct diagnostics remain NOT_RUN.''',
 '38_38003_Java_Sea_normalized_BA_completed_(mid1970s)':'''The latest retained canonical hash isdae4aa0106a4c47d7db6fa9764791e656d1ba75ae0e1756e6d20ec202180c9ba. The October2 source audit restores six formerly normalized diet cells to printed values. Printed Macrozoobenthos totals0.660, leaving0.340 unexplained despite the unit-sum caption. No omitted prey/import or corrected source value is established, and no diet deficit is repaired. Twenty-eight previous BA completions remain computational, not measured stock changes.

The former canonical hashdb0bc803ea5a068e346b82df8d8b4e4b13f8351bf61103c6507997cb6996ae35 is explicitly superseded and its JSON removed under the agreed latest-only rule. Historical diagnostics/results and review statements retain that identity. Before/after loader equality had been proved in historical runtime-equivalence evidence; the certificate requires the now-removed old bytes and therefore cannot prove current compatibility after cleanup. Active numerical coefficients/annual outputs/model ratios are pending, with full historical regional snapshot preserved. No current numerical/scientific/researcher freshness is claimed. Only six source diet cells were directly re-extracted by that audit; whole-matrix primary fidelity remains unverified.''',
}
pairs={
 'CAL-2016_California_Current_2000-2014':'CAL-2016_California_Current_2000-2014__source',
 'Chiaverano2018_detailed_Northern_Humboldt_1995_1998':'Chiaverano2018_detailed_Northern_Humboldt_1995_1998__source',
 '52_GM2019_Fig9_Pelagic_balanced_(2000-2014)':'52_GM2019_Fig9_Pelagic_(2000-2014)',
 'Guenette2014_BancArguin_Base_1991__approximation':'Guenette2014_BancArguin_Base_1991',
 'PAT2024_FalklandShelf_2020_native':'PAT2024_FalklandShelf_2020_native__source',
}
changes=[];difference_records=[]
for item in inventory['destinations']:
 unit,mid=item['unit_id'],item['model_id'];home=ROOT/item['directory'];oldnote=(home/'model_notes.md').read_text('utf8')if(home/'model_notes.md').exists()else ''
 meta=metadata.get((unit,mid),{});central=meta.get('central_row',{})
 source_id=meta.get('paper_ids')or next((r.get('paper_id')or r.get('proposed_paper_id') for k in ['unregistered_existing_model_mapping','distinct_source_computational_variants']for r in review[k]if r.get('model_id',r.get('proposed_distinct_model_id'))==mid and r['unit_id']==unit),None)
 if not source_id and '/papers/'in item['directory']:source_id=item['directory'].split('/papers/',1)[1].split('/')[0]+' (existing folder identity; publication metadata is not newly verified)'
 if not source_id:source_id='Existing JSON-only EcoBase candidate; exact bibliographic association is unknown unless stated in the retained native/source metadata.'
 period=meta.get('model_year')or central.get('model_years')or 'Not established by the retained registry metadata; model-name period is descriptive, not new provenance.'
 area=central.get('coverage_note')or 'No additional area or coverage value is inferred during relocation. Consult retained source/evidence; unknown coverage remains unknown.'
 departures=special.get(mid)
 extract=extraction_text(home)
 if departures is None:
  availability=meta.get('availability')or central.get('availability')
  prior_section=oldnote.split('## Departures from the publication',1)[-1].split('## Evidence links',1)[0].strip()if '## Departures from the publication'in oldnote else ''
  departures='Departures have not been independently re-extracted during this administrative task. No additional parameter correction is made. '+(availability+'\n\n'if availability else '')
  if prior_section:departures+='Existing departure summary retained: '+prior_section.split('\n\nNo additional parameter changes',1)[0]+'\n\n'
  if extract:departures+='The current validation document\'s Model extraction row records:\n\n> '+extract.replace('\n','\n> ')+'\n\n'
  departures+='Exact publication cells, values or decision provenance absent from retained evidence remain unknown. JSON loadability and an automated fidelity check do not by themselves establish source fidelity or scientific approval.'
 if mid in pairs:
  source=lookup.get((unit,pairs[mid]))
  if source:
   diff,rows_=exact_diff(home,source,'retained source variant');departures+=diff
   difference_records.append({'unit_id':unit,'model_id':mid,'source_model_id':pairs[mid],'differences':rows_})
 evidence=known_evidence(home)
 text='# '+mid+'\n\n## Source identity\n\n'+source_id+'\n\nRegional application: `'+unit+'`. Canonical JSON SHA-256: `'+sha(home/'model.json')+'`. The byte-preservation check compares this retained representation with the pre-relocation working state; it is not a fresh extraction or a new approval.\n\n## Modeled period and area\n\nPeriod: '+str(period)+'\n\n'+str(area)+'\n\n## Departures from the publication\n\n'+departures+'\n\n## Evidence links\n\n- '+link(home,home/'model.json','Canonical Ecopath representation')+'\n'
 text+=''.join('- '+link(home,p)+'\n'for p in evidence)
 text+='- '+link(home,ROOT/'common_reference_data/provenance/source_paths.csv','Portable source dispositions')+'\n\n## Removed extraction evidence\n\nSuperseded extraction packages and their unique old evidence are removed under the agreed latest-only policy; they are not merged into this package. Original paths, hashes and reasons are metadata in the linked disposition ledger. A link to this paragraph records an unavailable former payload, not replacement evidence or completed scientific verification.\n'
 (home/'model_notes.md').write_text(text,encoding='utf8');changes.append({'unit_id':unit,'model_id':mid,'notes_sha256':sha(home/'model_notes.md'),'evidence_links':len(evidence),'specialized_departure_record':mid in special,'validation_extraction_row_used':bool(extract)})
papers=set((ROOT/r['directory']).parents[1] for r in inventory['destinations'] if '/papers/'in r['directory'])
# Also cover source-only paper folders without manufacturing a model or citation.
papers.update((ROOT/r['retained_path']).parents[len((ROOT/r['retained_path']).parts)-(len(ROOT.parts)+6)] if False else ROOT/Path(r['retained_path']).parts[0]/Path(r['retained_path']).parts[1]/Path(r['retained_path']).parts[2]/'papers'/Path(r['retained_path']).parts[4] for r in moves if r['retained_path'].startswith('regions/') and '/papers/'in r['retained_path'] and '/sources/'in r['retained_path'])
manifests=[]
for paper in sorted(papers):
 sources=paper/'sources';entries=[]
 for p in sorted(sources.rglob('*'))if sources.exists()else []:
  if not p.is_file()or p.name=='source_manifest.json':continue
  rel=p.relative_to(ROOT).as_posix();move=bynew.get(rel);old=move['original_path']if move else None;role=byrole.get(old)or byrole.get(rel);head=p.read_bytes()[:128]if p.stat().st_size<1000000 else p.open('rb').read(128);pointer=head.startswith(b'version https://git-lfs.github.com/spec/v1')
  inferred='context'if 'context'in p.relative_to(sources).parts else ('supplement'if 'supplements'in p.relative_to(sources).parts else 'retained source file; exact publication role not newly assessed')
  entries.append({'path':p.relative_to(paper).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'verification':'lfs_pointer_only'if pointer else 'full_bytes','role':role['role']if role else inferred,'role_evidence':role.get('evidence')if role else 'Existing source placement and relocation record; no additional bibliographic inference.','original_path':old,'baseline_sha256':move['sha256']if move else None,'baseline_bytes_preserved':sha(p)==move['sha256']if move and move['sha256']else None})
 obj={'schema_version':1,'paper_folder_id':paper.name,'identity_status':'Existing folder/registry association. No new citation, coverage or publication-version equivalence is invented.','administrative_only':True,'models':[p.name for p in sorted((paper/'models').glob('*'))if(p/'model.json').is_file()],'files':entries,'limitations':['A source hash authenticates present bytes, not authorship or scientific validity. LFS pointers are not complete source-byte verification.','Current validation/source-review records retain any publication-version or retrieval limits.']}
 (paper/'source_manifest.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8');manifests.append({'path':(paper/'source_manifest.json').relative_to(ROOT).as_posix(),'source_files':len(entries),'lfs_pointer_only':sum(e['verification']=='lfs_pointer_only'for e in entries)})
(QA/'model_notes_and_sources.json').write_text(json.dumps({'notes':changes,'paper_manifests':manifests,'representation_difference_records':difference_records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Documented',len(changes),'models and',len(manifests),'paper source manifests; scientific JSONs untouched.')
