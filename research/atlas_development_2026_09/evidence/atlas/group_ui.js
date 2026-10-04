/* Shared group picker. Model data and calculations are embedded by the renderer. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.PPRGroupDialog=api;})(globalThis,function(){
  'use strict';
  const numeric=['te','tl','sppr_all','sppr_inner','ppr'];
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const bounds=v=>v===''||v==null?null:Number(v);
  function filterRows(rows,table={}){
    const query=String(table.query||'').trim().toLowerCase();
    return rows.filter(row=>(!query||row.name.toLowerCase().includes(query))&&numeric.every(key=>{
      const range=table.ranges?.[key]||{},min=bounds(range.min),max=bounds(range.max);
      return (!finite(min)&&!finite(max))||(finite(row[key])&&(!finite(min)||row[key]>=min)&&(!finite(max)||row[key]<=max));
    }));
  }
  function sortRows(rows,key='name',direction='asc'){
    return [...rows].sort((a,b)=>{
      const av=a[key],bv=b[key];
      if(key!=='name'){
        if(!finite(av)||!finite(bv))return finite(av)?-1:finite(bv)?1:a.name.localeCompare(b.name);
      }
      const order=key==='name'?String(av).localeCompare(String(bv)):av-bv;
      return order?(direction==='desc'?-order:order):a.name.localeCompare(b.name);
    });
  }
  function create({units,store,getContext,onChange}){
    const doc=document,el=(tag,text,className)=>{const node=doc.createElement(tag);if(text!=null)node.textContent=text;if(className)node.className=className;return node;};
    const available=Object.entries(units).filter(([,u])=>u.models?.some(m=>m.verified&&m.group_data));
    const dialog=el('dialog',null,'group-dialog');dialog.id='groupDialog';dialog.setAttribute('aria-labelledby','groupDialogTitle');
    const heading=el('div',null,'group-heading'),title=el('h2','Groups included in PPR');title.id='groupDialogTitle';
    const close=el('button','×','group-close');close.type='button';close.setAttribute('aria-label','Close group selection');close.onclick=()=>dialog.close();heading.append(title,close);dialog.append(heading);
    const controls=el('div',null,'group-controls');
    const selectField=(label,id)=>{const field=el('label',label),select=el('select');select.id=id;field.append(select);controls.append(field);return select;};
    const ecosystems=selectField('Ecosystem','groupEcosystem'),models=selectField('Model','groupModel'),methods=selectField('Method for SPPR and PPR columns','groupReferenceMethod');
    const fill=(select,items)=>{select.replaceChildren(...items.map(([value,text])=>{const option=el('option',text);option.value=value;return option;}));};
    fill(ecosystems,available.map(([id,u])=>[id,(u.name||u.label||id)+' ('+id+')']));
    dialog.append(controls);
    const contextNote=el('p',null,'group-context');contextNote.id='groupContext';dialog.append(contextNote);
    const searchLabel=el('label','Find groups by name','group-search'),search=el('input');search.type='search';search.id='groupSearch';search.placeholder='Group name';searchLabel.append(search);dialog.append(searchLabel);
    const actions=el('div',null,'group-actions'),count=el('span');count.id='groupSelectedCount';count.setAttribute('aria-live','polite');
    const button=(text,id)=>{const b=el('button',text);b.id=id;b.type='button';actions.append(b);return b;};
    actions.append(count);const all=button('Select all','groupSelectAll'),matching=button('Select matching','groupSelectMatching'),none=button('Clear all','groupClearAll');dialog.append(actions);
    const hint=el('p','Filters narrow the table. Select matching applies those rows; checkboxes change the comparison immediately.','group-hint');dialog.append(hint);
    const wrap=el('div',null,'group-table-wrap'),table=el('table');table.setAttribute('aria-label','Model groups and selection');
    const head=el('thead'),header=el('tr'),filters=el('tr'),body=el('tbody');body.id='groupTableBody';
    const columns=[['selected','Include'],['name','Group name'],['te','TE'],['tl','TL'],['sppr_all','SPPR_all'],['sppr_inner','SPPR_inner'],['ppr','Catch-related PPR (t C)']];
    const rangeInputs={},sortButtons={};
    for(const [key,label] of columns){
      const th=el('th');th.scope='col';const filter=el('th');
      if(key==='selected')th.textContent=label;
      else {const b=el('button',label,'group-sort');b.type='button';b.dataset.column=key;sortButtons[key]=b;th.append(b);b.onclick=()=>{const prefs=preferences();prefs.direction=prefs.sort===key&&prefs.direction==='asc'?'desc':'asc';prefs.sort=key;store.save();renderRows();};}
      if(numeric.includes(key)){
        rangeInputs[key]={};
        for(const bound of ['min','max']){const input=el('input');input.type='number';input.step='any';input.placeholder=bound==='min'?'Min':'Max';input.setAttribute('aria-label',label+' '+(bound==='min'?'minimum':'maximum'));input.dataset.column=key;input.dataset.bound=bound;
          input.oninput=()=>{const prefs=preferences();prefs.ranges||={};prefs.ranges[key]||={};prefs.ranges[key][bound]=input.value;store.save();renderRows();};rangeInputs[key][bound]=input;filter.append(input);}
      }
      header.append(th);filters.append(filter);
    }
    head.append(header,filters);table.append(head,body);wrap.append(table);dialog.append(wrap);
    const footer=el('div',null,'group-footer'),explanation=el('p','One group selection per model applies to all estimation methods in both views. TE = GE × EE from the model inputs; it is separate from fixed-TE assumptions in some methods. Excluded catch is not reassigned.');
    const done=el('button','Done','group-done');done.id='groupDone';done.onclick=()=>dialog.close();footer.append(explanation,done);dialog.append(footer);
    const storage=el('p',null,'group-storage');dialog.append(storage);doc.body.append(dialog);
    const current=()=>{const unit=units[ecosystems.value];return {unit,model:unit?.models.find(m=>m.id===models.value)};};
    const key=()=>ecosystems.value+'::'+models.value;
    function preferences(){return store.data.tables[key()]||=( {query:'',ranges:{},sort:'name',direction:'asc'} );}
    function selection(){const {model}=current();return new Set(store.data.selections[key()]??model?.group_data.groups.map(g=>g.id)??[]);}
    function sourceRows(){const {unit,model}=current();return model?PPRGroups.rows(unit,model,{...getContext(),method:methods.value}):[];}
    function visibleRows(){const prefs=preferences();return sortRows(filterRows(sourceRows(),prefs),prefs.sort,prefs.direction);}
    function notify(){store.save();onChange();store.shareLinks();renderCount();}
    function renderCount(){const {model}=current(),selected=selection();count.textContent=`${selected.size} of ${model?.group_data.groups.length||0} groups selected · ${visibleRows().length} matching`;
      storage.textContent=store.storageAvailable?'Selections are saved automatically in this browser.':'Browser saving is unavailable. Navigation links still carry the current selections.';}
    function setSelection(ids){const {model}=current();if(!model)return;const allIds=model.group_data.groups.map(g=>g.id);if(ids.length===allIds.length&&allIds.every(id=>ids.includes(id)))delete store.data.selections[key()];else store.data.selections[key()]=ids;notify();renderRows();}
    function renderRows(){
      const selected=selection(),rows=visibleRows();body.replaceChildren();
      for(const [index,row] of rows.entries()){
        const tr=el('tr');tr.dataset.groupId=row.id;const checkCell=el('td'),check=el('input');check.type='checkbox';check.checked=selected.has(row.id);check.setAttribute('aria-label','Include '+row.name);
        check.onchange=()=>{const ids=selection();if(check.checked)ids.add(row.id);else ids.delete(row.id);const {model}=current();if(ids.size===model.group_data.groups.length)delete store.data.selections[key()];else store.data.selections[key()]=[...ids];notify();};checkCell.append(check);tr.append(checkCell);
        for(const [key] of columns.slice(1)){const cell=el('td',key==='name'?row.name:finite(row[key])?row[key].toLocaleString(undefined,{maximumSignificantDigits:6}):'Unavailable');if(key!=='name'){cell.className='group-number';cell.title=finite(row[key])?String(row[key]):'No value in this source';}tr.append(cell);}body.append(tr);
      }
      if(!rows.length){const tr=el('tr'),cell=el('td','No groups match these filters.');cell.colSpan=7;tr.append(cell);body.append(tr);}
      for(const [column,b] of Object.entries(sortButtons)){const sorted=preferences().sort===column;b.parentElement.setAttribute('aria-sort',sorted?(preferences().direction==='desc'?'descending':'ascending'):'none');b.dataset.direction=sorted?preferences().direction:'';}
      renderCount();
    }
    function loadModel(){
      const {unit,model}=current();if(!model)return;const prefs=preferences(),context=getContext();
      const names=[...new Set([...model.group_data.methods,'simple trophic chain'])];fill(methods,names.map(id=>[id,id]));methods.value=names.includes(prefs.method)?prefs.method:names.includes(context.method)?context.method:names[0];prefs.method=methods.value;
      search.value=prefs.query||'';for(const [column,inputs] of Object.entries(rangeInputs))for(const [bound,input] of Object.entries(inputs))input.value=prefs.ranges?.[column]?.[bound]??'';
      const diagnostic=PPRGroups.mcAcceptanceFailure(model,methods.value),status=(model.taxon_scopes||model.scopes)?.[context.scope]?.status?.[methods.value];
      contextNote.textContent=`${context.year} · ${context.catch_basis==='catch'?'All catch':context.catch_basis==='discards'?'Discards':'Landings'} · PPR source: ${context.scope||'all'} · Values describe each group before selection. NPP remains the ecosystem total.`+(diagnostic?' '+diagnostic:status&&status!=='ok'?' PPR unavailable: '+status+'.':'');
      if(methods.value==='simple trophic chain')contextNote.textContent+=' Simple-chain SPPR is taxon-specific; choose a model method to use the group SPPR columns.';
      renderRows();
    }
    function loadEcosystem(){const unit=units[ecosystems.value];if(!unit)return;const modelList=unit.models.filter(m=>m.verified&&m.group_data);fill(models,modelList.map(m=>[m.id,m.label||m.id]));const defaultId=typeof unit.default_model==='number'?unit.models[unit.default_model]?.id:unit.default_model;const chosen=store.data.models[ecosystems.value]||defaultId;models.value=modelList.some(m=>m.id===chosen)?chosen:modelList[0].id;loadModel();}
    ecosystems.onchange=()=>{store.data.last_unit=ecosystems.value;loadEcosystem();store.save();};
    models.onchange=()=>{store.data.models[ecosystems.value]=models.value;loadModel();notify();};
    methods.onchange=()=>{preferences().method=methods.value;store.save();loadModel();};
    search.oninput=()=>{preferences().query=search.value;store.save();renderRows();};
    all.onclick=()=>{const prefs=preferences();prefs.query='';prefs.ranges={};delete store.data.selections[key()];notify();loadModel();};
    matching.onclick=()=>setSelection(visibleRows().map(r=>r.id));none.onclick=()=>setSelection([]);
    dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
    return {open(unitId){if(!available.length)return;const chosen=unitId||store.data.last_unit;if(available.some(([id])=>id===chosen))ecosystems.value=chosen;store.data.last_unit=ecosystems.value;loadEcosystem();store.save();dialog.showModal();},refresh(){if(dialog.open)loadModel();},summary(){const count=Object.keys(store.data.selections).length;return count?`${count} model${count===1?'':'s'} with group selections`:'All model groups included';},available:available.length};
  }
  return {create,filterRows,sortRows};
});
