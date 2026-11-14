/* Shared display preferences. Only explicit model choices override project defaults. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.PPRGroupSettings=api;})(globalThis,function(){
  'use strict';
  const object=value=>value&&typeof value==='object'&&!Array.isArray(value);
  const models=value=>Object.fromEntries(Object.entries(object(value)?value:{}).filter(([,id])=>typeof id==='string'||Number.isInteger(id)));
  const parse=value=>{try{return JSON.parse(value||'null');}catch{return null;}};
  function clean(value){
    const data={version:2,selections:{},models:{},tables:{}};
    if(!object(value))return data;
    if(typeof value.last_unit==='string')data.last_unit=value.last_unit;
    data.selections=Object.fromEntries(Object.entries(value.selections||{}).filter(([,ids])=>Array.isArray(ids)).map(([key,ids])=>[key,[...new Set(ids.filter(id=>typeof id==='string'))]]));
    data.tables=Object.fromEntries(Object.entries(value.tables||{}).filter(([,table])=>object(table)));
    data.models=models(value.models);
    if(object(value.legacy_models))data.legacy_models=models(value.legacy_models);
    if(object(value.legacy_model_views))data.legacy_model_views={...value.legacy_model_views};
    return data;
  }
  function create({env=globalThis,view='map',units={}}={}){
    const address=new URL(env.location.href),folder=new URL('.',address).pathname;
    // Old open pages rewrite their v1 store on storage events. Isolate v2 so
    // they cannot downcast new preferences or start a cross-tab write loop.
    const legacyKey='GlobalPPR:group-settings:v1:'+folder;
    const key='GlobalPPR:group-settings:v2:'+folder,viewKey=key+':'+view;
    let storageAvailable=true;
    const read=k=>{try{return env.localStorage.getItem(k);}catch{storageAvailable=false;return null;}};
    const activeRaw=read(key),migrating=activeRaw===null;
    const sourceKey=migrating?legacyKey:key;
    const current=new URLSearchParams(address.search),savedView=read(sourceKey+':'+view)||'';
    const mapView=read(sourceKey+':map')||'',trendView=read(sourceKey+':trends')||'';
    const normalize=value=>Object.fromEntries(Object.entries(models(value)).flatMap(([id,chosen])=>{
      const unit=units[id];if(!unit)return [];
      const defaultId=typeof unit.default_model==='number'?unit.models?.[unit.default_model]?.id:unit.default_model;
      const model=typeof chosen==='number'?unit.models?.[chosen]:unit.models?.find(m=>m.id===chosen);
      return model&&model.id!==defaultId?[[id,model.id]]:[];
    }));
    function migrate(raw){
      const data=clean(raw);
      if(raw&&raw.version!==2){
        data.legacy_models={...data.legacy_models,...models(raw.models)};
        data.legacy_model_views={...data.legacy_model_views,map:mapView,trends:trendView};
        // The old map saved only nondefault choices in models=. The old trends
        // view copied every shared model, so its models= is not evidence of intent.
        data.models=models(parse(new URLSearchParams(mapView).get('models')));
      }
      data.models=normalize(data.models);return data;
    }
    let raw=parse(migrating?read(legacyKey):activeRaw);
    if(current.has('group_settings')){
      const linked=parse(current.get('group_settings'));if(object(linked))raw=linked;
    }
    let data=migrate(raw);
    if(current.has('models'))data.models=normalize({...data.models,...models(parse(current.get('models')))});
    const params=new URLSearchParams(current.toString()||savedView);
    // Stored view URLs are presentation settings; active model intent has one home.
    const modelParams=p=>{if(Object.keys(store.data.models).length)p.set('models',JSON.stringify(store.data.models));else p.delete('models');return p;};
    const listeners=[];
    const store={data,params,get storageAvailable(){return storageAvailable;},
      selectModel(id,chosen){store.data.models=normalize({...store.data.models,[id]:chosen});},
      resetModels(){store.data.models={};store.save();for(const listener of listeners)listener(store.data);},
      save(p){
        store.data.models=normalize(store.data.models);
        try{
          env.localStorage.setItem(key,JSON.stringify(store.data));storageAvailable=true;
          if(p){const own=modelParams(new URLSearchParams(p));own.delete('group_settings');env.localStorage.setItem(viewKey,own.toString());}
        }catch{storageAvailable=false;}
        try{if(env.history){const url=new URL(env.location.href);modelParams(url.searchParams);store.attach(url.searchParams);env.history.replaceState(null,'',url.href);}}catch{/* Local-file history may be restricted. */}
        store.shareLinks();
      },
      attach(p){p.set('group_settings',JSON.stringify(store.data));return p;},
      link(href){const url=new URL(href,env.location.href);store.attach(url.searchParams);return url.href;},
      shareLinks(){
        if(!env.document)return;
        for(const link of env.document.querySelectorAll('a[href]')){
          const url=new URL(link.getAttribute('href'),env.location.href);
          if(new URL('.',url).href!==new URL('.',env.location.href).href||!/(?:index|trends)\.html$/.test(url.pathname))continue;
          store.attach(url.searchParams);link.href=url.href;
        }
      },
      subscribe(listener){listeners.push(listener);}
    };
    modelParams(params);
    if(migrating){
      // Copy presentation settings once; leave every legacy key byte-for-byte intact.
      for(const [name,value] of [['map',mapView],['trends',trendView]]){
        if(!value)continue;
        const own=modelParams(new URLSearchParams(value));own.delete('group_settings');
        try{env.localStorage.setItem(key+':'+name,own.toString());}catch{storageAvailable=false;}
      }
    }
    env.addEventListener?.('storage',event=>{
      if(event.key!==key||!event.newValue)return;
      const incoming=parse(event.newValue);if(!object(incoming))return;
      store.data=migrate(incoming);for(const listener of listeners)listener(store.data);
    });
    store.save();return store;
  }
  return {create,clean};
});
