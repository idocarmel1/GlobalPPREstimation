"""Render successor research prose from its actual regenerated numerical results."""
from pathlib import Path
import json

STUDY = Path(__file__).resolve().parents[1]
ROOT = next(p for p in STUDY.parents if (p / "Project.xlsx").is_file())
read = lambda relative: json.loads((STUDY / relative).read_text(encoding="utf-8"))
summary, regressions = read("results/summary.json"), read("results/regressions.json")
scenarios = read("results/scenarios.json")
method = "GE" if "new_GE_tC" in summary["baseline"] else "TE"
method_key = "new_GE" if method == "GE" else "new_TE_EEfix"
base = summary["baseline"]["new_" + method + "_tC"]
sample, cohort = summary["sample"], summary["cohort"]
by_id = {r["id"]: r for r in scenarios}
main = [by_id[k] for k in ("fished_catch__within", "review_included_uniform__within", "all_consumer_uniform__within")]
title = f"{method} PPR at taxon resolution: current validated cohort"
models = ", ".join(p["unit_id"] for p in cohort["pairs"])
bn = lambda value: f"{value / 1e9:,.6f}"


def table(headers, rows):
    return "| " + " | ".join(headers) + " |\n|" + "|".join("---" for _ in headers) + "|\n" + "\n".join("| " + " | ".join(str(x).replace("|", "\\|").replace("\n", " ") for x in row) + " |" for row in rows)


names = {"identity_b0": "Retain group coefficients", "unit_slope_b1": "Unit slope b=1",
         "all_consumer_uniform": "All positive consumers", "review_included_uniform": "Review-included consumers",
         "fished_uniform": "Catch-bearing groups, equal weights", "fished_catch": "Catch weights",
         "fished_ppr": "PPR weights; stress test"}


def scenario_name(key):
    if "__" not in key: return names[key]
    cohort_name, mode = key.split("__")
    return names[cohort_name] + ", " + mode + " ecosystems"


