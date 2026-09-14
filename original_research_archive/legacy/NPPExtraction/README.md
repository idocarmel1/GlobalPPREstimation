# ppr-npp

Satellite net primary production, aggregated to Sea Around Us regions.

The supplied single-year package targets **66 Large Marine Ecosystems**,
**18 high-seas areas** and **282 EEZs**, using up to **five ocean-colour algorithms**,
with a switchable gap-fill so the annual total covers the whole year rather than only the
months a satellite happened to see.
The algorithms share satellite inputs and are not statistically independent.

Built as the denominator for primary-production-required (PPR) work.

**For the GlobalPPREstimation annual workflow, start with
[`ANNUAL.md`](ANNUAL.md).** It includes Windows/Linux fresh-checkout installation,
source discovery, resumable extraction, and the canonical annual output contract.
The published history covers **all 366 ecosystems over 1998–2019**, independently
of catch or article availability. The [expansion publication proof](output/regional_expansion/publication_verification.json)
records exact preservation of all 11,310 earlier rows. The earlier
[`output/extraction_coverage.json`](output/extraction_coverage.json) is the historical
archive-subset audit. The fixed global-atlas union also has all 22 annual records;
see [its definition](../docs/GLOBAL_ATLAS_NPP_REFERENCE.md).
The 366-region figures and percentages below describe the supplied **2019 reference
run**, not measured percentages for every year of the expanded annual history.

**Read [`METHODS.md`](METHODS.md) before using the numbers.** It records every data source
with its exact URLs, the formulas, every parameter, the traps that produce wrong answers
silently, and the figures a re-run should reproduce.

---

## Install

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[test]"
```

Needs Python ≥ 3.11. `pyhdf` requires the HDF4 libraries; on Debian/Ubuntu
`apt-get install libhdf4-dev` first if the wheel does not cover your platform.

## Run

```bash
cp config.example.yaml config.yaml     # then edit year / paths / fill options

python -m npp.cli regions              # SAU polygons -> exact fractional coverage
python -m npp.cli fetch                # ~1.6 GB for the ensemble year + ~780 MB per window year
python -m npp.cli baseline             # gap-fill the year, integrate per region
python -m npp.cli ensemble             # five-model comparison, scaled onto the baseline
python -m npp.cli overlap              # how much the three region systems overlap
python -m npp.cli workbook             # the Excel deliverable

# or all of it:
python -m npp.cli all -c config.yaml
```

Stages reuse compatible cached outputs; changes to scientific configuration or inputs
can require recomputation. `--overwrite` forces regeneration.
`--year 2015`, `--layers lme,eez`, `--raw-dir …` override the config from the command line.

Programmatic use:

```python
from npp.config import Config
from npp.aggregate import run_baseline
from npp.report import baseline_table

cfg = Config.load("config.yaml", year=2019)
table = baseline_table(cfg, run_baseline(cfg))
```

## Outputs

In `out_dir`:

| file | contents |
|---|---|
| `npp_<year>_baseline_by_region.csv` | per region: gap-filled annual total, all four fill variants, per-stage accounting, SAU comparison |
| `npp_<year>_baseline_monthly.csv` | region × month detail |
| `npp_<year>_ensemble_by_region.csv` | five models per region: totals, median/min/max, spread, CV, which models had data |
| `region_system_overlap.csv` | pairwise overlap between LMEs, high seas and EEZs |
| `summary_<year>.txt` | console summary |
| `NPP_<year>_SAU_regions.xlsx` | README / Summary / Ensemble / Baseline / Overlap / Monthly |
| `benthic_<year>_by_LME_firstorder.csv` | only if the optional benthic module is enabled |

Key columns: `npp_central_tC_yr` is the headline number, `npp_observed_tC_yr` is the naive
sum over observed months, `scaled_<model>_tC_yr` are the five algorithm estimates. Units
are tonnes C per year (1e9 tC = 1 Pg C); rates are mg C m⁻² d⁻¹.

## Interpretation and supplied 2019 reference figures

**1. The region systems overlap — do not add them together.** About half of all EEZ area
lies inside an LME, and the Arctic Sea high-seas area is 99.99% inside the Central Arctic
Ocean LME. Adding an LME total to a high-seas total double counts 1.05 Pg C/yr. The
disjoint alternative is **EEZ + high seas**, which is how SAU defines the high seas and
which closes to the global total. See `region_system_overlap.csv` and METHODS §7.

**2. The supplied 2019 reference shows substantial algorithm spread.** Its
median per-region spread between the five models is 59% of the median for LMEs, 48% for
high seas, 71% for EEZs — against 1–2% for the gap fill. And it is structural, not noise:
CAFE puts 28% less production in the LMEs than Antoine–Morel and 29% more in the high
seas. These percentages are reference-run results, not uncertainty estimates for all
archive years. Model spread is not a statistical confidence interval. METHODS §6.

**3. Coverage is specific to the year and region.** The 1998–2002 estimates use only
Antoine–Morel. Later years schedule five models but some regions have fewer usable
retrievals, including the Black Sea and several EEZs. Inspect the actual annual
model fields rather than transferring one region's missingness to an entire sea.
The expanded canonical CSV has 5,938 five-model and 2,112 partial-model rows.
Blank model cells
mean "no data", never zero. Check `n_models` and `ensemble_basis`. METHODS §2.2, §6.2.

## The benthic module is optional and off by default

Ocean colour does not see kelp, seagrass, salt marsh, mangrove or benthic diatoms. On
broad sunlit shelves that is worth a fifth to a quarter of the pelagic total, and ~9%
across the LME system. It is a **first-order scoping estimate** — per-region values within
about a factor of two — so `benthic.enabled` defaults to `false` and **the main results
exclude it entirely**. Enable it with `benthic: {enabled: true}` or
`npp benthic --enable`. `npp/benthic.py` documents every parameter, source and exclusion;
METHODS §8 discusses what reaches a fish and the PPR convention problem.

## Configuration

`config.example.yaml` is commented. The parts that change results:

```yaml
year: 2019
window_years: [2017, 2018, 2019, 2020, 2021]   # water mask + fill climatology
layers: [lme, highseas, eez]

