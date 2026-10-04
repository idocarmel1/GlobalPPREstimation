"""Isolated direct-only tool regeneration; never adopts or repairs model inputs.

Run from any directory with the same Python environment as the retained evidence.
Comparison policy is frozen below. Historical dependencies are checked against the
recorded byte identities; the current compatibility setting is recorded separately.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import traceback
import warnings

METHODS = ("GE", "TE", "With Egestion")
MATRICES = ("SPPR", "A", "L")
ATOL = 1e-12
RTOL = 0.0
POLICY = {
    "frozen_before_execution": True, "rtol": RTOL, "atol": ATOL,
    "finite_numbers": "absolute difference <= 1e-12; no tolerance relaxation",
    "axes": "exact unique IDs, names, types, order and synthetic flags",
    "masks": "exact separate null/NaN/+infinity/-infinity and finite masks",
    "grades_and_flags": "exact status/component grades, Booleans, counts, config and warning text",
    "claim": "tool regeneration only; no independent extraction or full pipeline",
}
MID = "36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)"
MODEL_REL = Path("regions/LME/LME_036/papers/SCS-2007/models") / MID
EVIDENCE_REL = MODEL_REL / "model_validation/evidence/source_review/selected_regions_review_20260930/direct_diagnostics"
ENGINE_REL = Path("tools/scientific_code/PPREstimation")
EXPECTED_MODEL = "9a199f06809165104ed59b9fb53cb48e6bb9cd0439be081dc518da26a681cfc7"
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "Project.xlsx").exists())
RUN = Path(__file__).resolve().parent.parent
OUT = RUN / "outputs/direct_diagnostics"
QA = RUN / "qa"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def clean(value):
    """Tagged nonfinite scalars retain distinction from genuine null values."""
    import numpy as np
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, np.generic):
        return clean(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return {"nonfinite": "nan" if math.isnan(value) else ("positive_infinity" if value > 0 else "negative_infinity")}
    return value


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def frame(df, names=None, source_ids=None):
    import numpy as np
    vals = df.to_numpy(dtype=object).tolist()
    masks = {k: [[False for _ in df.columns] for _ in df.index]
             for k in ("null", "nan", "positive_infinity", "negative_infinity")}
    for i, row in enumerate(vals):
        for j, value in enumerate(row):
            if value is None:
                masks["null"][i][j] = True
            elif isinstance(value, (float, np.floating)):
                if np.isnan(value): masks["nan"][i][j] = True
                elif np.isposinf(value): masks["positive_infinity"][i][j] = True
                elif np.isneginf(value): masks["negative_infinity"][i][j] = True
    ans = {"row_ids": clean(df.index.tolist()), "column_ids": clean(df.columns.tolist()),
           "values": clean(vals), "masks": masks,
           "finite_mask": [[not any(m[i][j] for m in masks.values()) for j in range(len(df.columns))]
                           for i in range(len(df.index))]}
    if names is not None:
        axis = lambda ids: [{"group_id": clean(i), "group_name": str(names.loc[i, "group_name"]),
                             "trophic_info": str(names.loc[i, "trophic_info"]),
                             "synthetic": i not in source_ids} for i in ids]
        ans.update(row_axis=axis(df.index), column_axis=axis(df.columns))
    return ans


def compare(a, b, key=""):
    """Exact types/keys/masks; absolute-only finite numeric comparison."""
    result = {"within_frozen_tolerance": True, "exact_equal": True,
              "max_absolute_difference": 0.0, "max_relative_difference": 0.0,
              "changed_keys": [], "outside_tolerance_keys": []}
    def walk(x, y, k):
        if isinstance(x, dict) and isinstance(y, dict):
            if set(x) != set(y): change(k + ".keys", sorted(x), sorted(y), False)
            for n in sorted(set(x) & set(y)): walk(x[n], y[n], k + "." + n)
        elif isinstance(x, list) and isinstance(y, list):
            if len(x) != len(y): change(k + ".length", len(x), len(y), False)
            for i, (u, v) in enumerate(zip(x, y)): walk(u, v, f"{k}[{i}]")
        elif type(x) is bool or type(y) is bool:
            if type(x) is not type(y) or x != y: change(k, x, y, False)
        elif isinstance(x, (int, float)) and isinstance(y, (int, float)):
            d = abs(x - y)
            result["max_absolute_difference"] = max(result["max_absolute_difference"], d)
            if d: result["max_relative_difference"] = max(result["max_relative_difference"], d / abs(x) if x else math.inf)
            if type(x) is int or type(y) is int:
                same = type(x) is type(y) and x == y
            else:
                same = d <= ATOL
            if type(x) is not type(y) or x != y: change(k, x, y, same)
        elif type(x) is not type(y) or x != y:
            change(k, x, y, False)
    def change(k, x, y, within):
        result["exact_equal"] = False
        result["changed_keys"].append(k)
        if not within:
            result["within_frozen_tolerance"] = False
            result["outside_tolerance_keys"].append({"key": k, "retained": clean(x), "regenerated": clean(y)})
    walk(a, b, key)
    return result


def matrix_compare(a, b):
    keys = ("row_ids", "column_ids", "row_axis", "column_axis", "masks", "finite_mask", "values")
    ans = compare({k: a[k] for k in keys}, {k: b[k] for k in keys})
    ans["axis_uniqueness"] = all(len(x[k]) == len(set(x[k])) for x in (a, b) for k in ("row_ids", "column_ids"))
    ans["dimensions_valid"] = all(len(x["values"]) == len(x["row_ids"]) and
                                  all(len(v) == len(x["column_ids"]) for v in x["values"]) for x in (a, b))
    ans["within_frozen_tolerance"] &= ans["axis_uniqueness"] and ans["dimensions_valid"]
    ans["changed_group_source_keys"] = []
    for k in ans["changed_keys"]:
        if k.startswith(".values["):
            i, j = [int(v) for v in k.removeprefix(".values[").replace("][", ",").rstrip("]").split(",")]
            ans["changed_group_source_keys"].append({"recipient_id": a["row_ids"][i], "source_or_dependency_id": a["column_ids"][j]})
    return ans


def scientific_state(pc):
    """Every tabular/vector scientific field; solver caches are recorded separately."""
    import pandas as pd
    import numpy as np
    ans = {}
    for k, v in vars(pc).items():
        if isinstance(v, pd.DataFrame): ans[k] = frame(v)
        elif isinstance(v, pd.Series): ans[k] = frame(v.to_frame())
        elif isinstance(v, np.ndarray): ans[k] = clean(v)
        elif isinstance(v, (str, int, float, bool, type(None), np.generic)): ans[k] = clean(v)
        elif isinstance(v, dict) and all(isinstance(x, (str, int, float, bool, type(None), np.generic)) for x in v.values()): ans[k] = clean(v)
    return ans


def worker(label, engine_dir):
    import pandas as pd
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(engine_dir))
    from ModelData import ModelData
    from PPRCalculator import PPRCalculator, DEFAULT_DIAGNOSTIC_THRESHOLDS
    ident = read(ROOT / EVIDENCE_REL / "complete_input_identity.json")
    constructor = {**ident["constructor"], "weight_flow": 1.0, "weight_guess": 1.0}
    if label == "current_compatibility": constructor["balance_BA_after_DC_normalization"] = False
    # Extra solver defaults are verified from the exact historical API and made explicit.
    settings = {**ident["diagnostic_settings"], "TE": None, "DET_TE_vals": 1, "fix_EE_0_cases": True}
    dest = OUT / label
    start = time.perf_counter()
    records = {"label": label, "constructor": constructor, "diagnostic_settings": settings,
               "thresholds": ident["effective_diagnostic_thresholds"], "methods": {},
               "constructor_invocations": 1, "diagnose_sppr_invocations": 0}
    assert DEFAULT_DIAGNOSTIC_THRESHOLDS == ident["effective_diagnostic_thresholds"]
    md = None
    try:
        with warnings.catch_warnings(record=True) as ww:
            warnings.simplefilter("always")
            md = ModelData(str(ROOT / MODEL_REL / "model.json"))
            source_before = {"groups": frame(md.groups_data), "diet": frame(md.DC), "detritus_fate": frame(md.det_fate)}
            pc = PPRCalculator.from_modeldata(md, **constructor)
        records["constructor_warnings"] = [str(w.message) for w in ww]
        records["constructor_seconds"] = time.perf_counter() - start
        before = scientific_state(pc)
        save(dest / "runtime_before.json", before)
        pc._groups_df.to_csv(dest / "runtime_groups_before.csv", encoding="utf-8", float_format="%.17g")
        for attr, filename in (("_DC", "runtime_diet.csv"), ("_det_fate", "runtime_detritus_routing.csv")):
            getattr(pc, attr).to_csv(dest / filename, encoding="utf-8", float_format="%.17g")
        source_ids = {int(g["group_seq"]) for g in read(ROOT / MODEL_REL / "model.json")["group"]}
        for option in METHODS:
            stamp = time.perf_counter()
            stem = option.replace(" ", "_")
            records["diagnose_sppr_invocations"] += 1
            try:
                with warnings.catch_warnings(record=True) as ww:
                    warnings.simplefilter("always")
                    report, sppr, a, l = pc.diagnose_sppr(TE_option=option, short=False, flat=False,
                        return_sppr=True, thresholds=ident["effective_diagnostic_thresholds"], **settings)
                save(dest / (stem + "_report.json"), report)
                save(dest / (stem + "_warnings.json"), [str(w.message) for w in ww])
                record = {"outcome": "RETURNED", "status": report.get("status"), "matrices": {}}
                for name, df in zip(MATRICES, (sppr, a, l)):
                    if df is None:
                        record["matrices"][name] = {"availability": "missing", "reason": "Actual method returned None"}
                        continue
                    payload = frame(df, pc._groups_df, source_ids)
                    payload.update(orientation="Recipient/consumer groups in rows; basal sources in SPPR columns; dependency groups in A/L columns.",
                                   units="Dimensionless source-specific primary-production requirement per unit recipient mass" if name == "SPPR" else "Dimensionless operator weights",
                                   scope_definitions={"PP": "Runtime PP columns only", "inner": "All columns except runtime synthetic Import columns", "all": "Every returned basal column"})
                    save(dest / (stem + "_" + name + "_lossless.json"), payload)
                    record["matrices"][name] = {"availability": "present", "shape": list(df.shape)}
                records["methods"][option] = record
            except Exception as exc:
                records["methods"][option] = {"outcome": "EXCEPTION", "status": "NOT_RUN", "exception_type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
                save(dest / (stem + "_exception.json"), records["methods"][option])
            records["methods"][option]["seconds"] = time.perf_counter() - stamp
            print(label, option, records["methods"][option]["outcome"], records["methods"][option]["status"], flush=True)
        after = scientific_state(pc)
        save(dest / "runtime_after.json", after)
        records["runtime_before_after"] = compare(before, after)
        records["source_modeldata_before_after"] = compare(source_before,
            {"groups": frame(md.groups_data), "diet": frame(md.DC), "detritus_fate": frame(md.det_fate)})
        save(dest / "source_modeldata_before_after.json", {"before": source_before, "after":
            {"groups": frame(md.groups_data), "diet": frame(md.DC), "detritus_fate": frame(md.det_fate)}})
    except Exception as exc:
        records["constructor_exception"] = {"exception_type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        for option in METHODS:
            records["methods"][option] = {"outcome": "NOT_RUN", "status": "NOT_RUN", "reason": "Construction or source-state capture failed"}
    records["total_seconds"] = time.perf_counter() - start
    save(dest / "execution.json", records)


def ast_methods(text):
    cl = next(n for n in ast.parse(text).body if isinstance(n, ast.ClassDef) and n.name == "PPRCalculator")
    ans = {}
    for node in cl.body:
        if not isinstance(node, ast.FunctionDef): continue
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            node.body = node.body[1:]
        ans[node.name] = ast.dump(node, include_attributes=False)
    return ans


def main(compare_existing=False):
    import pandas as pd
    import numpy as np
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    if not compare_existing and any((OUT / label / "execution.json").exists() for label in ("exact_historical", "current_compatibility")):
        raise FileExistsError("Trial outputs already exist. Use --compare-existing to recheck them, or copy this script into a distinct authorized work run.")
    retained = ROOT / EVIDENCE_REL
    ident = read(retained / "complete_input_identity.json")
    code_paths = [ROOT / ENGINE_REL / n for n in ("PPRCalculator.py", "ModelData.py", "utils.py")]
    protected = code_paths + [ROOT / MODEL_REL / n for n in ("model.json", "model_notes.md", "sppr_source.xlsx", "inputs/provenance.json")]
    protected += list(retained.glob("*.json")) + list(retained.glob("*.csv"))
    before = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
    assert sha(ROOT / MODEL_REL / "model.json") == EXPECTED_MODEL == ident["source_sha256"]
    git_bytes, git_sources = {}, {}
    for filename, ref in (("PPRCalculator.py", "3b63135d"), ("ModelData.py", "7b2989fa"), ("utils.py", "3b63135d")):
        commit = subprocess.check_output(["git", "rev-parse", ref], cwd=ROOT, text=True).strip()
        data = subprocess.check_output(["git", "show", f"{commit}:{(ENGINE_REL / filename).as_posix()}"], cwd=ROOT)
        assert hashlib.sha256(data).hexdigest() == ident["runtime_code_hashes"][filename]
        git_bytes[filename] = data
        git_sources[filename] = {"commit": commit, "path": (ENGINE_REL / filename).as_posix(), "sha256": hashlib.sha256(data).hexdigest()}
    old = ast_methods(git_bytes["PPRCalculator.py"].decode("utf-8"))
    new = ast_methods((ROOT / ENGINE_REL / "PPRCalculator.py").read_text(encoding="utf-8"))
    preflight = {"policy": POLICY, "source_sha256": EXPECTED_MODEL,
        "retained_input_identity": EVIDENCE_REL.as_posix() + "/complete_input_identity.json",
        "recorded_constructor": ident["constructor"], "recorded_diagnostic_settings": ident["diagnostic_settings"],
        "effective_thresholds": ident["effective_diagnostic_thresholds"],
        "exact_historical_imported_code": git_sources,
        "current_imported_code": {p.name: sha(p) for p in code_paths},
        "code_mismatch_disclosed_before_trial": True,
        "historical_omitted_defaults_verified": {"weight_flow": 1.0, "weight_guess": 1.0, "TE": None, "DET_TE_vals": 1, "fix_EE_0_cases": True},
        "current_compatibility_setting": {"balance_BA_after_DC_normalization": False},
        "compatibility_setting_reason": "Historical engine has no BA-normalization-closure option or transformation; False is a current compatibility setting, not a historical flag or adopted production default.",
        "ast_body_comparison": {"changed_methods": [k for k in old if old[k] != new.get(k)], "added_methods": [k for k in new if k not in old],
                                "diagnose_sppr_equal": old["diagnose_sppr"] == new["diagnose_sppr"], "SPPR_new_equal": old["SPPR_new"] == new["SPPR_new"]},
        "protected_sha256_before": before, "environment": {"executable": sys.executable, "python": platform.python_version(), "platform": platform.platform(),
            "packages": {k: importlib.metadata.version(k) for k in ("numpy", "pandas", "scipy", "sympy", "igraph")}},
        "start_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    if compare_existing:
        previous = read(QA / "diagnostic_replication.json")
        preflight = read(QA / "diagnostic_replication_preflight.json")
        before = preflight["protected_sha256_before"]
    else:
        preflight["executed_trial_script_sha256"] = sha(Path(__file__))
        save(QA / "diagnostic_replication_preflight.json", preflight)
    # Preflight comparison policy and identities are written before any constructor or solve.
    proc_records = previous["processes"] if compare_existing else {}
    if not compare_existing:
        with tempfile.TemporaryDirectory(prefix="historical_engine_", dir=OUT) as temp:
            historical_dir = Path(temp).resolve()
            assert historical_dir.is_relative_to(OUT.resolve())
            for name, data in git_bytes.items(): (historical_dir / name).write_bytes(data)
            for label, engine in (("exact_historical", historical_dir), ("current_compatibility", ROOT / ENGINE_REL)):
                stamp = time.perf_counter()
                r = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--worker", label, "--engine-dir", str(engine)],
                                   cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True, encoding="utf-8", errors="replace")
                proc_records[label] = {"returncode": r.returncode, "wall_seconds": time.perf_counter() - stamp, "stdout": r.stdout, "stderr": r.stderr}
                print(r.stdout, end="", flush=True)
    corrections = []
    source_ids = {int(g["group_seq"]) for g in read(ROOT / MODEL_REL / "model.json")["group"]}
    if compare_existing:
        for label in proc_records:
            for path in (OUT / label).glob("*_lossless.json"):
                data = read(path)
                old_hash = sha(path)
                changes = []
                for axis_name in ("row_axis", "column_axis"):
                    for row in data[axis_name]:
                        correct = row["group_id"] not in source_ids
                        if row["synthetic"] != correct:
                            changes.append({"axis": axis_name, "group_id": row["group_id"], "old": row["synthetic"], "new": correct})
                            row["synthetic"] = correct
                if changes:
                    save(path, data)
                    corrections.append({"path": path.relative_to(RUN).as_posix(), "before_sha256": old_hash,
                        "after_sha256": sha(path), "changes": changes, "numeric_values_and_masks_changed": False})
        if not corrections: corrections = previous.get("temporary_axis_metadata_corrections", [])
    comparisons = {}
    executions = {}
    saved_book = pd.ExcelFile(ROOT / MODEL_REL / "sppr_source.xlsx")
    saved_coeff = {scope: pd.read_excel(saved_book, sheet_name="sppr_" + scope).set_index("seq") for scope in ("PP", "inner", "all")}
    for label in proc_records:
        dest = OUT / label
        execution = read(dest / "execution.json") if (dest / "execution.json").exists() else {"methods": {m: {"outcome": "NOT_RUN", "reason": "Worker failed before execution record"} for m in METHODS}}
        executions[label] = execution
        compared = {"methods": {}, "runtime_vs_retained": {}}
        negatives = []
        runtime_groups = pd.read_csv(dest / "runtime_groups_before.csv", index_col=0, float_precision="round_trip") if (dest / "runtime_groups_before.csv").exists() else None
        for filename in ("runtime_groups_before.csv", "runtime_diet.csv", "runtime_detritus_routing.csv"):
            if (dest / filename).exists():
                a = pd.read_csv(retained / filename, index_col=0, float_precision="round_trip")
                b = pd.read_csv(dest / filename, index_col=0, float_precision="round_trip")
                compared["runtime_vs_retained"][filename] = compare(frame(a), frame(b))
        for method in METHODS:
            stem = method.replace(" ", "_")
            m = {"execution": execution["methods"][method], "matrices": {}, "saved_coefficient_scope_sums": {}, "matrix_to_report_reconciliation": {}}
            if (dest / (stem + "_report.json")).exists():
                m["full_report"] = compare(read(retained / (stem + "_report.json")), read(dest / (stem + "_report.json")))
            for name in MATRICES:
                p = dest / (stem + "_" + name + "_lossless.json")
                if p.exists():
                    generated_matrix = read(p)
                    m["matrices"][name] = matrix_compare(read(retained / p.name), generated_matrix)
                    for i, row in enumerate(generated_matrix["values"]):
                        for j, value in enumerate(row):
                            if isinstance(value, (int, float)) and value < 0:
                                negatives.append({"method": method, "matrix": name,
                                    "recipient_group_id": generated_matrix["row_ids"][i], "recipient_group_name": generated_matrix["row_axis"][i]["group_name"],
                                    "source_or_dependency_id": generated_matrix["column_ids"][j], "source_or_dependency_name": generated_matrix["column_axis"][j]["group_name"],
                                    "value": value, "sign_threshold": 0.0, "comparison_atol": ATOL,
                                    "interpretation": "L = A - I operator term" if name == "L" else "Negative contribution/weight"})
                else: m["matrices"][name] = {"within_frozen_tolerance": False, "availability": "missing", "reason": "No regenerated matrix; see execution record"}
            p = dest / (stem + "_SPPR_lossless.json")
            if p.exists():
                data = read(p)
                vals = np.array(data["values"], dtype=float)
                cols = {x["group_id"]: x for x in data["column_axis"]}
                method_col = {"GE": "new_GE", "TE": "new_TE_EEfix", "With Egestion": "new_WithEgestion"}[method]
                scope_totals = {}
                for scope in ("PP", "inner", "all"):
                    use = [j for j, i in enumerate(data["column_ids"]) if scope == "all" or (scope == "PP" and cols[i]["trophic_info"] == "PP") or (scope == "inner" and cols[i]["trophic_info"] != "Import")]
                    generated = dict(zip(map(str, data["row_ids"]), clean(vals[:, use].sum(axis=1))))
                    expected = {str(i): clean(float(v)) for i, v in saved_coeff[scope][method_col].items()}
                    m["saved_coefficient_scope_sums"][scope] = compare(expected, generated)
                    scope_totals[scope] = np.array(list(generated.values()), dtype=float)
                report = read(dest / (stem + "_report.json"))
                catch = runtime_groups.loc[data["row_ids"], "catch"].to_numpy(dtype=float)
                report_keys = {"PP": "ppr_pp_only", "inner": "ppr_inner", "all": "ppr_all"}
                m["matrix_to_report_reconciliation"]["footprint"] = compare(
                    {scope: report["footprint"][key] for scope, key in report_keys.items()},
                    {scope: float((scope_totals[scope] * catch).sum()) for scope in report_keys})
                detritus_totals = {str(group["group_id"]): float(vals[i].sum()) for i, group in enumerate(data["row_axis"]) if group["trophic_info"] == "DET"}
                m["matrix_to_report_reconciliation"]["named_detritus_sppr"] = compare(report["divergence"]["sppr_det"], detritus_totals)
            compared["methods"][method] = m
        save(dest / "negative_entry_table.json", {"entries": negatives, "negative_SPPR_entries": sum(x["matrix"] == "SPPR" for x in negatives),
             "note": "Negative L terms are algebraic operator entries and are distinct from negative source SPPR."})
        comparisons[label] = compared
    cross = {}
    for method in METHODS:
        stem = method.replace(" ", "_")
        cross[method] = {}
        for name in MATRICES:
            p = stem + "_" + name + "_lossless.json"
            if all((OUT / label / p).exists() for label in executions):
                cross[method][name] = matrix_compare(read(OUT / "exact_historical" / p), read(OUT / "current_compatibility" / p))
        p = stem + "_report.json"
        if all((OUT / label / p).exists() for label in executions): cross[method]["full_report"] = compare(read(OUT / "exact_historical" / p), read(OUT / "current_compatibility" / p))
    after = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
    preserved = before == after
    summary = {"schema_version": 1, "run_id": RUN.name, "model_id": MID, "region_id": "LME_036", "trial_kind": "tool_regeneration",
        "independent_extraction": False, "full_pipeline_replication": False, "adopted": False, "global_or_monte_carlo_executed": False,
        "policy": POLICY, "preflight": "diagnostic_replication_preflight.json", "executions": executions, "processes": proc_records,
        "retained_comparisons": comparisons, "historical_vs_current_compatibility": cross,
        "preservation": {"all_protected_hashes_unchanged": preserved, "protected_file_count": len(before), "before": before, "after": after},
        "temporary_axis_metadata_corrections": corrections,
        "measurement": {"total_wall_seconds": previous["measurement"]["total_wall_seconds"] if compare_existing else time.perf_counter() - started,
                        "total_wall_seconds_scope": "Original two-engine trial and initial comparison; later metadata/comparison-only rechecks are separate",
                        "comparison_only_recheck_seconds": time.perf_counter() - started if compare_existing else 0,
                        "worker_processes": len(proc_records),
                        "constructor_invocations": sum(e.get("constructor_invocations", 0) for e in executions.values()),
                        "diagnose_sppr_invocations": sum(e.get("diagnose_sppr_invocations", 0) for e in executions.values()),
                        "comparison_policy_frozen_before_first_constructor": True, "workbook_parses": 1,
                        "token_telemetry": "unavailable", "context": "warm evidence-reading context; separate cold engine worker processes"},
        "limitations": ["Exact historical engine bytes are regenerated, not independently reimplemented.",
                        "Current compatibility setting is not a historical recorded flag or adopted default.",
                        "Scientific source discrepancies, WARN restrictions and provisional source applicability remain.",
                        "Any failed comparison remains unresolved; tolerance is unchanged."]}
    checks = []
    for label, trial in comparisons.items():
        direct_checks = [v["within_frozen_tolerance"] for v in trial["runtime_vs_retained"].values()]
        coefficient_checks = []
        for method, item in trial["methods"].items():
            direct_checks.append(item["execution"]["outcome"] == "RETURNED")
            direct_checks.append(item.get("full_report", {}).get("within_frozen_tolerance", False))
            direct_checks.extend(v["within_frozen_tolerance"] for v in item["matrices"].values())
            direct_checks.extend(v["within_frozen_tolerance"] for v in item["matrix_to_report_reconciliation"].values())
            coefficient_checks.extend(v["within_frozen_tolerance"] for v in item["saved_coefficient_scope_sums"].values())
        direct_checks.append(executions[label].get("source_modeldata_before_after", {}).get("exact_equal", False))
        direct_checks.append(executions[label].get("runtime_before_after", {}).get("exact_equal", False))
        applicable = direct_checks + coefficient_checks
        checks.append(all(applicable))
        summary[label + "_full_direct_returns_and_runtime_equivalent"] = all(direct_checks)
        summary[label + "_saved_coefficient_reconciliation_passed"] = all(coefficient_checks)
        summary[label + "_retained_equivalence_under_frozen_policy"] = all(applicable)
    summary["all_trials_equivalent_under_frozen_policy"] = all(checks) and preserved
    save(QA / "diagnostic_replication.json", summary)
    artifact_paths = [QA / "diagnostic_replication.json", QA / "diagnostic_replication_preflight.json", Path(__file__)]
    artifact_paths += [p for label in executions for p in (OUT / label).iterdir() if p.is_file()]
    artifact_paths += [ROOT / MODEL_REL / "model.json", ROOT / MODEL_REL / "sppr_source.xlsx", retained / "complete_input_identity.json"]
    import os as path_os
    artifacts = [{"role": p.relative_to(ROOT).as_posix(), "path": Path(path_os.path.relpath(p, QA)).as_posix(), "sha256": sha(p), "availability": "present"} for p in artifact_paths]
    inventory = {"schema_version": 1, "run_id": RUN.name, "region_id": "LME_036", "model_id": MID,
        "variant_id": "exact_historical_and_current_compatibility_tool_regeneration", "source_identity": {"path": MODEL_REL.as_posix() + "/model.json", "sha256": EXPECTED_MODEL},
        "computational_input_identity": {"retained_settings": preflight["retained_input_identity"], "historical_code": preflight["exact_historical_imported_code"], "current_compatibility_setting": preflight["current_compatibility_setting"]},
        "methods": list(METHODS), "required_roles": [a["role"] for a in artifacts], "artifacts": artifacts,
        "reconciliation": {"protected_hashes_unchanged": preserved,
            "historical_direct_reports_matrices_runtime": summary["exact_historical_full_direct_returns_and_runtime_equivalent"],
            "current_compatibility_direct_reports_matrices_runtime": summary["current_compatibility_full_direct_returns_and_runtime_equivalent"],
            "saved_coefficient_reconciliation": all(summary[label + "_saved_coefficient_reconciliation_passed"] for label in executions)}}
    save(QA / "diagnostic_replication_evidence_index.json", inventory)
    print(json.dumps({"summary": str(QA / "diagnostic_replication.json"), "equivalent": summary["all_trials_equivalent_under_frozen_policy"],
                      "protected_hashes_unchanged": preserved, "seconds": summary["measurement"]["total_wall_seconds"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=("exact_historical", "current_compatibility"))
    parser.add_argument("--engine-dir", type=Path)
    parser.add_argument("--compare-existing", action="store_true", help="Recheck this trial's own saved outputs without invoking the engine")
    args = parser.parse_args()
    if args.worker: worker(args.worker, args.engine_dir)
    else: main(args.compare_existing)