text = f"""# {title}

This successor analysis uses the current exact validated cohort following withdrawal of researcher validation for `(LME_028, 28_646_Guinea_(1998))`. The earlier 16 October studies remain historical and unchanged. The active review decision determines cohort membership; it does not alter saved model inputs, coefficients, numerical diagnostics or method eligibility.

The reconstructed {method} baseline is **{bn(base)} billion tC**. The within-ecosystem catch-weighted, review-included and all-consumer scenarios produce **{bn(main[0]['full_tC'])}**, **{bn(main[1]['full_tC'])}** and **{bn(main[2]['full_tC'])} billion tC**, respectively: factors of **{main[0]['full_over_base']:.6f}**, **{main[1]['full_over_base']:.6f}** and **{main[2]['full_over_base']:.6f}** relative to baseline. These are conditional arithmetic projections, not confidence bounds, a measured world total, or a reconstructed taxon food web.

## Scope and evidence

The [cohort manifest](inputs/cohort.json) binds **{sample['regions']} exact model-region pairs** to the final Project fingerprint and actual signed review identities: {models}. The withdrawn Guinea pair is excluded from all calibration, allocation, scenario and influence calculations in this successor. The 1985 Guinea candidate is not substituted. Separate upstream reference overlays remain context only and are not fitted observations or catch contributors.

All totals use **2019 total catch including discards**, **all basal sources**, unidentified treatment **method**, saved `{method_key}` coefficients, and the remaining models' signed-review default group exclusions. Original allocation shares are retained; excluded shares are not redistributed. The comparison contains **{sample['covered_catch_tonnes']:,.6f} tonnes** of allocated catch, **{sample['positive_catch_groups']} catch-bearing groups**, **{sample['region_taxon_records']:,} region–taxon records**, and **{sample['taxon_group_allocations']:,} taxon–group allocations**. Region–taxon records are not distinct biological species: taxa can recur across ecosystems and include broader catch categories.

The source experiment supplies {sample['consumer_groups_in_experiment']} consumer-group coefficients. {sample.get('positive_'+method+'_groups_in_experiment')} are positive and enter log fits; zero-valued coefficients: {sample.get('zero_'+method+'_groups_in_experiment',0)}. The review-included positive calibration sample has {sample['review_included_positive']} groups. Expected counts come from the new upstream records and aggregation package, then are independently checked against current published taxon allocations. [The count manifest](inputs/sample_manifest.json) is evidence for this cohort, not a reusable hardcoded sample size.

Taxon TL is `1 + log10(saved simple_sppr)`. Model-group TL is `1 + log10(saved SPPR_1995_TE0.1)`, retaining the cycle-pruned/detritus-basal effective coordinate. It is not silently replaced with the ordinary displayed model TL. Treating the two TL conventions as comparable is an explicit projection assumption.

## Reconstruction and conditional prediction

Let `c_ig` be catch allocated to group `g`, `C_g = sum_i c_ig`, `S_g` its saved {method} coefficient, `T_i` taxon TL and `T_g` effective group TL. The project carbon conversion gives `PPR0 = sum_g(C_g S_g)/9`.

The anchored projection is `s_ig(b) = S_g × 10^[b(T_i − T_g)]`. It retains each observed group coefficient, including its departure from the descriptive regression line. It assumes that a slope observed between functional groups also applies to taxa within those groups. Neither the regression nor this calculation establishes that assumption.

With allocation shares `q_ig = c_ig/C_g` and mean taxon TL `mu_g = sum_i q_ig T_i`, the exact multiplier is:

`R_g(b) = 10^[b(mu_g − T_g)] × sum_i q_ig 10^[b(T_i − mu_g)]`.

The first factor is the mean TL shift. The second is centered Jensen curvature, at least one. The full total is the sum of `c_ig S_g 10^[b(T_i − T_g)]/9` over actual allocations. A mean shift may be negative, so convexity alone does not guarantee that the full total exceeds baseline. Group factors must be weighted by this method's own baseline PPR contributions `C_g S_g / sum_h C_h S_h`.

This calculation does not rerun diets, mortality, detritus recycling, efficiency or feedback equations, and does not enforce flow balance in a finer network. A group network can already contain the cost of mixed diets: for two equally weighted terminal consumers with costs 10 and 100, a correctly aggregated linear diet calculation may already retain their mean cost 55, while the classic coefficient at mean TL is only 31.62. Thus an exponential TL projection is a sensitivity assumption, not a universal correction for network aggregation.

The fitted response is log SPPR. Anchoring retains each existing group residual, so no additional residual-smearing multiplier is applied; that would count the same observed group heterogeneity again. Unknown within-group residual variation remains unidentified. Scenario spread is not an estimated distribution of ecological true PPR.

## Numerical results

{table(['Saved-coefficient reconstruction', 'Billion tC'], [['Grouped classic',bn(summary['baseline']['classic_model_tC'])],['Taxon simple chain',bn(summary['baseline']['simple_taxon_tC'])],[method+' baseline',bn(base)]])}

{table(['Conditional scenario', 'Slope b', 'Billion tC', 'Factor over baseline'], [[scenario_name(s['id']),f"{s['b']:.6f}",bn(s['full_tC']),f"{s['full_over_base']:.6f}"] for s in scenarios])}

All {len(scenarios)} scenarios use identical catch support. The pooled and within fits are recomputed from the new cohort rather than subtracting Guinea from an old fitted result. PPR weighting uses the response itself and is retained as an influence stress test, not a preferred estimator.

![Conditional total PPR](results/conditional_totals.png)

At fixed slope b=1, the full factor is **{by_id['unit_slope_b1']['full_over_base']:.6f}**, decomposing sequentially into a mean-shift factor **{by_id['unit_slope_b1']['shift_over_base']:.6f}** and additional dispersion factor **{by_id['unit_slope_b1']['full_over_shift_jensen']:.6f}**. The centered-Jensen-only factor **{by_id['unit_slope_b1']['centered_jensen_over_base']:.6f}** answers a different question because it omits mean shifts. The sequential full/shift decomposition is not the product of independently averaged group factors.

## Refitted descriptive relationships

Five calibration choices are retained: all positive consumers, review-included consumers, catch-bearing groups with equal weights, catch weights and method-specific PPR weights. Pooled regressions fit one intercept; within regressions fit an intercept per ecosystem; between regressions fit one weighted centroid per ecosystem with equal weight per ecosystem. These are descriptions of functional groups, not independent-species regressions.

{table(['Calibration and design', 'Slope', 'R²', 'Observations', 'Models'], [[scenario_name(k),f"{f['slope']:.6f}",f"{f['r2']:.6f}",f['n_observations'],f['n_models']] for k,f in regressions['fits'].items()])}

![Refitted trophic-level associations](results/tl_associations.png)

There are {sample['regions']} food webs, not {sample['consumer_groups_in_experiment']} independent ecosystem replicates. A positive TL association does not identify a universal transfer efficiency, a causal within-group slope or feedback omitted by the cycle-pruned TL coordinate.

## Leave-one-model-out calibration sensitivity

Each refit omits one model from calibration, then applies that slope to the same full current {sample['regions']}-model catch support. It does not remove the held-out model's catch from the scenario. The {len(regressions['leave_one_model_out'])} refits and {len(regressions['per_model'])} per-model fits are saved in [regressions.json](results/regressions.json).

"""
lomo_rows = []
for name in sorted({r["fit"] for r in regressions["leave_one_model_out"]}):
    rows = [r for r in regressions["leave_one_model_out"] if r["fit"] == name]
    lomo_rows.append([scenario_name(name), f"{min(r['training_slope'] for r in rows):.6f}–{max(r['training_slope'] for r in rows):.6f}", f"{bn(min(r['full_cohort_total_tC'] for r in rows))}–{bn(max(r['full_cohort_total_tC'] for r in rows))}"])
