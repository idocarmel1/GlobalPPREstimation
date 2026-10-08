"""Narrow adapters for independent available series and retained reviewed numbers."""
from pathlib import Path

MARKER = "/* Shared annual denominator lookup. Substitution is an explicit display policy. */"


def _replace(text, old, new, count=1):
    found = text.count(old)
    if found != count:
        raise ValueError(f"Available-results adapter expected {count} anchors for {old[:100]!r}; found {found}")
    return text.replace(old, new)


def available_results_layout(text):
    if MARKER not in text:
        return text
    script = Path(__file__).with_name("available_results.js").read_text(encoding="utf-8")
    text = _replace(text, MARKER, MARKER + "\n" + script)
    # Group and whole-model calculations share the same bounded display policy.
    text = _replace(text, "!(scope.status?.[method]==='ok'||String(scope.status?.[method]).startsWith('provisional:'))", "!PPRAvailableResults.allowed(model,scope.status?.[method],method)")
    text = _replace(text, "(baseline<0&&!String(scope.status[method]).startsWith('provisional:'))", "(baseline<0&&!PPRAvailableResults.signed(model,scope.status[method],method))")
    text = _replace(text, "(v<0&&!String(scope.status[method]).startsWith('provisional:'))", "(v<0&&!PPRAvailableResults.signed(model,scope.status[method],method))")
    text = _replace(text, "methods.map(m=>scope.status[m]).filter(s=>String(s).startsWith('provisional:'))", "methods.map(m=>scope.status[m]).filter(s=>s&&s!=='ok')")
    if "const PPRMetrics = (() => {" in text:
        text = _replace(text, "!(scope.status[method]==='ok'||String(scope.status[method]).startsWith('provisional:'))", "!PPRAvailableResults.allowed(model,scope.status[method],method)")
        text = _replace(text, "(av<0&&!String(scope.status[state.method]).startsWith('provisional:'))", "(av<0&&!PPRAvailableResults.signed(model,scope.status[state.method],state.method))")
        text = _replace(text, "(bv<0&&!String(scope.status[state.denominator]).startsWith('provisional:'))", "(bv<0&&!PPRAvailableResults.signed(model,scope.status[state.denominator],state.denominator))")
        text = _replace(text, "].map(m=>scope.status[m]).filter(s=>String(s).startsWith('provisional:'))", "].map(m=>scope.status[m]).filter(s=>s&&s!=='ok')")
        return text
    text = _replace(text, "!(record.status==='ok'||String(record.status).startsWith('provisional:'))", "!PPRAvailableResults.allowed(selectedModel,record.status,state.method)", 2)
    text = _replace(text, "      const present=i=>finite(record?.ppr?.[i]) && (record.ppr[i]>=0||String(record.status).startsWith('provisional:'));", "      if(!reason)record=PPRAvailableResults.retainedAnnualRecord(unit,selectedModel,record,{...state,catch_basis:catchBasis},db.years);\n      const present=i=>finite(record?.ppr?.[i]) && (record.ppr[i]>=0||PPRAvailableResults.signed(selectedModel,record.status,state.method));")
    text = _replace(text, "records.push({unit,record});", "records.push({unit,record,model:selectedModel});")
    text = _replace(text, "const values=db.years.map((year,i)=>present(i)?groups.evaluate", "const values=db.years.map((year,i)=>indices.includes(i)&&present(i)?groups.evaluate")
    text = _replace(text, "(r.record.ppr[i]<0&&!String(r.record.status).startsWith('provisional:'))", "(r.record.ppr[i]<0&&!PPRAvailableResults.signed(r.model,r.record.status,state.method))")
    text = _replace(text, "records.map(r=>r.record.status).filter(s=>String(s).startsWith('provisional:'))", "records.map(r=>r.record.status).filter(s=>s&&s!=='ok')")
    text = _replace(text, "status:records.length&&records.every", "retained_numeric_display:records.some(r=>r.record.retained_numeric_display),status:records.length&&records.every")
    text = _replace(text, "  function compare(db,state) {", "  function compare(db,state) {\n    if(state.mode!=='npp'&&!state.baseline&&(state.methods||[]).length)return PPRAvailableResults.compare(db,state,aggregate,nppSeries);")
    text = _replace(text, "',result_status,diagnosis_flags';", "',result_status,diagnosis_flags,missing_result_count,excluded_results,retained_numeric_display';", 2)
    text = _replace(text, "result.included.length,result.selected,state.mode", "(p.included_ids||result.included).length,result.selected,state.mode")
    text = _replace(text, "result.included.join(';'),JSON.stringify", "(p.included_ids||result.included).join(';'),JSON.stringify")
    text = _replace(text, "JSON.stringify(result.model_ids),...nppCSV", "JSON.stringify(p.model_ids||result.model_ids),...nppCSV")
    text = _replace(text, "p.status,JSON.stringify(result.review_flags||[])].map(escape)", "p.status,JSON.stringify(p.review_flags||result.review_flags||[]),p.missing_result_count,JSON.stringify(p.excluded||[]),p.retained_numeric_display||false].map(escape)")
    text = _replace(text, "series.included.length,series.selected,state.mode", "(point.included_ids||series.included).length,series.selected,state.mode")
    text = _replace(text, "series.included.join(';'),", "(point.included_ids||series.included).join(';'),")
    text = _replace(text, "JSON.stringify(series.model_ids),", "JSON.stringify(point.model_ids||series.model_ids),")
    text = _replace(text, "point.status,JSON.stringify(series.review_flags||[])].map(escape)", "point.status,JSON.stringify(point.review_flags||series.review_flags||[]),point.missing_result_count,JSON.stringify(point.excluded||[]),point.retained_numeric_display||false].map(escape)")
    return text
