#!/usr/bin/env python3
"""Stdlib-only publication gate for Basin Nexus NG GitHub Pages site."""
from pathlib import Path
import json, re
root=Path(__file__).resolve().parents[1]
site=root/'site'
allowed={'index.html','data/catchments.geojson','data/registry.json','data/catchments.csv','data/build_report.json','data/nigeria_boundary.geojson','data/international_context.json','data/admin_crosswalk_provisional.json','data/catchment_states_provisional.csv','data/catchment_lgas_provisional.csv','data/adm1_states_provisional.geojson','data/adm2_lgas_study_provisional.geojson','data/admin_map_layer_QA.json','data/rivers_overview.geojson','data/lakes_overview.geojson','data/hydro_reference_metadata.json','data/detailed_river_manifest.json','data/stakeholder_coverage_index.json','data/public_evidence_catalogue.json','data/external_reference_sources.json',*{f'data/river_network/SCMP-C{i:02d}.geojson' for i in range(1,21)},'.nojekyll'}
actual={p.relative_to(site).as_posix() for p in site.rglob('*') if p.is_file()}
assert actual==allowed, f'Unexpected public files: missing={allowed-actual},extra={actual-allowed}'
registry=json.loads((site/'data/registry.json').read_text('utf-8'))
geometry=json.loads((site/'data/catchments.geojson').read_text('utf-8'))
report=json.loads((site/'data/build_report.json').read_text('utf-8'))
assert len(registry)==len(geometry['features'])==report['count']==20
# External reference links are public provenance metadata, never source or facility records.
import sys
sys.path.insert(0,str(root/'tools'))
import test_external_reference_sources
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
watermeta=json.loads((site/'data/hydro_reference_metadata.json').read_text('utf-8'))
rivers=json.loads((site/'data/rivers_overview.geojson').read_text('utf-8'))
lakes=json.loads((site/'data/lakes_overview.geojson').read_text('utf-8'))
assert watermeta['status']=='OVERVIEW_REFERENCE_ONLY'
assert watermeta['source_commit']=='ca96624a56bd078437bca8184e78163e5039ad19'
assert 5<=len(rivers['features'])==watermeta['datasets']['river']['output_count']<=100
assert len(lakes['features'])==watermeta['datasets']['lake']['output_count']==2
scale='1:10m' if 'ne_10m_' in watermeta['datasets']['river']['url'] else '1:50m'
assert scale in ('1:10m','1:50m')
assert all(f['properties']['source_scale']==scale for f in rivers['features']+lakes['features'])
assert all(f['properties']['precision']=='overview_only' and f['properties']['not_a_dam_inventory'] for f in rivers['features']+lakes['features'])
import hashlib
details=json.loads((site/'data/detailed_river_manifest.json').read_text('utf-8'))
assert details['status']=='PROVISIONAL_DETAILED_RIVER_NETWORK' and details['license']=='CC BY 4.0 (FAO AQUASTAT)'
assert len(details['files'])==20 and set(details['files'])==set(ids)
assert details['source_intersecting_unique_reaches']==51906
assert details['total_display_reaches']==52012
assert details['source_catchment_sha256']==hashlib.sha256((site/'data/catchments.geojson').read_bytes()).hexdigest()
for cid,f in details['files'].items():
    data=(site/'data'/f['file']).read_bytes()
    assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256'], cid
    fc=json.loads(data)
    assert fc['type']=='FeatureCollection' and fc['properties']['catchment_id']==cid
    assert len(fc['features'])==f['count']>=1000
    assert sum(f['classes'].values())==f['count']
    assert all(z['properties']['source_license']=='CC BY 4.0' and z['properties']['upstream_class'] in ('large_upstream_1000plus','medium_upstream_100plus','small_upstream_below100') for z in fc['features'])
coverage=json.loads((site/'data/stakeholder_coverage_index.json').read_text())
assert coverage['publication_status']=='PUBLIC_METADATA_ONLY'
assert coverage['source_documents_reviewed']==20
assert coverage['source_contents_published'] is False and coverage['coordinates_or_observations_published'] is False
assert coverage['engagement_provenance_status']=='SOURCE_EVENT_METADATA_ONLY'
assert coverage['source_records_publicly_cleared']==0
from evidence_publication_gate import validate as validate_evidence, SCHEMA_VERSION
public_catalogue=json.loads((site/'data/public_evidence_catalogue.json').read_text('utf-8'))
assert public_catalogue['schema_version']==SCHEMA_VERSION
assert set(public_catalogue)=={'type','schema_version','publication_status','records'}
assert public_catalogue['records']==[] # Intentional manual release decision required for nonempty records
assert validate_evidence(public_catalogue,set(ids))=={'validated_public_records':0,'mapped_locations':0}
assert all(x['source_type']=='SCMP institutional stakeholder engagement communiqué' and x['engagement_date_start']<=x['engagement_date_end'] and x['engagement_city'] in ('Kano','Sokoto','Ilorin','Lokoja','Gombe') for x in coverage['catchments'])
assert len(coverage['catchments'])==20 and set(x['id'] for x in coverage['catchments'])==set(ids)
assert all(len(x['source_section_keys'])==4 and x['public_release']=='Metadata only' for x in coverage['catchments'])
assert report['max_simplification_area_delta_pct']<0.1
html=(site/'index.html').read_text('utf-8')
assert 'id="mapCanvas"' in html
assert 'svg.addEventListener(' not in html
assert '<title>Basin Nexus NG' in html
assert 'PUBLIC GEOGRAPHY PREVIEW' in html
for path in ['data/catchments.geojson','data/registry.json','data/catchments.csv','data/nigeria_boundary.geojson','data/international_context.json','data/admin_crosswalk_provisional.json','data/catchment_states_provisional.csv','data/catchment_lgas_provisional.csv','data/adm1_states_provisional.geojson','data/adm2_lgas_study_provisional.geojson','data/rivers_overview.geojson','data/lakes_overview.geojson','data/hydro_reference_metadata.json','data/detailed_river_manifest.json','data/stakeholder_coverage_index.json','data/public_evidence_catalogue.json']:
    assert path in html
for forbidden in ('drive.google.com/file/', 'SCMP_Evidence_Register_REVIEW',
                  'SCMP_Asset_Observations_REVIEW','personal contact details:',
                  '4,929 evidence entries','Signed Stakeholder Engagement'):
    assert forbidden.lower() not in html.lower(), f'Sensitive or review-only reference: {forbidden}'
assert all(p.stat().st_size < (4_000_000 if 'river_network/' in p.relative_to(site).as_posix() else 2_000_000) for p in site.rglob('*') if p.is_file())
print('PUBLIC RELEASE GATE: PASS — 20 geographic features, approved file allowlist, alias, geometry metadata and review-data exclusions')
