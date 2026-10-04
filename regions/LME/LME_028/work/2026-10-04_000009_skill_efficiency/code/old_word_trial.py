import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
import zipfile
import xml.etree.ElementTree as ET

RUN = Path(__file__).resolve().parents[1]
ISO = RUN / "outputs" / "old_word_project"
MODEL = ISO / "regions/LME/LME_036/papers/SCS-2007/models/36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)"
DOC = MODEL / "model_validation/validation.docx"
QA = MODEL / "model_validation/work/2026-10-04_000009_old_word_trial/qa"
META = RUN / "qa/old_word_trial.json"
OLD = b"Taxon mapping and coverage"
NEW = b"Taxon mapping coverage"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load():
    return json.loads(META.read_text(encoding="utf-8"))

def save(data):
    META.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def record(data, kind, **kwargs):
    data["operations"].append({"timestamp": now(), "kind": kind, **kwargs})

def files():
    return {p.relative_to(ISO).as_posix(): {"sha256": sha(p.read_bytes()), "size": p.stat().st_size}
            for p in ISO.rglob("*") if p.is_file() and not p.is_relative_to(QA.parent)}

def doc_parts(path):
    with zipfile.ZipFile(path) as z:
        return {i.filename: z.read(i.filename) for i in z.infolist()}

def manual_rows(xml):
    tree = ET.fromstring(xml)
    found = {}
    for row in tree.iter(W + "tr"):
        cells = row.findall(W + "tc")
        if not cells:
            continue
        label = "".join(cells[0].itertext())
        for target in ["SPPR calculation", "Open issues and next action", "Review and reproducibility"]:
            if target in label:
                found[target] = sha(ET.tostring(row))
    assert set(found) == {"SPPR calculation", "Open issues and next action", "Review and reproducibility"}
    return found

def init():
    QA.mkdir(parents=True, exist_ok=True)
    baseline = QA / "before.docx"
    shutil.copyfile(DOC, baseline)
    inventory = files()
    parts = doc_parts(DOC)
    data = {
        "task": "OLD instruction observed bounded single-heading edit",
        "start_utc": "2026-10-04T05:26:35+00:00",
        "document": str(DOC), "isolated_project": str(ISO),
        "requested_change": {"before": OLD.decode(), "after": NEW.decode()},
        "instruction_checkpoint": str(RUN / "inputs/old_ecopath-model-validation.txt"),
        "trace": str(RUN / "qa/old_word_trace.jsonl"),
        "baseline_files": inventory,
        "baseline_docx_package": {k: sha(v) for k, v in parts.items()},
        "manual_rows_before": manual_rows(parts["word/document.xml"]),
        "operations": [],
        "instrumentation_issues": [
            {"kind": "version_crossing", "path": "tools/skills/paper-to-ppr/SKILL.md",
             "reason": "OLD validation entry mandated pipeline consultation; current revised entry read before parent supplied OLD checkpoint.",
             "exclude_from_matched_required_reference_counts": True, "keep_in_raw_totals": True},
            {"kind": "output_truncation", "reason": "Initial batched contract/skills output was truncated; individual rereads used and retained in raw trace."},
            {"kind": "lost_read_return", "reason": "First combined docx/Overview command yielded after 10 seconds and its session metadata was not retained; Overview reread synchronously. Raw trace counts both."}
        ],
        "scientific_reevaluation": False, "workbook_writes": 0,
        "scientific_execution": 0, "selection_or_adoption": False,
    }
    record(data, "binary_baseline", file_count=len(inventory), package_part_count=len(parts),
           baseline_copy=str(baseline), binary_hash_reads=len(inventory) + 1, package_read_count=1)
    save(data)
    print(json.dumps({"baseline": str(baseline), "files": len(inventory), "package_parts": len(parts)}))

