from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work'
D=ROOT/'HS_077_1_Eastern_tropical_Pacific_1993-1997'
p=json.loads((WORK/'provenance.json').read_text(encoding='utf-8'))
model=json.loads((D/'model.json').read_text(encoding='utf-8'))
sums=json.loads((WORK/'diet_sums.json').read_text(encoding='utf-8'))
bad=[(n,model['groups'][int(n)-1]['name'],v) for n,v in sums.items() if abs(float(v)-1)>.01]
est={f:[str(x['n']) for x in p['basic'] if x['fields'].get(f,{}).get('model_estimated')] for f in ['biomass','ee']}
text="""# Eastern tropical Pacific (1993-1997), final model ETP7

**Extraction status: PARTIAL / NOT IMPORT-READY.** The published ETP7 basic inputs and fisheries were extracted, but nine published diet columns do not sum to one and numeric detritus parameters/routing are absent. Those source defects remain visible. The bundled EE arithmetic alone reports BALANCED; that does not validate the malformed diets or establish a complete loadable model.

**Source:** Olson, R. J. and Watters, G. M. (2003). A model of the pelagic ecosystem in the eastern tropical Pacific Ocean. Inter-American Tropical Tuna Commission Bulletin 22(3), pp.135-218 (bilingual volume).
**LME:** HS_077 Pacific Eastern Central high seas. **Model number:** HS_077_1.
**Groups:** 39 rows: 38 living (36 consumers; 2 producers) plus Detritus.
**Fleets:** Longliners; Baitboats; purse-seine unassociated; purse-seine floating-object; purse-seine dolphin.
**Extracted:** 2026-09-04.

## Source bundle and eligibility

Read README.md and metadata.json before extraction. The bundle has one 89-page PDF, README.md, metadata.json, and footprint.geojson; no supplement, spreadsheet, or author model file is supplied. Metadata supplies the HS_077 high-seas classification and intended envelope, not numerical model parameters. The article covers a broader pelagic ETP ecosystem than the high-seas target alone; the target identity is retained without claiming spatial equivalence.

The publication averages estimates over 1993-1997 where possible (printed p.137 / PDF7). Some component source observations are older (e.g. bluefin); 2003 is the publication year, not the model year.

- ETP7 is the final eligible published parameterization (Tables2a and3a).
- ETP1 is explicitly described as unbalanced (printed p.139 / PDF9; Appendix Tables1a/2a at PDF82 and84-85). It is excluded from balanced-model imports. The first balanced model is identified as ETP2 (printed p.141 / PDF11).
- Intermediate ETP2-ETP6 are discussed, but complete individual parameter sets are not published. ETP5 sensitivity perturbations (including Cephalopod Q/B9.8 and Auxis P/B1.5 on p.141) cannot be combined with ETP7's changed groups and parameters. Figure2 is a dynamic comparison, not a full parameter table.
- English and Spanish copies are translations of the same model, not distinct models.

PDF source SHA-256: SOURCEHASH.

## Source tables

### Table2a (printed p.156 / PDF26): basic parameters

Mapped headers: Component -> group name; Trophic level -> TL; B -> biomass; P/B -> production/biomass; Q/B -> consumption/biomass; EE -> ecotrophic efficiency; U/Q -> unassimilated consumption (GS).

There are 38 living rows. Group order was fixed from Table2a and checked against the explicit IDs in Table3a; the original row39 Detritus was retained from Table3a with blank basic parameters. Row40 is external prey and maps to Import, not an extra organism. Table1a (PDF22-23) describes taxa and size ranges; no taxonomy workbook is produced.

The header mapping was checked with Large yellowfin: P/B2.35, Q/B15.6 and GS0.30 give diagnostic P/Q about0.151 and positive respiration. No P/Q was inserted into source files. Consumer Q/B and GS are present for all36 consumers; producers have no Q/B or GS.

B is printed in tons per million km2; every B value is divided by1,000,000 using decimal scaling. Example: Large yellowfin6500 ->0.006500 t/km2. The paper's density is on its model-area basis, not a separately tabulated habitat-area density. Basic_input uses its mandatory B column for the reported density; habitat fractions remain unknown. The database's biomass field preserves the published model-area density directly, without fabricating a habitat fraction or multiplying by1.

Footnote1 marks Ecopath-computed values. Biomass is model-estimated for groups ESTB. EE is model-estimated for groups ESTEE; other displayed basic values are supplied parameter estimates.

Sea turtle B appears as baseline '2601' in English Table2a. Spanish Table2b (printed p.157 / PDF27), inspected at300dpi, unambiguously prints260 with superscript1. This resolves it as260 t/million km2, an Ecopath estimate, not2601. EE for Baleen and Toothed whales is printed '<0.001'; exact numeric EE cells remain blank and the bounds are recorded here.

### Table3a (printed pp.158-159 / PDF28-29): diets

Prey rows1-40; predator columns1-18 on the first page and19-36 on the continuation. The layout is stored sideways. Raw pdfgrid output was examined first. Poppler bounding boxes from the bundled pdfgrid parser were assigned directly to the printed prey IDs along x and predator IDs along y; no positional text-layout parsing was used. This avoids merging narrow numeric gutters. Complete bbox XHTML and conventional-orientation TSVs are in work.

The bundled PDF rotation helper requires unavailable PyMuPDF; it was not installed. Instead the original PDF remained untouched, coordinate axes were mapped as stored, and 200dpi page renders were rotated into upright PNGs for visual inspection. All315 populated diet cells were independently compared against the Spanish Table3b (PDF30-31); both copies agree exactly, including the defects.

The external-prey fraction0.667 for Bluefin is carried as Import (source row40). The remaining import cells are blank. No diet is normalized. Empty prey cells remain blank in CSV; no unreported fractions are allocated.

### Tables5a and6a (printed pp.175 and177 / PDF45 and47): fisheries

Header mapping in order: Longliners; Baitboats; purse-seine Unassociated; Floating-object; Dolphin; Total. Rows1-34 match the source, and all five fleets are retained. Row and fleet totals are computed only from extracted fleet cells by the bundled writer. Landings and discards are separate published quantities, both in tons per million km2 per year, converted by1,000,000. Example: Large yellowfin longline landings520.00 ->0.00052000 t/km2/year.

Two censored Dolphin landings (Large swordfish and Large wahoo) are '<0.01' in source units, hence '<0.00000001' t/km2/year. They remain blank rather than becoming zero or the bound. Large swordfish reported total10.95 differs from the exact numeric fleet-cell sum10.94; the generated total is the latter, and the reported10.95 remains in work/provenance.json. Small swordfish unassociated landings0.00 is an explicit zero and is preserved.

Unreported catch cells remain blank; no coastal/artisanal/recreational fishery values were invented. The paper explicitly excludes those fisheries for lack of data (printed p.139).

## Biomass accumulation

The complete bilingual PDF was swept for accumulation terms, then revisited with group-specific searches. Printed pp.136-137 define BA in the general Ecopath/Ecosim equations but give no numerical static BA. No numeric BA is tabulated in Tables2-8 or the appendices. No per-group BA is set to zero.

Figures2-4 (printed pp.149-151 / PDF19-21) were rendered at300dpi and inspected. They show Ecosim trajectories, relative biomass/CPUE, fishing effort and climate forcing. Their curves are not statements of the BA term for the 1993-1997 Ecopath snapshot. No slope was digitized or inserted. 'Steady-state' occurs in discussion of model approaches, not as an explicit numeric BA assignment.

Biomass_accumulation.csv is intentionally blank for all39 rows. Both database BA fields are -9999. The arithmetic diagnostic omits unknown BA internally; its suggestions are never entered as data.

## Values from prose

- Model area approximately32.8million km2 and bounds20N-20S,150W to the shelf break along the Americas: p.137/PDF7. Density conversion is by1million because that is the source's stated denominator, not division by the whole32.8million area.
- P/B=Z is explicitly stated for stock-assessment estimates (p.138/PDF8). Z is carried alongside P/B for Large/Small yellowfin and Large/Small bigeye (groups8,9,21,22; sources Table4a), and for Bluefin group20 whose P/B source explicitly is biomass-weighted Z (Table4a p.164/PDF34). Other Z cells remain blank.
- The author derived U/Q from prey proximate composition and digestibility (pp.138-139); final U/Q values are already tabulated and copied unchanged, including Mesozooplankton0.35 and Microzooplankton0.42. No software or project assimilation convention is used.
- Bluefin overlap is7% of model area with four months' residency (p.142/PDF12). Table4a footnote10 (p.167/PDF37) explicitly applies those factors to predator diet contributions. They are already represented in the published diets; they are not reapplied to B or relabelled as an independently stated EwE habitat-area input.
- Immigration is assumed to balance emigration (pp.137 and146). This is a net-balance assumption, not numeric gross immigration/emigration inputs; the latter remain unknown.

## Conventions applied

None for ecological parameters. No default habitat area, GS, BA, detritus fate, missing diet residual, or catch value was supplied. Format-only transformations are unit scaling, removal of thousands separators and superscript footnote markers, explicit external-prey mapping, and writer-generated totals.

Group names follow the source; two 'Misc.' abbreviations are kept. Model name is the place alone; versionETP7 is in provenance and this report. Source period is retained as1993-1997.

## Deliberate blanks

- BA for all groups: not numerically stated; EwE may default0, while extraction/database retain unknown.
- Habitat fractions for all groups: not tabulated as model inputs. EwE may default1; extraction/database remain unknown. Bluefin overlap is not silently repurposed as a habitat scaling factor.
- Detritus basic parameters, TL, import and all39 detritus-fate rows: the source identifies the pool in Table3 but provides no numeric fate allocations, pool biomass, or TL. No assumption that all production routes to the sole pool was used. EwE may export the unspecified fate remainder.
- EE for groups3/4: censored '<0.001', not an exact number.
- Other mortality and P/Q: not printed as input columns. The diagnostic may derive ratios internally but import files stay blank.
- GS for the two primary producers and detritus: not applicable and absent. The generic validator warns of an EwE0.2 default; it is not a consumer-data omission.
- Missing catch/import cells and the two censored catch cells remain blank. EwE may substitute0; database fields remain -9999 where no numeric total/import is available.
- No numerical growth or price values were derived for database vbk/shadow_price placeholders. Ontogenetic Tables7-8 concern split-pool transition parameters, outside these eight static import files; no dynamic loadability claim is made.

## Unresolved and flagged

The following diet sums are source inconsistencies, visually verified in the English pages and identically reproduced in Spanish:

| Consumer | Group | Sum | Source |
|---|---|---|---|
BADROWS

Albacore column18 sums1.001, within the structural tolerance; it also remains unchanged. All other columns sum1.000. Some adjacent excesses and deficits suggest typesetting displacement, but no value has been shifted or normalized to repair them.

Low diagnostic P/Q for birds and marine mammals (groups1-6) comes from the printed low turnover and high Q/B values; columns and values were visually verified on p.156. These are endotherm groups, and their positive respiration does not resolve the source diet defects elsewhere.

The generic mass-balance script estimates pooled detritus inflow despite absent routing. That estimate is conditional and does not establish an actually parameterized detritus balance. Habitat/input completeness is also outside its arithmetic verdict.

## Validation

Bundled validate.py: **9 errors,43 warnings**. The nine errors are the source diet sums above. Warnings:39 absent detritus-fate rows;1 all-blank detritus basic row;1 GS warning covering producers/detritus;1 entirely blank BA file;1 absent detritus TL. No CSV formatting, numbering, fleet-total, or row-consistency error remains.

Diet sums range0.425-1.575; nine columns exceed±0.01. All39 fate rows are unknown, not falsely asserted to sum1. The standalone massbalance_check.py reports0 errors,6 low-P/Q warnings and35 notes. Maximum absolute EE difference is0.014 for Small yellowfin; no reconstructed EE exceeds1.

## Database conversion and round-trip verification

The requested bundled write_outputs.py generated all eight import files. The bundled database_json.py was executed on those files, but its raw output normalizes diets, inserts habitat1 and other placeholder zeros, and drops the all-blank detritus row. Those behaviors conflict with the extraction's source-preservation rules. The untouched raw output, workbook and log were archived in work/raw_converter.

A documented local adapter (work/adapt_database.py) reads the actual generated CSVs, restores all source proportions exactly, retains39 groups, and restores -9999 for unknown fields. It carries B as the published model-area density directly. It reruns the bundled equations on the corrected JSON. The installed skill and source files were not modified.

The reconstructed workbook was rebuilt from the corrected database parameters. source_parameters.json preserves fleet-disaggregated catches, Z, TL and metadata that the database schema cannot represent. It supplements the reconstructed sheets without inventing values. The workbook was reopened and all3162 source/reconstructed cells were checked, including blanks; all315 populated diet cells remain exact. No source diet normalization remains in the final database or workbook. Database unknowns and the39-group count are verified in roundtrip_verification.json.

Numeric source values are retained as strings in the reconstruction to preserve printed precision after unit conversion. Missing detritus-fate and biological values remain blank. Numerical analyses can parse these strings; the eight CSV/XLSX imports remain the canonical EwE input artifacts.

"""
text=text.replace('SOURCEHASH',p['source_sha256']).replace('ESTB',', '.join(est['biomass'])).replace('ESTEE',', '.join(est['ee']))
text=text.replace('BADROWS','\n'.join(f'| {n} | {name} | {s} | Table3a p.{158 if int(n)<=18 else 159} / PDF{28 if int(n)<=18 else 29} |' for n,name,s in bad))
(D/'REPORT.md').write_text(text+(D/'MASS_BALANCE.md').read_text(encoding='utf-8'),encoding='utf-8')
index="""# Eastern tropical Pacific extraction set

One eligible final Ecopath parameterization is extracted. Source defects remain visible; this is not a certified loadable EwE model.

| # | Model | Year | LME / unit | Groups | Fleets | Status | Notes |
|---|---|---|---|---|---|---|---|
| HS_077_1 | Eastern tropical Pacific ETP7 | 1993-1997 | HS_077 Pacific Eastern Central high seas | 39 (38 living + detritus) | 5 | partial | Nine published diet-sum errors; absent detritus parameters/fate and BA. EE-only arithmetic BALANCED with6 warnings; not import-ready. |
| excluded ETP1 | Initial Eastern tropical Pacific draft | 1993-1997 target period | HS_077 | 34 | - | excluded | Explicitly unbalanced, p.139/PDF9; Appendix Tables1a/2a are initial estimates. |
| excluded ETP2-ETP6 | Intermediate reviewed models and ETP5 sensitivities | not separately established | HS_077 | varied | - | excluded | Discussed but no complete distinct parameter tables; ETP5 dynamics are not additional extractable snapshots. |

See the model REPORT.md for provenance, every blank and flag, and converter limitations. work contains bbox coordinates, prose sweeps, rendered page evidence, deterministic extraction/adapter scripts and raw converter outputs. All original article files remain unchanged.
"""
(ROOT/'MASTER_INDEX.md').write_text(index,encoding='utf-8')
inventory="""# Source bundle inventory

| File | Role | Coverage | Authority / extraction location |
|---|---|---|---|
| Olson_Watters_2003_ETP-c037fcbc.pdf | Published bilingual bulletin,89pages | FinalETP7; initialETP1; intermediate model discussion | Primary numerical source. BasicPDF26-27; dietsPDF28-31; sourcesPDF32-37; landingsPDF45; discardsPDF47; BA/dynamic figuresPDF19-21; initial tablesPDF82,84-85. |
| metadata.json | Atlas bibliographic/model-envelope metadata | ArticleETP-2003; unitHS_077 | Read-only catalog context; original1993–1997 model-period claim verified in PDF7. |
| README.md | Atlas article overview | ETP-2003 | Read-only catalog context; complete-table/loadability claims treated as provisional and checked. |
| footprint.geojson | Target spatial envelope | High-seasEasternCentralPacific | Read-only target geometry, not a numerical Ecopath source; wider paper domain retained in report. |

No supplement, author model file, spreadsheet, prior calculation or other source file was supplied. Only ETP7 qualifies for a published balanced-model extraction, with source defects documented. ETP1 is explicitly pre-balance.
"""
(ROOT/'SOURCE_INVENTORY.md').write_text(inventory,encoding='utf-8')
manifest={f.name:{'size_bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in ROOT.parent.iterdir() if f.is_file()}
(WORK/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(D)
