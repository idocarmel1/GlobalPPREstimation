"""Bounded controls and table additions to the retained trend-page layout."""
from pathlib import Path


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Trend controls anchor changed: ' + old[:100])
    return text.replace(old, new, 1)


def trend_extras_layout(text):
    if 'const SERIES_DB=' not in text:
        return text
    directory = Path(__file__).parent
    script = '\n'.join((directory / name).read_text('utf-8') for name in
                       ['trend_extras.js', 'regional_results_table.js'])
    text = replace_once(text, '<script>/* Shared annual denominator lookup.',
                        '<script>' + script + '\n/* Shared annual denominator lookup.')
    anchor = '<div class="field treatment group-filter-launch"><button id="openGroupFilter" type="button" aria-haspopup="dialog">Choose model groups</button><small id="groupFilterSummary">All model groups included</small></div>'
    text = replace_once(text, anchor, anchor + '''
      <div class="field"><label for="regionReviewFilter">Regions to include</label><select id="regionReviewFilter"><option value="all">All selected regions</option><option value="validated">Selected regions with validated models</option></select></div>
      <div class="field"><label for="globalApproximation">Global approximation</label><select id="globalApproximation"><option value="0">Off</option><option value="1">Scale by selected simple-chain share</option></select></div>''')
    text = replace_once(text, '  <div class="context">', '''  <section class="region-results" aria-labelledby="regionTableTitle">
    <div class="region-table-heading"><h2 id="regionTableTitle">Annual values by region</h2><label for="regionTableYear">Year <select id="regionTableYear"></select></label></div>
    <p id="regionTableNote"></p><div class="region-table-scroll"><table aria-label="Annual values by region and selected method" aria-describedby="regionTableNote"><thead id="regionTableHead"></thead><tbody id="regionTableBody"></tbody><tfoot id="regionTableFoot"></tfoot></table></div>
  </section>
  <div class="context">''')
    text = replace_once(text, '</head>', '''<style>.region-results{margin:24px 0;background:white;border:1px solid var(--line);border-radius:12px;overflow:hidden}.region-table-heading{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 24px 0}.region-table-heading h2{font-size:18px;margin:0}.region-table-heading label{display:flex;align-items:center;gap:8px}.region-table-heading select{padding:6px;border:1px solid var(--line);border-radius:5px;background:white}.region-results>p{margin:12px 24px 18px;color:var(--muted);font-size:12px;line-height:1.6}.region-table-scroll{overflow:auto;max-height:500px}.region-results table{border-collapse:separate;border-spacing:0;width:100%;font-size:12px;font-variant-numeric:tabular-nums}.region-results th,.region-results td{padding:10px 14px;border-top:1px solid var(--line);text-align:right;white-space:nowrap}.region-results th:first-child{text-align:left}.region-results thead{position:sticky;top:0;background:var(--light)}.region-results tbody th{font-weight:500}.region-results tfoot{background:var(--light);font-weight:700}.region-results td small{display:block;color:var(--muted);font-size:10px}.region-unavailable{color:var(--muted)}
</style></head>''')
    text = replace_once(text, '  state.group_selections=groupStore?.data.selections||{};', '''  state.group_selections=groupStore?.data.selections||{};
  state.review_filter=params.get('region_review')==='validated'?'validated':'all';
  state.table_year=Number(params.get('table_year')||params.get('year')||db.years.at(-1));
  state.global_estimate=params.get('global_estimate')==='1';
  const calculationState=()=>({...state,units:PPRTrendExtras.selectedUnits(db,state)});
  let regionTable;''')
    text = replace_once(text, "  $('nppScope').value=state.npp_scope;", "  $('nppScope').value=state.npp_scope;\n  $('regionReviewFilter').value=state.review_filter;\n  $('globalApproximation').value=state.global_estimate?'1':'0';")
    text = replace_once(text, "    p.set('metric',state.mode);methodParams(p);", "    if(state.review_filter==='validated')p.set('region_review','validated');\n    p.set('table_year',state.table_year);\n    p.set('metric',state.mode);methodParams(p);")
    text = replace_once(text, '    result=PPRTimeSeries.compare(db,state);', '    const selection=calculationState();\n    result=PPRTrendExtras.scale(db,selection,PPRTimeSeries.compare(db,selection),PPRTimeSeries.aggregate);')
    text = replace_once(text, "    p.set('table_year',state.table_year);", "    p.set('table_year',state.table_year);\n    if(state.global_estimate)p.set('global_estimate','1');")
    text = replace_once(text, "  const usesModels=()=>state.mode!=='npp'&&", "  const usesModels=()=>state.review_filter==='validated'||state.mode!=='npp'&&")
    text = replace_once(text, "    if(!nppOnly&&state.unidentified!=='method')", "    $('globalApproximation').disabled=!ratio||!globalNPP||result.normalized;\n    $('globalApproximation').title='Available for PPR / NPP with global atlas NPP and no method baseline. Requires a complete fixed atlas simple-chain reference.';\n    if(result.global_estimate)$('chartTitle').textContent=catchBasisLabel()+' · Approximate global PPR / atlas NPP';\n    if(!nppOnly&&state.unidentified!=='method')")
    text = replace_once(text, '    renderCoverage();draw();saveURL();', '    renderCoverage();draw();regionTable?.render();saveURL();')
    text = replace_once(text, "  $('ecosystemSearch').addEventListener('input',renderPicker);", "  $('ecosystemSearch').addEventListener('input',renderPicker);\n  $('regionReviewFilter').addEventListener('change',()=>{state.review_filter=$('regionReviewFilter').value;update();if($('ecosystemDialog').open)renderPicker();});")
    text = replace_once(text, "  $('regionReviewFilter').addEventListener", "  $('globalApproximation').addEventListener('change',()=>{state.global_estimate=$('globalApproximation').value==='1';update();});\n  $('regionReviewFilter').addEventListener")
    text = replace_once(text, "    $('pickerCount').textContent=`${state.units.length} selected · ${rows.length} visible`;", "    $('pickerCount').textContent=`${state.units.length} selected · ${rows.length} visible`+(state.review_filter==='validated'?` · ${PPRTrendExtras.selectedUnits(db,state).length} have validated selected models`:'');")
    text = replace_once(text, "    if(!nppOnly&&state.methods.length>1)$('cohortSummary').textContent+=' · Same ecosystems across available curves';", "    if(result.independent_availability)$('cohortSummary').textContent=`${result.selected} selected regions · Each method uses its available results in each year`;\n    else if(!nppOnly&&state.methods.length>1)$('cohortSummary').textContent+=' · Same ecosystems across available curves';\n    if(state.review_filter==='validated')$('cohortSummary').textContent+=` · Validated selected models only (${result.selected} of ${state.units.length} selected regions)`;")
    text = replace_once(text, "    if(!nppOnly&&(state.methods.length>1 || result.normalized))$('calculationNote').textContent+=' Available curves use the same ecosystems; the catch taxa covered by each method may differ.';", "    if(result.independent_availability)$('calculationNote').textContent+=' Each method independently uses the available selected ecosystem-year results. Adding another method does not alter existing curves. Missing results are listed below.';\n    else if(!nppOnly&&(state.methods.length>1 || result.normalized))$('calculationNote').textContent+=' Available curves use the same ecosystems; the catch taxa covered by each method may differ.';")
    text = replace_once(text, "'PPR and NPP use the same fixed ecosystem cohort.'", "result.independent_availability?'Each method uses matching regional PPR and NPP for its available ecosystems in that year.':'PPR and NPP use the same fixed ecosystem cohort.'")
    text = replace_once(text, "    if(result.normalized)$('calculationNote')", "    if(result.global_estimate)$('calculationNote').textContent+=' Global approximation (%) = (100 × selected PPR / fixed global atlas NPP) ÷ (selected simple-chain PPR / fixed atlas simple-chain PPR). The selected simple-chain total uses the same included groups. Every reference region and every selected region for the chosen method must have a value; missing or nonpositive simple-chain totals leave the approximation unavailable. This extrapolation assumes the selected set represents the reference and does not remove boundary overlaps or NPP coverage limits.';\n    if(result.normalized)$('calculationNote')")
    text = replace_once(text, "    const unavailable=result.series.filter", "    if(result.independent_availability){const support=element('div');support.id='methodYearAvailability';excluded.appendChild(support);}\n    const unavailable=result.series.filter")
    text = replace_once(text, "    const descriptions=result.series.map", "    const support=$('methodYearAvailability');\n    if(support){support.replaceChildren(element('h3',`${p.year} · Availability by method`));for(const series of result.series){const point=series.points[focus],details=element('details');details.appendChild(element('summary',`${methodLabel(series.method)} · ${point.included_count??series.included.length} included, ${point.missing_result_count??0} missing`));const list=element('ul');for(const item of point.excluded||[])list.appendChild(element('li',`${item.name} (${item.id}) · ${item.reason}`));if(!(point.excluded||[]).length)list.appendChild(element('li','No missing regional results.'));if(point.status&&point.status!=='ok')list.appendChild(element('li','Retained result flags: '+point.status));if(point.scaling_reason)list.appendChild(element('li',point.scaling_reason));details.appendChild(list);support.appendChild(details);}}\n    const descriptions=result.series.map")
    # Keep export column order stable, appending the optional interpretation only.
    text = text.replace("',result_status,diagnosis_flags,missing_result_count,excluded_results,retained_numeric_display';", "',result_status,diagnosis_flags,missing_result_count,excluded_results,retained_numeric_display'+(state.global_estimate?PPRTrendExtras.csvHeader:'');")
    for point in ('p', 'point'):
        text = replace_once(text, point + '.retained_numeric_display||false].map(escape)', point + '.retained_numeric_display||false,...(state.global_estimate?PPRTrendExtras.csv(' + point + '):[])].map(escape)')
    text = replace_once(text, '  update();\n})();', '''  regionTable=PPRRegionTable.create({db,getState:()=>state,
    calculate:year=>PPRTrendExtras.table(db,state,year,PPRTimeSeries.compare,PPRTimeSeries.aggregate),methodLabel,save:saveURL});
  update();
})();''')
    return text
