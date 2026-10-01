# Combined PPR workflow and retained scientific resources

The project's active pipeline skill is [ecopath-paper-to-ppr](combined-src/SKILL.md). The original `combined-src` entry point includes the current regional workbook workflow and the lessons from the September 2026 extractions. Use it for the full pipeline or any requested subset. Use the separate [ecopath-model-validation skill](../ecopath-model-validation/SKILL.md) for model review packages and their evidence requirements.

## Current editing locations

| Change | Edit here |
|---|---|
| Combined entry point, stage routing and scope | [combined-src/SKILL.md](combined-src/SKILL.md) |
| Model validation and review packages | [ecopath-model-validation/SKILL.md](../ecopath-model-validation/SKILL.md) |
| Source preparation, extraction and selection | [model-preparation.md](combined-src/references/model-preparation.md) |
| Missing data and supplements online | [missing-data-recovery.md](combined-src/references/missing-data-recovery.md) |
| Source, conversion and loaded-state audit | [reconstruction-audit.md](combined-src/references/reconstruction-audit.md) |
| Group taxonomy and JSON-only models | [group-taxonomy.md](combined-src/references/group-taxonomy.md) |
| Direct GE, TE and With Egestion diagnostics | [direct-diagnostics.md](combined-src/references/direct-diagnostics.md) |
| Catch matching, comparisons and regional PPR/NPP | [regional-calculation.md](combined-src/references/regional-calculation.md) |
| Registry, map and knowledge graph | [project-integration.md](combined-src/references/project-integration.md) |

The former prepare-ecopath-model, calculate-regional-ppr and update-ppr-project skill folders were removed after their instructions and references were integrated here. Their capabilities remain stages of this combined skill.

The current skill is repository-dependent: run it from this checkout, resolving Project.xlsx and the project README as described in its entry point. References to retained domain resources resolve within this tree; do not copy only combined-src into a personal skill directory and assume the neighboring dependencies travel with it. No personal installation is changed by a repository update.

## Retained scientific resources

`claude/ecopath-extraction/` retains the detailed extraction workflow, eight-file templates, validators, converter helpers and scientific references. `claude/ewe-species-to-group-mapper/` retains mapping procedures, structure/coarse-taxon guidance, examples and validation helpers. The former assembled `claude/ecopath-paper-to-ppr/references/` also retains source-bundle, integration and mortality/discard references. The active combined stage references link the needed resources explicitly. Resolve scripts and embedded paths in those documents against their own original skill directory, then adapt their historical repository I/O to the current workbook contract.

Capture taxonomy once during source reading and reuse it for exact model-group matching. Preserve unknown values, source-table purpose, spatial scope, original inputs and configuration-specific diagnostic limitations. The current combined instructions govern execution where retained documents use old paths or broader diagnostics.

## Historical distributions and audits

The `claude/`, `codex/` and `codex-src/` skill entry points and six `.skill` archives record earlier distributions. They are retained resources, not extra active project skills. The historical `build_combined_skill.py` and compatibility builder assemble those former three-skill distributions; they are not the refresh command for this current combined workflow. Do not run them to publish or validate the active combined source. No current portable package or installed personal copy is claimed by this consolidation.

The original 201-file preservation audit and earlier refresh reports describe their dated snapshots. The current combined SKILL.md, taxonomy reference and this README were intentionally revised; six project-stage/detail references were added. Other original scientific scripts, templates, examples and distribution files remain unchanged. Historical commands such as tools/run_sppr.py, tools/apply_taxonomy.py and old data/top10 paths are superseded by the current instructions; do not recreate the old project layout to follow them.

For ongoing work, use the [project README](../../../README.md) and the [combined skill](combined-src/SKILL.md). Validate relative resources and requested-stage behavior after edits, then refresh the current knowledge graph when requested.
