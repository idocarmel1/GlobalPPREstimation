# PPR skills for Claude and Codex

Both directories contain the same three skills and a `.skill` archive for each.

| Skill | Claude | Codex | Purpose |
| --- | --- | --- | --- |
| Ecopath extraction | [SKILL.md](claude/ecopath-extraction/SKILL.md) | [SKILL.md](codex/ecopath-extraction/SKILL.md) | Paper → import files, database JSON and provenance |
| Species-to-group mapper | [SKILL.md](claude/ewe-species-to-group-mapper/SKILL.md) | [SKILL.md](codex/ewe-species-to-group-mapper/SKILL.md) | Catch taxa → model groups → PPR |
| Ecopath paper to PPR | [SKILL.md](claude/ecopath-paper-to-ppr/SKILL.md) | [SKILL.md](codex/ecopath-paper-to-ppr/SKILL.md) | Extraction, taxonomy, SPPR and mapping, or a requested subset |

Claude keeps the detailed workflow in each standalone `SKILL.md`, with the combined
skill routing to stage references. Its archives contain no OpenAI metadata.
Codex uses concise entry points, the complete workflows in `references/`, and
`agents/openai.yaml` for names, invocation prompts and existing interface settings.
Scripts, scientific references, examples and templates are shared byte-for-byte.
The combined skill includes its examples, so it does not depend on a sibling skill.

## Knowledge refresh — 2026-09-10

All three project skills were refreshed in both agent distributions, and all six
`.skill` archives were rebuilt. The refresh records source-table scope, mortality
rates versus flows, central **Final mappings**, annual NPP reproduction and units,
separate catch bases, and the limits of optional discard-routing sensitivity.
The full paper-to-PPR chain includes taxonomy; an extraction-only request still
stops after extraction.

[The refresh report](../docs/SKILL_KNOWLEDGE_REFRESH.md) records the baseline gaps,
seven supported retrieval scenarios, validation and installation evidence. The
mapping validator still cannot encode evidence scope or precedence, and a
composite can pass its membership check with only one overlapping group. Reconcile
source tables before populating `members.csv`, then review every candidate and
its spatial weights independently. The expanded carbon-conversion literature
review and new model coverage remain deferred.

## Using the distributions

Choose one agent directory. Copy the **three individual skill folders**, not their
parent, into that agent's skill location when installation is wanted. Claude Code
project skills use `.claude/skills/`; Codex personal skills use `$CODEX_HOME/skills`
(normally `~/.codex/skills/`). The Claude archives are ready for interfaces that
accept `.skill` uploads. Codex primarily uses the unpacked folders; its archives
are portable copies containing the same resources and metadata.

Repository rebuilds do not automatically update installed skills. The
2026-09-10 refresh deliberately updated the existing
`C:\Users\idoca\.agents\skills\ecopath-extraction` copy after backing it up,
while preserving its existing interface metadata. The paths and verified file
hashes are in [the installation record](../data/installed_skill_refresh.json).
No new global skills were installed. In this checkout, read
`skills/codex/<name>/SKILL.md` for Codex or `skills/claude/<name>/SKILL.md` for
Claude; do not assume another installed copy has picked up repository changes.

Resolve bundled script paths from the skill's own directory. Resolve repository
tools and data from the GlobalPPREstimation checkout. `GLOBALPPR_ROOT` tells mapping
helpers where the data are; it does not change the working directory or make a
relative script path resolve differently.

## Editing and rebuilding

| Change | Edit here |
| --- | --- |
| Extraction workflow, scripts, references or templates, including mortality/discard source accounting | `claude/ecopath-extraction/` |
| Mapping workflow, scripts, references or examples, including the annual PPR/NPP integration contract | `claude/ewe-species-to-group-mapper/` |
| Combined router and taxonomy stage | `combined-src/` |
| Codex entry points and interface metadata | `codex-src/<skill>/` |

`claude/ecopath-paper-to-ppr/` and all of `codex/` are generated. Do not edit their
copied resources directly. The Claude source directories are also runnable skills;
they are the common domain source so a correction is made once.

From the repository root:

```text
python skills/build_combined_skill.py
python skills/build_combined_skill.py --check
```

The builder assembles both complete distributions and all six archives with stable
archive metadata. `--check` writes nothing and fails for stale or missing files,
unexpected skills or stale archives. `build_skill.py` remains a compatibility
entry point to the same builder. Tests also verify resource and archive parity.

The old `skills/<skill>/` directories now live under `skills/claude/`; active
integration imports and commands have been updated. Older handoff examples and
historical design documents use the old paths. The former
`ecopath-extraction-gpt.skill` is superseded by `codex/ecopath-extraction.skill`;
its PDF portability and unknown-value documentation improvements were preserved
in the common extraction resources.

For SPPR use `tools/run_sppr.py`, including for one-model runs. The combined skill
now also documents `tools/apply_taxonomy.py` for Ecobase JSONs without an extraction
folder. Neither tool is bundled as a standalone skill helper: both need this
repository's algorithm and inputs.

The September11 follow-up adds all-identity simple PPR, regional NPP independent
of catch, NPP-only and fixed global-atlas views, physical-support limits, verified
source/cache lineage and the article reference/use log. Mapping-only and
extraction-only requests retain their stage boundaries. See
[`docs/SKILL_KNOWLEDGE_REFRESH.md`](../docs/SKILL_KNOWLEDGE_REFRESH.md) for the
independent retrieval checks and installed-skill backup record.
