"""massbalance_check.py — check an extracted model against the Ecopath equations.

Run:  python massbalance_check.py <model-dir>
      python massbalance_check.py <model-dir> --ee-tol 0.05 --quiet-ok

`validate.py` checks that the files are structurally sound. This checks that the
numbers in them are physically coherent, using the two Ecopath master equations:

  production:  B(P/B)EE  =  Y + SUM_j B_j (Q/B)_j DC_ji   (+ E + BA)
  energy:      Q         =  P + R + GS*Q

So EE can be recomputed from the diet matrix, the biomasses and the catches, and
compared with what the paper printed. Published models are balanced, so a group
that comes out consuming more than it produces is usually a mis-parsed number —
a Q/B read from the wrong column, a catch left in absolute tonnes, a diet
proportion in the wrong predator's column.

It is a diagnostic, not a verdict. Older models legitimately include migration
and biomass accumulation terms that this ignores, and some papers report
pre-balance parameters. Investigate what it flags against the page; never adjust
a number to make a check pass.

Exit code 1 if any ERROR, else 0.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ecopath's own default for unassimilated consumption, applied to blanks on
# import — so the respiration check must use it too, or it would test a model
# different from the one EwE will actually build.
EWE_DEFAULT_GS = 0.2

PQ_LO, PQ_HI = 0.02, 0.5


def read_rows(path: Path) -> list[list[str]]:
    return [
        ln.split(",")
        for ln in path.read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")
        if ln != ""
    ]


def f(s: str) -> float | None:
    s = (s or "").strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("model_dir")
    ap.add_argument("--ee-tol", type=float, default=0.05,
                    help="allowed absolute difference between printed and recomputed EE")
    ap.add_argument("--quiet-ok", action="store_true",
                    help="suppress the per-group table, print only findings")
    args = ap.parse_args()

    d = Path(args.model_dir)
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    basic = read_rows(d / "Basic_input.csv")
    diet = read_rows(d / "Diet_composition.csv")

    # ---- basic input ----
    G: dict[int, dict] = {}
    for r in basic[1:]:
        n = int(r[0])
        G[n] = {
            "name": r[1],
            "B": f(r[3]),
            "Z": f(r[4]),
            "PB": f(r[5]),
            "QB": f(r[6]),
            "EE": f(r[7]),
            "PQ": f(r[9]),
            "GS": f(r[10]),
        }

    # ---- biomass accumulation ----
    # EE = (Y + BA + predation) / (B.P/B), so a model with BA terms will show a
    # recomputed EE that differs from the printed one by BA/(B.P/B) unless BA is
    # carried through here.  Absolute BA wins over the rate form when both are
    # present; the rate is multiplied by B.
    BA: dict[int, float] = {}
    ba_path = d / "Biomass_accumulation.csv"
    if ba_path.exists():
        for r in read_rows(ba_path)[1:]:
            n = int(r[0])
            absolute, rate = f(r[2]), f(r[3]) if len(r) > 3 else None
            if absolute is not None:
                BA[n] = absolute
            elif rate is not None and G.get(n, {}).get("B") is not None:
                BA[n] = rate * G[n]["B"]
            elif rate is not None:
                warnings.append(
                    f"group {n}: a BA rate of {rate}/year is given but no biomass, "
                    "so it cannot be included in the mass-balance check"
                )

    # ---- catches ----
    Y: dict[int, float] = {n: 0.0 for n in G}
    for name in ("Landings.csv", "Discards.csv"):
        p = d / name
        if not p.exists():
            continue
        for r in read_rows(p)[1:]:
            n = int(r[0])
            v = f(r[-1])
            if v:
                Y[n] = Y.get(n, 0.0) + v

    # ---- diet matrix ----
    header = diet[0]
    consumers = [int(c) for c in header[2:] if c.strip().isdigit()]
    DC: dict[int, dict[int, float]] = {c: {} for c in consumers}
    for r in diet[1:]:
        if r[1] in ("Import", "Sum", "(1 - Sum)"):
            continue
        prey = int(r[0])
        for j, c in enumerate(consumers):
            v = f(r[2 + j]) if len(r) > 2 + j else None
            if v:
                DC[c][prey] = v

    # ---- consumption ----
    Q: dict[int, float] = {}
    for c in consumers:
        g = G.get(c)
        if g and g["B"] is not None and g["QB"] is not None:
            Q[c] = g["B"] * g["QB"]

    # a consumer with a Q/B but no diet column eats without anything being eaten:
    # its consumption vanishes from every prey's budget and the model is silently
    # unbalanced, with no single number looking wrong.
    for n, g in G.items():
        if g["QB"] and g["QB"] > 0 and n not in consumers:
            errors.append(
                f"group {n} ({g['name']}) has Q/B={g['QB']} but no diet column — "
                "its consumption is missing from every prey's budget"
            )
        elif n in consumers and not DC.get(n):
            warnings.append(
                f"group {n} ({g['name']}) has a diet column but no diet entries"
            )

    missing_q = [
        c for c in consumers if c not in Q and DC.get(c)
    ]
    if missing_q:
        notes.append(
            f"{len(missing_q)} consumer(s) lack B or Q/B, so predation on their prey "
            f"is under-counted and the EE check below is a lower bound: "
            + ", ".join(f"{c} ({G[c]['name']})" for c in missing_q[:6])
        )

    # ---- detritus groups: structurally different, so exempt from several checks ----
    detritus: set[int] = set()
    fate_rows = read_rows(d / "Detritus_fate.csv") if (d / "Detritus_fate.csv").exists() else []
    if fate_rows:
        pool_names = [c.strip() for c in fate_rows[0][2:-2]]
        by_name = {g["name"].strip(): n for n, g in G.items()}
        for nm in pool_names:
            if nm in by_name:
                detritus.add(by_name[nm])
            else:
                warnings.append(
                    f"Detritus_fate column {nm!r} does not match any group name — "
                    "detritus pools must also be groups"
                )
    # fall back on structure: no production and no consumption rate
    detritus |= {n for n, g in G.items() if g["PB"] is None and g["QB"] is None}

    # ---- per-group checks ----
    rows = []
    ee_used: dict[int, float] = {}
    for n, g in sorted(G.items()):
        pred = sum(Q.get(c, 0.0) * DC.get(c, {}).get(n, 0.0) for c in consumers)
        prod = g["B"] * g["PB"] if (g["B"] is not None and g["PB"] is not None) else None
        ba = BA.get(n, 0.0)
        ee_calc = (Y.get(n, 0.0) + ba + pred) / prod if prod else None

        if ee_calc is not None and ee_calc > 1.0:
            errors.append(
                f"group {n} ({g['name']}): recomputed EE = {ee_calc:.3f} > 1 — "
                f"consumption+catch+BA ({Y.get(n, 0.0) + ba + pred:.4g}) exceeds "
                f"production ({prod:.4g})"
            )
        if ee_calc is not None and g["EE"] is not None:
            if abs(ee_calc - g["EE"]) > args.ee_tol:
                hint = ""
                if not ba and prod:
                    # how much BA would be needed to close this gap?  If it is a
                    # plausible fraction of production, the paper may report one.
                    need = (g["EE"] - ee_calc) * prod
                    if abs(need) < abs(prod):
                        hint = (
                            f" — a BA of {need:+.4g} t/km2/year "
                            f"({need / prod:+.2f} of production) would close this; "
                            "check whether the paper reports biomass accumulation"
                        )
                warnings.append(
                    f"group {n} ({g['name']}): printed EE {g['EE']} vs recomputed "
                    f"{ee_calc:.3f} (diff {abs(ee_calc - g['EE']):.3f}){hint}"
                )

        if ee_calc is not None:
            ee_used[n] = ee_calc
        if g["EE"] is not None:
            ee_used[n] = g["EE"]

        if n in detritus:
            rows.append((n, g["name"], g["B"], g["PB"], g["QB"], g["EE"], None, None,
                         Y.get(n, 0.0)))
            continue

        # gross efficiency and respiration
        pq = g["PQ"]
        if pq is None and g["PB"] and g["QB"]:
            pq = g["PB"] / g["QB"]
        if pq is not None:
            gs = g["GS"] if g["GS"] is not None else EWE_DEFAULT_GS
            if pq >= 1 - gs:
                errors.append(
                    f"group {n} ({g['name']}): P/Q = {pq:.3f} with GS = {gs} implies "
                    f"non-positive respiration (needs P/Q < {1 - gs:.2f})"
                )
            elif not (PQ_LO <= pq <= PQ_HI):
                warnings.append(
                    f"group {n} ({g['name']}): P/Q = {pq:.3f} outside the usual "
                    f"{PQ_LO}-{PQ_HI} range — check the P/B and Q/B columns"
                )

        # solvability: Ecopath needs three of B, P/B, Q/B, EE
        known = sum(
            1 for k in ("B", "PB", "QB", "EE") if g[k] is not None
        )
        if known < 3:
            have = [k for k in ("B", "PB", "QB", "EE") if g[k] is not None]
            warnings.append(
                f"group {n} ({g['name']}): only {known} of B/P-B/Q-B/EE given "
                f"({', '.join(have) or 'none'}) — Ecopath needs three. Sweep the "
                "prose for the missing one before accepting this."
            )
        elif known == 4:
            notes.append(
                f"group {n} ({g['name']}): all four of B/P-B/Q-B/EE given — one is "
                "probably an Ecopath estimate; record which in the report"
            )

        rows.append(
            (n, g["name"], g["B"], g["PB"], g["QB"], g["EE"], ee_calc, pq, Y.get(n, 0.0))
        )

    # ---- detritus pools ----
    if fate_rows and detritus:
        inflow = 0.0
        for n, g in G.items():
            if n in detritus:
                continue
            if g["B"] is not None and g["PB"] is not None:
                ee = ee_used.get(n)
                if ee is not None and ee <= 1:
                    inflow += g["B"] * g["PB"] * (1 - ee)   # other mortality
            if n in Q:
                gs = g["GS"] if g["GS"] is not None else EWE_DEFAULT_GS
                inflow += Q[n] * gs                        # unassimilated food
        for r in read_rows(d / "Discards.csv")[1:] if (d / "Discards.csv").exists() else []:
            v = f(r[-1])
            if v:
                inflow += v                                # discarded catch
        outflow = sum(
            Q.get(c, 0.0) * DC.get(c, {}).get(n, 0.0)
            for c in consumers
            for n in detritus
        )
        if inflow > 0:
            notes.append(
                f"detritus pools ({len(detritus)}): inflow ~{inflow:.4g}, consumption "
                f"~{outflow:.4g} t/km2/yr, implied EE ~{outflow / inflow:.3f} "
                "(indicative — export not separated, and it uses recomputed EE where "
                "the paper gave none)"
            )
            if outflow > inflow:
                errors.append(
                    f"detritus consumption ({outflow:.4g}) exceeds detritus inflow "
                    f"({inflow:.4g}) — the pools cannot balance as extracted"
                )

    # ---- output ----
    if not args.quiet_ok:
        print(
            f"{'#':>3} {'group':<28}{'B':>10}{'P/B':>9}{'Q/B':>9}"
            f"{'EE':>8}{'EE calc':>9}{'P/Q':>7}{'catch':>9}"
        )
        for n, name, B, PB, QB, EE, eec, pq, y in rows:
            fmt = lambda v, w, p=4: (f"{v:>{w}.{p}g}" if v is not None else " " * (w - 1) + "-")
            print(
                f"{n:>3} {name[:27]:<28}{fmt(B,10)}{fmt(PB,9)}{fmt(QB,9)}"
                f"{fmt(EE,8)}{fmt(eec,9,3)}{fmt(pq,7,3)}{fmt(y or None,9)}"
            )
        print()

    for m in notes:
        print(f"NOTE  {m}")
    for m in warnings:
        print(f"WARN  {m}")
    for m in errors:
        print(f"ERROR {m}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s), {len(notes)} note(s)")
    if errors:
        print(
            "Check each error against a rendered image of the source page before "
            "changing anything. Do not adjust numbers to make this pass."
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
