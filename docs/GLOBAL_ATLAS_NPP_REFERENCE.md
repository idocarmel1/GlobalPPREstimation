# Global atlas NPP reference

All **22 annual records, 1998–2019**, completed on 11 September 2026. The full
verifier passed without the partial-history option, and the graph's 176 reference
checks passed with no missing reference years. Regional NPP expansion is a separate
calculation and does not change this fixed reference geography.

The time-series graph's **Global atlas NPP** denominator is an estimate for one fixed,
overlap-free atlas geography. It is independent of the selected ecosystems, their
catch histories, PPR methods, Ecopath availability and the numerator's missing-data
cohort. The map continues to use each region's own NPP.

The reference is **coverage-limited**. Completing its calculation does not establish
complete satellite coverage of every water pixel or make it total world-ocean NPP.
Its source-window water support, excluded fill categories and model support are
retained for every year and must remain visible with the denominator.

## Fixed geography and overlap

Reference identifier: `atlas_lme_high_seas_union_v1`.

The boundary is the geometric union of all **66 LMEs and 18 high-seas identities** in
`SeaAroundUsExtraction/global_output/tables/units.json`. The complete named identity
list, source-layer hashes, repaired union, polygon hash and overlap audit are saved in
`NPPExtraction/output/global_atlas_reference/geometry_manifest.json` and
`atlas_lme_high_seas_union.geojson`. The set includes the no-catch identities
`LME_064` and `HS_018`; a catch filter never determines the denominator boundary.

The extractor applies the existing `npp.regions.clean_geometry` topology and
antimeridian repair to **every** identity. It then dissolves all repaired polygons
before exact fractional-cell rasterization at 4 km and 1/12 degree. This removes
overlap within each system and between systems. It does not approximate overlap by
adding regional totals or subtracting a constant percentage.

The fixed union SHA-256 is
`716d96ccf2f814231bfe94e583ced4bffd4606841fcff3467b1f7dbcb0e3f124`.
The planar geometry diagnostic finds 41,495.0884753 square degrees in the separate
polygons versus 37,009.0214723 square degrees in their union. These are topology
diagnostics, **not physical ocean areas**. Physical km² use the package's spherical
raster-cell areas and fractional coverage.

The supplied `NPPExtraction/METHODS.md`, section 7, already documents substantial
LME/high-seas duplication, including most of the Arctic Sea high-seas area and
parts of 24 LMEs. It also reports boundary/version overlap between EEZs and high
seas. Therefore neither an LME + high-seas sum nor an uncorrected EEZ + high-seas sum
provides a defensible unique-geography denominator.

EEZs are **not added** to this reference. EEZ waters outside the LME/high-seas union
are excluded. The represented atlas geography must not be labeled the whole ocean.
The old report's rounded 2019 union budget and global retrieval-mask totals are
context, not numerical inputs to this reference.

## Annual NPP and ensemble convention

Values are **tonnes carbon per year**. The NPP package already produces carbon;
there is no wet-weight conversion or additional division by nine.

For each year the union is treated as one integration region. The calculation reuses
the original NPP package and the corresponding canonical annual source configuration.

Canonical rows from the later regional expansion carry their own provenance. The
global reader resolves those records through the explicit `source_configuration`
parent path and SHA-256, requires an original configuration from the same year,
and rejects conflicting original runs. The expansion cannot silently select a
different source window or model schedule for the global reference.

The annual calculation is:

1. Integrate the gap-filled Antoine–Morel baseline over the fixed union at 4 km.
   Retain observed months, physical polar-night zeros, donor-year climatology with
   the **union-month** anomaly factor, and near nearest-neighbour fill. Far fill is
   excluded from central NPP under the supplied configuration.
2. Integrate all scheduled algorithms over the union on the common 1/12-degree
   model-comparison grid. Calculate the existing common-mask model/reference ratios
   and apply those ratios to the union's gap-filled baseline. The package's documented
   own-coverage fallback remains explicit in `ensemble_basis`.
3. Take the **median of those union-wide model estimates**. Require every model
   scheduled for that year to produce a finite union estimate. An unexpected missing
   model produces an ensemble gap, not a median over a silently reduced model pool.

In symbols, for union U and year y,

`NPP_m(U,y) = baseline_AntoineMorel(U,y) × common_m(U,y) / common_AntoineMorel(U,y)`

on the common-mask branch, and

`global_atlas_ensemble(y) = median_m[NPP_m(U,y)]`.

This follows the supplied NPP workbook's **Summary** convention: median after
aggregating each model's total. It is different from the graph's selected-ecosystem
convention, which sums the selected regions' ensemble medians. For example, regional
model estimates `[100,400,900]` and `[900,400,100]` have regional medians summing to
800, while the model totals `[1000,800,1000]` have median 1000. Exports identify the
global convention as `median_of_union_model_totals` and retain all model estimates.

The union's gap-fill anomaly and model ratios are calculated for the union itself;
they are not reconstructed from old regional aggregates. This distinction matters
because anomaly clipping and ensemble medians are nonlinear. Existing cached
`baseline_YYYY_4km.npz` files contain only regional monthly accumulators, and
`ensemble_global_YYYY.npz` contains raw whole-grid common/own retrieval totals.
Neither can recover the required union estimate. Decoded monthly rasters and
matching water masks can be reused safely.

