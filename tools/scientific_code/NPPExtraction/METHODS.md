# METHODS — satellite NPP aggregated to Sea Around Us regions

Reference document for the `ppr-npp` pipeline. Written to be picked up cold: it records
what the code does, why each choice was made, which choices are wrong-but-tempting, and
the numbers a re-run should reproduce.

Everything here was produced and validated for **2019**. The pipeline is year-parametric;
2019 is the year the published tables use.

---

## 1. What the pipeline computes

For a chosen year, the annual net primary production of every region in three Sea Around
Us region systems, from five independent ocean-colour algorithms:

| region system | n | what it is |
|---|---|---|
| `lme` | 66 | Large Marine Ecosystems |
| `highseas` | 18 | SAU high-seas areas — FAO major fishing areas minus EEZs |
| `eez` | 282 | Exclusive Economic Zones as SAU divides them |

The core quantity is

```
NPP_annual,region = Σ_months Σ_pixels  PP[mg C m⁻² d⁻¹] × days_in_month
                                        × pixel_area[m²] × pixel_fraction_in_region
```

reported in tonnes C per year (`tC/yr`; 1e9 tC = 1 Pg C), with mean rates in mg C m⁻² d⁻¹.

**Purpose.** This is the *denominator* for primary-production-required (PPR) work. It
replaces the values Sea Around Us still publishes, which are a 1998–2007 SeaWiFS
climatology at 9 km.

---

## 2. Data sources

### 2.1 Antoine–Morel — Copernicus-GlobColour (the reference model)

| | |
|---|---|
| product | `OCEANCOLOUR_GLO_BGC_L4_MY_009_104` |
| dataset | `cmems_obs-oc_glo_bgc-pp_my_l4-multi-4km_P1M` |
| algorithm | Antoine & Morel — depth- and wavelength-resolved, chlorophyll-based |
| grid | 4320 × 8640 (1/24°), row 0 at +90°, column 0 at −180° |
| variable | `PP`, **mg C m⁻² day⁻¹**, NaN outside the retrieval |
| sensors | multi-sensor merge (SeaWiFS, MODIS, MERIS, VIIRS, OLCI) |
| period | 1997 → present, monthly |

**No Copernicus account is needed.** The native monthly NetCDF files sit on anonymously
readable object storage and are fetched by plain HTTPS GET. The root is discovered from
the STAC catalogue so a reprocessing does not silently break the URLs:

```
https://stac.marine.copernicus.eu/metadata/OCEANCOLOUR_GLO_BGC_L4_MY_009_104/product.stac.json
  → links[] entry containing "cmems_obs-oc_glo_bgc-pp_my_l4-multi-4km_P1M"
  → that dataset.stac.json → assets.native.href
```
which as of 2026-09 resolves to
```
https://s3.waw3-1.cloudferro.com/mdl-native-16/native/OCEANCOLOUR_GLO_BGC_L4_MY_009_104/cmems_obs-oc_glo_bgc-pp_my_l4-multi-4km_P1M_202603
```
List a year by S3 prefix (`?list-type=2&prefix=native/<key-root>/<YYYY>/`); files are
named `YYYYMM01-YYYYMMDD_<dataset>.nc`, ~65 MB each. 12 files/year ≈ 780 MB.
`npp/sources/copernicus.py` keeps that URL as `NATIVE_ROOT_FALLBACK` for when STAC is down.

### 2.2 VGPM, Eppley-VGPM, CbPM2, CAFE — OSU Ocean Productivity

