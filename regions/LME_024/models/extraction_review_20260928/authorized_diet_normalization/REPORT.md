# Authorized diet normalization and routing identifiability

User authorized diet normalization on 2026-09-28. The adjacent model JSON divides every known consumer diet entry, including known diet imports, by its published column sum. All 50 consumer sums are now one within 1e-35. Unknown entries and all other parameters remain unchanged. Source model SHA-256 is unchanged. NORMALIZATION_AND_ROUTING_CHECK.json records factors and verification. No detritus routing or pooling was implemented.

The normalized model passes the calculator diet validation and stops at the missing two-pool detritus-routing check. GE, TE and With Egestion remain NOT_RUN because construction fails; this is not a diagnostic FAIL result.

## Can the matrix be recovered?

Not uniquely from the numerical tables. Even if every living group's total waste/other-mortality flow were known, allocating it between two pools requires one fraction per living group (52 potential fractions). Each pool balance constrains only the sum of those contributions. With total supply fixed, the two pool constraints may themselves be dependent. Imports, transfers between detritus pools and export add further unknowns. Some living production parameters are also missing. Printed detritus EE constrains an aggregate outflow/inflow ratio, not donor-specific fractions.

The supplement provides a useful qualitative constraint: Appendix SF, page 57 says the discard pool is no longer fed when fishing stops. This supports a candidate structure with fishery returns to Discards (53) and natural mortality/unassimilated consumption to Detritus (54). It does not supply the full numerical matrix, surplus-transfer settings or external flows. Such a reconstruction must be labeled an assumption supported by prose, not a uniquely solved published matrix.

## Conditional Discards budget check

All flows below follow the extraction's t/km²/year interpretation of Table B3. Its caption does not explicitly supply units. Table B4 labels BA as an annual rate; using that printed convention gives BA = B × BA/B.

| Quantity | Value | Evidence |
|---|---:|---|
| Fishery discards, printed total | 0.2559104 | B3, page 16 |
| Consumer removal from Discards after normalization | 0.2145927601 | B2 pages 14–15, B and QB from B4 page 17 |
| Discards accumulation | 0.25 × 0.40 = 0.1000000 | B4 row 53, page 17 |
| Removal plus accumulation | 0.3145927601 | Derived |
| Minimum additional inflow needed if reported fishery discards are the sole supply | 0.0586823601 | Derived; excludes any extra export/transfer out |

Thus the simple fishery-only supply does not close with all printed values held fixed. This is conditional evidence of incomplete/inconsistent reconstruction, not proof that the authors' native model failed. Missing transfers/imports, parameter precision/stage, or BA/unit interpretation need checking. Do not repair this by silently adding natural mortality to Discards or changing BA.

Normalized consumer removal from Detritus (54) is 1853.6419550825 t/km²/year. This aggregate also cannot identify each donor's routing fraction.

Primary reference: the EwE user guide distinguishes detritus flow accounting, surplus routing, fishery inputs, and BA versus BA/B: https://pressbooks.bccampus.ca/eweguide/chapter/ecopath-input/ . It also describes sum-to-one diet normalization. Consult source-specific native settings before treating a hypothetical routing structure as the published model.

Next options are to obtain native routing/full-precision values, or explicitly authorize a source-informed routing sensitivity experiment. No such experiment or model selection has been made here.
