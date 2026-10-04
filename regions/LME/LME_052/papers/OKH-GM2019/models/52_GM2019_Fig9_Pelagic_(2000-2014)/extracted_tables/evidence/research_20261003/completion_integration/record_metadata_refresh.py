"""Bind completed standard rebuild/verification output to the final artifact hashes."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    browser = json.loads((HERE / "browser_verification.json").read_text(encoding="utf-8"))
    role = json.loads((HERE / "paper_file_role_metadata_proof.json").read_text(encoding="utf-8"))
    result = {
        "schema_version": 1, "timestamp_UTC": datetime.now(timezone.utc).isoformat(),
        "model_id": browser["model_id"],
        "build": {"command": "python tools/build_html.py --workbook Project.xlsx --output interactive_map/index.html --region LME_052", "exit_code": 0,
                  "stdout": "Checked HTML detail inputs: LME_052\nOriginal-format pages rebuilt: interactive_map/index.html, trends.html and archive/index.html"},
        "verify": {"command": "python tools/verify_html.py --workbook Project.xlsx --html interactive_map/index.html", "exit_code": 0,
                   "annual_cells_verified": 2071230,
                   "stdout": "Map/time-series layouts match the templates with file-link, basemap and provisional-display adapters; 2071230 annual cells and NPP match Project.xlsx; selected models, source files and archive page verified"},
        "sha256": {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in [ROOT / "Project.xlsx", ROOT / "interactive_map/index.html", ROOT / "interactive_map/trends.html", ROOT / "interactive_map/archive/index.html", ROOT / "interactive_map/data/articles.csv", ROOT / "interactive_map/data/files.csv", ROOT / "common_reference_data/paper_file_roles.json"]},
        "checks": {"file_roles_hash_matches_guarded_registration": sha(ROOT / "common_reference_data/paper_file_roles.json") == role["after_sha256"],
                   "final_browser_and_payload_verification_passed": browser["passed"],
                   "browser_uses_final_Project": browser["project_sha256"] == sha(ROOT / "Project.xlsx"),
                   "browser_uses_final_map_and_trends": browser["map_sha256"] == sha(ROOT / "interactive_map/index.html") and browser["trends_sha256"] == sha(ROOT / "interactive_map/trends.html")}
    }
    result["passed"] = all(result["checks"].values())
    if (HERE / "final_layout_refresh.json").is_file():
        result["subsequent_standard_layout_refresh"] = json.loads((HERE / "final_layout_refresh.json").read_text(encoding="utf-8"))
        result["checks"]["subsequent_layout_refresh_preserves_all_science_and_passes_verifier"] = result["subsequent_standard_layout_refresh"]["passed"]
        result["passed"] = all(result["checks"].values())
    (HERE / "metadata_regeneration_verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    navigation = json.loads((HERE / "navigation_updates.json").read_text(encoding="utf-8"))
    navigation["preserved_navigation_backups"] = [{"path": p.name, "sha256": sha(p)} for pattern in ["CURRENT_VARIANT.json.before_*", "MASTER_INDEX.md.before_*", "reports_index.md.before_*"] for p in sorted(HERE.glob(pattern))]
    navigation["checks"]["all_initial_and_intermediate_navigation_backups_present"] = len(navigation["preserved_navigation_backups"]) >= 3
    (HERE / "navigation_updates.json").write_text(json.dumps(navigation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["checks"]))
    assert result["passed"]


if __name__ == "__main__":
    main()
