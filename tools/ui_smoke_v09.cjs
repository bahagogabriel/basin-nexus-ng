#!/usr/bin/env node
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const {setTimeout:delay}=require('node:timers/promises');
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path');
const folder=path.join(process.cwd(),'review/browser-v09');fs.mkdirSync(folder,{recursive:true});
const server=spawn('python3',['-m','http.server','8791','--bind','127.0.0.1','--directory','site'],{stdio:'ignore'});
let browser;const errors=[];const url='http://127.0.0.1:8791/';
async function ready(){for(let i=0;i<60;i++){try{const r=await fetch(url);if(r.ok)return}catch{}await delay(250)}throw Error('Server did not respond')}
async function metric(page){return page.evaluate(()=>JSON.parse(JSON.stringify(window.__BN_MAP_DIAGNOSTICS__)))}
async function test(page,name){
 page.on('pageerror',e=>errors.push(name+': '+e.message));
 await page.goto(url,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__BN_MAP_DIAGNOSTICS__?.frames>0&&document.querySelector('#details h2')?.textContent==='Benue-Mada',{timeout:35000});
 assert.equal(await page.locator('#mapCanvas').count(),1);
 assert.equal((await metric(page)).selected,'SCMP-C02');
 await page.locator('#stateToggle').click();assert.equal(await page.locator('#stateToggle').getAttribute('aria-pressed'),'false');
 await page.locator('#stateToggle').click();assert.equal(await page.locator('#stateToggle').getAttribute('aria-pressed'),'true');
 await page.locator('#lgaToggle').click();
 await page.waitForFunction(()=>document.querySelector('#lgaToggle')?.getAttribute('aria-pressed')==='true',{timeout:45000});
 assert.match(await page.locator('#mapNote').innerText(),/outlined in gold/i);
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
(async()=>{try{
 await ready();browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const desktop=await browser.newPage({viewport:{width:1512,height:950}});
 await test(desktop,'desktop');await desktop.close();
 const tabletContext=await browser.newContext({viewport:{width:810,height:1080},deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const tablet=await tabletContext.newPage();await test(tablet,'tablet');await pinch(tablet);
 await tablet.screenshot({path:path.join(folder,'tablet_pinch.png'),fullPage:true});
 await tabletContext.close();
 assert.deepEqual(errors,[],errors.join('\n'));console.log('BROWSER QA v0.9: ALL PASS')
 }catch(e){console.error(e.stack||e);process.exitCode=1}finally{await browser?.close();server.kill('SIGTERM')}})();
