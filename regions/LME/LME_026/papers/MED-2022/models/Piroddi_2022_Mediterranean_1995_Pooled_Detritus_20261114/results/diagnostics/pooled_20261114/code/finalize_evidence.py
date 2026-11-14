"""Verify and index a completed pooled-model run without scientific execution.

Run only after the readable summary and final independent review are ready.
Existing diagnostic outputs are never changed. Exact watched tools/*.py bytes
are pinned only when they still match both execution-time hash inventories.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import runpy
import sys

sys.dont_write_bytecode = True
MODEL_ID = "Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114"
SOURCE_ID = "Piroddi_2022_Mediterranean_1995"
SOURCE_HASH = "f038707bf7837962933eec3e6daeae53eb0b9a7f48837763b0ce621edcdc3a9e"
PUBLISHED = {
    "s41598-022-18017-x-75a92a71.pdf": (
        "published_paper_pdf", "75a92a71a8925282375920beb6aa5acdea22af658e43d08a6f97363136511fad"),
    "41598_2022_18017_MOESM1_ESM-75e4d6d3.xlsx": (
        "published_parameter_workbook", "75e4d6d3437d9c1fafe41f8ae936192f6328e0cf4a6c9a2885be3cf297679882"),
    "41598_2022_18017_MOESM2_ESM-7d26163a.docx": (
        "published_parameter_document", "7d26163aa9f7868524e4c116940d0ada6ba4162c4a45bbdaaf8b193392aa5e84"),
}
METHODS = {"GE", "TE", "With Egestion"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return sha_bytes(Path(path).read_bytes())


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def relative(path, directory):
    return os.path.relpath(path, directory).replace("\\", "/")


def portable_target(directory, value, within=None):
    require(isinstance(value, str) and bool(value), "Missing artifact path")
    win = PureWindowsPath(value)
    require(not win.drive and not win.root and "://" not in value,
            f"Nonportable artifact path: {value}")
    target = (directory / Path(value.replace("\\", "/"))).resolve()
    if within is not None:
        require(target.is_relative_to(within.resolve()), f"Path escapes scope: {value}")
    require(target.name.casefold() != "notes for ai.txt", "Excluded file")
    return target


def write_new_or_identical(path, data):
    if path.exists():
        require(path.read_bytes() == data, f"Refusing to overwrite different bytes: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="outputs",
                        help="Completed diagnostic output directory relative to this run")
    args = parser.parse_args()
    run = Path(__file__).resolve().parents[1]
    model = run.parents[2]
    require(model.name == MODEL_ID and run.name == "pooled_20261114", "Wrong run identity")
    repo = next(p for p in model.parents if (p / "Project.xlsx").is_file())
    output = portable_target(run, args.output_dir, within=run)
    require(output != run and output.is_dir(), "Diagnostic output directory is unavailable")
    summary_path = output / "summary.json"
    manifest_path = output / "artifact_manifest.json"
    summary = read_json(summary_path)
    manifest = read_json(manifest_path)
    require(summary.get("schema_version") == manifest.get("schema_version") == 1,
            "Unsupported execution evidence schema")
    require(summary.get("model_id") == MODEL_ID and summary.get("base_model_id") == SOURCE_ID,
            "Summary model identity mismatch")
    require(summary.get("unit_id") == "LME_026", "Summary region mismatch")
    require(summary.get("status") in {"COMPLETE_OUTCOME_INVENTORY", "BLOCKED"},
            "Diagnostic execution is not complete")
    require(summary.get("adopted") is False, "Unexpected adopted calculation")
    require({m.get("method") for m in summary.get("methods", [])} == METHODS
            and len(summary["methods"]) == 3, "Incomplete or duplicate requested method inventory")
    require(manifest.get("model_id") == MODEL_ID and manifest.get("unit_id") == "LME_026"
            and manifest.get("run_id") == run.name, "Output manifest identity mismatch")
    require(set(manifest.get("required_methods", [])) == METHODS,
            "Output manifest method scope mismatch")
    require(manifest.get("artifact_hashes_rechecked") is True,
            "Runner did not verify its output hashes")

    before = summary.get("protected_hashes_before")
    after = summary.get("protected_hashes_after")
    require(isinstance(before, dict) and before and before == after
            and summary.get("protected_bytes_unchanged") is True,
            "Execution-time source/engine protection failed")
    watched = {}
    for value, expected in before.items():
        path = portable_target(repo, value, within=repo)
        require(path.is_file() and sha(path) == expected,
                f"Watched execution source changed after the run: {value}")
        watched[path] = expected
    source = model.parent / SOURCE_ID / "model.json"
    canonical = model / "model.json"
    require(source in watched and watched[source] == SOURCE_HASH and sha(source) == SOURCE_HASH,
            "Original source model hash mismatch")
    require(canonical in watched, "Variant was not watched during execution")
    model_hash = sha(canonical)
    groups = read_json(canonical)["group"]
    require([g["group_seq"] for g in groups] == [str(i) for i in range(1, 71)],
            "Variant group identity mismatch")
    require(len(read_json(source)["group"]) == 71, "Original source group count changed")
    require(sum(str(g.get("pp")) == "2" for g in groups) == 1,
            "Variant does not have exactly one detritus pool")

    ledger = read_json(run / "aggregation_ledger.json")
    provenance = read_json(model / "inputs/provenance.json")
    expected_flows = read_json(run / "independent_expected_flows.json")
    review = read_json(run / "independent_review.json")
    require(ledger.get("source_sha256_before") == ledger.get("source_sha256_after") == SOURCE_HASH
            and ledger.get("derived_model_sha256") == model_hash,
            "Aggregation ledger identity mismatch")
    require(provenance.get("model_id") == MODEL_ID
            and provenance.get("source", {}).get("sha256") == SOURCE_HASH
            and provenance.get("derived_model_sha256") == model_hash,
            "Input provenance identity mismatch")
    require(provenance.get("builder_sha256") == sha(run / "code/build_pooled_model.py"),
            "Builder changed since canonical creation")
    require(expected_flows.get("source_model_sha256") == SOURCE_HASH
            and expected_flows.get("pooled_model_sha256") == model_hash,
            "Independent expected-flow identity mismatch")
    require(review.get("model_id") == MODEL_ID
            and review.get("source_model_sha256") == SOURCE_HASH
            and review.get("derived_model_sha256") == model_hash,
            "Independent review identity mismatch")
    require(review.get("canonical_status") == "PASS"
            and bool(review.get("canonical_checks"))
            and all(value is True for value in review["canonical_checks"].values()),
            "Canonical independent review is incomplete or failed")
    diagnostic_review = review.get("diagnostic_output_review", {})
    require(diagnostic_review.get("status") == "PASS"
            and bool(diagnostic_review.get("checks"))
            and all(value is True for value in diagnostic_review["checks"].values()),
            "Final diagnostic artifact/accounting review is not PASS")
    require(review.get("scientific_approval") is False,
            "Independent review must not assert researcher approval")
    readable = run / "diagnostic_summary.md"
    require(readable.is_file() and readable.read_text(encoding="utf-8").strip(),
            "Readable diagnostic summary is not ready")

    artifacts = []
    roles = set()
    def add(role, path, expected=None):
        require(role not in roles, f"Duplicate evidence role: {role}")
        require(path.is_file(), f"Missing required artifact: {path}")
        digest = sha(path)
        require(expected is None or expected == digest, f"Artifact hash mismatch: {path}")
        artifacts.append({"role": role, "path": relative(path, run),
                          "sha256": digest, "availability": "present"})
        roles.add(role)

    add("original_canonical_model", source, SOURCE_HASH)
    for filename, (role, expected) in PUBLISHED.items():
        add(role, model.parent.parent / "sources" / filename, expected)
    fixed = {
        "derived_canonical_model": canonical,
        "derived_model_notes": model / "model_notes.md",
        "derived_input_provenance": model / "inputs/provenance.json",
        "complete_aggregation_ledger": run / "aggregation_ledger.json",
        "authorized_scenario_plan": run / "plan.md",
        "canonical_builder": run / "code/build_pooled_model.py",
        "executed_diagnostic_runner": run / "code/run_diagnostics.py",
        "independent_expected_flows": run / "independent_expected_flows.json",
        "final_independent_review": run / "independent_review.json",
        "readable_diagnostic_summary": readable,
        "diagnostic_output_artifact_manifest": manifest_path,
        "evidence_finalizer": Path(__file__).resolve(),
        "execution_log": run / "run.log",
        "bundled_runtime_bootstrap_failure": run / "bootstrap_bundled_failure.log",
    }
    for role, path in fixed.items():
        add(role, path)
    bootstrap_text = (run / "bootstrap_bundled_failure.log").read_text(encoding="utf-8")
    require("from PPRCalculator import PPRCalculator" in bootstrap_text
            and "No module named 'sympy'" in bootstrap_text,
            "Bootstrap environment-failure evidence differs from the recorded attempt")

    manifest_artifacts = manifest.get("artifacts")
    require(isinstance(manifest_artifacts, list) and manifest_artifacts,
            "Output artifact manifest is empty")
    manifest_roles = set()
    for item in manifest_artifacts:
        role = item.get("role")
        require(isinstance(role, str) and role and role not in manifest_roles,
                "Duplicate or missing output artifact role")
        require(item.get("availability") == "present",
                "Unexpected unavailable entry in the runner's saved-file manifest")
        digest = item.get("sha256")
        require(isinstance(digest, str) and len(digest) == 64
                and all(c in "0123456789abcdef" for c in digest),
                f"Output artifact lacks a valid SHA-256: {role}")
        path = portable_target(output, item.get("path"), within=output)
        add("diagnostic_output/" + role, path, digest)
        manifest_roles.add(role)
    require("machine_readable_outcome_summary" in manifest_roles
            and "execution_identity" in manifest_roles, "Essential runtime provenance is missing")

    unavailable = []
    for item in summary["methods"]:
        method = item["method"]
        slug = method.lower().replace(" ", "_")
        if item.get("execution") == "RETURNED":
            require(slug + "_lossless_direct_return" in manifest_roles
                    and slug + "_diagnostic_report" in manifest_roles,
                    f"Returned method lacks its full return/report: {method}")
            if "matrix_shape" in item:
                expected_roles = [slug + suffix for suffix in (
                    "_SPPR_matrix", "_A_matrix", "_L_matrix", "_scope_coefficients",
                    "_matrix_identity", "_all_strict_negative_entries")]
                require(all(role in manifest_roles for role in expected_roles),
                        f"Returned matrices are incompletely retained: {method}")
            else:
                unavailable.append({"role": slug + "_numerical_matrices",
                    "availability": "failed", "reason": item.get("matrix_unavailable_reason")
                    or "This diagnostic returned no matrices.",
                    "acquisition_status": "Recorded completed attempt; no rerun implied."})
        else:
            require(item.get("execution") in {"EXCEPTION", "NOT_RUN"},
                    f"Unrecognized method outcome: {method}")
            if item["execution"] == "EXCEPTION":
                require(slug + "_execution_exception" in manifest_roles,
                        f"Method exception evidence missing: {method}")
            else:
                require("blocked_execution_evidence" in manifest_roles,
                        f"NOT_RUN method lacks blocking evidence: {method}")
            unavailable.append({"role": slug + "_full_numerical_return",
                "availability": "failed", "reason": item.get("reason") or item.get("exception")
                or "Diagnostic method did not return numerical evidence.",
                "acquisition_status": "Explicit execution outcome retained; no rerun implied."})

    # Only code actually named in the execution-time watched inventory is pinned.
    # Models, runner and derived data stay in their single canonical locations.
    pins = []
    for path, digest in watched.items():
        repo_relative = path.relative_to(repo)
        if repo_relative.parts[0] != "tools" or path.suffix != ".py":
            continue
        data = path.read_bytes()
        require(sha_bytes(data) == digest, f"Engine source changed before pinning: {path}")
        destination = run / "code/executed_engine" / repo_relative
        if destination.exists():
            require(destination.read_bytes() == data,
                    f"Existing pinned engine bytes differ: {destination}")
        pins.append((path, destination, data, digest, repo_relative.as_posix()))
    require(bool(pins), "No watched tools source modules were available to pin")
    for _, destination, data, _, _ in pins:
        write_new_or_identical(destination, data)
    for _, destination, _, digest, repo_relative in pins:
        add("executed_engine/" + repo_relative, destination, digest)
    # A second live check prevents a post-run edit from being presented as the
    # executed engine, even if it happened during evidence packaging.
    require(all(sha(path) == digest for path, digest in watched.items()),
            "Watched input/code changed during finalization")
    require(all(sha(run / a["path"]) == a["sha256"] for a in artifacts),
            "Evidence changed during finalization")

    index = {
        "schema_version": 1, "run_id": run.name, "region_id": "LME_026",
        "model_id": MODEL_ID, "variant_id": MODEL_ID,
        "created_at": summary.get("completed_at"),
        "source_identity": {"model_id": SOURCE_ID, "model_sha256": SOURCE_HASH,
                            "source_files": [a for a in artifacts if a["role"].startswith("published_")]},
        "computational_input_identity": {
            "model_id": MODEL_ID, "model_sha256": model_hash,
            "runtime_initialization": summary.get("runtime_initialization"),
            "constructor": summary.get("constructor"), "method_options": summary.get("method_options"),
            "execution_summary": relative(summary_path, run),
            "executed_engine": [{"repository_relative_path": name,
                "pinned_path": relative(destination, run), "sha256": digest}
                for _, destination, _, digest, name in pins],
        },
        "methods": [item["method"] for item in summary["methods"]],
        "required_roles": sorted(roles), "artifacts": artifacts + unavailable,
        "execution_outcomes": [{key: item.get(key) for key in
            ("method", "execution", "status", "negative_entries", "negative_source_columns")}
            for item in summary["methods"]],
        "environment_attempts": [
            {"attempt": "bundled-runtime bootstrap", "outcome": "ModuleNotFoundError: sympy",
             "evidence": "bootstrap_bundled_failure.log", "scientific_constructors": 0,
             "diagnostic_calls": 0,
             "basis": "The traceback ends while importing PPRCalculator, before the runner's construction function is called."},
            {"attempt": "completed scientific execution", "evidence": "run.log",
             "runtime_identity": relative(output / "run_identity.json", run),
             "execution_status": summary["status"],
             "interpretation": "Execution completion does not imply diagnostic PASS."},
        ],
        "scientific_numerical_evidence_complete": not unavailable,
        "reconciliation": {
            "original_source_and_published_bytes_verified": True,
            "variant_and_aggregation_identity_verified": True,
            "execution_before_after_and_current_watched_hashes_exact": True,
            "output_manifest_all_listed_hashes_verified": True,
            "final_independent_canonical_checks_passed": True,
            "final_independent_artifact_and_accounting_checks_passed": True,
            "actual_executed_tools_source_pinned_without_model_duplication": True,
            "all_indexed_present_files_reopened_and_hashed": True,
        },
        "approval": "Experimental calculation only. Diagnostic status, evidence completeness and researcher approval remain separate; no selection, adoption or researcher approval.",
    }
    index_path = run / "evidence_index.json"
    index_bytes = (json.dumps(index, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    write_new_or_identical(index_path, index_bytes)
    checker_path = repo / "tools/skills/paper-to-ppr/scripts/check_evidence.py"
    checker = runpy.run_path(str(checker_path))["check"]
    completeness = checker(index_path)
    completeness_path = run / "completeness.json"
    write_new_or_identical(completeness_path,
        (json.dumps(completeness, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    require(completeness["complete"], "Standard evidence checker did not pass")
    print(json.dumps({"complete": True, "artifact_count": len(artifacts),
        "pinned_engine_modules": len(pins), "unavailable_numerical_roles": unavailable,
        "evidence_index": str(index_path), "completeness": str(completeness_path),
        "diagnostic_outputs_modified": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