fill:
  dark_is_zero: true          # polar night -> 0 (a physical zero, not a gap)
  use_climatology: true       # fill from the pixel's own other-year mean for that month
  anomaly_rescale: true       # carry the target year's anomaly into that fill
  use_nearest_neighbour: true # spatial fill, scaled down by insolation ratio
  nn_split_km: 200            # beyond this it is pack ice, and an over-estimate
  nn_far_in_central: false    # so it is excluded from the headline number

ensemble:
  models: [antoinemorel, vgpm, eppley, cbpm, cafe]
  grid: 12th                  # the common grid all five are compared on
  reference_model: antoinemorel
  min_common_mask_pct: 5.0    # below this, fall back to own-coverage ratios

benthic:
  enabled: false
```

To reproduce a conventional "observed months only" number, set all three fill switches to
`false`; `npp_central_tC_yr` then equals `npp_observed_tC_yr`.

## Repository layout

```
ppr-npp/
├── README.md                     this file
├── METHODS.md                    the full reference: sources, formulas, parameters, traps
├── requirements.txt              pinned floors for every dependency
├── pyproject.toml                installable package, exposes the `npp` console script
├── config.example.yaml           commented configuration
├── npp/
│   ├── __init__.py
│   ├── cli.py                    the subcommands
│   ├── config.py                 dataclass config + YAML loading + validation
│   ├── grids.py                  grid definitions, exact cell area, block-mean regrid
│   ├── solar.py                  TOA insolation and daylight per latitude and month
│   ├── http.py                   retrying GET / resumable download
│   ├── log.py                    one-line progress logging
│   ├── regions.py                SAU polygons: download, repair, fractional coverage
│   ├── sources/
│   │   ├── __init__.py           model -> provider dispatch
│   │   ├── copernicus.py         Antoine-Morel: STAC discovery, S3 listing, NetCDF read
│   │   └── osu.py                VGPM / Eppley / CbPM2 / CAFE: URLs and HDF4 read
│   ├── fill.py                   water mask + the gap-fill hierarchy
│   ├── aggregate.py              zonal integration into per-region, per-month, per-stage
│   ├── ensemble.py               common-mask comparison + scaling onto the baseline
│   ├── overlap.py                overlap between the three region systems
│   ├── benthic.py                OPTIONAL benthic estimate (off by default)
│   ├── report.py                 the CSV tables
│   └── workbook.py               the Excel deliverable
├── reference/
│   ├── expected_2019.json        validated figures the tests check against
│   └── summary_2019_validated.txt
└── tests/
    ├── test_smoke.py             invariants, no data needed
    └── test_validation.py        compares a finished run to reference/expected_2019.json
```

## Tests

```bash
python -m pytest tests -q
```

Covers the area/regrid/solar invariants and the antimeridian repair with no data needed.
METHODS §10 has the full validation checklist against the 2019 figures.

## Data sources

Copernicus Marine Service `OCEANCOLOUR_GLO_BGC_L4_MY_009_104` (Antoine–Morel, 4 km,
monthly — **no account needed**, the native files are anonymously readable) · Ocean
Productivity, Oregon State University (VGPM, Eppley-VGPM, CbPM2, CAFE; MODIS R2022,
1/12°, monthly) · Sea Around Us, UBC (region polygons and their published NPP values).
Please follow the Sea Around Us citation policy when publishing.
