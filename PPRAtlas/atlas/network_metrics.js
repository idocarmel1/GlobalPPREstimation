/* Pure calculations shared by the atlas and regression tests. */
const PPRMetrics = (() => {
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
    const scope = model.scopes[state.scope];
    const yi = unit.years.indexOf(Number(state.year));
    if (!scope || yi < 0) return empty('Scope or year unavailable');
    const a = scope.methods.indexOf(state.method), b = scope.methods.indexOf(state.denominator);
    const ratio = state.mode === 'ratio';
    if (a < 0 || (ratio && b < 0)) return empty('Method unavailable in this scope');
    for (const method of ratio ? [state.method,state.denominator] : [state.method]) {
      if (scope.status[method] !== 'ok') return empty(method + ': ' + (scope.status[method] || 'unavailable'));
    }
    let numerator=0, denominator=0, support=0, total=0, present=false;
    unit.catch.forEach((years,i) => {
      const c = years[yi] || 0, v = scope.values[i]; total += c;
      if (!c || !v || !finite(v[a]) || (ratio && !finite(v[b]))) return;
      numerator += c*v[a]; denominator += ratio ? c*v[b] : 0;
      support += c; present = true;
    });
    if (!present) return empty('No catch with available method values');
    if (ratio && denominator === 0) return empty('Zero denominator on common catch');
    // Sources and SPPR stay in wet weight; every returned PPR mass is carbon.
    const value = ratio ? numerator / denominator : numerator / 9;
    return finite(value) ? {value,coverage:total ? support/total : null,catch:support,
      status:'ok',numerator:numerator / 9,denominator:ratio ? denominator / 9 : null} : empty('Non-finite result');
  }
  return {evaluate,finite};
})();
if (typeof module !== 'undefined') module.exports = PPRMetrics;
