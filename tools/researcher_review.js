/* Presentation of centrally registered researcher decisions, without scientific regrading. */
const PPRResearcherReview=(()=>{
  const node=(tag,text)=>{const e=document.createElement(tag);if(text!=null)e.textContent=text;return e;};
  const localLink=path=>{if(/^https?:\/\//i.test(path))return path;const [file,...anchor]=path.split('#');return '../'+file.split('/').map(encodeURIComponent).join('/')+(anchor.length?'#'+anchor.join('#'):'');};
  function appendName(parent,model){
    parent.appendChild(document.createTextNode(' · '));
    const name=node('span',model?.label||model?.id||'No model');
    if(model?.researcher_review)name.className='researcher-validated-name';
    parent.appendChild(name);
  }
  function append(parent,model){
    const review=model?.researcher_review;
    if(!review){const pending=node('p','Model not yet validated by researcher');pending.className='researcher-review-pending';parent.appendChild(pending);return false;}
    const wrap=node('div');wrap.className='researcher-review';
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
  function selectionSummary(units,settings){
    let excluded=0;
    for(const [id,u] of Object.entries(units)){
      const defaultId=typeof u.default_model==='number'?u.models?.[u.default_model]?.id:u.default_model;
      const model=u.models?.find(m=>m.id===(settings.models[id]||defaultId));excluded+=(model?.display_ppr_excluded_group_ids||[]).length;
    }
    const manual=Object.keys(settings.selections).length;
    return excluded?`${excluded} groups excluded from displayed PPR by researcher${manual?` · ${manual} models with user selections`:''}`:manual?`${manual} models with group selections`:'All model groups included';
  }
  return {append,appendName,selectionSummary};
})();
