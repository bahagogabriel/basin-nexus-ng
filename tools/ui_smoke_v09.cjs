#!/usr/bin/env node
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const {setTimeout:delay}=require('node:timers/promises');
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path');
const folder=path.join(process.cwd(),'review/browser-v09');fs.mkdirSync(folder,{recursive:true});
const server=spawn('python3',['-m','http.server','8791','--bind','127.0.0.1','--directory','site'],{stdio:'ignore'});
let browser;const errors=[];const url='http://127.0.0.1:8791/';
async function ready(){
 const http=require('node:http');
 for(let i=0;i<60;i++){
  try{
   const status=await new Promise((resolve,reject)=>{
    const req=http.get(url,res=>{res.resume();resolve(res.statusCode)});
    req.once('error',reject);req.setTimeout(1500,()=>req.destroy(Error('HTTP server readiness timed out')));
   });
   if(status===200)return;
  }catch{}
  await delay(250);
 }
 throw Error('Server did not respond');
}
async function metric(page){return page.evaluate(()=>JSON.parse(JSON.stringify(window.__BN_MAP_DIAGNOSTICS__)))}

async function testWaterLayers(page,name){
 const manager=page.locator('#layerManager');
 if(!await manager.evaluate(n=>n.open))await page.locator('#layerManager > summary').click();
 const lakes=page.locator('#lakesToggle'),rivers=page.locator('#riversToggle');
 assert.equal(await rivers.getAttribute('aria-pressed'),'true');
 assert.equal(await lakes.getAttribute('aria-pressed'),'true');
 assert.match(await page.locator('#riverLegend').textContent(),/FAO 2026/);
 assert.match(await page.locator('#lakeLegend').textContent(),/1:10m/);
 await rivers.click();assert.equal(await rivers.getAttribute('aria-pressed'),'false');
 await rivers.click();assert.equal(await rivers.getAttribute('aria-pressed'),'true');
 await lakes.click();assert.equal(await lakes.getAttribute('aria-pressed'),'false');
 await lakes.click();assert.equal(await lakes.getAttribute('aria-pressed'),'true');
 await page.locator('#layerManager > summary').click();
 assert.equal(await manager.evaluate(n=>n.open),false,'Close layer menu to inspect the map');
 // Select a point inside the source polygon using the same geographic projection.
 const point=await page.evaluate(async()=>{
  const fc=await(await fetch('data/lakes_overview.geojson')).json(),f=fc.features.find(x=>x.properties.name==='Kainji Reservoir');
  if(!f)return null;
  const canvas=document.querySelector('#mapCanvas'),r=canvas.getBoundingClientRect(),view=window.__BN_MAP_DIAGNOSTICS__.view;
  const scale=Math.min(r.width/view.w,r.height/view.h),ox=(r.width-view.w*scale)/2,oy=(r.height-view.h*scale)/2;
  const xy=p=>[48+(p[0]-2.4)/13.2*922,25+(15.32-p[1])/11.37*698];
  const c=document.createElement('canvas').getContext('2d'),path=new Path2D();
  const poly=f.geometry.type==='MultiPolygon'?f.geometry.coordinates[0]:f.geometry.coordinates;
  for(const ring of poly){ring.forEach((p,i)=>{const q=xy(p);i?path.lineTo(...q):path.moveTo(...q)});path.closePath()}
  const outer=poly[0],v=outer.map(xy),xmin=Math.min(...v.map(x=>x[0])),xmax=Math.max(...v.map(x=>x[0])),
    ymin=Math.min(...v.map(x=>x[1])),ymax=Math.max(...v.map(x=>x[1]));
  for(let yi=1;yi<=20;yi++)for(let xi=1;xi<=20;xi++){
   const wx=xmin+(xmax-xmin)*xi/21,wy=ymin+(ymax-ymin)*yi/21;
   if(!c.isPointInPath(path,wx,wy,'evenodd'))continue;
   const x=ox+(wx-view.x)*scale,y=oy+(wy-view.y)*scale;
   if(x>30&&x<r.width-30&&y>60&&y<r.height-35)return {x:r.left+x,y:r.top+y}
  }
  return null;
 });
 assert(point,name+': no visible target within Kainji Reservoir');
 await page.mouse.click(point.x,point.y);
 await page.waitForFunction(()=>!document.querySelector('#hydroInfo')?.classList.contains('hidden'),null,{timeout:5000});
 assert.match(await page.locator('#hydroInfo').innerText(),/Kainji Reservoir/);
 assert.match(await page.locator('#hydroInfo').innerText(),/Natural Earth overview/);
 console.log(name+': PASS river/lake toggles, scale labelling, Kainji waterbody hit and popup');
}


