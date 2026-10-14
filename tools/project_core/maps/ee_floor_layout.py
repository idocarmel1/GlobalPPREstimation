"""Expose saved calculation assumptions outside the original signed review text."""
from html import escape
from pathlib import Path


def ee_floor_layout(text):
    if '/* Shared group picker.' not in text:return text
    def replace(old,new):
        nonlocal text
        if text.count(old)!=1:raise ValueError('EE-floor layout anchor changed: '+old[:90])
        text=text.replace(old,new,1)
    replace("cell.title=finite(row[key])?String(row[key]):'No value in this source';",
            "cell.title=key==='ee'?PPREeFloor.groupTooltip(row):finite(row[key])?String(row[key]):'No value in this source';")
    if 'const SERIES_DB=' in text:
        replace('PPRGroupContributions.toCSV(result,state,PPRTimeSeries.comparisonToCSV)',
                'PPREeFloor.toCSV(PPRGroupContributions.toCSV(result,state,PPRTimeSeries.comparisonToCSV),PPREeFloor.exportResult(db,result,state).calculation_provenance)')
        replace('PPRTimeSeries.comparisonToJSON(result,state)',
                'PPRTimeSeries.comparisonToJSON(PPREeFloor.exportResult(db,result,state),state)')
    else:
        replace('sensitivity_source_validity:band?.source_validity};',
                "sensitivity_source_validity:band?.source_validity,calculation_provenance:metricState.mode==='npp'?null:model?.calculation_provenance??null};")
    script=Path(__file__).with_name('ee_floor.js').read_text('utf-8')
    replace('/* Retain the original catch allocations when selecting model groups. */',
            script+'\n/* Retain the original catch allocations when selecting model groups. */')
    return text.replace('</head>','<style>.ee-floor-provenance{font-size:12px;line-height:1.5;margin:12px 0;color:#203c40}.ee-floor-provenance p{margin:4px 0 8px}.ee-floor-provenance p:first-child{font-weight:600}</style></head>',1)


def source_provenance_layout(text,catalog):
    """Link each source ecosystem to its exact saved model settings, including candidates."""
    for region in catalog['regions']:
        unit_id=region['unit_id'];models=catalog.get('network',{}).get('units',{}).get(unit_id,{}).get('models',[])
        parts=[]
        for model in models:
            provenance=model.get('calculation_provenance',{});enabled=provenance.get('use_ee_floor')
            if not isinstance(enabled,bool):continue
            setting=f'EE floor ON ({provenance.get("ee_floor") if provenance.get("ee_floor") is not None else "Unavailable"})' if enabled else 'EE floor OFF'
            links=[]
            for label,path in [('Saved calculation settings and EE-floor ledger',model.get('workbook')),
                               ('Calculator source export',model.get('source'))]:
                if path:links.append(f'<a href="{escape("../"+path,quote=True)}">{label}</a>')
            parts.append('<p><b>'+escape(model.get('label') or model['id'])+'</b> · '+escape(setting)+'. '
                         +'Hypothetical external nonfishery mortality sink; excluded from catch and fishery PPR. '
                         +'Existing signed researcher reviews retain their original scope and do not approve this changed calculation assumption or transformed diagnostics.'
                         +(' '+ ' · '.join(links) if links else '')+'</p>')
        if not parts:continue
        anchor='<small>'+escape(unit_id)+' · '
        start=text.find(anchor)
        if start<0:raise ValueError('Source calculation provenance ecosystem anchor changed: '+unit_id)
        end=text.index('</summary>',start)+len('</summary>')
        text=text[:end]+'<div class="calculation-provenance">'+''.join(parts)+'</div>'+text[end:]
    return text
