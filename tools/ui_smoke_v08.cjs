#!/usr/bin/env node
// Headless Chromium smoke QA for geographic layer behaviour.
// Requires "npm install --no-save playwright" and "npx playwright install chromium".
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const {setTimeout:wait}=require('node:timers/promises');
const {chromium}=require('playwright');
const fs=require('node:fs');
const path=require('node:path');
const qaDir=path.join(process.cwd(),'review','browser-v08');fs.mkdirSync(qaDir,{recursive:true});
const server=spawn('python3',['-m','http.server','8791','--bind','127.0.0.1','--directory','site'],{stdio:['ignore','pipe','pipe']});
let browser; const errs=[];
async function ready(){
 for(let i=0;i<45;i++){try{const r=await fetch('http://127.0.0.1:8791/');if(r.ok)return}catch(_){}await wait(350)}
 throw Error('Local web server did not start');
}
async function check(page,mode){
 page.on('pageerror',e=>errs.push(mode+': '+e.message));
 await page.goto('http://127.0.0.1:8791/',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.querySelectorAll('#mapSvg path.region').length===20 && document.querySelectorAll('#mapSvg path.adminState').length===37,{timeout:30000});
 assert.equal(await page.locator('path.adminState').count(),37,mode+': missing state outlines');
 assert.equal(await page.locator('path.nigeriaOutline').count(),1,mode+': missing country outline');
 await page.locator('#stateToggle').click();
 assert.equal(await page.locator('path.adminState').count(),0,mode+': state hide failed');
 await page.locator('#stateToggle').click();
 assert.equal(await page.locator('path.adminState').count(),37,mode+': state show failed');
 // All LGA geometry is lazy loaded, then the visible lines are clipped to the chosen catchment.
 await page.locator('#lgaToggle').click();
 await page.waitForFunction(()=>document.querySelectorAll('path.adminLGA').length===35,{timeout:45000});
 assert.equal(await page.locator('clipPath#lgaClipStudy').count(),1,mode+': selected-catchment clipping missing');
 assert.equal(await page.locator('path.adminLGA').count(),35,mode+': unexpected Benue-Mada LGA count');
 await page.locator('#catchmentList button[data-id="SCMP-C03"]').click();
 await page.waitForFunction(()=>document.querySelector('#details h2')?.textContent==='Gaji-Lamurde',{timeout:20000});
 assert.equal(await page.locator('path.adminLGA').count(),26,mode+': selection did not refresh LGA layer');
 await page.locator('#lgaToggle').click();
 assert.equal(await page.locator('path.adminLGA').count(),0,mode+': LGA hide failed');
 await page.locator('#lgaToggle').click();
 await page.waitForFunction(()=>document.querySelectorAll('path.adminLGA').length===26,{timeout:20000});
 await page.screenshot({path:path.join(qaDir,mode+'.png'),fullPage:true});
 console.log(mode+': PASS state toggles 37, clipped selected LGAs 35→26, lazy load, hide/show, catchment selection');
}
(async()=>{
 try{
  await ready();
  browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  const desktop=await browser.newPage({viewport:{width:1500,height:950}});
  await check(desktop,'desktop');
  await desktop.close();
  const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  await check(mobile,'mobile');
  await mobile.close();
  assert.deepEqual(errs,[],errs.join('\n'));
  console.log('BROWSER QA: PASS, no JS page errors');
 } catch(e) { console.error(e.stack||e);process.exitCode=1 }
 finally {await browser?.close();server.kill('SIGTERM')}
})();
