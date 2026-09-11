/* Pure calculations shared by the atlas and regression tests. */
const PPRMetrics = (() => {
  const annualNPP=typeof module==='object' && module.exports?require('./annual_npp.js'):globalThis.PPRAnnualNPP;
  const sensitivity=typeof module==='object' && module.exports?require('./discard_sensitivity.js'):globalThis.PPRDiscardSensitivity;
  const groups=typeof module==='object' && module.exports?require('./group_metrics.js'):globalThis.PPRGroups;
  const finite = v => typeof v === 'number' && Number.isFinite(v);
  const totalAt=(matrix,index)=>Array.isArray(matrix)&&matrix.length&&matrix.every(row=>finite(row[index])&&row[index]>=0)?matrix.reduce((sum,row)=>sum+row[index],0):null;
  const empty = reason => ({value:null, coverage:null, catch:null, status:reason});
  function independentSimple(unit,state) {
    const source={independent_simple:true,sources:unit.sources||{},source_sha256:unit.source_sha256||{}};
    const unavailable=reason=>({...empty(reason),...source});
    const yi=(unit.years||[]).indexOf(Number(state.year));
    if(yi<0)return unavailable('Catch or year unavailable');
    const catchBasis=sensitivity.basis(state),treatment=state.unidentified||'method';
    if(!['catch','landings','discards'].includes(catchBasis))return unavailable('Unknown catch basis');
    if(!['method','zero','simple'].includes(treatment))return unavailable('Unknown unidentified-catch treatment');
    let record=treatment==='method'?unit.simple:unit.simple?.['unidentified_'+treatment];
    if(catchBasis!=='landings')record=record?.catch_bases?.[catchBasis];
    if(!record || (record.status && record.status!=='ok'))return unavailable('Simple PPR unavailable for this catch basis and treatment');
    const wet=record.ppr?.[yi],total=record.catch?.[yi],support=record.covered_catch?.[yi];
    if(![wet,total,support].every(v=>finite(v)&&v>=0) || (total>0&&support===0))
      return unavailable('No catch with available trophic-level values');
    const affected=unit.unidentified?.catch_bases?.[catchBasis]||unit.unidentified;
    const at=values=>finite(values?.[yi])?values[yi]:null;
    const unidentifiedCatch=at(affected?.catch),carbon=wet/9;
    const npp=state.mode==='npp_ratio'?annualNPP.resolve(state.npp_data?.years||[],state.npp_data?.values,state.year,state.npp_fill,state.npp_data?.metadata):null;
    const band=sensitivity.unavailable('External fixed taxon-TL benchmark; discard-routing ecological uncertainty is not assessed.');
    return {...source,value:npp?(npp.value===null?null:100*carbon/npp.value):carbon,
      numerator:carbon,denominator:npp?npp.value:null,...(npp?{npp}:{}),
      coverage:total>0?support/total:null,catch:support,total_catch:total,
      catch_basis:catchBasis,total_catch_all:at(unit.simple?.catch_bases?.catch?.catch),
      total_discards:at(unit.simple?.catch_bases?.discards?.catch),
      unidentified_catch:unidentifiedCatch,unidentified_share:total>0&&unidentifiedCatch!==null?unidentifiedCatch/total:null,
      unidentified_missing_simple_catch:at(affected?.missing_simple_catch),
      sensitivity:sensitivity.display(band,state,npp?.value),
      status:npp?(npp.value===null?'Annual NPP unavailable':npp.substituted?`Estimated using ${npp.source_year} NPP`:'ok'):'ok'};
  }
  function evaluate(unit, modelIndex, state) {
    if(state.mode==='npp'){
      const data=state.npp_data||{};
      const npp=annualNPP.resolve(data.years||[],data.values,state.year,state.npp_fill,data.metadata,{allowZero:true});
      return {value:npp.value,npp,coverage:null,catch:null,
        status:npp.value===null?'Annual NPP unavailable':npp.substituted?`Estimated using ${npp.source_year} NPP`:'ok'};
    }
    const selectedModel=unit?.models?.[modelIndex];
    const selectedGroups=selectedModel?state.group_selections?.[groups.key(state.unit_id,selectedModel)]:undefined;
    const groupSubset=groups.active(selectedModel,selectedGroups);
    if(!groupSubset && state.method==='simple trophic chain' && state.scope==='all' &&
      ['ppr','npp_ratio'].includes(state.mode) && state.simple_unit)return independentSimple(state.simple_unit,state);
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
        sensitivity:sensitivity.display(ppr.sensitivity,state,npp.value),
        denominator:npp.value,status:npp.value===null?'Annual NPP unavailable':ppr.status==='No groups selected'?ppr.status:npp.substituted?`Estimated using ${npp.source_year} NPP`:'ok'};
    }
    if(groupSubset){
      const result=groups.evaluate(unit,model,state,selectedGroups);
      return result.sensitivity?{...result,sensitivity:sensitivity.display(result.sensitivity,state)}:result;
    }
    const scope = model.scopes[state.scope];
    const yi = unit.years.indexOf(Number(state.year));
    if (!scope || yi < 0) return empty('Scope or year unavailable');
    const a = scope.methods.indexOf(state.method), b = scope.methods.indexOf(state.denominator);
    const ratio = state.mode === 'ratio';
    const catchBasis=sensitivity.basis(state);
    if(!['catch','landings','discards'].includes(catchBasis))return empty('Unknown catch basis');
    const catchValues=catchBasis==='catch'?(unit.full_precision_catch||unit.catch):unit[catchBasis];
    // Legacy fixtures/exports predate catch classification. New exports must have
    // all three components; a missing component must not become total catch.
    const evaluationCatch=catchValues||(!unit.catch_basis_policy?unit.catch:null);
    if(!evaluationCatch)return empty('Catch classification unavailable for this basis');
    if(evaluationCatch.some(row=>!finite(row[yi])||row[yi]<0))return empty('Catch amounts are missing or invalid for this basis and year');
    if (a < 0 || (ratio && b < 0)) return empty('Method unavailable in this scope');
    for (const method of ratio ? [state.method,state.denominator] : [state.method]) {
      const mcFailure=groups.mcAcceptanceFailure(model,method);
      if(mcFailure)return empty(mcFailure);
      if (scope.status[method] !== 'ok') return empty(method + ': ' + (scope.status[method] || 'unavailable'));
    }
    const treatment=state.unidentified||'method';
    if(!['method','zero','simple'].includes(treatment))return empty('Unknown unidentified-catch treatment');
    if(treatment==='simple' && state.scope!=='all')return empty('Reference-TL sensitivity is total-only; select All sources. No source decomposition is available.');
    if(treatment!=='method' && !unit.unidentified)return empty('Unidentified-catch sensitivity unavailable in this export');
    const affected=new Map((unit.unidentified?.taxa||[]).map(t=>[t.name,t]));
    let numerator=0, denominator=0, support=0, total=0, present=false,unidentifiedCatch=0,missingSimpleCatch=0;
    evaluationCatch.forEach((years,i) => {
      const c = years[yi], v = scope.values[i],residual=affected.get(unit.taxa?.[i]);
      if(!finite(c)||c<0)return;
      total += c;
      if(residual){unidentifiedCatch+=c;if(!finite(residual.simple_sppr))missingSimpleCatch+=c;}
      const coefficient=j=>residual && treatment!=='method'?(treatment==='zero'?0:residual.simple_sppr):v?.[j];
      const av=coefficient(a),bv=coefficient(b);
      if (!finite(av) || av<0 || (ratio && (!finite(bv)||bv<0))) return;
      numerator += c*av; denominator += ratio ? c*bv : 0;
      support += c; if(c>0||total===0)present = true;
    });
    // A supported zero vector has a true zero PPR. Positive catch with no
    // supported coefficient remains unavailable even if other rows contain zero.
    if(total>0&&support===0)present=false;
    if (!present) return empty('No catch with available method values');
    if (ratio && denominator === 0) return empty('Zero denominator on common catch');
    // Sources and SPPR stay in wet weight; every returned PPR mass is carbon.
    const value = ratio ? numerator / denominator : numerator / 9;
    return finite(value) ? {value,coverage:total ? support/total : null,catch:support,
      total_catch:total,unidentified_catch:unit.unidentified?unidentifiedCatch:null,unidentified_share:unit.unidentified && total?unidentifiedCatch/total:null,
      unidentified_missing_simple_catch:unit.unidentified?missingSimpleCatch:null,
      catch_basis:catchBasis,
      total_catch_all:totalAt(unit.full_precision_catch||unit.catch,yi),
      total_discards:totalAt(unit.discards,yi),
      sensitivity:ratio?sensitivity.unavailable('Sensitivity is not defined for a ratio of calculation methods.'):
        sensitivity.display(model.discard_sensitivity?.[state.scope]?.[state.method]?.[treatment]?.[yi]||
          (model.discard_sensitivity_unavailable?.[state.scope]?.[state.method]?
            sensitivity.unavailable(model.discard_sensitivity_unavailable[state.scope][state.method]):null),state),
      status:'ok',numerator:numerator / 9,denominator:ratio ? denominator / 9 : null} : empty('Non-finite result');
  }
  return {evaluate,finite};
})();
if (typeof module !== 'undefined') module.exports = PPRMetrics;
