import pathlib,sys,json,re,hashlib,zipfile,xml.etree.ElementTree as E,subprocess,shutil
p=pathlib.Path(sys.argv[1]);w=p/'extracted/work';ex=p/'extracted';skill=pathlib.Path(r'C:\Users\idoca\.agents\skills\ecopath-extraction');meta=json.loads((p/'metadata.json').read_text(encoding='utf-8-sig'));prov=json.loads((w/'cell_provenance.json').read_text(encoding='utf-8'));conf=json.loads((w/'source_conflicts.json').read_text(encoding='utf-8'));tables=json.loads((w/'docx_tables.json').read_text(encoding='utf-8'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};root=E.fromstring(zipfile.ZipFile(p/'pone.0094742.s001-eb18ca66.docx').read('word/document.xml'));s8xml=root.findall('.//w:body/w:tbl',ns)[9];boldmap={}
for row in s8xml.findall('w:tr',ns):
 cells=row.findall('w:tc',ns);texts=[''.join(c.itertext()) for c in []]
 raw=[''.join(x.text or '' for x in c.findall('.//w:t',ns)) for c in cells]
 if raw and raw[0].strip().isdigit():boldmap[int(raw[0])]=[any(b.get('{'+ns['w']+'}val','true') not in ['false','0'] for b in c.findall('.//w:b',ns)) for c in cells]
for v in prov:
 if v.get('table')=='S8':v['category']='model-estimated' if boldmap[v['group']][v['column']-1] else 'tabulated'
(w/'cell_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2),encoding='utf-8')
inventory=[]
for f in p.iterdir():
 if not f.is_file():continue
 h=hashlib.sha256(f.read_bytes()).hexdigest();expected=next((m.get('sha256') for m in meta['material_files'] if m.get('local_filename')==f.name),None)
 inventory.append({'file':f.name,'bytes':f.stat().st_size,'sha256':h,'expected_sha256':expected,'matches_download_record':h==expected if expected else None})
(ex/'SOURCE_INVENTORY.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
assert all(x['matches_download_record'] is not False for x in inventory)
common='''## Eligibility and model identity
The source explicitly presents three balanced Ecopath parameterisations: Base, M30 and P30 (article pp. 2-5; Supplement Table S8). All represent 1991; 1991-2006 is the Ecosim fit interval. The catalog metadata value 2007-2009 is contradicted by the source and was not used. Habitat-loss, fictive-fleet, status-quo and 2056 endpoint simulations are dynamic scenarios, not separately parameterised static models. Supplement Table S9 2006 biomass/catch results are not another Ecopath snapshot.

## Source bundle and authority
README.md and metadata.json were read before extraction. The 16 top-level source files were inventoried. The 13 publication files match their recorded SHA-256 hashes (SOURCE_INVENTORY.json in the parent extraction directory).

- file-e30dfe50.pdf, 16 pages: article, static model Table 1 pp. 4-5, model scope/area pp. 2-3, scenarios p. 5, figures pp. 3 and 6-14.
- Table_1-f0424c0e.xls, one visible sheet Table_1 A1:N64, no hidden sheets/formulas: machine-readable version of article Table 1. Opened read-only in installed Excel, converted to an XLSX working copy in ../work; source never saved. HTML bold/italic tags were preserved separately and stripped from numeric text. The XLS and PDF table agree, including problematic zeros. This is the basic-input authority.
- Table_2-3434d627.xls, one visible sheet Table_2 A1:G6, no hidden sheets/formulas: aggregate food-web dependence percentages, not basic input.
- pone.0094742.s001-eb18ca66.docx: author supplement. Read document XML in source order, including all 11 physical tables, and rendered read-only using installed Word to ../work/supplement_rendered.pdf (21 pages). Text S1 pp. 1-6; Table S1 p. 7; Table S2 pp. 8-10; Table S3 and S4 p. 11; S5 p. 12; S6 p. 13; S7 p. 14; S8 pp. 15-16; S9 p. 17; Figure S1 p. 18. No supplementary numeric footnotes/endnotes outside the document body were found.
- Nine Figure_*.tif files were decoded and visually inventoried. Figure 1 gives area/map; Figures 2-3 depict dependence and trophic spectra; Figures 4-5 are 1991-2006 biomass/catch fits; Figure 6 compares trophic spectra; Figures 7-9 are simulated habitat/fishing outcomes. They do not supply a different static parameter set or a pre-1991 BA rate. No numbers were digitised from them.
- footprint.geojson supplies catalog geometry only; README and metadata are catalog context, not a substitute for published model parameters.

## Source tables
### Table 1 (article pp. 4-5; XLS Table_1 A1:N64)
Printed columns: number | Group name | TL | Biom (t/km2) | Z (/year | P/B/year | Q/B/year | EE | P/Q | BA | Artis. | Dem. | Pel. | Total.
Mapped to: n | name | tl | biomass | z | pb | qb | ee | pq | ba_rate | three catch fleets | sum check. BA units are resolved by Text S1 Fish (rendered p. 2), explicitly accumulation rates /year. Biomass and catches are already on the study-area density basis, so no 33,224 km2 division is applied. P/B and Q/B are annual rates.
51 groups, 47 consumers (1-47), 3 producers (48-50), 1 detritus pool (51). All eight import tables retain this group order; source diet row 52 is Import and is not a biological group. Figure and supplement abbreviations are mapped by published group number and name; the primary Table 1 names are retained exactly.
Columns were checked visually against both pages and arithmetically: Mackerel 0.45/3.0 = 0.150, Coastal M 0.58/2.9 = 0.200. Meagre P/B=0 conflicts with its nonzero Z and P/Q and remains as printed. Z is kept in its own field for multi-stanza groups; missing P/B is not silently replaced by Z. Source-stated producer/detritus zeros in Q/B/P/Q/P/B are retained even though ordinary import templates often leave them blank.
Bold values are Ecopath-estimated per Table 1 footnote; PROVENANCE.json records each basic parameter cell and the original markup. Italic biomass/QB cells for Croakers juv and Seabreams juv are retained and identified; the footnote only explicitly explains bold, so italics are not independently claimed to be measurements.

### Table S2 (DOCX physical tables 2-4; rendered pp. 8-10)
Prey rows 1-51 plus Import row 52; consumer blocks 1-15, 16-34, 35-47. Columns were matched to the explicit predator number and rows to the explicit prey number, then checked against the group names in the first block. OOXML preserves blank cells without coordinate guessing. PDF raw coordinates/visual renders support the audit; article Table 1 raw page coordinates are stored in ../work/page4_raw.txt. No layout-based plain-text table extraction was used.
The table entries are percentages: entire-food diets are 100 and most columns total approximately 100. Each stated numeric cell, including Import, is divided by exactly 100 using decimal arithmetic. No column is normalised; printed trailing precision is retained through decimal conversion. A source 00.10 is parsed numerically as 0.10 percent, not changed in magnitude. Blank cells remain blank.

### Table S8 (DOCX physical table 10; rendered pp. 15-16)
Headers distinguish imposed pBAi from balanced B/EE and from Ecosim vulnerability. B/EE columns are M30 6-7, Base 8-9, P30 10-11 (one-based physical cell columns). pBAi columns 3-5 are aggregate Banc-invertebrate diet shares, not new functional groups or a complete matrix. All 51 group rows are retained; unnumbered multi-stanza headings are skipped. S8 bold flags are captured in PROVENANCE.json. Vulnerability values are retained in SOURCE_DETAILS.json as contextual source data, not inserted into basic Ecopath inputs.

## Biomass accumulation
Table 1 column J states BA rates /year for groups 1-50. Nonzero rates: group 11 Coastal selacians, 23 Groupers ad, 24 Grouper juv and 27 Scianids each -0.05/year; group 30 Octopus vulgaris and 31 Cephalopods each -0.03/year. All other living groups have a printed zero. Detritus BA is blank. Negative signs and zeros were verified on article p. 4; Text S1 Fish p. 2 identifies these as rates estimated from trends before 1991, and balancing results p. 5 discuss their use. The absolute BA import column remains blank; database arithmetic may derive B times the rate and explicitly records that derivation.
The whole article and supplement, all tables/footnotes, and Figure 4 were searched. The 1991-2006 trajectories and Table S9 endpoints are Ecosim outputs; their slope is not substituted for the documented pre-1991 Ecopath BA. The 2056 equilibrium statement applies to forward simulations, not all 1991 groups. BA zero values here coincide with an EwE default because the paper actually states them.

## Values from prose
- Model year 1991, article p. 2; model area 33,224 km2 including Banc d'Arguin, article pp. 2-3. Area is documented but not inserted as habitat fraction.
- BA units and sign, Text S1 Fish p. 2, resolve the abbreviated column without changing numbers.
- Source catch data contain no information about discards (article p. 2; Text S1 Fishing data p. 3). The three reported catch series go into Landings as requested by the skill's total-catch rule; Discards remain unknown.
- Text S1 p. 1 discusses P/B=Z under equilibrium, while the table reports multi-stanza Z separately and nonzero BA in several groups. Consequently no universal replacement of P/B by Z is made.

## Conventions applied
No missing biological parameter was filled from EwE defaults or zooplankton conventions. Only exact percentage-to-proportion conversion was applied to S2 diet numbers. Fleet abbreviations Artis./Dem./Pel. are expanded to Artisanal/Industrial demersal/Industrial pelagic from source prose. Model names omit punctuation for portable directory naming; the actual citation preserves Banc d'Arguin.

## Deliberate blanks
After searching the whole bundle, GS/unassimilated consumption is unknown for every group, habitat-area proportion is unknown, detritus import/routing/export is not stated, and other mortality is not tabulated. The single detritus pool does not justify inventing a fate fraction of 1. EwE may default GS to 0.2, habitat to 1, catches/discards to 0 and unallocated detritus to export; these defaults are not source data and are not written into unknown extraction cells.
P/B is blank for groups 14-19 and 23-26 where Z is printed; the two Meagre P/B zeros are explicit, not blanks. Discards are entirely unknown. Detritus BA is unknown. Taxonomy.xlsx is outside scope. The database adapter records missing values as -9999 and retains stated zero separately.

## Unresolved and flagged
- Table S2 group 23 Groupers ad has prey 32 BA L crustaceans = 134 percent (rendered p. 9), an impossible single diet component. The resulting column sum is 220.06 percent (2.2006). The visual source unequivocally says 134; a plausible decimal correction to 13.4 is not authorised and is not made.
- Coastal birds column 2 sums to 98.0331 percent (0.980331), verified across every p. 8 row including Import 0.02 percent. No residual is invented.
- Meagre ad/juv P/B=0 while Z=0.21/0.3 and P/Q=0.100/0.017 (Table 1 p. 4). These source conflicts and multi-stanza structure limit mass-balance checks; the deliverables do not reconstruct stanza growth links.
- Table 1 BA phytoplankton B=5.9, EE=0.260 differs from S8 Base B=6, EE=0.40; recomputed EE using S2 is about 0.398. Table 1 remains the base authority. The arithmetic supports a source inconsistency, not permission to overwrite it.
- S8 differs from Table 1 mostly through rounding, including juvenile biomasses. SOURCE_DETAILS.json preserves every compared cell and all S8 rows. S9 gives initialization/output numbers with still different precision; these are retained context, not mixed into the static Table 1 input set.
- Text S1 balancing results say P/Q fixed at 0.2 for sardine/mackerel/horse mackerel, while Table 1 prints 0.150 for sardine/mackerel and 0.200 for horse mackerel. Structured Table 1 values are retained.
- Article p. 5 says M30 Banc share changes from 0.50 to 0.25; S8 gives 0.33 for those consumers. S8 parameter constraints are preserved and this prose discrepancy remains unresolved.
- Marine mammal P/Q=0.003 and bird P/Q=0.004 are genuinely printed; low homeotherm gross efficiency is not evidence of a column slip. Meagre juvenile P/Q=0.017 is also printed. Producer P/Q=0 is not a consumer physiology error.
'''
for variant,stem in [('Base','base'),('M30','m30'),('P30','p30')]:
 m=json.loads((w/(stem+'_input.json')).read_text(encoding='utf-8'));num=m['metadata']['model_number'];d=next(ex.glob(num+'_Banc*'));shutil.copyfile(w/(stem+'_input.json'),d/'model.json')
 pv=[x for x in prov if x['model']==variant or (variant!='Base' and x['model']=='Base' and x['field'] not in ['biomass','ee','tl'])];(d/'PROVENANCE.json').write_text(json.dumps(pv,ensure_ascii=False,indent=2),encoding='utf-8')
 details={'group_row_mapping':json.loads((w/'group_row_map.json').read_text(encoding='utf-8')),'table1_vs_s8_base':conf,'S8_source_rows':tables[9],'S9_source_rows':tables[10],'variant_constraints':m.get('extraction_notes'),'source_group_names':{str(g['n']):g['name'] for g in m['groups']}}
 (d/'SOURCE_DETAILS.json').write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding='utf-8')
 var='''\n## Variant scope\nBase Table 1 supplies all stated basic inputs, catch and trophic levels. The full published S2 diet matrix is preserved including the two invalid column totals. This extraction is therefore source-faithful but partial for operational loading because of missing GS/routing/habitat and unresolved publication inconsistencies.\n''' if variant=='Base' else f'''\n## Variant scope\n{variant} B and EE come from the corresponding S8 balanced columns for all 51 groups. P/B, Z, Q/B, P/Q, BA rates and fleet catches are retained as the common baseline parameters because the source describes variants in terms of benthic biomass and feeding location; they are explicitly marked inherited, not separately tabulated for this version. No post-1991 simulation rates are added. TL remains blank because variant-specific TL was not published.\n\nAffected consumers with changed Banc-invertebrate shares: {m['extraction_notes']['incomplete_diet_consumers']}. The source only constrains an aggregate share and the base matrix contains pairwise shares inconsistent with a single universal allocation. Each potentially changing pair among BA/shelf invertebrates (32/38, 33/39, 34/40, 35/41, 36/42, 37/43, 46/44, 47/45) is left unknown for those consumers; stated zero-zero pairs and remaining baseline components are retained and labelled inherited. No invented repartition or normalisation is performed. The precise S8 pBAi constraints are in model.json and SOURCE_DETAILS.json. This is a partial variant extraction, not a complete EwE import.\n\nS8 prints juvenile biomasses 0.00 for groups 15, 19 and 24. These printed zeros are retained; they are likely rounded positive values, but are not silently replaced by base biomass.\n'''
 head=f"# Banc d'Arguin and Mauritanian Shelf — {variant} (1991)\n\n**Source:** Guénette S, Meissa B, Gascuel D (2014), Assessing the Contribution of Marine Protected Areas to the Trophic Functioning of Ecosystems: A Model for the Banc d'Arguin and the Mauritanian Shelf. PLOS ONE 9(4): e94742. DOI: 10.1371/journal.pone.0094742.\n\n**LME:** 27 Canary Current. **Model number:** {num}. **Groups:** 51 (50 living; 1 detritus). **Fleets:** Artisanal, Industrial demersal, Industrial pelagic. **Extracted:** 2026-09-04. **Status:** partial; publication values retained with explicit gaps.\n\n"
 (d/'REPORT.md').write_text(head+common+var+'\n## Validation\nPending final saved logs.\n\n## Mass balance\nPending database conversion and source-preservation audit.\n',encoding='utf-8')
 for script,log in [('validate.py','VALIDATION.txt'),('massbalance_check.py','MASS_BALANCE_CHECK.txt')]:
  r=subprocess.run([sys.executable,'-X','utf8',str(skill/'scripts'/script),str(d)],capture_output=True,text=True,encoding='utf-8');(d/log).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8');print(variant,script,r.stdout.strip().splitlines()[-1])
 r=subprocess.run([sys.executable,'-X','utf8',str(skill/'scripts/database_json.py'),'-d',str(d),'--update-report'],capture_output=True,text=True,encoding='utf-8');(w/(stem+'_bundled_database_pipeline.txt')).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8');print(variant,'database exit',r.returncode)
 if r.returncode:print(r.stderr[-3000:])
