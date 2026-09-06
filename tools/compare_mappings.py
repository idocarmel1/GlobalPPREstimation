"""Compare two mappings of the same ecosystem and model, side by side.

Written to settle whether combining the extraction and mapping skills helps, hurts or does
nothing. Two agents map the same catch onto the same model from separate checkouts, and the
question is not which report reads better but which mapping covers more tonnage, rests on
more documented evidence, and where the two actually disagree.

Reports, for each side and then jointly:

    catch tonnage on a named group, and the split by confidence tier
    the evidence codes, weighted by tonnage -- documented membership versus inference
    how often the two agree, by taxon count and by tonnage
    the largest-tonnage disagreements, so they can be adjudicated rather than counted

Agreement is on the *set* of groups a taxon is assigned to, not the weights: two mappings
that both apportion `Sciaenidae` across the same three groups agree, even if their weights
came out differently.

    python tools/compare_mappings.py LME_028 "28_646_Guinea_(1998)" --other <root>
    python tools/compare_mappings.py LME_028 "28_646_Guinea_(1998)" \
        --left <root_a> --right <root_b> --labels combined separate
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "ewe-species-to-group-mapper" / "scripts"))
import mapping_io as mio  # noqa: E402

TIERS = ("high", "medium", "low", "unresolved")
# Evidence codes that mean "the source says so", as opposed to "I worked it out".
DOCUMENTED = {"explicit_member", "synonym", "inherited_model"}


def load(root: Path, unit: str, stem: str):
    path = mio.mapping_dir(root, unit) / f"{stem}.csv"
    if not path.exists():
        raise SystemExit(f"no mapping at {path}")
    rows = mio.read_mapping_csv(path)
    return {r["taxon"]: r for r in rows if (r.get("taxon") or "").strip()}


def summarise(name, m, totals, grand):
    tier_t = {k: 0.0 for k in TIERS}
    tier_n = {k: 0 for k in TIERS}
    ev_t, ev_n = {}, {}
    comp_t = comp_n = 0
    blank = 0
    groups_used = set()
    for taxon, r in m.items():
        t = totals.get(taxon, 0.0)
        names = mio.parse_groups_cell(r.get("group"))
        conf = (r.get("confidence") or "").strip().lower() or "(blank)"
        ev = (r.get("evidence") or "").strip().lower() or "(blank)"
        if not names:
            blank += 1
            continue
        tier_t[conf] = tier_t.get(conf, 0.0) + t
        tier_n[conf] = tier_n.get(conf, 0) + 1
        ev_t[ev] = ev_t.get(ev, 0.0) + t
        ev_n[ev] = ev_n.get(ev, 0) + 1
        if len(names) > 1:
            comp_t += t
            comp_n += 1
        if names != ["Unresolved"]:
            groups_used.update(names)

    cov = sum(tier_t[k] for k in ("high", "medium", "low"))
    doc = sum(v for k, v in ev_t.items() if k in DOCUMENTED)
    print(f"\n--- {name}")
    print(f"  rows                     : {len(m)}" + (f"  ({blank} with no decision)" if blank else ""))
    print(f"  CATCH TONNAGE ON A GROUP : {100 * cov / grand:.1f} %")
    print("  by confidence            : " + ", ".join(
        f"{k} {tier_n.get(k, 0)} ({100 * tier_t.get(k, 0) / grand:.1f} %)" for k in TIERS))
    print(f"  documented evidence      : {100 * doc / grand:.1f} % of tonnage "
          f"({sum(n for k, n in ev_n.items() if k in DOCUMENTED)} taxa)")
    print("  evidence codes           :")
    for k in sorted(ev_t, key=lambda k: -ev_t[k]):
        print(f"      {ev_n[k]:4}  {100 * ev_t[k] / grand:5.1f} %  {k}")
    print(f"  composite splits         : {comp_n} taxa, {100 * comp_t / grand:.1f} % of tonnage")
    print(f"  distinct groups used     : {len(groups_used)}")
    return {"coverage": 100 * cov / grand, "documented": 100 * doc / grand,
            "groups": groups_used}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("unit")
    ap.add_argument("stem", help="model stem, e.g. 28_646_Guinea_(1998)")
    ap.add_argument("--left", type=Path, default=ROOT)
    ap.add_argument("--right", type=Path, help="the other checkout")
    ap.add_argument("--other", type=Path, help="alias for --right")
    ap.add_argument("--labels", nargs=2, default=["left", "right"])
    ap.add_argument("--top", type=int, default=15, help="disagreements to list")
    a = ap.parse_args()

    right = a.right or a.other
    if right is None:
        raise SystemExit("pass --right (or --other) with the second checkout")

    taxa, _years = mio.read_catch(ROOT, a.unit)
    if not taxa:
        raise SystemExit(f"no catch for {a.unit}")
    totals = {t: sum(v["by_year"].values()) for t, v in taxa.items()}
    grand = sum(totals.values()) or 1.0

    left_m = load(a.left.resolve(), a.unit, a.stem)
    right_m = load(right.resolve(), a.unit, a.stem)

    print(f"=== {a.unit} / {a.stem}")
    print(f"  {len(taxa)} catch taxa, {grand:,.0f} tonnes over the whole period")
    ls = summarise(a.labels[0], left_m, totals, grand)
    rs = summarise(a.labels[1], right_m, totals, grand)

    shared = sorted(set(left_m) & set(right_m), key=lambda t: -totals.get(t, 0.0))
    agree_n = agree_t = 0
    diffs = []
    for t in shared:
        lg = set(mio.parse_groups_cell(left_m[t].get("group")))
        rg = set(mio.parse_groups_cell(right_m[t].get("group")))
        if lg == rg:
            agree_n += 1
            agree_t += totals.get(t, 0.0)
        else:
            diffs.append((totals.get(t, 0.0), t, sorted(lg), sorted(rg)))

    print(f"\n--- agreement")
    print(f"  taxa in both             : {len(shared)}")
    print(f"  identical group set      : {agree_n} ({100 * agree_n / len(shared):.1f} % of taxa, "
          f"{100 * agree_t / grand:.1f} % of tonnage)")
    only_l = sorted(ls["groups"] - rs["groups"])
    only_r = sorted(rs["groups"] - ls["groups"])
    if only_l:
        print(f"  groups only {a.labels[0]} used : {only_l}")
    if only_r:
        print(f"  groups only {a.labels[1]} used: {only_r}")

    print(f"\n--- largest disagreements")
    print(f"  {'tonnes':>14}  {'%':>5}  taxon")
    for tonnes, t, lg, rg in sorted(diffs, reverse=True)[:a.top]:
        print(f"  {tonnes:14,.0f}  {100 * tonnes / grand:5.1f}  {t}")
        print(f"      {a.labels[0]:>10}: {' | '.join(lg) or '(none)'}")
        print(f"      {a.labels[1]:>10}: {' | '.join(rg) or '(none)'}")

    print(f"\n--- verdict inputs")
    print(f"  coverage   {a.labels[0]} {ls['coverage']:.1f} %   "
          f"{a.labels[1]} {rs['coverage']:.1f} %   "
          f"difference {ls['coverage'] - rs['coverage']:+.1f} pp")
    print(f"  documented {a.labels[0]} {ls['documented']:.1f} %   "
          f"{a.labels[1]} {rs['documented']:.1f} %   "
          f"difference {ls['documented'] - rs['documented']:+.1f} pp")
    print("  Coverage and documented-evidence share are the two numbers that matter.")
    print("  Where they disagree, read the disagreements above rather than the totals:")
    print("  a mapping can raise coverage by widening candidate sets, which is not a gain.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
