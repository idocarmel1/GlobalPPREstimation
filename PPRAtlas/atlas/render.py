"""Extend the supplied map template while preserving its layout and palette."""
import html, json, re

YEAR_SCRIPT = r'''
function applyYear(year){
  DB.year=Number(year); const annual=DB.annual[String(year)];
  regions.forEach(r=>{const v=annual[r.unit_id];r.ppr_species_2019=v[0];r.total_catch_tonnes=v[1];r['data availability']=v[2]});
  regions.sort((a,b)=>(a.ppr_species_2019===null)-(b.ppr_species_2019===null)||(b.ppr_species_2019||0)-(a.ppr_species_2019||0)||a.unit_id.localeCompare(b.unit_id));
  const total=regions.reduce((sum,r)=>sum+(r.ppr_species_2019||0),0);let cumulative=0,prior=null,rank=null;
  regions.forEach((r,i)=>{const v=r.ppr_species_2019;if(v===null){r.ppr_rank=null;r.global_ppr_share=null;r.cumulative_ppr_share=null;return}if(v!==prior)rank=i+1;prior=v;cumulative+=v;r.ppr_rank=rank;r.global_ppr_share=total?v/total:0;r.cumulative_ppr_share=total?cumulative/total:0});
  regionGroup.clearLayers();markerGroup.clearLayers();regions.forEach(addRegion);
  document.querySelector('#yearTotal').textContent=`${num(total)} t PP equivalent · ${regions.filter(r=>r.ppr_species_2019===null).length} region(s) missing`;
  if(selectedId)renderDetails(regionById[selectedId]);refresh();
}
const yearSelect=document.querySelector('#yearFilter');Object.keys(DB.annual).sort().reverse().forEach(year=>{const o=document.createElement('option');o.value=year;o.textContent=year;o.selected=Number(year)===DB.year;yearSelect.appendChild(o)});
yearSelect.addEventListener('change',()=>applyYear(yearSelect.value));
applyYear(DB.year);
'''