async function responsiveUX(page,label){
 const v=page.viewportSize();if(!v)return;
 const inspect=await page.evaluate(()=>{
  const bounds=id=>{const r=document.querySelector(id).getBoundingClientRect();return {w:r.width,h:r.height,top:r.top,left:r.left}};
  return {scrollWidth:document.documentElement.scrollWidth,viewport:window.innerWidth,
   map:bounds('.mapPanel'),canvas:bounds('#mapCanvas'),
   layerOpen:document.querySelector('#layerManager').open,
   active:document.querySelector('#mapActiveSummary').textContent,
   legendOpen:document.querySelector('#countryLegend').open,
   grid:getComputedStyle(document.querySelector('.columns')).display}
 });
 assert(inspect.scrollWidth<=inspect.viewport+3,label+': unwanted horizontal overflow '+JSON.stringify(inspect));
 assert(inspect.canvas.w>Math.min(320,v.width*.72),label+': canvas too narrow');
 assert(inspect.canvas.top>=0&&inspect.canvas.top<Math.min(500,v.height*.60),label+': map starts too far below first viewport, top='+inspect.canvas.top+' viewport='+v.height);
 assert(inspect.canvas.top+Math.min(inspect.canvas.h,230)<v.height,label+': not enough map is visible without scrolling');
 if(v.width<=980){
  const order=await page.evaluate(()=>{const a=document.querySelector('.mapPanel').getBoundingClientRect(),b=document.querySelector('.directory').getBoundingClientRect();return [a.top,b.top]});
  assert(order[0]<order[1],label+': mobile/tablet map must precede catchment directory');
 }
 assert(inspect.active.includes('20 strategic catchments'),label+': regional context must be shown on arrival');
 assert(!inspect.layerOpen,label+': settings must start closed');
 if(v.width<=780)assert(!inspect.legendOpen,label+': legend should start collapsed on phones');
 await page.locator('#countryLegend > summary').click();
 const toggled=await page.locator('#countryLegend').evaluate(n=>n.open);
 assert.equal(toggled,!inspect.legendOpen,label+': legend disclosure is not interactive');
 await page.locator('#countryLegend > summary').click();
 assert.equal(await page.locator('#countryLegend').evaluate(n=>n.open),inspect.legendOpen,label+': legend should return to original state');
 console.log(label+': RESPONSIVE UX PASS '+v.width+'px, map width '+Math.round(inspect.canvas.w)+'px, no overflow');
}

