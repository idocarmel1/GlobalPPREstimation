"""Keep current project defaults separate from explicit browser model choices."""
from pathlib import Path


def model_preferences_layout(text):
    start_marker = '/* Compact preferences shared by the two standalone pages.'
    end_marker = '/* Shared group picker.'
    if start_marker not in text:
        return text
    start, end = text.index(start_marker), text.index(end_marker)
    text = text[:start] + Path(__file__).with_name('model_preferences.js').read_text('utf-8') + '\n\n' + text[end:]

    def replace(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('Model preferences layout anchor changed: ' + old[:100])
        text = text.replace(old, new, 1)

    # A model-change event is explicit intent; opening, redrawing or sorting is not.
    replace('store.data.models[ecosystems.value]=models.value;', 'store.selectModel(ecosystems.value,models.value);')
    anchor = '<small id="groupFilterSummary">All model groups included</small></div>'
    replace(anchor, anchor + '<button id="resetModelChoices" type="button">Use project model defaults</button>')
    if 'const SERIES_DB=' in text:
        replace("PPRGroupSettings.create({view:'trends'})", "PPRGroupSettings.create({view:'trends',units:db.units})")
        replace("  let models={...groupStore?.data.models};try {const parsed=JSON.parse(params.get('models')||'{}');if(parsed && !Array.isArray(parsed) && typeof parsed==='object') models={...parsed,...models};} catch { /* Invalid optional model overrides remain unset. */ }",
                '  const models={...groupStore?.data.models};')
        replace("state.models[id]=select.value;update();", "groupStore.selectModel(id,select.value);state.models={...groupStore.data.models};update();")
        replace('Object.assign(groupStore.data.models,state.models);groupStore.save(p);', 'groupStore.data.models={...state.models};groupStore.save(p);')
        # Both callback paths must replace state so a removed override stays removed.
        old = 'Object.assign(state.models,groupStore.data.models);'
        if text.count(old) != 2:
            raise ValueError('Model preferences trends synchronization anchors changed')
        text = text.replace(old, 'state.models={...groupStore.data.models};')
    else:
        replace("PPRGroupSettings.create({view:'map'})", "PPRGroupSettings.create({view:'map',units:network.units})")
        replace("  const saved={...JSON.parse(mapParams.get('models')||'{}'),...groupStore?.data.models};", '  const saved={...groupStore?.data.models};')
        replace('chosenModels[r.unit_id]=Number(sel.value);applyYear(DB.year)', 'chosenModels[r.unit_id]=Number(sel.value);groupStore.selectModel(r.unit_id,modelUnit.models[Number(sel.value)].id);applyYear(DB.year)')
        replace('    for(const [id,index] of Object.entries(chosenModels))if(network.units[id]?.models[index])groupStore.data.models[id]=network.units[id].models[index].id;\n', '')
        old = 'for(const [id,modelId] of Object.entries(groupStore.data.models)){const index=network.units[id]?.models.findIndex(m=>m.id===modelId);if(index>=0)chosenModels[id]=index;}'
        if text.count(old) != 2:
            raise ValueError('Model preferences map synchronization anchors changed')
        text = text.replace(old, 'for(const [id,unit] of Object.entries(network.units)){const index=unit.models.findIndex(m=>m.id===groupStore.data.models[id]);chosenModels[id]=index>=0?index:unit.default_model;}')
    replace("    $('openGroupFilter').addEventListener" if 'const SERIES_DB=' in text else "  $('openGroupFilter').addEventListener",
            ("    " if 'const SERIES_DB=' in text else "  ") + "$('resetModelChoices').addEventListener('click',()=>groupStore.resetModels());\n" +
            ("    " if 'const SERIES_DB=' in text else "  ") + "$('openGroupFilter').addEventListener")
    return text
