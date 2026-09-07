# Thailand Ecobase 412: 1980 payload under a 1963 filename

The filename and model_year say 1963, but the metadata description says the overexploited Gulf of Thailand 1980. All 11 biomasses supplied in Christensen 1998 TableIIp.136 match the 1980 column at printed precision;10 fail the 1963 column and Benthos is 33 in both. This is an identity conflict, not a numerical rounding issue. Numerical parameters and filenames are preserved, with the 1980 interpretation explicit.

Axis: named taxonomic pools, demersal size/feeding guilds and three juvenile compartments.
Prefixes: Juv.=juvenile; Sm./Med./Lg.=size classes without published length thresholds. The source explicitly includes juvenile grouper/snappers; the JSON's Juv. groupers label is shortened.
Area: Gulf of Thailand 10–50 m shelf; whole-LME extrapolation is not spatially validated.
Period:1980 payload (29 groups), despite 1963 label. The 40 group 1973 model of Vibunpant etal.2003 is separate.
Catch-capable: fish and nonplankton invertebrate groups; do not infer catch on mammals, zooplankton, phytoplankton, detritus or algorithm import.
Membership: Christensen 1998 p.130 lists important components, not exhaustive inventories. members.csv has 38 rows including replicated juvenile memberships, two common-name forage components, and an unresolved printed Tachysuridea spelling. Taxonomy spelling corrections are explicit. The original article HTML text was read via the author publication page; originalPDF requests returned 403.
Source constraints: Sciaenidae, Lethrinus and Psettodes are medium demersal piscivores; Priacanthus is small demersal piscivores; Scolopsis and Upeneus are medium demersal benthivores. Thus Nemipteridae spans Scolopsis and Nemipterus in different groups. Clupeiformes spans small pelagics plus large-piscivore Chirocentrus stages. Family/order labels must retain every documented candidate.
Residuals: source trash fish corresponds to O.fish by structure. Its mixed basal diet does not prove every unidentified landing is trash fish; broad demersal composites and herbivore analogues remain low confidence. The source's illustrative members do not automatically exclude plausible additional species.
Stage weights: shark, large-piscivore and grouper/snapper catches without ages use model_catch, with zero recorded catch on juveniles. These are period-invariant model weights, not historical catch-age data.
Health: input balance and diet sums pass; GE/TE/egestion configurations retain EE-related WARN. Six symbolic methods fail in the current implementation. A complete source parameter/diet table is absent from the article, so full numerical provenance verification is not claimed.
