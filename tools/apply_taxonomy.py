"""Write a model's group membership into its database JSON, so SPPR carries it downstream.

Stage 2 of `skills/ecopath-paper-to-ppr` records which taxa sit in which functional group.
For a model extracted from a paper that lands in `Taxonomy.xlsx` and reaches the database
JSON through `database_json.py`. The models here came from Ecobase as finished JSONs, with
no eight-file extraction to rebuild from, so the taxonomy has to go into the JSON directly.

`ModelData` reads `taxon_descr` straight off each group dict, and `create_PPRS_excel`
carries it into the `groups_df` sheet, which is what `prepare_mapping.py` prints in the
work order. So one field, written once, is the difference between a mapper reading the
paper's own membership and a mapper inferring it.

    python tools/apply_taxonomy.py data/LME_035/mapping/<stem>.taxonomy.csv --check
    python tools/apply_taxonomy.py data/LME_035/mapping/<stem>.taxonomy.csv --out <dir>

The CSV needs `group_name` and `taxon_descr`; `seq` is optional and only cross-checked.
Every group in the JSON must appear, and every name must match the JSON exactly -- a
mismatch means the taxonomy was written against a different model, and silently skipping
it would leave a group unlabelled with nothing saying so.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "PPREstimation" / "real_models" / "global_cover_jsons"


def load_taxonomy(path: Path) -> dict:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit(f"{path} is empty")
    for col in ("group_name", "taxon_descr"):
        if col not in rows[0]:
            raise SystemExit(f"{path} needs a {col!r} column; has {list(rows[0])}")
    out = {}
    for r in rows:
        name = (r["group_name"] or "").strip()
        if not name:
            continue
        if name in out:
            raise SystemExit(f"{path}: {name!r} appears twice")
        out[name] = (r["taxon_descr"] or "").strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("taxonomy", type=Path, help="<model_stem>.taxonomy.csv")
    ap.add_argument("--model", help="model stem; default is the CSV's own stem")
    ap.add_argument("--json-dir", type=Path, default=JSON_DIR)
    ap.add_argument("--out", type=Path,
                    help="write the patched JSON here instead of in place")
    ap.add_argument("--check", action="store_true",
                    help="report what would change and write nothing")
    a = ap.parse_args()

    stem = a.model or a.taxonomy.name.replace(".taxonomy.csv", "")
    src = a.json_dir / f"{stem}.json"
    if not src.exists():
        raise SystemExit(f"no model JSON at {src}")

    tax = load_taxonomy(a.taxonomy)
    model = json.loads(src.read_text(encoding="utf-8"))
    groups = model.get("group") or []
    if not groups:
        raise SystemExit(f"{src} has no 'group' array")

    names = [str(g.get("group_name", "")).strip() for g in groups]
    unknown = sorted(set(tax) - set(names))
    absent = [n for n in names if n not in tax]
    if unknown:
        raise SystemExit(
            f"{a.taxonomy.name} names {len(unknown)} group(s) the model does not have: "
            f"{unknown[:5]}. The taxonomy belongs to a different model.")
    if absent:
        raise SystemExit(
            f"{len(absent)} of {len(names)} groups have no row in {a.taxonomy.name}: "
            f"{absent[:5]}. Every group needs one, including the ones whose answer is "
            "'not documented'.")

    filled = sum(1 for v in tax.values() if v and v.lower() != "not documented")
    undoc = len(tax) - filled
    before = sum(1 for g in groups if (g.get("taxon_descr") or "").strip())

    print(f"{stem}")
    print(f"  groups                  : {len(names)}")
    print(f"  taxon_descr already set : {before}")
    print(f"  documented in the CSV   : {filled}")
    print(f"  'not documented'        : {undoc}")

    if a.check:
        print("  --check: nothing written")
        return 0

    for g in groups:
        g["taxon_descr"] = tax[str(g.get("group_name", "")).strip()] or None

    dest = (a.out / f"{stem}.json") if a.out else src
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
    else:
        backup = src.with_suffix(".json.pre-taxonomy")
        if not backup.exists():
            shutil.copy2(src, backup)
            print(f"  kept the original at {backup.name}")
    dest.write_text(json.dumps(model, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"  wrote {dest}")
    print("  regenerate the SPPR workbook so groups_df carries it:")
    print(f"    python tools/run_sppr.py --models \"{stem}\" --out <dir> --compare")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
