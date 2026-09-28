# SOJ-2023 source extraction review

**USER-PREFERRED/SPECIFIED SOURCE:** Impacts of regime shift on the fishery ecosystem in the coastal area of Kyoto prefecture, Sea of Japan, assessed using the Ecopath model (2023); reason: **only available paper**.

Two tabulated reconstructions are retained. Neither is adopted as the original year-specific model. The one published diet matrix is captioned for both years, but the Results explicitly state that sardine was the main prey in 1985 and anchovy in 2013. Distinct original year-specific diets cannot be recovered from these files without further author evidence.

The model area is 2,230 km² of coastal Kyoto, from the coastline to 240 m depth. This is partial spatial coverage of LME_050. The inherited 1% estimate was not verified and is not used.

The local PDF is the complete publisher article, not a thesis chapter. Its first page verifies the five authors, DOI, receipt/acceptance dates, and online publication on 12 June 2023. The publisher landing page was retrieved successfully; its sole DOCX supplement was re-downloaded and exactly matches the retained SHA-256. No native EwE model is linked there.

## Model evidence
- [50_501985_Coastal_Kyoto_Inoue_(1985)](../50_501985_Coastal_Kyoto_Inoue_(1985)/REPORT.md): 40 groups; source admission unresolved; all requested diagnostic calls returned WARN.
- [50_502013_Coastal_Kyoto_Inoue_(2013)](../50_502013_Coastal_Kyoto_Inoue_(2013)/REPORT.md): 40 groups; source admission unresolved; all requested diagnostic calls returned WARN.

## Separate diagnostic report

[Direct GE / TE / With Egestion diagnostics](SPPR_DIAGNOSTICS_REPORT.md). Raw method returns are retained in DIAGNOSE_SPPR_RESULTS.json.

## Registration and selection

Existing paper row SOJ-2023__LME_050 was found; no existing LME_050 model rows were found. Reuse that paper row and add the two local model IDs. Preserve existing scores, rankings, filter tables and preferences of other regions. The central proposal is unregistered until the parent grants a serialized Project.xlsx write slot. Regional Overview remains unchanged and exact model selection remains pending.
