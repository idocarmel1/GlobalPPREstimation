# Ecopath extraction results

All five requested source folders were processed. Eight distinct model versions have separate output directories. Every model includes the eight import files, extraction and database JSON, reconstructed workbook, provenance report, validation and mass-balance findings. Original source files were retained unchanged.

**All eight are partial reconstructions, not certified import-ready models.** Published inconsistencies and unreported parameters were retained rather than repaired by assumption. The work has extracted the available evidence; additional author data or correction decisions are needed to establish runnable balanced models.

| Model number | Model and report | Reference year | Groups | Final JSON | Main limitation |
|---|---|---|---:|---|---|
| 13_1 | [Patagonia base](13_1_Chilean_Patagonia_1980/REPORT.md) | 1980 | 15 | [JSON](13_1_Chilean_Patagonia_1980/13_Humboldt_Current_13_1_Chilean_Patagonia_(1980).json) | Skates EE mismatch; missing GS, BA, detritus routing and fleet splits. |
| 13_2 | [Northern Humboldt resolved](../../HUM-2018/extracted/13_2_Northern_Humboldt_Current_1995-1998/REPORT.md) | 1995-1998 | 39 | [JSON](../../HUM-2018/extracted/13_2_Northern_Humboldt_Current_1995-1998/13_Humboldt_Current_13_2_Northern_Humboldt_Current_(1995-1998).json) | Jellyfish diet 1.045; small-jellyfish energy deficit; sardine prose/table conflict. |
| 13_3 | [Northern Humboldt aggregated](../../HUM-2018/extracted/13_3_Northern_Humboldt_Current_1995-1998/REPORT.md) | 1995-1998 | 24 | [JSON](../../HUM-2018/extracted/13_3_Northern_Humboldt_Current_1995-1998/13_Humboldt_Current_13_3_Northern_Humboldt_Current_(1995-1998).json) | Same jellyfish defects; rounded zero biomass; missing aggregated detritus routing. |
| 27_1 | [Mauritanian shelf Base](../../../LME_027/CAN-2014/extracted/27_1_Banc_d_Arguin_and_Mauritanian_Shelf_1991/REPORT.md) | 1991 | 51 | [JSON](../../../LME_027/CAN-2014/extracted/27_1_Banc_d_Arguin_and_Mauritanian_Shelf_1991/27_Canary_Current_27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991).json) | Published grouper diet 2.2006; bird diet 0.980331; missing basic inputs. |
| 27_2 | [Mauritanian shelf M30](../../../LME_027/CAN-2014/extracted/27_2_Banc_d_Arguin_and_Mauritanian_Shelf_1991/REPORT.md) | 1991 | 51 | [JSON](../../../LME_027/CAN-2014/extracted/27_2_Banc_d_Arguin_and_Mauritanian_Shelf_1991/27_Canary_Current_27_2_Banc_d_Arguin_and_Mauritanian_Shelf_(1991).json) | Incomplete changed diets and rounded parameter values, plus base-source defects. |
| 27_3 | [Mauritanian shelf P30](../../../LME_027/CAN-2014/extracted/27_3_Banc_d_Arguin_and_Mauritanian_Shelf_1991/REPORT.md) | 1991 | 51 | [JSON](../../../LME_027/CAN-2014/extracted/27_3_Banc_d_Arguin_and_Mauritanian_Shelf_1991/27_Canary_Current_27_3_Banc_d_Arguin_and_Mauritanian_Shelf_(1991).json) | Incomplete changed diets and rounded parameter values, plus base-source defects. |
| HS_077_1 | [Eastern tropical Pacific ETP7](../../../HS_077/ETP-2003/extracted/HS_077_1_Eastern_tropical_Pacific_1993-1997/REPORT.md) | 1993-1997 | 39 | [JSON](../../../HS_077/ETP-2003/extracted/HS_077_1_Eastern_tropical_Pacific_1993-1997/HS_077_Pacific_Eastern_Central_high_seas_HS_077_1_Eastern_tropical_Pacific_(1993-1997).json) | Nine published diet-sum errors; missing BA and detritus information. |
| 35_1 | [Gulf of Thailand](../../../LME_035/GOT-2003/extracted/35_1_Gulf_of_Thailand_1973/REPORT.md) | 1973 | 40 | [JSON](../../../LME_035/GOT-2003/extracted/35_1_Gulf_of_Thailand_1973/35_Gulf_of_Thailand_35_1_Gulf_of_Thailand_(1973).json) | Fifteen malformed diet columns and ten consumers without positive diets. |

## Important distinctions

- Northern Humboldt uses 1995–1998 source inputs; the archive metadata says 1995–2004. The two resolutions are separate models.
- Canary models use 1991, not the catalog’s 2007–2009. Base, M30 and P30 have separate parameterizations; the latter two have incomplete published diets.
- ETP7 is the final model. Its EE arithmetic reconciles within 0.014, but its malformed diets still prevent import-ready status. The explicitly unbalanced ETP1 draft was excluded.
- Thailand includes 14 nonzero biomass-accumulation values and 26 stated zeros. These were preserved.
- Unknown values remain blank/-9999. Local adapters undo the bundled converter’s normalization and default insertion, retaining original diet sums and stated P/Q. They also preserve the explicit model_number in final JSON metadata.

Final integration verified all required files, eight unique identifiers, matching metadata and 11,094 cross-file numeric checks. The per-model round-trip reports contain more detailed checks. Source inconsistencies are expected validation failures and were not suppressed.

Article-specific MASTER_INDEX.md files remain in each extracted directory. This cross-folder index is stored with the first requested article so every output stays within an article’s extracted directory.