def render_map(root, db):
    template=(root/'inputs/original_map.html').read_text(encoding='utf-8')
    prefix,remaining=template.split('const DB=',1)
    _,end=json.JSONDecoder().raw_decode(remaining)
    text=prefix+'const DB='+json.dumps(db,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('</',r'<\/')+remaining[end:]
    replacements={
        'All 84 PPR Units':'167 Selected Ecosystems',
        'All 84 LME and high-seas production units · curated for extraction readiness':'66 LMEs · 84 EEZs · 17 High Seas regions · Global Estimation set',
        '<span>Global PPR</span>':'<span>Selected ecosystems</span>',
        '<span>Article packages</span>':'<span>Study assignments</span>',
        '<span>Units with models</span>':'<span>Units with sources</span>',
        '<option value="all">LME + High Seas</option>':'<option value="all">All region types</option><option value="EEZ">EEZ only</option>',
        '<option value="84" selected>All 84</option>':'<option value="167" selected>All 167</option><option value="50">Top 50</option><option value="100">Top 100</option>',
        'Cumulative global PPR — ranked circles':'Cumulative selected PPR — ranked circles',
        "function pprColor(r){const t=":"function pprColor(r){if(r.ppr_rank===null)return '#9aa9b1';const t=",
        "const pct=v=>`${(Number(v)*100).toFixed(v<.01?1:0)}%`, num=v=>Number(v).toLocaleString(undefined,{maximumFractionDigits:0});":"const pct=v=>v==null?'unknown':`${(Number(v)*100).toFixed(v<.01?1:0)}%`, num=v=>v==null?'Missing':Number(v).toLocaleString(undefined,{maximumFractionDigits:0});",
        'function addArticle(a){const q=':'function addArticle(a){if(!a.geometry)return;const q=',
        'const n=String(r.ppr_rank),':'const n=r.ppr_rank===null?\'—\':String(r.ppr_rank),',
        'return r.ppr_rank<=rank&&':"return (rank===167||(r.ppr_rank!==null&&r.ppr_rank<=rank))&&",
        "articles.filter(a=>passArticle(a)&&passRegion(regionById[a.unit_id])).forEach(a=>articleLayers[a.article_id].addTo(articleGroup));":"articles.filter(a=>a.geometry&&passArticle(a)&&passRegion(regionById[a.unit_id])).filter((a,i,all)=>all.findIndex(b=>b.footprint_key===a.footprint_key)===i).forEach(a=>articleLayers[a.article_id].addTo(articleGroup));",
        "if(selectedId&&(!regionById[selectedId]||!passRegion(regionById[selectedId])))selectedId=null;":"if(selectedId&&(!regionById[selectedId]||!passRegion(regionById[selectedId]))){selectedId=null;document.querySelector('#details').innerHTML='<p>Select a region from the filtered results.</p>'}",
        '<span class="rank" style="background:${pprColor(r)};color:${t<.24||t>.76?\'white\':\'#1e2830\'}">${r.ppr_rank}</span>':'<span class="rank" style="background:${pprColor(r)};color:${t<.24||t>.76?\'white\':\'#1e2830\'}">${r.ppr_rank??\'—\'}</span>',
        '<span>PPR 2019</span>':'<span>PPR ${DB.year}</span>',
        '<span>Global share</span>':'<span>Selected-set share</span>',
        '${a.recommendation}</div>':'${a.recommendation}<br><b>Coverage:</b> ${a.coverage_class}<br><b>Boundary:</b> ${a.geometry_method}</div>',
        '<button onclick="highlightArticle(\'${a.article_id}\')">Show area</button>':'${a.geometry?`<button onclick="highlightArticle(\'${a.article_id}\')">Show area</button>`:\'<span class="chip">Study boundary unavailable</span>\'}${fileLinks(a)}',
        'Web and Zotero searches found background ecosystem sources but no defensible extractable model. This is a documented gap, not evidence that no unpublished model exists.':'${r.search_notes||\'The inherited catalog contains no recommended Ecopath model for this region.\'} This is a documented search gap, not evidence that no model exists.',
        "document.querySelector('#kpiPpr').textContent='100%';":"document.querySelector('#kpiPpr').textContent=regions.length;",
        "files.filter(f=>String(f.status).includes('verified')).length":"new Set(files.filter(f=>f.status==='downloaded_verified').map(f=>f.sha256)).size",
        "refresh();\n</script>":YEAR_SCRIPT+'\n</script>',
    }
    for before,after in replacements.items():
        if before not in text:raise ValueError('Map template fragment not found: '+before[:100])
        text=text.replace(before,after)
    marker='<div class="section-title">Filters</div>'
    text=text.replace(marker,'''<div class="section-title">PPR year</div><div class="field"><select id="yearFilter" aria-label="PPR year"></select></div><p id="yearTotal" style="font-size:11px;color:#647b8b"></p><p style="font-size:10px;color:#647b8b">Whole-region PPR sum at TE=0.1. Residual overlap is retained; shares are not unique global coverage. Gray markers indicate missing data.</p>'''+marker)
    text=text.replace("const regionById=", "function fileLinks(a){return (a.material_files||[]).map(f=>`<a href=\"${f.relative_path}\" target=\"_blank\" rel=\"noopener\">${f.role} file ↗</a>`).join('')}\nconst regionById=")
    text=text.replace('.actions{display:flex;gap:6px;', '.actions{display:flex;flex-wrap:wrap;gap:6px;')
    text=text.replace('width:25px;height:25px','width:29px;height:29px').replace('grid-template-columns:27px 1fr auto','grid-template-columns:31px 1fr auto')
    text=text.replace('height:22px;width:22px','height:27px;width:27px')
    text=text.replace('${r.search_status}', '${label(r.search_status)}').replace('${a.coverage_class}', '${label(a.coverage_class)}')
    text=text.replace("const regionById=", "function label(v){return ({whole_eez:'Whole EEZ',whole_lme:'Whole LME',subregional:'Part of region',basin_proxy:'Ocean-basin proxy',proxy_only:'Proxy studies only',direct_model_found:'Regional study found',partial_model_found:'Local study found',no_defensible_model_found:'No suitable model found',geographic_assignment_unverified:'Geographic assignment unverified'})[v]||v}\nconst regionById=")
    text=text.replace('· est. ${pct(a.target_coverage_ratio)} of target',"· ${a.target_coverage_ratio==null?'Coverage not quantified':'est. '+pct(a.target_coverage_ratio)+' of target'}")
    text=text.replace('<b>Boundary rule.</b>', '<b>Model loading.</b> No model was load-tested in this project.<br><br><b>Boundary rule.</b>')
    text=text.replace('${f.role} file ↗', "${f.file_label||(f.material_kind==='related_thesis'?'Related thesis':f.material_kind==='author_manuscript'?'Author manuscript':f.material_kind==='related_report'?'Related report':f.role.replace('_',' ')+' '+f.relative_path.split('.').pop().toUpperCase())} ↗")
    text=text.replace('${r.ppr_rank}',"${r.ppr_rank??'—'}")
    text=text.replace('zoomControl:true,minZoom:2}).setView([12,10],2)','zoomControl:true,minZoom:1}).setView([12,10],1)')
    text=text.replace("toFixed(v<.01?1:0)","toFixed(2)")
    text=text.replace('<div class="section-title">PPR-ranked units</div>','<p style="font-size:11px"><a href="archive/index.html" target="_blank">Browse article archive</a> · <a href="data/eez_searches.csv">EEZ searches</a> · <a href="data/lme_searches.csv">LME searches</a></p><div class="section-title">PPR-ranked units</div>')
    return text
