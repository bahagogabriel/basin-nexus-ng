#!/usr/bin/env python3
"""Basin Nexus NG public administrative metadata regression gate."""
import csv,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'site'
a=json.loads((p/'data/admin_crosswalk_provisional.json').read_text('utf-8'))
geo=json.loads((p/'data/catchments.geojson').read_text('utf-8'))
assert len(geo['features'])==20
assert a['status']=='PROVISIONAL_GEOMETRIC_OVERLAY'
assert a['totalCatchments']==20
assert a['totalStateIntersections']==102
assert a['totalLGAIntersections']==754
assert len(a['sourceHashADM1'])==len(a['sourceHashADM2'])==64
assert len(a['sourceCatchmentHash'])==64
assert set(a['byCatchment'])==set(f['properties']['id'] for f in geo['features'])
for x in a['byCatchment'].values():
 assert x['states'] and x['lgas']
 assert all(0<s['pctTotal']<=100 for s in x['states'])
 assert all(0<l['pctTotal']<=100 for l in x['lgas'])
 assert abs(sum(s['pctTotal'] for s in x['states'])+x['outsidePct']-100)<0.2
 assert all(l['stateId'] in {s['id'] for s in x['states']} for l in x['lgas'])
with (p/'data/catchment_states_provisional.csv').open(newline='',encoding='utf-8') as f: assert len(list(csv.DictReader(f)))==102
with (p/'data/catchment_lgas_provisional.csv').open(newline='',encoding='utf-8') as f: assert len(list(csv.DictReader(f)))==754
html=(p/'index.html').read_text('utf-8')
for item in ('adminPanel(c)','adminSearch(c)','PROVISIONAL · GEOMETRIC OVERLAY','data/admin_crosswalk_provisional.json'):
 assert item in html
print('PUBLIC ADMIN CATALOGUE GATE: PASS (20 catchments, 102 state/FCT, 754 LGA intersections)')
