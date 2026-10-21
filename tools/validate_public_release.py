#!/usr/bin/env python3
"""Stdlib-only publication gate for Basin Nexus NG GitHub Pages site."""
from pathlib import Path
import json, re
root=Path(__file__).resolve().parents[1]
site=root/'site'
allowed={'index.html','data/catchments.geojson','data/registry.json','data/catchments.csv','data/build_report.json','data/nigeria_boundary.geojson','data/international_context.json','data/admin_crosswalk_provisional.json','data/catchment_states_provisional.csv','data/catchment_lgas_provisional.csv','data/adm1_states_provisional.geojson','data/adm2_lgas_study_provisional.geojson','data/admin_map_layer_QA.json','.nojekyll'}
actual={p.relative_to(site).as_posix() for p in site.rglob('*') if p.is_file()}
assert actual==allowed, f'Unexpected public files: missing={allowed-actual},extra={actual-allowed}'
registry=json.loads((site/'data/registry.json').read_text('utf-8'))
geometry=json.loads((site/'data/catchments.geojson').read_text('utf-8'))
report=json.loads((site/'data/build_report.json').read_text('utf-8'))
assert len(registry)==len(geometry['features'])==report['count']==20
ids=[r['id'] for r in registry];geo_ids=[g['properties']['id'] for g in geometry['features']]
assert len(set(ids))==20 and set(ids)==set(geo_ids)
assert all(r['name'] and r['area_km2']>0 for r in registry)
assert sum(r['historical_alias']=='Okwa-Mada' for r in registry)==1
assert next(r for r in registry if r['historical_alias']=='Okwa-Mada')['name']=='Benue-Mada'
assert all(f['geometry']['type'] in ('Polygon','MultiPolygon') for f in geometry['features'])
assert geometry['type']=='FeatureCollection'
country=json.loads((site/'data/nigeria_boundary.geojson').read_text('utf-8'))
context=json.loads((site/'data/international_context.json').read_text('utf-8'))
assert len(country['features'])==1 and country['features'][0]['properties']['name']=='Nigeria'
assert country['features'][0]['properties']['classification']=='context_only'
assert context['total_catchments']==20 and len(context['coverage'])==20
assert set(x['id'] for x in context['coverage'])==set(ids)
assert all(0<=x['outside_pct_unrounded']<=100 for x in context['coverage'])
assert context['extension_count_indicative']==sum(x['classification']=='extends_beyond_nigeria' for x in context['coverage'])
admin=json.loads((site/'data/admin_crosswalk_provisional.json').read_text('utf-8'))
assert admin['status']=='PROVISIONAL_GEOMETRIC_OVERLAY'
assert admin['totalCatchments']==20 and admin['totalStateIntersections']==102 and admin['totalLGAIntersections']==754
assert set(admin['byCatchment'])==set(ids)
assert sum(len(v['states']) for v in admin['byCatchment'].values())==102
assert sum(len(v['lgas']) for v in admin['byCatchment'].values())==754
adm1=json.loads((site/'data/adm1_states_provisional.geojson').read_text('utf-8'))
adm2=json.loads((site/'data/adm2_lgas_study_provisional.geojson').read_text('utf-8'))
adminqa=json.loads((site/'data/admin_map_layer_QA.json').read_text('utf-8'))
assert len(adm1['features'])==37
assert len(adm2['features'])==495
assert adminqa['status']=='PROVISIONAL_MAP_GEOMETRY'
assert adminqa['adm1']['sha256']==admin['sourceHashADM1'] and adminqa['adm2']['sha256']==admin['sourceHashADM2']
assert adminqa['max_state_area_delta_pct']<1 and adminqa['max_lga_area_delta_pct']<3
assert set(f['properties']['id'] for f in adm2['features'])=={l['id'] for v in admin['byCatchment'].values() for l in v['lgas']}
assert report['max_simplification_area_delta_pct']<0.1
html=(site/'index.html').read_text('utf-8')
assert '<title>Basin Nexus NG' in html
assert 'PUBLIC BOUNDARY PREVIEW' in html
for path in ['data/catchments.geojson','data/registry.json','data/catchments.csv','data/nigeria_boundary.geojson','data/international_context.json','data/admin_crosswalk_provisional.json','data/catchment_states_provisional.csv','data/catchment_lgas_provisional.csv','data/adm1_states_provisional.geojson','data/adm2_lgas_study_provisional.geojson']:
    assert path in html
for forbidden in ('drive.google.com/file/', 'SCMP_Evidence_Register_REVIEW',
                  'SCMP_Asset_Observations_REVIEW','personal contact details:',
                  '4,929 evidence entries','Signed Stakeholder Engagement'):
    assert forbidden.lower() not in html.lower(), f'Sensitive or review-only reference: {forbidden}'
assert all(p.stat().st_size < 2_000_000 for p in site.rglob('*') if p.is_file())
print('PUBLIC RELEASE GATE: PASS — 20 geographic features, approved file allowlist, alias, geometry metadata and review-data exclusions')
