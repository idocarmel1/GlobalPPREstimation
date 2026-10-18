"""Bind this successor study to current authority and exact upstream evidence."""
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile


def validate_cohort(root, study, experiment, prior_path, records, prior, db, method, register):
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    read = lambda p: json.loads(p.read_text(encoding="utf-8-sig"))
    source = experiment / "inputs/cohort.json"
    cohort = read(source)
    assert cohort["schema_version"] == 1
    pairs = {(p["unit_id"], p["model_id"]) for p in cohort["pairs"]}
    assert len(pairs) == len(cohort["pairs"]) and pairs
    withdrawn = ("LME_028", "28_646_Guinea_(1998)")
    assert withdrawn not in pairs
    assert withdrawn in {(p["unit_id"], p["model_id"]) for p in cohort["excluded_pairs"]}
    project = root / cohort["project_path"]
    assert sha(project) == cohort["project_sha256"], "Cohort Project authority changed"
    sys.path.insert(0, str(root))
    from tools.project_core.validation.researcher_review import table_rows
    with zipfile.ZipFile(project) as archive:
        metadata = [r for _, r in table_rows(archive, "Models & coverage", "Models")[3]]
    positive = {(r["unit_id"], r["model_id"]) for r in metadata
                if r.get("researcher_review_status") == "Validated by researcher"}
    assert positive == pairs, ("Current positive cohort differs", positive, pairs)
    indexed = {(r["unit_id"], r["model_id"]): r for r in metadata}
    assert indexed[withdrawn]["researcher_review_status"] == "Disqualified by researcher"
    register(project, "Current exact researcher-review cohort authority")
    register(source, "Upstream exact model-region cohort manifest")
    aggregation_cohort = prior_path.parents[1] / "inputs/cohort.json"
    assert source.read_bytes() == aggregation_cohort.read_bytes(), "Upstream cohort manifests differ"
    register(aggregation_cohort, "Aggregation cohort identical to upstream SPPR cohort")
    for page, variable in (("index.html", "DB"), ("trends.html", "SERIES_DB")):
        path = root / "interactive_map" / page
        text = path.read_text(encoding="utf-8")
        marker = re.search(r'ppr-project-sha256" content="([0-9a-f]{64})"', text)
        assert marker and marker.group(1) == cohort["project_sha256"], page
        start = text.index("const " + variable + "=") + len("const " + variable + "=")
        payload, _ = json.JSONDecoder().raw_decode(text, start)
        units = payload["network"]["units"] if variable == "DB" else payload["units"]
        rejected_unit = units[withdrawn[0]]
        rejected = next(m for m in rejected_unit["models"] if m["id"] == withdrawn[1])
        assert rejected["researcher_review"]["status"] == "Disqualified by researcher"
        assert rejected["researcher_review"]["sections"] == []
        assert rejected["display_ppr_excluded_group_ids"] == []
        for unit_id, model_id in pairs:
            unit = units[unit_id]
            default = unit["default_model"]
            actual = unit["models"][default]["id"] if isinstance(default, int) else default
            assert actual == model_id, ("Selection changed", unit_id)
            matches = [m for m in unit["models"] if m["id"] == model_id]
            assert len(matches) == 1
            model, central = matches[0], indexed[(unit_id, model_id)]
            review = model["researcher_review"]
            assert review["status"] == "Validated by researcher"
            assert review["report_sha256"] == central["validation_report_sha256"]
            assert review["model_sha256"] == central["reviewed_model_sha256"]
            assert review["researcher_name"] == central["researcher_name"]
            assert review["review_date"] == central["researcher_review_date"]
            summary = json.loads(central["researcher_review_summary"])
            assert review["sections"] == summary["sections"]
            assert model["display_ppr_excluded_group_ids"] == summary["excluded_group_ids"]
            for field, hashfield in (("validation_report_path", "validation_report_sha256"),
                                     ("model_path", "reviewed_model_sha256")):
                artifact = root / central[field]
                assert sha(artifact) == central[hashfield], artifact
                register(artifact, "Current signed-source/canonical identity for included review")
        register(path, "Current published review, selection and calculation payload")
    # Verify the complete upstream dependency ledger, including unchanged
    # contextual overlays. These checks do not add overlays to the cohort.
    for relative, expected in read(experiment / "inputs/source_hashes.json").items():
        expected = expected["sha256"] if isinstance(expected, dict) else expected
        path = root / relative
        assert sha(path) == expected, ("Upstream source changed", relative)
        register(path, "Transitive upstream source identity")
    method_rows = [r for r in records if r["method"] == method]
    assert {(r["unit"], r["model_id"]) for r in method_rows} == pairs
    assert len({(r["unit"], r["group"]) for r in method_rows}) == len(method_rows)
    assert {(r["unit_id"], r["model_id"]) for r in prior["regional"]} == pairs
    expected_counts = {
        "models": len(pairs), "consumer_groups": len(method_rows),
        "catch_groups": prior["aggregate"]["group_count"],
        "region_taxon_records": prior["aggregate"]["region_taxon_count"],
        "taxon_group_allocations": sum(g["positive_taxa"] for g in prior["groups"]),
        "basis": "Expected counts derived from new upstream group records and independently reconstructed aggregation inputs; checked again against direct HTML allocations.",
    }
    assert expected_counts["catch_groups"] == len(prior["groups"])
    assert prior["aggregate"]["region_count"] == len(pairs)
    (study / "inputs/cohort.json").write_bytes(source.read_bytes())
    (study / "inputs/sample_manifest.json").write_text(json.dumps(expected_counts, indent=2), encoding="utf-8")
    register(study / "inputs/cohort.json", "Local byte-identical exact cohort manifest")
    register(study / "inputs/sample_manifest.json", "Manifest-derived count expectations")
    register(Path(__file__), "Cohort, source and count guard implementation")
    return cohort, pairs, expected_counts
