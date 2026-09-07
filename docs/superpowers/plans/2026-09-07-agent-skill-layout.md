# Agent skill layout implementation plan

**Goal:** Continue the integration from `docs/HANDOFF.md`, beginning with the requested
review and equivalent Claude/Codex skill sets.

**Architecture:** Maintain extraction and mapping domain resources in `skills/claude/`.
Assemble its combined skill from those sources and `skills/combined-src/`. Generate
`skills/codex/` from the same resources plus concise entry points and UI metadata in
`skills/codex-src/`. Build and check all six packages together.

**Constraints:** Work on main. Preserve existing research inputs, outputs, uncommitted
work and Jensen behaviour. Do not run `PPREstimation/create_PPRS_excel.py` as a program.
The present deliverable is review and skill preparation; the remaining scientific and
map-integration tasks stay in the handoff.

- [x] Read the complete handoff; compare current integration code, data inventory,
  history, generated skill assembly and legacy GPT package. Existing graph is stale.
- [x] Establish baseline: 225 tests pass; all six workbooks in five ecosystems verify.
- [x] Run an independent read-only skill scenario check before adaptation.
- [x] Add checks for matching skill names/resources/packages and detection of drift.
- [x] Move the sources, retain the legacy GPT portability improvements, make paths
  explicit, correct the combined workflow's SPPR and JSON-only taxonomy routes.
- [x] Generate Codex entry points with local workflow references and openai.yaml.
- [x] Update active imports, eval-root copying and current documentation for the layout.
- [x] Check all packages, run scripts from outside their installed location, repeat
  integration tests/workbook verification and compare protected file hashes.
- [x] Record the observed takeover state and outstanding integration work.

New checks live in `tests/test_skill_distribution.py`; `skills/build_combined_skill.py`
remains the public builder and `skills/build_skill.py` delegates to it. The shared
mapping helper and ecosystem index must both exclude `.taxonomy.csv` sidecars.
