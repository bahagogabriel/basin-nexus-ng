#!/usr/bin/env python3
"""S17: source-approved, anonymized 20-catchment resource inventory contract."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
s=root/'site'
d=json.loads((s/'data/stakeholder_resource_atlas.json').read_text())
registry=json.loads((s/'data/registry.json').read_text())
ids={c['id'] for c in registry}
assert d['schema_version']=='BN_STAKEHOLDER_RESOURCE_ATLAS_V1'
assert d['release_status']=='OWNER_AUTHORIZED_ANONYMIZED_STAKEHOLDER_INVENTORY'
assert d['catchment_count']==len(d['catchments'])==len(ids)==20
assert d['resource_records']==len(d['resources'])==375
assert d['source_mentions']==592
assert set(c['id'] for c in d['catchments'])==ids
assert all(c['distinct_resource_terms']>0 for c in d['catchments'])
assert sum(c['distinct_resource_terms'] for c in d['catchments'])==375
assert sum(c['source_mentions'] for c in d['catchments'])==592
assert len({r['id'] for r in d['resources']})==375
assert sum(r['stakeholder_source_mentions'] for r in d['resources'])==592
cats={'crop','mineral','ecology','water','pressure'}
assert all(set(c['categories'])==cats for c in d['catchments'])
for r in d['resources']:
 assert r['catchment_id'] in ids and r['category'] in cats
 assert r['source_status']=='INSTITUTIONAL_STAKEHOLDER_REPORTED'
 assert r['location_precision']=='CATCHMENT_LEVEL' and r['stakeholder_source_mentions']>=1
 assert r['source_reference']=='Original SCMP catchment stakeholder communiqué'
 assert isinstance(r['source_locators'],list) and isinstance(r['lga_location_hints'],list)
 assert not any(k in r for k in ('lat','lon','latitude','longitude','geometry','coordinates','stakeholder_source_text_private','participant_name','phone','email'))
assert sum(c['categories']['mineral'] for c in d['catchments'])>0
assert next(c for c in d['catchments'] if c['id']=='SCMP-C01')['distinct_resource_terms']==24
assert next(c for c in d['catchments'] if c['id']=='SCMP-C02')['distinct_resource_terms']==27
assert json.loads((s/'data/public_evidence_catalogue.json').read_text())['records']==[]
text=json.dumps(d).lower()
for private in ('drive.google.com','gmail.com','original_source_excerpt_private','stakeholder_source_text_private'):
 assert private not in text
html=(s/'index.html').read_text()
for marker in ('stakeholder_resource_atlas.json','resourceAtlasToggle','resourceAtlasCategory','resourceGlobalSearch','renderStakeholderResourcePanel(c)','renderResourceGlobalSearch','drawStakeholderResourceSymbols()'):
 assert marker in html,marker
print('S17 RESOURCE ATLAS: PASS — 20 catchments, 375 public resource names, 592 original mentions, no private excerpts or inferred coordinates')
