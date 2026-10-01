"""Independent coordinator reproduction of two consequential reporting mismatches."""
from pathlib import Path
import hashlib
import json
import math
import zipfile

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "regions/LME_032/validation_reports/32_1_Arabian_Sea_off_Karnataka_(2000)/mapping"
TARGETS = {
    "Siluriformes": {"Ariidae", "Netuma thalassina", "Plotosidae", "Plotosus lineatus"},
    "Pleuronectiformes": {"Soleidae", "Psettodes erumei", "Bothus pantherinus", "Bothidae"},
}
DIMENSIONS = ["fishing_entity", "fishing_sector", "gear_type", "reporting_status", "catch_type", "decade", "year"]


def run():
    raw = ROOT / "regions/LME_032/raw/LME_032-catch.zip"
    evidence = json.loads((BASE / "w5_reporting_applicability.json").read_text(encoding="utf-8"))
    fingerprint = hashlib.sha256(raw.read_bytes()).hexdigest()
    assert fingerprint == evidence["raw_sha256"]
    labels = set(TARGETS).union(*TARGETS.values())
    selected = []
    member = "SAU LME 32 v50-1.csv"
    with zipfile.ZipFile(raw) as archive, archive.open(member) as stream:
        cols = ["scientific_name", "tonnes", *[d for d in DIMENSIONS if d != "decade"]]
        for chunk in pd.read_csv(stream, usecols=cols, chunksize=200000, encoding="utf-8-sig", keep_default_na=False):
            chunk = chunk.loc[chunk.scientific_name.isin(labels) & chunk.year.between(1950, 2019)].copy()
            if not chunk.empty:
                selected.append(chunk)
    frame = pd.concat(selected, ignore_index=True)
    frame["decade"] = frame.year // 10 * 10
    output = {"raw_zip_sha256": fingerprint, "member": member,
              "scope": "Independent raw-data reproduction; reporting mismatch does not reveal residual species composition.",
              "items": []}
    for target, donors in TARGETS.items():
        expected = next(i for i in evidence["items"] if i["taxon"] == target)
        groups = {"target": frame.loc[frame.scientific_name == target],
                  "donor": frame.loc[frame.scientific_name.isin(donors)]}
        totals = {role: math.fsum(part.tonnes) for role, part in groups.items()}
        record = {"taxon": target, "donors": sorted(donors), "totals_t": totals,
                  "record_counts": {role: len(part) for role, part in groups.items()}, "dimensions": {}}
        for role in groups:
            assert math.isclose(totals[role], expected[f"{role}_total_catch_t"], rel_tol=1e-12)
            assert len(groups[role]) == expected["original_record_counts"][role]
        for dim in DIMENSIONS:
            shares = {role: {str(key): value / totals[role] for key, value in part.groupby(dim, dropna=False).tonnes.sum().items()}
                      for role, part in groups.items()}
            target_shares, donor_shares = shares["target"], shares["donor"]
            tv = math.fsum(abs(target_shares.get(k, 0) - donor_shares.get(k, 0))
                           for k in target_shares.keys() | donor_shares.keys()) / 2
            assert math.isclose(tv, expected["dimensions"][dim]["total_variation"], abs_tol=1e-12)
            for role in groups:
                observed = shares[role]
                retained = expected["dimensions"][dim][f"{role}_distribution"]
                assert set(observed) == set(retained)
                assert all(math.isclose(observed[k], retained[k], abs_tol=1e-12) for k in observed)
            record["dimensions"][dim] = {"total_variation": tv, "all_distribution_values_match": True}
        output["items"].append(record)
    output["passed"] = True
    destination = HERE / "verification/LME_032_independent_reporting_strata.json"
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output), flush=True)


if __name__ == "__main__":
    run()
