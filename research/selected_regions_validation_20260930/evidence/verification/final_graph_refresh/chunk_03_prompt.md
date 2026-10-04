You are a graphify extraction subagent. Read the files listed and extract a knowledge graph fragment.
Output ONLY valid JSON matching the schema below - no explanation, no markdown fences, no preamble.

Files (chunk 3 of 3):
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\regions\LME_050\validation_reports\50_502013_Coastal_Kyoto_Inoue_(2013)\reports_index.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\regions\LME_050\validation_reports\50_502013_Coastal_Kyoto_Inoue_(2013)\source_review.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\regions\LME_052\reports_index.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\regions\LME_052\validation_reports\52_1_Sea_of_Okhotsk_NE_(1980)\source_review.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\ecopath-model-validation\SKILL.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\ecopath-model-validation\agents\openai.yaml
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\ecopath-model-validation\references\acceptance-checks.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\ecopath-model-validation\references\document-production.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\ecopath-model-validation\references\evidence-and-calculations.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\original_skill_resources\README.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\original_skill_resources\combined-src\SKILL.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\original_skill_resources\combined-src\references\direct-diagnostics.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\original_skill_resources\combined-src\references\evidence-handoff.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\original_skill_resources\combined-src\references\group-taxonomy.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\original_skill_resources\combined-src\references\missing-data-recovery.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\original_skill_resources\combined-src\references\model-preparation.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\original_skill_resources\combined-src\references\project-integration.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\original_skill_resources\combined-src\references\regional-calculation.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\skills\original_skill_resources\combined-src\references\size-stage-allocations.md
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\tools\templates\Model_validation_template_instructions.md

Rules:
- EXTRACTED: relationship explicit in source (import, call, citation, "see §3.2")
- INFERRED: reasonable inference (shared data structure, implied dependency)
- AMBIGUOUS: uncertain - flag for review, do not omit

Code files: focus on semantic edges AST cannot find (call relationships, shared data, arch patterns).
  Do not re-extract imports - AST already has those.
Doc/paper files: extract named concepts, entities, citations. For rationale (WHY decisions were made, trade-offs, design intent): store as a `rationale` attribute on the relevant concept node — do NOT create a separate rationale node or fragment node. Only create a node for something that is itself a named entity or concept. Use `file_type:"rationale"` for concept-like nodes (ideas, principles, mechanisms, design patterns). `file_type` MUST be one of exactly these six values: `code`, `document`, `paper`, `image`, `rationale`, `concept`. Any other value is invalid and will be rejected.
Code files: when adding `calls` edges, source MUST be the caller (the function/class doing the calling), target MUST be the callee. Never reverse this direction. `calls` edges MUST stay within one language: a Python function cannot `calls` a JS/TS/Go/Rust/Java symbol and vice versa — cross-language call edges are phantom artifacts, never emit them.
Image files: use vision to understand what the image IS - do not just OCR.
  UI screenshot: layout patterns, design decisions, key elements, purpose.
  Chart: metric, trend/insight, data source.
  Tweet/post: claim as node, author, concepts mentioned.
  Diagram: components and connections.
  Research figure: what it demonstrates, method, result.
  Handwritten/whiteboard: ideas and arrows, mark uncertain readings AMBIGUOUS.

false (if --mode deep was given): be aggressive with INFERRED edges - indirect deps,
  shared assumptions, latent couplings. Mark uncertain ones AMBIGUOUS instead of omitting.

Semantic similarity: if two concepts in this chunk solve the same problem or represent the same idea without any structural link (no import, no call, no citation), add a `semantically_similar_to` edge marked INFERRED with a confidence_score reflecting how similar they are (0.6-0.95). Examples:
- Two functions that both validate user input but never call each other
- A class in code and a concept in a paper that describe the same algorithm
- Two error types that handle the same failure mode differently
Only add these when the similarity is genuinely non-obvious and cross-cutting. Do not add them for trivially similar things.

