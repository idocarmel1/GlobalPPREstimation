from pathlib import Path
import json,csv,hashlib
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'work';M=ROOT/'35_1_Gulf_of_Thailand_1973'
DB=M/'35_Gulf_of_Thailand_35_1_Gulf_of_Thailand_(1973).json'
j=json.loads(DB.read_text(encoding='utf-8'));groups=j['group'];by={g['group_seq']:g for g in groups}
source=json.loads((M/'model.json').read_text(encoding='utf-8'))
cells=json.loads((WORK/'source_cells.json').read_text(encoding='utf-8'))
def num(s):return None if s in [None,'-9999',''] else D(s)
q={};diets={};missing=[];derived=[]
for g in groups:
    n=g['group_seq'];b=num(g['biomass']);qb=num(g['qb']);pq=num(g['ge']);pb=num(g['pb'])
    if qb is None and pq is not None and pb is not None:
        qb=pb/pq;derived.append(n)
    q[n]=None if qb is None else b*qb
    diets[n]={v['prey_seq']:D(v['proportion']) for v in (g['diet_descr'] or {}).get('diet',[])}
    if g['pp']=='0' and not any(v>0 for v in diets[n].values()):missing.append(n)
res=[]
for g in groups:
    n=g['group_seq'];b=num(g['biomass']);pb=num(g['pb']);ee=num(g['ee']);ba=num(g['biomass_accum']);y=num(g['export'])
    pred=sum((q[c]*ds.get(n,D(0)) for c,ds in diets.items() if q[c] is not None),D(0))
    ee_calc=(pred+(y if y is not None else D(0))+ba)/(b*pb) if pb is not None and pb>0 else None
    res.append({'n':n,'name':g['group_name'],'EE':ee,'EE_calc':ee_calc,'predation':pred,'catch':y,'BA':ba,'known_catch':y is not None})
over=[r for r in res if r['EE_calc'] is not None and r['EE_calc']>1]
gaps=[r for r in res if r['EE_calc'] is not None and abs(r['EE_calc']-r['EE'])>D('.05')]
maximum=max(gaps,key=lambda r:abs(r['EE_calc']-r['EE']))
lines=['# Mass balance','', '**Verdict: NOT BALANCED as the published tables are transcribed.** This verdict concerns the available reconstruction, not a claim that the authors failed to balance their unpublished model.','',
'This final analysis uses the corrected database JSON, exact unnormalized diet proportions, stated biomass/catch/BA, and the source P/Q (database ge). When Q/B is dashed but P/Q is stated, Q/B = (P/B)/(P/Q) is calculated for arithmetic only; no derived Q/B is written to the import files or database. The bundled raw calculation and its normalized database result are retained only as working evidence.','',
f'Q/B is derived internally for {len(derived)} consumers. Ten consumers have no positive diet entries: {", ".join(missing)}. Their predation is unreported, so recomputed prey demands are lower bounds. Missing catch for nine groups is likewise treated as zero only for this lower-bound calculation. No unknown detritus fate or assimilation fraction is supplied.','',
f'{len(over)} groups have lower-bound recomputed EE > 1: '+', '.join(f"{r['n']} ({r['name']}, {r['EE_calc']:.3f})" for r in over)+'.',
f'{len(gaps)} groups differ from printed EE by more than 0.05; maximum absolute difference {abs(maximum["EE_calc"]-maximum["EE"]):.3f} at group {maximum["n"]} ({maximum["name"]}).',
'','Every group has a source-stated absolute BA, including 26 printed zeros and 14 nonzero entries. No BA is inferred to close a gap. Migration terms were not reported in the chapter; they cannot be used to reconcile the discrepancies.','',
'Mammals P/Q = 0.05 / 30.00 = 0.001667 is unusually low and was visually verified in Table 1, printed p.369. The other stated P/Q values are 0.20 or 0.25. Assimilation is not reported, so positive respiration cannot be proved without an import assumption. Under the EwE GS = 0.2 assumption, none implies non-positive respiration; that assumption is not extracted as data. Detritus-pool balance is undecidable because routing and GS are unreported.','',
'The overproduction flags are supported by verified Table 1 B/PB/BA, Table 2 catch, and Table 3 feeding values. Known diet columns with sums above one inflate consumption, but normalizing them would alter the publication and is prohibited. Some EE mismatches can also reflect the conflicting catch versions discussed in REPORT.md.','',
'| Group | Name | Printed EE | Recomputed lower-bound EE | Reported catch | BA |','|---|---|---|---|---|---|']
for r in res:lines.append(f"| {r['n']} | {r['name']} | {r['EE']} | {r['EE_calc']:.4f} | {r['catch'] if r['catch'] is not None else 'unknown'} | {r['BA']} |" if r['EE_calc'] is not None else f"| {r['n']} | {r['name']} | {r['EE']} | undecidable | unknown | {r['BA']} |")
mass='\n'.join(lines)+'\n';(M/'MASS_BALANCE.md').write_text(mass,encoding='utf-8')
diet_sums={str(c):sum((D(v) for v in source['diet'].get(str(c),{}).values()),D(0)) for c in source['consumers']}
bad={k:str(v) for k,v in diet_sums.items() if v and abs(v-1)>D('.01')}
estimated={}
for c in cells['basic']:
    if c['category']=='model-estimated':estimated.setdefault(c['parameter'],[]).append(str(c['group']))
