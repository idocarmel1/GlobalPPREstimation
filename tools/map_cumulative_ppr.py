"""Add cumulative PPR coverage to the active map without changing saved inputs."""

LIST_START = 'renderList = function() {'
LIST_END = 'const originalDetails=renderDetails;'
LIST_LAYOUT = '''renderList = function() {
  $('regionList').replaceChildren();
  // Display filters affect the running numerator, never the chosen-set total.
  const validPpr=r=>typeof r.networkResult?.value==='number'&&Number.isFinite(r.networkResult.value)&&r.networkResult.value>=0;
  const total=metricState.mode==='ppr'?regions.filter(r=>r.inRankingSet&&validPpr(r)).reduce((sum,r)=>sum+r.networkResult.value,0):0;
  let cumulative=0;
  regions.filter(passRegion).forEach(r=>{
    let coverage='';
    if(metricState.mode==='ppr'){
      const available=validPpr(r)&&total>0;
      if(available)cumulative+=r.networkResult.value;
      const text=available?`${pct(Math.min(1,cumulative/total))} cumulative PPR`:'Cumulative PPR unavailable';
      coverage=`<br><small title="Running PPR of listed ecosystems / PPR of the entire selected ecosystem set">${text}</small>`;
    }
    const b=document.createElement('button');b.className='region-btn'+(selectedId===r.unit_id?' active':'');
    b.innerHTML=`<span class="rank" style="background:${pprColor(r)}">${r.ppr_rank??'–'}</span><span><b>${r.region_name}</b><br><small>${resultText(r)}</small>${coverage}</span>`;
    b.onclick=()=>selectRegion(r.unit_id);$('regionList').appendChild(b);
  });
};
'''


def cumulative_ppr_layout(text):
    """Apply only to the map; trends and scientific result data stay untouched."""
    start = text.find(LIST_START)
    if start < 0:
        return text
    end = text.index(LIST_END, start)
    text = text[:start] + LIST_LAYOUT + text[end:]
    return text.replace(
        'Ranks and cumulative shares use the full chosen ecosystem set; display limits and other filters do not change them.',
        'Ranks use the full chosen ecosystem set. List cumulative PPR adds the displayed ecosystems relative to the entire set under the current method and calculation settings; filtered lists may finish below 100%.')
