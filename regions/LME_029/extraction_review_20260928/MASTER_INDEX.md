# LME029 BEN-2020 extraction and diagnostics

One available candidate: **BEN2020_Southern_Benguela_1978**, 49 groups and31 fleets. The paper was published in2020; its extractable Ecopath baseline is1978, with Ecosim fitting through2015. No model has been selected.

| Model | GE | TE | With Egestion | Status |
|---|---|---|---|---|
| BEN2020_Southern_Benguela_1978, documented diagnostic completion | FAIL | FAIL | FAIL | Full source transcription retained; native multistanza and accumulation interpretation unresolved |

- [Extraction/source review](../models/BEN2020_Southern_Benguela_1978/extracted_tables/REPORT.md)
- [Only the full direct SPPR method returns](../models/BEN2020_Southern_Benguela_1978/diagnostics/DIRECT_SPPR_REPORT.md)
- [Canonical source model](../models/BEN2020_Southern_Benguela_1978/model.json)
- [Model structure and taxonomy](../models/BEN2020_Southern_Benguela_1978/extracted_tables/MODEL_PROFILE.md)
- [Staging transformations](../models/BEN2020_Southern_Benguela_1978/diagnostics/staging_transformations.json)
- [Verification](VERIFICATION.json)
- [Compact results](results_record.json)
- [Central metadata proposal](central_metadata_proposal.json)

The immediate reason for all three FAIL statuses is a production-budget discrepancy of about24% under the reported sardine stock accumulation term and current standalone group equations. TE also fails its PP budget and has near-singular bird transfer efficiencies. No correction was adopted to hide these results. The appropriate next evidence is the native EwE file or clarification of the shared stock BA and mortality/production conventions.
