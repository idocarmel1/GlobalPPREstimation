/* The region table is a view of the graph's calculation settings. */
const PPRRegionTable=(()=>{
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  function create({db,getState,calculate,methodLabel,save}){
    const el=(tag,text)=>{const node=document.createElement(tag);if(text!=null)node.textContent=text;return node;};
    const year=document.getElementById('regionTableYear'),head=document.getElementById('regionTableHead');
    const body=document.getElementById('regionTableBody'),foot=document.getElementById('regionTableFoot'),note=document.getElementById('regionTableNote');
    year.replaceChildren(...db.years.map(y=>{const o=el('option',String(y));o.value=String(y);return o;}));
    function render(){
      const state=getState();
      if(!db.years.includes(Number(state.table_year)))state.table_year=db.years.at(-1);
      year.value=String(state.table_year);
      const result=calculate(Number(state.table_year)),normalized=state.mode!=='npp'&&Boolean(state.baseline);
      const metric=state.mode==='npp'?'NPP (t C/year)':normalized?'Multiple of '+methodLabel(state.baseline)+' (×)':state.mode==='ratio'?'PPR / NPP (%)':'PPR (t C/year)';
      note.textContent=metric+' · '+result.year+'. Uses the graph’s selected models, methods, catch basis and included groups. '+
        (state.mode==='ratio'&&!normalized?(state.npp_scope==='global'?'Each region uses the same fixed global atlas NPP denominator. ':'Each region uses its own NPP; the selected-set row is the ratio of sums. '):'')+
        'The table year can be selected independently of the plotted range. Missing results remain unavailable.';
      if(PPRTrendExtras.scaling(state))note.textContent+=' Global approximation is enabled: each row uses the full selected-set simple-chain share as the scale factor. An incomplete reference leaves all scaled values unavailable.';
      const header=el('tr'),region=el('th','Region');region.scope='col';header.append(region);
      for(const method of result.methods){const cell=el('th',methodLabel(method));cell.scope='col';header.append(cell);}head.replaceChildren(header);
      const rowElement=row=>{
        const tr=el('tr');if(row.id)tr.dataset.regionId=row.id;
        const label=el('th',row.id?row.name+' ('+row.id+')':row.name);label.scope='row';tr.append(label);
        for(const point of row.values){
          const cell=el('td');cell.dataset.method=point.method;
          cell.textContent=finite(point.value)?point.value.toLocaleString(undefined,{maximumSignificantDigits:6})+(normalized?'×':state.mode==='ratio'?'%':''):'Unavailable';
          const flagged=finite(point.value)&&point.status&&point.status!=='ok';
          if(flagged||point.npp_estimated)cell.append(el('small',(flagged?'Flagged':'')+(flagged&&point.npp_estimated?' · ':'')+(point.npp_estimated?'Historical NPP estimate':'')));
          cell.title=finite(point.value)?[String(point.value),flagged?point.status:null,point.npp_estimated?'Earlier missing NPP uses the earliest available annual value.':null].filter(Boolean).join('\n'):point.reason;
          if(!finite(point.value))cell.className='region-unavailable';tr.append(cell);
        }
        return tr;
      };
      body.replaceChildren(...result.rows.map(rowElement));foot.replaceChildren(rowElement(result.total));
      if(!result.rows.length||!result.methods.length){const tr=el('tr'),cell=el('td',!result.rows.length?'No selected regions match the current filter.':'Select a method to see regional results.');cell.colSpan=Math.max(1,result.methods.length+1);tr.append(cell);body.replaceChildren(tr);foot.replaceChildren();}
    }
    year.addEventListener('change',()=>{getState().table_year=Number(year.value);render();save();});
    return {render};
  }
  return {create};
})();
