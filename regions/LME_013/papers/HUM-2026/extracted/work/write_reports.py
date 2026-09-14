from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).parents[3]
common="""## Conversion and round trip

The installed Ecopath scripts wrote the eight import files and initial database JSON. Their converter normalizes non-unit diet columns, fills unknown habitat with 1, omits P/Q and loses fleet splits on workbook reconstruction. The local preserve_database.py adapter reverses those transformations using the CSV files, carries stated P/Q in ge, and preserves metadata, TL, fleet data and all eight source tables in JSON extensions. The final workbook is rebuilt from the saved JSON, with exact cell comparisons recorded in ROUND_TRIP_AUDIT.md. Unmodified converter results are archived in extracted/work and are not the final model.

Unknown habitat stays -9999. Biomass retains the publication's density over the model domain for mass-balance arithmetic; this does not assert a habitat fraction of 1. Unknown BA, GS, Z, detritus import, migration and prices are not populated from software defaults. Sparse blank diet cells mean absent prey links; missing complete fields remain unknown. The checker may assume GS=0.2 internally for diagnostic calculations, but that assumption is not written into source files.

## Reproduction

Use the source JSON in this model directory with the installed write_outputs.py, run validate.py and massbalance_check.py, run database_json.py, then run extracted/work/preserve_database.py with this model directory as its argument. The adapter is mandatory to retain unnormalized source values. Installed skill files were not changed.
"""
p=root/'HUM-2026'/'extracted'/'13_1_Chilean_Patagonia_1980'
text="""# Chilean Patagonia (1980)

Source: Neira et al. (2026), Analysing ecosystem and demersal-stock dynamics in Chilean Patagonia system (41°28.6′S–57°S) from 1980 to 2020 using food web modelling. Progress in Oceanography 241, 103631. DOI 10.1016/j.pocean.2025.103631.
Model number: 13_1. LME: 13 Humboldt Current (archive assignment; actual model spans southern Patagonia). Extracted: 2026-09-04.
15 groups: 14 living and one detritus; 13 consumers. Three named fleets in the study; the published basic table gives only pooled landings, retained as one reporting column.

Status: partial reconstruction. All available basic parameters, diets and pooled landings were extracted. GS, detritus routing, detritus biomass, BA and fleet allocation are not numerically reported in the supplied material. Native EwE loading was not tested.

## Source bundle and eligibility

README.md and metadata.json were read first. Both claim no recovered source, but 1-s2.0-S0079661125002198-main.pdf exists and is a readable 15-page paper. SOURCE_INVENTORY.json records all article files and hashes. The paper has one 1980 mass-balanced Ecopath model. 1980–2020 time series and fitting hypotheses concern Ecosim and are not separate static parameterizations. Supplements S1–S7 are referenced but absent from this source bundle; no values were borrowed from them.

## Source tables

### Table 3, PDF/printed page 6
Header: Functional group | TL | B | P/B | Q/B | EE | P/Q | Y.
Mapping: name | tl | biomass | pb | qb | ee | pq | pooled landings.
B is tons/km²; rates are annual; Y is tons/km²/year. All 15 groups retained in source order. No biomass conversion: the approximate 290,000 km² area on page 4 is contextual.
The Q/B column is blank for phytoplankton and detritus. Table 3 bold values are Ecopath estimates: TL throughout, biomass groups 2–7, P/Q for consumers, and EE except the input 0.95 for groups 2–4 and 6–7. Retained exact printed digits.
Header mapping check: juvenile hoki P/B 1.20 / Q/B 6.24 = approximately 0.19, matching tabulated P/Q.
Extraction: pdfgrid word boxes, merge_gap=2, explicit group-name matches; page rendered at 220 dpi and inspected.

### Table 4, PDF/printed page 7
Prey rows 1–15 plus Import; predator columns 2–14. pdfgrid merge_gap=0.4, header anchor line4. Every label matched against Table3.
Consumer imports: Hoki adults0.270, Kingklip0.220, Skates0.820, Sea lions0.590. Other imports left blank as printed.
Sea lions diet sums1.002 although the printed total says1.000. The individual values, including Kingklip0.002, were visually checked and preserved.

## Biomass accumulation

Searched all 15 pages, methods equations on page4, Figures2/9/10 and the accumulation sweep. BA and migration are defined symbolically, but no static 1980 group BA value is given. Figure2 contains long-term biomass histories, not a declared Ecopath BA input; no slope was manufactured. Hoki stable age distribution is not a numerical BA statement. BA stays blank/-9999.

## Values from prose

Page4: model area approximately290,000 km²; year1980; three fleets (industrial trawl, artisanal vertical longline, artisanal bottom longline); hoki juvenile/adult definitions. Fleet catches are not apportioned by assumption.
Page3 Figure2 and page6 describe corrected landings accounting for discards/underreporting. This does not provide a numeric discard split, so Table3 Y was preserved as labeled.
No numeric assimilation efficiency or GS found in prose. Table2 supplies references/pedigree sources, not replacement numeric values.

## Conventions applied

None used to fill ecological inputs. No project 0.35/0.4 zooplankton GS defaults. The pooled reporting label is explicit because only total Y is available.

## Deliberate blanks

Habitat fractions, GS, BA, migration, other mortality, detritus routing/import/biomass, and unprinted catches/discards remain unknown. EwE may fill habitat1, GS0.2, BA0 and catch0 on import; these are software assumptions, not extracted source values. Primary producers/detritus have no Q/B or GS by definition.
Single detritus pool does not establish numeric routing or export fractions. No Taxonomy.xlsx is produced.

## Unresolved and flagged

Skates EE0.09 has no documented landings and no incoming predation in Table4; reconstructed EE from reported flows is0.000. Both cells checked visually. The suggested BA that would close this is not extracted.
Sea lions P/Q0.01 is printed and plausible for an endotherm; no adjustment.
The geography is broader than the archived LME label; the model is not a full Humboldt Current model.

## Validation

validate.py:0 errors,17 warnings (unknown GS, BA and 15 detritus fate rows).
Input mass balance:0 errors,2 warnings (Skates EE mismatch and low sea-lion P/Q).
All 13 diet sums within ±0.01; sea-lion1.002 retained. No numeric detritus-fate row is available.
Final source-preserving JSON check: INDETERMINATE. See below and ROUND_TRIP_AUDIT.md.
"""
(p/'REPORT.md').write_text(text+'\n'+common+'\n'+(p/'MASS_BALANCE.md').read_text(encoding='utf-8'),encoding='utf-8')
base="""# Northern Humboldt Current (1995–1998) — {variant}

Source: Chiaverano et al. (2018), Evaluating the role of large jellyfish and forage fishes as energy pathways, and their interplay with fisheries, in the Northern Humboldt Current System. Progress in Oceanography164:28–36. DOI10.1016/j.pocean.2018.04.009.
Model number: {number}. LME13 Humboldt Current. Extracted2026-09-04.
{counts}

Status: partial reconstruction with source inconsistencies. Numeric source fields were transcribed, including failed diet and mass-balance checks; native EwE loading was not tested.

## Source bundle and eligibility

README and metadata were read before extraction; their no-verified-file claims are stale. The bundle includes the nine-page article, Supplementary material revised and final.xls (12 visible worksheets), and Peru paper figures and tables II.docx (figures/table images and scenario-results Table2). footprint.geojson is spatial context.
Workbook Index and all 12 sheet contents were inventoried, including scenarios and pedigree. An installed Excel instance opened the XLS read-only, macros disabled, and saved a working XLSX under extracted/work; original files remain unchanged. Source table renderings were made from the working copy. SOURCE_INVENTORY.json records filenames/hashes.
The paper p30 states the reference inputs average1995–1998; metadata1995–2004 is not supported. This is one of two published model resolutions. Four ECOTRAN scenarios and uncertainty simulations are not separately specified Ecopath input models.

## Source tables

{tables}

## Biomass accumulation

All nine paper pages, workbook sheets (including production and scenario tables), and DOCX content searched for accumulation/migration. Paper p30 explicitly describes steady state and defines BA symbolically but reports no numeric group BA values. BA remains blank/-9999 rather than assumed0. Scenario production changes are not static baseline biomass accumulation.

## Values from prose

Paper p30 gives model area165,000 km² (4°S–16°S, to111 km offshore), input reference period1995–1998, a10% artisanal discard assumption, and a sardine catch adjustment from5.65 to1.4 t/km²/year.
Assimilation efficiency is explicitly tabulated as AE; GS is the exact complement1−AE. Thus AE0.65 givesGS0.35, AE0.80 givesGS0.20; these are source-derived, not defaults.
The source table's catch/discards take precedence over recalculation from generic rates; contradictions are recorded below.

## Conventions applied

No unstated ecological defaults. Names normalized only for whitespace/ligatures and explicit synonyms to match tables. Fisheries are fleet columns rather than biological groups. Anchovy/fish eggs are classified as the source's non-consuming detritus recipient pool, matching blank P/B/Q/B and the dedicated detritus-fate column; biological eggs are not given an invented turnover rate.
{numbering}

## Deliberate blanks

TL is not numerically tabulated in these parameter sources and remains blank. Habitat fractions, numeric BA/migration, Z, other mortality and external detritus imports are unreported. EwE may substitute habitat1, GS0.2, BA0 or catch0; those software assumptions were not copied into missing inputs.
Q/B/GS are structurally inapplicable to primary producers and four detritus pools. {fate_missing}

## Unresolved and flagged

- Large jellyfish/Chrysaora column totals1.04499999999999783 (about1.045), not1. No normalization. Both workbook diet tables retain the same defect.
- Gelatinous/small jellyfish biomass is about0.00907 in resolved TableA (display0.01), but the Chrysaora diet includes0.0492610837438424 on that group (TableB H9; aggregate TableF H9). That single flow is already far larger than its production. Verified against the formatted parameter and diet tables. No source-supported BA correction exists. The formal checker labels the gap INDETERMINATE because BA is unknown; it is a major failure to reproduce the paper's claimed steady-state balance.
- Paper p30 says sardine landings were reduced to1.4, but resolved TableA J14 stores5.6513425 and aggregated Table1 forage-fish landings28.13 remain consistent with the unreduced sardine plus anchovy catch. Published table values are retained; the stated revision is not silently applied across resolutions.
- TableA column label gives biomass t/km²/year, a dimensional labeling problem. Values are the model's standing biomass B per km² as defined in the methods; no time conversion applied.
- Workbook TableE misassigns fish-egg/offal/pelagic detritus aggregate codes relative to article Table1 and TableF. Matching uses names and the parameter/diet tables, not TableE code positions.
{extra_flags}

## Validation

{validation}
Final JSON uses preserved source diets. Formal balance verdict INDETERMINATE; this does not establish a runnable balanced model. See exact comparisons in ROUND_TRIP_AUDIT.md.
"""
variants=[
('13_2','fully resolved','39 Ecopath groups:35 living (2 producers,33 consumers) and4 detritus/egg pools;2 fleets.',
"""Table A-resolved parameters!A4:L44: columns Group/code, Functional group, B, P/B, Q/B, P/Q, AE, EE, Artisanal/Commercial landings, Artisanal/Commercial discards. Mapping to n/name/biomass/pb/qb/pq/(1−AE)/ee and two fleet tables. Rows6–44 supply groups1–39; rows45–46 are fleets40–41 and are not biological groups.
Stored numeric values are retained at the precision present in the machine-readable source. Cell display formats often round to2 decimals (even turning tiny turtle biomass/PQ into0.00); those display formats and bold-estimated flags are retained in SOURCE_CELLS.csv, avoiding replacement of nonzero stored values by rounded display zeros.
Table B-resolved diet!B3:AN43: group1–39 headers, rows4–42 prey, row43 Import. Consumers3–35 only are exported as diet columns; primary producer/detritus columns are structural zeros. Name matches verified individually.
Table C-resolved detritus fate!A3:G42:39 group routes to Anchovy eggs, Fishery offal, Pelagic detritus, Benthic detritus, Export; all row sums1. Fleet routes in rows43–44 are retained separately in FLEET_DETRITUS_FATE.json (all fishery discards to offal).
P/Q consistency check: microzooplankton256/1024=0.25. Original zero cells remain zero.""",
'Source group numbers1–39 retained; fleets40–41 separated without renumbering the biological groups.',
'Detritus fates are fully supplied by TableC.',
'- Nonzero turtle biomasses and endotherm P/Q are retained from underlying cells, despite display0.00. Prose discard rates are approximate and do not override the stored fleet-specific values.',
'validate.py:1 error (Chrysaora diet1.045),3 warnings (GS in6 non-consumers, unknown BA, missing TL). Detritus fate39/39 rows sum1. Known-flow EE for gelatinous zooplankton is about4409.97, versus printed0.95. Other major parameters reconcile much more closely.'),
('13_3','aggregated','24 Ecopath groups:20 living (2 producers,18 consumers) and4 detritus/egg pools;1 pooled fishery.',
"""Article Table1, PDF page4/printed31: Group code | Functional group | Biomass | p/b | q/b | p/q | ae | ee | Landings | Discards. Numerical columns identified by bounding-box x positions209.9,266.3,309.0,355.2,390.7,426.2,461.7,518.1. Names matched to source parameter rows, preserving all2-decimal values and zero cells.
Supplement Table F-aggregated diet (caption calls it TableG)!A3:Y28 supplies24 prey groups plus Import and matching predator headers. Names, not TableE codes, define the mapping. Sea turtle↔Sea turtles and Eggs↔Fish eggs are explicit synonyms. Consumer columns3–20 exported.
Supplement Table G-aggregate detritus fate (caption calls it TableH) is explicitly for ECOTRAN and separates feces, senescence and NH4 excretion into surface/sub-surface pools. It is not one Ecopath detritus-fate matrix; its complete cells remain in extracted/work, but are not merged by invented weights.
Header check: microzooplankton256/1024=0.25. Table1 and workbook diet were visually inspected.""",
'Article Table1 codes4–27 become importer numbers1–24, preserving exact source order. GROUP_NUMBER_MAP.csv and source_group_code record every mapping. Codes1–3 in the ECOTRAN production matrix are nutrients, not Ecopath groups; code28 is Fisheries.',
'Aggregated Ecopath detritus routing is not explicitly supplied; separate ECOTRAN surface/subsurface fates cannot be collapsed without an assumption, so all24 rows stay blank.',
'- Article Table1 Sea turtles biomass0.00 and seabird/marine mammal P/Q0.00 are printed rounding zeros; retained exactly. Do not interpret as biological absence or zero production. Apex-predator rounded values also produce a0.152 EE discrepancy. No high-precision aggregate basic table was supplied.',
'validate.py:1 error (large jellyfish diet1.045),27 warnings (GS in6 non-consumers, unknown BA,24 missing detritus routes,missing TL). Small-jellyfish known-flow EE is about4024.64.')]
for num,variant,counts,tables,numbering,fate_missing,extra_flags,validation in variants:
 p=root/'HUM-2018'/'extracted'/f'{num}_Northern_Humboldt_Current_1995-1998'
 report=base.format(variant=variant,number=num,counts=counts,tables=tables,numbering=numbering,fate_missing=fate_missing,extra_flags=extra_flags,validation=validation)
 (p/'REPORT.md').write_text(report+'\n'+common+'\n'+(p/'MASS_BALANCE.md').read_text(encoding='utf-8'),encoding='utf-8')
