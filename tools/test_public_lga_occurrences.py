#!/usr/bin/env python3
import json
from pathlib import Path
site=Path(__file__).resolve().parents[1]/'site'
d=json.loads((site/'data/public_lga_occurrences.json').read_text())
a=json.loads((site/'data/admin_crosswalk_provisional.json').read_text())
assert d['schema_version']=='BN_PUBLIC_LGA_OCCURRENCE_PILOT_V1' and d['restricted_workshop_records_included']==0
r=d['records']
assert len(r)==15 and len({x['id'] for x in r})==15 and len({x['lga_id'] for x in r})==11
assert {x['catchment_id'] for x in r}=={'SCMP-C17'}
assert set(x['category'] for x in r)=={'crop','mineral','ecology','pressure'}
for x in r:
 assert x['spatial_scope']=='LGA_REPRESENTATIVE_POSITION_NOT_EXACT_ASSET'
 assert x['evidence_status']=='PUBLISHED_PLAN_STAKEHOLDER_REPORTED'
 assert x['source_pdf_page'] in (176,177) and x['public_report_url'].startswith('https://acresal.gov.ng/')
 assert not any(key in x for key in ('latitude','longitude','coordinates','geometry'))
 matches=[y for y in a['byCatchment']['SCMP-C17']['lgas'] if y['id']==x['lga_id']]
 assert len(matches)==1 and matches[0]['name']==x['lga_name'] and matches[0]['state']==x['state']
h=(site/'index.html').read_text()
for token in ('occurrenceLayerToggle','occurrenceCategory','public_lga_occurrences.json','drawOccurrenceSymbols','renderOccurrenceList','guideQuickstart'):
 assert token in h,token
assert json.loads((site/'data/public_evidence_catalogue.json').read_text())['records']==[]
print('S15 public occurrence pilot PASS: 15 LGA-scoped records; 11 LGAs; no invented asset coordinates')