async function test(page,name){
 page.on('pageerror',e=>errors.push(name+': '+e.message));
 await page.goto(url,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.frames>0&&document.querySelector('#details h2')?.textContent==='Explore all 20 catchments',{timeout:35000});
 await responsiveUX(page,name);
 // Stage 3D-S: source research overlay starts hidden, is opt-in, and never confirms a dam.
 assert.equal(await page.locator('#compiledDamQuickToggle').isEnabled(),true,name+': optional source research layer loaded');
 assert.equal(await page.locator('#compiledDamToggle').getAttribute('aria-pressed'),'false');
 assert.equal(await page.locator('#damRefLegend').evaluate(el=>el.classList.contains('hidden')),true);
 await page.locator('#compiledDamQuickToggle').click();
 assert.equal(await page.locator('#compiledDamToggle').getAttribute('aria-pressed'),'true');
 assert.match(await page.locator('#compiledDamStatus').textContent(),/186 published compiled references/);
 assert.equal(await page.locator('#damRefLegend').evaluate(el=>el.classList.contains('hidden')),false);
 // Select original-source Kainji reference, but require nonverification in the card.
 const pos=await page.evaluate(()=>{
   // Recompute the documented world-to-screen transform, as map internals are scoped.
   const view=window.__BN_MAP_DIAGNOSTICS__.view;
   const box=document.getElementById('mapCanvas').getBoundingClientRect();
   const wx=48+(4.6108-2.4)/(15.6-2.4)*922;
   const wy=25+(15.32-9.8631)/(15.32-3.95)*698;
   const scale=Math.min(box.width/view.w,box.height/view.h);
   const ox=(box.width-view.w*scale)/2,oy=(box.height-view.h*scale)/2;
   return {x:ox+(wx-view.x)*scale,y:oy+(wy-view.y)*scale};
 });
 const rect=await page.locator('#mapCanvas').boundingBox();
 await page.mouse.click(rect.x+pos.x,rect.y+pos.y);
 assert.match(await page.locator('#damRefInfo').innerText(),/Kainji/);
 assert.match(await page.locator('#damRefInfo').innerText(),/Not independently verified/);
 await page.locator('#closeDamRef').click();
 await page.locator('#compiledDamQuickToggle').click();
 assert.equal(await page.locator('#compiledDamToggle').getAttribute('aria-pressed'),'false');
 assert.equal(await page.locator('#damRefInfo').isVisible(),false);
 // Stage 3D-O: aggregate source review is accessible and contains no facility points.
 await page.locator('#navData').click();
 assert.equal(await page.locator('#waDamReferenceSummary').count(),1,name+': Data page research summary');
 assert.match(await page.locator('#waDamReferenceSummary').innerText(),/189 source point positions across 18 of 20 catchments/);
 await page.locator('#waDamReferenceCounts summary').click();
 assert.equal(await page.locator('#waDamReferenceCounts tbody tr').count(),20,name+': exactly 20 source-count rows');
 assert.equal(await page.locator('[data-reference-catchment-id="SCMP-C06"]').getAttribute('data-reference-count'),'33');
 assert.equal(await page.locator('[data-reference-catchment-id="SCMP-C03"]').getAttribute('data-reference-count'),'0');
 await page.locator('#navKnowledge').click();
 await page.waitForFunction(()=>document.querySelector('#knowledgeCards article.knowledgeCard')?.querySelector('h3'));
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),20,name+': expected 20 source-coverage records');
 assert.match(await page.locator('#knowledgeCount').innerText(),/20 of 20/);
 assert.match(await page.locator('#evidenceCount').innerText(),/0 matching approved records/);
 assert.match(await page.locator('#evidenceList').innerText(),/No individual stakeholder evidence records are cleared/);
 assert.equal(await page.locator('#evidenceList .evidenceEntry').count(),0);
 assert.equal(await page.locator('#knowledgeCards .knowledgeEvent').count(),20,name+': engagement provenance must exist per catchment');
 assert.match(await page.locator('#knowledgeCards .knowledgeEvent').first().innerText(),/2024|2025/);
 await page.locator('#knowledgeYear').selectOption('2024');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),6,name+': only six 2024 source records');
 await page.locator('#knowledgeYear').selectOption('2025');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),14,name+': only fourteen 2025 source records');
 await page.locator('#knowledgeYear').selectOption('all');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),20,name+': all-year source reset');
 for(const [city,expected] of [['Kano',6],['Sokoto',3],['Ilorin',4],['Lokoja',4],['Gombe',3]]){
  await page.locator('#knowledgeCity').selectOption(city);
  assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),expected,name+': incorrect '+city+' source count');
 }
 await page.locator('#knowledgeCity').selectOption('Sokoto');
 await page.locator('#knowledgeYear').selectOption('2024');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),0,name+': impossible year/city combination must be empty');
 assert.match(await page.locator('#knowledgeCards').innerText(),/No matching catchments/);
 assert.equal(await page.locator('#knowledgeExport').isDisabled(),true,name+': cannot export an empty selection');
 await page.locator('#knowledgeReset').click();
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),20,name+': reset must clear combined filters');
 assert.equal(await page.locator('#knowledgeCity').inputValue(),'all');
 assert.equal(await page.locator('#knowledgeYear').inputValue(),'all');


 await page.locator('#knowledgeState').selectOption('Plateau');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),7,name+': Plateau must have seven provisional geometry overlaps');
 assert.equal(await page.locator('#knowledgeCards .knowledgeGeo').count(),7,name+': state-specific caveats absent');
 assert.match(await page.locator('#knowledgeCards .knowledgeGeo').first().innerText(),/km²/);
 await page.locator('#knowledgeState').selectOption('Abuja Federal Capital Territory');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),2,name+': FCT must have two provisional geographic overlaps');
 await page.locator('#knowledgeState').selectOption('Niger');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),6,name+': Niger state overlap count is six');
 await page.locator('#knowledgeReset').click();
 assert.equal(await page.locator('#knowledgeState').inputValue(),'all',name+': reset must clear geographic filter');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),20);
 await page.locator('#knowledgeState').selectOption('Plateau');
 assert.equal(await page.locator('#knowledgeLGA option').count(),18,name+': Plateau should have 17 LGAs plus All');
 await page.locator('#knowledgeLGA').selectOption({label:'Jos South · Plateau'});
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),4,name+': Jos South intersects four catchments in provisional crosswalk');
 assert.equal(await page.locator('#knowledgeCards .knowledgeGeo').count(),8,name+': both state and LGA overlap descriptions must appear');
 await page.locator('#knowledgeCards .knowledgeDetail summary').first().click();
 assert.match(await page.locator('#knowledgeCards .knowledgeDetail').first().innerText(),/FAO AQUASTAT 2026/);
 assert.equal(await page.locator('#knowledgeExport').isEnabled(),true);
 const downloadWait=page.waitForEvent('download');
 await page.locator('#knowledgeExport').click();
 const downloaded=await downloadWait;
 assert.equal(downloaded.suggestedFilename(),'basin-nexus-filtered-public-reference.csv');
 const csv=fs.readFileSync(await downloaded.path(),'utf8');
 assert.equal(csv.split(/\r?\n/).filter(Boolean).length,5,name+': CSV must contain header plus four matching catchments');
 assert.match(csv,/source metadata only/);
 assert.doesNotMatch(csv,/raw_statement_internal|private_drive_id|release_authorization/);
 await page.locator('#knowledgeState').selectOption('Niger');
 assert.equal(await page.locator('#knowledgeLGA').inputValue(),'all',name+': changing state must clear incompatible LGA');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),6);
 await page.locator('#knowledgeReset').click();
 assert.equal(await page.locator('#knowledgeLGA option').count(),496,name+': expected 495 distinct LGA options plus All');
 await page.locator('#knowledgeSort').selectOption('area');
 assert.match(await page.locator('#knowledgeCards h3').first().innerText(),/Hadejia Jama'are/);
 await page.locator('#knowledgeSort').selectOption('rivers');
 assert.match(await page.locator('#knowledgeCards h3').first().innerText(),/Hawul-Kilange/);
 await page.locator('#knowledgeSort').selectOption('name');
 assert.match(await page.locator('#knowledgeCards h3').first().innerText(),/Aloma-Konshisha/);
 await page.locator('#knowledgeReset').click();
 assert.equal(await page.locator('#knowledgeSort').inputValue(),'name');
 // Stage 3D-C: thematic water hierarchy totals and release gating.
 assert.equal(await page.locator('#knowledgeLenses button[aria-pressed="true"]').count(),1,name+': exactly one active thematic view');
 assert.equal(await page.locator('#knowledgeLenses button[aria-pressed="true"]').getAttribute('data-knowledge-lens'),'water');
 assert.match(await page.locator('#knowledgeThemePanel').innerText(),/33,169/);
 assert.match(await page.locator('#knowledgeThemePanel').innerText(),/11,433/);
 assert.match(await page.locator('#knowledgeThemePanel').innerText(),/7,410/);
 assert.equal(await page.locator('#knowledgeCards .knowledgeCardLens').count(),20);
 await page.locator('#knowledgeCrossborder').selectOption('yes');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),9,name+': nine cross-border catchments (>0.5% threshold)');
 const borderRiverTotals=await page.evaluate(()=>{
  const ids=Object.entries(window.__BN_MAP_DIAGNOSTICS__?.detailedManifest?.files||{});return ids.length;
 });
 // A filtered CSV must preserve class breakdown without confidential records.
 const crossExport=page.waitForEvent('download');
 await page.locator('#knowledgeExport').click();
 const borderCsv=fs.readFileSync(await (await crossExport).path(),'utf8');
 assert.equal(borderCsv.split(/\r?\n/).filter(Boolean).length,10);
 assert.match(borderCsv,/modeled_reaches_upstream_1000plus_km2/);
 assert.doesNotMatch(borderCsv,/raw_statement_internal|source_internal_id|release_authorization/);
 await page.locator('#knowledgeCrossborder').selectOption('no');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),11,name+': 11 catchments are within Nigeria by provisional threshold');
 await page.locator('#knowledgeCrossborder').selectOption('all');
 await page.locator('#knowledgeLenses button[data-knowledge-lens="geography"]').click();
 assert.equal(await page.locator('#knowledgeLenses button[aria-pressed="true"]').getAttribute('data-knowledge-lens'),'geography');
 assert.match(await page.locator('#knowledgeThemePanel').innerText(),/102/);
 assert.match(await page.locator('#knowledgeThemePanel').innerText(),/9/);
 assert.match(await page.locator('#knowledgeCards .knowledgeCardLens').first().innerText(),/Largest provisional state/);
 await page.locator('#knowledgeLenses button[data-knowledge-lens="engagement"]').click();
 assert.match(await page.locator('#knowledgeThemePanel').innerText(),/2024/);
 assert.match(await page.locator('#knowledgeThemePanel').innerText(),/2025/);
 await page.locator('#knowledgeLenses button[data-knowledge-lens="assets"]').click();
 assert.match(await page.locator('#knowledgeThemePanel').innerText(),/189/);
 assert.match(await page.locator('#knowledgeThemePanel').innerText(),/71 have usable dam names/);
 assert.match(await page.locator('#knowledgeCards .knowledgeCardLens').first().innerText(),/Compiled 2026 dam-source references/);
 await page.locator('#knowledgeSort').selectOption('dam_refs');
 assert.match(await page.locator('#knowledgeCards h3').first().innerText(),/Hadejia Jama'are/);
 await page.locator('#knowledgeSort').selectOption('dam_named');
 assert.match(await page.locator('#knowledgeCards h3').first().innerText(),/Hadejia Jama'are/);
 await page.locator('#knowledgeSort').selectOption('name');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),20);
 await page.locator('#knowledgeReset').click();
 assert.equal(await page.locator('#knowledgeCrossborder').inputValue(),'all');
 assert.equal(await page.locator('#knowledgeLenses button[aria-pressed="true"]').getAttribute('data-knowledge-lens'),'water');
 await page.locator('#knowledgeTheme').selectOption('policies');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),20,name+': policies are indexed across all 20 catchments');
 await page.locator('#knowledgeSearch').fill('Okwa');
 assert.equal(await page.locator('#knowledgeCards article.knowledgeCard').count(),1,name+': historical catchment alias must work');
 assert.match(await page.locator('#knowledgeCards h3').innerText(),/Benue-Mada/);
 await page.locator('button[data-knowledge-map="SCMP-C02"]').click();
 await page.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.selected==='SCMP-C02');
 assert.match(await page.locator('#details .knowledgeProfile').innerText(),/Lokoja/,name+': profile must expose institutional workshop provenance');
 assert.match(await page.locator('#details .knowledgeProfile').innerText(),/15–23 August 2025/,name+': profile must expose source date range');
 assert.equal(await page.locator('#navExplore').getAttribute('aria-current'),'page');
 await page.locator('#overviewBtn').click();
 await page.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.selected===null);
 console.log(name+': PASS 20 source-coverage entries, themes, aliases, and map navigation');
 assert.equal(await page.locator('#mapHint').evaluate(n=>n.open),false,name+': map guide must start collapsed');
 await page.locator('#mapHint > summary').click();
 assert.equal(await page.locator('#mapHint').evaluate(n=>n.open),true);
 await page.locator('#mapHint > summary').click();
 assert.equal(await page.locator('#mapHint').evaluate(n=>n.open),false);
 assert.equal((await metric(page)).selected,null,name+': launch must not preselect a catchment');
 assert.equal((await metric(page)).riverScope,'all');
 assert.equal((await metric(page)).detailCount,0);
 assert.equal(await page.locator('button[data-id].active').count(),0,name+': catchment should not be highlighted at launch');
 assert.equal(await page.locator('#overviewBtn').isDisabled(),true);
 assert.equal(await page.locator('#focusMapBtn').isDisabled(),true);
 assert.equal(await page.locator('#riverScopeToggle').isDisabled(),true);
 assert.equal(await page.locator('#riverDensity').isDisabled(),true);
 assert.equal(await page.locator('#lgaToggle').isDisabled(),true);
 await page.screenshot({path:path.join(folder,name+'_regional_launch.png'),fullPage:true});
 await page.locator('#catchmentList button[data-id="SCMP-C02"]').click();
 await page.waitForFunction(()=>document.querySelector('#details h2')?.textContent==='Benue-Mada');
 assert.equal((await metric(page)).selected,'SCMP-C02');
 assert.equal((await metric(page)).riverScope,'selected');
 assert.equal(await page.locator('#riverScopeToggle').isEnabled(),true);
 assert.equal(await page.locator('#riverDensity').isEnabled(),true);
 await page.locator('#overviewBtn').click();
 await page.waitForFunction(()=>document.querySelector('#details h2')?.textContent==='Explore all 20 catchments');
 assert.equal((await metric(page)).selected,null);
 assert.equal((await metric(page)).riverScope,'all');
 assert.equal((await metric(page)).view.w,1020);
 assert.equal((await metric(page)).detailFor,null);
 await page.locator('#catchmentList button[data-id="SCMP-C02"]').click();
 await page.waitForFunction(()=>document.querySelector('#details h2')?.textContent==='Benue-Mada');
 assert.equal(await page.locator('#mapCanvas').count(),1);
 assert.equal((await metric(page)).selected,'SCMP-C02');
 await page.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.detailStatus==='ready'&&window.__BN_MAP_DIAGNOSTICS__.detailCount===1769,{timeout:45000});
 assert.equal((await metric(page)).detailFor,'SCMP-C02',name+': expected Benue-Mada detailed rivers');
 const riverSelector=page.locator('#riverDensity');
 await riverSelector.selectOption('main');assert.equal(await riverSelector.inputValue(),'main');
 await riverSelector.selectOption('medium');assert.equal(await riverSelector.inputValue(),'medium');
 await riverSelector.selectOption('all');
 // Validate the exact catchment shown in the user's screenshots.
 await page.locator('#catchmentList button[data-id="SCMP-C15"]').click();
 await page.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.detailStatus==='ready'&&window.__BN_MAP_DIAGNOSTICS__.detailFor==='SCMP-C15'&&window.__BN_MAP_DIAGNOSTICS__.detailCount===2038,{timeout:45000});
 assert.match(await page.locator('#details').innerText(),/2,038/);
 const activeRow=page.locator('#catchmentList button.active');
 assert.equal(await activeRow.getAttribute('data-id'),'SCMP-C15');
 const visibleRow=await page.evaluate(()=>{
  const row=document.querySelector('#catchmentList button.active').getBoundingClientRect(),box=document.querySelector('#catchmentList').getBoundingClientRect();
  return row.top>=box.top-1&&row.bottom<=box.bottom+1;
 });
 assert(visibleRow,name+': active catchment should remain visible in the directory');
 assert.equal(await page.locator('.profileJumps button').count(),4);
 await page.locator('button[data-profile-target="profileAdmin"]').click();
 await page.waitForFunction(()=>{
  const panel=document.querySelector('#details'),target=document.querySelector('#profileAdmin');
  const r=target.getBoundingClientRect();
  return panel.scrollTop>45||(r.top>=0&&r.top<innerHeight*.65);
 },{timeout:5500});
 assert.equal(await page.locator('#profileAdmin').count(),1);
 await page.locator('button[data-profile-target="profileRivers"]').click();
 await page.screenshot({path:path.join(folder,name+'_sarkin_rivers.png'),fullPage:true});
 console.log(name+': PASS regional launch + overview return + 2,038 Sarkin Pawa–Kaduna FAO reaches, all river density choices');
 await page.locator('#catchmentList button[data-id="SCMP-C02"]').click();
 await page.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.detailStatus==='ready'&&window.__BN_MAP_DIAGNOSTICS__.detailFor==='SCMP-C02',{timeout:45000});
 await page.locator('#zoomReset').click();
 assert.equal((await metric(page)).riverScope,'selected');
 await page.locator('#riverScopeToggle').click();assert.equal((await metric(page)).riverScope,'all');
 await page.locator('#riverScopeToggle').click();assert.equal((await metric(page)).riverScope,'selected');
 await testWaterLayers(page,name);
 const manager=page.locator('#layerManager');
 assert.equal(await manager.evaluate(n=>n.open),false,'Layers menu should be collapsed on load');
 await page.locator('#layerManager > summary').click();
 assert.equal(await manager.evaluate(n=>n.open),true,'Layers menu should open');
 await page.locator('#stateToggle').click();assert.equal(await page.locator('#stateToggle').getAttribute('aria-pressed'),'false');
 await page.locator('#stateToggle').click();assert.equal(await page.locator('#stateToggle').getAttribute('aria-pressed'),'true');
 await page.locator('#lgaToggle').click();
 await page.waitForFunction(()=>document.querySelector('#lgaToggle')?.getAttribute('aria-pressed')==='true',{timeout:45000});
 assert.match(await page.locator('#mapNote').textContent(),/outlined in gold/i);
 await page.locator('#focusMapBtn').click();
 const focusView=(await metric(page)).view;
 assert(focusView.w<1020,name+': Focus catchment failed to zoom');
 await page.locator('#catchmentList button[data-id="SCMP-C03"]').click();
 await page.waitForFunction(()=>document.querySelector('#details h2')?.textContent==='Gaji-Lamurde');
 assert.equal((await metric(page)).selected,'SCMP-C03');
 const canvas=page.locator('#mapCanvas');await canvas.scrollIntoViewIfNeeded();
 const r=await canvas.boundingBox();assert(r&&r.width>200&&r.height>180);
 const before=await metric(page);
 await page.mouse.move(r.x+r.width*.5,r.y+r.height*.55);await page.mouse.down();
 for(let i=1;i<=9;i++)await page.mouse.move(r.x+r.width*.5+i*8,r.y+r.height*.55+i*3,{steps:1});
 await page.mouse.up();
 const after=await metric(page);
 assert(after.panMoves>before.panMoves,name+': pointer drag did not pan');
 assert(Math.abs(after.view.x-before.view.x)>.1,name+': view stayed unchanged');
 await page.locator('#catchmentList button[data-id="SCMP-C02"]').click();
 const lga=await page.evaluate(async()=>{
  const admin=await(await fetch('data/admin_crosswalk_provisional.json')).json();
  const geo=await(await fetch('data/adm2_lgas_study_provisional.geojson')).json();
  const catchments=await(await fetch('data/catchments.geojson')).json();
  const view=window.__BN_MAP_DIAGNOSTICS__.view,rect=document.querySelector('#mapCanvas').getBoundingClientRect();
  const scale=Math.min(rect.width/view.w,rect.height/view.h),ox=(rect.width-view.w*scale)/2,oy=(rect.height-view.h*scale)/2;
  const xy=p=>[48+(p[0]-2.4)/13.2*922,25+(15.32-p[1])/11.37*698];
  const make=g=>{const p=new Path2D();for(const poly of g.type==='MultiPolygon'?g.coordinates:[g.coordinates])for(const ring of poly){ring.forEach((v,i)=>{const a=xy(v);i?p.lineTo(...a):p.moveTo(...a)});p.closePath()}return p};
  const target=catchments.features.find(f=>f.properties.id==='SCMP-C02');
  const cp=make(target.geometry),t=document.createElement('canvas').getContext('2d');
  const allowed=new Map(admin.byCatchment['SCMP-C02'].lgas.map(x=>[x.id,x]));
  for(const f of geo.features){if(!allowed.has(f.properties.id))continue;
   const lp=make(f.geometry),parts=f.geometry.type==='MultiPolygon'?f.geometry.coordinates:[f.geometry.coordinates];
   const ring=parts[0][0];let x0=Infinity,x1=-Infinity,y0=Infinity,y1=-Infinity;
   for(const v of ring){const a=xy(v);x0=Math.min(x0,a[0]);x1=Math.max(x1,a[0]);y0=Math.min(y0,a[1]);y1=Math.max(y1,a[1])}
   for(let yi=1;yi<=8;yi++)for(let xi=1;xi<=8;xi++){
    const wx=x0+(x1-x0)*xi/9,wy=y0+(y1-y0)*yi/9;
    if(!t.isPointInPath(lp,wx,wy,'evenodd')||!t.isPointInPath(cp,wx,wy,'evenodd'))continue;
    const x=ox+(wx-view.x)*scale,y=oy+(wy-view.y)*scale;
    if(x>30&&x<rect.width-30&&y>45&&y<rect.height-30)return {name:allowed.get(f.properties.id).name,x:rect.left+x,y:rect.top+y}
   }
  }
  return null;
 });
 assert(lga,name+': no testable visible LGA');
 await page.mouse.click(lga.x,lga.y);
 await page.waitForFunction(()=>!document.querySelector('#lgaInfo')?.classList.contains('hidden'),{timeout:5000});
 assert.equal((await metric(page)).selectedLGA,lga.name);
 await page.screenshot({path:path.join(folder,name+'.png'),fullPage:true});
 console.log(name+': PASS Canvas pan, LGA selection/popup and layer switches');
}

