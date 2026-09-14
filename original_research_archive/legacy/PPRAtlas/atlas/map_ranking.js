/* Rank the full chosen geography; display limits never change the denominator. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.PPRMapRanking=api;
})(typeof globalThis==='object'?globalThis:this,function(){
  const finite=value=>typeof value==='number'&&Number.isFinite(value)&&value>=0;
  function rank(regions,ids){
    for(const r of regions){
      r.inRankingSet=ids===null||ids.has(r.unit_id);
      r.ppr_rank=null;r.rank_position=null;r.global_ppr_share=null;
      r.cumulative_ppr_share=null;r.cumulative_before_share=null;
    }
    regions.sort((a,b)=>Number(b.inRankingSet)-Number(a.inRankingSet)||
      Number(finite(b.networkResult?.value))-Number(finite(a.networkResult?.value))||
      (b.networkResult?.value||0)-(a.networkResult?.value||0)||a.unit_id.localeCompare(b.unit_id));
    const members=regions.filter(r=>r.inRankingSet),available=members.filter(r=>finite(r.networkResult?.value));
    const total=available.reduce((sum,r)=>sum+r.networkResult.value,0);
    let cumulative=0;
    for(let start=0;start<available.length;){
      let end=start+1;
      const value=available[start].networkResult.value,before=total?cumulative/total:0;
      while(end<available.length&&available[end].networkResult.value===value)end++;
      cumulative+=value*(end-start);
      for(let i=start;i<end;i++)Object.assign(available[i],{
        ppr_rank:start+1,rank_position:i+1,global_ppr_share:total?value/total:0,
        cumulative_before_share:before,cumulative_ppr_share:total?Math.min(1,cumulative/total):0
      });
      start=end;
    }
    return {total,available:available.length,size:members.length,
      extent:available.length?[available[available.length-1].networkResult.value,available[0].networkResult.value]:[0,1]};
  }
  function visible(region,limit,custom){
    if(!region.inRankingSet)return false;
    if(limit==='all')return true;
    const count=Number(limit==='custom'?custom:limit);
    return Number.isSafeInteger(count)&&count>0&&region.rank_position!==null&&region.rank_position<=count;
  }
  return {rank,visible};
});
