# Multiple PPR curves and optional baseline

The time-series view will plot one curve per selected SPPR method, with an
optional method used as the divisor for every plotted value in that year.
One selected method without a baseline retains the existing values, cohort,
teal curve and shaded area. Multiple curves use distinct colors and a legend
with values for the inspected year. The baseline is plotted only if selected.

The existing annual data and estimation algorithms stay unchanged. PPR masses
remain carbon (source wet weight divided by 9); PPR/NPP retains its single
conversion. Normalized values are dimensionless multiples of the baseline.
Comparisons use one ecosystem cohort common to the usable selected methods
and the baseline. Completely unavailable methods remain labeled unavailable;
missing or zero baseline values create gaps. Per-method catch-taxon coverage
can differ because the input annual totals are already aggregated; disclose
that coverage rather than imply matching taxon support.

Implementation: extend pure aggregation with `compare` and a comparison CSV
export; add an accessible method picker and optional baseline selector; render
all curves on one shared axis with per-method year readouts; preserve old
single-method URLs and include new choices in shared links and downloads.

Validation: numerical identity of the original single curve, matched cohorts,
baseline division and cancellation for PPR/NPP, zero/missing cases, failed
methods, model/scope handling, CSV values, and browser checks for one/two/three
curves, shading, selection, baseline removal, deep links and year inspection.
Refresh documentation and the knowledge graph, then commit and push under
the existing user authorization.

Implemented and checked: the numerical suite covers original single-method
identity, two/three methods, shared cohorts, failed/disjoint cohorts, optional
baseline and self-division, missing/zero denominators, PPR/NPP cancellation,
scope/year/model choices, empty/duplicate methods, long CSV values and baseline
model provenance. Browser checks confirm one-curve shading, two/three separate
curves, baseline removal, model changes, year inspection and URL restoration.
The default-model identity for an unplotted baseline and per-year gap reasons
are retained in comparison downloads following independent review.
