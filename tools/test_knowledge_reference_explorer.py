#!/usr/bin/env python3
"""Stage 3D-B source-safe geographic/river explorer contract; no private record access."""
from pathlib import Path
import json
import re

site = Path(__file__).resolve().parents[1] / 'site'
data = site / 'data'
registry = json.loads((data/'registry.json').read_text(encoding='utf-8'))
admin = json.loads((data/'admin_crosswalk_provisional.json').read_text(encoding='utf-8'))
water = json.loads((data/'detailed_river_manifest.json').read_text(encoding='utf-8'))
sources = json.loads((data/'stakeholder_coverage_index.json').read_text(encoding='utf-8'))
html = (site/'index.html').read_text(encoding='utf-8')
keys = {row['id'] for row in registry}
assert len(registry)==len(keys)==20
assert keys == set(admin['byCatchment']) == set(water['files'])
assert keys == {row['id'] for row in sources['catchments']}
assert admin['status']=='PROVISIONAL_GEOMETRIC_OVERLAY'
assert admin['boundaryYear']==2022
assert 'GRID3' in admin['sourceAttribution']
assert water['status']=='PROVISIONAL_DETAILED_RIVER_NETWORK'
assert 'data.fao.org' in water['source']
assert sources['publication_status']=='PUBLIC_METADATA_ONLY'
assert sources['source_records_publicly_cleared']==0
assert sources['source_contents_published'] is False
assert sources['coordinates_or_observations_published'] is False
assert sum(item['count'] for item in water['files'].values())==water['total_display_reaches']==52012

state_links=sum(len(v['states']) for v in admin['byCatchment'].values())
lga_links=sum(len(v['lgas']) for v in admin['byCatchment'].values())
ids={}
for key,entry in admin['byCatchment'].items():
 assert entry['area']>0
 assert len(entry['states'])>=1 and len(entry['lgas'])>=1
 assert water['files'][key]['count']>0
 assert sum(water['files'][key]['classes'].values())==water['files'][key]['count']
 for state in entry['states']:
  assert state['km2']>0 and isinstance(state['name'],str)
 for lga in entry['lgas']:
  assert lga['km2']>0
  if lga['id'] in ids:
   assert ids[lga['id']] == (lga['name'],lga['state'])
  else:
   ids[lga['id']] = (lga['name'],lga['state'])
assert (state_links,lga_links,len(ids))==(102,754,495)

assert "thematic evidence explorer v1.11" in html
assert "function riverClassesFor(id)" in html
assert "function renderKnowledgeLens(rows)" in html
assert "function renderKnowledgeCardLens(c,row,admin,river)" in html
assert "id=\"knowledgeCrossborder\"" in html
assert "id=\"knowledgeLenses\"" in html
required = ('id="knowledgeLGA"','id="knowledgeSort"','id="knowledgeExport"',
            'function updateKnowledgeLGAOptions()','function filteredKnowledge()',
            'function downloadKnowledgeCSV()', 'FAO modeled river reaches',
            'source metadata only','provisional geographic references',
            'LGA geographic overlap (provisional)','no stakeholder asset points',
            'individual claims', 'detailedManifest?.files?.[c.id]')
for text in required:
 assert text in html,text
# Prevent accidentally introducing private sources to public site.
for token in ('raw_statement_internal','source_internal_id','principal_candidate_id',
              'release_authorization','signed_source_internal','private_drive_id',
              'drive.google.com/file/'):
 assert token not in html,token

# Review is a separate source file; public exports are constructed only from metadata.
start=html.index('function downloadKnowledgeCSV(){')
end=html.index('function tab(name)',start)
csv_fn=html[start:end]
assert 'filteredKnowledge()' in csv_fn and 'source metadata only' in csv_fn
assert 'catchment_area_km2' in csv_fn and 'modeled_river_reaches_fao_2026' in csv_fn
assert "'provisional geographic references'" in csv_fn
assert 'fetch(' not in csv_fn
assert re.search(r'\.disabled=result\.length===0',html)
assert 'modeled_reaches_upstream_below100_km2' in csv_fn
assert 'modeled_reaches_upstream_100_to_below1000_km2' in csv_fn
assert 'modeled_reaches_upstream_1000plus_km2' in csv_fn
assert '...riverClassesFor(item.id)' in csv_fn
assert "cross==='all'||(Number(admin?.outsidePct||0)>0.5)===(cross==='yes')" in html
print('STAGE 3D-B PUBLIC GEOGRAPHY, HYDROLOGY, DOWNLOAD AND PRIVACY CONTRACT: PASS')
