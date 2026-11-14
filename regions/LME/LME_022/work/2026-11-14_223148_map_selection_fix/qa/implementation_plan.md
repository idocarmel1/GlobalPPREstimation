# Map selection implementation plan

Goal: fix cached defaults hiding the reviewed ICES model, verify LME038 review filtering, and add an editable validated-model cohort to the trends ecosystem picker.

Scope and design: preserve scientific inputs, signed reviews, selected regional models, group weights and diagnostics. Extend the existing bounded HTML layout pipeline. Defaults follow Project; explicit stable model-ID choices and explicit URLs take precedence. Legacy automatic defaults must not become permanent overrides; retain recoverable legacy preferences and group/table settings. The new validated preset starts from all currently reviewed chosen models, then supports a custom subset.

1. Reproduce preference precedence and current LME022/LME038 eligibility with actual page code. Completed read-only: cached Scotland overrides ICES; current clean defaults pass both models. LME038 browser omission remains unconfirmed.
2. Add meaningful failing preference tests, implement bounded shared preference helper/layout integration, and verify default changes, explicit alternatives, URL priority, legacy preservation and cross-page behavior.
3. Add meaningful failing picker tests, implement the validated cohort in trend_extras.js/layout, and verify empty/custom starting states, exclusions, subset editing and URL/model changes.
4. Root reviews both changes, runs focused integration checks, then rebuilds saved-data pages with unchanged Project/scientific inputs. Verify full UI behavior through supported browser tools where available and retain truthful limits.
5. Refresh only affected graph sources, verify final source hashes, and commit the fixes on current main. Public push remains blocked by GitHub LFS quota; do not bypass LFS or discard source artifacts.

Review focus: ambiguous legacy defaults; explicit unvalidated choices; malformed/absent IDs; custom cohorts that omit reviewed ecosystems; review status independent of numeric availability; generated-page layout anchors and serialized URL state.

Authorization: user requested the two map fixes and the validated custom-selection option. The preceding 3,006-file public push was directly approved but GitHub rejected the LFS upload because its quota is exhausted. No fresh scientific solves or Monte Carlo are authorized or needed.
