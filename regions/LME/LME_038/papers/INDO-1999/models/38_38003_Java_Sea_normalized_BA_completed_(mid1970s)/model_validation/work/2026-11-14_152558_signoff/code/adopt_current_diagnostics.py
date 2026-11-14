"""Prepare the current Java Sea diagnostic adoption; apply only in a caller's journal.

This is a scoped evidence importer, not a calculator modification. The verified
GE/TE/With Egestion returns are imported without execution. Other canonical
methods are requested from the supported adapter, which may record NOT_RUN.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import gzip
import json
import math
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT = Path(__file__).resolve()
RUN = SCRIPT.parents[1]
MODEL = RUN.parents[2]
ROOT = next(p for p in MODEL.parents if (p / "tools/project_core").is_dir())
REGION = ROOT / "regions/LME/LME_038/LME_038.xlsx"
DIRECT = MODEL / "results/diagnostics/validation_20261114"
DEFAULT_PACKAGE = RUN / "outputs/current_adoption_v3"
PREFIX = "method_coverage/current_validation_20261114"
METHODS = {"new_GE": "GE", "new_TE_EEfix": "TE", "new_WithEgestion": "With Egestion"}
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _relative(path, base=ROOT):
    return Path(path).resolve().relative_to(Path(base).resolve()).as_posix()


def _fingerprint(path):
    return _sha(path) if Path(path).is_file() else None


def _check_inputs(inputs):
    for name, expected in inputs.items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or _fingerprint(path) != expected:
            raise ValueError("Consumed input changed: " + name)


def _near(a, b):
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12)


def _verify_direct(book):
    """Reopen exact package bytes and all matrix/scope/footprint relationships."""
    from tools.project_core.workbooks.workbooks import records
    evidence = _read(DIRECT / "execution_evidence.json")
    current = _sha(MODEL / "model.json")
    if evidence["canonical_sha256_before"] != current or evidence["canonical_sha256_after"] != current:
        raise ValueError("Direct evidence does not identify current canonical input")
    if evidence.get("construction", {}).get("status") != "constructed":
        raise ValueError("Direct constructor was not completed")
    if not all(v is True for v in evidence["preservation_checks"].values()):
        raise ValueError("Direct preservation check failed")
    index = _read(DIRECT / "evidence_index.json")
    consumed = {MODEL / "model.json", SCRIPT}
    for item in index["artifacts"]:
        path = (DIRECT / item["path"]).resolve()
        if not path.is_relative_to(MODEL) or item.get("availability") != "present" or _sha(path) != item["sha256"]:
            raise ValueError("Direct evidence hash mismatch: " + item["path"])
        consumed.add(path)
    consumed.update(DIRECT / name for name in ("evidence_index.json", "completeness.json", "loaded_groups.json"))
    checks = _read(DIRECT / "verification.json")["checks"]
    if not all(v is True for v in checks.values()) or _read(DIRECT / "completeness.json").get("complete") is not True:
        raise ValueError("Direct package is not verified complete")
    engines = {}
    engine_hashes = {}
    for item in evidence["engine_files"]:
        path = (DIRECT / item["path"]).resolve()
        if not path.is_relative_to(MODEL) or _sha(path) != item["sha256"]:
            raise ValueError("Pinned direct engine changed")
        engines[path.name] = _relative(path, MODEL)
        engine_hashes[path.name] = item["sha256"]
        consumed.add(path)
    if set(engines) != {"PPRCalculator.py", "ModelData.py", "utils.py"}:
        raise ValueError("Incomplete pinned engine identity")
    script = (DIRECT / evidence["script_path"]).resolve()
    if _sha(script) != evidence["script_sha256"]:
        raise ValueError("Direct execution script changed")
    consumed.add(script)
    flags = {
        "constructor": copy.deepcopy(evidence["constructor_settings"]),
        "diagnostics": {**copy.deepcopy(evidence["diagnostic_settings"]),
                        "thresholds": copy.deepcopy(evidence["effective_thresholds"])},
        "methods": {}, "mc": {}, "engine_sources": engines,
        "engine_source_hashes": engine_hashes,
        "configuration_evidence": [{"relative_path": _relative(path, MODEL), "sha256": _sha(path),
                                     "original_source_hash": current}
                                    for path in [DIRECT / "execution_evidence.json", *sorted(consumed & {MODEL / p for p in engines.values()})]],
    }
    # The executed pre-floor engine has no floor kwargs. Its exact bytes, rather
    # than an unsupported modern constructor argument, establish floor absence.
    if evidence.get("ee_floor", {}).get("applied") is not False:
        raise ValueError("This importer is limited to the audited pre-floor run")
    groups = _read(DIRECT / "loaded_groups.json")
    names = dict(zip(groups["index"], [r[groups["columns"].index("group_name")] for r in groups["data"]]))
    catch = dict(zip(groups["index"], [r[groups["columns"].index("catch")] for r in groups["data"]]))
    existing_groups = records(book, "Selected model groups", "Groups")
    if {int(r["seq"]): r["group_name"] for r in existing_groups} != names:
        raise ValueError("Current workbook group identities differ from direct evidence")
    by_id = {int(r["seq"]): r for r in existing_groups}
    for gid, values in zip(groups["index"], groups["data"]):
        for field, value in zip(groups["columns"], values):
            original = by_id[gid].get(field)
            if isinstance(value, dict) and value.get("__nonfinite__") == "NaN":
                if original is not None:
                    raise ValueError("Group missingness differs: " + field)
            elif isinstance(value, (float, int)):
                if not isinstance(original, (float, int)) or not _near(value, original):
                    raise ValueError("Group value differs: " + field)
            elif value != original:
                raise ValueError("Group text differs: " + field)
    reports = _read(DIRECT / "direct_reports.json")
    matrices = _read(DIRECT / "direct_solutions.json")
    metadata = _read(DIRECT / "matrices_metadata.json")
    coefficients = _read(DIRECT / "group_scope_coefficients.json")
    expected_keys = {(method, scope, gid) for method in METHODS.values() for scope in ("all", "inner", "PP") for gid in names}
    keys = [(r["method"], r["scope"], r["group_id"]) for r in coefficients]
    if len(keys) != len(set(keys)) or set(keys) != expected_keys or set(reports) != set(METHODS.values()):
        raise ValueError("Direct coefficient inventory is incomplete or duplicated")
    values = {key: row for key, row in zip(keys, coefficients)}
    negative = []
    for method, returned in matrices.items():
        for kind, matrix in returned.items():
            meta = next(m for m in metadata if m["method"] == method and m["matrix"] == kind)
            if (len(set(matrix["index"])) != len(matrix["index"]) or
                    len(set(matrix["columns"])) != len(matrix["columns"]) or
                    matrix["index"] != meta["row_ids"] or matrix["columns"] != meta["column_ids"] or
                    [names[i] for i in matrix["index"]] != meta["row_names"] or
                    [names[i] for i in matrix["columns"]] != meta["column_names"]):
                raise ValueError("Direct matrix axes differ")
            if meta["shape"] != [len(matrix["index"]), len(matrix["columns"])]:
                raise ValueError("Direct matrix shape differs")
            if len(matrix["data"]) != len(matrix["index"]) or any(len(r) != len(matrix["columns"]) for r in matrix["data"]):
                raise ValueError("Direct matrix dimensions differ")
            if not all(isinstance(v, (int, float)) and math.isfinite(v) for r in matrix["data"] for v in r):
                raise ValueError("Direct matrix has nonfinite coefficients")
            for mask in ("null_mask", "nan_mask", "positive_infinity_mask", "negative_infinity_mask"):
                if len(meta[mask]) != len(matrix["data"]) or any(len(r) != len(matrix["columns"]) or any(r) for r in meta[mask]):
                    raise ValueError("Direct finite mask differs")
        matrix = returned["SPPR"]
        meta = next(m for m in metadata if m["method"] == method and m["matrix"] == "SPPR")
        for gid, row in zip(matrix["index"], matrix["data"]):
            for sid, v in zip(matrix["columns"], row):
                if v < 0:
                    negative.append(dict(method=method, matrix="SPPR", source_id=sid, source_name=names[sid], group_id=gid, group_name=names[gid], sppr_value=v))
            for scope, ids in meta["source_scope_definitions"].items():
                stored = values[method, scope, gid]
                total = math.fsum(row[matrix["columns"].index(i)] for i in ids)
                if stored["group_name"] != names[gid] or not _near(total, stored["sppr"]):
                    raise ValueError("Direct scoped coefficient does not reconcile")
        for scope, field in (("all", "ppr_all"), ("inner", "ppr_inner"), ("PP", "ppr_pp_only")):
            value = math.fsum(values[method, scope, gid]["sppr"] * catch[gid] for gid in names)
            if not _near(value, reports[method]["footprint"][field]):
                raise ValueError("Direct footprint does not reconcile")
    if negative != _read(DIRECT / "negative_source_entries.json")["entries"]:
        raise ValueError("Negative source pairings differ")
    return flags, consumed, coefficients, reports, matrices


def _exact_source_numbers(path, book):
    """Preserve the imported float values exactly despite Excel writer rounding."""
    from tools.project_core.validation.researcher_review import sheet_xml, S
    from openpyxl.utils import get_column_letter
    from tools.project_core.workbooks.workbooks import records
    import openpyxl
    wanted = {(r["scope"], r["group"], r["method"]): r["sppr"] for r in records(book, "Selected model groups", "Group SPPR")}
    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    cells = {}
    try:
        for scope in ("all", "inner", "PP"):
            sheet = wb["sppr_" + scope]
            data = list(sheet.values)
            header = data[0]
            group_column = header.index("group_name")
            cells[sheet.title] = {get_column_letter(j) + str(i): wanted[scope, row[group_column], method]
                                  for i, row in enumerate(data[1:], 2)
                                  for j, method in enumerate(header, 1)
                                  if (scope, row[group_column], method) in wanted and wanted[scope, row[group_column], method] is not None}
    finally:
        wb.close()
    with zipfile.ZipFile(path) as archive:
        replaced = {}
        for name, numbers in cells.items():
            member, sheet = sheet_xml(archive, name)
            found = set()
            for cell in sheet.iter(f"{{{S}}}c"):
                address = cell.get("r")
                if address not in numbers:
                    continue
                node = cell.find(f"{{{S}}}v")
                if node is None or cell.find(f"{{{S}}}f") is not None or not _near(float(node.text), numbers[address]):
                    raise ValueError("Source coefficient serialization differs")
                node.text = repr(numbers[address])
                found.add(address)
            if found != set(numbers):
                raise ValueError("Source coefficient cells missing")
            replaced[member] = ET.tostring(sheet, encoding="utf-8")
        members = [(item, replaced.get(item.filename, archive.read(item.filename))) for item in archive.infolist()]
    with zipfile.ZipFile(path, "w") as archive:
        for item, data in members:
            archive.writestr(item, data)


def verify_package(package_path=None, *, check_inputs=True):
    from tools.project_core.calculations import coverage
    from tools.project_core.workbooks.workbooks import read_book, input_hash, overview
    from tools.project_core.calculations.regional import result_hash
    package = Path(package_path or DEFAULT_PACKAGE).resolve()
    plan = _read(package / "preparation.json")
    if check_inputs:
        _check_inputs(plan["consumed_inputs"])
    for item in plan["promotions"]:
        source = (package / item["source"]).resolve()
        target = (ROOT / item["target"]).resolve()
        if not source.is_relative_to(package) or not target.is_relative_to(ROOT) or _sha(source) != item["sha256"]:
            raise ValueError("Prepared promotion changed")
    book = read_book(package / "regional/LME_038.xlsx")
    manifest = _read(package / "model/results/result_manifest.json")
    if coverage._preserved_inputs(book) != plan["protected_inputs_sha256"]:
        raise ValueError("Prepared workbook changed a protected input")
    if overview(book).get("calculation_input_sha256") != input_hash(book) or overview(book).get("calculation_result_sha256") != result_hash(book):
        raise ValueError("Prepared calculation fingerprints are stale")
    cached = coverage._package_cache_valid(package / "model", package / "regional/LME_038.xlsx", manifest, plan["context"], plan["expected_methods"])
    if not cached or not coverage._source_matches(package / "model", book, plan["expected_methods"]):
        raise ValueError("Prepared package cannot pass the canonical coverage cache")
    coefficients = _read(DIRECT / "group_scope_coefficients.json")
    from tools.project_core.workbooks.workbooks import records
    actual = {(r["method"], r["scope"], r["group"]): r["sppr"] for r in records(book, "Selected model groups", "Group SPPR")}
    inverse = {option: key for key, option in METHODS.items()}
    if any(actual[inverse[r["method"]], r["scope"], r["group_name"]] != r["sppr"] for r in coefficients):
        raise ValueError("Prepared workbook did not preserve exact imported coefficients")
    return plan


def prepare(package_path=None, *, progress=print, resume_from=None):
    """Write only this signoff run's inputs and staged outputs; never adopt."""
    from tools.project_core.calculations import coverage
    from tools.project_core.calculations.snapshots import dependencies
    from tools.project_core.calculations.regional import set_setting
    from tools.project_core.workbooks.workbooks import read_book, rows, overview, input_hash, digest_tables
    from tools.scientific_helpers.sppr import method_coverage as adapter
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    package = Path(package_path or DEFAULT_PACKAGE).resolve()
    if not package.is_relative_to(RUN / "outputs"):
        raise ValueError("Prepared outputs must stay in this signoff run")
    if (package / "preparation.json").is_file():
        return verify_package(package)
    if package.exists() and any(package.iterdir()):
        raise ValueError("Partial package exists; inspect it and use a new outputs subdirectory")
    original = read_book(REGION)
    if overview(original).get("selected_model_id") != MODEL.name or rows(original, "Selected model groups", "Group SPPR"):
        raise ValueError("Importer expects the selected model's empty pending coefficient table")
    protected = coverage._preserved_inputs(original)
    flags, inputs, coefficients, reports, matrices = _verify_direct(original)
    # Resolve these explicitly bound flags through the unchanged shared resolver.
    flags = resolve_audited_configuration(MODEL, original, {"canonical_model_sha256": _sha(MODEL / "model.json"), "effective_flags": flags})
    keys = list(adapter.method_inventory())
    if not set(METHODS).issubset(keys):
        raise ValueError("Current canonical registry lacks reviewed methods")
    inputs.update([REGION, MODEL / "sppr_source.xlsx", MODEL / "results/regional_snapshot.xlsx", MODEL / "results/result_manifest.json"])
    inputs.update(adapter._engine_paths(flags, MODEL / "model.json").values())
    inputs.update([Path(adapter.__file__), adapter.ENGINE / "PPRCalculator.py", adapter.ENGINE / "create_PPRS_excel.py"])
    inputs.update(ROOT / "tools/project_core" / name for name in coverage._arithmetic_identity())
    input_hashes = {_relative(p): _fingerprint(p) for p in sorted(inputs)}
    historical = RUN / "inputs/pre_adoption"
    backup_index = {}
    for path in (REGION, MODEL / "sppr_source.xlsx", MODEL / "results/regional_snapshot.xlsx", MODEL / "results/result_manifest.json"):
        destination = historical / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and _sha(destination) != _sha(path):
            raise ValueError("Historical backup already exists with different bytes")
        if not destination.exists():
            shutil.copyfile(path, destination)
        backup_index[_relative(path)] = {"path": _relative(destination, MODEL), "sha256": _sha(destination)}
    _write(historical / "backup_index.json", backup_index)
    stage_model = package / "model"
    stage_region = package / "regional/LME_038.xlsx"
    evidence_dir = stage_model / "results/diagnostics" / PREFIX
    evidence_dir.mkdir(parents=True)
    stage_region.parent.mkdir(parents=True)
    shutil.copyfile(REGION, stage_region)
    shutil.copyfile(MODEL / "sppr_source.xlsx", stage_model / "sppr_source.xlsx")
    context = coverage._context(ROOT, MODEL / "model.json", flags)
    missing = [key for key in keys if key not in METHODS]
    prior = Path(resume_from).resolve() if resume_from else None
    if prior is not None:
        if not prior.is_relative_to(RUN / "outputs") or prior == package:
            raise ValueError("Resume source must be a distinct output package in this run")
        previous_evidence = prior / "model/results/diagnostics" / PREFIX
        index_path = previous_evidence / "method_coverage.json.gz"
        calculated = json.loads(gzip.decompress(index_path.read_bytes()))
        if (calculated.get("model_sha256") != _sha(MODEL / "model.json") or
                calculated.get("flags") != adapter.encode_lossless(flags) or
                calculated.get("adapter_sha256") != _sha(Path(adapter.__file__)) or
                set(calculated.get("methods", {})) != set(missing)):
            raise ValueError("Interrupted adapter evidence does not match current request")
        # Only complete explicit no-execution outcomes are resumed here.
        if any(o.get("status") != "NOT_RUN" or not o.get("reason") for o in calculated["methods"].values()):
            raise ValueError("Interrupted evidence is outside this no-execution resume scope")
        calculated["evidence_index"] = {"path": index_path.name, "sha256": _sha(index_path), "availability": "present"}
        references = [o["evidence"] for o in calculated["methods"].values()]
        references.extend(calculated[k] for k in ("constructor_evidence", "evidence_index"))
        for reference in references:
            source = (previous_evidence / reference["path"]).resolve()
            if not source.is_relative_to(previous_evidence) or _sha(source) != reference["sha256"]:
                raise ValueError("Interrupted adapter evidence changed")
            shutil.copyfile(source, evidence_dir / source.name)
        progress("Reused 19 verified NOT_RUN adapter records from the interrupted preparation")
    else:
        calculated = adapter.compute_methods(MODEL / "model.json", flags, missing, evidence_dir, progress=progress)
    outcomes = calculated["methods"]
    for key, option in METHODS.items():
        scopes = {scope: {r["group_name"]: r["sppr"] for r in coefficients if r["method"] == option and r["scope"] == scope}
                  for scope in ("all", "inner", "PP")}
        report = reports[option]
        negative = any(v < -adapter.NEGATIVE_TOLERANCE for row in matrices[option]["SPPR"]["data"] for v in row)
        status = "FAIL: negative SPPR in a source-model group" if negative else "FAIL: configuration diagnostic" if report["status"] == "FAIL" else "ok"
        certificate = {"schema_version": 1, "evidence_kind": "verified_current_direct_adoption", "method": key,
                       "adopted_utc": datetime.now(timezone.utc).isoformat(), "context": context,
                       "executed_at": _read(DIRECT / "execution_evidence.json")["finished_utc"],
                       "scientific_execution_performed_by_adoption": False,
                       "source_package": _relative(DIRECT, MODEL), "scopes": scopes,
                       "direct_report": report, "direct_matrices": matrices[option],
                       "source_artifacts": [{"path": _relative(p, MODEL), "sha256": _sha(p)}
                                            for p in sorted(inputs) if p.is_relative_to(DIRECT)],
                       "reconciliation": {"all_scopes_vs_matrix_sums_at_1e_12": True,
                                          "matrix_axes_and_finite_masks": True, "footprint_at_1e_12": True,
                                          "exact_saved_coefficient_values_imported": True,
                                          "workbook_groups_preserved": True}}
        evidence = adapter._save(evidence_dir / (key + ".adopted.json.gz"), certificate)
        outcomes[key] = {"status": "reused", "reason": "Verified current-input direct return adopted without rerunning; original diagnostic status " + report["status"],
                         "evidence_kind": certificate["evidence_kind"], "scopes": scopes,
                         "annual_status": {scope: status for scope in scopes}, "diagnostics": adapter.encode_lossless(report),
                         "evidence": evidence}
    outcomes = {key: outcomes[key] for key in keys}
    for outcome in outcomes.values():
        outcome["evidence"]["path"] = PREFIX + "/" + outcome["evidence"]["path"]
    execution_evidence = {key: {**calculated[key], "path": PREFIX + "/" + calculated[key]["path"]}
                          for key in ("constructor_evidence", "evidence_index") if key in calculated}
    book = copy.deepcopy(original)
    coverage._apply_outcomes(book, MODEL.name, outcomes, keys)
    set_setting(book, "sppr_engine_hashes", json.dumps({k: v for k, v in context["code_identity"].items() if k != "create_PPRS_excel.py"}))
    coverage._arithmetic(book, REGION, MODEL / "model.json", flags, original)
    # Treat the just-imported exact numbers as the preservation baseline for
    # serialization. This does not assert historical identity or rerun SPPR.
    progress("Saving freshly rebuilt regional tables with exact imported coefficient values")
    saved = coverage._save_calculation(stage_region, book, MODEL / "model.json", flags, copy.deepcopy(book))
    if coverage._preserved_inputs(saved) != protected:
        raise ValueError("Prepared adoption changed protected scientific inputs")
    progress("Updating staged coefficient source and restoring exact numeric values")
    coverage._update_source(stage_model / "sppr_source.xlsx", saved, outcomes, replace_methods=keys)
    _exact_source_numbers(stage_model / "sppr_source.xlsx", saved)
    set_setting(saved, "results_source_sha256", _sha(stage_model / "sppr_source.xlsx"))
    progress("Saving final staged source identity before snapshot and cache verification")
    saved = coverage._save_calculation(stage_region, saved, MODEL / "model.json", flags, copy.deepcopy(saved))
    snapshot = stage_model / "results/regional_snapshot.xlsx"
    shutil.copyfile(stage_region, snapshot)
    row_hashes = coverage._method_rows(saved)[1]
    for key in keys:
        outcomes[key]["group_rows_sha256"] = row_hashes[key]
    manifest = {"schema_version": 1, "unit_id": "LME_038", "model_id": MODEL.name,
                "snapshot_selected_model_id": MODEL.name, "timestamp": datetime.now(timezone.utc).isoformat(),
                "canonical_model_sha256": _sha(MODEL / "model.json"), "present_canonical_model_sha256": _sha(MODEL / "model.json"),
                "snapshot_sha256": _sha(snapshot), "coefficient_source_sha256": _sha(stage_model / "sppr_source.xlsx"),
                "effective_flags": flags, "code_identity": {k: v for k, v in context["code_identity"].items() if k != "create_PPRS_excel.py"},
                "provenance_status": "Three verified current-input direct results adopted; remaining canonical methods have explicit adapter outcomes. Historical snapshot is not relabeled.",
                "dependencies": dependencies(saved), "artifacts": {"snapshot": "regional_snapshot.xlsx", "model": "../model.json", "coefficients": "../sppr_source.xlsx"},
                "historical_package_backup": backup_index,
                "method_coverage": {"schema_version": 1, "expected_methods": keys, "context": context, "methods": outcomes,
                                    "execution_evidence": execution_evidence, "arithmetic_code_identity": coverage._arithmetic_identity(),
                                    "protected_inputs_sha256": protected}}
    _write(stage_model / "results/result_manifest.json", manifest)
    promotions = [{"source": _relative(stage_region, package), "target": _relative(REGION), "sha256": _sha(stage_region)}]
    for source in sorted(p for p in stage_model.rglob("*") if p.is_file()):
        target = MODEL / source.relative_to(stage_model)
        promotions.append({"source": _relative(source, package), "target": _relative(target), "sha256": _sha(source)})
        input_hashes.setdefault(_relative(target), _fingerprint(target))
    _check_inputs(input_hashes)
    plan = {"schema_version": 1, "prepared_utc": datetime.now(timezone.utc).isoformat(), "package": _relative(package),
            "unit_id": "LME_038", "model_id": MODEL.name, "consumed_inputs": input_hashes,
            "expected_methods": keys, "context": context, "protected_inputs_sha256": protected,
            "promotions": promotions, "method_outcomes": {key: {"status": o["status"], "reason": o.get("reason"), "evidence": o["evidence"]} for key, o in outcomes.items()},
            "numerical_adoption_performed": False}
    _write(package / "preparation.json", plan)
    progress("Reopening prepared artifacts and verifying the canonical coverage cache")
    verify_package(package)
    return plan


