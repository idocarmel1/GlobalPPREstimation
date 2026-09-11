/* Compact preferences shared by the two standalone pages. No data requests. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.PPRGroupSettings=api;})(globalThis,function(){
  'use strict';
  const object=v=>v&&typeof v==='object'&&!Array.isArray(v);
  function clean(value){
    const data={version:1,selections:{},models:{},tables:{}};
    if(!object(value))return data;
    if(typeof value.last_unit==='string')data.last_unit=value.last_unit;
    for(const [key,ids] of Object.entries(value.selections||{}))if(Array.isArray(ids))data.selections[key]=[...new Set(ids.filter(id=>typeof id==='string'))];
    for(const [key,id] of Object.entries(value.models||{}))if(typeof id==='string')data.models[key]=id;
    for(const [key,table] of Object.entries(value.tables||{}))if(object(table))data.tables[key]=table;
    return data;
  }
  function create({env=globalThis,view='map'}={}){
    const address=new URL(env.location.href),folder=new URL('.',address).pathname;
    const key='GlobalPPR:group-settings:v1:'+folder,viewKey=key+':'+view;
    let data=clean(null),storageAvailable=true;
    const read=k=>{try{return env.localStorage.getItem(k);}catch{storageAvailable=false;return null;}};
    try{data=clean(JSON.parse(read(key)||'null'));}catch{/* Invalid preferences start with all groups. */}
    const current=new URLSearchParams(address.search);
    const params=new URLSearchParams(current.toString()||read(viewKey)||'');
    if(current.has('group_settings')){
      try{data=clean(JSON.parse(current.get('group_settings')));}catch{/* A malformed link never executes content. */}
    }
    const listeners=[];
    const store={data,params,get storageAvailable(){return storageAvailable;},
      save(p){
        try{
          env.localStorage.setItem(key,JSON.stringify(store.data));storageAvailable=true;
          if(p){const own=new URLSearchParams(p);own.delete('group_settings');env.localStorage.setItem(viewKey,own.toString());}
        }catch{storageAvailable=false;}
        try{if(env.history){const url=new URL(env.location.href);store.attach(url.searchParams);env.history.replaceState(null,'',url.href);}}catch{/* Some local-file browsers restrict history. */}
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
    env.addEventListener?.('storage',event=>{
      if(event.key!==key||!event.newValue)return;
      try{store.data=clean(JSON.parse(event.newValue));for(const listener of listeners)listener(store.data);}catch{/* Ignore invalid external preferences. */}
    });
    store.save();
    return store;
  }
  return {create,clean};
});
