/* Isolated browser regression for the completed publication. No user profile. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {pathToFileURL}=require('node:url');

const WORK=path.resolve(__dirname,'..');
let ROOT=WORK;
while(!fs.existsSync(path.join(ROOT,'Project.xlsx'))){
  const next=path.dirname(ROOT);assert.notEqual(next,ROOT,'Cannot find project root');ROOT=next;
}
const QA=path.join(WORK,'qa','browser');
const MODULES='C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const MODEL='Chiaverano2018_detailed_Northern_Humboldt_1995_1998';
const METHODS=['simple trophic chain','SPPR_1995_TE0.1','new_GE','new_TE_EEfix'];
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const relative=p=>path.relative(ROOT,p).split(path.sep).join('/');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));

async function main(){
  assert(process.argv.includes('--publication-ready'),
    'Run only after coordinator confirms completed publication: node verify_browser.cjs --publication-ready');
  const publicationPath=path.join(WORK,'outputs','adoption_publication.json');
  assert(fs.existsSync(publicationPath),'Completed adoption publication record is required');
  const publication=read(publicationPath);
  const project=path.join(ROOT,'Project.xlsx');
  assert.equal(hash(project),publication.project_sha256,'Project must match completed adoption record');
  const files=[project,path.join(ROOT,'interactive_map','trends.html'),path.join(ROOT,'interactive_map','index.html')];
  const before=Object.fromEntries(files.map(p=>[relative(p),hash(p)]));
  const expectedUnits=read(path.join(WORK,'inputs','validated_inventory.json')).pairs.map(p=>p.unit_id).sort();
  assert.equal(expectedUnits.length,16);
  fs.mkdirSync(QA,{recursive:true});
  const temporary=path.join(WORK,'tmp');fs.mkdirSync(temporary,{recursive:true});
  process.env.TEMP=temporary;process.env.TMP=temporary;process.env.TMPDIR=temporary;
  const {chromium}=require(path.join(MODULES,'playwright'));
  const executable=[process.env.PPR_BROWSER_EXECUTABLE,
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    chromium.executablePath()].find(p=>p&&fs.existsSync(p));
  assert(executable,'No installed Chromium executable; no download is performed');
  const report={schema_version:1,started_at:new Date().toISOString(),status:'RUNNING',
    test_scope:'Production pages in new isolated headless Chromium contexts; no existing browser session or user profile',
    playwright_version:read(path.join(MODULES,'playwright','package.json')).version,
    executable,source_sha256_before:before,checks:[],page_errors:[],request_failures:[],screenshots:[]};
  let browser,currentPage;
  const check=(name,details)=>{report.checks.push({name,status:'PASS',details});console.log('PASS '+name);};
  const watch=(page,label)=>{
    page.on('pageerror',error=>report.page_errors.push({page:label,message:error.message}));
    page.on('requestfailed',request=>report.request_failures.push({page:label,url:request.url(),error:request.failure()?.errorText}));
  };
  const screenshot=async(page,name,selector)=>{
    const target=path.join(QA,name);
    if(selector)await page.locator(selector).screenshot({path:target,animations:'disabled'});
    else await page.screenshot({path:target,fullPage:true,animations:'disabled'});
    report.screenshots.push({path:relative(target),sha256:hash(target)});
  };
  try{
    browser=await chromium.launch({headless:true,executablePath:executable,timeout:60000});
    report.browser_version=browser.version();
    const trendsContext=await browser.newContext({viewport:{width:1600,height:1200},deviceScaleFactor:1});
    const trends=await trendsContext.newPage();currentPage=trends;watch(trends,'trends');
    trends.setDefaultTimeout(30000);
    await trends.goto(pathToFileURL(files[1]).href,{waitUntil:'domcontentloaded',timeout:120000});
    await trends.waitForFunction(()=>document.querySelectorAll('#chart [data-method]').length===4);
    assert.equal(await trends.locator('meta[name="ppr-project-sha256"]').getAttribute('content'),before['Project.xlsx']);
    const defaults={catchBasis:'landings',uncertainty:'1',metric:'ratio',baselineMethod:'',
      sourceScope:'all',nppScope:'global',nppFill:'earliest',unidentifiedTreatment:'method',
      groupDisplay:'total',globalApproximation:'0',regionReviewFilter:'validated',fromYear:'1950',toYear:'2019'};
    const controls={};
    for(const [id,value]of Object.entries(defaults)){
      const control=trends.locator('#'+id);assert.equal(await control.count(),1,id+' exists');
      assert(await control.isVisible(),id+' is visible');assert.equal(await control.inputValue(),value,id);
      controls[id]={value:await control.inputValue(),label:await control.locator('option:checked').innerText()};
    }
    assert.match(await trends.locator('#groupFilterSummary').innerText(),/^57 groups excluded from displayed PPR by researcher/);
    check('Visible fresh-context trend defaults and 57 researcher exclusions',controls);
    await trends.locator('#chooseEcosystems').click();
    assert.equal(await trends.locator('#ecosystemSet').inputValue(),'validated');
    const selected=await trends.locator('#ecosystemList input[type=checkbox]:checked').evaluateAll(nodes=>nodes.map(n=>n.value).sort());
    assert.deepEqual(selected,expectedUnits);
    assert.match(await trends.locator('#pickerCount').innerText(),/^16 selected/);
    await screenshot(trends,'validated-ecosystems.png','#ecosystemDialog');
    await trends.locator('#doneEcosystems').click();
    check('Visible picker contains exactly the sixteen validated ecosystems',selected);
    await trends.locator('#pprMethod').click();
    const methods=await trends.locator('#methodList input[type=checkbox]:checked').evaluateAll(nodes=>nodes.map(n=>({
      id:SERIES_DB.ppr_methods[Number(n.id.replace('method_',''))]?.id,
      label:n.closest('label').innerText
    })));
    assert.deepEqual(methods.map(m=>m.id),METHODS);
    assert.equal(await trends.locator('#methodCount').innerText(),'4 selected');
    await screenshot(trends,'selected-methods.png','#methodDialog');
    await trends.locator('#doneMethods').click();
    check('Visible method picker contains the requested four methods',methods);
    const chart=await trends.locator('#chart').evaluate(svg=>({
      viewBox:svg.getAttribute('viewBox'),title:svg.querySelector('title')?.textContent,
      description:svg.querySelector('desc')?.textContent,
      methods:[...svg.querySelectorAll('[data-method]')].map(g=>({id:g.dataset.method,
        paths:[...g.querySelectorAll('path')].map(p=>p.getAttribute('d')).filter(Boolean)}))
    }));
    assert.deepEqual(chart.methods.map(m=>m.id),METHODS);
    assert(chart.methods.every(m=>m.paths.some(d=>/^M/.test(d))),'Each requested curve has actual SVG path geometry');
    assert.match(chart.description,/1950 to 2019/);
    assert(await trends.locator('#emptyState').isHidden(),'Chart is not an empty result');
    assert.equal(await trends.locator('#seriesLegend b').count(),4);
    await screenshot(trends,'trends-defaults.png','.chart-card');
    check('Four production curves render over 1950-2019',chart);
    await trendsContext.close();

    // A second clean context ensures inspecting the map does not inherit any
    // presentation or model/group preferences from the trends interaction.
    const mapContext=await browser.newContext({viewport:{width:1600,height:1200},deviceScaleFactor:1});
    const mapPage=await mapContext.newPage();currentPage=mapPage;watch(mapPage,'map');
    mapPage.setDefaultTimeout(30000);
    await mapPage.goto(pathToFileURL(files[2]).href,{waitUntil:'domcontentloaded',timeout:120000});
    await mapPage.waitForFunction(()=>document.querySelectorAll('#regionList .region-btn').length>0);
    assert.equal(await mapPage.locator('meta[name="ppr-project-sha256"]').getAttribute('content'),before['Project.xlsx']);
    await mapPage.locator('#rankSetFilter').selectOption('all');
    await mapPage.locator('#rankFilter').selectOption('all');
    await mapPage.locator('#search').fill('LME_013');
    await mapPage.waitForFunction(()=>document.querySelectorAll('#regionList .region-btn').length===1);
    await mapPage.locator('#regionList .region-btn').click();
    await mapPage.locator('#modelFilter').waitFor({state:'visible'});
    const target=await mapPage.evaluate(modelId=>{
      const unit=DB.network.units.LME_013,index=unit.models.findIndex(m=>m.id===modelId);
      if(index<0)throw Error('Exact Humboldt model missing');
      const model=unit.models[index];return {index,id:model.id,label:model.label,health:model.health,
        review_status:model.researcher_review?.status,excluded:model.display_ppr_excluded_group_ids};
    },MODEL);
    await mapPage.locator('#modelFilter').selectOption(String(target.index));
    assert.match(await mapPage.locator('#details .code').innerText(),/LME_013/);
    assert.equal(await mapPage.locator('#modelFilter').inputValue(),String(target.index));
    assert.equal(target.review_status,'Validated by researcher');
    assert.deepEqual(target.excluded,['Fishery offal','Pinnipeds','Seabirds','Chrysaora plocamia']);
    const review=mapPage.locator('#details .researcher-review');await review.waitFor({state:'visible'});
    const reviewText=await review.innerText();
    assert.match(reviewText,/Validated by researcher.*Ido Carmel.*2026-10-08/);
    assert.match(reviewText,/GE diagnostics/);assert.match(reviewText,/TE diagnostics/);
    assert.match(reviewText,/WARN: successful pooled-detritus GE result with EE floor 0\.1/);
    assert.match(reviewText,/WARN: EE-floor TE result/);
    assert.match(reviewText,/Unpooled option: FAIL/);
    assert.match(reviewText,/saved engine aggregate grade remains FAIL/);
    assert.equal(target.health.GE.status,'FAIL','Raw saved GE aggregate remains FAIL');
    assert.equal(target.health.TE.status,'WARN','Raw saved TE remains WARN');
    const modelColor=await mapPage.locator('#modelFilter').evaluate(element=>getComputedStyle(element).color);
    assert.equal(modelColor,'rgb(24, 115, 68)','Exact selected model shows validated green styling');
    await screenshot(mapPage,'humboldt-map.png');
    await screenshot(mapPage,'humboldt-review.png','#details .researcher-review');
    check('Humboldt visible review preserves validated pooled GE WARN, TE WARN, and raw GE FAIL distinction',
      {...target,modelColor,reviewText});
    // Inspect the raw GE diagnostic through the normal controls as well.
    await mapPage.locator('#metricMode').selectOption('b');
    await mapPage.locator('#teFilter').selectOption('GE');
    assert.match(await mapPage.locator('#details .network-status').first().innerText(),/FAIL/);
    await screenshot(mapPage,'humboldt-raw-ge-diagnostic.png');
    check('Map raw GE diagnostic visibly retains FAIL');
    await sleep(300);
    assert.deepEqual(report.page_errors,[],'No browser JavaScript pageerror on either production page');
    check('No browser JavaScript pageerrors');
    await mapContext.close();
    report.status='PASS';
  }catch(error){
    report.status='FAIL';report.error={message:error.message,stack:error.stack};
    if(currentPage&&!currentPage.isClosed()){
      try{await screenshot(currentPage,'failure.png');}catch(screenshotError){report.failure_screenshot_error=screenshotError.message;}
    }
    process.exitCode=1;
  }finally{
    if(browser)await browser.close();
    report.source_sha256_after=Object.fromEntries(files.map(p=>[relative(p),hash(p)]));
    if(JSON.stringify(before)!==JSON.stringify(report.source_sha256_after)){
      report.status='FAIL';report.source_change_detected=true;process.exitCode=1;
    }
    report.finished_at=new Date().toISOString();
    const output=path.join(QA,'production_browser_verification.json');
    fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify({status:report.status,checks:report.checks.length,page_errors:report.page_errors,
      report:relative(output),sha256:hash(output),error:report.error?.message},null,2));
  }
}
main().catch(error=>{console.error(error.stack||error);process.exitCode=1;});
