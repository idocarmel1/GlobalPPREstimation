# Reproducing this diagnostic package

The immutable `initial_*.json` files contain each actual full four-part return: report, SPPR, A and L. `reload_*.json` are fresh-process replays of the persisted canonical variant. `diagnostic_summary.json` reconciles them; the independent review checks dimensions, masks, scope sums and provenance. Scientific FAIL is a retained result, not an execution error.

Use `run_identity.json` for exact Python/package versions, constructor flags, method options and executed source hashes. The `executed_code/` tree preserves the code bytes under their original repository-relative paths. Restore or verify those bytes before reproduction; do not silently substitute a newer engine. The raw parent EE provenance must be retained because solved EE values are not floor-eligible source measurements.

The original entry point was `regions/LME/LME_002/work/2026-11-14_191000_native_balance_diagnostics/code/run_diagnostics.py`, retained inside `executed_code/`. From the repository root, restore that script to a bounded work directory inside the repository (root discovery follows the script's ancestors) and invoke Python 3.11.9 with:

```text
python <restored-run_diagnostics.py> --parent regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49/model.json --variant regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance/model.json --outdir <new-bounded-work-directory>/diagnostics
```

Each of the three calls and three reproduction calls has a 180-second worker bound. The runner checks source/code identities, constructs without normalization or BA repair, applies the floor once using raw parent eligibility, and retains exact typed arrays and masks. Its path records are historical provenance; inventory paths resolve relative to the retained evidence index.

Native reproduction and its R runtime/package acquisition are documented in [the native evidence directory](../../extracted_tables/evidence/native_reproduction/). Build-variant code and maintained conversion helper bytes are under [reproduction_code](../../extracted_tables/evidence/reproduction_code/). Temporary downloaded runtime binaries and duplicate staging files are not scientific inputs and may be removed after their receipts and outputs are retained.

No forced-balance diagnostic, detritus-loss assumption, parameter repair, catch mapping, annual regional calculation or map update was executed. The accounting decomposition is arithmetic on retained results, not a new solve.
