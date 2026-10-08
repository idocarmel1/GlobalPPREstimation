"""Scoped group catch inspection layered over the current review adapters."""
from pathlib import Path


def group_catch_layout(text):
    if '/* Shared group picker.' not in text:
        return text

    def replace(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('Group catch layout anchor changed: ' + old[:90])
        text = text.replace(old, new, 1)

    replace('const catch_indices=manual?indices:list.map((g,i)=>i);', 'const catch_indices=indices;')
    replace('// Researcher exclusions affect displayed PPR only. Manual group selections\n    // retain their existing catch/coverage behavior, without reallocating weights.',
            '// Every unchecked group is omitted from catch and coverage with its\n    // original allocation weight; excluded shares are never reassigned.')
    start = text.index('  function rows(unit,model,options){')
    end = text.index('  return {key,selection,active,rows,evaluate,inputs,mcAcceptanceFailure};', start)
    text = text[:start] + '''  function rows(unit,model,options){
    return PPRGroupCatch.rows(unit,model,options,evaluate);
  }
''' + text[end:]
    anchor = '/* Retain the original catch allocations when selecting model groups. */'
    replace(anchor, Path(__file__).with_name('group_catch.js').read_text(encoding='utf-8') + '\n' + anchor)
    replace("methods=selectField('Method for SPPR and PPR columns','groupReferenceMethod');",
            "methods=selectField('Method for SPPR and PPR columns','groupReferenceMethod'),catchSource=selectField('Catch source for PPR column','groupCatchSource'),catchYear=selectField('Catch year for PPR column','groupCatchYear');")
    replace("    dialog.append(controls);", "    fill(catchSource,[['annual','Annual taxon catch'],['model','Saved Ecopath model catch']]);\n    dialog.append(controls);")
    replace("function sourceRows(){const {unit,model}=current();return model?PPRGroups.rows(unit,model,{...getContext(),method:methods.value}):[];}",
            "function sourceRows(){const {unit,model}=current();return model?PPRGroups.rows(unit,model,{...getContext(),method:methods.value,catch_source:catchSource.value,year:Number(catchYear.value)}):[];}")
    replace("      search.value=prefs.query||'';", """      const years=PPRGroups.inputs(unit).years||[];
      fill(catchYear,years.map(year=>[String(year),String(year)]));
      const preferredYear=Number(prefs.catch_year??context.year);
      catchYear.value=String(years.includes(preferredYear)?preferredYear:years[years.length-1]??'');
      catchSource.value=prefs.catch_source==='model'?'model':'annual';catchYear.disabled=catchSource.value==='model';
      prefs.catch_source=catchSource.value;if(catchYear.value)prefs.catch_year=Number(catchYear.value);
      sortButtons.ppr.textContent=catchSource.value==='model'?'Model-catch PPR (t C/km²/year)':'Catch-related PPR (t C)';
      search.value=prefs.query||'';""")
    replace("`${context.year} · ${context.catch_basis==='catch'?'All catch':context.catch_basis==='discards'?'Discards':'Landings'} · PPR source: ${context.scope||'all'} · Values describe each group before selection. NPP remains the ecosystem total.`",
            "`${catchSource.value==='model'?(finite(model.model_catch_carbon_factor)?'Saved native model catch × group SPPR'+(model.model_catch_carbon_factor===1?'':' / 9')+' (t C/km²/year); no area scaling':'Saved native model catch; catch/SPPR unit conversion unavailable'):catchYear.value+' · '+(context.catch_basis==='catch'?'All catch':context.catch_basis==='discards'?'Discards':'Landings')} · PPR source: ${context.scope||'all'} · Values describe each group before selection. Catch source and year affect this table only. NPP remains the ecosystem total.`")
    replace("    search.oninput=()=>{", "    catchSource.onchange=()=>{preferences().catch_source=catchSource.value;loadModel();store.save();};\n    catchYear.onchange=()=>{preferences().catch_year=Number(catchYear.value);loadModel();store.save();};\n    search.oninput=()=>{")
    return text
