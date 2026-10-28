#!/usr/bin/env python3
"""Stage 3D-C thematic public-data invariants. Does not load any private source."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
site=root/'site'
network=json.loads((site/'data/detailed_river_manifest.json').read_text(encoding='utf-8'))
admin=json.loads((site/'data/admin_crosswalk_provisional.json').read_text(encoding='utf-8'))
sources=json.loads((site/'data/stakeholder_coverage_index.json').read_text(encoding='utf-8'))
registry=json.loads((site/'data/registry.json').read_text(encoding='utf-8'))
html=(site/'index.html').read_text(encoding='utf-8')
keys=['small_upstream_below100','medium_upstream_100plus','large_upstream_1000plus']
assert network['status']=='PROVISIONAL_DETAILED_RIVER_NETWORK'
assert 'upstream drainage area' in network['hierarchy_method']
ids={x['id'] for x in registry}
assert len(ids)==20==len(network['files'])==len(admin['byCatchment'])
assert ids==set(network['files'])==set(admin['byCatchment'])
assert sources['source_records_publicly_cleared']==0
assert sources['coordinates_or_observations_published'] is False
assert sources['source_contents_published'] is False
assert sources['publication_status']=='PUBLIC_METADATA_ONLY'
totals=[0,0,0]
outside=[]
for id in sorted(ids):
    river=network['files'][id]
    assert set(river['classes'])==set(keys)
    classes=[river['classes'][key] for key in keys]
    assert all(isinstance(x,int) and x>=0 for x in classes)
    assert sum(classes)==river['count']
    totals=[a+b for a,b in zip(totals,classes)]
    area=admin['byCatchment'][id]
    assert 0<=area['outsidePct']<=100
    if area['outsidePct']>0.5:
        outside.append(id)
assert totals==[33169,11433,7410], totals
assert sum(totals)==network['total_display_reaches']==52012
assert len(outside)==9, outside

for needle in (
    'thematic evidence explorer v1.11',
    'id="knowledgeLenses"',
    'id="knowledgeCrossborder"',
    'data-knowledge-lens="water"',
    'data-knowledge-lens="geography"',
    'data-knowledge-lens="engagement"',
    'data-knowledge-lens="assets"',
    "riverClassKeys=['small_upstream_below100','medium_upstream_100plus','large_upstream_1000plus']",
    'function riverClassesFor(id)',
    'function renderKnowledgeLens(rows)',
    'function renderKnowledgeCardLens(c,row,admin,river)',
    "renderKnowledgeLens(result);",
    "renderKnowledgeCardLens(c,row,admin,river)",
    "cross==='all'||(Number(admin?.outsidePct||0)>0.5)===(cross==='yes')",
    'No individually cleared facility or intervention records published',
    'Source documents have been reviewed privately, but no individual infrastructure facilities',
    'Reaches may appear in more than one catchment clip',
    'modeled_reaches_upstream_below100_km2',
    'modeled_reaches_upstream_100_to_below1000_km2',
    'modeled_reaches_upstream_1000plus_km2',
    'No individually cleared facility or intervention records',
):
    assert needle in html, needle
assert html.count('data-knowledge-lens="')==4
# A thematic view is a way to present public data, not a new private record feed.
for forbidden in ('raw_statement_internal','source_internal_id','principal_candidate_id',
                  'release_authorization','confidential_source_url','private_drive_id'):
    assert forbidden not in html, forbidden
csv=html[html.index('function downloadKnowledgeCSV(){'):html.index('function tab(name)')]
assert '...riverClassesFor(item.id)' in csv
assert 'filteredKnowledge()' in csv
assert 'fetch(' not in csv
print('STAGE 3D-C MODELLED RIVER HIERARCHY, TRANSBOUNDARY GEO AND SOURCE SAFETY: PASS')
