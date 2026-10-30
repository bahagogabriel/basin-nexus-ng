#!/usr/bin/env python3
"""Check that the only published evidence is individually approved; empty until actual decisions."""
import json
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from evidence_publication_gate import validate,SCHEMA_VERSION

site=root/'site'
doc=json.loads((site/'data/public_evidence_catalogue.json').read_text('utf-8'))
ids={row['id'] for row in json.loads((site/'data/registry.json').read_text('utf-8'))}
result=validate(doc,ids)
assert doc['schema_version']==SCHEMA_VERSION
assert set(doc)=={'schema_version','type','publication_status','records'}
# Any future non-empty publication must deliberately update this test and accompanying
# release governance; don't infer authority from a superficially valid PUBLIC-* identifier.
assert doc['records']==[], 'STOP: individual evidence records require new human-reviewed release PR'
assert result=={'validated_public_records':0,'mapped_locations':0}
html=(site/'index.html').read_text('utf-8')
for phrase in (
 '© 2026 Basin Nexus NG', 'Designed by <a href="https://bahagogabriel.com/"',
 'id="evidenceCataloguePanel"','id="evidenceList"','id="evidenceSearch"',
 'id="evidenceStatus"','id="evidenceTheme"',
 "function acceptPublicEvidence(document)",'function renderEvidenceCatalogue(scope)',
 'data/public_evidence_catalogue.json',
 'evidenceLoadState', 'Approved for public release',
 'No individual stakeholder evidence records are cleared',
):
 assert phrase in html,phrase
for key in ('raw_statement_internal','principal_candidate_id','private_drive_id',
            'source_internal_id','source_file_id'):
 assert key not in html,key
print('STAGE 3D-D APPROVED-ONLY EMPTY CATALOGUE, FAIL-CLOSED UI AND PUBLIC FILE GATE: PASS')
