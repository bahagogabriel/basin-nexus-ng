#!/usr/bin/env python3
"""Source index restricted to theme presence; no claims, private IDs or locations."""
import json
from pathlib import Path
site=Path(__file__).resolve().parents[1]/'site'
d=json.loads((site/'data/stakeholder_coverage_index.json').read_text())
registry=json.loads((site/'data/registry.json').read_text())
assert d['publication_status']=='PUBLIC_METADATA_ONLY'
assert d['source_documents_reviewed']==len(d['catchments'])==20
assert not d['source_contents_published'] and not d['coordinates_or_observations_published']
assert {x['id'] for x in registry}=={x['id'] for x in d['catchments']}
keys={t['key'] for t in d['themes']}
assert keys=={'natural_resources','threats_challenges','socioeconomics','policies'}
for x in d['catchments']:
 assert set(x)=={'id','name','source_documents_located','source_section_keys','verification','public_release'}
 assert set(x['source_section_keys'])==keys
 assert x['source_documents_located']==1 and x['public_release']=='Metadata only'
html=(site/'index.html').read_text()
for s in ('id="navKnowledge"','id="pageKnowledge"','id="knowledgeSearch"','id="knowledgeTheme"','id="knowledgeCards"','function renderKnowledge()','data/stakeholder_coverage_index.json'):
 assert s in html,s
for s in ('drive.google.com/file/','4,929 evidence entries','Signed Stakeholder Engagement'):
 assert s.lower() not in html.lower()
print('SOURCE INDEX PRIVACY AND PUBLIC READINESS: PASS')