def apply(publication, package_path=None):
    """Adopt staged bytes inside the caller's existing lock and transaction."""
    from tools.project_core.registry.publication import _ACTIVE, publication_write
    from tools.project_core.calculations.coverage import _write_bytes
    package = Path(package_path or DEFAULT_PACKAGE).resolve()
    if publication not in _ACTIVE.get() or publication.root != ROOT:
        raise ValueError("Apply requires the caller's active project publication transaction")
    lock = ROOT / ".project-write.lock"
    if not lock.is_file() or lock.read_text().strip() != str(os.getpid()):
        raise ValueError("Apply requires this process to hold the project writer lock")
    plan = verify_package(package, check_inputs=False)
    targets = {item["target"] for item in plan["promotions"]}
    _check_inputs({name: value for name, value in plan["consumed_inputs"].items() if name not in targets})
    if all(_fingerprint(ROOT / item["target"]) == item["sha256"] for item in plan["promotions"]):
        return {"status": "already_applied", "changed_units": ["LME_038"], "written_paths": []}
    _check_inputs(plan["consumed_inputs"])
    written = []
    for item in plan["promotions"]:
        source, target = package / item["source"], ROOT / item["target"]
        # Every target is explicitly captured by this preparation and journal.
        expected = plan["consumed_inputs"][item["target"]]
        with publication_write(target, fingerprint=item["sha256"]):
            _write_bytes(target, source.read_bytes(), expected_sha256=expected)
        written.append(str(target))
    from tools.project_core.calculations.coverage import _package_cache_valid
    manifest = _read(MODEL / "results/result_manifest.json")
    if not _package_cache_valid(MODEL, REGION, manifest, plan["context"], plan["expected_methods"]):
        raise ValueError("Installed package failed canonical coverage cache verification")
    return {"status": "applied", "changed_units": ["LME_038"], "written_paths": written,
            "written_hashes": {str(ROOT / p["target"]): p["sha256"] for p in plan["promotions"]}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("--package", type=Path)
    parser.add_argument("--resume-from", type=Path)
    args = parser.parse_args()
    result = prepare(args.package, resume_from=args.resume_from) if args.command == "prepare" else verify_package(args.package)
    print(json.dumps({"package": result["package"], "methods": {key: value["status"] for key, value in result["method_outcomes"].items()}, "promotions": len(result["promotions"])}, ensure_ascii=False))
