# Corrales Israeli continental shelf 2008–2012

Corrales et al. (2017), Journal of Marine Systems 170:88–102, doi:10.1016/j.jmarsys.2017.02.004. The supplied Corrales-2010 alias is retained. The model describes 3,725 km² of shelf at 0–200 m depth, rather than the entire Israeli Mediterranean EEZ. There are 41 ecological groups; older source IDs 24 and 35 are absent and the import crosswalk retains the original IDs.

Article Table 1 (PDF 4 / printed 91) supplies B, P/B, Q/B, EE, P/Q, landings and discards for both periods. Table 2 (PDF 6 / printed 93) supplies TL, fishing mortality F, predation mortality M2, other mortality, F/Z and detritus flow. Table 3 (PDF 8 / printed 95) and all eight supplementary tables are retained as companions. Bold initial-input markers and author-estimated roles remain explicit. Supplement section 1 supplies group membership; section 5 supplies the two continued diet matrices and their totals. The gray status comes from the source cell shading, not inferred diet magnitudes.

Ordinary blank diet cells are assumed zero only at runtime. Gray cells mean less than 0.01; source models preserve their -9999 missing marker. There are 99 such cells in this period. Published known consumer diet subtotals are 0.98–1.03 in 1990–1994 and 0.97–1.01 in 2008–2012. Source values were not normalized; runtime normalization is recorded separately. Seabird biomass printed 0.00 loses biological precision. Biomass accumulation, GS, habitat fraction, native detritus fate and several catch components are unpublished, not observed zero. Biomass values are explicitly per whole model area.

Known rounded landings sum to 0.79 / 0.65, compared with published aggregate landings 0.80 / 0.64; known discards sum to 0.10 / 0.29 compared with aggregate 0.14 / 0.29 t km⁻² yr⁻¹. The source tables remain unchanged. These differences do not justify distributing an invented residual among groups. The original loader's incomplete aggregate-catch default can omit known partial components; this is distinguished from missing source catch.

The label Mullets means red mullets Mullus barbatus and M. surmuletus in the author definitions. Mugilidae grey mullets instead occur in Small native dem. fishes. Several author spellings are retained verbatim and crosswalks are separately evidenced.

This exact candidate has direct method outcomes {"GE": "FAIL", "TE": "FAIL", "With Egestion": "FAIL"}. A source checklist or rounded equation check does not establish balance of the author's original native model. Current import/JSON/reconstructed-workbook cells and missing masks were checked with the maintained domain routine; deliberate fitted-gray departures are tested separately in CURRENT_VARIANT_CHECK.json. These reconstruction checks establish value retention, not ecological validity.

Natural mortality and egestion are routed to natural Detritus under the researcher-authorized fate assumption. Discards remains a separate pool; explicit fishery-return amounts are retained as a donor ledger, but the current calculator omits recipient fleet returns. Runtime GS is 0.2, living accumulation is zero by default, detritus EE becomes one, and detritus accumulation is calculated; these are not published observations. Full differences and all-group balances are in results/diagnostics.

The conditional detritus-collapse and discard-removal experiments were not run because the researcher required a mass-balanced prerequisite. No selection, signed approval or annual regional PPR adoption is inferred.

[Canonical notes](../../model_notes.md) · [Current extraction check](CURRENT_VARIANT_CHECK.json) · [Full diagnostic returns](../../results/diagnostics)
