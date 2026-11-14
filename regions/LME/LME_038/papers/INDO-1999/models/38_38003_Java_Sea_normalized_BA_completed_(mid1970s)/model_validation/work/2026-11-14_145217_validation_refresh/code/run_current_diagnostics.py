"""Bounded, user-authorized current-input diagnostics; no adoption or input edits."""
from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import math
import os
import platform
import sys
import time
import traceback
import warnings
from datetime import datetime, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve()
RUN = SCRIPT.parents[1]
MODEL = RUN.parents[2]
ROOT = next(p for p in MODEL.parents if (p / "Project.xlsx").is_file())
HIST = MODEL / "model_validation/evidence/source_review/direct_diagnostics"
ENGINE = HIST / "engine"
OUT = RUN / "outputs/current_diagnostics"
OUT.mkdir(parents=True, exist_ok=True)
sys.dont_write_bytecode = True
sys.path.insert(0, str(ENGINE))

import numpy as np
import pandas as pd
from ModelData import ModelData
from PPRCalculator import PPRCalculator, DEFAULT_DIAGNOSTIC_THRESHOLDS

METHODS = ["GE", "TE", "With Egestion"]
EXPECTED_INPUT = "dae4aa0106a4c47d7db6fa9764791e656d1ba75ae0e1756e6d20ec202180c9ba"
EXPECTED_ENGINE = {
    "PPRCalculator.py": "b2bb08f0564c8cd0fcc873eb1c681fd924c3dd113e22d6b388456248fc0162a7",
    "ModelData.py": "24a12fb0af33cc4b1976d40b39627c509436e808837aebb46517208e4d285e23",
    "utils.py": "817f969850b250d06563cfff2e5d1be0fdf70bacb7a3c4ac317bf69c805ca07f",
}
SETTINGS = dict(underdetermined=True, zero_catch=True, zero_biomass_accum=False,
                default_gs=True, weight_flow=1.0, weight_guess=1.0,
                normalize_DC=True, DC_tol=0.001)
OPTIONS = dict(short=False, flat=False, return_sppr=True, det_open_mode="none",
               det_theta=1.0, det_external_sppr=0.0, det_collapse_mode="never")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path, parent=OUT):
    return Path(os.path.relpath(path, parent)).as_posix()


def plain(value):
    if isinstance(value, pd.DataFrame):
        return dict(index=plain(value.index.tolist()), columns=plain(value.columns.tolist()),
                    data=plain(value.to_numpy(dtype=object).tolist()),
                    dtypes={str(k): str(v) for k, v in value.dtypes.items()})
    if isinstance(value, pd.Series):
        return plain(value.to_frame())
    if isinstance(value, np.ndarray):
        return plain(value.tolist())
    if isinstance(value, np.generic):
        return plain(value.item())
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if value is pd.NA:
        return {"__missing__": "pandas.NA"}
    if isinstance(value, float) and not math.isfinite(value):
        return {"__nonfinite__": "NaN" if math.isnan(value) else "+Infinity" if value > 0 else "-Infinity"}
    return value


def write(name, data):
    (OUT / name).write_text(json.dumps(plain(data), ensure_ascii=False, indent=2,
                                      allow_nan=False) + "\n", encoding="utf-8")


def state(calc):
    return {k: plain(v) for k, v in calc.__dict__.items()
            if isinstance(v, (pd.DataFrame, pd.Series, np.ndarray))}


def mismatch(left, right, path="", atol=1e-12):
    out = []
    if isinstance(left, (int, float)) and not isinstance(left, bool) and isinstance(right, (int, float)) and not isinstance(right, bool):
        if not math.isclose(left, right, abs_tol=atol, rel_tol=0):
            out.append(dict(path=path, before=left, after=right,
                            absolute_difference=abs(right-left)))
    elif isinstance(left, dict) and isinstance(right, dict):
        for key in sorted(set(left) | set(right)):
            if key == "dtypes":
                continue
            if key not in left or key not in right:
                out.append(dict(path=path+"/"+str(key), before=left.get(key), after=right.get(key)))
            else:
                out.extend(mismatch(left[key], right[key], path+"/"+str(key), atol))
    elif isinstance(left, list) and isinstance(right, list) and len(left) == len(right):
        for i, (a, b) in enumerate(zip(left, right)):
            out.extend(mismatch(a, b, path+"/"+str(i), atol))
    elif left != right:
        out.append(dict(path=path, before=left, after=right))
    return out


def matrix_meta(method, key, frame, names, source_ids):
    vals = frame.to_numpy(dtype=object)
    def mask(kind):
        def one(v):
            if kind == "null": return v is None or v is pd.NA
            if not isinstance(v, (int, float, np.number)): return False
            if kind == "nan": return bool(np.isnan(v))
            if kind == "positive_infinity": return bool(np.isposinf(v))
            return bool(np.isneginf(v))
        return [[one(v) for v in row] for row in vals]
    return dict(method=method, matrix=key, shape=list(frame.shape),
                row_ids=frame.index.tolist(), column_ids=frame.columns.tolist(),
                row_names=[names.get(i, str(i)) for i in frame.index],
                column_names=[names.get(i, str(i)) for i in frame.columns],
                orientation="recipient group rows, basal source columns" if key == "SPPR" else "group rows and columns as returned by the pinned engine",
                units="t wet primary-source requirement per t wet recipient" if key == "SPPR" else "dimensionless solver operator",
                synthetic_group_ids=[29], source_scope_definitions=source_ids,
                null_mask=mask("null"), nan_mask=mask("nan"),
                positive_infinity_mask=mask("positive_infinity"), negative_infinity_mask=mask("negative_infinity"))