nonzero=[g for g in source['groups'] if D(g['ba'])!=0]
report=f'''# Gulf of Thailand (1973)

**Source:** Vibunpant, S., N. Khongchai, J. Seng-eid, M. Eiamsa-ard and M. Supongpan. 2003. Trophic model of the coastal fisheries ecosystem in the Gulf of Thailand. In Assessment, Management and Future Directions for Coastal Fisheries in Asian Countries, WorldFish Center Conference Proceedings 67, pp.365-386.

**LME:** 35 Gulf of Thailand. **Model number:** 35_1 (assigned atlas extraction identifier).
**Groups:** 40 (37 consumers, 2 primary producers, 1 detritus). **Fleets:** Otter board trawl; Pair trawl; Beam trawl; Pushnet; Purse seine; Other gear.
**Extracted:** 2026-09-04. **Status:** partial, source transcription complete; not ready for a defensible complete EwE reconstruction. **Mass-balance verdict:** NOT BALANCED for the source-preserving reconstruction.

## Source inventory and model eligibility

README.md and metadata.json were read first. The only published source supplied is content-d78aa261.pdf, 22 pages (printed pp.365-386). SHA-256: {hashlib.sha256((ROOT.parent/'content-d78aa261.pdf').read_bytes()).hexdigest()}. The article folder also contains README.md, metadata.json and footprint.geojson; these are catalog/spatial context, not author model inputs. No supplement, native EwE file, spreadsheet, prior extraction or prior calculation is supplied. Sources were not changed.

One static 1973 model is independently parameterized in Tables 1-3. The 1973-1993 time series, 1993 fishery results, 1993-2000 management scenarios, optimization strategies, and 1998 aspect-ratio measurements are not separately parameterized static Ecopath models. They were reviewed and no extra model was invented.

## Source tables

### Table 1, printed pp.368-369 (PDF pp.4-5): group list and basic input

Columns: Ecological group | Biomass (t/km²) | P/B (year⁻¹) | Q/B (year⁻¹) | EE | P/Q | Biom.acc. (t/km²/year). Mapped to name, biomass, pb, qb, ee, pq, and absolute ba. No unit conversion. The 13 rows on p.368 plus 27 continued rows on p.369 establish all 40 groups; Table 3 supplies numbering in the same order. Group 28 Seaweeds and group 39 Phytoplankton are producers; group 40 is Detritus. Group 20's comma is removed (Crab, Lobster → Crab Lobster) solely for the required unquoted CSV format. Table 1's Lutianidae spelling is retained and explicitly matched to Lutjanidae in Tables 2-3. Ponyfishes is matched to Pony fishes; capitalization differences for medium demersal groups are immaterial.

Caption states parenthesized values are estimated by Ecopath to fit mass-balance constraints. All 43 parenthesized values are extracted, with cell-level provenance in source_cells.json. Estimated group lists: {estimated}. Parentheses are provenance notation, not negative signs. The mapping check is Scomberomorus: 0.07 / 0.35 = P/Q 0.20. Carangidae and Pomfret are consistent within printed precision. Q/B is dashed in 33 consumers; stated P/Q is retained rather than manufacturing Q/B source cells.

Coordinates were read with the bundled pdfgrid.py (Poppler backend); Table 1 lines 28-40 on PDF p.4 and lines 4-30 on p.5. All table rows were visually verified on 220-dpi renders. Detritus B is printed 10 000, extracted as 10000, not 10.000 or 10.0.

### Table 2, printed p.371 (PDF p.7): catch by fleet

Columns: ecological group, six fleets, Total. Each of 31 printed catch rows is matched by name to Table 1. Catch is already t/km²/year. Every printed zero is retained; nine omitted group rows remain unknown. All eight deliverable group tables retain the complete 40-group spine. Catch goes to Landings because no discard split is stated; Discards remains blank. Fleet Other gear is defined in the caption as shrimp gillnet, fish gillnet, swimming crab gillnet and trap.

The printed fleet totals 0.991, 0.543, 0.023, 0.072, 0.158, 0.646 sum to 2.433 and match the reconstructed individual cells exactly. All rows and fleet headers were visually checked at 220 dpi. Table 4 (p.374) gives juvenile fractions of trashfish for Otter board trawl, Pair trawl and Pushnet. These are not applied again to Table 2 because juvenile catches already have their own explicit rows; a second split would double count or overwrite the source.

### Table 3, printed pp.372-373 (PDF pp.8-9): diet

Prey rows 1-23 and continued 24-40; same 31 predator columns on both pages: 1-25 and 29-34. Predator numbering is anchored to the numbered header, never inferred from dense body values. pdfgrid merge_gap=0.4; header lines 5 and 2 after a clockwise coordinate transform. The installed rotate_pdf.py required unavailable PyMuPDF; no package was installed. Original Poppler word boxes were rotated in memory (x′=792-y, y′=x), saved with originals in work, and reconstructed using the bundled pdfgrid. Separate rendered page images were turned upright solely as working views. All flagged columns were compared to the 300-dpi pages.

The paper really omits columns 26,27,35,36,37,38. These six consumers receive blank output columns to show missing diets. Printed columns 6,12,22,32 contain only dashes/zeros and have no positive diet. A blank/dash in an otherwise populated diet is preserved as absent feeding; an entirely absent/empty diet is unresolved, not a producer. The source prints a literal -0 at prey 11 / predator 29; it is retained exactly and represents numeric zero. Source blank at prey 31 / predator 31 remains blank.

Nonzero-column sums range 0.90-2.00. Fifteen nonzero columns exceed ±0.01 from one: {bad}. Coastal tuna sums 0.99 (at tolerance), also retained. Crab Lobster has both Benthos=1 and Detritus=1; Rastrelliger has Zooplankton=0.9, Juvenile small pelagics=0.1, Phytoplankton=0.1. These are visible source problems, not rounding to be repaired. No normalization was applied to final outputs.

### Figure 2 and other material

Figure 2 (p.377/PDF p.13) shows boxes against a trophic-level axis, not numeric per-group TL. Box heights vary with biomass and no unique point for digitizing TL is specified. TL.xlsx therefore remains blank for all 40 groups; no spurious precision is assigned from a schematic. Figure 2's Lutianidae B=0.015 differs from Table 1's 0.016; Table 1 is retained as the primary parameter table. Table 8 gives aggregate biomass per integer trophic level, not group TL. Figures 3-4 are mixed impacts and Ecosim fits. Appendix A (p.386) contains 1998 caudal-fin/aspect-ratio inputs, not another model.

## Biomass accumulation

Absolute BA is explicitly tabulated for every group in Table 1; {len(nonzero)} entries are nonzero and {40-len(nonzero)} are stated zero. Nonzero entries (group: value): {', '.join(str(g['n'])+': '+g['ba'] for g in nonzero)}. Positive Sillago 0.086 and Saurida 0.012; negative values including Cephalopod -0.1 and Rays -0.01 were visually checked. BA rate stays blank in the import file; the database alone derives BA/B and the workbook labels that derived form. The table's zeros are paper-stated, even though they coincide with the EwE default. General mass balance does not imply BA=0, and the nonzero terms disprove a blanket steady-state assumption. Whole-chapter accumulation search and Figure 4 were reviewed; no figure-derived BA replaces Table 1.

## Values from prose

No numerical import parameter was added from prose. The model survey/swept-area calculation uses A=101384 km² (p.367), whereas p.366 reports the whole Gulf seabed area of 304000 km². Neither is a reported habitat-area fraction; neither was used to rescale already normalized table biomass/catch. Mean habitat temperature is 29°C; primary-production carbon-to-wet-weight factor 7.47 is described on p.374, but Table 1 already gives the model parameters, so it was not applied again. The printed conversion expression on p.374 was not used to create new rates. Trashfish is defined in the p.366 footnote and includes low-value and juvenile/undersized fish, not discarded fish.

## Conventions applied

- Only format-level conventions: full group-row spine, comma removal from group 20, thousands-space removal from detritus biomass, and catch placed in Landings without inventing a discard split.
- The bundled writer emits Import=0 and (1 - Sum)=0 as required by its export format even though no diet import is stated. These are explicit file-format conventions, not author values. Final DB diet_imp stays -9999, and the round-trip workbook leaves Import blank to preserve source silence.
- No GS, habitat-area fraction, detritus fate, missing catch, missing diet or missing TL default is filled. No zooplankton convention is applied to the pooled Zooplankton group. No diet normalization.

## Deliberate blanks

The complete 22-page source bundle, all captions/footnotes, methods, results, figures and Appendix A were searched, then targeted searches revisited the groups/fields still missing. Assimilation/GS and detritus routing are not stated. GS remains blank for all groups (structurally inapplicable for producers/detritus); EwE may supply GS=0.2 for consumers at import, but this is not the author's input. Habitat area is unreported (software default 1); detritus import/export/fate unreported (unassigned fate can be exported by EwE). Discards are not separated (software default 0). No catch rows are supplied for groups 26,27,28,31,32,33,34,39,40 (software default 0). No migration, other mortality, total mortality or numerical group TL is reported. Q/B dashes, and P/Q dashes for Mammals/producers/detritus, are retained. The final database uses -9999 for unknowns.

## Unresolved and flagged

The published diet has missing consumers, zero-only columns and substantial column-sum contradictions. Reported catches also conflict: Table 2 total 2.433 for 1973 vs Ecosim fitted 1973 Table 10 total 1.454 (p.381); p.379 explicitly identifies the latter as time-series simulation results. Table 10 has no group allocation. Tables 1-3 are extracted together; no attempt is made to infer a revised group-by-fleet catch set from the totals. Table 4 prose says purse seines but the actual third header says Pushnet; header retained as contextual evidence and no numerical transformation depends on it.

The stock converter silently normalizes diets, discards stated P/Q, classifies blank-Q/B/empty-diet consumers as producers, and substitutes several zero/one defaults. Its initial outputs are archived only in work/bundled_*. The local adapt_database.py restores exact CSV diet values including zeros, carries P/Q in supported ge/ge_input, establishes pp from the group list, restores unknown sentinels, and rebuilds the final workbook. The log's final adapter entry supersedes earlier raw messages. source_parameters.json preserves six-fleet catch detail that the core database schema otherwise collapses into export totals. This is documented compatibility work, not a source correction.

## Validation

Bundled validate.py: 15 errors (the confirmed source diet sums) and 52 warnings (40 unknown detritus fates; 10 empty diets; one GS summary; one TL summary). CSV structures, numbering, source row counts, numeric precision, CRLF and lack of quotes are valid. All 40 detritus-fate rows are blank, not normalized. The eight required files, model.json, database JSON and reconstructed workbook exist.

Bundled massbalance_check.py: 1 error, 44 warnings, 6 notes. It ignores usable source P/Q when computing missing Q/B and undercounts predation; it also suggests BA for printed zeros, which must not be adopted. The raw database converter reported BALANCED after normalizing diets and omitting consumption; this is invalid evidence for the final transcription. The final analysis below uses source P/Q internally and unnormalized source diets. ROUNDTRIP_CHECK.md confirms 2280 independently reopened source/JSON/workbook checks. No native EwE import/load test was run, and the package is explicitly not presented as a complete loadable model.

'''
(M/'REPORT.md').write_text(report+mass.replace('# Mass balance','## Mass balance',1),encoding='utf-8')
(M/'source_cells.json').write_text(json.dumps(cells,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'MASTER_INDEX.md').write_text('''# GOT-2003 extraction index

Source: Vibunpant et al. (2003), Gulf of Thailand, supplied chapter pp.365-386. Source transcription is complete; model reconstruction is partial because essential information is missing or inconsistent in the publication.

| # | Model | Year | LME | Groups | Fleets | Status | Mass balance | Notes |
|---|---|---|---|---|---|---|---|---|
| 35_1 | [Gulf of Thailand](35_1_Gulf_of_Thailand_1973/REPORT.md) | 1973 | 35 | 40 | 6 | partial | NOT BALANCED | 15 malformed diet columns; 10 consumers without positive diets; unknown GS/routing/TL; explicit BA retained; fleet catch conflicts; exact source values preserved |

One distinct static model. 1973-1993 Ecosim fits, 1993 fishery state and 2000 management/optimization outputs are not separate static Ecopath parameter sets. Appendix A is 1998 aspect-ratio evidence, not a static model.

All outputs are under this extracted directory. Original sources were unchanged. Work files include original/rotated word boxes and rendered visual checks, extraction scripts, prose sweeps and superseded bundled converter outputs.
''',encoding='utf-8')
(WORK/'final_massbalance_values.json').write_text(json.dumps(res,default=str,indent=2),encoding='utf-8')
print('Nonzero BA',len(nonzero),'derived QB',len(derived),'missing diets',missing)
print('Over EE',[(r['n'],str(r['EE_calc'])) for r in over]);print('Gaps',len(gaps),'max',maximum)