async function assertIdleStability(page,name,seconds=3){
 const snapshot=()=>page.evaluate(()=>{
   const cv=document.querySelector('#mapCanvas'),panel=document.querySelector('#mapbody');
   const cr=cv.getBoundingClientRect(),pr=panel.getBoundingClientRect(),m=window.__BN_MAP_DIAGNOSTICS__;
   return {view:{...m.view},frames:m.frames,canvas:[cr.left,cr.top,cr.width,cr.height,cv.width,cv.height],
    parent:[pr.left,pr.top,pr.width,pr.height],cssPosition:getComputedStyle(cv).position}
 });
 const before=await snapshot();await delay(seconds*1000);const after=await snapshot();
 assert.equal(before.cssPosition,'absolute',name+': canvas still participates in layout');
 for(const v of ['x','y','w','h'])assert(Math.abs(after.view[v]-before.view[v])<1e-8,name+': map view moved while idle ('+v+')');
 for(const label of ['canvas','parent'])for(let i=0;i<6&&(i<(label==='parent'?4:6));i++){
  assert(Math.abs(after[label][i]-before[label][i])<1.1,name+': '+label+' layout shifted while idle, column '+i);
 }
 assert(after.frames-before.frames<=2,name+': continuous canvas repaint while idle ('+(after.frames-before.frames)+' frames)');
 console.log(name+': IDLE STABILITY PASS '+seconds+' seconds, viewport fixed, layout stable, '+(after.frames-before.frames)+' draws');
}

