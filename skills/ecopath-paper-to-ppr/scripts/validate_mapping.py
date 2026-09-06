"""Check a mapping against the model and the catch, and measure it by tonnage.

Run this after every editing pass, not once at the end. It exists so the mapping can be
improved against a number instead of a feeling. Two numbers matter and they diverge
sharply: a mapping can leave 44 % of taxa unresolved and still cover 90 % of the catch,
because the unresolved tail is rarities. PPR is a tonnage quantity, so tonnage coverage
is the one to optimise.

Errors (exit 1) are things that would make the downstream PPR wrong:

    a catch taxon missing from the mapping, or a row for a taxon not in the catch
    a group name that is not verbatim in the model's own `groups_df`
    a catch taxon mapped onto Detritus or diet_import
    malformed weights
    a decision whose confidence, evidence and group contradict each other

Warnings do not block, but each one is a place a reader will lose trust.

    python validate_mapping.py LME_047
    python validate_mapping.py LME_047 --min-coverage 90
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapping_io as mio  # noqa: E402

GENERIC = ("best match", "closest group", "most similar", "seems to fit", "best fit",
           "appropriate group", "obvious choice", "n/a", "see above")

TIER_ORDER = ("high", "medium", "low", "unresolved")


def read_members(path: Path) -> dict:
    """`<stem>.members.csv`: the paper's own species-to-group table, if it has one.

    Wanted `printed_name`, `accepted_name`, `group_name`. Both name columns are indexed
    because the mismatches hide in the older nomenclature -- a table printed in 1998 says
    `Formio niger` where the catch record says `Parastromateus niger`, and a mapping can
    contradict a documented member without either name looking wrong on its own.
    """
    if not path.exists():
        return {}
    import csv as _csv
    out = {}
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for r in _csv.DictReader(fh):
            g = (r.get("group_name") or "").strip()
            if not g:
                continue
            for key in ("accepted_name", "printed_name"):
                n = (r.get(key) or "").strip().lower()
                if n:
                    out.setdefault(n, set()).add(g)
    return out


def check(root: Path, unit: str, min_coverage: float) -> int:
    taxa, _years = mio.read_catch(root, unit)
    if not taxa:
        print(f"{unit}: no catch data", file=sys.stderr)
        return 1
    totals = {t: sum(v["by_year"].values()) for t, v in taxa.items()}
    grand = sum(totals.values()) or 1.0

    books = {p.stem: p for p in mio.model_workbooks(root, unit)}
    files = mio.mapping_files(root, unit)
    if not files:
        print(f"{unit}: no mapping files under {mio.mapping_dir(root, unit)}", file=sys.stderr)
        return 1

    worst = 0
    for path in files:
        stem = path.stem
        print(f"\n=== {unit} / {stem}")
        errors, warnings = [], []
        book = books.get(stem)
        if book is None:
            errors.append(f"no model workbook named {stem}.xlsx in PPREstimation/output/top10")
            groups, gtype = {}, {}
        else:
            gl = mio.read_groups(book)
            groups = {g["group_name"] for g in gl}
            gtype = {g["group_name"]: (g.get("group_type") or "") for g in gl}

        rows = mio.read_mapping_csv(path)
        missing_cols = [c for c in mio.FIELDS if c not in (rows[0] if rows else {})]
        if missing_cols:
            errors.append(f"missing columns: {missing_cols}")

        members = read_members(path.parent / f"{stem}.members.csv")
        confirmed_n = confirmed_t = 0
        contradicted = []

        seen = {}
        tier_t = {k: 0.0 for k in TIER_ORDER}
        tier_n = {k: 0 for k in TIER_ORDER}
        composite_t, composite_n = 0.0, 0
        inherited_t, inherited_n = 0.0, 0
        blank = 0
        used_groups = set()

        for i, r in enumerate(rows, start=2):
            t = (r.get("taxon") or "").strip()
            if not t:
                errors.append(f"row {i}: blank taxon")
                continue
            if t in seen:
                errors.append(f"row {i}: `{t}` appears again (first at row {seen[t]})")
                continue
            seen[t] = i
            if t not in taxa:
                errors.append(f"row {i}: `{t}` is not in the catch for {unit}")
                continue

            tonnes = totals[t]
            gcell = (r.get("group") or "").strip()
            conf = (r.get("confidence") or "").strip().lower()
            ev = (r.get("evidence") or "").strip().lower()
            expl = (r.get("explanation") or "").strip()

            if not gcell:
                blank += 1
                continue

            names = mio.parse_groups_cell(gcell)
            unresolved = len(names) == 1 and names[0].lower() == "unresolved"

            if not unresolved:
                unknown = [n for n in names if groups and n not in groups]
                if unknown:
                    errors.append(
                        f"row {i} `{t}`: group(s) absent from {stem} groups_df: {unknown}")
                dead = [n for n in names if gtype.get(n) in ("DET", "Import")]
                if dead:
                    errors.append(
                        f"row {i} `{t}`: mapped onto a non-living compartment {dead}")
                pp = [n for n in names if gtype.get(n) == "PP"]
                if pp and "algae" not in t.lower() and "weed" not in t.lower():
                    warnings.append(
                        f"row {i} `{t}`: mapped onto a primary producer {pp}; only "
                        "harvested algae belong there")
                _w, _basis, err = mio.parse_weights_cell(r.get("weights"), len(names))
                if err:
                    errors.append(f"row {i} `{t}`: {err}")
                used_groups.update(names)

            if conf not in mio.CONFIDENCE:
                errors.append(f"row {i} `{t}`: confidence {conf!r} not one of {mio.CONFIDENCE}")
                conf = "low"
            if ev and ev not in mio.EVIDENCE:
                errors.append(f"row {i} `{t}`: evidence {ev!r} not one of {mio.EVIDENCE}")

            if unresolved and conf != "unresolved":
                errors.append(f"row {i} `{t}`: Unresolved must carry confidence `unresolved`")
            if not unresolved and conf == "unresolved":
                errors.append(f"row {i} `{t}`: confidence `unresolved` but a group is named")
            if len(names) > 1 and ev != "composite_split":
                errors.append(f"row {i} `{t}`: several groups but evidence is {ev!r}, "
                              "expected `composite_split`")
            if unresolved and ev not in ("none", ""):
                warnings.append(f"row {i} `{t}`: Unresolved with evidence {ev!r}")

            if not expl:
                errors.append(f"row {i} `{t}`: no explanation")
            elif len(expl) < 25:
                warnings.append(f"row {i} `{t}`: explanation is {len(expl)} characters")
            elif any(g in expl.lower() for g in GENERIC) and len(expl) < 90:
                warnings.append(f"row {i} `{t}`: explanation is generic — {expl[:60]!r}")

            tier_t[conf] = tier_t.get(conf, 0.0) + tonnes
            tier_n[conf] = tier_n.get(conf, 0) + 1
            if len(names) > 1:
                composite_t += tonnes
                composite_n += 1
            if ev == "inherited_mapping":
                inherited_t += tonnes
                inherited_n += 1

            # The paper's own member list, where one was transcribed, outranks every
            # judgement in this file. A row that contradicts it is an error, not a
            # difference of opinion.
            documented = members.get(t.strip().lower())
            if documented and not unresolved:
                if documented & set(names):
                    confirmed_n += 1
                    confirmed_t += tonnes
                else:
                    contradicted.append((tonnes, t, sorted(documented), names))

        absent = [t for t in taxa if t not in seen]
        if absent:
            miss_t = sum(totals[t] for t in absent)
            errors.append(
                f"{len(absent)} catch taxa have no row ({miss_t:,.0f} t, "
                f"{100 * miss_t / grand:.1f} %): {sorted(absent, key=lambda x: -totals[x])[:6]}")
        if blank:
            errors.append(f"{blank} row(s) have no decision yet")

        resolved_t = sum(tier_t[k] for k in ("high", "medium", "low"))
        cov = 100 * resolved_t / grand

        print(f"  taxa in catch      : {len(taxa)}")
        print(f"  rows in mapping    : {len(rows)}")
        if groups:
            print(f"  model groups used  : {len(used_groups)} of {len(groups)}")
        print("  by confidence      : " + ", ".join(
            f"{k} {tier_n[k]} ({100 * tier_t[k] / grand:.1f} %)" for k in TIER_ORDER))
        print(f"  composite splits   : {composite_n} taxa, "
              f"{100 * composite_t / grand:.1f} % of tonnage")
        if inherited_n:
            print(f"  inherited, unchecked : {inherited_n} taxa, "
                  f"{100 * inherited_t / grand:.1f} % of tonnage still carry evidence "
                  "`inherited_mapping`")
        if members:
            print(f"  against the paper's member list ({len(members)} names):")
            print(f"      confirmed        : {confirmed_n} taxa, "
                  f"{100 * confirmed_t / grand:.1f} % of tonnage")
            print(f"      contradicted     : {len(contradicted)}")
            for tonnes, t, doc, got in sorted(contradicted, reverse=True)[:10]:
                errors.append(f"`{t}` ({tonnes:,.0f} t) is listed under {doc} in the "
                              f"paper's member list but mapped to {got}")
        print(f"  CATCH TONNAGE ON A GROUP : {cov:.1f} %   "
              f"(taxa resolved: {100 * (len(taxa) - tier_n['unresolved']) / len(taxa):.1f} %)")

        if tier_n["unresolved"]:
            unres = sorted(((totals[t], t) for t, i in seen.items()
                            if (rows[i - 2].get("confidence") or "").strip().lower()
                            == "unresolved"), reverse=True)
            print("  largest unresolved :")
            for v, t in unres[:8]:
                print(f"      {v:14,.0f} t  ({100 * v / grand:4.1f} %)  {t}")

        for e in errors:
            print(f"  ERROR   {e}")
        for wmsg in warnings[:25]:
            print(f"  warn    {wmsg}")
        if len(warnings) > 25:
            print(f"  warn    ... and {len(warnings) - 25} more")

        if errors:
            print(f"  VERDICT: FAIL — {len(errors)} error(s) must be fixed")
            worst = max(worst, 1)
        elif cov < min_coverage:
            print(f"  VERDICT: INCOMPLETE — {cov:.1f} % of tonnage mapped, "
                  f"target is {min_coverage:.0f} %. Work the unresolved list above.")
            worst = max(worst, 2)
        else:
            print(f"  VERDICT: PASS — {cov:.1f} % of tonnage mapped, no errors")

    return worst


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("unit")
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--min-coverage", type=float, default=95.0,
                    help="target percentage of catch tonnage on a named group")
    a = ap.parse_args()
    root = a.root.resolve() if a.root else mio.find_root()
    return check(root, a.unit, a.min_coverage)


if __name__ == "__main__":
    raise SystemExit(main())
