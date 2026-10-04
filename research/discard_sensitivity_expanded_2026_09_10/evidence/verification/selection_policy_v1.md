# Prespecified expansion policy — version 1

This policy is fixed before calculating sensitivity directions. All writes stay in
this directory; inputs are existing repository JSONs, never recovered paper data.

Snapshot all 252 JSONs in real_models, the metadata catalog, the original private
engine, and the original four source JSONs/workbooks. Hash raw bytes and canonical
ecological content (sorted groups and diets, numerical strings normalized; omit
taxonomy, pedigree and descriptive fields). Exclude originals by identity/content,
file copies, toy/broken models, aggregate non-model JSONs and nonmarine systems.

Candidate ordering prefers EwE_jsons, then global_cover_jsons. Within each corpus,
round-robin geographically distinct metadata strata (FAO region, or geographic
longitude band/hemisphere where region is missing). Within each stratum sort by
ecosystem type, structural size bin (<20, 20–39, >=40 groups), then numeric model ID.
Stop selection at 20 eligible additions. Inventory every file and retain all
screened rejection reasons; untested remaining candidates are explicitly untested.
No sensitivity magnitude, direction, workbook availability or method ranking
enters selection. Distinct ecosystem/time models may qualify, file copies do not.

Eligibility requires real marine/estuarine metadata and a recorded wet-weight
currency compatible with the fixed /9 convention; compatible group schema;
positive finite original living harvest; producers and detritus; finite positive
living biomass and production, positive consumer consumption; EE and egestion
fractions in [0,1] (numerical allowance 1e-8); nonnegative diet and fates with fate
sums <=1+1e-8. Raw consumer diet deviations >0.001 are material and rejected;
normalization within 0.001 is explicitly recorded, not silently repaired.

Use the original initializer settings for comparability. Reject missing required
B/PB/QB/EE/catch inputs, any LIM change to supplied biological parameters, and
inferred living accumulation exceeding 1e-4 of group production (absolute floor
1e-10). Zero accumulation defaults within this rounding tolerance are exposed.
Require initialized physical residuals <=1e-4 relative per living production,
consumer consumption and whole-system budget; constructed detritus closure has
absolute tolerance 1e-7. Negative physical flows beyond 1e-8 are invalid.
No biomass accumulation is invented to rescue an unbalanced model. Original four
references retain their established, less restrictive source limitations and are
never counted among the additions.

Require a finite nonnegative fixed-TL standard baseline and at least one usable
new_GE, new_TE_EEfix or new_WithEgestion recycling baseline. Usable means physical
closure, finite nonnegative source coefficients, spectral radii <1, and the frozen
method's PP-equivalent identity relative gap <=5%. Other method failures remain
visible. This is numerical eligibility, not proof of ecological truth.

Exact solved fractions: every integer percent 0 through 20, then 25,30,40,50,75,100.
Freeze native H; D=fH; L=(1-f)H. SC/SM/SE retain the original ledger and private
adapter. SR is only available with verified original metadata; no name-based
destination transfer. High fractions are stress tests. Keep invalid masks and
fixed comparison support. Native units are reported verbatim from metadata;
missing area/time normalization remains unknown. Carbon conversion /9 is the
original study convention, not a taxon-specific measurement. Native ratios are
unavailable when source boundaries or currency are incompatible.

Run at most one heavy model at a time. A baseline candidate exceeding 180 seconds
is recorded as resource-limited and unassessed, not scientifically invalid; continue
the same deterministic queue. This resource guard was added after the first 18
baseline screens, when the 99-group Albatross Bay candidate exceeded three minutes;
no sensitivity direction had been calculated. Reuse installed Python dependencies. Compare
saved outputs where available; otherwise compare fresh baseline and zero-discard
adapter outputs against the untouched frozen calculator and independent analytic
and conservation checks. Preserve the old four-point study and cross-check overlap.
