"""Add an optional group stack to the existing trend chart and its exports."""
from pathlib import Path

from tools.project_core.maps.trend_extras_layout import replace_once


def group_contributions_layout(text):
    if 'const SERIES_DB=' not in text:
        return text
    script = Path(__file__).with_name('group_contributions.js').read_text('utf-8')
    text = replace_once(text, '/* Additional trend views reuse the existing selected-model calculations. */',
                        '/* Additional trend views reuse the existing selected-model calculations. */\n' + script)
    text = replace_once(text, '<div class="field"><label for="globalApproximation">',
                        '<div class="field"><label for="groupDisplay">Plot</label><select id="groupDisplay" aria-describedby="groupDisplayNote"><option value="total">Total</option><option value="groups">Top 5 groups + Other</option></select></div>\n      <div class="field"><label for="globalApproximation">')
    text = replace_once(text, '  <div class="context">',
                        '  <div class="context"><p id="groupDisplayNote" hidden></p>')
    text = replace_once(text, '  let regionTable;',
                        "  let regionTable;\n  state.group_display=params.get('group_display')==='groups'?'groups':'total';")
    text = replace_once(text, "  $('regionReviewFilter').value=state.review_filter;",
                        "  $('regionReviewFilter').value=state.review_filter;\n  $('groupDisplay').value=state.group_display;")
    text = replace_once(text, "    p.set('table_year',state.table_year);",
                        "    p.set('table_year',state.table_year);\n    if(state.group_display==='groups')p.set('group_display','groups');")
    text = replace_once(text, '    focus=result.points.findIndex', '''    const groupCompatible=PPRGroupContributions.compatible(state);
    if(state.group_display==='groups'&&groupCompatible)result.group_breakdown=PPRGroupContributions.build(db,selection,result);
    $('groupDisplay').disabled=!groupCompatible;
    $('groupDisplay').title=groupCompatible?'Rank groups by cumulative included PPR over the displayed years.':'Choose one PPR method without a baseline to see group contributions.';
    $('groupDisplayNote').hidden=state.group_display!=='groups';
    $('groupDisplayNote').textContent=!groupCompatible?$('groupDisplay').title:'Top five included model groups by cumulative PPR over '+state.from+'–'+state.to+'. Other combines the remaining contributions. All layers use the same denominator and sum to the total curve. Unchecking groups recalculates the ranking; original catch allocations are retained.';
    if(result.group_breakdown?.has_unattributed)$('groupDisplayNote').textContent+=' Other also includes retained PPR without compatible group attribution.';
    if(result.group_breakdown&&PPRGroupContributions.bounds(result.group_breakdown).some(v=>v<0))$('groupDisplayNote').textContent+=' Signed diagnostic contributions stack above and below zero; their net sum is the total curve.';
    focus=result.points.findIndex''')
    text = replace_once(text, "    const values=result.series.flatMap(s=>s.points.flatMap(p=>assessedSensitivity(p)?[p.value,p.sensitivity.upper]:[p.value])).filter(finite),max=values.length?Math.max(...values):1;",
                        "    const values=[...result.series.flatMap(s=>s.points.flatMap(p=>assessedSensitivity(p)?[p.value,p.sensitivity.upper]:[p.value])),...PPRGroupContributions.bounds(result.group_breakdown)].filter(finite),max=values.length?Math.max(...values):1;")
    text = replace_once(text, "    result.series.forEach((series,index)=>{\n      const style=lineStyle(index),group=svg('g'",
                        "    PPRGroupContributions.draw(result.group_breakdown,{chart,svg,x,y});\n    result.series.forEach((series,index)=>{\n      const style=lineStyle(index),group=svg('g'")
    text = replace_once(text, "    $('seriesLegend').hidden=!multiple;", '''    const breakdown=result.group_breakdown;
    $('seriesLegend').hidden=!multiple&&!breakdown?.available;
    if(breakdown?.available)$('seriesLegend').replaceChildren(...breakdown.layers.map(layer=>{
      const value=layer.points[focus].value,item=element('div',null,'series-key'),key=svg('svg',{width:26,height:10,viewBox:'0 0 26 10','aria-hidden':'true'});
      key.appendChild(svg('rect',{x:0,y:0,width:26,height:10,fill:layer.color}));
      const text=element('div');text.appendChild(element('b',layer.label));
      text.appendChild(element('output',displayValue(value)+(finite(value)&&p.value>0?' · '+fmt(100*value/p.value)+'% of total':'')));
      item.append(key,text);return item;
    }));''')
    text = replace_once(text, "  $('globalApproximation').addEventListener('change'",
                        "  $('groupDisplay').addEventListener('change',()=>{state.group_display=$('groupDisplay').value;update();});\n  $('globalApproximation').addEventListener('change'")
    text = replace_once(text, 'PPRTimeSeries.comparisonToCSV(result,state)',
                        'PPRGroupContributions.toCSV(result,state,PPRTimeSeries.comparisonToCSV)')
    return text