The available source schedules are one model, Antoine–Morel, in 1998–2002 and five
models in 2003–2019. A one-model ensemble is labeled as such. Algorithm spread is
not a statistical confidence interval; the algorithms also share satellite inputs.

## Coverage and missing years

The **polygon boundary remains fixed**. The source method's water mask comprises
pixels with an Antoine–Morel retrieval in the annual donor window, which varies
with year. Permanently unobserved water is outside this support; it is not an
observed zero. Far nearest-neighbour fills are also excluded from central NPP.

Every processed year records:

- Fixed polygon area and source-supported water area in km², plus their ratio.
- Monthly common-mask and per-model own-mask areas.
- Monthly baseline areas assigned to observed, dark, climatology, near-fill and
  far-fill categories.
- Day-weighted central support as a percentage of supported-water pixel-days and
  of fixed-polygon pixel-days, plus excluded far-fill share.
- Observed, central and all-fill baseline totals, source years, donor years,
  model names, model count, ensemble basis and source/code/output hashes.

`calculation_complete`, `geometry_complete`, `model_support_complete` and the
compatibility alias `complete` describe successful computation. They do **not** mean
full spatial satellite coverage. Successful records have `status: coverage_limited`,
`coverage_limited: true` and `coverage_complete: false`. All 84 `available_ids` mean
all reference geometries were integrated; they do not mean all pixels were observed.

Years outside 1998–2019 remain blank by default. An unprocessed, failed or incomplete
annual calculation also remains blank. The display's explicit earliest-year policy
may substitute the first available annual reference only for earlier years; it must
record that source year. It must not fill internal/later gaps, replace missing values
with zero, or silently shrink the reference geography.

For PPR/NPP, divide the central PPR estimate and both discard-routing sensitivity
endpoints by the **same numeric annual denominator**. Changing numerator selection
cannot alter that denominator. Selected mode answers a different question and uses
the same included ecosystem cohort for both its PPR numerator and regional NPP sum.

## Reproduction and safe resumption

The graph can read the saved compact reference without loading geospatial libraries.
The reference is produced by `tools/global_npp_reference.py`; the public reader is
`build_global_npp_reference(root, years)`.

From the repository root, after the annual NPP setup and extraction described in
`NPPExtraction/ANNUAL.md`:

```powershell
NPPExtraction/.venv/Scripts/python.exe -u -X utf8 tools/global_npp_reference.py --extract --years 1998:2019
```

The runner uses existing full SAU geometries and monthly source files. It performs
2019 first, then the remaining requested years in chronological order, using one
raster worker. No canonical annual CSV, workbook, PPR engine, map export or source
geometry is changed. A completed annual record and the compact `reference.json` are
written atomically after each year. Large intermediate rasters remain in the ignored
`NPPExtraction/data/work/global_atlas_reference` cache.

Source bytes are checked against the canonical download checksums. Geometry,
membership, source configuration, verified file hashes and the execution code hash
form an immutable input key written before numerical stages. A partial cache cannot
resume under changed inputs; a requested new run recomputes into a different frozen
cache. The source configuration follows the canonical annual CSV's provenance field,
so old provenance directories left by previous checkouts do not make a new run
ambiguous. Conflicting canonical source configurations are rejected.
Interrupted/incomplete array files are preserved as
diagnostic caches and recalculated. A completed record's provenance checksum is
verified before loading. Changing extraction source code during a worker run raises
an error rather than assigning a new hash to calculations executed by old code.
Exact executed helper files are preserved under `execution_sources`, including the
2019 helper used before the source-directory selection improvement. The underlying
NPP numerical implementation is the same across those helper revisions.

The numerical reader tests are in `tests/test_global_npp_reference.py`; they cover
the ensemble order, fixed geography, overlap removal, missing models/years, zero,
invalid totals, changed source bytes and incompatible partial-cache inputs.
The actual complete-year inventory is always the saved `reference.json` metadata;
an absent year is not evidence of zero production.

For an independent audit of the published numerical ledgers:

```powershell
python -X utf8 tools/verify_global_npp_reference.py
```

This requires all 22 years, compares every model estimate to its baseline and
coverage-matched model ratio, checks the median and graph values, verifies source
and helper provenance, and recomputes the coverage percentages. Its report is
`NPPExtraction/output/global_atlas_reference/verification.json`. The optional
`--allow-partial` flag is for inspecting an ongoing extraction and never labels
an unfinished history complete.

The reconstructed 2019 baseline is **42,068,251,754.19618 tC/year**, agreeing with
the source report's rounded 42.07 Pg C union budget. The five union model estimates
are 42.0683, 40.9071, 41.8081, 47.8654 and 44.9043 Pg C/year for Antoine–Morel,
VGPM, Eppley, CbPM and CAFE respectively. Their median is 42.0683 Pg C/year.
Source-water support is 97.7159% of the fixed polygon; day-weighted central support
is 91.7081% of fixed-polygon pixel-days. These are reference-domain support measures,
not percentages of the world's ocean or estimates of statistical confidence.
