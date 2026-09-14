"""Build one workbook per Ecopath model per ecosystem.

There is no such thing as "the PPR of an LME". There is the PPR implied by a particular
Ecopath model of it, under a particular method. An ecosystem with two published models has
two answers, and they are not averageable. So each model gets its own workbook and every
column inside it belongs to that one model -- no `EwE_Ecobase_412_GulfOfThailande_1963 ::
EwE_TE_noEE` headers, just `EwE_TE_noEE`.

    data/<unit>/models/<model_stem>.xlsx        the workbook
    data/<unit>/mapping/<model_stem>.resolved.csv   the weights actually used, for audit

Sheets:

    Summary          identity, coverage, and per-year catch / PPR / PPR-over-NPP
    Catch            taxon x year, tonnes
    Taxon-Group Map  the mapping, with confidence colouring and the explanations
    Final mappings   exact numeric taxon/group weights, evidence, and model identity
    SPPR             taxon x method -- the simple per-taxon value and the model's, together
    PPR by method    method x year, summed over taxa
    PPR by taxon     taxon x method for one year, chosen from a dropdown
    Model groups     the model's own groups_df and per-group SPPR
    NPP              satellite estimates

The mapping comes from `data/<unit>/mapping/<model_stem>.csv`, produced by
`skills/claude/ewe-species-to-group-mapper`. A taxon there may name one group, several groups
(apportioned), or `Unresolved`.

Two rules the arithmetic depends on:

* A group named in a mapping that is absent from the model's own `groups_df` is a hard
  error. It means mapping and model disagree, and every number derived from that row
  would be fiction.
* Composite weights are constant over time, so each taxon keeps a single SPPR per method
  and `PPR = catch(taxon, year) x SPPR(taxon, method)` stays exact.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import tempfile
import textwrap
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "claude" / "ewe-species-to-group-mapper" / "scripts"))
import mapping_io as mio  # noqa: E402
from ppr_scopes import SCOPES, read_scopes, read_health, method_health_flags, add_recycling_sheet
from npp_data import load_npp, npp_for_year

TRANSFER_EFFICIENCY = 0.1
WET_WEIGHT_TO_CARBON = 9.0

# Every quantity is rounded once, here, and the rounded value is what every sheet uses.
# Rounding per sheet instead would leave `PPR by method` and `PPR by taxon` disagreeing in
# the ninth digit -- harmless arithmetically, but it means a reader who cross-checks one
# against the other finds a discrepancy and has no way to tell it from a real one.
CATCH_DP = 3
SPPR_DP = 6

HEAD = Font(bold=True)
TITLE = Font(bold=True, size=14)
WHITE_ON_BLUE = Font(bold=True, color="FFFFFF")
BLUE = PatternFill("solid", fgColor="1F4E79")
CONF_FILL = {
    "high": PatternFill("solid", fgColor="C6EFCE"),
    "medium": PatternFill("solid", fgColor="FFEB9C"),
    "low": PatternFill("solid", fgColor="FFC49C"),
    "unresolved": PatternFill("solid", fgColor="FFC7CE"),
}

# Preference order for the one method the Summary sheet leads with. `new_TE_EEfix` is
# the primary solver with EE=0 groups repaired; the rest are fallbacks for models where
# it did not converge.
HEADLINE = ["new_TE_EEfix", "new_TE_noEEfix", "SPPR_2015", "Ulanowicz_TE",
            "SPPR_1995_TE0.1", "SPPR_1986"]

# A network method may legitimately sit well above or below the trophic-chain estimate --
# across the healthy models here the ratio runs 0.1x to 4.6x. It may not sit 6,000x above
# it: `sym_GE_asDC` on the Bay of Bengal model returns 2.1e13 tonnes, which after the usual
# 9:1 wet-weight-to-carbon conversion is some thousands of times that sea's entire annual
# primary production. That is a near-singular solve, not a modelling difference. The
# threshold is a plausibility flag, not a claim about which method is right.
IMPLAUSIBLE_RATIO = 25.0


def simple_sppr(level):
    """The trophic-chain SPPR, rounded once so every sheet quotes the same number."""
    if level is None:
        return None
    return round((1.0 / TRANSFER_EFFICIENCY) ** (level - 1.0), SPPR_DP)


def show_weights(w, dp=3):
    """Round weights for display so they still sum to 1 exactly.

    Rounding each independently leaves a set like 0.360/0.240/0.400 reading 0.999, which
    a reader checks, finds wrong, and cannot distinguish from a real normalisation bug.
    Largest-remainder: round every weight down, then hand the leftover units to whichever
    had the biggest fractional part.
    """
    if not w:
        return ""
    scale = 10 ** dp
    scaled = [x * scale for x in w]
    floors = [int(x) for x in scaled]
    short = round(scale - sum(floors))
    for i in sorted(range(len(w)), key=lambda i: -(scaled[i] - floors[i]))[:max(0, short)]:
        floors[i] += 1
    return " | ".join(f"{f / scale:.{dp}f}" for f in floors)


def num(v):
    """A finite float, or None. sppr_all uses NaN for a method that did not resolve."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return None if math.isnan(v) or math.isinf(v) else float(v)


