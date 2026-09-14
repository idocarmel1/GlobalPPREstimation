"""Human-readable archive navigation with short relative paths."""
from html import escape as esc

def archive_index(db):
    parts=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ecopath source archive</title><style>body{font:15px system-ui;margin:0;background:#eef5f7;color:#14354a}header{background:#0b4657;color:white;padding:28px}main{max-width:1000px;margin:auto;padding:24px}a{color:#087d89}header a{color:#bcebea}input{width:95%;padding:14px;border:1px solid #bbcfd6;border-radius:7px;font:inherit}details{background:white;padding:16px;margin:10px 0;border-radius:8px;border:1px solid #dce8ee}summary{cursor:pointer;font-weight:650}article{border-top:1px solid #ddd;margin-top:18px;padding-top:8px}small{color:#526c7b}li{margin:6px 0}.file{display:inline-block;background:#e2f3f3;padding:7px;margin:3px;border-radius:5px}h2{font-size:17px}</style><header><h1>Ecopath source archive</h1><p>167 selected ecosystems · LME, EEZ and High Seas</p><a href="../index.html">Return to the interactive map</a></header><main><p>Study relevance, file availability, and a working Ecopath model are separate questions. Whole-EEZ, subregional and basin-proxy assignments are labeled below. No model was load-tested in this project.</p><p><a href="../data/articles.csv">Article catalog CSV</a> · <a href="../data/eez_searches.csv">EEZ search log CSV</a> · <a href="../data/files.csv">File manifest CSV</a></p><input id="search" placeholder="Filter ecosystem, article, or author" aria-label="Filter archive">''']
    for r in db['regions']:
        related=[a for a in db['articles'] if a['unit_id']==r['unit_id']]
        rank=r['ppr_rank'] or '—'
        parts.append(f'<details><summary>#{rank} {esc(r["region_name"])} <small>{r["unit_id"]} · {len(related)} studies</small></summary><p>{esc(r.get("search_notes",r["search_status"]))}</p>')
        for a in related:
            parts.append(f'<article><h2>{esc(a["title"])}</h2><p>{esc(str(a.get("authors","")))} · {a.get("publication_year","")}</p><p><b>{esc(a["coverage_class"])}</b> — {esc(a.get("coverage_note",a.get("recommendation","")))}</p><p>Quality: {a["quality_score_100"]}/100. {esc(a.get("quality_rationale",""))}</p><a href="{esc(a.get("landing_page") or "",quote=True)}" target="_blank" rel="noopener">Public source ↗</a><p>')
            for f in a['material_files']:
                parts.append(f'<a class="file" href="../{esc(f["relative_path"],quote=True)}" target="_blank">{esc(f.get("file_label") or f["role"])} · {esc(f["filename"])}</a>')
            if not a['material_files']:parts.append('No verified local source file. See retrieval log for actual attempts.')
            parts.append('</p></article>')
        if not related:parts.append('<p>No defensible recommended model located. This does not establish that no unpublished or unindexed model exists.</p>')
        parts.append('</details>')
    parts.append("</main><script>document.querySelector('#search').addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('details').forEach(d=>d.hidden=!d.textContent.toLowerCase().includes(q))})</script></html>")
    return ''.join(parts)
