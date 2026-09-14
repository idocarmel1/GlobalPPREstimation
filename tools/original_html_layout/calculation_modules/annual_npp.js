/* Shared annual denominator lookup. Substitution is an explicit display policy. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object' && module.exports)module.exports=api;
  else root.PPRAnnualNPP=api;
})(typeof globalThis==='object'?globalThis:this,function(){
  const positive=value=>typeof value==='number' && Number.isFinite(value) && value>0;
  function resolve(years,values,year,policy='observed',metadata={},options={}){
    const acceptable=options.allowZero?value=>typeof value==='number'&&Number.isFinite(value)&&value>=0:positive;
    const index=years.indexOf(Number(year)),annual=Array.isArray(values);
    const raw=annual?values[index]:values;
    let sourceYear=Number(year),value=raw,substituted=false;
    if(index>=0 && annual && raw==null && policy==='earliest'){
      const first=years.map((y,i)=>({year:Number(y),value:values[i]})).filter(p=>acceptable(p.value)).sort((a,b)=>a.year-b.year)[0];
      if(first && Number(year)<first.year){value=first.value;sourceYear=first.year;substituted=true;}
    }
    const valid=index>=0 && acceptable(value);
    return {value:valid?value:null,source_year:valid?sourceYear:null,substituted:valid && substituted,
      status:valid?(substituted?'earliest_year_estimate':'observed'):'unavailable',
      metadata:metadata[String(valid?sourceYear:year)]||null};
  }
  return {resolve,positive};
});
