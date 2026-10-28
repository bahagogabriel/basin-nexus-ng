#!/usr/bin/env python3
"""Source index restricted to theme presence; no claims, private IDs or locations."""
import json
from datetime import date
from pathlib import Path
site=Path(__file__).resolve().parents[1]/'site'
d=json.loads((site/'data/stakeholder_coverage_index.json').read_text())
registry=json.loads((site/'data/registry.json').read_text())
assert d['publication_status']=='PUBLIC_METADATA_ONLY'
assert d['engagement_provenance_status']=='SOURCE_EVENT_METADATA_ONLY'
assert d['source_records_publicly_cleared']==0
assert 'official endorsement' in d['attribution_notice']
assert d['coordinates_or_observations_published'] is False
assert d['source_documents_reviewed']==len(d['catchments'])==20
assert not d['source_contents_published'] and not d['coordinates_or_observations_published']
assert {x['id'] for x in registry}=={x['id'] for x in d['catchments']}
keys={t['key'] for t in d['themes']}
assert keys=={'natural_resources','threats_challenges','socioeconomics','policies'}
for x in d['catchments']:
 assert set(x)=={'id','name','source_documents_located','source_section_keys','verification','public_release','source_type','engagement_date_start','engagement_date_end','engagement_period','engagement_city','evidence_status'}
 assert x['source_type']=='SCMP institutional stakeholder engagement communiqué'
 assert x['evidence_status']=='Source documented; individual claims withheld pending review'
 assert date(2024,1,1)<=date.fromisoformat(x['engagement_date_start'])<=date.fromisoformat(x['engagement_date_end'])<=date(2025,12,31)
 assert x['engagement_date_start'][-10:] and len(x['engagement_city'])>=4
 assert set(x['source_section_keys'])==keys
 assert x['source_documents_located']==1 and x['public_release']=='Metadata only'
assert sum(c['engagement_date_start'].startswith('2024-') for c in d['catchments'])==6
assert sum(c['engagement_date_start'].startswith('2025-') for c in d['catchments'])==14
assert {c['engagement_city'] for c in d['catchments']}=={'Kano','Sokoto','Ilorin','Lokoja','Gombe'}
html=(site/'index.html').read_text()
assert 'thematic evidence explorer v1.11' in html
assert "id=\"knowledgeLenses\"" in html
assert "id=\"knowledgeCrossborder\"" in html
assert "function renderKnowledgeLens(rows)" in html
assert "function renderKnowledgeCardLens(c,row,admin,river)" in html
assert 'function downloadKnowledgeCSV()' in html
assert 'function updateKnowledgeLGAOptions()' in html
assert 'function filteredKnowledge()' in html
assert 'FAO modeled river reaches' in html
assert 'source metadata only' in html
assert "state==='all'||(admin?.states||[]).some(s=>s.name===state)" in html
assert "lga==='all'||(admin?.lgas||[]).some(l=>l.id===lga)" in html
assert "city==='all'||c.engagement_city===city" in html
for s in ('id="navKnowledge"','id="pageKnowledge"','id="knowledgeSearch"','id="knowledgeTheme"','id="knowledgeCards"','function renderKnowledge()','data/stakeholder_coverage_index.json','id="knowledgeYear"','id="knowledgeCity"','id="knowledgeState"','id="knowledgeLGA"','id="knowledgeSort"','id="knowledgeCrossborder"','id="knowledgeExport"','id="knowledgeReset"','class="knowledgeEvidence"','Institutional SCMP engagement communiqué'):
 assert s in html,s
for s in ('drive.google.com/file/','4,929 evidence entries','Signed Stakeholder Engagement'):
 assert s.lower() not in html.lower()
print('SOURCE INDEX PRIVACY AND PUBLIC READINESS: PASS')