Hyperedges: if 3 or more nodes clearly participate together in a shared concept, flow, or pattern that is not captured by pairwise edges alone, add a hyperedge to a top-level `hyperedges` array. Examples:
- All classes that implement a common protocol or interface
- All functions in an authentication flow (even if they don't all call each other)
- All concepts from a paper section that form one coherent idea
Use sparingly — only when the group relationship adds information beyond the pairwise edges. Maximum 3 hyperedges per chunk.

If a file has YAML frontmatter (--- ... ---), copy source_url, captured_at, author,
  contributor onto every node from that file.

confidence_score is REQUIRED on every edge - never omit it, never use 0.5 as a default:
- EXTRACTED edges: confidence_score = 1.0 always
- INFERRED edges: pick exactly ONE value from this set — never 0.5:
    0.95  direct structural evidence (shared data structure, named cross-file reference).
    0.85  strong inference (clear functional alignment, no direct symbol link).
    0.75  reasonable inference (shared problem domain + similar shape, requires interpretation).
    0.65  weak inference (thematically related, no shape evidence).
    0.55  speculative but plausible (surface-level co-occurrence only).
  Models follow discrete rubrics better than continuous ranges; the bimodal
  distribution observed in production (>50% at 0.5, >40% at 0.85+) shows the
  range guidance is being collapsed to a binary. If no value above fits, mark
  the edge AMBIGUOUS rather than picking 0.4 or below.
- AMBIGUOUS edges: 0.1-0.3

Node ID format: lowercase, only `[a-z0-9_]`, no dots or slashes. Format: `{stem}_{entity}` where stem is `{parent_dir}_{filename_without_ext}` (the **immediate** parent directory name + the filename stem, both lowercased with non-alphanumeric chars replaced by `_`) and entity is the symbol name similarly normalized. Only one level of parent is used — not the full path. Examples: `src/auth/session.py` + `ValidateToken` → `auth_session_validatetoken`; `lib/utils/helpers.py` + `parse_url` → `utils_helpers_parse_url`; `tests/test_foo.py` + `_helper` → `tests_test_foo_helper`. Top-level files (no parent dir, e.g. `setup.py`) use just the filename stem: `setup_my_func`. This must match the ID the AST extractor generates — using just the filename (e.g., `session_validatetoken`) or the full path (e.g., `src_auth_session_validatetoken`) will create orphan ghost-duplicate nodes. If you are re-extracting a project that had ghost duplicates under the old format, the user should run `graphify extract --force` to rebuild cleanly. CRITICAL: never append chunk numbers, sequence numbers, or any suffix to an ID (no `_c1`, `_c2`, `_chunk2`, etc.). IDs must be deterministic from the label alone — the same entity must always produce the same ID regardless of which chunk processes it.

Generate the extraction JSON matching this schema exactly:
{"nodes":[{"id":"session_validatetoken","label":"Human Readable Name","file_type":"code|document|paper|image|rationale|concept","source_file":"relative/path","source_location":null,"source_url":null,"captured_at":null,"author":null,"contributor":null}],"edges":[{"source":"node_id","target":"node_id","relation":"calls|implements|references|cites|conceptually_related_to|shares_data_with|semantically_similar_to|rationale_for","confidence":"EXTRACTED|INFERRED|AMBIGUOUS","confidence_score":1.0,"source_file":"relative/path","source_location":null,"weight":1.0}],"hyperedges":[{"id":"snake_case_id","label":"Human Readable Label","nodes":["node_id1","node_id2","node_id3"],"relation":"participate_in|implement|form","confidence":"EXTRACTED|INFERRED","confidence_score":0.75,"source_file":"relative/path"}],"input_tokens":0,"output_tokens":0}

Then write the JSON to disk using the Write tool at this exact absolute path (no relative paths — Write resolves relative paths against an undefined cwd and the file will be silently lost):
C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation\original_research_archive\research\selected_regions_validation_20260930\work\graph_prepare\final_refresh\chunk_03.json

PROJECT-SPECIFIC COORDINATOR INSTRUCTIONS (take precedence where more specific):
Read every listed file and verify its full-byte SHA-256 against chunk_03_sources.json before and after extraction. Files and the whole corpus are frozen. Do not edit sources. Your only write ownership is chunk_03.json plus chunk_03_verification.json in this directory. Use repository-relative forward-slash source_file values, actual source_location line numbers or null, and record the exact source_sha256 on nodes for the source you read. For every regional document, prefix the generic deterministic ID with the lowercase region ID (eez_598, lme_052, etc.) derived from the full path so identical WCPO basenames never collide across regions. For nonregional files use the documented generic ID. Never add chunk/sequence suffixes. Each source must contribute a named document node and useful domain entities; each edge endpoint must be a node in your chunk. A cited external file may be represented by a source-attributed concept node with its target path as an attribute, without claiming that external file was read. Keep source evidence explicit: current model selection is not scientific approval; accepted scientific inputs remain unchanged; mapping corrections are distinct from parameter repair; diagnosis and Annual availability differ; historical snapshots are not current release authority. Model-specific conclusions must stay with their own region. Capture meaningful concepts and relationships (roughly 5–15 entities per substantive document is often adequate), not one node per arbitrary numeric value. Preserve rationale as node attributes. Do not infer graph/Git completion from an index that says tracked separately. Use native Sol gpt-6.1-sol/xhigh only; do not spawn descendants here. Token/cost fields should be null with usage_note unavailable; schema zero placeholders are not telemetry. Validate JSON, unique IDs, allowed types, every confidence score, internal endpoints and all source hashes. Maximum 3 hyperedges. Retain a compact verification with file hash list and counts. Finish with a brief ownership-release handoff; no production/shared/Git/browser operations.
