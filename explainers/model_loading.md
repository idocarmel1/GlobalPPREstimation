# Extracted model values versus the calculation model

`model.json` should represent the extracted model values, with missing values and any accepted corrections or transformations traceable to their evidence. It is not automatically the exact model used in calculations: a selected JSON can already be an accepted transformed variant, and loading changes the in-memory representation further. Each distinct variant owns its single canonical model.json and adjacent model_notes.md under the [project layout](structure.md); no redundant source-model or computational-input JSON accompanies it. The regional selection, input hash, executed code and recorded settings establish which version produced a result. The [project guide](../README.md) and [direct-diagnostics contract](../tools/skills/paper-to-ppr/references/direct-diagnostics.md) require candidate-specific settings; the defaults below are not a universal regional configuration.

The forward sequence is **selected input → parsed groups and flows → deterministic completion → optional LIM → runtime vectors → SPPR**. Inspect both source values and the resulting runtime state.

## Default settings: what they mean

The [exporter's `load_model()`](../tools/scientific_code/PPREstimation/create_PPRS_excel.py) calls `PPRCalculator.from_modeldata()` with the following effective settings. These differ from calling the [bare calculator](../tools/scientific_code/PPREstimation/PPRCalculator.py) directly.

| Setting | Exporter | Bare constructor / `from_modeldata()` | Meaning and rationale |
|---|---|---|---|
| `underdetermined` | `True` | `False` | After deterministic completion, allow optimization of remaining missing flows. This makes incomplete inputs calculable, subject to the limitations below. |
| `zero_catch` | `True` | `True` | Missing catch becomes zero, an assumption consistent with unfished groups but not evidence that an unknown catch was zero. |
| `zero_biomass_accum` | `False` | `True` | The exporter leaves missing living-group accumulation available for equation solving; the bare API assumes zero accumulation, corresponding to steady state. |
| `default_gs` | `True` | `True` | Supply a missing unassimilated-food fraction: normally 0.2 for consumers, with the small-zooplankton exception below. |
| `weight_flow`, `weight_guess` | `1`, `1` | `1`, `1` | Weight scaled minimum-flow and deviation-from-initial-guess penalties in LIM. Equal weights do not make the guesses observations. |
| `normalize_DC` | `True` | `False` in `from_modeldata()` | Divide every nonzero diet row by its sum, including imported food. This enforces relative diet fractions but changes reported fractions. The bare constructor defaults to normalize_DC=False and passes an explicit request through; it does not normalize unless requested. |
| `DC_tol` | `0.001` | `0.001` in `from_modeldata()` | Allow 0.001 absolute consumer-row deviation before a warning under normalization, or rejection without it. The code documents rounding as the rationale; a material deficit still needs source review. |
| `balance_BA_after_DC_normalization` | `True` | `True` | For an eligible living group whose raw production identity is already consistent and whose counterfactual terms are finite, offset normalization-induced predation by the negative delta in runtime biomass accumulation. Other groups retain their original runtime BA and a reason in the transformation ledger. Input ModelData/JSON remains unchanged; this is computational closure, not observed BA. |

With normalization enabled, even rows within tolerance are rescaled. An empty consumer row stays zero after normalization; this operation cannot reconstruct missing prey.

## Deterministic completion and other transformations

[ModelData](../tools/scientific_code/PPREstimation/ModelData.py) converts numeric strings and missing sentinels, classifies `pp=0/1/2` as consumer/primary producer/detritus, renames `export` to `catch`, and derives production `p=B×PB`, consumption `q=B×QB`, other mortality `M0=p×(1−EE)` and net migration `emigration−immigration`. The JSON parser recomputes other mortality from PB and EE rather than retaining an independent `other_mort` estimate.

The calculator then:

- Fills missing biomass with **1**, a numerical placeholder that does not recover biological biomass. Since flows were derived earlier, this also does not reconstruct missing production or consumption from the original rates.
- Defaults missing immigration, emigration, net migration and detritus import to zero. Runtime net migration subtracts detritus import to represent an external inflow.
- Sets nonconsumer respiration/egestion to zero and detritus/import other mortality to zero; sets detritus/import EE to 1 during deterministic completion. Detritus catch is set to zero by the JSON loader.
- Fills missing consumer GS with 0.2. Names matching a hard-coded multilingual small-zooplankton whitelist, after removing spaces, underscores and hyphens, receive 0.4. This is name matching, not taxonomic inference; existing GS values are retained at this step.
- Derives egestion `q×GS`, recomputes predation from diet-weighted consumption, and solves an equation when exactly one term is missing: `q=p+respiration+egestion` or `p=M0+catch+predation+net_migration+biomass_accum`. It recomputes efficiency ratios and rates from flows.

A synthetic `diet_import` source is added to the group table and diet matrix. Missing diet cells become zero. Detritus routing uses group-to-pool fractions. `_finalize_det_fate()` forces the DET×DET block to identity and the Import row to zero, overwriting supplied pool-to-pool routing. Completely absent living-group routing defaults to the sole pool only for a single-detritus model; absent multi-pool routing is rejected. Partial living-group routing remains as supplied, warns, and records the unrouted remainder as export. Detritus inflow, production and accumulation are recomputed; supplied detritus accumulation can therefore be replaced.

Real-group TL is initialized as missing by the JSON parser, then calculated from the loaded diet via `(I−DC)⁻¹·1`, without cycle removal at initialization. It need not reproduce a published TL.

## LIM and balancing: useful completion, limited assurance

`apply_lim()` optimizes **per group**, only missing `q`, `p`, respiration, egestion, `M0` and accumulation. It keeps known flows fixed, conditionally imposes the two balance equations, and conditionally bounds EE to 0–0.95 and GS to 0.10–0.35. Accumulation can be negative. Predation and diets are fixed during optimization. Afterwards, predation is recomputed from final consumer consumption, followed by routed detritus inflows, exports and accumulation, and then efficiency ratios and PB/QB. The group table and runtime vectors therefore reflect the post-LIM flows. This refresh can reveal living-group production residuals; it does not rebalance known biological flows or perform a coupled reconstruction of the food web.

On optimizer failure, the implementation prints a message and leaves unsolved cells missing; it does not write the initial guesses back. Runtime construction subsequently fills most missing flow vectors with zero and missing EE/GE with one. These fallback values require explicit review.

Construction checks balance and creates a separate `balanced_model` copy. Its default adjustment absorbs residuals into growth and net migration while preserving production. The exporter returns the original completed calculator; SPPR uses that object's state unless a caller explicitly substitutes the copy.

Automatic completion or algebraic balance is neither scientific approval nor evidence of the authors' native Ecopath balancing. Compare extracted values, transformed input, runtime changes and diagnostics before interpreting results. The [user guide](PPREstimation/USER_GUIDE.md) and [methods reference](sppr_methods.md) provide background; actual source behavior governs the distinctions above.
