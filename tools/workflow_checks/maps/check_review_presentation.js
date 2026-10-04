const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
class Element {
  constructor(tag,text=''){this.tag=tag;this.textContent=text;this.children=[];this.className='';}
  appendChild(child){this.children.push(child);return child;}
  setAttribute(key,value){this[key]=value;}
}
const document={createElement:tag=>new Element(tag),createTextNode:text=>new Element('#text',text)};
const context={document};vm.createContext(context);
vm.runInContext(fs.readFileSync(require('node:path').resolve(__dirname,'../../project_core/maps/researcher_review.js'),'utf8'),context);
const review=vm.runInContext('PPRResearcherReview',context);
const collect=e=>e.textContent+e.children.map(collect).join('');
const pending=new Element('div');assert.equal(review.append(pending,{id:'pending',review_flags:['WARN'],review_note:'provisional'}),false);
assert.equal(pending.children.length,1);assert.equal(collect(pending),'Model not yet validated by researcher');
assert.equal(pending.children[0].className,'researcher-review-pending');
const row=text=>({text,paragraphs:[[{text}]]});
const model={researcher_review:{status:'Validated by researcher',researcher_name:'Reviewer',review_date:'2026-09-30',
  sections:[{heading:'Model extraction notes',rows:[row('Exact extraction')]},
    {heading:'GE and TE diagnostics',rows:[{...row('rho_living = 0.32'),label:'GE'},{...row('Exact TE'),label:'TE'}]},
    {heading:'Groups excluded from displayed PPR',rows:[row('Exact SPPR')]},
    {heading:'Geographic fit',rows:[row('Exact geography')]},{heading:'Taxon mapping confidence',reference:['2019 landings']}],
  note:'Approved closing note',report_path:'regions/review.docx'}};
const snapshot=JSON.stringify(model),approved=new Element('div');assert.equal(review.append(approved,model),true);
assert.deepEqual(approved.children[0].children.filter(e=>e.tag==='h4').map(e=>e.textContent),
  ['Model extraction notes','GE diagnostics','TE diagnostics','SPPR Calculation Notes','Geographic fit','Taxon mapping confidence']);
assert.equal(JSON.stringify(model),snapshot,'Presentation must retain the approved source snapshot');
assert(collect(approved).includes('rho_living = 0.32'));assert(collect(approved).includes('Approved closing note'));
assert(collect(approved).includes('Reviewer'));assert(!collect(approved).includes('Model not yet validated'));
const reason='Reason – too strong living compartments recycling due to near-zero EE values (rho_living = 0.99).';
const rejectedModel={id:'rejected',label:'Original model label',researcher_review:{
  status:'Disqualified by researcher',verdict:'MODEL DISQUALIFIED',reason,
  researcher_name:'Reviewer',review_date:'2026-10-02',sections:[],report_path:'regions/review.docx'}};
const rejected=new Element('div');assert.equal(review.append(rejected,rejectedModel),true);
assert.equal(rejected.children[0].children[0].textContent,'MODEL DISQUALIFIED');
assert.equal(rejected.children[0].children[1].textContent,reason,'Exact reason is immediately under the verdict');
assert.equal(rejected.children[0].children[0].className,'researcher-disqualified-name');
assert(!collect(rejected).includes('Model not yet validated'));
const named=new Element('div');review.appendName(named,rejectedModel);
assert.equal(named.children[1].textContent,'Original model label');
assert.equal(named.children[1].className,'researcher-disqualified-name');
assert.equal(review.isValidated(rejectedModel),false);assert.equal(review.isValidated(model),true);
console.log('Review presentation passed: exact pending message, six flat headings, original review content and source snapshot retained.');

