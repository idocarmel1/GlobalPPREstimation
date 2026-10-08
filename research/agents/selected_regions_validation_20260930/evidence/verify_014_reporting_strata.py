"""Read-only independent reproduction of the Falkland hake donor comparison."""
from collections import defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TARGET = "Merluccius"
DONORS = {"Merluccius hubbsi", "Merluccius australis"}
DIMENSIONS = ["fishing_entity", "fishing_sector", "catch_type", "reporting_status",
              "gear_type", "end_use_type", "year"]


def run():
    evidence_path = ROOT / "regions/LME_014/validation_reports/PAT2024_FalklandShelf_2020_native/independent_review/hake_reporting_population_comparison.json"
    evidence_hash = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    expected = json.loads(evidence_path.read_text(encoding="utf-8"))
    raw = ROOT / "regions/LME_014/raw/LME_014-catch.zip"
    raw_hash = hashlib.sha256(raw.read_bytes()).hexdigest()
    assert raw_hash == expected["sha256"]
    selected = []
    member = "SAU LME 14 v50-1.csv"
    with zipfile.ZipFile(raw) as archive:
        member_hash = hashlib.sha256(archive.read(member)).hexdigest()
        with archive.open(member) as stream:
            reader = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig"))
            for row in reader:
                if row["scientific_name"] in DONORS | {TARGET} and 1950 <= int(row["year"]) <= 2019:
                    row["tonnes"] = float(row["tonnes"])
                    selected.append(row)
    taxa_totals = {taxon: math.fsum(r["tonnes"] for r in selected if r["scientific_name"] == taxon)
                   for taxon in sorted(DONORS | {TARGET})}
    for taxon, total in taxa_totals.items():
        assert math.isclose(total, expected["totals"][taxon], rel_tol=1e-12)
    donor_total = math.fsum(taxa_totals[t] for t in DONORS)
    for taxon in DONORS:
        assert math.isclose(taxa_totals[taxon] / donor_total, expected["donor_species_weights"][taxon], rel_tol=1e-12)
    groups = {"target": [r for r in selected if r["scientific_name"] == TARGET],
              "donor": [r for r in selected if r["scientific_name"] in DONORS]}
    output = {"raw_zip_sha256": raw_hash, "csv_member": member, "csv_sha256": member_hash,
              "regional_evidence_sha256": evidence_hash,
              "selection": "Exact three scientific-name labels; 1950–2019 inclusive; all catch types, reporting strata and sectors; no positive-tonnage filter.",
              "taxon_totals_t": taxa_totals, "record_counts": {k: len(v) for k, v in groups.items()},
              "dimensions": {}}
    for dim in DIMENSIONS:
        shares = {}
        for role, rows in groups.items():
            parts = defaultdict(list)
            for row in rows:
                parts[row[dim]].append(row["tonnes"])
            total = math.fsum(row["tonnes"] for row in rows)
            totals = {key: math.fsum(values) for key, values in parts.items()}
            shares[role] = {key: value / total for key, value in totals.items()}
            expected_key = "target_Merluccius_tonnes" if role == "target" else "combined_identified_donor_tonnes"
            reference = expected["distributions"][dim]
            assert set(totals) == set(reference[expected_key]), (dim, role)
            for key, value in totals.items():
                assert math.isclose(value, reference[expected_key][key], rel_tol=1e-12, abs_tol=1e-10), (dim, role, key)
                assert math.isclose(shares[role][key], reference[f"{role}_shares"][key], abs_tol=1e-12)
        tv = math.fsum(abs(shares["target"].get(k, 0) - shares["donor"].get(k, 0))
                       for k in shares["target"].keys() | shares["donor"].keys()) / 2
        assert math.isclose(tv, expected["distributions"][dim]["total_variation_distance"], abs_tol=1e-12)
        output["dimensions"][dim] = {"total_variation_distance": tv, "all_totals_and_shares_match": True}
    assert hashlib.sha256(evidence_path.read_bytes()).hexdigest() == evidence_hash
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == raw_hash
    output["interpretation"] = "Substantial donor/target reporting mismatch supports Low allocation confidence; it does not identify the residual genus mixture or justify replacing the accepted numeric split."
    output["passed"] = True
    (HERE / "verification/LME_014_independent_reporting_strata.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output), flush=True)


if __name__ == "__main__":
    run()