async function pinch(page){
 const cv=page.locator('#mapCanvas');await cv.scrollIntoViewIfNeeded();const r=await cv.boundingBox();
 const session=await page.context().newCDPSession(page),x=r.x+r.width*.5,y=r.y+r.height*.5;
 const before=(await metric(page)).view.w,pinch0=(await metric(page)).pinchMoves;
 await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:x-32,y,id:1},{x:x+32,y,id:2}]});
 for(let i=1;i<=8;i++)await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x-32-i*9,y,id:1},{x:x+32+i*9,y,id:2}]});
 await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await delay(120);
 const result=await metric(page);
 assert(result.pinchMoves>pinch0,'touch pinch events not handled');
 assert(result.view.w<before*.9,'pinch-out did not zoom in');
 console.log('tablet real two-finger pinch: PASS '+before.toFixed(1)+' to '+result.view.w.toFixed(1));
}

async function testReachComparison(browser){
 const ctx=await browser.newContext({viewport:{width:1320,height:940}});
 const page=await ctx.newPage();
 await page.goto(url,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.frames>0&&document.querySelector('#reachCompareStatus')?.textContent.includes('20 of 20'),{timeout:35000});
 await page.locator('#navData').click();
 assert.equal(await page.locator('#reachCompareRows tr[data-reach-catchment]').count(),20);
 assert.match(await page.locator('#reachComparison').innerText(),/not drainage length per area/i);
 await page.locator('#reachCompareSort').selectOption('total');
 assert.equal(await page.locator('#reachCompareRows tr').first().getAttribute('data-reach-catchment'),'SCMP-C07');
 await page.locator('#reachCompareSearch').fill('Sokoto');
 assert.equal(await page.locator('#reachCompareRows tr[data-reach-catchment]').count(),1);
 assert.equal(await page.locator('#reachCompareRows tr').first().getAttribute('data-reach-catchment'),'SCMP-C17');
 await page.locator('#reachCompareRows button[data-reach-focus="SCMP-C17"]').click();
 await page.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.selected==='SCMP-C17',{timeout:5000});
 assert.equal(await page.locator('#navExplore').getAttribute('aria-current'),'page');
 assert.match(await page.locator('#details').innerText(),/not measured drainage density/);
 await page.locator('#reachProfileCompare').click();
 assert.equal(await page.locator('#navData').getAttribute('aria-current'),'page');
 await ctx.close();
 const invalid=await browser.newContext();
 await invalid.route('**/data/river_reach_comparison.json',async route=>{
  const resp=await route.fetch();const data=await resp.json();
  data.rows[0].reach_count+=1;
  await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(data)});
 });
 const bad=await invalid.newPage();await bad.goto(url,{waitUntil:'domcontentloaded'});
 await bad.waitForFunction(()=>document.querySelector('#reachCompareStatus')?.textContent.includes('unverified'),{timeout:35000});
 await bad.locator('#navData').click();
 assert.equal(await bad.locator('#reachCompareRows tr[data-reach-catchment]').count(),0);
 await invalid.close();
 console.log('FAO REACH COMPARISON: 20 catchments, normalized source count, sort/search, map link, profile and invalid-source lockout PASS');
}