# --------------------------------------------------------------------------- weights

def resolve_weights(names, basis, explicit, groups_by_name, solo_catch):
    """Return (weights, basis actually used).

    `catch_composition` weights a candidate group by the catch that taxa assigned to it
    *alone* already carry. Using only single-group assignments keeps the estimate from
    depending on other composites, which would make the result order-dependent.

    Falls back through model catch, model biomass and equal shares, so a candidate set
    that no identified taxon has landed on still gets a defensible split. The basis
    actually used is returned and recorded, because "we fell back to equal" is
    information the reader needs.
    """
    if explicit is not None:
        return explicit, "explicit"
    n = len(names)
    if n == 1:
        return [1.0], "single"

    def by(fn, label):
        vals = [max(0.0, fn(g) or 0.0) for g in names]
        total = sum(vals)
        return ([v / total for v in vals], label) if total > 0 else (None, None)

    chain = []
    if basis == "catch_composition":
        chain = ["catch_composition", "model_catch", "model_biomass", "equal"]
    elif basis == "model_catch":
        chain = ["model_catch", "model_biomass", "equal"]
    elif basis == "model_biomass":
        chain = ["model_biomass", "model_catch", "equal"]
    else:
        chain = ["equal"]

    for step in chain:
        if step == "catch_composition":
            w, lab = by(lambda g: solo_catch.get(g, 0.0), "catch_composition")
        elif step == "model_catch":
            w, lab = by(lambda g: num(groups_by_name.get(g, {}).get("catch")), "model_catch")
        elif step == "model_biomass":
            w, lab = by(lambda g: num(groups_by_name.get(g, {}).get("biomass")), "model_biomass")
        else:
            return [1.0 / n] * n, "equal"
        if w:
            return w, lab
    return [1.0 / n] * n, "equal"


def build_taxon_sppr(rows, methods, sppr_by_group, groups_by_name, totals):
    """taxon -> {names, weights, basis, confidence, evidence, explanation, sppr[]}.

    A method is None for a taxon when any contributing group is None for that method:
    a partial weighted sum would silently understate the taxon and look like a real number.
    """
    solo = {}
    for r in rows:
        names = mio.parse_groups_cell(r.get("group"))
        if len(names) == 1 and names[0].lower() != "unresolved":
            solo[names[0]] = solo.get(names[0], 0.0) + totals.get(r["taxon"], 0.0)

    out = {}
    for r in rows:
        taxon = r["taxon"]
        names = mio.parse_groups_cell(r.get("group"))
        conf = (r.get("confidence") or "").strip().lower()
        rec = {
            "names": names,
            "weights": [],
            "basis": "",
            "confidence": conf,
            "evidence": (r.get("evidence") or "").strip(),
            "explanation": (r.get("explanation") or "").strip(),
            "sppr": [None] * len(methods),
        }
        if not names or (len(names) == 1 and names[0].lower() == "unresolved"):
            rec["names"] = ["Unresolved"]
            out[taxon] = rec
            continue
        explicit, basis, err = mio.parse_weights_cell(r.get("weights"), len(names))
        if err:
            raise SystemExit(f"{taxon}: {err}")
        w, used = resolve_weights(names, basis, explicit, groups_by_name, solo)
        rec["weights"], rec["basis"] = w, used
        vals = []
        for i in range(len(methods)):
            parts = [num(sppr_by_group.get(g, [None] * len(methods))[i]) for g in names]
            vals.append(None if any(p is None for p in parts)
                        else round(sum(wi * p for wi, p in zip(w, parts)), SPPR_DP))
        rec["sppr"] = vals
        out[taxon] = rec
    return out


def final_mapping_rows(unit, stem, taxa, resolved, totals):
    """One numeric row per assignment, using the exact weights used for SPPR."""
    out = []
    for taxon in sorted(taxa, key=lambda t: -totals[t]):
        e, rec = taxa[taxon], resolved[taxon]
        for i, group in enumerate(rec['names']):
            out.append({
                'unit_id': unit, 'model_id': stem, 'taxon': taxon,
                'common_name': e['common_name'], 'SAU functional group': e['functional_group'],
                'SAU commercial group': e['commercial_group'], 'group': group,
                'weight': rec['weights'][i] if rec['weights'] else None,
                'weight_basis': rec['basis'], 'confidence': rec['confidence'],
                'evidence': rec['evidence'], 'explanation': rec['explanation'],
                'catch_tonnes': round(totals[taxon], 3),
            })
    return out


# ---------------------------------------------------------------------------- sheets

def header_row(ws, values, row=None):
    ws.append(values)
    r = row or ws.max_row
    for c in ws[r]:
        c.font = WHITE_ON_BLUE
        c.fill = BLUE
        c.alignment = Alignment(vertical="center")
    return r


