# Unidentified-catch sensitivity

The atlas map and time series offer three treatments. The selected method's own
SPPR remains the default and preserves the existing calculations. The zero option
assigns no PPR contribution to the explicitly affected catches as a sensitivity
assumption; it does not remove their catch tonnage or claim that they have no
biological production requirement. The reference-TL option substitutes
`10 ** (reference_TL - 1)` for each affected catch taxon, using its existing Sea
Around Us reference TL and the project's 10% trophic-chain transfer efficiency.

Classification version `explicit-labels-v1` matches these case-insensitive markers
in either the catch taxon label or its common name: `unidentified`, `not identified`,
`NEI` (also `N.E.I.`), or `not elsewhere included`. Matching uses word boundaries.
It does not classify a named genus or family by rank, or match `spp.`, `other`, or
`miscellaneous` alone. A genus/family label is included only if its actual catch
label or common name explicitly contains one of the listed markers.

`data/unidentified_taxa.json` records every affected label by ecosystem, the
matching field and marker, common name, reference TL and replacement coefficient.
The exports also carry annual affected catch and the affected catch lacking a
reference coefficient. The displayed affected share uses total catch, including
unmapped catch. This is a reproducible label-based sensitivity definition, not a
claim to know the species composition of any residual category.

A missing reference TL retains a missing coefficient and its catch remains
outside coefficient coverage. It is never changed to zero by the reference-TL
option. Failed model methods remain unavailable under every treatment. The
reference-TL replacement has only a total SPPR and is available in the `all`
source scope; it is unavailable for `inner` and `PP`, which would require a source
decomposition that the reference chain does not provide. The zero assumption can
be applied within any existing source scope.

The URL parameter `unidentified=method|zero|simple` preserves the choice. Downloads
record the treatment and affected catch alongside the plotted values. All PPR
mass calculations still convert wet-weight equivalents to carbon once, at 1/9.
NPP retains the selected method, matching year, availability and historical-proxy
policy. Source workbooks keep the default scientific inputs and mappings; the
additional treatments are explicit atlas sensitivity calculations.

After rebuilding the network and time-series exports, run
`node tools/verify_unidentified.cjs` to compare their actual model-method results
under every treatment and source scope for 2019. It writes
`data/unidentified_validation.json`. The focused Python and JavaScript tests also
cover missing reference coefficients, unchanged catch tonnage, failed methods,
explicit label matching, scope restrictions, URLs and CSV output.