text += table(["Fit", "Omission-refitted slope range", "Full-cohort scenario range, billion tC"], lomo_rows)
text += "\n\nThese ranges describe calibration sensitivity, not confidence intervals for true PPR. Group and regional influence remain descriptive diagnostics and do not authorize further exclusions.\n\n"
if method == "GE":
    comparison = read("results/ge_te_comparison.json")
    text += "## GE–TE comparison on common support\n\nThe new [TE successor](../ppr_taxonomic_resolution_20261018_validated7/report.md) is the comparison source. Its full consumed-input ledger is checked transitively before GE analysis. Exact model/group identity, catch allocations, taxon TLs, effective group TLs and classic/simple totals are required to match. GE uses its own coefficients and PPR weights.\n\n"
    text += table(["Scenario", "GE billion tC", "TE billion tC", "GE/TE total", "GE factor", "TE factor"], [[scenario_name(r["id"]),bn(r["GE"]["full_tC"]),bn(r["TE"]["full_tC"]),f"{r['GE_over_TE_total']:.6f}",f"{r['GE']['full_over_base']:.6f}",f"{r['TE']['full_over_base']:.6f}"] for r in comparison["scenarios"]])
    text += "\n\nAt b=0 and b=1, every group's mean-shift, Jensen and full TL factors are identical across GE and TE because the catch/TL support and specified slopes are identical. Aggregate factors can differ because GE and TE assign different baseline PPR weights to those groups. Fitted scenarios also use different estimated slopes; their differences cannot be attributed solely to weights. GE's consumer ratio P/Q does not make the entire GE calculation automatically independent of the EE floor: saved detrital accounting may also depend on mortality. This study preserves the actual saved configuration.\n\n"
text += "## Retained diagnostic restrictions\n\nPositive researcher review concerns the model extraction and signed diagnostics; it does not approve every additional coefficient, transformed calculation or annual outcome. The following saved flags remain in force. A finite reconstructed total is not a new annual publication permission.\n\n"
text += table(["Region", "Saved diagnostic", "Published annual status", "rho living", "EE floor"], [[d["unit"],d["diagnostic_status"],d["published_annual_status"],d["rho_living"],f"{d['use_ee_floor']} / {d['ee_floor']}"] for d in summary["diagnostics"]])
text += "\n\n## Reproducibility\n\n[Source hashes](inputs/source_hashes.json) bind the current cohort, generated pages, canonical model/source packages and transitive upstream results. [Analysis verification](evidence/verification.json) records direct-sum identities and actual runtime. [Independent verification](evidence/independent_verification.json) reconstructs catch allocations from current HTML and solves separate weighted design matrices for pooled, within, between, per-model and leave-one-model-out fits. [Figure review](evidence/figure_review.json) records visual checks of the regenerated figures. No production model solver, regional workbook recalculation or page publication is performed by this research package.\n"
(STUDY / "report.md").write_text(text, encoding="utf-8")

