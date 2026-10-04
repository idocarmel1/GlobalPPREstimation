# Project instructions

## project_contract

Before modifying project content, read [README.md](README.md), [structure.md](explainers/structure.md), and [workflow.md](explainers/workflow.md). Both active project skills follow this contract. The final agreements in [the reorganization plan](explainers/plans/project_reorganization_plan.md) override older conflicting instructions. Preserve the plans in `explainers/plans/`.

Preserve scientific inputs, researcher edits, missingness and diagnostic restrictions. Selection, loadability, readiness and researcher approval are separate. Do not repair parameters or invent provenance during administrative work. Serialize Project.xlsx writes. Use only canonical discovery and model-local outputs. Each distinct model retains only its latest extraction; Git history supplies recovery.

## graphify

Use the current graph at `tools/knowledge_graph/graph.json`; its scope describes coverage and freshness. Query with `graphify query "question" --graph tools/knowledge_graph/graph.json`. An outdated graph is an index of its stated snapshot, not evidence about current scientific results. `/graphify` uses the installed graphify skill; do not create a second graph location.
