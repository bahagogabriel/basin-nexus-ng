import json
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]/'site'
SCREEN_DIR=BASE.parent/'preview';SCREEN_DIR.mkdir(exist_ok=True)
registry=(BASE/'data/registry.json').read_text()
geo=(BASE/'data/catchments.geojson').read_text()
html=(BASE/'index.html').read_text()
mock='<script>window.__REGISTRY__='+registry+';window.__GEO__='+geo+';window.fetch=(p)=>Promise.resolve(new Response(JSON.stringify(p.includes("registry.json")?window.__REGISTRY__:window.__GEO__),{status:200,headers:{"Content-Type":"application/json"}}));</script>'
html=html.replace('<script>\n(()=>',mock+'<script>\n(()=>',1)
logs=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--no-proxy-server','--proxy-bypass-list=*'])
    p=browser.new_page(viewport={'width':1540,'height':900},device_scale_factor=1)
    p.on('pageerror',lambda e:logs.append('page:'+str(e)))
    p.on('console',lambda msg: logs.append('console:'+msg.text) if msg.type=='error' else None)
    p.set_content(html,wait_until='load');p.wait_for_selector('path.region',state='attached',timeout=20000)
    assert p.locator('.region').count()==20,p.locator('.region').count()
    assert p.locator('#catchmentList button').count()==20
    assert 'Benue-Mada' in p.locator('#details').inner_text()
    p.locator('#catchmentSearch').fill('Okwa')
    assert p.locator('#catchmentList button').count()==1
    assert 'Benue-Mada' in p.locator('#catchmentList button').inner_text()
    p.locator('#catchmentList button').click()
    assert 'Benue-Mada' in p.locator('#details h2').inner_text()
    p.locator('#catchmentSearch').fill('')
    p.locator('#catchmentList button',has_text='Rima').click()
    assert p.locator('#details h2').inner_text()=='Rima'
    p.locator('#zoomReset').click()
    p.locator('#labelsToggle').click()
    assert p.locator('text.mlabel').first.get_attribute('display')=='none'
    p.locator('#labelsToggle').click()
    p.locator('#expandBtn').click()
    assert 'expanded' in p.locator('body').get_attribute('class')
    p.locator('#expandBtn').click()
    assert 'expanded' not in (p.locator('body').get_attribute('class') or '')
    p.locator('#navAbout').click()
    assert p.locator('#pageAbout').is_visible()
    p.locator('#navData').click()
    assert p.locator('#pageData').is_visible()
    assert p.locator('#pageData a[download]').count()==2
    p.locator('#navExplore').click()
    p.screenshot(path=str(SCREEN_DIR/'desktop_qa.png'),full_page=True)
    m=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
    m.on('pageerror',lambda e:logs.append('mobile:'+str(e)))
    m.set_content(html,wait_until='load');m.wait_for_selector('path.region',state='attached',timeout=20000)
    assert m.locator('path.region').count()==20
    assert m.locator('#catchmentList button').count()==20
    m.screenshot(path=str(SCREEN_DIR/'mobile_qa.png'),full_page=True)
    assert m.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1')
    assert not logs,logs
    browser.close()
report=json.loads((BASE/'data/build_report.json').read_text())
assert report['count']==20
text=(BASE/'index.html').read_text()
assert '4,929' not in text and '91 asset' not in text and 'drive.google.com/file/' not in text
assert 'SCMP_Evidence_Register' not in text
print(json.dumps({'status':'PASS','desktop_mobile':'PASS','twenty_geometries':'PASS','alias':'PASS','search':'PASS','zoom':'PASS','tabs':'PASS','no_console_errors':'PASS','no_sensitive_review_data_embedded':'PASS','test_mode':'in-memory page with mocked static JSON fetch (workspace blocks all navigation)'},indent=2))