| | |
|---|---|
| base URL | `https://orca.science.oregonstate.edu/data/2x4/monthly/<dir>/hdf/` |
| grid | 2160 × 4320 (1/12°, OSU's "2x4"), same orientation as above |
| format | gzipped HDF4, one SDS named `npp`, float32, **mg C m⁻² day⁻¹** |
| no-data | `-9999.0` (the file's own "Hole Value" attribute) |
| naming | `<prefix>.<YYYY><DOY-of-month-start>.hdf.gz`, e.g. `vgpm.2019001.hdf.gz` |
| inputs | MODIS R2022 reprocessing — **the same chain for all four** |
| size | ~17 MB per model-month; 48 files/year ≈ 780 MB |

| model | prefix | directory | algorithm |
|---|---|---|---|
| `vgpm` | `vgpm` | `vgpm.r2022.m.chl.m.sst` | Behrenfeld & Falkowski 1997 |
| `eppley` | `eppley` | `eppley.r2022.m.chl.m.sst` | as VGPM, exponential Eppley temperature function |
| `cbpm` | `cbpm` | `cbpm2.modis.r2022` | carbon-based, Westberry et al. 2008 |
| `cafe` | `cafe` | `cafe.modis.r2022` | absorption-based, spectrally resolved, Silsbe et al. 2016 |

Read `npp` with `pyhdf.SD`; pyhdf cannot read a file object, so the gzip is expanded once
into `work_dir` and reused.

**⚠ Coverage gaps that will bite you.** These are real properties of the products:

* **No VGPM and no Eppley-VGPM anywhere in the Black Sea.**
* **No CbPM2 anywhere in the Persian Gulf.**
* Very small semi-enclosed water bodies (Bosnia, Jordan, Israel/Red Sea, Marmara) are
  barely resolved by the 1/12° grid and may have essentially no OSU data at all.

The ensemble detects this per region and records it (§6.2). Do not silently treat a
missing model as a zero — that is what the original version of this code did, and it
produced `#VALUE!` cells and nonsense spreads in the Black Sea.

**Note.** The OSU site stopped updating in September 2024. Fine for years ≤ 2023; it will
not follow future reprocessings.

### 2.3 Why not the OC-CCI five-model product

[Ryan-Keogh et al. 2023](https://doi.org/10.5194/essd-15-4829-2023) (data
[10.5281/zenodo.8314348](https://doi.org/10.5281/zenodo.8314348)) is the better product on
paper: five algorithms — Eppley-VGPM, Behrenfeld-VGPM, Behrenfeld-CbPM, Westberry-CbPM,
Silsbe-CAFE — on one set of OC-CCI v6 inputs, 1998–2022.

It was evaluated and rejected for this pipeline:

* Distributed **only** as five monolithic 8-day `.nc.zip` archives, 2.4–4.5 GB each,
  **20 GB total**. There is no monthly version on Zenodo.
* Zenodo serves HTTP ranges (verified: `206`), but the zip members are **deflate**
  (method 8, ZIP64 streaming), so no byte range can reach a single year — extracting 2019
  requires transferring the whole archive.
* Only 25 km, against 1/12° for OSU, which matters on narrow shelves.

OSU preserves the property that makes an ensemble meaningful — one input chain, so the
spread is algorithm choice — at 1/12° and one small file per model-month. If the OC-CCI
product is ever wanted, everything downstream of `read_model()` is grid-agnostic: add a
source module and a grid entry.

### 2.4 Sea Around Us regions and reference values

Polygons: `https://api.seaaroundus.org/api/v1/<layer>/` returns
`{"meta": …, "data": <FeatureCollection>}` with `region_id` and `title` per feature
(lme 1.4 MB, highseas 151 kB, eez 2.5 MB).

Published metrics: `https://api.seaaroundus.org/api/v1/<layer>/<id>` — **no trailing
slash**. With a trailing slash the API returns only its own metadata, which is a silent
trap: the request succeeds and contains no data. The `data.metrics` array holds
`LME area` / `HighSeas area` / `EEZ area`, `Shelf Area`,
`Inshore Fishing Area (IFA)`, `Tropical Coral Reefs` (% of world) and
`Primary production` (mg C m⁻² d⁻¹). There is no bulk endpoint — one request per region.

SAU's published NPP is a **1998–2007 SeaWiFS 9 km climatology**: a sanity check, not
truth. Their published *areas* also disagree with their own polygons for several revised
Arctic LMEs (LME 18: metric 315 069 km² vs polygon 1 377 425 km²; LME 65 Aleutian Islands:
metric 982 382 vs polygon 212 055). **Prefer areas measured from the polygons**, which is
what this pipeline reports.

---

## 3. Grids and geometry

### 3.1 Cell area

```
A(φ) = R² · Δλ · (sin φ_top − sin φ_bottom),   R = 6 371 007.181 m  (WGS84 authalic)
```

Exact on a sphere; summed cell areas reproduce Earth's surface area to 7 significant
figures (validated in `tests/`). A constant cell area over-weights the poles by up to 25×.

### 3.2 The only regridding

The 4 km grid is **exactly twice** the 1/12° grid and shares its origin, so the reduction
is a 2×2 block mean over valid cells — no interpolation, no resampling library, no
introduced smoothing. `npp.grids.to_grid` refuses any non-integer factor and refuses
upscaling outright, since that would invent detail the product does not have.

Verified orientation for both products: **row 0 is the northernmost row**. The test is
seasonal, not geographic — in January 2019 the OSU field has 0.0% valid data in
+70…+90° and 89% valid in −50…−70°, which is only consistent with row 0 at the north
pole. (A land/ocean spot check is symmetric and cannot distinguish the two.)

### 3.3 Polygon repair — two traps

**Antimeridian.** The SAU LME GeoJSON contains longitudes down to **−188.6°**: some parts
were unwrapped westward past the dateline instead of split at it. Clipping naively to
[−180, 180] deletes those parts silently. Every geometry is therefore translated by 0 and
±360°, each copy clipped to the world box, and the union taken
(`npp.regions.clean_geometry`). Affected: LME 1 East Bering Sea, LME 54 Northern
Bering–Chukchi, LME 65 Aleutian Islands.

**Topology.** 43 of 66 LME features and 4 of 18 high-seas features fail `is_valid` as
delivered, and exactextract raises `Mixed-type geometries not supported` on geometry
collections. Each feature goes through `shapely.make_valid` and is then reduced to a
MultiPolygon of its positive-area polygonal parts.

### 3.4 Fractional coverage

`exactextract` gives the exact fraction of each grid cell inside each polygon. Stored
sparsely as `(cid int32, cov float32, ridx int16)`.

**Do not use centroid-in-polygon.** Along a coastline the error is about half a cell, and
coastlines are where the production is.

Validation: rasterised polygon areas reproduce geodesic areas (`pyproj.Geod`) to **0.02%**
for the LME set (83.87 vs 83.85 M km²).

Regions *within* a layer are stored independently, so genuine same-layer overlaps (present
in the EEZ layer) are preserved rather than collapsed.

---

## 4. Completing the year (the gap fill)

A plain sum over the months a satellite happened to see is **not** an annual total. Two
Arctic regions come out a factor of ten low; the North Sea loses 11%. But the naive answer
is also what most published regional NPP numbers are, so every stage is switchable and
every category is reported separately.

### 4.1 The water mask

A cell belongs to a region's water mask if the reference product retrieved a value there
in **any month of any `window_years`** (default: target year ± 2). That mask is then the
integration area in **all twelve months**, which is what makes the annual total complete.

Cells never seen in the whole window — the permanent pack ice of the central Arctic — stay
outside it. That keeps those regions' water areas conservative rather than inventing
production under multi-year ice.

### 4.2 The hierarchy

Stages run in order; each sees only what the previous could not supply.

| stage | rule | config |
|---|---|---|
| `obs` | the target year's own retrieval | always |
| `dark` | **no sunrise on any day of that month at that latitude → 0.** A physical zero, not a gap. | `dark_is_zero` |
| `clim` | the pixel's own mean for that month over the donor years, rescaled by the region-month ratio of target year to climatology measured where both exist (clipped to `anomaly_clip`) so the fill carries the target year's anomaly | `use_climatology`, `anomaly_rescale` |
| `nn_near` | never retrieved that month in any window year, but a valid cell lies within `nn_split_km`; its value scaled by the ratio of TOA insolation so light is never borrowed from a brighter latitude | `use_nearest_neighbour` |
| `nn_far` | the same rule beyond that distance — in practice the interior of the pack ice, where an ice-edge value is an **over-estimate** | `nn_far_in_central` (default **false**) |

Distinguishing `dark` from a data gap is the single most important part of this. Filling
polar night from anywhere else invents production that physically cannot exist. Solar
declination and the eccentricity factor use Spencer (1971) Fourier fits
(`npp/solar.py`); "no sunrise" is `−tan φ · tan δ ≥ 1` on every day of the month.

The nearest-neighbour search is a `scipy.ndimage.distance_transform_edt` on a
longitudinally padded copy (`nn_wrap_pad` = 240 columns each side) so a cell just east of
the dateline can be served by one just west of it. Index-space distances are converted to
km with the target latitude's own cosine.

**The insolation cap is what makes the spatial fill defensible**: `ratio =
clip(Q_toa[target] / Q_toa[source], 0, 1)` — never scale a borrowed value *up*.

### 4.3 Which combination is "central"

`central = obs + dark + clim + nn_near` by default. `npp_all_fills` (including `nn_far`) is
an upper bound; `npp_no_nn` (obs + dark + clim) has no spatial fill at all;
`npp_observed` is the naive sum. All four are always in the output, so a downstream user
can pick a different definition without re-running anything.

### 4.4 What the fill is worth (2019, validated)

| | % of NPP | % of water area |
|---|---|---|
| `obs` | 97.2 | 90.0 |
| `dark` | 0.00 | 0.86 |
| `clim` | 0.64 | 0.81 |
| `nn_near` | 0.84 | 1.86 |
| `nn_far` | 1.30 | 6.44 |

**The fill is inert where the data were already good** — across the 52 of 84 LME/high-seas
regions already >95% observed, it changed the total by 0.17% on average and 2.2% at most.
It is decisive only in the Arctic and around Antarctica. Two regions (Central Arctic Ocean
LME 64, Arctic Sea high seas 18) are more fill than observation and should be read as
order-of-magnitude only; `area_obs_pct` flags them.

An independent check: the same integration on the 2017–2021 mean field
(`npp_mean_year_tC_yr`) lands within 2% of the gap-filled 2019 figure.

---

## 5. Zonal integration

`npp/aggregate.py`. Three details that change the answer materially:

1. **Weight each month by its own length.** Monthly fields are daily *rates*; averaging
   the twelve rates and multiplying by 365 biases the year.
2. **Use the real cell area** (§3.1).
3. **Use fractional coverage** (§3.4).

Accumulated per `(month, region, fill-category)` into
`work_dir/baseline_<year>_<grid>.npz`, so the definition of the central estimate is a
reporting choice rather than a re-run.

The anomaly factor is a per-region-per-month quantity, so `npp/fill.py` deliberately
returns the **unscaled** climatology and `npp/aggregate.py` applies the factor once the
region is known.

---

## 6. The five-algorithm ensemble

### 6.1 One grid, one mask

All models are integrated over the **same pixels of the same grid** (default `12th`) —
those where **every** model has a retrieval that month (the *common mask*, 43–54% of the
globe by month in 2019). Without this, a model with more aggressive cloud masking looks
less productive for a reason that has nothing to do with its photosynthesis
parameterisation.

The reference model is regridded to the ensemble grid by the 2×2 block mean (§3.2).

### 6.2 Carrying the spread onto the baseline

Common-mask totals are the clean comparison but exclude the gaps §4 took trouble to fill.
So the ensemble's contribution is a set of **ratios**:

```
scaled[model] = baseline_central[region] × common[model] / common[reference]
```

giving five absolute estimates at the resolution and completeness of the best product.

**Fallback.** If the common mask covers less than `min_common_mask_pct` (default 5%) of a
region's water area, ratios are taken from **own-coverage** totals over whichever models
cover the region at all, and `ensemble_basis` records `"own coverage"`. If even the
reference has nothing, only the baseline survives (`"baseline only"`). Every row carries
`ensemble_basis`, `n_models` and `common_area_pct_of_water`.

In 2019: 347 of 366 regions use the clean common mask; at the 25th percentile it still
covers 93% of a region's water area. The 19 fallbacks are the Black Sea LME + 5 Black Sea
EEZs (3 models), the 5 Persian Gulf EEZs (4 models), and 3 tiny water bodies (reference
only).

### 6.3 Results to reproduce (2019)

Global, common mask, Pg C/yr:

| Antoine–Morel | VGPM | Eppley-VGPM | CbPM2 | CAFE |
|---|---|---|---|---|
| 48.83 | 45.52 | 48.19 | 54.60 | 53.28 |

All within published literature ranges. Scaled onto the gap-filled baseline, Pg C/yr:

| system | water area | Antoine–Morel | VGPM | Eppley-VGPM | CbPM2 | CAFE |
|---|---|---|---|---|---|---|
| 66 LMEs | 77.42 M km² | **18.49** | 18.11 | 21.04 | 20.34 | 13.24 |
| 18 high seas | 217.93 M km² | **24.63** | 23.71 | 22.05 | 28.63 | 31.99 |
| 282 EEZs | 144.21 M km² | **27.82** | 25.12 | 29.91 | 29.73 | 24.41 |

### 6.4 What the spread means

**Algorithm choice dominates every other uncertainty here by an order of magnitude.**

| uncertainty source | effect on regional totals |
|---|---|
| **algorithm choice** | **median spread 59% of the median (LMEs), 48% (high seas), 71% (EEZs); CV 20–27%** |
| gap filling the year | 1–2% system-wide, ≤2.2% where already well observed |
| agreement with SAU's published values | +5% (LMEs), +1% (high seas), +19% median (EEZs) |

And it is **structural, not noise**: CAFE puts 28% *less* production in the LMEs than
Antoine–Morel and 29% *more* in the high seas; Eppley-VGPM does the reverse. The models
disagree less about the global total than about *where* the production is — which is
exactly the axis a fisheries denominator depends on. A denominator built on CAFE gives a
PPR ratio ~1.6× higher than one built on Eppley-VGPM for the same catch.

Widest disagreement is in optically complex or seasonally extreme water — Baltic Sea 169%,
Kara Sea 158%, Laptev Sea 145%, Guinea Current 128% — consistent with
[Saba et al. 2011](https://doi.org/10.5194/bg-8-489-2011), who tested 21 ocean-colour NPP
models against 1156 in-situ ¹⁴C measurements and found water-column depth (distance to
coast) to be the *primary* influence on model skill, worse shallower than 250 m, **even
when in-situ chlorophyll was supplied as input**. Tightest agreement is open subtropical
water: Indian Ocean Western 22%, Kuroshio 25%.

Antoine–Morel is the extreme in only 15 of 84 LME/high-seas regions — a useful property
for a central estimate.

**This band is a lower bound on total uncertainty**: four of the five share one MODIS
input chain, so sensor and atmospheric-correction error is largely common to them. A
structurally independent check (e.g. the NEMO-PISCES biogeochemical hindcast, which is not
an ocean-colour algorithm at all) would widen it honestly.

---

## 7. ⚠ The three region systems overlap

**This is the easiest way to get a wrong answer from these data.** Measured on the same
raster (`npp/overlap.py`, `region_system_overlap.csv`):

* **51.6% of total EEZ area lies inside an LME** (146.18 M km² total, 75.50 inside an
  LME). Strongly bimodal: median 97.9%, 25th percentile 19.9% — continental EEZs are
  ~100% inside an LME (Australia 99.4%, China 99.8%), oceanic island EEZs are 0% (French
  Polynesia, Micronesia, Mauritius, Cook Islands).
* **5.3% of high-seas area lies inside an LME.** The Arctic Sea high-seas area is
  **99.99%** inside the Central Arctic Ocean LME — almost entirely duplicated.
* 24 of 66 LMEs extend past the EEZ limit into the high seas: 7.4 M km² carrying
  **1.05 Pg C/yr**. Adding an LME total to a high-seas total double counts that.
* 0.7% of high-seas area also falls inside an EEZ (boundary/version slop).

Overlap per cell is `min(coverage_a, coverage_b) × cell_area` — exact wherever one region
nests inside the other within a cell, which is the normal case at 4 km for regions this
large, and an upper bound on the rare cells where two regions occupy genuinely different
parts of one cell.

### The 2019 budget on union geometries

| piece | area (M km²) | NPP (Pg C/yr) | share of global |
|---|---|---|---|
| LME inside an EEZ | 70.01 | 17.44 | 33.4% |
| **LME inside the high seas** | 7.41 | **1.05** | 2.0% — double counted if you add |
| high seas outside any LME | 210.52 | 23.58 | 45.1% |
| EEZ outside any LME | 69.00 | 9.45 | 18.1% |
| inland & unassigned water | 1.58 | 0.76 | 1.4% |
| **global ocean** | **358.52** | **52.28** | 100% |

`LME ∪ high seas` (overlap removed once) = 42.07 Pg C over 287.9 M km² = **80.5%** of
global NPP. The residual ~18% is EEZ water outside any LME, confirmed directly by
rasterising all 282 EEZ polygons. The remaining 1.4% is **large inland water bodies** the
ocean-colour product covers but SAU's marine system does not — the Great Lakes, the
Caspian, and slivers on disputed EEZ boundaries.

**Recommendation.** Build the denominator on the **EEZ + high-seas** partition: it is
disjoint by construction (SAU defines the high seas as FAO areas minus EEZs) and closes to
the global total. Use LMEs as a reporting aggregation with the overlap subtracted
explicitly.

---

## 8. Benthic production — optional, off by default

`npp/benthic.py`, `benthic.enabled: false`. **Nothing in the main outputs depends on it.**

Ocean colour measures phytoplankton in the water column. It does not see the kelp,
seagrass, salt marsh, mangrove or benthic diatoms on the seabed underneath. On broad
sunlit shelves that is not marginal — on this estimate it adds ~26% to pelagic NPP in the
Gulf of Thailand, ~22% in the South China Sea, ~21% on the North Australian Shelf and in
the East China Sea, and ~9% across the LME system as a whole (1.75 Pg C/yr, range
1.29–2.44).

### What is in, with sources

| habitat | global NPP (Pg C/yr) | global area | source | data quality |
|---|---|---|---|---|
| macroalgae | **1.32** (1.00–1.80) | 6.06–7.22 M km² | [Duarte et al. 2022](https://doi.org/10.1111/geb.13515); rates [Pessarrodona et al. 2022](https://doi.org/10.1126/sciadv.abn2465) | **niche model**, not observed extent — and 3/4 of the total |
| microphytobenthos | 0.42 (0.30–0.60) | ~8.35 M km² photic shelf | Cahoon 1999 review; photic fraction 33% of shelf from [Gattuso et al. 2006](https://doi.org/10.5194/bg-3-489-2006) | **no global map exists** |
| mangrove | 0.218 ± 0.072 | 0.147 M km² | [Bouillon et al. 2008](https://doi.org/10.1029/2007gb003052); area [Bunting et al. 2022](https://doi.org/10.3390/rs14153657) | good — observed, annually updated |
| seagrass | 0.064 (0.045–0.110) | 0.160 M km² (up to 0.267) | [McKenzie et al. 2020](https://doi.org/10.1088/1748-9326/ab7d06); rate Duarte & Chiscano 1999 | patchy, very uneven national coverage |
| salt marsh | 0.066 (0.045–0.120) | 0.055 M km² | [Mcowen et al. 2017](https://doi.org/10.3897/BDJ.5.e11764) | patchy — 43 countries only |

### What is deliberately out

* **Coral reefs.** Gross production is ~0.7 Pg C/yr but **net community production is near
  zero** (Gattuso et al. 1998): almost all of it is recycled inside the reef and never
  leaves. Adding it would count energy that goes nowhere. Reported in its own column for
  context — in the Great Barrier Reef LME reef gross PP is 39.5% of pelagic NPP, which is
  tempting and wrong.
* **Terrestrial / riverine carbon.** Rivers deliver ~0.9 Pg C/yr to the ocean, but ~70% of
  the particulate organic fraction is remineralised within estuaries and isotopic tracers
  find **very little terrestrial organic carbon in the global ocean** or in marine
  consumers ([Bianchi 2011](https://doi.org/10.1073/pnas.1017982108)). It is a local
  subsidy in river-plume systems, not a term in a global denominator. Mangrove outwelling
  is already inside the estimate above.

### Allocation, and why it is only first order

Global habitat totals are distributed across LMEs by shelf area (macroalgae,
microphytobenthos), inshore fishing area (mangrove, seagrass, salt marsh) or SAU's own
coral share, each scaled by a **light index**: annual mean TOA insolation at that latitude
over the global ocean mean, times the ice-free lit fraction of the year taken from the
pipeline's own retrieval coverage.

That scaling is not cosmetic. Without it, raw shelf area gave the Canadian High Arctic
**191% of its pelagic NPP** in kelp forests — on ice-covered shelves. The resulting
pattern is shelf geometry × light, not latitude.

**The rigorous replacement** is to overlay the actual habitat rasters — Global Mangrove
Watch v3, UNEP-WCMC seagrass and salt marsh, the Duarte et al. 2022 macroalgal layer,
UNEP-WCMC or Allen Coral Atlas reefs — on the same grid and the same regions, exactly as
the pelagic pipeline does. That turns a factor-of-two guess into a measured area × a
literature rate. Most of those datasets sit behind download forms (UNEP-WCMC requires
accepting terms), which is why it has not been done yet.

### Trophic availability, and a convention warning

The five sources are not interchangeable currency.
[Duarte & Cebrián 1996](https://doi.org/10.4319/lo.1996.41.8.1758) compiled the fate of NPP
by autotroph type: herbivory takes **>40% of microalgal** production and **33.6 ± 4.9% of
macroalgal**, but much less of the vascular plants, whose production is
disproportionately buried (marine angiosperms are 4% of ocean NPP but 30% of the carbon
stored in marine sediments). Kelp additionally exports 24–44% of production as drift and
particulate detritus (Krumhansl & Scheibling 2012, 8–2657 g C m⁻² yr⁻¹).

Applied availability fractions: microphytobenthos 60%, macroalgae 50%, mangrove 30%,
seagrass 25%, salt marsh 15%. That cuts the benthic total from 1.75 to 0.84 Pg C/yr
(4.6% of LME pelagic).

**⚠ Convention.** Classical PPR (Pauly & Christensen 1995) uses **unweighted** total NPP as
its denominator and puts transfer efficiency on the catch side. Adding an
availability-weighted benthic term to an unweighted pelagic denominator mixes two
conventions. Either add raw to raw (+9%), or weight both sides — which would also *reduce*
the pelagic denominator, since much oceanic phytoplankton production is respired by
microbes before reaching metazoans. Both columns are provided; pick one and say which.

Seagrass, marsh and mangrove matter to fisheries mostly as **habitat and nursery**, not as
carbon. Microphytobenthos and macroalgae are the ones with a real carbon route to fish.

---

## 9. Outputs

Written to `out_dir`:

| file | contents |
|---|---|
| `npp_<year>_baseline_by_region.csv` | one row per region: gap-filled totals, all four variants, per-stage accounting, SAU comparison |
| `npp_<year>_baseline_monthly.csv` | region × month: central and observed carbon, rate, per-stage area shares, anomaly factor |
| `npp_<year>_ensemble_by_region.csv` | five models per region: common-mask, own-coverage and scaled totals, median/min/max, spread, CV, basis, `n_models` |
| `region_system_overlap.csv` | pairwise overlap between the three systems, per region |
| `benthic_<year>_by_LME_firstorder.csv` | optional; per-LME benthic estimate by habitat |
| `summary_<year>.txt` | the console summary |
| `NPP_<year>_SAU_regions.xlsx` | README / Summary / Ensemble / Baseline / Overlap / Monthly (+ Benthic_LME if enabled) |

Intermediates in `work_dir` (safe to delete; expensive to rebuild):
`coverage_<layer>_<grid>.npz`, `watermask_<grid>_<years>.npy`,
`baseline_<year>_<grid>.npz`, `ensemble_<year>_<grid>.npz`.

Derived cells in the workbook (medians, ranges, spreads, system totals) are **formulas**,
not Python-computed literals, so it recalculates and a reader can see the derivation.

---

## 10. Reproducing / extending — notes for the next agent

**Run order.** `regions` → `fetch` → `baseline` → `ensemble` → `overlap` → (`benthic`) →
`workbook`. Or `npp all`. Every stage is resumable: anything on disk is reused unless
`--overwrite`.

**Cost.** ~1.6 GB of raw data per year for the ensemble, plus ~780 MB per extra window
year for the fill climatology (default window = 5 years ≈ 3.9 GB). Baseline is ~50 s per
month on the 4 km grid with all three layers, peak RSS ~4 GB. Ensemble ~15 s per month.

**Changing the year** is `--year`, and the window follows unless the config pins
`window_years`. Copernicus covers 1997→present; OSU MODIS R2022 covers mid-2002→2023, so
before ~2003 you must switch the OSU directories to the SeaWiFS variants
(`vgpm.r2022.s.chl.a.sst`, `cafe.seawifs.r2022`, …) in `npp/sources/osu.py`, and note that
they are then a *different* input chain from the MODIS ones.

**Turning the fill off** to reproduce a conventional "observed months only" number:
```yaml
fill: {dark_is_zero: false, use_climatology: false, use_nearest_neighbour: false}
```
`npp_central_tC_yr` then equals `npp_observed_tC_yr`.

**Adding a model.** Write a module in `npp/sources/` exposing `NATIVE_GRID`, `local_path`,
`fetch` and `read` (returning a 2-D float32 array on that grid, NaN for no data), register
it in `npp/sources/__init__.PROVIDER` and in `config.MODELS`/`MODEL_LABELS`, and add its
grid to `npp.grids` if it is new. Everything downstream is model-agnostic. If the new grid
is not an integer multiple of an existing one you will need a real conservative regridder
(`xesmf`); do not silently interpolate.

**Adding a region system.** Any SAU layer name works if the API serves
`/api/v1/<layer>/`; add it to `config.LAYERS`. For non-SAU polygons, drop a GeoJSON with
`region_id` and `title` at `raw_dir/sau_<layer>.geojson` and the rest works unchanged.

**Environment gotchas found the hard way.**
* `openpyxl` writes `float('nan')` as a literal that Excel and LibreOffice read as
  `#VALUE!`. Convert NaN to `None` before writing (`npp/workbook.py::_clean`).
* `pyhdf` cannot read a file object — the gzip must be expanded to a real path.
* On a machine whose egress is restricted, none of these hosts may be reachable. The
  original 2019 run had to route every download through a browser on a separate machine.
  The code assumes plain HTTPS; if that fails, fetch the raw files by any means and drop
  them in `raw_dir` under the canonical names (`copernicus.local_name`, `osu.local_name`)
  — both `local_path` helpers accept a flat `raw_dir` as well as `raw_dir/<source>/`.
* Chrome blocks multiple programmatic downloads per origin, which silently drops
  everything after the first. Irrelevant to the code, relevant to anyone re-fetching by
  hand.

**Validation checklist for a re-run** (2019 numbers, §4.4, §6.3, §7):
1. `Grid("4km").total_area_m2() ≈ 5.1007e14 m²`.
2. Rasterised LME polygon area 83.87 M km², within 0.05% of the geodesic area.
3. Global common-mask totals per model within 0.05 Pg C of §6.3.
4. LME / high seas / EEZ water areas 77.42 / 217.93 / 144.21 M km².
5. Fill composition within 0.05 pp of §4.4.
6. EEZ union + high-seas union + inland residual ≈ global total (§7).

`tests/test_smoke.py` covers 1, the area/regrid/solar invariants and the antimeridian
repair without needing any data; 2–6 need the raw files.

---

## 11. Citation

Primary production: E.U. Copernicus Marine Service, *Global Ocean Colour
(Copernicus-GlobColour), Bio-Geo-Chemical, L4, monthly primary production, 4 km*, product
`OCEANCOLOUR_GLO_BGC_L4_MY_009_104`. Ocean Productivity, Oregon State University
(VGPM, Eppley-VGPM, CbPM2, CAFE; MODIS R2022). Region geometries and reference
primary-production values: Sea Around Us, University of British Columbia
(seaaroundus.org) — see their citation policy.
