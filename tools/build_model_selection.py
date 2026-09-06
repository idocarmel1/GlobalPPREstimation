"""Build `data/model_selection.xlsx` — which article and model each ecosystem uses.

One row per candidate model, not per ecosystem: several ecosystems have more than one
published model, and the point of this sheet is to record *which* was chosen and why the
others were not. The `usable` column is the operative one — a model can be extracted and
still be unfit, and three of the pilot candidates are.

Seeded from the project owner's tracking spreadsheet. Cross-checked against what is
actually on disk: `PPREstimation/real_models/global_cover_jsons/` for extracted models and
`PPRAtlas/archive/regions/<unit_id>/` for archived articles, so the sheet cannot silently
drift from the repository.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "model_selection.xlsx"
MODEL_JSON_DIR = ROOT / "PPREstimation" / "real_models" / "global_cover_jsons"
SPPR_DIR = ROOT / "PPREstimation" / "output" / "top10"
ARCHIVE = ROOT / "PPRAtlas" / "archive" / "regions"
ATLAS_REGIONS = ROOT / "PPRAtlas" / "data" / "regions.csv"

# Transcribed from the owner's tracking sheet. `usable` is derived from the run results
# and notes: a model that explodes, is unbalanced, or is flagged NOT USEABLE is not usable.
ROWS = [
    # unit, name, priority, author, title, ge, te, usable, notes
    ("LME_036", "South China Sea", "VERY HIGH", "Cheung W.L. (2007)",
     "Vulnerability of marine fishes to fishing: from global overview to the South China Sea",
     "ok", "sppr of one group", "yes", "prefer model for 2000"),
    ("LME_032", "Arabian Sea", "HIGH", "Mohamed K.S (2008)",
     "A trophic model of the Arabian Sea Ecosystem off Karnataka",
     "ok", "ok", "yes", ""),
    ("LME_034", "Bay of Bengal", "VERY HIGH", "Guenette (2013)",
     "An exploratory ecosystem model of the Bay of Bengal Large Marine Ecosystem",
     "ok", "ok", "yes", "meiobenthos DC fixed to eat 100% detritus"),
    ("LME_047", "East China Sea", "VERY HIGH", "Xu L, Song P, Wang Y, Xie B, Huang L, Li Y, Zhen...",
     "Estimating the Impact of a Seasonal Fishing Moratorium",
     "ok", "ok", "yes", "used the 2018 model"),
    ("LME_052", "Sea of Okhotsk", "HIGH", "(2004)",
     "A model of the Okhotsk Sea with a focus on the northeast",
     "ok", "ok for NE", "partial", "ONLY NE is good; SD explodes for TE"),
    ("LME_013", "Humboldt Current (north)", "VERY HIGH", "Chiaverano, Luciano M. et al. (2018)",
     "Evaluating the role of large jellyfish and forage fishes as energy pathways",
     "ok", "ok", "yes", "one group has EE=0"),
    ("LME_013", "Humboldt Current (south)", "VERY HIGH", "Neira et al. (2026)",
     "Analysing ecosystem and demersal stocks dynamics",
     "explodes", "explodes", "no", "2 models, both not good enough"),
    ("LME_027", "Canary Current", "HIGH", "",
     "", "ok", "EE=0 for 10 groups, max_sppr=3M", "no", ""),
    ("LME_027", "Canary Current", "HIGH", "From Ecobase 118",
     "Assessing the Contribution of Marine Protected Areas",
     "ok", "explodes", "no", "NOT BALANCED according to PPRCalculator - needs verifying"),
    ("LME_028", "Guinea Current", "HIGH", "Ecobase 726 (2009) and 646 (2004)",
     "", "ok", "ok", "yes", "646 is the better of the two"),
    ("HS_077", "Pacific, Eastern Central", "HS_077", "Olson & Watters (2003)",
     "A model of the pelagic ecosystem in the eastern tropical Pacific Ocean",
     "", "", "no", "NOT USEABLE - DC rows far from 1 (check later)"),
    ("LME_035", "Gulf of Thailand", "HIGH", "From Ecobase 412 (Christensen, 1998)",
     "", "ok", "ok", "yes", ""),
    ("LME_035", "Gulf of Thailand", "HIGH", "Mala Supongpan (2003)",
     "Trophic Model of the Coastal Fisheries Ecosystem in the Gulf of Thailand",
     "", "", "unchecked", "NOT CHECKED"),
    ("LME_022", "North Sea", "HIGH", "Saygu I, Thurstan RH, Roberts C, Heard Z, Akoglu...",
     "Historical ecosystem models can serve as a baseline for indicator-based assessment: the North Sea",
     "", "", "unchecked", "candidate - not yet extracted"),
    ("LME_049", "Kuroshio Current", "HIGH", "Gan C. et al. (2025)",
     "Study on the ecosystem structure and trophodynamics in the Kuroshio-Oyashio Extension area",
     "", "", "unchecked", "candidate - not yet extracted"),
]

HEAD = ["unit_id", "region_name", "priority", "author", "title", "ge_run", "te_run",
        "usable", "notes", "extracted_models_on_disk", "sppr_workbooks_on_disk",
        "archived_articles_on_disk"]

FILL = {
    "yes": PatternFill("solid", fgColor="C6EFCE"),
    "partial": PatternFill("solid", fgColor="FFEB9C"),
    "no": PatternFill("solid", fgColor="FFC7CE"),
    "unchecked": PatternFill("solid", fgColor="E7E6E6"),
}


def unit_from_model_filename(name: str) -> str | None:
    m = re.match(r"^(\d+)HS_", name)
    if m:
        return f"HS_{int(m.group(1)):03d}"
    m = re.match(r"^(\d+)_", name)
    if m:
        return f"LME_{int(m.group(1)):03d}"
    return None


def on_disk(unit: str) -> tuple[int, int, int]:
    models = sum(1 for p in MODEL_JSON_DIR.glob("*.json")
                 if unit_from_model_filename(p.name) == unit) if MODEL_JSON_DIR.exists() else 0
    books = sum(1 for p in SPPR_DIR.glob("*.xlsx")
                if unit_from_model_filename(p.name) == unit) if SPPR_DIR.exists() else 0
    d = ARCHIVE / unit
    arts = sum(1 for p in d.iterdir() if p.is_dir()) if d.exists() else 0
    return models, books, arts


def main() -> int:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Model selection"

    ws.append(["Selected article and Ecopath model per ecosystem"])
    ws["A1"].font = Font(bold=True, size=14)
    ws.append(["One row per candidate model. `usable` is the operative column - a model can be "
               "extracted and still be unfit for PPR."])
    ws.append(["The last three columns are read from the repository at build time, so this sheet "
               "cannot drift from what is actually on disk."])
    ws.append([])
    ws.append(HEAD)
    for c in ws[5]:
        c.font = Font(bold=True)

    for r in ROWS:
        unit = r[0]
        m, b, a = on_disk(unit)
        ws.append(list(r) + [m, b, a])
        ws.cell(ws.max_row, 8).fill = FILL.get(r[7], FILL["unchecked"])

    widths = [10, 26, 11, 34, 56, 10, 26, 10, 44, 12, 12, 12]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A6"
    ws.sheet_view.showGridLines = False
    for row in ws.iter_rows(min_row=5):
        for c in row:
            c.alignment = Alignment(vertical="top", wrap_text=False)

    # second sheet: the ecosystems with catch but no model at all, so the gap is visible
    gaps = wb.create_sheet("Ecosystems without a model")
    gaps.append(["Ecosystems that have catch data but no extracted Ecopath model."])
    gaps["A1"].font = Font(bold=True)
    gaps.append(["Ranked by the 1995 PPR method where PPRAtlas provides a rank - these are the "
                 "candidates worth extracting next."])
    gaps.append([])
    gaps.append(["unit_id", "region_name", "region_type", "ppr_rank_1995", "archived_articles"])
    for c in gaps[4]:
        c.font = Font(bold=True)

    atlas = {}
    if ATLAS_REGIONS.exists():
        with ATLAS_REGIONS.open(encoding="utf-8-sig") as fh:
            atlas = {r["unit_id"]: r for r in csv.DictReader(fh)}
    modelled = {r[0] for r in ROWS if r[7] in ("yes", "partial")}
    idx = ROOT / "data" / "INDEX.csv"
    rows = []
    if idx.exists():
        with idx.open(encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                if r["unit_id"] in modelled or int(r["articles"] or 0) == 0:
                    continue
                a = atlas.get(r["unit_id"], {})
                rank = a.get("ppr_rank") or ""
                rows.append((r["unit_id"], r["region_name"], r["region_type"],
                             int(rank) if str(rank).isdigit() else 9999, int(r["articles"])))
    for row in sorted(rows, key=lambda t: t[3])[:60]:
        gaps.append([row[0], row[1], row[2], row[3] if row[3] != 9999 else "", row[4]])
    for i, w in enumerate([10, 34, 12, 15, 18], start=1):
        gaps.column_dimensions[get_column_letter(i)].width = w
    gaps.freeze_panes = "A5"
    gaps.sheet_view.showGridLines = False

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    wb.close()

    usable = sum(1 for r in ROWS if r[7] == "yes")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  candidate models tracked : {len(ROWS)}")
    print(f"  usable                   : {usable}")
    print(f"  partial                  : {sum(1 for r in ROWS if r[7] == 'partial')}")
    print(f"  not usable               : {sum(1 for r in ROWS if r[7] == 'no')}")
    print(f"  unchecked                : {sum(1 for r in ROWS if r[7] == 'unchecked')}")
    print(f"  ecosystems with a usable or partial model : {len({r[0] for r in ROWS if r[7] in ('yes','partial')})}")
    print(f"  gap list (catch + articles, no model)     : {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