started = datetime.now(timezone.utc).isoformat()
source = MODEL / "model.json"
before_hash = sha(source)
assert before_hash == EXPECTED_INPUT
assert {name: sha(ENGINE/name) for name in EXPECTED_ENGINE} == EXPECTED_ENGINE
assert Path(inspect.getfile(PPRCalculator)).resolve() == ENGINE / "PPRCalculator.py"
assert Path(inspect.getfile(ModelData)).resolve() == ENGINE / "ModelData.py"
signature = inspect.signature(PPRCalculator.from_modeldata)
assert "use_ee_floor" not in signature.parameters
canonical = json.loads(source.read_text(encoding="utf-8-sig"))
reports, solutions, timings, metadata, negatives, coefficients = {}, {}, {}, [], [], []
construction = {"status": "not_started"}
checks = {}
captured_warnings = []
try:
    with warnings.catch_warnings(record=True) as warning_records:
        warnings.simplefilter("always")
        raw = ModelData(str(source))
        raw_groups, raw_dc, raw_fate = raw.groups_data.copy(deep=True), raw.DC.copy(deep=True), raw.det_fate.copy(deep=True)
        write("source_loaded_state.json", {"groups": raw_groups, "diet": raw_dc, "detritus_fate": raw_fate})
        t0 = time.monotonic()
        calc = PPRCalculator.from_modeldata(raw, **SETTINGS)
        construction = {"status": "constructed", "seconds": time.monotonic()-t0}
        before_state = state(calc)
        loaded = calc.get_groups_df()
        names = {int(i): str(v) for i, v in loaded["group_name"].items()}
        scopes = {"all": [29, 28, 2, 1], "inner": [28, 2, 1], "PP": [2, 1]}
        write("runtime_before_methods.json", before_state)
        write("loaded_groups.json", loaded)

        parameter_changes = []
        for gid in raw_groups.index:
            for field in raw_groups.columns:
                if field not in loaded.columns: continue
                a, b = plain(raw_groups.loc[gid, field]), plain(loaded.loc[gid, field])
                if a != b:
                    parameter_changes.append(dict(group_id=int(gid), group_name=names[int(gid)], field=field, source_loaded=a, runtime=b))
        diet_changes = []
        for recipient in raw_dc.index:
            for prey in raw_dc.columns:
                a, b = float(raw_dc.loc[recipient, prey]), float(calc._DC.loc[recipient, prey])
                if a != b:
                    diet_changes.append(dict(consumer_id=int(recipient), consumer_name=names[int(recipient)], prey_id=int(prey), prey_name=names[int(prey)], raw=a, runtime=b, factor=(b/a if a else None)))
        diet_sums = [dict(consumer_id=int(i), consumer_name=names[int(i)], raw=float(raw_dc.loc[i].sum()), runtime=float(calc._DC.loc[i].sum())) for i in raw_dc.index]
        ba_changes = []
        for group in canonical["group"]:
            gid = int(group["group_seq"])
            old, new = float(group["biomass_accum"]), float(loaded.loc[gid,"biomass_accum"])
            if abs(old-new) > 1e-12:
                ba_changes.append(dict(group_id=gid, canonical=old, runtime=new))
        checks["accepted_BA_preserved_at_1e_12"] = not ba_changes
        write("runtime_transformation_ledger.json", dict(parameter_changes=parameter_changes,
            added_runtime_fields=[c for c in loaded.columns if c not in raw_groups.columns],
            diet_changes=diet_changes, diet_sums=diet_sums, BA_changes_at_1e_12=ba_changes,
            synthetic_groups=[dict(group_id=29, group_name=names[29], role="diet_import; synthetic loader source")],
            floor=dict(implemented=False, applied=False, basis="The audited pinned engine predates the EE-floor transformation; no floor migration was requested."),
            limitations=["Runtime normalization is a computational convention; the raw Macrozoobenthos diet sum remains 0.660 in canonical input.",
                         "Twenty-eight accepted BA values are prior computational completions, not observed stock changes.",
                         "This is a diagnostic run, not a fresh primary-source extraction."]))
        if ba_changes:
            raise RuntimeError("Pinned constructor changed accepted BA beyond 1e-12; diagnostics stopped without repair")

        for method in METHODS:
            t0 = time.monotonic()
            try:
                report, sppr, A, L = calc.diagnose_sppr(TE_option=method, **OPTIONS)
                reports[method] = report
                solutions[method] = {"SPPR":sppr, "A":A, "L":L}
                for key, frame in solutions[method].items():
                    if isinstance(frame, pd.DataFrame):
                        metadata.append(matrix_meta(method,key,frame,names,scopes))
                for gid, row in sppr.iterrows():
                    for sid, value in row.items():
                        if pd.notna(value) and float(value) < 0:
                            negatives.append(dict(method=method,matrix="SPPR",source_id=int(sid),source_name=names[int(sid)],group_id=int(gid),group_name=names[int(gid)],sppr_value=float(value)))
                    for scope, ids in scopes.items():
                        coefficients.append(dict(method=method,scope=scope,group_id=int(gid),group_name=names[int(gid)],sppr=float(row.loc[ids].sum())))
                footprint = {scope: float((sppr.loc[:,ids].sum(axis=1) * calc.catch.reindex(sppr.index)).sum()) for scope,ids in scopes.items()}
                fields = {"all":"ppr_all","inner":"ppr_inner","PP":"ppr_pp_only"}
                checks[method+"_footprint_reconciles"] = all(math.isclose(footprint[s],report["footprint"][f],rel_tol=1e-12,abs_tol=1e-12) for s,f in fields.items())
                checks[method+"_negative_count_reconciles"] = int((sppr<0).any(axis=0).sum()) == report["divergence"]["n_negative_sources"]
                checks[method+"_detritus_SPPR_reconciles"] = math.isclose(float(sppr.loc[28].sum()),float(report["divergence"]["sppr_det"][28]),rel_tol=1e-12,abs_tol=1e-12)
            except Exception as exc:
                reports[method] = dict(status="EXCEPTION",exception_type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc())
            timings[method] = time.monotonic()-t0
            write("direct_reports.json",reports)
            write("direct_solutions.json",solutions)
            print(method, reports[method].get("status"), timings[method], flush=True)
        after_state = state(calc)
        write("runtime_after_methods.json",after_state)
        checks["methods_preserved_runtime_state"] = before_state == after_state
        historical_state = json.loads((HIST/"loaded_state.json").read_text(encoding="utf-8"))
        differences = mismatch(historical_state,before_state)
        historical_solutions = json.loads((HIST/"direct_solutions.json").read_text(encoding="utf-8"))
        solution_differences = mismatch(historical_solutions,plain(solutions))
        write("historical_comparison.json",dict(atol=1e-12,rtol=0,
            historical_input_sha256="db0bc803ea5a068e346b82df8d8b4e4b13f8351bf61103c6507997cb6996ae35",
            current_input_sha256=before_hash,state_differences=differences,
            matrix_differences=solution_differences, runtime_equal_at_tolerance=not differences,
            matrices_equal_at_tolerance=not solution_differences))
        captured_warnings = [dict(category=w.category.__name__,message=str(w.message)) for w in warning_records]