relative = STUDY.relative_to(ROOT).as_posix()
old = "ppr_taxonomic_resolution_" + ("GE_" if method == "GE" else "") + "20261016"
readme = f"""# {title}

Researcher-owned successor analysis requested on 18 October 2026. It refits the {method} taxon-resolution study for the {sample['regions']} exact currently validated model-region pairs after withdrawal of Guinea 1998 validation. The [16 October study](../{old}/README.md) remains historical and unchanged.

The saved-coefficient baseline is **{bn(base)} billion tC**. Catch-weighted, review-included and all-consumer within-ecosystem projections are **{bn(main[0]['full_tC'])}**, **{bn(main[1]['full_tC'])}** and **{bn(main[2]['full_tC'])} billion tC**. They are conditional scenarios, not uncertainty bounds or new scientific approvals.

- [Report and interpretation](report.md).
- [Exact cohort](inputs/cohort.json), [count expectations](inputs/sample_manifest.json), and [consumed source hashes](inputs/source_hashes.json).
- [Summary](results/summary.json), [all scenarios](results/scenarios.json), [regressions and LOMO fits](results/regressions.json), and [scenario CSV](results/scenario_totals.csv).
- [Conditional totals](results/conditional_totals.png) and [TL associations](results/tl_associations.png), with SVG companions.
- [Analysis verification](evidence/verification.json), [independent verification](evidence/independent_verification.json), [figure review](evidence/figure_review.json), and [process](evidence/process.md).

From the repository root, with the recorded scientific Python runtime:

```powershell
python {relative}/code/analyze.py
python {relative}/code/render_report.py
python {relative}/code/verify_independent.py
```

Source versions must match the manifests. A changed cohort or dependency requires a deliberate successor or scoped rerun, not a silent fallback to historical results. These commands write only this study's derived outputs and never run the production model solver.
"""
if method == "GE": readme += "\nThe [GE–TE comparison](results/ge_te_comparison.json) checks identical support and fixed-slope group factors against the new TE successor.\n"
(STUDY / "README.md").write_text(readme, encoding="utf-8")
process = f"""# Execution and evidence scope

The 18 October {method} successor adapts the historical analyzer into a new package. Historical results, reports and scripts are not overwritten. The successor consumes the new seven-pair cohort manifest, current published catch allocations and new upstream aggregation/SPPR studies after active review publication.

All pooled, within, between, per-model and leave-one-model-out regressions are refitted. Twelve conditional scenarios are recalculated from original allocation weights and saved coefficients. Sample counts are derived from upstream evidence and checked by a separate direct allocation enumeration. The independent verifier uses least-squares design matrices rather than the analyzer's demeaning formulas and verifies all refit classes and transported totals.

The report and figures are regenerated from these outputs. [Runtime and analysis checks](verification.json), [independent checks](independent_verification.json), [stdout](run_stdout.json) and [figure review](figure_review.json) record completed verification. The [cohort](../inputs/cohort.json) and [source ledger](../inputs/source_hashes.json) identify exact inputs. No production scientific engine call, input repair, model selection change, or mutation of a historical study is part of this package.

Scope remains 2019 catch including discards, all sources, unidentified treatment method, and the cohort's signed-review default exclusions. Numerical restrictions survive. These are conditional reconstructions and calibration sensitivities, not a claim of taxon-level model validation or measured global PPR.
"""
(STUDY / "evidence/process.md").write_text(process, encoding="utf-8")
print(json.dumps({"report": str(STUDY / "report.md"), "method": method, "models": sample["regions"]}))
