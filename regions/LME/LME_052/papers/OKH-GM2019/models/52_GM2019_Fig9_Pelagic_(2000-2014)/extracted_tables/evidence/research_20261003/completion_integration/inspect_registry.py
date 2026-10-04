"""Read the bounded LME052 central metadata without traversing annual archives."""
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "tools"))
from researcher_review import table_rows


def bounded_table(archive, sheet, table):
    _, header, _, data = table_rows(archive, sheet, table)
    return header, [row for _, row in data]


with zipfile.ZipFile(ROOT / "Project.xlsx") as archive:
    model_header, models = bounded_table(archive, "Models & coverage", "Models")
    paper_header, papers = bounded_table(archive, "Papers", "Papers")
    _, geometry_rows = bounded_table(archive, "Map geography", "Geometry")
    geometry_selected = [r for r in geometry_rows if any(str(v) in {"LME_052", "article:OKH-GM2019", "article:OKH-2015"} for v in r.values())]
with zipfile.ZipFile(ROOT / "regions/LME_052/LME_052.xlsx") as archive:
    _, settings = bounded_table(archive, "Overview", "Settings")

result = {
    "models_header": model_header,
    "papers_header": paper_header,
    "models": [r for r in models if r.get("unit_id") == "LME_052"],
    "papers": [r for r in papers if r.get("unit_id") == "LME_052" or r.get("article_id") == "OKH-GM2019"],
    "geometry_chunks": geometry_selected,
    "settings": settings,
}
out = Path(__file__).with_name("registry_before.json")
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k != "geometry_chunks"}, ensure_ascii=False, indent=2))
print("geometry chunks", len(geometry_selected))
