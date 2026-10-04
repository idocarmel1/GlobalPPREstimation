"""Reconcile observed browser text with independently recomputed file payloads."""
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path[:0] = [str(ROOT / "tools"), str(HERE.parent / "integration")]
from original_atlas_data import embedded
from regional_book_io import read_fast
from workbooks import records

MID = "52_GM2019_Fig9_Pelagic_balanced_(2000-2014)"
PAPER = "OKH-GM2019__LME_052"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    observed = json.loads((HERE / "browser_observations.json").read_text(encoding="utf-8"))
    db, text = embedded(ROOT / "interactive_map/index.html", "DB")
    series, _ = embedded(ROOT / "interactive_map/trends.html", "SERIES_DB")
    unit = db["network"]["units"]["LME_052"]
    model = next(m for m in unit["models"] if m["id"] == MID)
    annual = records(read_fast(ROOT / "regions/LME_052/LME_052.xlsx"), "PPR", "Annual")
    yi = unit["years"].index(2019)
    rows = []
    for obs in observed["observations"]:
        method, scope = obs["method"], obs["scope"]
        data = model["scopes"][scope]
        mi = data["methods"].index(method)
        computed = sum(c[yi] * values[mi] for c, values in zip(unit["landings"], data["values"])
                       if values[mi] is not None and math.isfinite(values[mi]) and values[mi] >= 0) / 9
        record = next(r for r in annual if r["model_id"] == MID and r["method"] == method and r["scope"] == scope and r["catch_basis"] == "landings" and r["unidentified"] == "method" and r["metric"] == "ppr")
        expected = record[2019] / 9
        display = re.search(r"([\d,]+) t C", obs["detail"])
        rounded = float(f"{computed:.4g}")
        rows.append({"method": method, "scope": scope, "computed_tC": computed, "regional_tC": expected,
                     "observed_display": display.group(1) if display else None,
                     "rounded_display_matches": display is not None and int(display.group(1).replace(",", "")) == rounded,
                     "regional_matches": math.isclose(computed, expected, rel_tol=2e-14, abs_tol=1e-6)})
    paper = next(a for a in db["articles"] if a["article_id"] == PAPER)
    materials = paper["material_files"]
    jsonfiles = [f for f in materials if f["relative_path"].endswith(".json")]
    initial = observed["observations"][0]["group_settings"]
    final = observed["finalSettings"]
    trend_model = next(m for m in series["units"]["LME_052"]["models"] if m["id"] == MID)
    trend_record = trend_model["scopes"]["all"]["methods"]["new_GE"]
    # Source series remains in wet equivalent mass, with one display division by9.
    trend_exact = trend_record["ppr"][yi] / 9
    checks = {
        "all_observed_map_values_match_regional_and_payload": all(r["rounded_display_matches"] and r["regional_matches"] for r in rows),
        "all_23_groups_included": len(observed["groups"]["rows"]) == 23 and all(r["checked"] for r in observed["groups"]["rows"]),
        "bacteria_protozoa_and_detritus_visible": all(any(n in r["text"] for r in observed["groups"]["rows"]) for n in ["Bacteria", "Protozoa", "Detritus"]),
        "zero_researcher_exclusions_for_new_model": "0 researcher exclusions" in observed["groups"]["text"],
        "other_saved_model_choices_preserved_during_final_checks": {k:v for k,v in initial["models"].items() if k != "LME_052"} == {k:v for k,v in final["models"].items() if k != "LME_052"},
        "all_26_prior_table_preferences_preserved": len(initial["tables"]) == 26 and all(final["tables"].get(k) == v for k,v in initial["tables"].items()),
        "selected_new_model_persisted": final["models"]["LME_052"] == MID,
        "native_diagnostics_WARN_visible": all(m + " WARN" in observed["finalMetadata"]["text"] for m in ["GE", "TE", "With Egestion"]),
        "researcher_review_pending_visible": "Model not yet validated by researcher" in observed["finalMetadata"]["text"],
        "five_JSONs_all_context_not_model": len(jsonfiles) == 5 and all(f["role"] == "context" and "Provenance:" in f["file_label"] for f in jsonfiles),
        "one_original_primary_article": len([f for f in materials if f["role"] == "main"]) == 1 and "original Russian" in next(f for f in materials if f["role"] == "main")["file_label"],
        "translation_labeled_unofficial": any("Unofficial English translation" in f["file_label"] and f["role"] == "context" for f in materials),
        "live_source_labels_updated": "Model source JSON" not in observed["finalMetadata"]["text"] and "Provenance: original source identities" in observed["finalMetadata"]["text"],
        "time_series_chart_rendered": observed["trends"]["svgCount"] == 1 and "Sea of Okhotsk · 1950–2019" in observed["trends"]["body"],
        "time_series_exclusion_caption_correct": "All model groups included" in observed["trends"]["body"] and "groups excluded from displayed PPR by researcher" not in observed["trends"]["body"],
        "time_series_value_correct": f"{float(f'{trend_exact:.5g}'):,.0f} t C" in observed["trends"]["body"],
        "time_series_new_model_carried_in_URL": MID in __import__("urllib.parse", fromlist=["unquote"]).unquote(observed["trends"]["url"]),
        "two_saved_nonempty_screenshots": all((HERE / n).stat().st_size > 10000 for n in ["browser_map.jpg", "browser_trends.jpg"]),
        "fresh_project_fingerprint": sha(ROOT / "Project.xlsx") in text,
    }
    result = {"schema_version": 1, "model_id": MID, "project_sha256": sha(ROOT / "Project.xlsx"), "regional_sha256": sha(ROOT / "regions/LME_052/LME_052.xlsx"), "map_sha256": sha(ROOT / "interactive_map/index.html"), "trends_sha256": sha(ROOT / "interactive_map/trends.html"), "observations_path": "browser_observations.json", "map_comparisons": rows, "time_series_2019_exact_tC": trend_exact, "checks": checks, "passed": all(checks.values())}
    (HERE / "browser_verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"comparisons": rows, "checks": checks, "passed": result["passed"]}, ensure_ascii=False, indent=2))
    assert result["passed"]


if __name__ == "__main__":
    main()
