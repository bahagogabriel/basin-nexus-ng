#!/usr/bin/env python3
"""Stdlib-only publication gate for Basin Nexus NG GitHub Pages site."""
from pathlib import Path
import json, re
root=Path(__file__).resolve().parents[1]
site=root/'site'
allowed={'index.html','climate.js','data/nasa_power_20_catchment_point_climate_2005_2025.json','data/integrated_catchment_indicator_register.json','data/integrated_catchment_indicator_register.csv','data/catchments.geojson','data/registry.json','data/catchments.csv','data/build_report.json','data/nigeria_boundary.geojson','data/international_context.json','data/admin_crosswalk_provisional.json','data/catchment_states_provisional.csv','data/catchment_lgas_provisional.csv','data/adm1_states_provisional.geojson','data/adm2_lgas_study_provisional.geojson','data/admin_map_layer_QA.json','data/rivers_overview.geojson','data/lakes_overview.geojson','data/hydro_reference_metadata.json','data/detailed_river_manifest.json','data/fao_downstream_summary.json','data/fao_downstream_index.json','data/fao_endpoint_gap_summary.json','data/fao_endpoint_gap_index.json','data/fao_three_original_gap_resolution.json','data/fao_89_catchment_source_boundary_audit.json','data/fao_89_catchment_source_boundary_audit.csv','data/fao_study_area_overlap_outlet_readiness.json','data/fao_model_boundary_exit_screen_records.csv','data/river_reach_comparison.json','data/river_reach_comparison.csv','data/stakeholder_coverage_index.json','data/source_content_publication_model.json','data/stakeholder_source_detail.json','data/stakeholder_resource_atlas.json','data/stakeholder_lga_occurrences.json','data/public_lga_occurrences.json','data/public_evidence_catalogue.json','data/external_reference_sources.json','data/wa_dams_2026_catchment_reference_counts.json','data/wa_dams_2026_source_quality.json','data/confirmed_dam_sites.json','data/wa_dam_compiled_reference_preview.json',*{f'data/river_network/SCMP-C{i:02d}.geojson' for i in range(1,21)},'.nojekyll'}
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
import test_wa_dam_reference_counts
import test_wa_dam_source_quality
import test_compiled_dam_preview
from validate_confirmed_dam_sites import validate_collection
validate_collection(json.loads((site/'data/confirmed_dam_sites.json').read_text('utf-8')))
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
from build_stage3d_au_av_fao_topology import build as rebuild_fao_topology
source_topology,source_index,source_index_bytes=rebuild_fao_topology()
assert json.loads((site/'data/fao_downstream_summary.json').read_text('utf-8'))==source_topology
assert (site/'data/fao_downstream_index.json').read_bytes()==source_index_bytes
assert source_topology['source_cycle_members']==0 and source_topology['unique_source_reach_ids']==51906
from build_stage3d_ay_az_fao_endpoint_qa import build as rebuild_model_endpoints
model_gap_summary,model_gap_index,model_gap_bytes=rebuild_model_endpoints()
assert json.loads((site/'data/fao_endpoint_gap_summary.json').read_text('utf-8'))==model_gap_summary
assert (site/'data/fao_endpoint_gap_index.json').read_bytes()==model_gap_bytes
assert model_gap_summary['total_clipped_source_link_classification']['endpoint_gt_500m']==3
assert model_gap_summary['source_manifest_sha256']==source_topology['source_manifest_sha256']
from build_stage3d_bd_bf_uncut_source_resolution import generate as rebuild_uncut_three
uncut_three=rebuild_uncut_three(root/'research/source_qa/FAO_2026_SIX_ORIGINAL_MODELED_REACHES_NOT_SURVEYED.geojson')
assert json.loads((site/'data/fao_three_original_gap_resolution.json').read_text('utf-8'))==uncut_three
assert uncut_three['all_three_original_model_endpoint_gaps_zero'] is True
assert uncut_three['independent_hydraulic_continuity_verified'] is False
from build_stage3d_bg_bh_89_boundary_qa import build as rebuild_crosscatchment_model, to_csv as model_crosscatchment_csv
crosscatchment_model=rebuild_crosscatchment_model()
assert json.loads((site/'data/fao_89_catchment_source_boundary_audit.json').read_text('utf-8'))==crosscatchment_model
assert (site/'data/fao_89_catchment_source_boundary_audit.csv').read_text('utf-8')==model_crosscatchment_csv(crosscatchment_model)

