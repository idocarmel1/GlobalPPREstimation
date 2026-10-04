# Project instructions

## project_contract

Before modifying project content, read [README.md](README.md) and [the current agent project contract](explainers/agents/project_contract.md). Both active project skills follow this contract. Reuse an unchanged contract already read in the same execution context; new contexts or changed contracts require reading it. Human guides live in `explainers/`; agent rules live in `explainers/agents/`. Current instructions replace superseded implementation plans; Git history supplies their recovery.

Preserve scientific inputs, researcher edits, missingness and diagnostic restrictions. Selection, loadability, readiness and researcher approval are separate. Do not repair parameters or invent provenance during administrative work. Serialize Project.xlsx writes. Use only canonical discovery and model-local outputs. Each distinct model retains only its latest extraction; Git history supplies recovery.

## graphify

Use the current graph at `tools/knowledge_graph/graph.json`; its scope describes coverage and freshness. Query with `graphify query "question" --graph tools/knowledge_graph/graph.json`. An outdated graph is an index of its stated snapshot, not evidence about current scientific results. `/graphify` uses the installed graphify skill; do not create a second graph location.