def widths(ws, spec):
    for i, w in enumerate(spec, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def sheet_final_mappings(wb, records):
    ws = wb.create_sheet('Final mappings')
    if not records:
        ws.append(['No final mappings are available for this ecosystem.'])
        ws.append(['Models without a recorded mapping are not assigned invented taxon groups or weights.'])
        widths(ws, [26])
        ws.freeze_panes = "A2"
        ws.sheet_view.showGridLines = False
        return
    ws.append(['Final taxon-to-group mappings, identified separately for each Ecopath model'])
    ws['A1'].font = Font(bold=True, size=14)
    ws.append(['One row per taxon/group assignment; numeric weights are the exact values used to calculate SPPR.'])
    ws.append(['Unresolved taxa retain a row with a blank weight. Catch tonnes repeat across a taxon\'s assignments; do not sum these rows.'])
    header = list(records[0])
    ws.append(header)
    for c in ws[4]:
        c.font = HEAD
    for rec in records:
        ws.append([rec[k] for k in header])
        ws.cell(ws.max_row, header.index('weight') + 1).number_format = '0.000000000000000'
        ws.cell(ws.max_row, header.index('confidence') + 1).fill = CONF_FILL.get(rec['confidence'], CONF_FILL['low'])
    ws.freeze_panes = 'D5'
    ws.sheet_view.showGridLines = False
    for i, width in enumerate([14, 46, 30, 23, 27, 24, 35, 23, 22, 14, 24, 95, 18], 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    for cells in ws.iter_rows(min_row=5):
        lines = 1
        for cell in cells:
            cell.alignment = Alignment(vertical='top')
        for index, width in ((1, 44), (2, 28), (6, 33), (11, 93)):
            cells[index].alignment = Alignment(wrap_text=True, vertical='top')
            lines = max(lines, sum(max(1, len(textwrap.wrap(part, width=width)))
                                   for part in str(cells[index].value or '').split('\n')))
        ws.row_dimensions[cells[0].row].height = max(18, lines * 15 + 6)
    ws.auto_filter.ref = f'A4:M{ws.max_row}'


def sheet_catch(wb, order, taxa, years):
    ws = wb.create_sheet("Catch")
    header_row(ws, ["taxon", "common_name", "functional_group", "commercial_group"]
               + list(years))
    for t in order:
        e = taxa[t]
        ws.append([t, e["common_name"], e["functional_group"], e["commercial_group"]]
                  + [e["by_year"].get(y, 0.0) for y in years])
    widths(ws, [34, 26, 30, 22] + [12] * len(years))
    ws.freeze_panes = "E2"
    ws.sheet_view.showGridLines = False
    return ws


def sheet_map(wb, order, taxa, resolved, totals, grand):
    ws = wb.create_sheet("Taxon-Group Map")
    ws.append(["Which Ecopath group each catch taxon belongs to, and on what evidence."])
    ws["A1"].font = TITLE
    ws.append(["Several groups separated by | means the taxon spans them and its catch is "
               "apportioned; the weights used are in the next two columns."])
    ws.append([])
    header_row(ws, ["taxon", "common_name", "SAU functional group", "SAU commercial group",
                    "Ecopath group", "weights", "weight basis", "confidence", "evidence",
                    "catch tonnes", "% of catch", "explanation"])
    for t in order:
        e, r = taxa[t], resolved[t]
        ws.append([
            t, e["common_name"], e["functional_group"], e["commercial_group"],
            " | ".join(r["names"]),
            show_weights(r["weights"]) if len(r["weights"]) > 1 else "",
            r["basis"] if len(r["weights"]) > 1 else "",
            r["confidence"], r["evidence"],
            round(totals[t], 3), round(100 * totals[t] / grand, 4) if grand else 0,
            r["explanation"],
        ])
        ws.cell(ws.max_row, 5).fill = CONF_FILL.get(r["confidence"], CONF_FILL["low"])
    widths(ws, [34, 24, 28, 20, 40, 18, 18, 12, 20, 14, 10, 110])
    ws.freeze_panes = "B5"
    ws.sheet_view.showGridLines = False
    for row in ws.iter_rows(min_row=5):
        row[11].alignment = Alignment(wrap_text=False, vertical="top")
    return ws


def sheet_sppr(wb, order, resolved, methods, tl, unit, stem, scope='all'):
    """The combined SPPR sheet: the simple per-taxon value and the model's, side by side."""
    ws = wb.create_sheet("SPPR" if scope == 'all' else 'sppr_' + scope)
    ws.append([f"Specific PPR per taxon — {unit}, model {stem}"])
    ws["A1"].font = TITLE
    ws.append([f"sppr_simple is the trophic-chain estimate (1/TE)^(TL-1) at TE={TRANSFER_EFFICIENCY}, "
               "applied to the taxon's own trophic level and needing no model."])
    ws.append([SCOPES[scope] + '. Blank means unavailable, not zero. sppr_simple is an unpartitioned reference.'])
    hdr = header_row(ws, ["taxon", "trophic_level", "sppr_simple", "Ecopath group"] + methods)
    for t in order:
        r = resolved[t]
        level = tl.get(t)
        ws.append([
            t,
            level,
            simple_sppr(level),
            " | ".join(r["names"]),
        ] + list(r["sppr"]))
    assert hdr == 4, "SPPR header must sit on row 4; the PPR by taxon formulas assume it"
    widths(ws, [34, 14, 14, 40] + [15] * len(methods))
    # Composite group names must remain readable when adjacent method cells are blank.
    import textwrap
    for row in ws.iter_rows(min_row=5):
        cell = row[3]
        cell.alignment = Alignment(wrap_text=True, vertical='top')
        lines = sum(max(1, len(textwrap.wrap(part, width=34)))
                    for part in str(cell.value or '').splitlines())
        ws.row_dimensions[cell.row].height = max(18, 15 * lines + 6)
    ws.freeze_panes = "E5"
    ws.sheet_view.showGridLines = False
    if scope != 'all':
        ws.row_dimensions[4].height = 42
        for c in ws[4]:
            c.alignment = Alignment(wrap_text=True, vertical='center')
        for j in range(5, 5 + len(methods)):
            ws.column_dimensions[get_column_letter(j)].width = 21
    return ws


def sheet_ppr_by_method(wb, order, taxa, years, resolved, methods, tl, totals, grand,
                        scope='all', upstream_flags=None):
    """Rows are methods, columns are years, values are the sum over every taxon."""
    ws = wb.create_sheet("PPR by method" if scope == 'all' else 'PPR ' + scope)
    ws.append(["Total PPR by method and year — every taxon summed, tonnes wet weight "
               "equivalent of primary production."])
    ws["A1"].font = TITLE
    ws.append([SCOPES[scope] + '. The simple chain rows are unpartitioned references; model rows use this scope.'])
    ws.append(["Methods are not alternatives to be averaged. They rest on different "
               "assumptions and the spread between them is the result."])
    ws.append(["The two grey rows aggregate the catch to a group before exponentiating, "
               "which understates the total: SPPR is convex in trophic level, so they "
               "measure the Jensen effect rather than the PPR."])
    header_row(ws, ["method", "status"] + list(years))

    simple = []
    for y in years:
        s = 0.0
        for t in order:
            v = simple_sppr(tl.get(t))
            if v is None:
                continue
            s += taxa[t]["by_year"].get(y, 0.0) * v
        simple.append(s)
    ws.append(["simple trophic chain, per taxon", "ok"] + [round(v, 3) for v in simple])
    ws.cell(ws.max_row, 1).font = Font(italic=True)

    # The same simple method applied to catch-weighted mean trophic levels of the Sea
    # Around Us groups rather than to each taxon. SPPR is convex in TL, so aggregating
    # first and exponentiating after always understates the per-taxon sum -- Jensen's
    # inequality. These two rows exist to show the size of that gap, not to be used.
    for label, key in [("simple, aggregated to SAU functional group", "functional_group"),
                       ("simple, aggregated to SAU commercial group", "commercial_group")]:
        row = []
        for y in years:
            by_group = {}
            for t in order:
                level = tl.get(t)
                c = taxa[t]["by_year"].get(y, 0.0)
                if level is None or not c:
                    continue
                g = taxa[t][key] or "(none)"
                acc = by_group.setdefault(g, [0.0, 0.0])
                acc[0] += c
                acc[1] += c * level
            total = 0.0
            for c, ctl in by_group.values():
                if c:
                    total += c * (1.0 / TRANSFER_EFFICIENCY) ** ((ctl / c) - 1.0)
            row.append(round(total, 3))
        ws.append([label, "Jensen comparison, not a PPR estimate"] + row)
        ws.cell(ws.max_row, 1).font = Font(italic=True, color="808080")

    per_method, status = {}, {}
    for i, m in enumerate(methods):
        row = []
        for y in years:
            s, any_v = 0.0, False
            for t in order:
                v = resolved[t]["sppr"][i]
                if v is None:
                    continue
                c = taxa[t]["by_year"].get(y, 0.0)
                if c:
                    s += c * v
                    any_v = True
            row.append(round(s, 3) if any_v else None)
        per_method[m] = row

        # A negative SPPR means the solver diverged for that group under that method.
        # The resulting PPR is not small or uncertain, it is meaningless -- one Okhotsk
        # group comes out at -2.7e10 -- and an unflagged negative in a results table is
        # worse than no number at all.
        vals = [v for v in row if v is not None]
        ratio = max((abs(v) / s for v, s in zip(row, simple)
                     if v is not None and s), default=0.0)
        if (upstream_flags or {}).get(m):
            status[m] = upstream_flags[m]
        elif any(v < 0 for v in vals):
            status[m] = ("DIVERGED - negative SPPR reaches this ecosystem's catch; "
                         "the numbers on this row are not a PPR")
        elif not vals:
            status[m] = "did not resolve for any mapped group"
        elif all(v == 0 for v in vals):
            status[m] = "returned zero for every mapped group - check the method upstream"
        elif ratio > IMPLAUSIBLE_RATIO:
            status[m] = (f"IMPLAUSIBLE - up to {ratio:,.0f}x the trophic-chain estimate; "
                         "the solve is near-singular for this model")
        else:
            status[m] = "ok"
        ws.append([m, status[m]] + row)
        if status[m] != "ok":
            ws.cell(ws.max_row, 2).fill = PatternFill("solid", fgColor="FFC7CE")
            ws.cell(ws.max_row, 1).font = Font(bold=True, color="9C0006")

    ws.append([])
    resolved_t = sum(totals[t] for t in order
                     if resolved[t]["names"] != ["Unresolved"])
    ws.append([f"Catch tonnage on a named group: {resolved_t:,.0f} of {grand:,.0f} "
               f"({100 * resolved_t / grand if grand else 0:.1f} %). Unresolved taxa "
               "contribute nothing to the model rows and everything to the simple row, so "
               "the two are not directly comparable until coverage is 100 %."])
    flagged = [m for m in methods if status[m] != "ok"]
    if flagged:
        ws.append([f"{len(flagged)} of {len(methods)} methods are flagged above. A flagged "
                   "row is a property of this model under that method, not of the mapping; "
                   "see model_health in the SPPR workbook."])
        ws.cell(ws.max_row, 1).font = Font(bold=True, color="9C0006")
    ws.append(["Coverage by year, %:"])
    cov = []
    for y in years:
        tot_y = sum(taxa[t]["by_year"].get(y, 0.0) for t in order)
        res_y = sum(taxa[t]["by_year"].get(y, 0.0) for t in order
                    if resolved[t]["names"] != ["Unresolved"])
        cov.append(round(100 * res_y / tot_y, 2) if tot_y else None)
    ws.append(["catch on a named group, %", ""] + cov)

    widths(ws, [42, 60] + [14] * len(years))
    ws.freeze_panes = "C5"
    ws.sheet_view.showGridLines = False
    return per_method, simple, status


def sheet_ppr_by_taxon(wb, order, years, methods, catch_ws, n_meta_cols):
    """taxon x method for one year, chosen from a dropdown. Live formulas.

    Column letters are derived from the sheets that were just written rather than
    hardcoded, because a layout change that moves a column is exactly the kind of thing
    that silently corrupts a formula-driven sheet.
    """
    ws = wb.create_sheet("PPR by taxon")
    ws.append(["PPR per taxon for one year — pick the year in the yellow cell."])
    ws["A1"].font = TITLE
    ws.append(["PPR = that year's catch for the taxon x the taxon's SPPR under each method. "
               "Everything below recalculates when the year changes."])
    ws.append([])
    ws["A4"] = "Year"
    ws["A4"].font = HEAD
    ws["B4"] = years[-1]
    ws["B4"].fill = PatternFill("solid", fgColor="FFF2CC")
    ws["B4"].font = Font(bold=True, size=12)
    ws["C4"] = f"choose any year from {years[0]} to {years[-1]}"
    ws["C4"].font = Font(italic=True, color="808080")
    ws.append([])

    first_year_col = 5                      # Catch: A taxon, B common, C fg, D cg, E first year
    cy0 = get_column_letter(first_year_col)
    cy1 = get_column_letter(first_year_col + len(years) - 1)
    sm0 = get_column_letter(n_meta_cols + 1)              # SPPR: first method column
    sm1 = get_column_letter(n_meta_cols + len(methods))
    assert catch_ws.cell(1, first_year_col).value == years[0], "Catch year block moved"

    dv = DataValidation(type="list", formula1=f"=Catch!${cy0}$1:${cy1}$1", allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(ws["B4"])

    header_row(ws, ["taxon", "Ecopath group", "catch tonnes"] + methods)
    hdr = ws.max_row
    total_row = hdr + 1
    first = hdr + 2
    last = first + len(order) - 1

    ws.cell(total_row, 1, "ALL TAXA")
    ws.cell(total_row, 1).font = HEAD
    ws.cell(total_row, 3, f"=SUM(C{first}:C{last})").font = HEAD
    for j in range(len(methods)):
        col = get_column_letter(4 + j)
        ws.cell(total_row, 4 + j, f'=IF(COUNT({col}{first}:{col}{last})=0,"",SUM({col}{first}:{col}{last}))').font = HEAD

    for i, t in enumerate(order):
        r = first + i
        ws.cell(r, 1, t)
        ws.cell(r, 2, f"=IFERROR(INDEX(SPPR!$D:$D,MATCH($A{r},SPPR!$A:$A,0)),\"\")")
        ws.cell(r, 3, f"=IFERROR(INDEX(Catch!${cy0}:${cy1},MATCH($A{r},Catch!$A:$A,0),"
                      f"MATCH($B$4,Catch!${cy0}$1:${cy1}$1,0)),0)")
        for j in range(len(methods)):
            lookup = (f'INDEX(SPPR!${sm0}:${sm1},'
                      f'MATCH($A{r},SPPR!$A:$A,0),{j + 1})')
            ws.cell(r, 4 + j,
                    f'=IFERROR(IF(ISNUMBER({lookup}),$C{r}*{lookup},""),"")')

    widths(ws, [34, 40, 14] + [15] * len(methods))
    ws.freeze_panes = f"D{first}"
    ws.sheet_view.showGridLines = False
    return ws


def sheet_model_groups(wb, groups, methods, sppr_by_group):
    ws = wb.create_sheet("Model groups")
    ws.append(["The model's own compartments, and their SPPR under each method."])
    ws["A1"].font = TITLE
    ws.append(["Group names here are authoritative. Everything in the other sheets joins "
               "on them character for character."])
    ws.append([])
    header_row(ws, ["seq", "group_name", "type", "TL", "GE", "EE", "biomass",
                    "model catch"] + methods)
    for g in groups:
        vals = sppr_by_group.get(g["group_name"], [None] * len(methods))
        ws.append([g.get("seq"), g["group_name"], g.get("group_type"), num(g.get("tl")),
                   num(g.get("ge")), num(g.get("ee")), num(g.get("biomass")),
                   num(g.get("catch"))]
                  + [None if num(v) is None else round(num(v), SPPR_DP) for v in vals])
    widths(ws, [6, 40, 10, 10, 10, 10, 14, 14] + [15] * len(methods))
    ws.freeze_panes = "C5"
    ws.sheet_view.showGridLines = False


def sheet_npp(wb, npp, years=()):
    ws = wb.create_sheet("NPP")
    ws.append(["Annual net primary production, tonnes carbon per year"])
    ws["A1"].font = TITLE
    ws.append(["PPR/NPP uses the ensemble median for the matching catch year. Blank values are unavailable; no year is substituted."])
    numeric = ['npp_antoinemorel_tC_yr', 'npp_vgpm_tC_yr', 'npp_eppley_tC_yr',
               'npp_cbpm_tC_yr', 'npp_cafe_tC_yr', 'ens_median_tC_yr',
               'ens_min_tC_yr', 'ens_max_tC_yr']
    header_row(ws, ['year'] + numeric + ['status', 'reason', 'provenance',
                                       'n_models', 'available_models', 'ensemble_basis'])
    available_years = {int(y) for y in (npp or {}).get('annual', {})}
    if not available_years and npp_for_year(npp, 2019):
        available_years.add(2019)
    for year in sorted(set(years) | available_years):
        rec = npp_for_year(npp, year) or {}
        vals = [num(float(rec[k])) if rec.get(k) not in (None, '') else None for k in numeric]
        ws.append([year] + vals + [rec.get('status') or 'unavailable',
                                  rec.get('reason') or ('' if any(v is not None for v in vals) else 'No annual NPP estimate recorded'),
                                  rec.get('provenance') or '',
                                  int(rec['n_models']) if rec.get('n_models') not in (None, '') else None,
                                  rec.get('available_models') or '', rec.get('ensemble_basis') or ''])
    widths(ws, [10] + [23] * len(numeric) + [22, 60, 75, 12, 36, 65])
    for c in ws[3]:
        c.alignment = Alignment(wrap_text=True, vertical='center')
    ws.row_dimensions[3].height = 32
    ws.freeze_panes = 'B4'
    ws.auto_filter.ref = f'A3:O{ws.max_row}'
    ws.sheet_view.showGridLines = False
    return npp


def sheet_summary(wb, unit, stem, meta, order, taxa, years, resolved, methods,
                  per_method, simple, status, npp, totals, grand, notes_head):
    ws = wb.create_sheet("Summary", 0)
    ws.append([f"{unit} — {meta.get('region_name') or ''}"])
    ws["A1"].font = TITLE
    ws.append([f"Ecopath model: {stem}"])
    ws["A2"].font = Font(bold=True)
    if notes_head:
        ws.append([notes_head])
        ws.cell(ws.max_row, 1).font = Font(italic=True)
    ws.append([])

    # Never lead with a method that diverged for this model. `new_TE_EEfix` is the
    # primary solver and the natural headline, but it produces negative SPPR on the
    # Okhotsk model, and a Summary sheet quoting -71 billion tonnes would be read as the
    # answer by anyone who did not scroll to the flags.
    def usable(m):
        return status.get(m) == "ok" and any(v is not None for v in per_method[m])
    headline = (next((m for m in HEADLINE if m in methods and usable(m)), None)
                or next((m for m in methods if usable(m)), None))
    resolved_t = sum(totals[t] for t in order if resolved[t]["names"] != ["Unresolved"])
    n_unres = sum(1 for t in order if resolved[t]["names"] == ["Unresolved"])
    n_comp = sum(1 for t in order if len(resolved[t]["names"]) > 1)

    for k, v in [
        ("region type", meta.get("region_type") or ""),
        ("latitude", meta.get("marker_lat") or ""),
        ("longitude", meta.get("marker_lon") or ""),
        ("catch years", f"{years[0]}-{years[-1]}"),
        ("taxa in catch", len(order)),
        ("taxa apportioned across groups", n_comp),
        ("taxa unresolved", n_unres),
        ("catch tonnage on a named group, %", round(100 * resolved_t / grand, 1) if grand else 0),
        ("SPPR methods", len(methods)),
        ("methods flagged as unusable", sum(1 for m in methods if status.get(m) != "ok")),
        ("headline method below", headline or "none usable — see PPR by method"),
    ]:
        ws.append([k, v])
    ws.append([])

    header_row(ws, ["year", "catch_tonnes", "ppr_simple", f"ppr_{headline}",
                    "ppr_simple / NPP %", f"ppr_{headline} / NPP %"])
    hi = methods.index(headline) if headline else None
    for i, y in enumerate(years):
        annual = npp_for_year(npp, y) or {}
        npp_median = float(annual['ens_median_tC_yr']) if annual.get('ens_median_tC_yr') not in (None, '') else None
        catch = sum(taxa[t]["by_year"].get(y, 0.0) for t in order)
        ps = simple[i]
        pm = per_method[headline][i] if headline else None
        ws.append([
            y, round(catch, 3), round(ps, 3), pm,
            round(100 * ps / WET_WEIGHT_TO_CARBON / npp_median, 4) if npp_median else None,
            round(100 * pm / WET_WEIGHT_TO_CARBON / npp_median, 4) if (npp_median and pm is not None) else None,
        ])
    ws.append(['PPR/NPP converts wet-weight PP to carbon at 9:1 and uses the matching year\'s NPP ensemble median.'])
    ws.append(['PPR/NPP is blank for years without NPP; see NPP for availability and provenance.'])
    widths(ws, [36, 22, 20, 24, 20, 24])
    ws.freeze_panes = "A2"
    ws.sheet_view.showGridLines = False


# ------------------------------------------------------------------------------ main

def load_atlas():
    p = ROOT / "PPRAtlas" / "data" / "regions.csv"
    if not p.exists():
        return {}
    with p.open(encoding="utf-8-sig") as fh:
        return {r["unit_id"]: r for r in csv.DictReader(fh)}


def load_npp_json(unit):
    """Load authoritative annual data rather than a potentially stale JSON export."""
    return load_npp(ROOT).get(unit)


def save_workbook_atomic(wb, out):
    """Serialize beside the output, then replace it without opening it for truncation.

    An intermittent Windows EINVAL has occurred when ZipFile opens an existing
    destination with ``w+b``. Passing an already-open temporary stream avoids that
    operation and keeps the last usable workbook intact if serialization fails.
    """
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w+b', prefix='.model-', suffix='.xlsx',
                                         dir=out.parent, delete=False) as stream:
            temporary = Path(stream.name)
            wb.save(stream)
        os.replace(temporary, out)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def build_one(unit, book_path, atlas):
    stem = book_path.stem
    mapping_csv = mio.mapping_dir(ROOT, unit) / f"{stem}.csv"
    if not mapping_csv.exists():
        return None, f"no mapping at {mapping_csv.relative_to(ROOT)}"

    groups = mio.read_groups(book_path)
    methods, sppr_by_group = mio.read_methods(book_path)
    if not groups or not methods:
        return None, f"{stem}: groups_df or sppr_all missing"
    groups_by_name = {g["group_name"]: g for g in groups}
    known = set(groups_by_name)

    rows = mio.read_mapping_csv(mapping_csv)
    taxa, years = mio.read_catch(ROOT, unit)
    tl = mio.read_trophic_levels(ROOT, unit)
    if not taxa:
        return None, f"{unit}: no catch"

    bad = []
    seen = set()
    for r in rows:
        t = (r.get("taxon") or "").strip()
        if not t:
            continue
        seen.add(t)
        for n in mio.parse_groups_cell(r.get("group")):
            if n.lower() != "unresolved" and n not in known:
                bad.append((t, n))
    if bad:
        return None, (f"{stem}: {len(bad)} mapped group(s) absent from groups_df, "
                      f"e.g. {bad[:4]}")
    missing = [t for t in taxa if t not in seen]
    if missing:
        return None, (f"{stem}: {len(missing)} catch taxa have no mapping row, "
                      f"e.g. {sorted(missing)[:4]}")

    for e in taxa.values():
        e["by_year"] = {y: round(v, CATCH_DP) for y, v in e["by_year"].items()}
    decided = sum(1 for r in rows
                  if mio.parse_groups_cell(r.get("group"))
                  and mio.parse_groups_cell(r.get("group")) != ["Unresolved"])
    if not decided:
        return None, (f"{stem}: no taxon has been assigned a group yet "
                      "(the mapping is still a stub)")

    totals = {t: sum(v["by_year"].values()) for t, v in taxa.items()}
    grand = sum(totals.values())
    order = sorted(taxa, key=lambda t: -totals[t])
    resolved = build_taxon_sppr(rows, methods, sppr_by_group, groups_by_name, totals)
    scoped = read_scopes(book_path)
    health = read_health(book_path)

    notes = mio.mapping_dir(ROOT, unit) / f"{stem}.notes.md"
    notes_head = ""
    if notes.exists():
        for line in notes.read_text(encoding="utf-8").splitlines():
            s = line.strip().lstrip("#").strip()
            if s and not s.startswith("---"):
                notes_head = s[:200]
                break
    selection_path = ROOT / 'data/atlas_selection.json'
    if selection_path.exists():
        choice = json.loads(selection_path.read_text(encoding='utf-8')).get('units', {}).get(unit, {})
        notes_head = (choice.get('note', '') + ' ' + notes_head).strip()

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    catch_ws = sheet_catch(wb, order, taxa, years)
    sheet_map(wb, order, taxa, resolved, totals, grand)
    sheet_final_mappings(wb, final_mapping_rows(unit, stem, taxa, resolved, totals))
    sheet_sppr(wb, order, resolved, methods, tl, unit, stem)
    per_method, simple, method_status = sheet_ppr_by_method(
        wb, order, taxa, years, resolved, methods, tl, totals, grand,
        upstream_flags=method_health_flags(methods, sppr_by_group, health))
    for scope in ('inner', 'PP'):
        scope_methods, scope_groups = scoped[scope]
        scope_resolved = build_taxon_sppr(rows, scope_methods, scope_groups, groups_by_name, totals)
        sheet_sppr(wb, order, scope_resolved, scope_methods, tl, unit, stem, scope=scope)
        sheet_ppr_by_method(wb, order, taxa, years, scope_resolved, scope_methods, tl, totals, grand,
                            scope=scope, upstream_flags=method_health_flags(scope_methods, scope_groups, health))
    add_recycling_sheet(wb, [book_path])
    sheet_ppr_by_taxon(wb, order, years, methods, catch_ws, n_meta_cols=4)
    sheet_model_groups(wb, groups, methods, sppr_by_group)
    npp = sheet_npp(wb, load_npp_json(unit), years)
    sheet_summary(wb, unit, stem, atlas.get(unit, {}), order, taxa, years, resolved,
                  methods, per_method, simple, method_status, npp, totals, grand,
                  notes_head)

    out = ROOT / "data" / unit / "models" / f"{stem}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        save_workbook_atomic(wb, out)
    finally:
        wb.close()

    audit = mio.mapping_dir(ROOT, unit) / f"{stem}.resolved.csv"
    with audit.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["taxon", "groups", "weights", "weight_basis", "confidence",
                    "catch_tonnes"] + methods)
        for t in order:
            r = resolved[t]
            w.writerow([t, " | ".join(r["names"]),
                        " | ".join(f"{x:.6f}" for x in r["weights"]),
                        r["basis"], r["confidence"], round(totals[t], 3)]
                       + ["" if v is None else f"{v:.6f}" for v in r["sppr"]])

    resolved_t = sum(totals[t] for t in order if resolved[t]["names"] != ["Unresolved"])
    return {
        "unit": unit, "model": stem, "taxa": len(order),
        "unresolved": sum(1 for t in order if resolved[t]["names"] == ["Unresolved"]),
        "composite": sum(1 for t in order if len(resolved[t]["names"]) > 1),
        "coverage": round(100 * resolved_t / grand, 1) if grand else 0.0,
        "path": out.relative_to(ROOT).as_posix(),
    }, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", nargs="*", help="default: every unit with a mapping")
    a = ap.parse_args()

    units = a.units or sorted(
        d.name for d in (ROOT / "data").iterdir()
        if d.is_dir() and (d / "mapping").is_dir() and mio.mapping_files(ROOT, d.name))
    atlas = load_atlas()

    ok, failed = [], []
    for unit in units:
        for book in mio.model_workbooks(ROOT, unit):
            res, err = build_one(unit, book, atlas)
            if err:
                failed.append(err)
            else:
                ok.append(res)
                print(f"  {res['path']}")
                print(f"      {res['taxa']} taxa, {res['composite']} apportioned, "
                      f"{res['unresolved']} unresolved, {res['coverage']} % of tonnage mapped")
    for e in failed:
        print(f"  skipped: {e}", file=sys.stderr)
    print(f"\nbuilt {len(ok)} model workbook(s); {len(failed)} skipped")
    return 0 if ok or not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
