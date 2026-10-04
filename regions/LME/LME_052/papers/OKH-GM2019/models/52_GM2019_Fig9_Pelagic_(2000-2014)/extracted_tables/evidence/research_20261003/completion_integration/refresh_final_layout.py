"""Run standard presentation refresh with exact before/after science guards."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "tools"))
from original_atlas_data import embedded


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def payload_hashes():
    return {name: hashlib.sha256(json.dumps(embedded(ROOT / "interactive_map" / name, variable)[0], sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
            for name, variable in [("index.html", "DB"), ("trends.html", "SERIES_DB")]}


def main():
    model = HERE.parents[1] / "assumption_variants/adopted_balanced_20261003"
    protected = [ROOT / "Project.xlsx", ROOT / "regions/LME_052/LME_052.xlsx", model / "model.json", model / "evidence_index.json", model / "evidence_completeness.json", ROOT / "common_reference_data/paper_file_roles.json"]
    before = {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in protected}
    data_before = payload_hashes()
    cmds = [[sys.executable, str(ROOT / "tools/build_html.py"), "--workbook", str(ROOT / "Project.xlsx"), "--output", str(ROOT / "interactive_map/index.html"), "--layout-only"],
            [sys.executable, str(ROOT / "tools/verify_html.py"), "--workbook", str(ROOT / "Project.xlsx"), "--html", str(ROOT / "interactive_map/index.html")]]
    execution = []
    for args in cmds:
        completed = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        execution.append({"command": args, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
        print(completed.stdout, flush=True)
        if completed.returncode:
            print(completed.stderr, flush=True)
            break
    after = {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in protected}
    data_after = payload_hashes()
    proof = {"schema_version": 1, "reason": "Scope time-series group exclusion caption to displayed ecosystems while preserving all stored settings and all scientific payloads.",
             "execution": execution, "protected_before": before, "protected_after": after, "scientific_payload_hashes_before": data_before, "scientific_payload_hashes_after": data_after,
             "final_page_sha256": {name: sha(ROOT / "interactive_map" / name) for name in ["index.html", "trends.html"]},
             "checks": {"standard_layout_refresh_and_verifier_pass": len(execution) == 2 and all(r["exit_code"] == 0 for r in execution), "all_protected_files_byte_identical": before == after, "all_embedded_scientific_payloads_identical": data_before == data_after}}
    proof["passed"] = all(proof["checks"].values())
    (HERE / "final_layout_refresh.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(proof["checks"]), flush=True)
    assert proof["passed"]


if __name__ == "__main__":
    main()
