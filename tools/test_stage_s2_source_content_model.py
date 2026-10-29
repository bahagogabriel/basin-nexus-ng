#!/usr/bin/env python3
"""Stage S2: public metadata-only evidence gate, no private originals loaded."""
import json
from pathlib import Path
s=Path(__file__).resolve().parents[1]/"site"
idx=json.loads((s/"data/stakeholder_coverage_index.json").read_text(encoding="utf-8"))
mod=json.loads((s/"data/source_content_publication_model.json").read_text(encoding="utf-8"))
pub=json.loads((s/"data/public_evidence_catalogue.json").read_text(encoding="utf-8"))
html=(s/"index.html").read_text(encoding="utf-8")
ids={x["id"] for x in idx["catchments"]}
assert len(ids)==20 and len(idx["catchments"])==20
assert mod["schema_version"]=="BN_SOURCE_CONTENT_PUBLIC_V1"
assert mod["publication_status"]=="PUBLIC_METADATA_ONLY" and mod["individual_public_claims_approved"]==0
assert mod["source_material_publicly_released"] is False
assert pub["publication_status"]=="APPROVED_PUBLIC_ONLY" and pub["records"]==[]
records=mod["catchments"]
assert len(records)==20 and {x["id"] for x in records}==ids
assert all(x["principal_communique_indexed"] is True for x in records)
assert all(x["public_approved_claims"]==0 and x["review_release_status"]=="HOLD" for x in records)
assert all(x["spatial_claims_cleared"] is False and x["signed_materials_published"] is False for x in records)
assert sum(x["original_intervention_phrase_indexed"] for x in records)==14
assert sum(x["linked_shared_vision_source_in_restricted_set"] for x in records)==19
actual={x["id"] for x in idx["catchments"] if "past_present_interventions" in x["source_section_keys"]}
expected={x["id"] for x in records if x["original_intervention_phrase_indexed"]}
assert actual==expected
assert len(mod["thematic_sections"])==9
assert len({x["key"] for x in mod["thematic_sections"]})==9
assert all(x["release_state"]=="WITHHELD_PENDING_REVIEW" for x in mod["thematic_sections"])
import sys
sys.path.insert(0,str(s.parents[0]/"tools"))
from evidence_publication_gate import ALLOWED_FIELDS,SCHEMA_VERSION
assert mod["future_evidence_gate_schema_version"]==SCHEMA_VERSION
assert set(mod["future_approved_record_schema_fields"])==ALLOWED_FIELDS
assert set(mod["future_required_record_fields"])<=ALLOWED_FIELDS
assert set(mod["future_optional_record_fields"])==ALLOWED_FIELDS-set(mod["future_required_record_fields"])
assert mod["future_approved_record_count"]==0
assert mod["future_evidence_gate_validator"]=="tools/evidence_publication_gate.py"
assert "data/source_content_publication_model.json" in html
assert 'value="past_present_interventions"' in html and "sourceContentModel" in html
for bad in ("drive.google.com","private_drive_id","original_source_excerpt_private","source_file_name_private","source_url_private","Signed Stakeholder Engagement"):
    assert bad.lower() not in (json.dumps(mod)+json.dumps(idx)+html).lower(),bad
print("STAGE S2 SOURCE CONTENT AND PUBLICATION-GATE QA: PASS")
