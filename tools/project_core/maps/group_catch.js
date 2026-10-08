/* Inspect saved native model catch without changing the graph's annual basis. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.PPRGroupCatch=api;})(globalThis,function(){
  'use strict';
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  function rows(unit,model,options,evaluate){
    const data=model?.group_data;if(!data)return [];
    const column=data.methods.indexOf(options.method),scope=(model.taxon_scopes||model.scopes)?.[options.scope],status=scope?.status?.[options.method];
    const policy=globalThis.PPRAvailableResults;
    const admitted=policy?policy.allowed(model,status,options.method):status==='ok'||String(status).startsWith('provisional:');
    const signed=policy?policy.signed(model,status,options.method):String(status).startsWith('provisional:');
    const mcFailure=globalThis.PPRGroups.mcAcceptanceFailure(model,options.method);
    return data.groups.map((group,index)=>{
      let ppr=null;
      if(options.catch_source==='model'){
        const coefficient=group.model_catch_sppr?group.model_catch_sppr[options.scope]?.[options.method]:data.scopes?.[options.scope]?.[index]?.[column],catchValue=group.model_catch,factor=model.model_catch_carbon_factor;
        if(model.verified&&admitted&&!mcFailure&&column>=0&&finite(factor)&&factor>0&&finite(catchValue)&&catchValue>=0&&finite(coefficient)&&(coefficient>=0||signed))ppr=catchValue*coefficient*factor;
      }else ppr=evaluate(unit,model,{...options,mode:'ppr'},[group.id]).value;
      return {...group,sppr_all:data.scopes?.all?.[index]?.[column]??null,sppr_inner:data.scopes?.inner?.[index]?.[column]??null,ppr};
    });
  }
  return {rows};
});