# Source inventory in each extraction directory; no output written into source root.
for aid in ['HUM-2026','HUM-2018']:
 folder=root/aid
 inventory=[]
 for f in folder.iterdir():
  if f.is_file():
   inventory.append({'file':f.name,'size_bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'role':'source material; retained unchanged'})
 (folder/'extracted'/'SOURCE_INVENTORY.json').write_text(json.dumps(inventory,indent=2,ensure_ascii=False),encoding='utf-8')
 (folder/'extracted'/'MASTER_INDEX.md').write_text('# Extraction index\n\n| Model number | Model | Year | Groups | Fleets | Status | Key issue |\n|---|---|---|---:|---:|---|---|\n'+(
 '|13_1|[Chilean Patagonia](13_1_Chilean_Patagonia_1980/REPORT.md)|1980|15|1 pooled|partial; INDETERMINATE|Skates EE mismatch; GS, BA, detritus routing and fleet splits unreported|\n' if aid=='HUM-2026' else
 '|13_2|[Northern Humboldt resolved](13_2_Northern_Humboldt_Current_1995-1998/REPORT.md)|1995–1998|39|2|partial; INDETERMINATE|Large-jellyfish diet1.045; gelatinous zooplankton production mismatch; conflicting sardine catch|\n|13_3|[Northern Humboldt aggregated](13_3_Northern_Humboldt_Current_1995-1998/REPORT.md)|1995–1998|24|1|partial; INDETERMINATE|Same jellyfish issues; rounded zero biomass; aggregated detritus routing missing|\n'),encoding='utf-8')
shutil.copy2(Path(__file__).parent/'preserve_database.py',root/'HUM-2018'/'extracted'/'work'/'preserve_database.py')
print('Reports and indexes written.')

