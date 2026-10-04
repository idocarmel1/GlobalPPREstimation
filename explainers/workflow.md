# Regional workflow

Read [the structure contract](structure.md) before modifying project files. Regional workbooks provide the authoritative table inputs; Project.xlsx owns publication/model metadata and human review records. Generated views expose the resulting state.

For an existing registered model, edit only `selected_model_id` and `selection_rationale` in the regional Overview, then run:

```powershell
python tools/cli/region.py refresh --region regions/LME/LME_028
```

Refresh validates identity/schema, saves usable outgoing results under their actual identity, derives the path, restores compatible selected-model material, recalculates ready arithmetic, and publishes central/map updates. Missing prerequisites produce an explicit pending selection with outgoing values unavailable. Repeating refresh is safe. The execution record records the completed refresh checks and scientific freshness limitations.

New papers/models require actual metadata registration once, source recovery/extraction and scientific review as requested. The [pipeline skill](../tools/skills/paper-to-ppr/SKILL.md) describes scientific stages; the [validation skill](../tools/skills/ecopath-model-validation/SKILL.md) describes reports and review. Selection itself does not authorize parameter repair, fresh broad diagnostics, mapping guesses or human approval.

Catch, classic PPR and NPP remain independent inputs during model switches. Ready arithmetic uses compatible retained coefficients/matching. Fresh direct diagnostics retain the agreed GE, TE and With Egestion scope; ordinary validation report rows remain GE/TE. Missing values remain missing and provisional/failed status remains explicit.
