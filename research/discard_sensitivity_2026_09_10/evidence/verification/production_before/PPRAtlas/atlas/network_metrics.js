/* Pure calculations shared by the atlas and regression tests. */
const PPRMetrics = (() => {
  const annualNPP=typeof module==='object' && module.exports?require('./annual_npp.js'):globalThis.PPRAnnualNPP;
  const finite = v => typeof v === 'number' && Number.isFinite(v);
  const empty = reason => ({value:null, coverage:null, catch:null, status:reason});
  function evaluate(unit, modelIndex, state) {
    if (!unit) return empty('No selected article in the pilot');
    const model = unit.models[modelIndex];
    if (!model) return empty('No extracted model');
    if (state.mode === 'b' || state.mode === 'rho_living') {
      const h = model.health?.[state.te];
      return h && finite(h[state.mode]) ? {...h,value:h[state.mode],coverage:null,catch:null}
        : empty('Diagnostic unavailable');
    }
    if (!model.verified) return empty('Mapping workbook not verified');
    if (state.mode === 'npp_ratio') {
      const ppr=evaluate(unit,modelIndex,{...state,mode:'ppr'});
      const data=state.npp_data||{};
      const npp=annualNPP.resolve(data.years||[],data.values,state.year,state.npp_fill,data.metadata);
      if(!finite(ppr.value))return {...ppr,npp};
      return {...ppr,npp,value:npp.value===null?null:100*ppr.value/npp.value,
        denominator:npp.value,status:npp.value===null?'Annual NPP unavailable':npp.substituted?`Estimated using ${npp.source_year} NPP`:'ok'};
    }
    const scope = model.scopes[state.scope];
    const yi = unit.years.indexOf(Number(state.year));
    if (!scope || yi < 0) return empty('Scope or year unavailable');
    const a = scope.methods.indexOf(state.method), b = scope.methods.indexOf(state.denominator);
    const ratio = state.mode === 'ratio';
    if (a < 0 || (ratio && b < 0)) return empty('Method unavailable in this scope');
    for (const method of ratio ? [state.method,state.denominator] : [state.method]) {
      if (scope.status[method] !== 'ok') return empty(method + ': ' + (scope.status[method] || 'unavailable'));
    }
    const treatment=state.unidentified||'method';
    if(!['method','zero','simple'].includes(treatment))return empty('Unknown unidentified-catch treatment');
    if(treatment==='simple' && state.scope!=='all')return empty('Reference-TL sensitivity is total-only; select All sources. No source decomposition is available.');
    if(treatment!=='method' && !unit.unidentified)return empty('Unidentified-catch sensitivity unavailable in this export');
    const affected=new Map((unit.unidentified?.taxa||[]).map(t=>[t.name,t]));
    let numerator=0, denominator=0, support=0, total=0, present=false,unidentifiedCatch=0,missingSimpleCatch=0;
    unit.catch.forEach((years,i) => {
      const c = years[yi] || 0, v = scope.values[i],residual=affected.get(unit.taxa?.[i]); total += c;
      if(residual){unidentifiedCatch+=c;if(!finite(residual.simple_sppr))missingSimpleCatch+=c;}
      const coefficient=j=>residual && treatment!=='method'?(treatment==='zero'?0:residual.simple_sppr):v?.[j];
      const av=coefficient(a),bv=coefficient(b);
      if (!c || !finite(av) || (ratio && !finite(bv))) return;
      numerator += c*av; denominator += ratio ? c*bv : 0;
      support += c; present = true;
    });
    if (!present) return empty('No catch with available method values');
    if (ratio && denominator === 0) return empty('Zero denominator on common catch');
    // Sources and SPPR stay in wet weight; every returned PPR mass is carbon.
    const value = ratio ? numerator / denominator : numerator / 9;
    return finite(value) ? {value,coverage:total ? support/total : null,catch:support,
      total_catch:total,unidentified_catch:unit.unidentified?unidentifiedCatch:null,unidentified_share:unit.unidentified && total?unidentifiedCatch/total:null,
      unidentified_missing_simple_catch:unit.unidentified?missingSimpleCatch:null,
      status:'ok',numerator:numerator / 9,denominator:ratio ? denominator / 9 : null} : empty('Non-finite result');
  }
  return {evaluate,finite};
})();
if (typeof module !== 'undefined') module.exports = PPRMetrics;