from build_stage3d_bo_bq_nasa_power_climate import registry as power_registry, make_climate as rebuild_power_climate, integrated as build_unified_register, csv_text as unified_register_csv, SNAP as POWER_SNAP
power_climate=rebuild_power_climate(power_registry(),POWER_SNAP)
unified_register=build_unified_register(power_climate,power_registry())
assert json.loads((site/'data/nasa_power_20_catchment_point_climate_2005_2025.json').read_text('utf-8'))==power_climate
assert json.loads((site/'data/integrated_catchment_indicator_register.json').read_text('utf-8'))==unified_register
assert (site/'data/integrated_catchment_indicator_register.csv').read_text('utf-8')==unified_register_csv(unified_register)
assert power_climate['catchment_point_count']==20
assert all(len(r['annual'])==21 and len(r['monthly_climatology'])==12 for r in power_climate['records'])
assert all(r['climate_spatial_basis']=='NASA_POWER_MAP_LABEL_POINT_NOT_CATCHMENT_MEAN' for r in unified_register['rows'])
assert 'not a catchment' in (site/'climate.js').read_text('utf-8').lower() or 'not catchment' in (site/'climate.js').read_text('utf-8').lower()

assert crosscatchment_model['source_reach_copies_crossing_selected_catchment_index']==89
assert crosscatchment_model['unique_cross_catchment_source_association_pairs']==33
assert crosscatchment_model['reference_memberships_across_target_catchments']==92
assert crosscatchment_model['polygon_relationship_reference_counts']=={'boundaries_touch_or_intersect':1,'overlapping_study_polygons':91}
from build_stage3d_bk_bl_overlap_outlet_screen import build as screen_outlet_readiness, to_csv as source_model_exit_csv
outlet_readiness=screen_outlet_readiness()
assert json.loads((site/'data/fao_study_area_overlap_outlet_readiness.json').read_text('utf-8'))==outlet_readiness
assert (site/'data/fao_model_boundary_exit_screen_records.csv').read_text('utf-8')==source_model_exit_csv(outlet_readiness)
assert outlet_readiness['source_screen_record_count']==125
assert outlet_readiness['actual_verified_outlet_count']==0
assert outlet_readiness['screen_overlap']['study_pair_count']==190
assert outlet_readiness['screen_overlap']['screen_overlap_pair_count']==42


from build_stage3d_aq_river_reach_comparison import verify as verify_reach_comparison
verify_reach_comparison(details,registry,json.loads((site/'data/river_reach_comparison.json').read_text('utf-8')),(site/'data/river_reach_comparison.csv').read_text('utf-8'))
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
assert all(len(x['source_section_keys']) in (4,5) and x['public_release']=='Metadata only' for x in coverage['catchments'])
assert sum('past_present_interventions' in x['source_section_keys'] for x in coverage['catchments'])==14
source_model=json.loads((site/'data/source_content_publication_model.json').read_text('utf-8'))
assert source_model['publication_status']=='PUBLIC_METADATA_ONLY' and source_model['individual_public_claims_approved']==0
assert len(source_model['catchments'])==20 and all(x['public_approved_claims']==0 and x['review_release_status']=='HOLD' for x in source_model['catchments'])
assert sum(x['linked_shared_vision_source_in_restricted_set'] for x in source_model['catchments'])==19
assert report['max_simplification_area_delta_pct']<0.1
html=(site/'index.html').read_text('utf-8')
assert 'id="mapCanvas"' in html
assert 'svg.addEventListener(' not in html
assert '<title>Basin Nexus NG' in html
assert 'PUBLIC GEOGRAPHY PREVIEW' in html
for path in ['data/catchments.geojson','data/registry.json','data/catchments.csv','data/nigeria_boundary.geojson','data/international_context.json','data/admin_crosswalk_provisional.json','data/catchment_states_provisional.csv','data/catchment_lgas_provisional.csv','data/adm1_states_provisional.geojson','data/adm2_lgas_study_provisional.geojson','data/rivers_overview.geojson','data/lakes_overview.geojson','data/hydro_reference_metadata.json','data/detailed_river_manifest.json','data/stakeholder_coverage_index.json','data/source_content_publication_model.json','data/public_evidence_catalogue.json']:
    assert path in html
for forbidden in ('drive.google.com/file/', 'SCMP_Evidence_Register_REVIEW',
                  'SCMP_Asset_Observations_REVIEW','personal contact details:',
                  '4,929 evidence entries','Signed Stakeholder Engagement'):
    assert forbidden.lower() not in html.lower(), f'Sensitive or review-only reference: {forbidden}'
assert all(p.stat().st_size < (4_000_000 if 'river_network/' in p.relative_to(site).as_posix() else 2_000_000) for p in site.rglob('*') if p.is_file())
print('PUBLIC RELEASE GATE: PASS — 20 geographic features, approved file allowlist, alias, geometry metadata and review-data exclusions')
