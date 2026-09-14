from pathlib import Path
import json,hashlib,shutil,csv,re
from decimal import Decimal as D
w=Path(r'C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/קוד/PPR_Ecopath_Atlas/archive/regions/LME_036/SCS-2007/extracted/work');out=w.parent;article=out.parent
prov=json.loads((w/'cell_provenance.json').read_text(encoding='utf-8'))
catch=json.loads((w/'catch_source_totals.json').read_text(encoding='utf-8'))
conflicts='''| Parameter | Summary table retained | Appendix or other statement | Source location (printed / PDF) |
|---|---|---|---|
| Phytoplankton P/B, 2000s | 398 | 399; both periods said to be identical | 322 / 337 |
| Benthic producer P/B | 11.89 | 11.9 | 323 / 338 |
| Benthic producer catch, 2000s | fleet sum 0.0056 | 0.045 | 323 / 338 |
| Jellyfish, 2000s B and EE | 1.53 and 0.520 | B estimated with EE 0.95 | 324 / 339 |
| Non-cephalopod molluscs, 2000s P/B and Q/B | 3.50 and 11.7 | 3 and 7; described as similar across periods | 324-325 / 339-340 |
| Crabs P/B, 2000s | 3.00 | increased to 4 | 326 / 341 |
| Cephalopods EE, 1970s | 0.500 | assumed 0.95 | 326 / 341 |
| Threadfin bream catch, 1970s | 0.0440 | 0.062 used in mortality estimation | 327 / 342 |
| Threadfin bream Q/B | 8.10 and 15.4 | described as stationary between years | 327 / 342 |
| Bigeyes catch, 1970s | 0.0350 | 0.025 used in mortality estimation | 328 / 343 |
| Lizard fish B and P/B, 1970s | 0.30 and 2.30 | 0.149 and 0.79, later adjusted to 0.85 | 328-329 / 343-344 |
| Lizard fish catch, 2000s | fleet sum 0.0234 | 0.086 | 329 / 344 |
| Adult hairtail P/B, 1970s | 1.50 | 1.08 | 330 / 345 |
| Pomfret B, 1970s | 0.065 | 1.03 | 331 / 346 |
| Pomfret catch, 2000s | 0.2390 | 0.230 | 331 / 346 |
| Snappers P/B, 1970s | 1.34 | 1.24 | 331 / 346 |
| Adult groupers P/B, 1970s | 0.85 | 1.24 | 332 / 347 |
| Adult groupers catch, 2000s | 0.0089 | 0.089 | 332 / 347 |
| Small croakers catch, 1970s | 0.0160 | 0.0197 | 334 / 349 |
| Juvenile large croakers B and Q/B, 2000s | 0.04 and 16.366 | 0.072 and 16.47 | 335 / 350 |
| Juvenile large croakers B and Q/B, 1970s | 0.0425 and 15.65 | 0.051 and 15.48 | 335 / 350 |
| Adult large demersal fish B, 2000s | 0.021 | 0.015 | 336 / 351 |
| Adult large demersal fish P/B, 1970s | 1.44 | 1.54 | 336 / 351 |
| Juvenile demersal fish P/B, 1970s | 2.60 | said to equal small demersal fish (2.7) | 336-337 / 351-352 |
| Benthopelagic fish P/B, 1970s | 3.00 | small benthopelagic 2.31 | 337 / 352 |
| Benthopelagic catches, 1970s and 2000s | 0.0303 and 0.6025 | small benthopelagic 0.0023 and 0.643 | 337 / 352 |
| Large benthopelagic group | no separate group in final 38-row table | separate parameterization discussed | 337-338 / 352-353 |
| Adult large pelagic P/B, 2000s | 1.40 | 1.31 | 339 / 354 |
| Juvenile large pelagic B and Q/B, 2000s | 0.289 and 16.12 | 0.242 and 16.08 | 339 / 354 |
| Demersal sharks B, 1970s | 0.04 | 0.015 | 340 / 355 |
| Demersal sharks P/B, 2000s | 1.20 | 2.2 | 340 / 355 |
| Marine turtle catch, 1970s | 0.0001 | Table 6.5 F=0.05 and B=0.0002 imply catch 0.00001 (diagnostic only) | 179 and 190 / 194 and 205 |
| Total catch, 2000s | fleet-cell sum 7.7375; printed total 7.736 | prose 7.35 | 190 / 205 |
'''
(out/'SOURCE_CONFLICTS.md').write_text('# Source conflicts\n\nFinal Tables 6.1, 6.2 and 6.5 are transcribed as printed. The following alternatives are retained as evidence, not used as replacements. Some differences may reflect earlier parameterizations; the thesis does not resolve all of them. Rates are annual and biomass/catch densities are on the model-area basis.\n\n'+conflicts,encoding='utf-8')
inventory=[]
for p in article.iterdir():
 if p.is_file(): inventory.append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'role':'published thesis' if p.suffix=='.pdf' else 'archive reference metadata'})