except Exception as exc:
    construction.update(exception_type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc())
    for method in METHODS:
        reports.setdefault(method,dict(status="NOT_RUN",reason="construction or protected-input guard failed"))
    write("direct_reports.json",reports)
finally:
    checks["canonical_input_unchanged"] = sha(source) == before_hash
    checks["engine_unchanged"] = {name: sha(ENGINE/name) for name in EXPECTED_ENGINE} == EXPECTED_ENGINE
    write("matrices_metadata.json",metadata)
    write("negative_source_entries.json",dict(comparison="strict < 0 before rounding",tolerance=0,entries=negatives))
    write("group_scope_coefficients.json",coefficients)
    provenance = dict(schema_version=1,run_id=RUN.name,unit_id="LME_038",model_id=MODEL.name,
        authorization="User explicitly authorized missing SPPR runs during this validation refresh; direct diagnostic results for report use only.",
        started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
        canonical_input=relative(source),canonical_sha256_before=before_hash,canonical_sha256_after=sha(source),
        engine_files=[dict(path=relative(ENGINE/n),sha256=h) for n,h in EXPECTED_ENGINE.items()],
        constructor="PPRCalculator.from_modeldata(ModelData(current canonical model.json))",
        constructor_settings=SETTINGS,constructor_signature=str(signature),diagnostic_settings=OPTIONS,
        effective_thresholds=DEFAULT_DIAGNOSTIC_THRESHOLDS,methods=METHODS,
        ee_floor=dict(implemented=False,applied=False,configuration="audited pre-floor baseline, no engine migration"),
        construction=construction,timings_seconds=timings,warnings=captured_warnings,
        environment=dict(python_executable=sys.executable,python_version=sys.version,platform=platform.platform(),
                         packages={n:getattr(importlib.import_module(n),"__version__","unknown") for n in ["numpy","pandas","scipy","sympy","igraph","tqdm"]}),
        adoption_performed=False,workbooks_updated=False,canonical_input_repaired=False,
        preservation_checks=checks,script_path=relative(SCRIPT),script_sha256=sha(SCRIPT))
    write("execution_evidence.json",provenance)
    print(json.dumps({"construction":construction,"checks":checks,"statuses":{k:v.get("status") for k,v in reports.items()}},ensure_ascii=False),flush=True)

if not checks.get("canonical_input_unchanged") or any(reports[m].get("status") in ["EXCEPTION","NOT_RUN"] for m in METHODS):
    raise SystemExit(2)
