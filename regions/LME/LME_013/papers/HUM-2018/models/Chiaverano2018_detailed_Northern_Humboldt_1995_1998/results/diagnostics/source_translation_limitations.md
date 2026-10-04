# Source interpretation and computational translation

The primary branch retains the revised/final native supplement's numerical
parameters, diets, imports and full fleet removals. The source audit preserves
the native cells and conflicting prose separately. This is a limited
computational representation, not an author-confirmed reconstructed native EwE
model.

The paper describes 36 living groups and three detritus pools. The native tables
give anchovy eggs (group 36) biomass and EE but no P/B or Q/B, and route a quarter
of anchovy's detritus fate to that compartment. The computational translation
has 35 living compartments and four nonfeeding detritus pools. The engine adds
one synthetic imported-diet compartment, giving 40 runtime groups. Runtime ID
40 means `diet_import`; the native source's fleet node 40 means Artisanal
fisheries. Native fleet nodes 40 and 41 are companion fishery nodes, not stock
groups.

Source assimilation efficiencies give consumer GS exactly as 1 minus AE. Source
steady state motivates explicit zero living biomass accumulation; unreported
migration, external detritus import and habitat fraction use disclosed
computational conventions in the source transformation ledger. No LIM,
biomass-placeholder reconstruction or GS default is used. Printed source values
remain unnormalized.

Runtime diet normalization changes 19 rows and 161 cells. Four deviations exceed
0.001: Chrysaora plocamia 1.045, Chub mackerel 0.99523389955, Large hake 1.00905
and Green sea turtle 1.002. Every row factor and changed cell is retained. The
normalization-induced predation change is calculated with fixed consumer flows;
living BA is not adjusted. The engine nonetheless solves detritus accumulation
as its own structural identity. Those derived pool values are not observed
stock trends. It also forces all runtime detritus EE to one, replacing native
eggs EE 0.8843322396278381, offal EE 0, pelagic EE 0 and benthic EE
0.8890905380249023. Both layers are retained in the field ledger.

The ModelData loader also forces the four detritus routing rows to an identity
block. Eight native cells change: eggs to benthic 1 becomes 0; offal to benthic
0.9 and pelagic 0.1 become 0; pelagic to benthic 1 becomes 0; each pool's
self-routing 0 becomes 1. The source's benthic Export 1 is retained in source
tables rather than in the loader's four-column fate matrix. These changes and
all synthetic row cells are explicit in the matrix field ledger. The engine
uses zero detritus M0/egestion, so source pool transitions are not translated
into supported native flow equations by this identity convention.

Native fleet discard fate routes 100% to fishery offal. The engine's recycling
matrix uses natural mortality and egestion routes and has no donor-resolved
fishery return ancestry. Full native landings plus discards remain removals in
the primary branch; no synthetic external detritus import is substituted. The
offal pool's runtime natural inflow and SPPR are consequently zero. This
translation limitation remains separate from the source's complete fishery
evidence. Native Sardine landings 5.6513425 also conflict with the paper's
reported revised 1.4; this branch preserves the native value.

Native Gelatinous zooplankton (group 6) stored B 0.009068332612514496, P/B
0.5839999914169312 and Q/B 2.919999837875366 are corroborated by the rounded
focal Table 1 values. Its production is 0.0052959061678743424. The source
Chrysaora diet includes Gelatinous zooplankton at 0.0492610837438424, producing a
large predation demand. The normalized runtime predation is 22.349293378715736;
its production residual is 22.344262267919387. The independent raw source
budget also exhibits the discrepancy. This record does not repair a magnitude
or infer publication error from a translation residual.

All three actual direct configurations return FAIL. GE and With Egestion have
divergent detritus recycling and 59 negative source-recipient SPPR entries each;
26 entries in each occur in unfished recipients. TE has no negative matrix
entries but remains FAIL for model input and the PP budget. Its b=0 is a method
convention. The EE=0 re-credit requested by the default setting is unsupported
for this four-pool case and is not applied. Full dictionaries and matrices,
strict flags, retained masks and scope reconciliation are in the direct return
artifacts.

Scientific methods do not change any biological runtime field. Only the
method-specific detritus-resolution cache changes. The constructor's separate
balanced copy is never used. For GE and With Egestion, the SPPR-weighted
production residuals reproduce the signed PP budget gap to numerical precision.
TE does not satisfy that residual-only identity; its remainder is retained
explicitly rather than attributed to invented group flows.

Finite returned coefficients were used only for candidate arithmetic. All
1,236,060 taxon-year rows, 5,670 annual totals and 34,020 NPP ratio rows remain
production-ineligible. Negative values are preserved. The regional catch and
independent NPP snapshot have not been replaced. No selected model, active
regional workbook, Project workbook, map, graph or researcher approval record
is altered.
