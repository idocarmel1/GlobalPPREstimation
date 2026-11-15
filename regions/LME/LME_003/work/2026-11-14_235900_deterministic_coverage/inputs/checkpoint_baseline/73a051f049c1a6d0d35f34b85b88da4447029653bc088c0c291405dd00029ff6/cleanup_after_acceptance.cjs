/* Explicit post-acceptance cleanup only. --prepare writes a reviewable plan;
 * --apply revalidates that exact plan before any deletion. No recursive delete.
 * A pending ledger disposition precedes unlink; only completed removals receive
 * final dispositions. Interrupted cleanup leaves an explicit pending journal.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const assert=require('node:assert/strict'),cp=require('node:child_process');
const WORK_REL='regions/LME/LME_003/work/2026-11-14_235900_deterministic_coverage';
const HUM_REL='regions/LME/LME_013/papers/HUM-2018/models/Chiaverano2018_detailed_Northern_Humboldt_1995_1998/model_validation/work/2026-11-15_011000_ee_floor_docx';
const INVENTORY_SHA='e729b933d175aaeee5ecf9dd4922a72714170074ddd314fbb701e41f5e4a96c4';
const RECOVERY_SHA='7fbcbee28594862f11517ff5cd39a12859040a17b30282d9ed0ac4963b552dd6';
const COLUMNS=['original_path','retained_path','sha256','retained_sha256','action','reason','unit_id','model_id','extraction_run_id'];
const RUN='2026-11-14_235900_deterministic_coverage';
const digest=data=>crypto.createHash('sha256').update(data).digest('hex');
const hash=p=>digest(fs.readFileSync(p));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sorted=x=>[...x].sort();

function safeRelative(name){
  assert.equal(typeof name,'string');
  assert(name && !/[\0:*?]/.test(name) && !path.posix.isAbsolute(name) && !path.win32.isAbsolute(name),'Absolute/unsafe path rejected');
  const parts=name.replaceAll('\\','/').split('/');
  assert(parts.every(p=>p && p!=='.' && p!=='..' && !/[. ]$/.test(p)),'Path traversal or Windows alias rejected');
  return parts.join('/');
}
function assertOwnedDeletion(name,work=WORK_REL,hum=HUM_REL){
  name=safeRelative(name);
  const bytecode=name.startsWith(work+'/code/__pycache__/') && name.endsWith('.pyc');
  const render=['baseline_render','final_render','temp'].some(d=>name.startsWith(hum+'/qa/'+d+'/'));
  const recovery=name===work+'/tmp/adoption_recovery_attempt3/manifest.json' ||
    (name.startsWith(work+'/tmp/adoption_recovery_attempt3/objects/') && /^[a-f0-9]{64}$/.test(name.split('/').at(-1)) && name.split('/').length===(work+'/tmp/adoption_recovery_attempt3/objects/x').split('/').length);
  assert(bytecode || render || recovery || name===work+'/inputs/Project_before_humboldt_review.xlsx','Deletion outside explicit temporary scope');
  assert(!name.endsWith('.lock'),'Lock deletion forbidden');
  return name;
}
function parseCsv(text){
  text=String(text).replace(/^\uFEFF/,'');
  const rows=[];let row=[],value='',quoted=false,closed=false;
  for(let i=0;i<text.length;i++){
    const c=text[i];
    if(quoted){if(c==='"'){if(text[i+1]==='"'){value+='"';i++;}else{quoted=false;closed=true;}}else value+=c;continue;}
    if(c==='"'){assert(!value && !closed,'Malformed CSV quote');quoted=true;}
    else if(c===','){row.push(value);value='';closed=false;}
    else if(c==='\r' || c==='\n'){if(c==='\r' && text[i+1]==='\n')i++;row.push(value);rows.push(row);row=[];value='';closed=false;}
    else{assert(!closed,'Characters after CSV quoted field');value+=c;}
  }
  assert(!quoted,'Unterminated CSV field');
  if(value || row.length || closed){row.push(value);rows.push(row);}
  return rows;
}
function encodeCsvRows(rows){
  return rows.map(row=>row.map(v=>{v=String(v??'');return /[",\r\n]/.test(v)?'"'+v.replaceAll('"','""')+'"':v;}).join(',')).join('\r\n')+'\r\n';
}
function assertAcceptanceShape(x){
  assert.equal(x.status.phase,'COMPLETED','Adoption is not completed');assert.equal(x.status.exit_code,0);
  assert.equal(x.publication.scientific_execution_performed,false);
  assert.equal(x.current['Project.xlsx'],x.publication.project_sha256,'Project differs from adoption');
  assert.equal(x.final.status,'PASS_FINAL_PUBLICATION');assert.equal(x.final.project_sha256,x.current['Project.xlsx']);
  assert.equal(x.final.validated_pairs,16);assert.equal(x.final.researcher_exclusions,57);
  assert.equal(x.final.preservation_evidence.adoption_sha256,x.adoptionHash,'Final QA used another adoption certificate');
  assert.equal(x.final.pages.length,2);
  assert.deepEqual(sorted(x.final.pages.map(p=>p.path)),['interactive_map/index.html','interactive_map/trends.html']);
  for(const p of x.final.pages){assert.equal(p.sha256,x.current[p.path]);assert.equal(p.project_sha256,x.current['Project.xlsx']);}
  assert.equal(x.browser.status,'PASS');assert.deepEqual(x.browser.page_errors,[]);
  assert(x.browser.checks.length>=7 && x.browser.checks.every(c=>c.status==='PASS'));
  for(const p of ['Project.xlsx','interactive_map/index.html','interactive_map/trends.html']){
    assert.equal(x.browser.source_sha256_before[p],x.current[p]);assert.equal(x.browser.source_sha256_after[p],x.current[p]);
  }
  assert.equal(x.table.passed,true);assert(x.table.source_sha256,'Table QA has no source fingerprints');
  for(const p of ['Project.xlsx','interactive_map/trends.html'])assert.equal(x.table.source_sha256[p],x.current[p]);
  assert.equal(x.units.length,16);assert.equal(new Set(x.units).size,16);
  for(const basis of ['landings','catch']){
    const rows=x.table.tables[basis].rows;assert.deepEqual(sorted(rows.map(r=>r.id)),sorted(x.units));
    for(const r of rows)assert(Number.isFinite(r.values[0].value),'Fixed-1995 table value unavailable');
  }
  const expected=x.units.flatMap(u=>['landings','catch'].map(b=>u+'/'+b));
  assert.deepEqual(sorted(x.table.annual_checks.map(c=>c.unit_id+'/'+c.catch_basis)),sorted(expected));
  for(const c of x.table.annual_checks)assert(c.passed===true && Number.isInteger(c.years_with_control_results) && c.years_with_control_results>=0 && c.years_with_control_results<=70);
}

function context(){
  const work=path.resolve(__dirname,'..');let root=work;
  while(!fs.existsSync(path.join(root,'Project.xlsx'))){const next=path.dirname(root);assert.notEqual(next,root);root=next;}
  root=fs.realpathSync.native(root);
  assert.equal(fs.realpathSync.native(work).toLowerCase(),path.join(root,...WORK_REL.split('/')).toLowerCase(),'Wrong workspace');
  return {root,work:path.join(root,...WORK_REL.split('/'))};
}
function local(ctx,name){
  name=safeRelative(name);const p=path.resolve(ctx.root,...name.split('/'));
  const relative=path.relative(ctx.root,p);assert(relative && !relative.startsWith('..'+path.sep) && !path.isAbsolute(relative),'Path escaped workspace');
  return p;
}
function ancestors(ctx,p){
  const result=[];
  for(let q=p;;q=path.dirname(q)){result.push(q);if(q===ctx.root)break;assert(q!==path.dirname(q) && !path.relative(ctx.root,q).startsWith('..'),'Parent escaped workspace');}
  return result;
}
function checkLinks(ctx,p){
  for(const q of ancestors(ctx,p))if(fs.existsSync(q)){
    assert(!fs.lstatSync(q).isSymbolicLink(),'Symbolic link/junction rejected: '+q);
    assert.equal(fs.realpathSync.native(q).toLowerCase(),q.toLowerCase(),'Redirected path rejected: '+q);
  }
}
function checkReparse(ctx,paths){
  assert.equal(process.platform,'win32','This bounded cleanup is for the Windows workspace');
  const all=sorted(new Set(paths.flatMap(p=>ancestors(ctx,p)).filter(p=>fs.existsSync(p))));
  for(const p of paths)checkLinks(ctx,p);
  const script='$ErrorActionPreference="Stop"; $cleanupPaths=ConvertFrom-Json ([Console]::In.ReadToEnd()); $cleanupBad=@(); foreach($cleanupPath in $cleanupPaths){ if(([int][System.IO.File]::GetAttributes([string]$cleanupPath) -band 1024) -ne 0){$cleanupBad+= [string]$cleanupPath} }; [Console]::Out.Write((ConvertTo-Json -InputObject @($cleanupBad) -Compress))';
  const output=cp.execFileSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',script],{input:JSON.stringify(all),encoding:'utf8',windowsHide:true});
  assert.deepEqual(JSON.parse(output.trim()||'[]'),[],'Reparse point rejected');
}
function verifyFile(ctx,name,expected){
  const p=local(ctx,name);checkLinks(ctx,p);assert(fs.statSync(p).isFile());assert.equal(hash(p),expected,'File hash changed: '+name);return p;
}
function assertNoLocks(ctx,own=false){
  for(const name of ['.project-write.lock',WORK_REL+'/tmp/adoption_supervisor.lock',...(own?[]:[WORK_REL+'/qa/cleanup_after_acceptance.lock'])])
    assert(!fs.existsSync(local(ctx,name)),'Active or unreconciled lock blocks cleanup: '+name);
}
function atomicWrite(ctx,p,bytes,expected){
  checkLinks(ctx,p);const current=fs.existsSync(p)?hash(p):null;assert.equal(current,expected,'Output changed before write: '+p);
  const temporary=p+'.cleanup-'+process.pid+'.tmp';assert(!fs.existsSync(temporary),'Temporary write collision');
  let created=false;
  try{const fd=fs.openSync(temporary,'wx');created=true;try{fs.writeFileSync(fd,bytes);fs.fsyncSync(fd);}finally{fs.closeSync(fd);}
    assert.equal(fs.existsSync(p)?hash(p):null,expected);fs.renameSync(temporary,p);created=false;
  }finally{if(created)fs.unlinkSync(temporary);}
}
function snapshotAcceptance(ctx){
  assertNoLocks(ctx);const bound={};
  const load=name=>{const p=local(ctx,name);checkLinks(ctx,p);bound[name]=hash(p);return read(p);};
  const names={status:WORK_REL+'/outputs/background_adoption_status.json',publication:WORK_REL+'/outputs/adoption_publication.json',
    final:WORK_REL+'/qa/final_publication_verification.json',browser:WORK_REL+'/qa/browser/production_browser_verification.json',table:WORK_REL+'/qa/time_series_table_verification.json'};
  const data={};for(const [key,name] of Object.entries(names))data[key]=load(name);
  const inventory=load(WORK_REL+'/inputs/validated_inventory.json');data.units=inventory.pairs.map(r=>r.unit_id);
  data.current={};for(const name of ['Project.xlsx','interactive_map/index.html','interactive_map/trends.html']){data.current[name]=hash(local(ctx,name));bound[name]=data.current[name];}
  data.adoptionHash=bound[names.publication];assertAcceptanceShape(data);
  assert(data.final.consumed_files && Object.keys(data.final.consumed_files).length,'Final acceptance has no consumed-file bindings');
  for(const [name,h]of Object.entries(data.final.consumed_files)){verifyFile(ctx,name,h);if(bound[name])assert.equal(bound[name],h);bound[name]=h;}
  for(const [name,h]of Object.entries(bound))verifyFile(ctx,name,h);
  return {files:bound,project_sha256:data.current['Project.xlsx'],qa_paths:names};
}
function collectFiles(ctx,directory){
  const files=[],dirs=[];
  function walk(p){checkLinks(ctx,p);dirs.push(p);for(const entry of fs.readdirSync(p,{withFileTypes:true})){
    const q=path.join(p,entry.name);assert(!entry.isSymbolicLink());if(entry.isDirectory())walk(q);else{assert(entry.isFile());files.push(q);}
  }}
  walk(directory);return {files,dirs};
}
function ledgerRow(item,pending=false){
  const hum=item.path.startsWith(HUM_REL+'/');
  return [item.path,item.retained_path||'',item.sha256,item.retained_path?item.sha256:'',pending?'cleanup_pending':item.action,
    (pending?'Pending bounded cleanup; intended action '+item.action+'. ':'')+item.reason,hum?'LME_013':'LME_003',
    hum?'Chiaverano2018_detailed_Northern_Humboldt_1995_1998':'',RUN];
}
function appendRows(original,rows){
  if(!rows.length)return original;
  return Buffer.concat([original,original.length && !/[\r\n]$/.test(original.toString('utf8'))?Buffer.from('\r\n'):Buffer.alloc(0),Buffer.from(encodeCsvRows(rows),'utf8')]);
}
function buildPlan(ctx){
  const acceptance=snapshotAcceptance(ctx),inventoryName=WORK_REL+'/qa/final_cleanup_inventory.json';
  const inventory=read(verifyFile(ctx,inventoryName,INVENTORY_SHA));
  const audit=read(local(ctx,WORK_REL+'/outputs/final_cohort_audit.json'));assert.equal(hash(local(ctx,WORK_REL+'/outputs/final_cohort_audit.json')),inventory.required_retention.audit_sha256);
  const items=[];
  function add(name,h,reason,retained_path=''){
    name=assertOwnedDeletion(name);assert(!Object.hasOwn(audit.protected_files,name),'Scientific proof deletion rejected');
    const p=verifyFile(ctx,name,h);items.push({path:name,sha256:h,bytes:fs.statSync(p).size,reason,retained_path,action:retained_path?'relocated':'obsolete_removed'});
  }
  for(const item of inventory.candidate_files){assert(item.post_acceptance_candidate && !item.hard_proof_overlap);add(item.path,item.sha256,'Accepted '+RUN+' temporary '+item.category+'; retained source and compact QA. '+item.reason);}
  const recovery=inventory.tmp_inventory.recovery_package;
  assert.equal(recovery.manifest_sha256,RECOVERY_SHA);const manifest=read(verifyFile(ctx,recovery.manifest_path,RECOVERY_SHA));
  const digests=sorted(new Set(manifest.entries.map(e=>e.before_sha256).filter(Boolean)));assert.equal(digests.length,961);assert.equal(manifest.entries.length,1052);
  const recovered=collectFiles(ctx,local(ctx,recovery.path));const expected=['manifest.json',...digests.map(h=>'objects/'+h)].sort();
  assert.deepEqual(recovered.files.map(p=>path.relative(local(ctx,recovery.path),p).split(path.sep).join('/')).sort(),expected,'Recovery package has unexpected content');
  for(const h of digests){assert(/^[a-f0-9]{64}$/.test(h));add(recovery.path+'/objects/'+h,h,'Completed transaction backup retired after final acceptance; exact original paths/hashes retained in '+recovery.manifest_copy_target);}
  const backupName=inventory.conditional_project_snapshot.path;
  if(fs.existsSync(local(ctx,backupName)))add(backupName,hash(local(ctx,backupName)),'Completed pre-Humboldt-registration transaction snapshot; final publication and exact review QA retained');
  // The original manifest is removed last, after its exact compact copy exists.
  add(recovery.manifest_path,RECOVERY_SHA,'Completed transaction manifest retired to compact QA after final acceptance',recovery.manifest_copy_target);
  assert.equal(new Set(items.map(i=>i.path.toLowerCase())).size,items.length,'Duplicate deletion target');
  const copyTarget=local(ctx,recovery.manifest_copy_target);if(fs.existsSync(copyTarget))assert.equal(hash(copyTarget),RECOVERY_SHA,'Retired manifest collision');
  const directoryNames=new Set(recovered.dirs.map(p=>path.relative(ctx.root,p).split(path.sep).join('/')));
  for(const dir of [WORK_REL+'/code/__pycache__',...['baseline_render','final_render','temp'].map(d=>HUM_REL+'/qa/'+d)])
    if(fs.existsSync(local(ctx,dir)))for(const p of collectFiles(ctx,local(ctx,dir)).dirs)directoryNames.add(path.relative(ctx.root,p).split(path.sep).join('/'));
  const ledgerName='common_reference_data/provenance/source_paths.csv',ledgerPath=local(ctx,ledgerName),ledgerBytes=fs.readFileSync(ledgerPath);
  const csv=parseCsv(ledgerBytes.toString('utf8'));assert.deepEqual(csv[0],COLUMNS);assert(csv.slice(1).every(r=>r.length===COLUMNS.length),'Malformed existing ledger');
  const targetSet=new Set(items.map(i=>i.path));assert(!csv.slice(1).some(r=>targetSet.has(r[0]) && ['cleanup_pending','obsolete_removed','relocated'].includes(r[4])),'Existing cleanup disposition requires reconciliation');
  checkReparse(ctx,[...items.map(i=>local(ctx,i.path)),copyTarget,ledgerPath,...[...directoryNames].map(n=>local(ctx,n))]);
  return {schema_version:1,status:'PREPARED_AFTER_ACCEPTANCE',helper_sha256:hash(__filename),inventory_path:inventoryName,inventory_sha256:INVENTORY_SHA,
    acceptance,ledger:{path:ledgerName,before_sha256:digest(ledgerBytes),columns:COLUMNS},manifest_copy:{source:recovery.manifest_path,destination:recovery.manifest_copy_target,sha256:RECOVERY_SHA},
    items,empty_directories:[...directoryNames].sort((a,b)=>b.split('/').length-a.split('/').length||a.localeCompare(b)),
    total_bytes:items.reduce((n,i)=>n+i.bytes,0),recovery_manifest_entries:1052,
    guard:'No canonical scientific paths, recursive deletion, lock removal, solver or workbook parsing. --apply must revalidate this exact plan.'};
}
function prepare(ctx){
  const plan=buildPlan(ctx),p=local(ctx,WORK_REL+'/qa/prepared_cleanup_plan.json');
  atomicWrite(ctx,p,Buffer.from(JSON.stringify(plan,null,2)+'\n'),fs.existsSync(p)?hash(p):null);
  console.log(JSON.stringify({mode:'prepare',plan:WORK_REL+'/qa/prepared_cleanup_plan.json',sha256:hash(p),files:plan.items.length,bytes:plan.total_bytes,deletions_performed:false},null,2));
}
function apply(ctx){
  const planName=WORK_REL+'/qa/prepared_cleanup_plan.json',planPath=local(ctx,planName),prepared=read(planPath),planHash=hash(planPath);
  assert.equal(prepared.helper_sha256,hash(__filename),'Prepared plan used another helper');
  const plan=buildPlan(ctx);assert.deepEqual(plan,prepared,'Prepared cleanup plan is stale; prepare/review again');
  const ownLock=local(ctx,WORK_REL+'/qa/cleanup_after_acceptance.lock');const lockBytes=Buffer.from(String(process.pid));
  const fd=fs.openSync(ownLock,'wx');try{fs.writeFileSync(fd,lockBytes);}finally{fs.closeSync(fd);}
  const resultPath=local(ctx,WORK_REL+'/qa/cleanup_after_acceptance_result.json'),events=local(ctx,WORK_REL+'/qa/cleanup_after_acceptance_events.jsonl');
  const removed=[],removedDirs=[];let ledgerBase,ledgerCurrent,manifestCopied=false,error=null;
  const event=record=>fs.appendFileSync(events,JSON.stringify({timestamp:new Date().toISOString(),...record})+'\n','utf8');
  const ledgerPath=local(ctx,plan.ledger.path);
  try{
    assertNoLocks(ctx,true);assert.equal(hash(planPath),planHash);
    for(const [name,h]of Object.entries(plan.acceptance.files))verifyFile(ctx,name,h);
    const source=verifyFile(ctx,plan.manifest_copy.source,plan.manifest_copy.sha256),destination=local(ctx,plan.manifest_copy.destination);
    checkReparse(ctx,[source,destination,ledgerPath]);
    if(!fs.existsSync(destination)){atomicWrite(ctx,destination,fs.readFileSync(source),null);manifestCopied=true;}
    assert.equal(hash(destination),RECOVERY_SHA);
    ledgerBase=fs.readFileSync(ledgerPath);assert.equal(digest(ledgerBase),plan.ledger.before_sha256);
    const pending=appendRows(ledgerBase,plan.items.map(i=>ledgerRow(i,true)));
    atomicWrite(ctx,ledgerPath,pending,plan.ledger.before_sha256);ledgerCurrent=digest(pending);
    event({event:'BEGIN',plan:planName,plan_sha256:planHash,files:plan.items.length,ledger_pending_sha256:ledgerCurrent,retired_manifest_sha256:RECOVERY_SHA});
    for(const item of plan.items){
      assertNoLocks(ctx,true);assertOwnedDeletion(item.path);const p=verifyFile(ctx,item.path,item.sha256);
      if(item.retained_path)verifyFile(ctx,item.retained_path,item.sha256);
      event({event:'UNLINK_INTENT',path:item.path,sha256:item.sha256});fs.unlinkSync(p);removed.push(item);
      event({event:'UNLINK_DONE',path:item.path,sha256:item.sha256});
    }
    for(const name of plan.empty_directories){
      assertNoLocks(ctx,true);const p=local(ctx,name);if(!fs.existsSync(p))continue;checkLinks(ctx,p);
      if(fs.readdirSync(p).length===0){fs.rmdirSync(p);removedDirs.push(name);event({event:'EMPTY_DIRECTORY_REMOVED',path:name});}
    }
    for(const [name,h]of Object.entries(plan.acceptance.files))verifyFile(ctx,name,h);
  }catch(e){error=e;}
  finally{
    try{
      if(ledgerBase && ledgerCurrent){
        const directoryRows=removedDirs.map(name=>ledgerRow({path:name,sha256:'',action:'empty_directory_removed',reason:'Verified empty after accepted bounded temporary-file cleanup'}));
        const final=appendRows(ledgerBase,[...removed.map(i=>ledgerRow(i)),...directoryRows]);
        atomicWrite(ctx,ledgerPath,final,ledgerCurrent);ledgerCurrent=digest(final);
      }
      const report={schema_version:1,status:error?'FAILED_PARTIAL_CLEANUP':'COMPLETED',timestamp:new Date().toISOString(),plan:planName,plan_sha256:planHash,
        helper_sha256:hash(__filename),project_sha256:plan.acceptance.project_sha256,manifest_copy:plan.manifest_copy,manifest_copy_created:manifestCopied,
        removed_files:removed.map(i=>({path:i.path,sha256:i.sha256,bytes:i.bytes,action:i.action})),removed_empty_directories:removedDirs,
        ledger_sha256:ledgerCurrent||hash(ledgerPath),error:error?{message:error.message,stack:error.stack}:null,recursive_deletion_performed:false,scientific_execution_performed:false};
      atomicWrite(ctx,resultPath,Buffer.from(JSON.stringify(report,null,2)+'\n'),fs.existsSync(resultPath)?hash(resultPath):null);
      console.log(JSON.stringify({status:report.status,removed_files:removed.length,removed_empty_directories:removedDirs.length,result:WORK_REL+'/qa/cleanup_after_acceptance_result.json',sha256:hash(resultPath)},null,2));
    }finally{
      if(fs.existsSync(ownLock) && fs.readFileSync(ownLock).equals(lockBytes))fs.unlinkSync(ownLock);
    }
  }
  if(error)throw error;
}

module.exports={safeRelative,assertOwnedDeletion,parseCsv,encodeCsvRows,assertAcceptanceShape};
if(require.main===module){
  try{assert(process.argv.length===3 && ['--prepare','--apply'].includes(process.argv[2]),'Use exactly --prepare or --apply');
    const ctx=context();if(process.argv[2]==='--prepare')prepare(ctx);else apply(ctx);
  }catch(e){console.error(e.stack||String(e));process.exitCode=1;}
}
