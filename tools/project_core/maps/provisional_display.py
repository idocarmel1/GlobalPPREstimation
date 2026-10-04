"""Explicit research-preview support without modifying retained historical templates."""

def provisional_layout(text):
    # Availability labels describe mapping/coefficient gates, not scientific
    # approval. Diagnostic flags remain separately visible.
    text=text.replace('a verified selected model', 'available coefficients for the selected model')
    text=text.replace('Mapping workbook not verified', 'Selected model has no usable taxon mapping')
    text=text.replace('Model has no verified PPR workbook.', 'Selected model has no usable taxon mapping.')
    text=text.replace('no verified PPR', 'no usable taxon mapping')
    text=text.replace(':unit.note;panel.appendChild(notes);',":('Retained selection rationale: '+(unit.note||''));panel.appendChild(notes);")
    text=text.replace("single?(db.units[state.units[0]]?.note||''):","single?('Retained selection rationale: '+(db.units[state.units[0]]?.note||'')):")
    text=text.replace('generated ${DB.generated_on}', 'source archive date ${DB.generated_on}')
    # Only an explicit provisional status opts into numerical preview. Ordinary FAIL,
    # missing methods and unverified mappings retain their existing gates.
    text=text.replace("scope.status?.[method]!=='ok'", "!(scope.status?.[method]==='ok'||String(scope.status?.[method]).startsWith('provisional:'))")
    text=text.replace("scope.status[method] !== 'ok'", "!(scope.status[method]==='ok'||String(scope.status[method]).startsWith('provisional:'))")
    text=text.replace("record.status!=='ok'", "!(record.status==='ok'||String(record.status).startsWith('provisional:'))")
    # Preserve negative diagnostic values in explicitly opted-in previews. Filtering
    # negative contributions would silently create a different, positive subtotal.
    text=text.replace("if (!finite(av) || av<0 || (ratio && (!finite(bv)||bv<0))) return;",
        "if (!finite(av) || (av<0&&!String(scope.status[state.method]).startsWith('provisional:')) || (ratio && (!finite(bv)||(bv<0&&!String(scope.status[state.denominator]).startsWith('provisional:'))))) return;")
    text=text.replace("status:'ok',numerator:numerator / 9", "status:[state.method,...(ratio?[state.denominator]:[])].map(m=>scope.status[m]).filter(s=>String(s).startsWith('provisional:')).join('; ')||'ok',numerator:numerator / 9")
    text=text.replace("npp.substituted?`Estimated using ${npp.source_year} NPP`:'ok'};\n    }\n    if(groupSubset)",
        "npp.substituted?`${ppr.status==='ok'?'':ppr.status+'; '}Estimated using ${npp.source_year} NPP`:ppr.status};\n    }\n    if(groupSubset)")
    text=text.replace("if(!valid(baseline))return null;", "if(!finite(baseline)||(baseline<0&&!String(scope.status[method]).startsWith('provisional:')))return null;")
    text=text.replace("if(!valid(w)||!valid(v))return null;", "if(!valid(w)||!finite(v)||(v<0&&!String(scope.status[method]).startsWith('provisional:')))return null;")
    text=text.replace("if(!valid(a)||!valid(b))return;", "if(!finite(a)||!finite(b))return;")
    text=text.replace("status:selected.empty?'No groups selected':'ok',group_selection:selected", "status:selected.empty?'No groups selected':methods.map(m=>scope.status[m]).filter(s=>String(s).startsWith('provisional:')).join('; ')||'ok',group_selection:selected")
    text=text.replace("' PPR unavailable: '+status+'.'", "' PPR status: '+status+'.'")
    text=text.replace("const present=i=>finite(record?.ppr?.[i]) && record.ppr[i]>=0;", "const present=i=>finite(record?.ppr?.[i]) && (record.ppr[i]>=0||String(record.status).startsWith('provisional:'));")
    text=text.replace('r.record.ppr[i]<0', "(r.record.ppr[i]<0&&!String(r.record.status).startsWith('provisional:'))")
    text=text.replace('r.record.ppr[i] < 0', "(r.record.ppr[i]<0&&!String(r.record.status).startsWith('provisional:'))")
    text=text.replace('catch_basis:catchBasis,total_catch_all:totalAll,total_discards:totalDiscarded,', "status:records.length&&records.every(r=>r.record.group_values?.[i]?.group_selection?.empty)?'No groups selected':records.map(r=>r.record.status).filter(s=>String(s).startsWith('provisional:')).join('; ')||'ok',catch_basis:catchBasis,total_catch_all:totalAll,total_discards:totalDiscarded,")
    text=text.replace('return {points,included,excluded,selected:ids.length,npp_year:', "return {points,included,excluded,review_flags:[...new Set(included.flatMap(id=>db.units[id].models?.find(m=>m.id===modelIds[id])?.review_flags||[]))],selected:ids.length,npp_year:")
    text=text.replace('+groupCSVHeader(state);', "+groupCSVHeader(state)+',result_status,diagnosis_flags';")
    text=text.replace('...groupCSV(state)].map(escape)', '...groupCSV(state),p.status,JSON.stringify(result.review_flags||[])].map(escape)',1)
    text=text.replace('...groupCSV(state)].map(escape)', '...groupCSV(state),point.status,JSON.stringify(series.review_flags||[])].map(escape)',1)
    # Signed failed previews need a signed plotting range; positive-only plots
    # retain the original scale and tick placement.
    text=text.replace('const raw=(max||1)*1.08/4,', 'const min=Math.min(0,...values),span=Math.max(0,max)-min;\n    const raw=(span||1)*1.08/4,')
    text=text.replace('const ymax=Math.ceil((max||1)*1.04/step)*step;', 'const ymin=Math.floor(min*1.04/step)*step,ymax=Math.ceil((Math.max(0,max)||(min<0?0:1))*1.04/step)*step;')
    text=text.replace('const y=v=>margin.top+height*(1-v/ymax);', 'const y=v=>margin.top+height*(1-(v-ymin)/(ymax-ymin));')
    text=text.replace('for(let tick=0;tick<=ymax+step/100;tick+=step)', 'for(let tick=ymin;tick<=ymax+step/100;tick+=step)')
    text=text.replace("if(!PPRMetrics.finite(v))return '#b7c4ca';", "if(!PPRMetrics.finite(v))return '#b7c4ca';\n  if(v<0)return '#8b3f91';")
    # A visible warning remains attached to both map results and trend source panels.
    text=text.replace("const sel=panel.querySelector('select');", """if(model?.review_flags?.length){const flag=document.createElement('p');flag.className='network-status';flag.style.color='#a33b20';flag.textContent='Diagnosis / review flags: '+model.review_flags.join(' · ');panel.appendChild(flag);}
  if(model?.review_note){const note=document.createElement('p');note.className='network-note';note.textContent=model.review_note;panel.appendChild(note);}
  const sel=panel.querySelector('select');""")
    text=text.replace("o.textContent=m.label||m.id.replaceAll('_',' ');", "o.textContent=(m.review_flags?.length?'⚠ ':'')+(m.label||m.id.replaceAll('_',' '));")
    text=text.replace("li.appendChild(document.createTextNode(' · '+(model?.label||model?.id||'No model')));", """li.appendChild(document.createTextNode(' · '+(model?.label||model?.id||'No model')));
        if(model?.review_flags?.length)li.appendChild(element('p','Diagnosis / review flags: '+model.review_flags.join(' · ')));
        if(model?.review_note)li.appendChild(element('p',model.review_note));""")
    text=text.replace('Failed methods remain unavailable.', 'Explicit provisional results are shown with diagnostic flags for later validation. Other failed or missing methods remain unavailable.')
    return text
