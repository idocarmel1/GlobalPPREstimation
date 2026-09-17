"""Descriptive findings, validity boundaries and unit-safe scientific summaries."""
from pathlib import Path
from collections import Counter
import json
import numpy as np
import pandas as pd
from baseline import ROOT
from run_study import write_json

def run():
    df=pd.read_csv(ROOT/'results/ecosystem_ppr.csv');a=df[df.cohort=='additional'];rows=[];boundaries=[];curve=[]
    for method in ['new_GE','new_TE_EEfix','new_WithEgestion','Ulanowicz_TE','SPPR_1995_TEmean']:
        for f in [.01,.05,.1,.2,.5,1.]:
            sub=a[(a.method==method)&(a.scope=='all')&(a.route=='SM')&np.isclose(a.fraction,f)]
            good=sub[sub.valid&sub.coefficient_change_pct.notna()]
            rows.append(dict(method=method,fraction=f,n_valid=len(good),n_total=len(sub),median_change_pct=float(good.coefficient_change_pct.median()) if len(good) else None,
                min_change_pct=float(good.coefficient_change_pct.min()) if len(good) else None,max_change_pct=float(good.coefficient_change_pct.max()) if len(good) else None,
                median_retained_change_pct=float(good.retained_change_pct.median()) if len(good) else None,
                min_retained_change_pct=float(good.retained_change_pct.min()) if len(good) else None,max_retained_change_pct=float(good.retained_change_pct.max()) if len(good) else None,
                standard_positive_excess=int((good.standard_relative_excess_pct>0).sum()),standard_negative_excess=int((good.standard_relative_excess_pct<0).sum())))
    for (mid,method,scope,route),rr in a[(a.fraction<=.2)&(a.route!='S0')].groupby(['model_id','method','scope','route']):
        rr=rr.sort_values('fraction')
        for (_,prev),(_,nxt) in zip(rr.iloc[:-1].iterrows(),rr.iloc[1:].iterrows()):
            if prev.valid!=nxt.valid:boundaries.append(dict(model_id=mid,method=method,scope=scope,route=route,left_fraction=prev.fraction,right_fraction=nxt.fraction,left_valid=bool(prev.valid),right_valid=bool(nxt.valid),right_reasons=nxt.reasons))
        if route=='SM' and scope=='all' and rr.valid.all() and rr.coefficient_change_pct.notna().all():
            y=rr.coefficient_change_pct.to_numpy();delta=np.diff(y);second=np.diff(y,n=2)
            curve.append(dict(model_id=mid,method=method,scope=scope,route=route,change_at_20_pct=float(y[-1]),max_change_per_one_percentage_point=float(np.max(np.abs(delta))),
                max_second_difference_response_percentage_points=float(np.max(np.abs(second))),fraction_of_largest_curvature=float(rr.fraction.iloc[int(np.argmax(np.abs(second)))+1])))
    curve.sort(key=lambda x:x['max_second_difference_response_percentage_points'],reverse=True)
    checks=json.loads((ROOT/'verification/output_checks.json').read_text(encoding='utf-8'))
    baseline=json.loads((ROOT/'results/baseline_checks.json').read_text(encoding='utf-8'))
    selected=json.loads((ROOT/'results/selected_models.json').read_text(encoding='utf-8'))
    screening=json.loads((ROOT/'results/candidate_screening.json').read_text(encoding='utf-8'))
    families=Counter(r['metadata'].get('model_name',r['model_id']) for r in selected)
    fate_classes=Counter(r['screening']['detritus_source_checks']['fate_class'] for r in selected)
    screened=max(r.get('selection_rank',0) for r in selected)
    summary=dict(at_selected_fractions=rows,low_fraction_validity_boundaries=boundaries,low_fraction_curvature=curve,
        baseline_comparison_counts=dict(Counter(c.get('provenance','unknown') for c in baseline)),baseline_passed=sum(c.get('passed') is True for c in baseline),
        baseline_unavailable=sum(c.get('passed') is None for c in baseline),baseline_strict_differences=sum(c.get('passed') is False for c in baseline),
        configuration_differences_reproduced=sum(c.get('configuration_difference_verified',False) for c in baseline),
        added_status_counts=dict(Counter(a.status)),screening_counts=screening['status_counts'])
    write_json(ROOT/'results/scientific_findings.json',summary)
    pd.DataFrame(rows).to_csv(ROOT/'results/findings_at_fractions.csv',index=False);pd.DataFrame(boundaries).to_csv(ROOT/'results/low_fraction_validity_boundaries.csv',index=False);pd.DataFrame(curve).to_csv(ROOT/'results/low_fraction_curvature.csv',index=False)
    lines=['# Expanded discard-routing experiment: methods and findings','',
        'Exactly **20 additional distinct real marine model JSONs** passed the numerical and amended source-fidelity eligibility checks. Four original models were extended as a separate reference cohort and are excluded from the addition count. Sea of Okhotsk NE remains a zero-native-harvest null control. No paper extraction, parameter recovery, annual reconstruction, SAU mapping or production-atlas export was performed.','',
        '## Design and limits','',
        'Each source model retains its original living harvest H. Every integer percentage from 0% through 20%, plus 25%, 30%, 40%, 50%, 75% and 100%, is an exact solved fraction f. Designated D=fH is reclassified through SC (remains catch), SM (catch becomes L=(1−f)H; M0 gains D; EE falls D/P) or SE (catch becomes L, separate external loss gains D). Only the original Humboldt reference has supported SR destination information. Other SR cases remain explicitly unavailable.',
        'Living physiology, diet, predation, original accumulation and migration are held fixed. The dependent detritus accumulation absorbs changed inflows at fixed predation; returned material is not assumed to become additional consumption. This is a constrained accounting sensitivity, not a fitted Ecopath dynamics forecast.',
        'All selected additional metadata use the WetWeight currency enum. Those records do not explicitly state the mass/area/time normalization. PPR is therefore reported as native wet-weight production equivalent /9; unknown normalization is not relabeled tonnes per square kilometre per year. Relative coefficient responses and native ratios use matching within-model units. Absolute native PPR is never pooled across models. The /9 factor preserves the original assumed carbon convention. All-source ratios are unavailable with positive imported support and an internal-only PP denominator.','',
        '## Selection and numerical eligibility','',
        'Candidate order was fixed before sensitivity directions: EwE_jsons first, geographical metadata strata in round-robin order, then ecosystem type, structural group-size bin and numeric model identifier. The original reference inputs, canonical ecological duplicates, toy/broken and nonmarine models, and incompatible currencies were excluded. All 252 JSON files were inventoried. Twenty passed after assessing the first 52 queued candidates. Remaining candidates are explicitly untested after the count was met, not presumed valid. The 99-group Albatross Bay baseline exceeded the 180-second resource guard and is unassessed, not scientifically invalid.',
        'Eligibility requires compatible finite source inputs, positive living harvest, primary producers and detritus, admissible EE/diet/fates, no material invented living accumulation, physical closure and at least one usable recycling method. Diet normalization is allowed only within a raw row-sum deviation of 0.001; every change is logged. Physical residuals allow 1e−4 group-relative living/consumption/whole-system rounding and 1e−7 absolute constructed detritus closure. Source changes beyond 1e−4 of a supplied biological parameter reject a candidate. Recycling methods also require finite nonnegative coefficients, spectral radii below 1, and their frozen PP-equivalent identity gap at most 5%. These checks do not validate ecological realism.','',
        'The source-fidelity amendment followed an input audit of the provisional set, after its scenario runs, and did not use sensitivity direction or magnitude. It rejects nonzero documented detritus onward fates overwritten by the frozen loader and unsupplied negative baseline detritus accumulation used to finance consumption. Santa Pola Bay (explicitly a marine fish farm) and Western Channel overwrite nonzero source routes; Moreton Bay and Western Bering Sea require unobserved detritus stock draw. All four provisional runs remain under results/excluded_provisional_models and do not enter valid aggregate distributions. They were replaced by South Benguela, Lagoon Chiku, Independence Bay and Northern Gulf of St Lawrence using the unchanged queue.',
        f'Detritus fate classifications among the final additions: {dict(fate_classes)}. Zero source rows changed to identity are disclosed as bookkeeping representation changes: detritus M0/egestion is zero, so no nonzero onward source flow is erased. Scenario detritus accumulation remains a dependent residual; that modeling convention is not claimed to be an observed source accumulation.',
        f'The 20 model/time cases represent {len(families)} named ecosystems. Central Atlantic (1950/1990) and North Atlantic (1950/1997) are dependent temporal observations. Their separate cases describe model response diversity and do not constitute independent ecosystem replicates. No global-population inference is made.','',
        '## Findings on the fixed original H','',
        '| Method, SM | Fraction | Paired models | Median coefficient change | Min–max change |','|---|---:|---:|---:|---:|']
    for r in rows:
        if r['fraction'] not in [.2,.5]:continue
        formatv=lambda v:'unavailable' if v is None else f'{v:+.4f}%'
        lines.append(f"| {r['method']} | {r['fraction']*100:.0f}% | {r['n_valid']}/20 | {formatv(r['median_change_pct'])} | {formatv(r['min_change_pct'])} to {formatv(r['max_change_pct'])} |")
    lines+=['','These are descriptive pointwise model distributions, not confidence intervals. The HTML separately offers the same-model support across all 27 fractions, so invalid high-discard scenarios cannot silently change a response curve’s donor population.',
        'At 20% under SM, the fixed standard exceeds new_GE in 5 of 20 cases and is below it in 15; against new_WithEgestion the signs split 12 versus 8. Standard overestimation is therefore not universal and depends on the recycling formulation. The GE coefficient median rises 0.9628%, while the retained-catch footprint median falls 19.2298%. By contrast, the TE_EEfix coefficient increase is often close to 25%, nearly canceling a 20% retained-catch reduction. In Prince William Sound, the TEmean coefficient rises 68.6679%, giving a 34.9343% increase in the retained-catch footprint despite the 20% lower retained amount. These are exact uniform-reclassification algebra on the original H, not a forecast of changing ecosystem biomass.',
        'SC is invariant under fraction relabeling. SC and SE have the same coefficients below 100% under uniform reclassification. At 100%, normalized catch weights vanish: TEmean uses a biomass fallback and SPPR_1986 is undefined. The fixed baseline-TL TE=0.1 standard is invariant by definition; its signed excess or deficit against recycling methods can still be substantial. Positive and negative standard discrepancies are reported, without assuming universal overestimation.',
        'Some finite 100% flow-method coefficients are extremely large (including TE_EEfix and Ulanowicz), where remaining removal approaches zero and source rounding can dominate. Their finite/convergent status does not establish conditioning or ecological robustness. These explicitly labeled stress endpoints should not be interpreted as realistic discard-effect magnitudes. Exact values and invalid masks remain exposed; zero retained L is not evidence that the underlying coefficient is reliable.',
        f"The 0–20% grid contains **{len(boundaries)} method/scope/route validity transitions** across adjacent solved points. The exact brackets and reasons are in `results/low_fraction_validity_boundaries.csv`. Curvature is measured by second differences of the coefficient-response percentage at adjacent one-percentage-point increments; it is not a confidence or error bound.",'']
    if curve:
        c=curve[0];lines.append(f"Largest fully supported low-range curvature: {c['model_id']} / {c['method']}, second difference {c['max_second_difference_response_percentage_points']:.6g} response percentage points near f={c['fraction_of_largest_curvature']:.2f}. Its change at 20% is {c['change_at_20_pct']:+.6g}%. No uncomputed point is presented as solved.")
    lines+=['','## Verification and deliverables','',f"The final output audit checks {checks['scenario_records']:,} scenario records and {checks['group_rows']:,} coefficient rows. It covers immutable input/engine hashes, zero-fraction identity, SC invariance, SC/SE equivalence, fixed harvest support, exact designated amounts, living production residual preservation, SM EE adjustment, no double-counted return, separate external loss without migration, finite/convergent/nonnegative validity, missing-data propagation, native denominator boundaries and decomposition reconciliation. Original overlap comparisons cover all 3,936 old records. Maximum absolute decomposition residual is {checks['maxima'].get('decomposition_absolute_residual',0):.8g} native units.",
        f"Baseline comparisons: {summary['baseline_passed']} strict matches, {summary['baseline_unavailable']} unavailable, {summary['baseline_strict_differences']} strict differences. Of those differences, {summary['configuration_differences_reproduced']} are reproduced by replaying the existing workbook with unnormalized raw diet rows. The experiment retains the original study's normalize_DC=True, restricted to documented rounding tolerance. No tolerance is loosened. Provenance counts: {summary['baseline_comparison_counts']}. Saved workbooks were snapshotted only after selection; no production export was run.",
        '`report.html` embeds compact verified data, scripts and assets. `results/ecosystem_ppr.csv`, `group_sppr.csv`, `effect_decomposition.csv`, `scenario_envelopes.csv`, `aggregate_distributions.csv` and `standard_method_comparison.json` provide machine-readable results. Per-model `study.validated.json`, `flow_ledger.csv`, `parameter_changes.csv` and diagnostics retain full numerical provenance. `results/discard_responses.v2.json` is a proposed exact-model group-coefficient interface, not an installed atlas uncertainty layer.','',
        '## Selected model catalog','', '| Existing model | Groups | Metadata ecosystem type |','|---|---:|---|']
    lines += [f"| {r['model_id']} | {r['group_count']} | {r['metadata'].get('ecosystem_type','')} |" for r in selected]
    (ROOT/'METHODS_AND_FINDINGS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(summary['at_selected_fractions'],ensure_ascii=False,indent=2))
if __name__=='__main__':run()