assert [i['sha256'] for i in inventory if i['file'].endswith('.pdf')][0]=='87ea9ea00b6b71b896f89c0364bba09071f1683a71f5a66c71ea4da6bdbe3468'
(out/'SOURCE_INVENTORY.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
layouts=json.loads((w/'table_layouts.json').read_text())
for year in ['1970s','2000s']:
 m=json.loads((w/f'model-{year}.json').read_text(encoding='utf-8'));d=out/f'SCS-2007_Northern_South_China_Sea_{year}'
 shutil.copyfile(w/f'model-{year}.json',d/'model.json')
 (d/'PROVENANCE.json').write_text(json.dumps([p for p in prov if p['period'] in [year,'both']],indent=2,ensure_ascii=False),encoding='utf-8')
 (d/'SOURCE_CATCH_TOTALS.json').write_text(json.dumps(catch,indent=2,ensure_ascii=False),encoding='utf-8')
 (d/'SOURCE_MORTALITIES.json').write_text(json.dumps([x for x in json.loads((w/'mortality_source.json').read_text()) if x['period']==year],indent=2),encoding='utf-8')
 sums={n:sum(D(v) for v in diet.values()) for n,diet in m['diet'].items()}
 estimates=[p for p in prov if p['period']==year and p['category']=='model-estimated']
 estimated='\n'.join(f"| {p['group']} | {m['groups'][p['group']-1]['name']} | {p['field']} | {p['printed']} |" for p in estimates)
 proserows='\n'.join(f"- Group {p['group']} ({m['groups'][p['group']-1]['name']}): {p['field']} = {p['value']}; PDF p. {p['pdf_page']} (printed p. {p['pdf_page']-15}). {p['category']}." for p in prov if p['period']==year and p['field'] in ['z','pq'])
 layoutrows='\n'.join(f"| {l['pdf_page']-15} / {l['pdf_page']} | {', '.join(map(str,l['predators']))} | {l['body_lines']} | {', '.join(f'{x:.2f}' for x in l['numeric_right_anchors'])} |" for l in layouts)
 drift='\n'.join(f"| {n} | {m['groups'][int(n)-1]['name']} | {v} |" for n,v in sums.items() if v!=1)
 printedpage=175 if year=='1970s' else 176
 catchtotal=sum(D(v) for r in m['landings'].values() for v in r.values())
 mb=(d/'MASS_BALANCE.md').read_text(encoding='utf-8').replace('`ewe_model_json_creator.py`','the source-preserving local copy of `database_json.py`').replace('which is a lower bound on what the model may actually contain, not a steady-state result.','which is an assumption for this diagnostic calculation; negative or positive unreported BA would change it in either direction.')
 (d/'MASS_BALANCE.md').write_text(mb,encoding='utf-8')
 report=f'''# Northern South China Sea ({year})

**Status: partial reconstruction; balance INDETERMINATE.** Published core parameters, diets and catches have been extracted. Missing source fields and inconsistencies prevent a claim that this is a fully reproduced or load-tested native EwE model.

**Source:** Cheung, Wai Lung (2007). *Vulnerability of marine fishes to fishing: from global overview to the northern South China Sea*. University of British Columbia doctoral thesis. DOI 10.14288/1.0074894. Local source: `ubc_2007-317501-87ea9ea0.pdf`.
**LME:** 36 South China Sea. **Coverage:** northern continental shelf, mainly the Chinese EEZ; not the whole LME (printed p.170 / PDF p.185).
**Model identifier:** SCS-2007, the existing archive source identifier used as a surrogate in `model_number`; this is not a verified EcoBase numeric ID. Metadata reports EcoBase 410 without a verified period mapping, so it was not assigned to either model.
**Period:** {year}; retained as a decade label, not an invented single year.
**Groups:** 38 (35 consumers, 2 primary producers, 1 detritus). **Fleets:** {', '.join(m['fleets'])}.
**Extracted:** 2026-09-04.

## Source inventory and authority

README.md and metadata.json were read first. The bundle contains one 369-page thesis and those two archive reference files; no supplement, workbook or native model is present. `../SOURCE_INVENTORY.json` records sizes and hashes. PDF printed pages are PDF page minus 15 in the relevant chapters. Core sources: Table 6.1 pp.175-176 / PDF190-191; Table 6.2 pp.178-179 / PDF193-194; Table 6.5 p.190 / PDF205; Appendix6.1 pp.322-341 / PDF337-356; Appendix6.2 pp.342-348 / PDF357-363.

Final chapter tables take precedence over conflicting appendix parameterization prose. Alternatives remain listed in `../SOURCE_CONFLICTS.md`. Parenthesized values are retained and tagged as Ecopath estimates per Table6.1 caption. All supplied source files are unchanged.

## Source tables

### Table 6.1 - basic inputs

Columns: Group no. | Functional group | B | P/B | Q/B | EE. Mapping: n | name | biomass | pb | qb | ee. There are exactly 38 rows per period, in the original order. Units are t/km2 wet weight for B and /year for P/B and Q/B, supported by Appendix6.1. Dashes and empty cells stay blank. Right-aligned numeric columns were mapped using their PDF coordinates, approximately x=365,410,456,501 points. The 1970s jellyfish row checks the mapping: P/B=5.00, Q/B=20.0, giving diagnostic P/Q=0.25; EE=0.950.

Names were matched across tables using an explicit abbreviation map (Juv./Juvenile, Ad./Adult, Dem./Demersal; plankton singular/plural; taxonomic suffixes). The source spelling 'Demesral' is retained. The optical text layer's '<' in small-group labels was restored to the visible '≤'; whitespace around '>30' was standardized. No groups were merged or renumbered.

### Appendix 6.2 - diet composition

The appendix is labelled for both periods and contains one shared set of 35 predator columns. Prey are rows, predators are columns. There are 417 printed nonblank fractions. All ten blocks across seven pages were extracted from word coordinates with `pdfgrid.get_words(merge_gap=0.4)` and checked against 200-dpi images. Wrapped labels were joined before matching group names. Numeric right-edge clusters were aligned to the named predator headers; exact mappings are retained below and in `../work/table_layouts.json`.

| Printed / PDF page | Predator group numbers | Raw body line indices (inclusive) | Right-edge anchors (points) |
|---|---|---|---|
{layoutrows}

All 38 prey rows are retained, including primary producers and detritus; consumers are groups3-37. Empty matrix cells remain empty. Diet Import is 0 under the skill's explicit no-reported-import convention, not a separately tabulated source observation. No diet fractions were normalized, including in the database JSON.

### Table 6.2 - catches

Columns: group | 1970s total | 2000s PSt | ShT | PS | H&L | GN | Others | total. PSt=pair and stern trawl; ShT=shrimp trawl; PS=purse seine; H&L=hook and line; GN=gillnet. Both parts were joined by group name to give 38 rows. The 1970s uses one aggregate column labelled Total fishery; the 2000s retains all six fleet columns. Reported catch is written to Landings; no discard split is supplied. These are annual catches (Table caption density units t/km2; Appendix6.1 and chapter methods specify annual landings). No area conversion is applied.

Sum of extracted catch entries: **{catchtotal} t/km2/year**. The printed 1970s grand total is0.8500 versus sum0.8501. For the 2000s the six-fleet cell sum is7.7375 versus printed grand total7.736; printed group totals sum to7.738. Generated Total cells use exact decimal sums of fleet entries. `SOURCE_CATCH_TOTALS.json` preserves each printed total so the differences remain reviewable.

### Table 6.5 - mortality outputs

Columns: group | 1970s F | M | M0 | 2000s F | M | M0. M0 is carried verbatim as an annual other-mortality rate for37 living groups; detritus has no row. F and the column labelled M are retained in `SOURCE_MORTALITIES.json` for diagnostics. The M column behaves as predation mortality (M0 is separately listed), despite the caption saying natural mortality. No F+M or other sum was substituted for P/B. Some mortality rows do not reproduce Table6.1 precisely; final table values remain separate.

## Biomass accumulation

Searched chapter6 and Appendix6.1-6.2, then the entire thesis text for biomass accumulation, BA, dB/dt, steady state, migration and biomass change. Ecopath is described as steady-state on p.172 / PDF187. The thesis revisits the steady-state assumption on p.289 / PDF304. Equation6.1 defines BA but supplies no group-specific numeric BA. Figures6.2-6.5 compare period snapshots, not model-year accumulation; Ecosim trajectories in later chapters are simulations. No numeric BA was extracted. Both BA columns remain blank, and both database fields are -9999. No residual from the balance check was entered as data. No numeric net migration term was found for these static models.

## Values from prose

{proserows}

P/Q assumptions are copied only where the text scopes them to the period/group. In particular, the pomfret assumption0.2 slightly differs from the 1970s table-derived ratio1.30/6.38; both are retained with distinct provenance. Total mortality Z is populated only for explicitly stated, matching P/B=Z cases. Appendix assumptions that disagree with the final basic table are not used to backfill Z.

## Conventions applied

No GS, BA, habitat, detritus routing or discard defaults were inserted into source fields. The only explicit numerical output convention is Diet Import0 when no import is reported. Decade labels and the source identifier are retained. The single aggregate 1970s fleet name is an output label.

## Deliberate blanks

The full bundle and whole-thesis text were searched, with a second targeted search after table extraction.

- Unassimilated consumption: no numerical assumption found for any consumer. All GS cells blank; EwE may use0.2 on import. The checker uses0.2 for diagnostic respiration/detritus calculations, but this is not a paper value. No0.35/0.4 zooplankton convention was authorized or applied. Producer/detritus GS is inapplicable.
- Habitat area: no group habitat fractions reported. CSV blank, database -9999. Biomass is the paper's model-area density; internal arithmetic uses that common area basis, without a biological habitat restriction. EwE's default habitat proportion is1.
- Discards: not separated numerically from the published catch. Blank, not evidence of zero; catch remains in Landings. EwE may import blank discards as0.
- Detritus fate/export routing and detritus import: no numerical routing or import statement located. One detritus pool does not establish that100% of all mortality enters it. Fate and import cells stay blank; database unknown fates are -9999. The checker's pooled detritus calculation is indicative and cannot validate this missing routing. EwE may export an unspecified routing remainder.
- Trophic levels: no complete group-specific numeric TL table located. TL.xlsx includes all38 groups with blank TL cells; TL values were not manufactured from the matrix or read as false-precision values from a graph.
- Other blank Z/PQ cells: no unambiguous final-period numeric statement. No derived replacements.

## Model-estimated values

Parentheses in Table6.1 denote values estimated by Ecopath. All are retained with this category in `PROVENANCE.json`.

| Group | Name | Field | Printed value |
|---|---|---|---|
{estimated}

## Unresolved and flagged

See `../SOURCE_CONFLICTS.md` for the cross-source conflict register. The appendix discusses an extra large-benthopelagic group which has no row in the final38-group table; it was not added. Juvenile/adult groups are kept separate. Appendix TableA6.3 provides stanza-growth settings beyond the eight-file schema; these are documented in `../MULTISTANZA.md`. Native stanza linkage and a native EwE load test have not been performed.

The 1970s turtle table values B0.0002 and P/B0.100 imply production0.00002, while printed catch is0.0001. This is a source-level inconsistency confirmed in the rendered tables. Table6.5 instead prints F0.05, which would imply0.00001 catch with that B; the latter is a diagnostic inference and was not substituted. The 2000s pinniped catch is printed as zero in Table6.2 although Table6.5 F0.01 is nonzero. Several1970s diet/predation results disagree with the printed EE beyond rounding. Rechecking the source matrix did not reveal shifted columns. A shared published matrix may not fully reproduce both final parameterizations; a native author model would be needed to resolve that possibility.

## Validation

`validate.py`: **0 errors,41 warnings**: one aggregate GS warning, one all-blank BA warning,38 unknown detritus-fate rows, one warning covering38 blank TLs. All CSVs use consistent38-group numbering and CRLF. All35 diet sums are within±0.01 (range{min(sums.values())} to{max(sums.values())}). Non-unit sums below are preserved.

| Consumer | Name | Diet sum |
|---|---|---|
{drift}

`MASS_BALANCE_SOURCE.txt` preserves the source-file arithmetic check. Database check: **INDETERMINATE**, with {'17' if year=='1970s' else '7'} EE discrepancies beyond0.05 and3 low-P/Q warnings for birds/mammals. The source-file checker reports {'1 error and20 warnings' if year=='1970s' else '0 errors and10 warnings'}; its hard turtle error assumes no BA. The database checker treats unknown BA explicitly, hence the different verdict wording. Neither result establishes a balanced native model. The low-P/Q values were visually confirmed and retained.

## Conversion and round-trip limitations

The installed converter normalized diet columns and filled several missing fields with defaults. A local copy under `../work/` was adapted to preserve source diet fractions, missing habitat/fate values, and P/Q, and to read metadata from the sibling workbook. `converter_changes.patch` records the exact differences; the installed skill is untouched. The source CSV/XLSX files and `model.json` are the authoritative extraction. The database JSON stores density biomass on the model-area basis; unknown fields use-9999. Its reconstruction workbook consolidates catches and does not reproduce individual fleets, all-zero catch rows, Z, or blank TL/BA sheets. It is a round-trip inspection artifact, not a substitute for the eight import files.

'''
 report=re.sub(r'(?<=[A-Za-z])(?=\d)', ' ',report) if False else report
 (d/'REPORT.md').write_text(report+mb,encoding='utf-8')
(out/'MASTER_INDEX.md').write_text('''# SCS-2007 extraction set

Both requested periods were extracted from Cheung (2007). Each contains38 groups and35 consumer diets. Core tables are transcribed; missing source fields and unresolved arithmetic make both reconstructions **partial**. Neither is certified balanced or native-load-tested.

| Model identifier | Period | Groups | Fleets | Status | Balance | Report |
|---|---|---|---|---|---|---|
| SCS-2007 | 1970s | 38 | 1 aggregate | partial | INDETERMINATE;17 EE discrepancies, including turtle catch exceeding production | [Report](SCS-2007_Northern_South_China_Sea_1970s/REPORT.md) |
| SCS-2007 | 2000s | 38 | 6 | partial | INDETERMINATE;7 EE discrepancies | [Report](SCS-2007_Northern_South_China_Sea_2000s/REPORT.md) |

Missing: numerical GS, BA, habitat proportions, detritus routing/import, discard split and group TLs. Source blanks remain blank; no diet normalization was applied. SCS-2007 is the archive identifier, not a verified EcoBase number. Metadata's reported410 was not assigned without a period mapping.

[Source conflicts](SOURCE_CONFLICTS.md) · [Multi-stanza notes](MULTISTANZA.md)

Each model directory contains the eight EwE import files, extraction JSON, database JSON, reconstructed workbook, provenance and validation reports. Working text, page images, extraction scripts and the source-preserving converter copy are under work/. Source README, metadata and thesis remain unchanged.
''',encoding='utf-8')
print('Reports and provenance written; source PDF hash matches archive metadata.')
