#!/usr/bin/env python3
"""Source metadata and public hydrology overview release guard."""
from pathlib import Path
import json
s=Path(__file__).resolve().parents[1]/'site'
r=json.loads((s/'data/rivers_overview.geojson').read_text())
l=json.loads((s/'data/lakes_overview.geojson').read_text())
m=json.loads((s/'data/hydro_reference_metadata.json').read_text())
assert m['status']=='OVERVIEW_REFERENCE_ONLY'
assert m['source_commit']=='ca96624a56bd078437bca8184e78163e5039ad19'
assert m['license']=='Natural Earth public domain'
assert 5<=len(r['features'])==m['datasets']['river']['output_count']<=100
assert len(l['features'])==2
assert all(f['geometry']['type'] in ('LineString','MultiLineString') for f in r['features'])
assert all(f['geometry']['type'] in ('Polygon','MultiPolygon') for f in l['features'])
assert all(f['properties']['precision']=='overview_only' for f in r['features']+l['features'])
scale='1:10m' if 'ne_10m_' in m['datasets']['river']['url'] else '1:50m'
assert all(f['properties']['source_scale']==scale for f in r['features']+l['features'])
html=(s/'index.html').read_text()
for term in ('id="riversToggle"','id="lakesToggle"','id="hydroInfo"',
             'function hitHydro(world)','function cacheHydro(rivers,lakes,meta)',
             'data/rivers_overview.geojson','data/lakes_overview.geojson',
             "not a verified local stream or dam inventory"):
 assert term in html,term
print('PUBLIC HYDRO OVERVIEW QA: PASS',len(r['features']),'rivers, 2 lakes, provenance and disclaimer')
