# LME037 missing diet source found

The missing baseline diet matrix is available in **Bacalso, Romagnoni and Wolff (2023), Supplementary Table S2, printed pages 7–8**. The official Frontiers Figshare attachment has been downloaded and verified. Its **33 prey rows × 30 consumer columns (990 cells, 297 nonzero entries)** match the model group structure used by Bacalso et al. (2026).

- [Official supplement record](https://frontiersin.figshare.com/articles/dataset/21959183)
- [Direct Word download](https://ndownloader.figshare.com/files/38954888)
- [2023 article and methods](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2023.1099400/full)
- [2026 institutional article record](https://cris.leibniz-zmt.de/id/eprint/6047/)

The recovered source is saved under `papers/LME037-Bacalso-2026/recovered_sources_20260928/Bacalso2023_DataSheet_1.docx`. The file is 249,874 bytes; its MD5 equals the publisher's recorded checksum `764703bffdcac6cd97c0cb2ffccf33f3`. SHA-256: `9f199e51199cd890c9f19b1b2b4310b3fb268a98152eaf361fc1f1a048605e3c`. A download manifest and the full publisher Figshare metadata accompany it. The 2023 main PDF and publisher XML are also retained.

## Why it belongs to this baseline

The 2026 main paper, section 2.2, PDF pages 3–4 explicitly reuses the Visayan Sea baseline of Bacalso et al. (2023b). Its 33 groups consist of 30 consumers, two producers and one detritus pool. The 2023 source describes a 1996–1997 survey baseline; the 2026 output table labels it 1997. A 1997–1998 phrase in the 2026 methods conflicts with that lineage and is retained as a date caveat.

A coordinate-based comparison of the 2026 Table 1 baseline against 2023 Table 3 checked **all 191 populated TL/B/PB/QB/EE/PQ cells**. Every value agrees at the 2026 printed precision after accounting for the stated habitat fraction of 0.2 for reef groups 16–20. For example, 2023 group 16 habitat biomass 1.653 becomes 0.3306 over the full model area, printed as 0.331 in 2026. The comparison and PDF bounding boxes are in `BASELINE_PARAMETER_CROSSWALK.json`; the page image is retained.

Table S2 orientation is prey in rows, predators in columns. Both continuation blocks preserve source group numbers 1–33 and consumer columns 1–30. The complete matrix is directly tabulated, so it need not be recreated from species-level stomach-content studies or borrowed from a different Philippine model. Table S3, printed pages 9–11, also provides 34-fleet catches and per-group totals. Individual `0.000*` fleet cells mean values below 0.001; they must not be silently assigned exact zero. Published group totals are available for a total-fishery representation.

## Remaining extraction caveats

The original diet proportions have been retained. Five consumer columns differ from one: group 1 = 1.001; group 2 = 0.9996; group 5 = 1.001; group 13 = 1.001; group 16 = 1.002. These are consistent with rounding. No normalization has been applied to the source matrix. A diagnostic admission failure from rounding must be distinguished from missing diets or a balance failure.

The source supports reconstruction of the **1997 baseline**. The **2018 endpoint is an Ecosim simulation output**, and its changed trophic levels already indicate changed feeding relationships. The retrieved 1997 matrix is not evidence of the 2018 realized diets. A 2018 diet/flow export, biomass-accumulation values and matching catches/native model would be needed for a defensible separate 2018 reconstruction. The table's censored 2018 biomass for Jacks/barracudas (`<0.001`) is an additional precision gap.

The Visayan Sea is a local model within the LME037 candidate assignment, not a whole-Sulu–Celebes model. No unsupported coverage percentage or spatial extrapolation has been introduced. No model has been selected, no regional PPR has been published, and no shared workbook has been changed.

## Search record

Checked the 2026 publisher/institutional record and its existing 26-page supplement (sources of diets, not numerical matrix), the explicitly cited 2023 Frontiers precursor, its publisher XML, official Figshare dataset, ZMT publication record and thesis/project listings. Searches did not establish a public matching native EwE database or a downloadable thesis containing a more recent matrix. The 2007 Danajon thesis and the 2014/2016 Danajon papers concern different systems and were not substituted. The initial Frontiers attachment control did not expose its file; the official Figshare API query by exact parent DOI recovered the attachment, verified by its `IsSupplementTo` metadata. This is a successful source recovery, not a claim that no other native model exists.
