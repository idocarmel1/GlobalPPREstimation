"""Verify model-specific Markdown links, including parentheses in filenames."""
from pathlib import Path
import json
import re

E = Path(__file__).resolve().parent
source = (E / "reports_index.md").read_text(encoding="utf-8")
targets = []
for match in re.finditer(r"\]\(",source):
    start = match.end()
    depth = 1
    end = start
    while end < len(source) and depth:
        if source[end] == "(":
            depth += 1
        elif source[end] == ")":
            depth -= 1
        end += 1
    assert depth == 0
    target = source[start:end-1]
    assert "://" not in target and not Path(target).is_absolute()
    path = (E/target).resolve()
    assert path.is_file(),target
    targets.append({"target":target,"exists":True,"portable_relative":True})
result = {"all_links_resolve":True,"link_count":len(targets),"links":targets}
(E/"report_index_link_verification.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"all_links_resolve":True,"link_count":len(targets)}))
