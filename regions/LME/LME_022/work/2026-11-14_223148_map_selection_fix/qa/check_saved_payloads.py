"""Check that a presentation refresh preserves every embedded scientific value."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path.cwd()
OUT = Path(__file__).parent


def digest(value):
    return hashlib.sha256(value).hexdigest()


def snapshot():
    result = {"Project.xlsx": digest((ROOT / "Project.xlsx").read_bytes()), "pages": {}}
    for name, variable in [("index.html", "DB"), ("trends.html", "SERIES_DB")]:
        page = (ROOT / "interactive_map" / name).read_text("utf-8")
        start = page.index("const " + variable + "=") + len("const " + variable + "=")
        payload, end = json.JSONDecoder().raw_decode(page, start)
        units = payload["network"]["units"] if variable == "DB" else payload["units"]
        focus = {}
        for key in ["LME_022", "LME_038"]:
            unit = units[key]
            default = unit["default_model"]
            model = unit["models"][default] if isinstance(default, int) else next(m for m in unit["models"] if m["id"] == default)
            assert model["researcher_review"]["status"] == "Validated by researcher", (name, key)
            if key == "LME_022":
                assert model["id"] == "ICES_WGSAM2015_North_Sea_1991", model["id"]
            focus[key] = {"default_model": model["id"], "review": model["researcher_review"]["status"]}
        embedded = re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">', page).group(1)
        assert embedded == result["Project.xlsx"]
        result["pages"][name] = {"payload_sha256": digest(page[start:end].encode("utf-8")), "project_fingerprint": embedded, "focus": focus}
    result["sources.html"] = digest((ROOT / "interactive_map/sources.html").read_bytes())
    return result


current = snapshot()
baseline = OUT / "saved_payloads_before.json"
if "--before" in sys.argv:
    if baseline.exists():
        raise SystemExit("Baseline already exists; refusing to replace it")
    baseline.write_text(json.dumps(current, indent=2) + "\n", "utf-8")
else:
    assert current == json.loads(baseline.read_text("utf-8")), "Saved payload or project content changed"
    (OUT / "saved_payloads_after.json").write_text(json.dumps(current, indent=2) + "\n", "utf-8")
print(json.dumps(current, indent=2))
