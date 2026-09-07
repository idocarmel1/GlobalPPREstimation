# PPR integration takeover — 2026-09-07

The task is **Finish PPR estimation integration**. The first requested deliverable
was to understand Claude's work and prepare equivalent Claude/Codex skills.
That review and skill reorganization are complete. The full research integration
is still in progress; the priorities below carry it forward.

## What was reviewed

Read the complete [original handoff](HANDOFF.md), project/data documentation,
integration design history, recent commits, skill sources and both builders, the
older GPT archive, and the active integration paths. Queried the existing knowledge
graph, then checked its results against the files: the graph predates the `data/`
integration layer and is not an authority on its present state.

The join is catch `unit_id` → model selection → exact `groups_df.group_name` →
per-group `sppr_all` → taxon mapping → fixed composite weights → annual PPR.
`build_model_workbook.py` derives composition weights from singly assigned catch,
then falls back to model catch, biomass or equal weights and records the basis.
Missing SPPR propagates to a missing taxon/method result. Methods and distinct
models remain separate. Workbook verification independently evaluates the key
formulas and checks catch totals.

Preserve both uses of Jensen's inequality: the deliberately aggregated comparison
rows, and the algorithm's separate Monte Carlo correction. No files inside
`PPREstimation/` were changed in this pass. Work remains on `main`.

## Observed state, rather than assumed completed agent work

| Asset | Present in the integration index |
| --- | --- |
| Catch ecosystems | 364 |
| Ecosystems with archived articles | 109 |
| Ecosystems with NPP | 82 |
| Extracted models | 16 across 10 ecosystems |
| Mapping files | 7 across 6 ecosystems, including the Guinea stub |
| Network PPR workbooks | 6 across 5 ecosystems |

- **Guinea / `LME_028`:** `28_646_Guinea_(1998).members.csv` arrived as an
  untracked file. The mapping CSV still contains **0 decisions out of 375 rows**.
  An A/B outcome cannot be inferred from its presence. No final comparison was
  found in that mapping directory.
- **Thailand / `LME_035` and Okhotsk / `LME_052`:** each mapping directory contains
  its existing mapping and resolved-weights CSV. The promised taxonomy CSV,
  member list and model profile are absent there. Resume source verification;
  do not assume stage 2 finished.
- `tools/apply_taxonomy.py`, `tools/run_sppr.py` and the original handoff were
  already untracked when this task began. The two helper scripts were preserved
  byte-for-byte. The original handoff text is retained, with a takeover addendum.

Some older documentation is stale. In particular, the handoff places the 368 stale
upstream workbooks in PPRAtlas, while the root README identifies the affected
SeaAroundUsExtraction workbooks. These are distinct from the six integration
model workbooks verified here. The old graph and broad claims that all mapping
membership is missing also predate the member-list work in the handoff.

## Skill layout and integration changes

[skills/README.md](../skills/README.md) documents the complete layout and build rules.
`skills/claude/` and `skills/codex/` each contain extraction, species-to-group
mapping, and the combined paper-to-PPR skill. Claude retains detailed standalone
workflows; Codex has concise entry points, full local workflow references and
OpenAI interface metadata. All shared scripts, references, templates and examples
are identical between corresponding distributions. Six archives are generated.

The shared domain source lives in the Claude standalone directories. The existing
`combined-src/` owns the combined router and taxonomy stage; `codex-src/` owns the
Codex entry points and metadata. The builder assembles the other files and checks
trees and archives without writing during `--check`. Text checkout rules make the
packages reproducible across platforms while retaining CRLF for EwE templates.

The older GPT package's PDF backend, rendering/rotation instructions, output-log
placement and unknown-value clarifications were preserved in the shared resources.
No global skill installation was changed.

Active tool imports, eval-root copying and current README links were updated for
the new paths. The combined skill now uses `tools/run_sppr.py`, documents the
Ecobase JSON-only taxonomy route, and explains when refreshed SPPR must reach
`output/top10` before preparing stage 4. It also preserves extraction-only scope
and source-member priority over habitat inference.

One integration defect found during review was fixed: `.taxonomy.csv` is now
excluded from mapping discovery and ecosystem mapping counts, alongside the other
sidecars. The regression test demonstrated the previous false mapping detection.
The existing index was not regenerated as part of reorganizing the skills.

## Verification

- Before changes: **225 tests passed**; all **6/6 model workbooks verified**.
- After changes: **231 tests passed**, including distribution parity, exact archive
  contents, read-only drift detection and taxonomy-sidecar exclusion. The existing
  Jupyter deprecation warning remains.
- All six distributed skills pass the skill frontmatter validator.
- Independent scenario review checked extraction with unknown BA, JSON-only
  taxonomy with one-model SPPR, and coarse-taxon mapping against membership evidence.
- All six skills were copied to temporary installed locations and invoked from
  a different working directory with spaces in the paths. Applicable PDF table/text
  extraction, EwE output writing/database conversion, unknown BA preservation and
  work-order generation passed. The PDF smoke test used the available Poppler
  fallback; PyMuPDF is not installed in the active Python environment.
- Protected-file hashes confirmed **7,824 files unchanged**, including data/results,
  PPREstimation Python files and Claude's two unfinished helper scripts. The only
  difference among the original 7,825 protected entries was the intentional link
  update in `data/README.md`. Every original skill resource has a relocated copy.

These checks establish preservation and portability, not a new paper-to-PPR
scientific validation. No research model or result workbook was regenerated.

## Remaining integration work

1. Finish source verification/taxonomy for Thailand and Okhotsk, then apply taxonomy,
   regenerate the named SPPR workbooks, prepare refreshed work orders, map, validate,
   build and verify PPR. Complete the Guinea mapping and any isolated A/B comparison.
2. Re-check the Arabian Sea inherited mapping tail against the paper's member table.
3. Map the remaining usable Humboldt and South China Sea models.
4. Test a genuinely new paper through extraction, taxonomy, SPPR and PPR in one pass.
5. Wire verified network results into the atlas and address stale upstream workbooks.
6. Extend model/article coverage, then refresh coverage documentation and the graph.

Carry forward two pre-existing validator limitations discovered in the skill
review: member checking uses literal taxa/synonyms rather than deriving family/order
containment, and a composite can pass when only one candidate overlaps the documented
member set. Manually check every candidate against the source; a validator pass does
not prove ecological correctness. This pass did not change those scientific rules.

## Completion of the subsequent integration pass — 2026-09-07

The numbered list above is retained as the plan at takeover. **Tasks 1–5 are now
complete**, together with the requested source-scope workbook sheets, map scope
switch, method ratios, GE/TE recycling metrics and selected-pilot coloring gate.
The graph is refreshed for these changes; task 6's coverage expansion remains
future work. See [INTEGRATION_COMPLETION.md](INTEGRATION_COMPLETION.md) for the
current artifacts, tests, independent Guinea comparison and source caveats.
