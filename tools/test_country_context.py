#!/usr/bin/env python3
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
site=root/'site'
geo=json.loads((site/'data/catchments.geojson').read_text())
country=json.loads((site/'data/nigeria_boundary.geojson').read_text())
context=json.loads((site/'data/international_context.json').read_text())
html=(site/'index.html').read_text()
assert len(geo['features'])==20
assert len(country['features'])==1
assert country['features'][0]['properties']['source']=='Natural Earth'
assert country['features'][0]['properties']['classification']=='context_only'
assert context['total_catchments']==20
assert context['extension_count_indicative']==sum(x['outside_pct_unrounded']>0.5 for x in context['coverage'])
assert set(x['id'] for x in context['coverage'])==set(f['properties']['id'] for f in geo['features'])
assert 'nationalToggle' in html and 'nigeriaOutline' in html
assert 'path.nigeriaOutline{fill:none;' in html and 'pointer-events:none' in html
assert 'national=country' in html
assert 'e.target.setPointerCapture(e.pointerId)' in html
assert 'svg.setPointerCapture(e.pointerId)' not in html
assert 'Northern Nigeria' in html
print('COUNTRY CONTEXT GATE: PASS — 20 catchments and non-interactive 1:110m national overlay')
