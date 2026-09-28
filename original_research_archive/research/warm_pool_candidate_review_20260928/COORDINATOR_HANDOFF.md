# Pacific papers: end-to-end assignment

User authorization: compare Griffiths et al. (2019), *Just a FAD?*, and Allain et al. (2021), *Tuna fisheries bycatch and climate change in the western tropical Pacific Ocean*, against HS_071 and EEZ_941. Add each paper to its better-fitting region, extract every source-supported model, run direct SPPR diagnostics, and produce a report that supports a paper choice for each region. No model selection is authorized. User asks a new subagent to carry this from start to finish and recurring progress updates.

## Work already completed

- Main paper retrieval and supplementary source discovery are underway in `Griffiths2019/` and `Allain2021/` below this directory. Preserve files and any agent handoff.
- `spatial_overlap.py` and `SPATIAL_OVERLAP.json` calculate intersection with actual stored regional polygons using WGS84 geodesic areas and densified geographic segments. A finer densification changes intersection areas by under 0.00001 percent.
- Griffiths 2019 explicitly models 140–180 E, 15 S–10 N. Its stated gross area 12,203,000 km² agrees with calculated 12,202,880 km². Coverage is 99.71577% of EEZ_941 and 29.09639% of HS_071. EEZ_941 is the better home when judging completeness of target-region coverage. Only 9.07086% of its reported 11,543,000 km² ocean domain lies in EEZ_941; it is a broad mixed-jurisdiction pelagic proxy, not an EEZ-specific model. HS_071 intersection is larger in absolute area (1,510,912 vs 1,047,050 km²), which does not mean better coverage of HS_071.
- WCP2007 domain 110–180 E, 15 S–15 N covers 57.57808% of HS_071 and 99.71577% of EEZ_941. It is a distinct 31-group mixed-period model, not the 2019 baseline.
- The 2021 bounds still need source verification; do not silently reuse the 2019 rectangle.

## Primary sources

- Griffiths 2019 DOI: https://doi.org/10.1111/fog.12389
- Full author PDF: https://www.bmis-bycatch.org/system/files/zotero_attachments/library_1/MQDAAXEY%20-%20Griffiths%20et%20al.%20-%202019%20-%20Just%20a%20FAD%20Ecosystem%20impacts%20of%20tuna%20purse-seine%20.pdf
- 2019 model: baseline 2005, 46 groups (44 living, detritus, fishery discards); main Table 1 and Appendix S1 Tables S1/S2. Do not conflate with Allain 2015's 44-group model. Migration explicitly zero; detritus/discard routing must be sourced rather than invented.
- Allain 2021 official listing: https://meetings.wcpfc.int/node/12403 ; PDF https://meetings.wcpfc.int/file/8826/download . Web tool previously timed out. It describes updated 2019 lineage but numerical equivalence is not established.

## Reporting and extraction contract

Read project README, prepare-ecopath-model skill, ecopath-extraction workflow and taxonomy references. Source-faithful eight imports, extraction JSON and canonical database JSON, taxonomy, visual/page/cell evidence, reconstruction validation and source mass balance are required when inputs support them. Preserve unknowns and published precision. Report blockers explicitly when full data are unavailable; never produce fabricated successful extraction.

SPPR report must contain only full direct `PPRCalculator.diagnose_sppr(short=False, flat=False)` returns for GE, TE, and With Egestion; exclude global. Put extraction assumptions, defaults and source limitations in a separate report. Keep unapproved parameter/routing fixes and pooling out of canonical models. Full model selection remains user's decision. If none can run, explain and consult the user after completing independent work.

WCP2007 benchmark and failure investigation are complete at `regions/EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)/`. All three diagnostics FAIL because juvenile yellowfin and bigeye production residuals explain the PP-budget gaps; exact native catch/stanza discrepancy remains unresolved. Refer to its balance_investigation/BALANCE_CAUSE_REPORT.md instead of rerunning.

## Central registration caution

No agent currently owns the central writing window. Parent may grant the new coordinator exclusive ownership. Live Project.xlsx has an unresolved empty duplicate Models row42 from LME049 registration; a narrow correction is staged. See `regions/LME_049/models/extraction_review_20260928/CENTRAL_SELECTION_BLOCKED.json`. Windows denied atomic replacement, lock holder unknown. Do not overwrite a changed workbook with the staged old version; compare fresh hashes and rebuild narrow fix if necessary. Preserve all other model preferences, metadata, native tables, annual data and rankings. Do not force-close apps or bypass a real lock. Parent coordinates this repair; prepare registration proposals if blocked.

No exact production model selection or annual PPR publishing is authorized for either Pacific paper. Do not alter unrelated region workbooks. Rebuild/verify the map only after safe supported metadata integration.

## User note for later selection — 2026-09-28

EEZ_598 (Papua New Guinea) is also linked to WCP-2007 (Allain et al., 2007). The parent verified that `regions/EEZ_598/papers/WCP-2007` exists. The user requests preserving this shared-paper relationship for the later model-selection review of **HS_071, EEZ_941, and EEZ_598 together**. Include this relationship in the final comparison and subsequent selection discussions. Each region still needs its own spatial/ecological applicability assessment; a shared article does not establish an identical regional fit. This instruction records future review context, not a model choice or authorization for a new extraction. Existing WCP2007 extraction and diagnostic evidence can be referenced without duplicating the extraction.
