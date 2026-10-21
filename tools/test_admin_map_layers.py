#!/usr/bin/env python3
"""QA gate for admin-boundary Canvas layer switching, geometry references and file safety."""
from pathlib import Path
import json
p=Path(__file__).resolve().parents[1]/'site'
html=(p/'index.html').read_text('utf-8')
adm=json.loads((p/'data/admin_crosswalk_provisional.json').read_text('utf-8'))
states=json.loads((p/'data/adm1_states_provisional.geojson').read_text('utf-8'))
lgas=json.loads((p/'data/adm2_lgas_study_provisional.geojson').read_text('utf-8'))
qa=json.loads((p/'data/admin_map_layer_QA.json').read_text('utf-8'))
assert len(states['features'])==qa['adm1_features']==37
assert len(lgas['features'])==qa['study_intersecting_adm2_features']==495
assert len({f['properties']['id'] for f in lgas['features']})==495
for c in adm['byCatchment'].values():
 assert all(x['id'] in {f['properties']['id'] for f in lgas['features']} for x in c['lgas'])
for check in ("function draw(", "ctx.clip(cp.path,'evenodd')","function choose(id,zoom){selected=id;mapMetrics.selected=id;",
              "id=\"stateToggle\"","id=\"lgaToggle\"","data/adm1_states_provisional.geojson",
              "data/adm2_lgas_study_provisional.geojson","pointer-events:none"):
 assert check in html,check
assert "canvas.setPointerCapture(e.pointerId)" in html
assert "svg.setPointerCapture(e.pointerId)" not in html
assert len(list(p.rglob('*.csv')))<=3
print("ADMIN MAP UI + PROVENANCE GATE: PASS")