async function testEvidenceCatalogueFixture(browser){
 // Browser route fixtures never alter files in site/ or the actual released evidence collection.
 const make=(record_id,extra={})=>({
  record_id,catchment_ids:['SCMP-C02'],theme:'water_infrastructure',
  record_type:'facility_report',statement:'Synthetic fictional field report <img src=x onerror=alert(1)>; not a real facility.',
  evidence_status:'stakeholder_reported',source_reference:'Synthetic public test provenance',
  source_locator:'Invented section, paragraph 1',release_authorization:'PUBLIC-SYNTHETIC-11111',
  location:null,...extra
 });
 const fixtures=[
  make('BN-SYNTH-101'),
  make('BN-SYNTH-102',{theme:'interventions',evidence_status:'independently_verified',
   statement:'Invented intervention, used only by the browser acceptance suite.',
   location:{latitude:9.2,longitude:8.5,verification:'independently_validated',
             method:'Invented GNSS field inspection',uncertainty_m:35}})
 ];
 const approved={schema_version:'BN_PUBLIC_EVIDENCE_V1',type:'PublicEvidenceCollection',
                 publication_status:'APPROVED_PUBLIC_ONLY',records:fixtures};
 const c=await browser.newContext({viewport:{width:1200,height:840}});
 await c.route('**/data/public_evidence_catalogue.json',r=>r.fulfill({
  status:200,contentType:'application/json',body:JSON.stringify(approved)}));
 const page=await c.newPage();
 await page.goto(url,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.querySelector('#evidenceCount')?.textContent.includes('2 publicly released overall'),{timeout:35000});
 await page.locator('#navKnowledge').click();
 assert.equal(await page.locator('#evidenceList article.evidenceEntry').count(),2);
 assert.equal(await page.locator('#evidenceList img').count(),0,'Untrusted source text must be HTML escaped');
 assert.match(await page.locator('#evidenceList').innerText(),/<img src=x onerror=alert\(1\)>/);
 await page.locator('#evidenceTheme').selectOption('interventions');
 assert.equal(await page.locator('#evidenceList article.evidenceEntry').count(),1);
 await page.locator('#evidenceStatus').selectOption('stakeholder_reported');
 assert.equal(await page.locator('#evidenceList article.evidenceEntry').count(),0);
 await page.locator('#evidenceStatus').selectOption('independently_verified');
 assert.equal(await page.locator('#evidenceList article.evidenceEntry').count(),1);
 await page.locator('#evidenceList details summary').click();
 assert.match(await page.locator('#evidenceList').innerText(),/uncertainty 35 m/);
 assert.match(await page.locator('#evidenceList').innerText(),/Map navigation below selects the catchment/);
 await page.locator('#evidenceList button[data-evidence-map]').click();
 await page.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.selected==='SCMP-C02');
 assert.equal(await page.locator('#navExplore').getAttribute('aria-current'),'page');
 await c.close();
 const invalid=await browser.newContext();
 await invalid.route('**/data/public_evidence_catalogue.json',r=>r.fulfill({
  status:200,contentType:'application/json',
  body:JSON.stringify({...approved,publication_status:'DRAFT'})}));
 const badPage=await invalid.newPage();
 await badPage.goto(url,{waitUntil:'domcontentloaded'});
 await badPage.waitForFunction(()=>document.querySelector('#evidenceCount')?.textContent.includes('unavailable'),{timeout:35000});
 await badPage.locator('#navKnowledge').click();
 assert.equal(await badPage.locator('#evidenceList article.evidenceEntry').count(),0);
 assert.match(await badPage.locator('#evidenceList').innerText(),/failed its schema check/);
 assert.equal(await badPage.locator('#knowledgeCards article.knowledgeCard').count(),20,'Invalid evidence cannot break geographic atlas');
 await invalid.close();
 console.log('APPROVED-ONLY EVIDENCE CATALOGUE: PASS synthetic records, status and theme filters, XSS escaping, map navigation, fail-closed invalid feed');
}

