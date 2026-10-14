/* Optional end-to-end check: requires Playwright and an installed Chromium browser. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url'),{chromium}=require('playwright');
(async()=>{
  const browser=await chromium.launch({headless:true,...(process.env.PPR_BROWSER_EXECUTABLE?{executablePath:process.env.PPR_BROWSER_EXECUTABLE}:{})});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    const filename=path.resolve(process.argv[2]||path.join(__dirname,'../../../interactive_map/trends.html'));
    const url=pathToFileURL(filename).href;
    await page.goto(url+'?units=LME_032&method=EwE_TE_EE&metric=ratio&npp_scope=global&npp_fill=earliest',{timeout:60000});
    await page.locator('#groupDisplay').selectOption('groups');
    await page.waitForFunction(()=>document.querySelectorAll('[data-group-layer]').length>1);
    const labels=()=>page.locator('#seriesLegend b').allTextContents();
    const initial=await labels();assert.equal(initial.length,6);assert.equal(initial.at(-1),'Other');
    assert.equal(await page.locator('[data-group-layer] path').count(),6);
    assert.ok(new URL(page.url()).searchParams.get('group_display')==='groups');
    const fixture=await page.evaluate(()=>{
      const state={units:['LME_032'],methods:['EwE_TE_EE'],scope:'all',mode:'ratio',npp_scope:'global',npp_fill:'earliest',catch_basis:'landings',unidentified:'method'};
      const result=PPRTimeSeries.compare(SERIES_DB,state),breakdown=PPRGroupContributions.build(SERIES_DB,state,result);
      return {top:breakdown.layers.filter(l=>!l.other).map(l=>l.group_id),model_id:SERIES_DB.units.LME_032.default_model,
        unattributed:breakdown.has_unattributed,errors:result.points.filter((p,i)=>p.value!==null&&Math.abs(p.value-breakdown.layers.reduce((s,l)=>s+l.points[i].value,0))>1e-8).length};
    });
    assert.equal(fixture.errors,0);assert.equal(fixture.unattributed,false);
    await page.locator('#openGroupFilter').click();
    // Find actual model IDs in row metadata so display labels need not match IDs.
    const choices=await page.locator('#groupTableBody tr').evaluateAll(rows=>rows.filter(r=>r.querySelector('input[type=checkbox]')?.checked).map(r=>r.dataset.groupId));
    const other=choices.find(id=>!fixture.top.includes(id));assert.ok(other);
    const choose=async id=>{
      const row=page.locator('#groupTableBody tr[data-group-id]').filter({has:page.locator('input[type=checkbox]')});
      const index=await row.evaluateAll((rows,id)=>rows.findIndex(r=>r.dataset.groupId===id),id);
      assert.ok(index>=0);await row.nth(index).locator('input[type=checkbox]').uncheck();
    };
    await choose(other);assert.deepEqual(await labels(),initial,'Excluding Other preserves the top-five legend');
    await choose(fixture.top[0]);
    const reranked=await labels();assert.equal(reranked.length,6);assert.ok(!reranked.includes(initial[0]));
    assert.ok(reranked.some(label=>label!=='Other'&&!initial.includes(label)),'A former Other group is promoted');
    await page.locator('#groupDialog').evaluate(dialog=>dialog.close());
    const downloadEvent=page.waitForEvent('download');await page.locator('#downloadCSV').click();
    const download=await downloadEvent,csv=fs.readFileSync(await download.path(),'utf8');
    assert.match(csv,/Other contribution/);
    await page.locator('#groupDisplay').selectOption('total');assert.equal(await page.locator('[data-group-layer]').count(),0);
    await page.locator('#groupDisplay').selectOption('groups');assert.equal(await page.locator('[data-group-layer]').count(),6);
    await page.reload({timeout:60000});assert.deepEqual(await labels(),reranked,'URL and stored group choices preserve the stacked view');
    await page.goto(url+'?set=pilot&method=EwE_TE_EE&metric=ratio&npp_scope=global&npp_fill=earliest&region_review=validated&group_display=groups',{timeout:60000});
    await page.waitForFunction(()=>document.querySelectorAll('[data-group-layer]').length>1);
    if(process.env.PPR_STACK_SCREENSHOT)await page.locator('.chart-card').screenshot({path:process.env.PPR_STACK_SCREENSHOT});
    await page.setViewportSize({width:390,height:844});
    await page.waitForFunction(()=>document.querySelector('#chart').getAttribute('viewBox').split(' ')[2]<400);
    assert.equal(await page.locator('#seriesLegend b').count(),6);
    if(process.env.PPR_STACK_MOBILE_SCREENSHOT)await page.locator('.chart-card').screenshot({path:process.env.PPR_STACK_MOBILE_SCREENSHOT});
    assert.deepEqual(errors,[]);
    console.log('Browser: area layers, excluded-group promotion, stable top five, CSV download, URL reload and mobile layout pass.');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
