# Bounded candidate diagnostics and arithmetic

Run from the repository root with Python 3.13 and the exact package versions in
[runtime-requirements.txt](runtime-requirements.txt). The actual run used the
existing NPP Python environment for NumPy, pandas and SciPy, with the missing
SymPy, igraph, tqdm and dependencies installed only in the local `vendor/`
folder. That regenerable folder is ignored; package versions and executed engine
bytes are retained. No global environment was altered.

Create an isolated Python environment and install the locked requirements there.
The bounded commands, using that environment's Python, are:

```powershell
python regions/LME_013/candidate_studies/HUM2018_20261003/diagnostics/run_direct_candidate.py --input regions/LME_013/candidate_studies/HUM2018_20261003/source/computational/model.json
python regions/LME_013/candidate_studies/HUM2018_20261003/diagnostics/summarize_direct.py
python regions/LME_013/candidate_studies/HUM2018_20261003/diagnostics/verify_retained_matrices.py
```

Preserve this completed evidence directory before a new run. Verify the current
engine hashes against the retained manifest; the exact executed bytes are also
retained for restoring the execution environment when code has changed.

The constructor is explicit: no LIM, no default catch, no default GS, no default
living BA and no BA compensation for diet normalization. The source audit's
computational conventions are retained. Diet normalization changes only the
runtime copy, with every factor and changed cell recorded. The engine creates a
separate `balanced_model` during initialization; that object is retained in the
runtime evidence and is never used for diagnosis or regional arithmetic.

The three methods call `diagnose_sppr` once each with `short=False`, `flat=False`
and `return_sppr=True`; no global or Monte Carlo options are executed. Input,
runtime, code and package identities are in [run_manifest.json](run_manifest.json).
The engine bytes used in the actual execution are under [executed_code](executed_code/).

The actual returns are scientific FAIL for all three methods. Their finite
coefficients support arithmetic-only investigation. None is eligible for valid
regional annual PPR or adoption. The source includes fisheries discard returns
to offal that the engine's native recycling equations do not represent. The
paper describes anchovy eggs as living; the computational translation treats
that nonfeeding routed compartment as a fourth detritus pool. These limitations
remain explicit in the source audit.

The arithmetic script `calculate_candidate.py` reads a completed candidate
mapping using `--mapping <path>` and the retained regional catch, classic PPR and
NPP snapshot. It performs no new model execution and writes only this folder.
Every negative coefficient and PPR value is retained, all results remain
ineligible, and wet-weight-equivalent PPR is divided by nine exactly once.
