# PPREstimation

Fish biomass / **PPR** (Primary Production Required) estimation from Ecopath marine
ecosystem models. Given a mass-balanced food web, the tool computes **SPPR** (Specific
Primary Production Required) for every functional group and rolls it up into
ecosystem-level footprints — total PPR appropriated by the catch and %PPR relative to
net primary production.

## What it does

SPPR is the amount of primary production required to sustain one unit of a group's
production. PPREstimation estimates it with several methods, from classic
trophic-level approximations (Pauly & Christensen 1986; Christensen & Pauly 1995) to
modern flow-network solvers that trace production through the full diet matrix, handle
detritus recycling, and support uncertainty propagation. Weighting each group's SPPR by
its catch yields the ecosystem PPR footprint.

See [`SPPR_Methods.md`](information/SPPR_Methods.md) for the full method catalog and math.

## Project structure

- `PPRCalculator.py` — central computation class; SPPR methods, PPR/NPP aggregation, detritus solving.
- `ModelData.py` — model loading, species-group management, diet/detritus-fate matrices.
- `utils.py` — matrix utilities and Ulanowicz cycle removal (`remove_cycles`).
- `create_PPRS_excel.py` — batch exporter; runs every SPPR method over a directory of models and writes one multi-sheet Excel workbook per model, plus a reader that loads them back.
- `real_models/` — JSON model data (EwE parameters, species groups, diet matrices).

## Usage

```python
from PPRCalculator import PPRCalculator

# Load and mass-balance a model by its number (or JSON filepath).
model = PPRCalculator(227, use_ee_floor=True, ee_floor=0.1)

print("groups:", model.n_groups)
print("balanced?", model.is_model_balanced()[0])

# Classic trophic-chain method (per-group SPPR).
sppr_1995 = model.SPPR_1995(global_TE=0.1)

# Full flow-network solver; returns (SPPR, A, L).
sppr_new, A, L = model.SPPR_new(TE_option='GE')

# Is that result trustworthy? One call grades the input data, both convergence
# conditions, and the PP budget. return_sppr=True reuses the same solve.
report, sppr_new, A, L = model.diagnose_sppr(return_sppr=True)
print("status:", report['status'])          # 'OK' | 'WARN' | 'FAIL'
print(report['warnings'])

# Ecosystem footprint: total PPR appropriated by the catch (1-row DataFrame).
ppr = model.get_PPR(sppr_new)
print("total PPR:", ppr.sum(axis=1).sum())

# Uncertainty propagation over transfer efficiency. Pick the solver with `kind`, give it
# its own parameters with `method_kwargs`, and drop draws whose TE sample pushed the
# recycling gain past divergence (which a negative-SPPR test alone can miss).
mean, samples, reject_frac, _, _, diag = model.monte_carlo_SPPR(
    n_samples=200, kind='new', TE_option='TE',
    method_kwargs={'fix_EE_0_cases': True},
    exclude_diverged=True, return_diagnostics=True)
print(f"rejected {reject_frac:.0%}: "
      f"{diag['n_rejected_diverged']} diverged, {diag['n_rejected_negative']} negative")
```

Both constructors default to `use_ee_floor=True, ee_floor=0.1, ee_threshold=0.1`; pass
`use_ee_floor=False` to preserve the preceding audited numerical behavior.
`ee_threshold` selects groups with pre-floor EE strictly below that value;
`ee_floor` is their replacement EE. For example, `ee_threshold=0.1, ee_floor=0.95`
sets eligible groups below 0.1 to 0.95, while groups at or above 0.1 retain their EE/M0.
The existing invalid-input and nonnegative-export checks still apply; a replacement
requiring an external source instead of a sink is skipped with its diagnostic reason.
`from_dict` inherits both saved settings unless explicitly overridden. Both settings
are recorded in initialization and diagnostic configuration. The floor is applied once after
completed loading/LIM to eligible real living groups, including primary producers. It
preserves living flows and catch, reduces effective `M0`, and records the removed mortality
as `external_mortality_export`, a hypothetical nonfishery sink. Reduced mortality plus
egestion remain fate-routed to detritus, whose inflows/export/stock residuals are refreshed.
Negative detritus stock residuals remain explicit limitations. Balance accounting includes
the weighted sink; fishery PPR still weights SPPR by catch alone. Both EE values must be finite
numbers in `[0, 1]`, excluding Booleans. Preserve source, pre-floor and effective EE/M0 in
the ledger; floor settings are constructor flags, not SPPR-method flags. The project
[EE-floor contract](../../skills/paper-to-ppr/references/ee-floor.md) governs migration,
archived-loader upgrades, dependency-specific reruns and historical review evidence.

### Batch export

`create_PPRS_excel.py` runs the canonical `ALL_METHOD_KEYS` inventory (currently 22 configurations) over a directory of models
and writes **one workbook per model** into the output directory, alongside a plain-text
run report listing every warning, skipped method and Monte-Carlo rejection:

```bash
# defaults to real_models/EwE_jsons -> output/
python create_PPRS_excel.py [json_dir] [out_dir] [--resume] [--timeout SECONDS]
```

Each workbook holds eight sheets: `groups_df` (per-group parameters); `sppr_PP`,
`sppr_inner` and `sppr_all` — the same flat groups × methods table under three source
scopes (primary producers only; within-system, i.e. adding detritus; and every source,
adding import); `model_health` (`diagnose_sppr` per `TE_option`), `footprint` (PPR and
%NPP per method), `mc_diagnostics` (Monte-Carlo accept/reject breakdown) and `run_notes`
(the conventions needed to read the numbers correctly).

### Per-method time budget

Every method — and every `diagnose_sppr` row — runs in a worker process with a wall-clock
budget, **180 s by default**. The heavy methods (`SPPR_EwE`'s path enumeration, the
Monte-Carlo drivers) can run for hours on a large food web, and once they are down in
numpy/sympy there is no way to interrupt them from inside the interpreter — so a method
that overruns has its worker killed, is left NaN and is recorded as a *timeout*, and the
export moves straight on to the next method. One worker is shared by the whole directory,
so the budget costs a single process spawn, not one per model.

A timeout is not a failure of the method, and the workbook keeps the two apart: the
`status` column of the `run_notes` sheet says `ok` / `failed` / `timeout` / `crashed` per
method, and the run report gives the reason in full. Rerun with a larger budget before
reading anything into a timeout.

```bash
python create_PPRS_excel.py real_models/EwE_jsons output --timeout 600  # 10 minutes
python create_PPRS_excel.py real_models/EwE_jsons output --timeout none # no budget at all
```

```python
cpe.run_directory('real_models/EwE_jsons', 'output', method_timeout=600)
cpe.run_directory('real_models/EwE_jsons', 'output', method_timeout=None)  # in-process
```

From Python you can run a subset and read the result back:

```python
import create_PPRS_excel as cpe

# Skip the heavy path-enumeration method while iterating.
summary = cpe.run_directory('real_models/EwE_jsons', 'output',
                            method_keys=cpe.FAST_METHOD_KEYS)
print(summary['n_written'], 'workbooks;  report:', summary['report'])

tables = cpe.read_pprs_excel('output/435_435_Black_Sea_(1990).xlsx')
tables['sppr_all']['new_GE']    # total SPPR per group for one method
tables['sppr_PP']['new_GE']     # the primary-producer-only share
```

Throughout the workbook **NaN means "not available", never zero** — a method that raised,
one that ran out of time, and a value that cannot be attributed to the sheet's source
scope all stay empty.
`SPPR_1986` and `SPPR_1995` return a single un-attributed SPPR, so they are blank in
`sppr_PP` while carrying their total in `sppr_inner` and `sppr_all`.

## Setup

Requires Python 3.10+ and the scientific Python stack: `numpy`, `pandas`, `scipy`,
`sympy`, `igraph`, `tqdm`, and `openpyxl` (the Excel engine used by the batch exporter).
There is no packaged dependency file yet; install these manually, e.g.:

```bash
pip install numpy pandas scipy sympy igraph tqdm openpyxl
```

Tests are plain `pytest`:

```bash
python -m pytest tests/ -q
```

Note that `PPRCalculator` imports `tqdm.notebook`, so calling `SPPR_EwE` or
`monte_carlo_SPPR` with `silent=False` outside Jupyter raises unless `ipywidgets` is
installed. Pass `silent=True` in scripts — `create_PPRS_excel.py` already does.

### Known test failures

The historical repository-integration run of `pytest tests/` reported
**1 failed, 76 passed, 18 errors**. This record is not a current EE-floor test result:

- **18 errors** in `tests/test_diagnose_sppr.py` and `tests/test_monte_carlo_sppr.py`
  are `FileNotFoundError`s: their fixture model,
  `real_models/new_EwE_jsons/62_10062_Black_Sea_(1960-1969).json`, was part of the
  `real_models/new_EwE_jsons/` directory, which was deliberately removed. The affected
  assertions depend on that specific model's scientific properties (convergence
  behaviour, `EE=0` groups, TE matrices), so the tests are not repointed at a
  substitute fixture — that is a call about the algorithm's own test data, not one to
  make as part of moving files around.
- **1 failure**, `test_registry_holds_the_nineteen_specified_methods` in
  `tests/test_create_pprs_excel.py`, asserts exactly 19 registered SPPR methods; the
  registry then held 20. The current canonical inventory holds 22; this historical
  assertion/result is not the inventory contract.

## Documentation

- [`SPPR_Methods.md`](information/SPPR_Methods.md) — deep reference on every SPPR method and the underlying mathematics.
- [`USER_GUIDE.md`](information/USER_GUIDE.md) — practical guide to `ModelData` and `PPRCalculator`, with an end-to-end example.
