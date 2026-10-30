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
assert "officialSCMPEntries" in html and "renderOfficialSCMPReports(result)" in html
assert mod["official_scmp_publication_links"]["listed_pages"]==9
assert mod["official_scmp_publication_links"]["indexed_direct_pdfs"]==9
assert sum(bool(r["official_publication_page"]) for r in records)==9
assert sum(bool(r["official_public_pdf"]) for r in records)==9
assert all(r["official_report_link_status"]==("ACRESAL_PUBLICATION_ENTRY_INDEXED" if r["official_publication_page"] else "INDIVIDUAL_PUBLIC_LINK_NOT_VERIFIED") for r in records)
assert all((r["official_publication_page"] is None or r["official_publication_page"].startswith("https://acresal.gov.ng/publications/")) and (r["official_public_pdf"] is None or r["official_public_pdf"].startswith("https://acresal.gov.ng/wp-content/uploads/2025/11/")) for r in records)
assert mod["official_report_page_guides"]["total_page_anchors"]==24
assert mod["official_report_page_guides"]["publisher_pdf_pages_indexed"]==7
page_entries=mod["official_report_page_guides"]["entries"]
assert len(page_entries)==24 and len({x["catchment_id"] for x in page_entries})==7
assert all(x["catchment_id"] in {r["id"] for r in records if r["official_public_pdf"]} for x in page_entries)
assert all(x["review_scope"]=="PUBLIC_REPORT_PAGE_NAVIGATION_ONLY" and isinstance(x["pdf_page_1_based"],int) and 1<=x["pdf_page_1_based"]<=277 for x in page_entries)
assert all(set(x)=={"catchment_id","theme","topic","pdf_page_1_based","review_scope"} for x in page_entries)
assert "officialSCMPPages" in html and "pdf_page_1_based" in html
activity=mod["official_2026_consultations"]
assert activity["status"]=="OFFICIAL_PUBLISHER_REPORTING_ONLY"
assert activity["count_catchments_in_final_10"]==10
assert activity["count_individual_activity_articles"]==5
assert activity["individual_story_source_types"]=={"ACReSAL":4,"FCT ACReSAL":1}
assert len(activity["catchments"])==20 and {r["id"] for r in activity["catchments"]}==ids
assert sum(r["mentioned_in_2026_oct15_final_ten"] for r in activity["catchments"])==10
assert sum(bool(r["individual_activity_news"]) for r in activity["catchments"])==5
assert all(not r["individual_activity_news"] or r["mentioned_in_2026_oct15_final_ten"] for r in activity["catchments"])
assert all(not r["individual_activity_news"] or (r["individual_activity_news"]["url"].startswith("https://acresal.gov.ng/") or r["individual_activity_news"]["url"].startswith("https://www.acresalfcta.org.ng/")) for r in activity["catchments"])
assert activity["all_20_validated_attribution"]["source_date"]=="2026-03-22"
assert activity["final_10_consultation_phase"]["source_date"]=="2026-10-15"
assert "official2026Updates" in html and "renderOfficial2026Updates(result)" in html
archive=mod["official_2025_event_archive"]
assert archive["articles"]==5 and len(archive["events"])==5
assert archive["distinct_linked_catchments"]==11
assert len({cid for e in archive["events"] for cid in e["catchment_ids"]})==11
assert all(e["date"].startswith("2025-") and e["url"].startswith("https://acresal.gov.ng/") for e in archive["events"])
assert all(set(e["catchment_ids"])<=ids for e in archive["events"])
assert "SCMP-C20" not in {cid for e in archive["events"] for cid in e["catchment_ids"]}
assert "renderOfficial2025Events(result)" in html and "official2025Archive" in html
assert next(r for r in records if r["id"]=="SCMP-C12")["official_public_pdf"].endswith("NGADA-WEST-CHAD-STRATEGICCATCHMENTMANAGEMENTPLAN-Ready1.pdf")
pilot=mod["public_report_profile_pilot"]
assert pilot["version"]=="BN_PUBLIC_SCMP_REPORT_PROFILES_V1"
assert pilot["status"]=="PUBLISHER_PLAN_PARAPHRASE_ONLY"
assert {p["id"] for p in pilot["profiles"]}=={"SCMP-C14","SCMP-C17"}
assert all(len(p["topics"])==5 for p in pilot["profiles"])
assert all({t["theme"] for t in p["topics"]}=={"natural_resources","threats_challenges","socioeconomics","policies","past_present_interventions"} for p in pilot["profiles"])
assert all(25<=len(t["summary"])<=350 for p in pilot["profiles"] for t in p["topics"])
assert "catchmentInsightsPanel" in html and "renderCatchmentInsights(result)" in html
assert "data-insight-map" in html and "insightTheme" in html
assert "renderCatchmentContentBridge(c)" in html
assert "profilePublishedSections" in html
assert "sourceSections" in html
assert "official_report_page_guides" in html
assert "profileTopics" in html and "data-open-catchment-topic" in html
assert "syncCatchmentURL(id)" in html and "restoreSharedCatchment()" in html
assert "window.history.replaceState" in html
assert "el('insightTheme').value=theme" in html
assert "Direct link to this catchment" in html
assert "renderStakeholderResourcePanel(c)" in html
assert "resourceGlobalPanel" in html and "resourceAtlasToggle" in html
assert mod["individual_public_claims_approved"]==0
assert 'value="past_present_interventions"' in html and "sourceContentModel" in html
for bad in ("drive.google.com","private_drive_id","original_source_excerpt_private","source_file_name_private","source_url_private","Signed Stakeholder Engagement"):
    assert bad.lower() not in (json.dumps(mod)+json.dumps(idx)+html).lower(),bad
print("STAGE S2 SOURCE CONTENT AND PUBLICATION-GATE QA: PASS")
