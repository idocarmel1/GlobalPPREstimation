# Source-preserving ICES loader repair implementation plan

> For agentic workers: execute the independent loader and accounting tasks with regression tests, then independently review their integrated changes.

**Goal:** Repair shared source loading and SPPR accounting, rerun the three ICES methods, update its review package and commit the global fixes.

**Architecture:** Preserve the canonical source bytes. Load explicitly supplied routing, including zeros, before applying any legacy fallback. Handle nonfeeding structural diet cells by trophic role without filling unknown consumer inputs. Account for unrouted flows in each formulation's own production currency. Changes are general rather than keyed to ICES.

**Tech stack:** Existing Python/pandas/numpy/scipy engine, unittest/pytest, model-local lossless diagnostic serializer, DOCX and XLSX review artifacts.

**Authorization:** User explicitly requested global loader/accounting fixes and a commit, three fresh ICES methods, and updated report/appendix/recommendation. Source parameters, regional selection, Project.xlsx, map and trends are protected. The Scotland investigation is delegated to a separate user-requested chat.

## Tasks

- [ ] Loader: add failing regressions for standalone producer routing, explicit-zero DET routing, legacy missing routing, unknown consumer imports versus nonfeeding structural imports, source TL and metadata. Implement the bounded general fix in ModelData.py. Demonstrate source input immutability.
- [ ] Accounting: add failing formulation-specific export checks for GE, TE and With Egestion, including imported prey and internal fleet discard returns where supported. Port only relevant existing accounting work into the isolated branch; exclude unrelated opt-in BA completion changes. Verify source-known quantities are not silently overwritten to obtain a pass.
- [ ] Integration: inspect combined diff; run the scientific engine suite and relevant workflow checks, report any pre-existing failures. Keep SPPR_Methods.md and USER_GUIDE.md consistent. Commit only reviewed global code/tests/docs.
- [ ] Diagnostics: run exact canonical ICES model with the previous explicit flags (EE floor 0.1; no diet normalization, GS defaults, zero-catch/BA substitutions or pooling). Use normal shared loader, no four-cell local workaround. Save constructor, full direct GE/TE/With Egestion returns, 70-by-basal-source matrices, sign/nonfinite audit, source/runtime ledger, code identity and evidence completeness. Bound construction to 300s and each method to 180s.
- [ ] Review artifacts: preserve latest researcher/manual content and existing taxon mapping sheets; revise diagnostics, comparison and recommendation only from verified new evidence. Render and inspect all DOCX pages and appendix changes. Check portable links and hashes.
- [ ] Delivery: verify protected source/regional/publication hashes, summarize actual method outcomes and limitations, provide review files and commit ID. No decision registration or publication.

## Review focus

Explicit zero must remain distinguishable from absent routing. Missing consumer import must not become observed zero. Internal discard returns must be counted once. TE must not double-count mortality already absorbed in efficiency. A balanced total must not conceal negative source contributions or recycling divergence.