def edit():
    data = load()
    before = doc_parts(QA / "before.docx")
    xml = before["word/document.xml"]
    assert xml.count(OLD) == 1, xml.count(OLD)
    root = ET.fromstring(xml)
    headings = [e for e in root.iter(W + "p") if "".join(e.itertext()) == OLD.decode()]
    assert len(headings) == 1
    changed = xml.replace(OLD, NEW)
    output = DOC.with_suffix(".trial.docx")
    with zipfile.ZipFile(DOC) as source, zipfile.ZipFile(output, "w") as dest:
        dest.comment = source.comment
        for entry in source.infolist():
            dest.writestr(entry, changed if entry.filename == "word/document.xml" else source.read(entry.filename))
    output.replace(DOC)
    record(data, "minimal_ooxml_edit", document=str(DOC), replacement_count=1,
           changed_part="word/document.xml", package_read_count=1, package_write_count=1,
           old_bytes=len(xml), new_bytes=len(changed), edit_command_count=1)
    save(data)
    verify()

def verify():
    data = load()
    before = doc_parts(QA / "before.docx")
    after = doc_parts(DOC)
    assert set(before) == set(after)
    changed_parts = [k for k in before if before[k] != after[k]]
    assert changed_parts == ["word/document.xml"]
    assert after["word/document.xml"] == before["word/document.xml"].replace(OLD, NEW)
    assert manual_rows(after["word/document.xml"]) == data["manual_rows_before"]
    before_text = [e.text for e in ET.fromstring(before["word/document.xml"]).iter(W + "t")]
    after_text = [e.text for e in ET.fromstring(after["word/document.xml"]).iter(W + "t")]
    expected = [NEW.decode() if t == OLD.decode() else t for t in before_text]
    assert after_text == expected
    before_layout = re.sub(re.escape(OLD), NEW, before["word/document.xml"])
    assert before_layout == after["word/document.xml"]
    inventory = files()
    changed_files = [p for p in data["baseline_files"] if inventory[p] != data["baseline_files"][p]]
    doc_relative = DOC.relative_to(ISO).as_posix()
    assert changed_files == [doc_relative], changed_files
    links = []
    ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    for part_name, body in after.items():
        if not part_name.endswith(".rels"):
            continue
        tree = ET.fromstring(body)
        for r in tree:
            if r.get("Type", "").endswith("/hyperlink"):
                target = r.get("Target")
                local = not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) and not target.startswith("#")
                resolved = DOC.parent / target.split("#", 1)[0] if local else None
                links.append({"id": r.get("Id"), "target": target, "local": local,
                              "resolved_exists": resolved.exists() if local else None})
    data["preservation"] = {
        "verified_utc": now(), "changed_files": changed_files, "changed_docx_parts": changed_parts,
        "other_package_parts_exact": True, "single_text_replacement": True,
        "manual_row_xml_exact": True, "source_link_parts_exact": True,
        "style_rounding_breaks_signatures_deletions_exact": True,
        "all_scientific_workbooks_and_appendix_bytes_exact": True,
        "docx_sha256_before": data["baseline_files"][doc_relative]["sha256"],
        "docx_sha256_after": inventory[doc_relative]["sha256"],
        "hyperlink_targets": links, "local_link_targets_resolve": all(x["resolved_exists"] for x in links if x["local"])
    }
    record(data, "binary_preservation_verification", package_read_count=2, hash_read_count=len(inventory),
           unchanged_files=len(inventory)-1, changed_files=1, hyperlinks=len(links))
    save(data)
    print(json.dumps({k:v for k,v in data["preservation"].items() if k != "hyperlink_targets"}, ensure_ascii=False))

def render():
    data = load()
    renderer = Path("C:/Users/idoca/.codex/plugins/cache/openai-primary-runtime/documents/26.915.20218/skills/documents/render_docx.py")
    python = Path("C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe")
    target = QA / "packaged_render"
    start = time.monotonic()
    cmd = [str(python), "-B", str(renderer), str(DOC), "--output_dir", str(target), "--emit_pdf", "--verbose"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = RUN / "qa/old_word_packaged_render.log"
    log.write_text(p.stdout + p.stderr, encoding="utf-8")
    record(data, "packaged_render_attempt", timestamp_start=now(), exit_code=p.returncode,
           seconds=time.monotonic()-start, command=cmd, log=str(log),
           produced_pages=len(list(target.glob("page-*.png"))), render_attempt_count=1)
    save(data)
    print(p.stdout + p.stderr)
    print(json.dumps({"exit_code":p.returncode, "log":str(log)}))

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["init", "edit", "verify", "render"])
args = parser.parse_args()
globals()[args.mode]()