(async()=>{try{
 await ready();browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const desktop=await browser.newPage({viewport:{width:1512,height:950}});
 await test(desktop,'desktop');await assertIdleStability(desktop,'desktop after drag');await desktop.close();
 await testReachComparison(browser);
await testEvidenceCatalogueFixture(browser);
 const phoneContext=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const phone=await phoneContext.newPage();phone.on('pageerror',e=>errors.push('phone: '+e.message));
 await phone.goto(url,{waitUntil:'domcontentloaded'});
 await phone.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.frames>0&&document.querySelector('#details h2')?.textContent==='Explore all 20 catchments',{timeout:35000});
 await responsiveUX(phone,'phone390');await phone.screenshot({path:path.join(folder,'phone_ux_a.png'),fullPage:true});
 await phoneContext.close();
 const tabletContext=await browser.newContext({viewport:{width:810,height:1080},deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const tablet=await tabletContext.newPage();await test(tablet,'tablet');await pinch(tablet);await assertIdleStability(tablet,'tablet after pinch',4);
 await tablet.screenshot({path:path.join(folder,'tablet_pinch.png'),fullPage:true});
 await tabletContext.close();
 assert.deepEqual(errors,[],errors.join('\n'));console.log('BROWSER QA v1.7: SOURCE INDEX, REGIONAL FIRST, CATCHMENT SWITCHING, LGA, PINCH AND STABILITY ALL PASS')
 }catch(e){console.error(e.stack||e);process.exitCode=1}finally{await browser?.close();server.kill('SIGTERM')}})();
