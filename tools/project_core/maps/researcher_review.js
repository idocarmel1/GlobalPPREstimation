/* Presentation of centrally registered researcher decisions, without scientific regrading. */
const PPRResearcherReview=(()=>{
  const node=(tag,text)=>{const e=document.createElement(tag);if(text!=null)e.textContent=text;return e;};
  const localLink=path=>{if(/^https?:\/\//i.test(path))return path;const [file,...anchor]=path.split('#');return '../'+file.split('/').map(encodeURIComponent).join('/')+(anchor.length?'#'+anchor.join('#'):'');};
  const isValidated=model=>model?.researcher_review?.status==='Validated by researcher';
  const isDisqualified=model=>model?.researcher_review?.status==='Disqualified by researcher';
  const nameClass=model=>isDisqualified(model)?'researcher-disqualified-name':isValidated(model)?'researcher-validated-name':'';
  function decorateName(element,model){
    if(!element)return;
    element.classList.remove('researcher-validated-name','researcher-disqualified-name');
    const className=nameClass(model);if(className)element.classList.add(className);
    element.style.color=isDisqualified(model)?'#b42318':isValidated(model)?'#187344':'#203c40';
    element.style.fontWeight=className?'600':'400';
  }
  function appendName(parent,model){
    parent.appendChild(document.createTextNode(' · '));
    const name=node('span',model?.label||model?.id||'No model');
    name.className=nameClass(model);
    parent.appendChild(name);
  }
  function append(parent,model){
    const review=model?.researcher_review;
    if(!review){const saved=model?.recorded_review_pending;const pending=node('p',saved?`${saved.recorded_status} recorded by ${saved.researcher_name||'unknown researcher'} (${saved.review_date||'date unavailable'}). Current verification pending: ${saved.reason}`:'Model not yet validated by researcher');pending.className='researcher-review-pending';parent.appendChild(pending);
      if(model?.validation_document){const report=node('a','Model validation document — pending researcher review');report.href=localLink(model.validation_document);parent.appendChild(report);}
      const provenance=model?.calculation_provenance;
      if(provenance?.det_collapse_mode==='auto'){
        const config=node('p','Selected configuration: det_collapse_mode=auto · '+(provenance.production_eligible===false?'Production-ineligible':'Eligibility requires review'));config.className='network-status';parent.appendChild(config);
        for(const flag of model.review_flags||[]){if(flag.startsWith('new_')){const grade=node('p',flag);grade.className='researcher-review-pending';parent.appendChild(grade);}}
        const region=(model.workbook||'').split('/').slice(0,-1).join('/');
        for(const [label,path] of [['Audited computational input',provenance.model_path],['Auto run settings and hashes',provenance.diagnostic_manifest]]){
          if(region&&path){const link=node('a',label);link.href=localLink(region+'/'+path);parent.appendChild(node('p'));parent.appendChild(link);}
        }
      }
      return false;}
    const wrap=node('div');wrap.className='researcher-review';
    if(isDisqualified(model)){
      const verdict=node('p',review.verdict);verdict.className='researcher-disqualified-name';wrap.appendChild(verdict);
      wrap.appendChild(node('p',review.reason));
      wrap.appendChild(node('p',review.researcher_name+' · '+review.review_date));
      const report=node('a','Researcher review report');report.href=localLink(review.report_path);wrap.appendChild(report);
      parent.appendChild(wrap);return true;
    }
    const status=node('p',review.status+' · '+review.researcher_name+' · '+review.review_date);status.className='researcher-validated-name';wrap.appendChild(status);
    // Adapt the original source snapshot for display without modifying its
    // approved text, identity hashes or centrally stored schema.
    const sections=review.sections.flatMap(section=>section.heading==='GE and TE diagnostics'
      ?(section.rows||[]).map(row=>({...section,heading:row.label+' diagnostics',rows:[{...row,label:null}]}))
      :[{...section,heading:section.heading==='Groups excluded from displayed PPR'?'SPPR Calculation Notes':section.heading}]);
    for(const section of sections){
      wrap.appendChild(node('h4',section.heading));
      for(const row of section.rows||[]){
        if(row.label)wrap.appendChild(node('strong',row.label));
        for(const segments of row.paragraphs){
          const p=node('p');
          for(const segment of segments){
            if(segment.href){const a=node('a',segment.text);a.href=localLink(segment.href);p.appendChild(a);}
            else p.appendChild(document.createTextNode(segment.text));
          }
          wrap.appendChild(p);
        }
      }
      for(const text of section.reference||[])wrap.appendChild(node('p',text));
      if(section.table){
        const table=node('table');table.setAttribute('aria-label','Taxon mapping confidence for 2019 landings');
        section.table.forEach((row,i)=>{const tr=node('tr');for(const value of row)tr.appendChild(node(i?'td':'th',value));table.appendChild(tr);});wrap.appendChild(table);
      }
      if(section.appendix_path){const a=node('a','Excel taxon appendix and Sources');a.href=localLink(section.appendix_path);wrap.appendChild(a);}
    }
    const note=node('p',review.note);note.className='researcher-note';wrap.appendChild(note);
    const links=node('p');links.className='researcher-review-links';const report=node('a','Researcher validation report');report.href=localLink(review.report_path);links.appendChild(report);wrap.appendChild(links);
    parent.appendChild(wrap);return true;
  }
  function selectionSummary(units,settings,unitIds){
    let excluded=0;const selectedKeys=new Set();
    for(const [id,u] of Object.entries(units)){
      if(unitIds&&!unitIds.includes(id))continue;
      const defaultId=typeof u.default_model==='number'?u.models?.[u.default_model]?.id:u.default_model;
      const model=u.models?.find(m=>m.id===(settings.models[id]||defaultId));excluded+=(model?.display_ppr_excluded_group_ids||[]).length;
      if(model)selectedKeys.add(id+'::'+model.id);
    }
    const manual=Object.keys(settings.selections).filter(key=>!unitIds||selectedKeys.has(key)).length;
    return excluded?`${excluded} groups excluded from displayed PPR by researcher${manual?` · ${manual} models with user selections`:''}`:manual?`${manual} models with group selections`:'All model groups included';
  }
  return {append,appendName,selectionSummary,isValidated,decorateName};
})();
