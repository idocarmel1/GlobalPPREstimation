# Guinea combined versus separate mapping check

Completed 2026-09-07 for the 1998 model and all 375 catch taxa. The combined arm
ran in an isolated evaluation root, with the combined Codex skill, the audited
source membership and taxonomy, and the same catch input. That agent was explicitly
denied the production mapping. The separate arm is the independently completed
production mapping. The source extraction was shared, and workflow/task context
was known: this is an independent mapping comparison, not a fully blinded
end-to-end experiment or a statistical non-inferiority test.

| Measure | Combined | Separate (production) |
|---|---:|---:|
| Catch tonnage mapped | 99.6652% | 98.5802% |
| High-confidence catch | 41.2% | 41.5% |
| Medium-confidence catch | 21.2% | 23.6% |
| Low-confidence catch | 37.2% | 33.5% |
| Unresolved taxa | 5 | 83 |
| Composite assignments | 56 | 43 |
| Documented evidence code, catch share | 37.5% | 34.7% |

Both structurally validate. Group sets agree for **276/375 taxa (73.6%)**,
representing **96.4% of catch tonnage**. This comparison does not compare composite
weights or establish equal PPR values. The documented-evidence code metric excludes
source-backed composite rows, so it is not total source support.

The largest differences were reviewed against their stated evidence:

- Sciaenidae: the separate arm uses five documented member guilds. The combined
  arm adds a sixth through an inferred Pentheroscion guild. That increases the
  candidate set rather than adding a directly documented member.
- Blackchin tilapia: the combined arm uses a low-confidence feeding/habitat analogue
  to the herbivorous Mulets group. The separate arm leaves the absence of a named
  cichlid group unresolved.
- Lutjanidae: the combined arm adds an inferred demersal guild for Apsilus; the
  separate arm retains the documented Lutjanus coastal guild.
- Scombroidei: the combined arm constrains the historical name using the catch
  common/commercial label; the separate arm uses its broader historical taxonomy.
- Mugil cephalus: the combined arm infers the source mullet feeding guild, while
  the separate arm declines to extrapolate across the source's Mugil exception.

These are unresolved ecological choices, not evidence that higher coverage is
more accurate. The production mapping remains the separate arm. Its source-only
ablation in `../../mapping/28_646_Guinea_(1998).comparison.txt` is a different test
and must not be confused with this comparison. No algorithm, source biological
number, SPPR result or production choice was changed by the combined arm.

The model covers **111,932 km² off the country Guinea**, not the whole Guinea
Current LME. Both arms share that geographic extrapolation. See `comparison.txt`
for the full disagreement ranking, the two CSVs for reproducible inputs, and
`input_hashes.json` for the shared audited source tables.
