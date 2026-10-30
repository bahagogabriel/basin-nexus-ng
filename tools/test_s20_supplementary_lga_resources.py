#!/usr/bin/env python3
"""Supplementary source-inventory gate: no invented coordinates or catchment assignments."""
import json
from pathlib import Path
from collections import Counter
base=Path(__file__).resolve().parents[1]/'site'
d=json.loads((base/'data/supplementary_lga_resource_references.json').read_text(encoding='utf-8'))
admin=json.loads((base/'data/admin_crosswalk_provisional.json').read_text(encoding='utf-8'))
assert d['schema_version']=='BN_S20_SUPPLEMENTARY_LGA_INVENTORY_V1'
assert (d['mapped_records'],d['unmapped_records'],d['catchment_count'])==(127,21,2)
assert len(d['records'])==127 and len(d['unmapped'])==21
assert Counter(x['catchment_id'] for x in d['records'])=={'SCMP-C08':59,'SCMP-C20':68}
names={'MINERALS WITHIN THE MARIGA CATCHMENT.docx',
       'GONGOLA_GOMBE STATE MINERAL RESOURCES AND THEIR LOCATIONS.docx',
       'Grazing Reserves within Mariga_kaduna in Niger State -.docx'}
seen=set()
for item in d['records']+d['unmapped']:
 assert item['id'] not in seen; seen.add(item['id'])
 assert item['source_document'] in names
 assert item['category'] in ('mineral','ecology')
 assert item['name'] and item['reported_lga']
 assert item['verification']=='SUPPLEMENTARY_INSTITUTIONAL_SOURCE_REPORT_NOT_FIELD_VERIFIED'
 assert item['precision']=='LGA_INTERSECTION_REPRESENTATIVE_NOT_SURVEYED'
 assert not any(k in item for k in ('latitude','longitude','coordinates','geometry','owner_drive_id','surveyed_site'))
 assert item['catchment_id'] in ('SCMP-C08','SCMP-C20')
 if item['category']=='ecology':
  assert item['name'].endswith(' grazing reserve')
  assert item['source_document'].startswith('Grazing Reserves')
  assert item['reported_legal_status'] in ('Gazetted','Not Gazetted')
  assert item['reported_area_ha']>0
 else:
  assert 'reported_legal_status' not in item
 if item['source_scope']=='GOMBE_STATE_GONGOLA_SUPPLEMENTARY_MINERALS':
  assert item['catchment_id']=='SCMP-C20' and item['state']=='Gombe'
 if item['source_scope']=='KADUNA_MARIGA_NIGER_STATE_MINERAL_INVENTORY':
  assert item['catchment_id']=='SCMP-C08'
for item in d['records']:
 match=[l for l in admin['byCatchment'][item['catchment_id']]['lgas'] if l['id']==item['lga_uid']]
 assert len(match)==1
 assert (match[0]['name'],match[0]['state'])==(item['lga_name'],item['state'])
 assert abs(match[0]['km2']-item['intersection_km2'])<.015 and item['intersection_km2']>=.5
for item in d['unmapped']:
 assert item['status']=='REVIEW_ONLY_NOT_PLOTTED'
 assert item['review_reason']=='NAMED_LGA_NO_POSITIVE_INTERSECTION_WITH_NOMINATED_CATCHMENT'
 assert 'lga_uid' not in item and 'coordinates' not in item
 assert not any(l['name'].lower()==item['reported_lga'].lower() and l['km2']>=.5
  for l in admin['byCatchment'][item['catchment_id']]['lgas'])
assert d['counts_by_catchment']=={'SCMP-C08':59,'SCMP-C20':68}
assert any(x['name']=='Talc' and x['lga_name']=='Rafi' for x in d['records'])
assert any(x['name']=='Coal' and x['lga_name']=='Akko' for x in d['records'])
assert any(x['name']=='Bobi grazing reserve' and x['lga_name']=='Mariga' for x in d['records'])
assert any(x['name']=='Iri grazing reserve' and x['reported_lga']=='Rijau' for x in d['unmapped'])
html=(base/'index.html').read_text(encoding='utf-8')
for token in ('supplementary_lga_resource_references.json','acceptSupplementaryLGAEvidence','supplementaryLGAEvidence','source_document'):
 assert token in html
assert json.loads((base/'data/confirmed_dam_sites.json').read_text(encoding='utf-8'))['records']==[]
print('S20 supplementary source QA PASS: 127 LGA reports mapped, 21 outside-area reports withheld, no invented coordinates')
