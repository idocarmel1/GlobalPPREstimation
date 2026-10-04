import datetime as dt
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image, ImageChops

RUN = Path(__file__).resolve().parents[1]
data_path = RUN / "qa/old_word_trial.json"
data = json.loads(data_path.read_text(encoding="utf-8"))
fallback = json.loads((RUN / "qa/old_word_fallback_render.json").read_text(encoding="utf-8-sig"))
QA = Path(data["document"]).parent / "work/2026-10-04_000009_old_word_trial/qa"
poppler = Path("C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin")
results = {}
for target in fallback["documents"]:
    pdf = Path(target["pdf"])
    info = subprocess.run([str(poppler / "pdfinfo.exe"), str(pdf)], capture_output=True, text=True, check=True)
    prefix = pdf.parent / target["label"]
    render = subprocess.run([str(poppler / "pdftoppm.exe"), "-png", "-r", "110", str(pdf), str(prefix)], capture_output=True, text=True, check=True)
    dest = QA / target["label"]
    dest.mkdir(exist_ok=True)
    pages = []
    for p in sorted(pdf.parent.glob(target["label"]+"-*.png")):
        output = dest / ("page-"+p.stem.split("-")[-1]+".png")
        shutil.copyfile(p, output)
        pages.append(str(output))
    results[target["label"]] = {"pages": pages, "pdfinfo": info.stdout, "render_stderr": render.stderr}
assert len(results["before"]["pages"]) == len(results["after"]["pages"])
diffs = []
for page, (before, after) in enumerate(zip(results["before"]["pages"], results["after"]["pages"]), start=1):
    a, b = Image.open(before).convert("RGB"), Image.open(after).convert("RGB")
    assert a.size == b.size
    diff = ImageChops.difference(a,b)
    box = diff.getbbox()
    diffs.append({"page": page, "size": a.size, "different": box is not None, "diff_box": box})
data["render"] = {"fallback": fallback, "raster": results, "page_image_comparison": diffs,
                  "page_count": len(diffs), "all_pages_visually_inspected": False}
data["operations"] += [
    {"timestamp":dt.datetime.now(dt.timezone.utc).isoformat(),"kind":"word_fallback_attempts",
     "attempt_count":3,"successful_attempt_count":1,"exports":2,"readonly":True,
     "failure_reasons":["sandbox COM 80070520 logon session","PowerShell 7 COM Hwnd null before document open"],
     "created_final_instance_closed":True,"prior_sessions_preserved":True},
    {"timestamp":dt.datetime.now(dt.timezone.utc).isoformat(),"kind":"poppler_raster",
     "render_count":2,"page_images":len(diffs)*2,"dpi":110,"image_comparison_pages":len(diffs)},
    {"timestamp":dt.datetime.now(dt.timezone.utc).isoformat(),"kind":"artifact_marker",
     "count":1,"operation_kind":"edit","expected_output_count":1,"output_format":"docx","exit_code":0},
    {"timestamp":dt.datetime.now(dt.timezone.utc).isoformat(),"kind":"percentage_format_check","count":1,"exit_code":0}
]
data_path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({"page_count":len(diffs),"comparison":diffs,"images":results["after"]["pages"]},ensure_ascii=False))
