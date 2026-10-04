"""Create the requested conversation summary from verified final selections."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent
v=json.loads((P/'SELECTION_VERIFICATION.json').read_text(encoding='utf-8'))
assert v['status']=='PASS' and v['selected_count']==23
STATUS={
'LME_036':('WARN / WARN / OK','Existing selected 2000s model retained; saved regional results retained.'),
'LME_032':('OK / WARN / OK','Existing Karnataka 2000 selection and saved regional results retained.'),
'LME_034':('WARN / WARN / OK','Existing Bay of Bengal 1978 selection and saved results retained.'),
'LME_047':('WARN / WARN / WARN','Existing East China Sea 2018 selection retained; source catch is zero, distinct from regional catch used for PPR.'),
'LME_052':('WARN / FAIL / WARN','Existing northeast Okhotsk 1980 selection retained. GE/Egestion calculate; TE fails.'),
'LME_013':('WARN / WARN / WARN','Changed to Chilean Patagonia 1980. Old Northern Humboldt 1995–1998 fails all three. Spatial suitability remains a concern; new regional matching/PPR pending.'),
'LME_027':('WARN / WARN / WARN','Changed to Northwest Africa 1987. Old Banc d Arguin/Mauritanian Shelf 1991 fails all three. New regional matching/PPR pending.'),
'LME_028':('OK / WARN / OK','Existing Guinea 1998 selection and saved results retained.'),
'HS_077':('OK / FAIL / OK','Existing eastern tropical Pacific 1993–1997 selection retained. TE fails; GE/Egestion available.'),
'LME_035':('WARN / WARN / WARN','Existing Gulf of Thailand 1963 selection and saved results retained.'),
'LME_022':('OK / FAIL / OK','Previously preferred East Coast of Scotland 1991–1995 is now formally selected. Regional matching/PPR pending. EcoBase457 flow-balance debugging retained.'),
'LME_049':('OK / FAIL / OK','Watari 2013 detritus-pooled experiment retained as selected. Source routing unavailable; pooling and defaults documented. TE investigation deferred; no adopted annual model PPR. Only 7/253 taxa in preliminary membership preparation.'),
'LME_038':('OK / WARN / OK','Buchary Java Sea selected after diet normalization and BA completion: best available model. Derived and source versions retained. Partial annual calculations available; approximately 96.7% catch coverage reported.'),
'LME_048':('— / — / —','No extracted model and deliberately unselected. Candidate papers available.'),
'EEZ_941':('WARN / WARN / WARN','WCP2007 option1 selected. Juvenile-tuna parameter changes documented; shared model diagnostics completed. Regional matching/annual integration pending. Griffiths variants retained for investigation.'),
'EEZ_938':('— / — / —','No extracted model and deliberately unselected. EKAS-2005 registered.'),
'HS_071':('WARN / WARN / WARN','WCP2007 option1 selected as warm-pool proxy. Regional integration pending; study rectangle overlaps about 57.58% of region. Griffiths retained for investigation.'),
'LME_050':('WARN / WARN / WARN','2013 Coastal Kyoto selected because newer; 1985 retained as a good comparison. Partial annual PPR: 19/253 taxa, 25.05% of 2019 catch. Proposed aliases not yet applied.'),
'LME_014':('WARN / WARN / WARN','Native Falkland Shelf 2020 selected. Partial annual PPR validated; approximately 65.31% of 2019 catch. Printed-table reconstruction blocked; Ocampo-Reinaldo model fails.'),
'EEZ_598':('WARN / WARN / WARN','WCP2007 option1 selected, as for the other Pacific regions. Regional matching/annual integration pending. Griffiths source and pooled models retained for investigation.'),
'LME_003':('WARN / WARN / WARN','CAL2016 California Current 2000–2014 selected. Author-equation B/EE runtime completion documented. Partial annual PPR available: 147/349 taxa, 76.51% of 2019 catch.'),
'LME_024':('FAIL* / unsupported* / FAIL*','Extracted Celtic Sea 1985 selected despite failure. Original canonical source remains blocked. Authorized normalized-diet/routing adapter yields failing GE/Egestion; TE has no supported return equation. No annual PPR.'),
'LME_026':('NOT_RUN / NOT_RUN / NOT_RUN','Mediterranean 1995 selected despite missing Discards/Detritus routing. Fin-whale catch/production discrepancy retained. No annual PPR.'),
'LME_029':('FAIL / FAIL / FAIL','Southern Benguela 1978 selected despite failed diagnostics. Production residual reaches 23.96%; BA/stanza and TE issues unresolved. No annual PPR.'),
'LME_037':('WARN* / WARN* / WARN*','Visayan Sea 1997 baseline selected under all-top25 instruction. Diagnostics require audited runtime defaults and diet tolerance. Geographic fit needs review; 2018 endpoint not reconstructable. Regional integration pending.'),
}
text='''# Conversation summary and regional status — 28 September 2026

**23 of the atlas top 25 now have exactly one selected model. LME_048 and EEZ_938 are the only unselected regions.** Selection is the user's research choice, not evidence that a calculation passed. Blocked and failing models retain those statuses and have no new numerical regional results.

The selection update changed seven regions: LME013, LME027, LME022, LME024, LME026, LME029 and LME037. Existing model-dependent regional results for changed selections were archived and cleared. Catch, classic PPR and NPP were preserved. Source model JSONs were not changed, and no scientific diagnostics were rerun for this update.

## What was done in this conversation

- **North Sea:** extracted the historical Scotland models and North Sea parameterisation report, with a separate EcoBase457 variant. Compared full SPPR diagnostics. Recorded the user's preference for East Coast of Scotland 1991–1995 because it had the fewest failures, now promoted to selection. Kept the EcoBase457 flow-balance failure as a deferred debugging question.
- **Kuroshio:** extracted Watari2019 and Chen2025. Original models were unsuitable for reliable use. Tested user-authorized pooling of Watari's three detritus pools, retaining its three phytoplankton regions; selected the 2013 pooled experiment. Documented missing routing and all transformations, and retained the request to investigate TE failure.
- **Indonesian Sea:** extracted Buchary and Nurhakim. Selected Buchary's Java Sea model after explicitly authorized diet normalization and BA completion because it was the best available model. Nurhakim remains a problematic comparison candidate.
- **Pacific:** extracted WCP2007 and investigated why juvenile bigeye/yellowfin parameters could not support assigned removals. Developed the explicitly documented option1 parameter adjustment preserving other-mortality flows. Investigated Griffiths2019 and Allain2021, compared geographic fit for HS071, EEZ941 and EEZ598, recovered the new Griffiths Word data, and re-extracted. After online routing checks, tested authorized Griffiths detritus pooling. Griffiths still failed all three diagnostics; Allain2021 did not provide a complete standalone numeric baseline. Selected WCP option1 for all three regions and copied/registered Griffiths sources and models for later investigation. The completed comparison monitor was paused.
- **Sea of Japan:** extracted 1985 and 2013 and compared group GE coefficients and catches. The approximately 5.22-fold higher 1985 catch-weighted GE PPR was largely explained by approximately 5.367-fold larger catch, rather than uniformly worse coefficients. Selected 2013 because newer, retained 1985 for comparison. Investigated poor taxon matching and prepared, but did not apply, evidence-backed alias improvements.
- **Patagonian Shelf:** extracted native Falkland Shelf and printed-table variants, plus Ocampo-Reinaldo with the added diet supplement. Selected the non-failing native 2020 model and prepared partial regional calculations.
- **California Current:** used CAL2016 and its ZIP supplement; extracted the 93-group model, documented runtime completions, diagnosed it and prepared selected partial regional calculations.
- **Celtic Sea:** used Hernvann2020 and Word data. Located diet rounding, BA and routing issues in sources. After user authorization, normalized diets and tested explicit discard-return routing. GE/Egestion converged but failed balance; TE return accounting was unsupported. Preserved printed accumulation and the source model. Now selected despite failure.
- **Mediterranean:** used MED2022 with both XLSX and Word supplements; extracted 71 groups and 37 fleets. Missing two-pool routing prevents construction; additional conditional fin-whale source conflict documented. Now selected despite NOT_RUN status.
- **Benguela:** extracted BEN2020's 49-group Southern Benguela 1978 model. All three diagnostics fail; BA, multistanza and TE limitations documented. Now selected despite failure.
- **Sulu-Celebes:** recovered the official predecessor supplement supplying the missing 1997 diets and catches. Verified model lineage and habitat-area conversion. Extracted the 33-group baseline and ran the three conditional diagnostics. The 2018 simulation endpoint lacks a complete compatible input set. The available 1997 baseline is now selected under the user's top25 instruction.
- **Project coordination:** registered model/paper evidence, preserved selection rationale and deferred investigations, consolidated regional workbooks and refreshed the atlas. Audited all top25 regions. Changed Humboldt and Canary selections to their existing alternatives with WARN diagnostics. Requested firsthand retrospectives from three extraction agents and additional retained-evidence reviews of the nine extractions named by the user. Prepared consolidated skill revision proposals without editing the skills.

## All 25 regions

Diagnostic order is **GE / TE / With Egestion**. Older regions use retained diagnostics, not a new run. WARN is not proof of strict balance or full regional suitability. An asterisk marks a conditional runtime or experimental adapter. Exact model identities are listed after the compact status table.

| Atlas rank | Region | Diagnostics | Current status and remaining work |
|---:|---|---|---|
'''
for r in v['top25']:
    uid=r['unit_id'];status,note=STATUS[uid]
    text+=f"| {r['atlas_region_rank']} | {uid} — {r['name']} | {status} | {note} |\n"
text+='\n## Exact selected model identities\n\n| Region | Selected model |\n|---|---|\n'
for r in v['top25']:text+=f"| {r['unit_id']} | `{r['selected_model_id']}` |\n" if r.get('selected_model_id') else f"| {r['unit_id']} | None — explicitly excluded |\n"
text+='''
## Remaining work

- Missing model extractions: Yellow Sea LME048 and Indonesia Indian Ocean EEZ938.
- Blocked/failing selected models: Mediterranean routing, Celtic Sea budgets/return equations, Benguela source/stanza issues. Selection has not repaired these issues.
- Deferred diagnostic investigations: Watari TE, Griffiths source and pooled variants, EcoBase457 flow balance. North Sea, Okhotsk and eastern tropical Pacific also retain TE failures.
- Regional integration: changed selections and the three Pacific applications need matching/calculation work before new regional annual model PPR can be published. Conditional runtime assumptions must remain explicit for North Sea and Sulu-Celebes.
- Taxonomy: the Sea of Japan alias proposal would increase resolved taxa from 19 to 22 and 2019 catch coverage from 25.05% to approximately 29.20%, but major group gaps remain. It has not been applied. Kuroshio matching also remains sparse.
- Geographic fit: numerical health does not establish suitability. In particular, Chilean Patagonia as the Humboldt substitute and Visayan Sea as the Sulu-Celebes substitute need geographic review. Do not confuse study-area overlap with catch coverage.
- Skill maintenance: review the proposed improvements in [PIPELINE_LESSONS.md](PIPELINE_LESSONS.md). No skill edits were made.

## Verification and evidence

The authoritative selection is in each regional Overview; Project.xlsx derives selection flags from those records. [SELECTION_VERIFICATION.json](SELECTION_VERIFICATION.json) records all 25 registry rows, seven decisions, exact model hashes, preserved unrelated records and the verified 23/25 selection count. Earlier region-specific extraction and diagnostic reports remain in their model folders. The current task changed selection metadata and invalidated obsolete model-dependent results; it did not fabricate missing parameters or recalculate failed models.
'''
(P/'CONVERSATION_SUMMARY.md').write_text(text,encoding='utf-8')
print('Conversation summary written for all 25 regions.')
