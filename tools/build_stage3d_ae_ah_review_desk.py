#!/usr/bin/env python3
"""Stages 3D-AE–AH: five-case deterministic evidence routing, never facility admission.

This is a source-only review desk. Nothing here can confirm, rename, deduplicate
or publish dams or disclose restricted stakeholder source material.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from urllib.parse import urlparse

IDS=("WA26-003","WA26-184","WA26-185","WA26-186","WA26-083")
SHA="2dc9c81925ea2ed6b2cb82f13410868a96ccc93d1897f3eda6040e924c9dd82a"
RECEIPTS=("structure_exists_independent_evidence_url","facility_status_evidence_date",
"reviewed_dam_wall_position_WGS84","wall_position_method","wall_position_uncertainty_m",
"independent_source_lineage_assessment","image_interpretation_notes_with_dates",
"independent_engineering_or_field_source","reviewer_identity_and_organization",
"human_review_date","rights_privacy_release_receipt","specific_publication_approval")
ACTIONS={
"WA26-003":("P0_DOCUMENTED_FACILITY_LEAD_UNMATCHED",
"Request the Gusau Barrage as-built/dam-wall survey and resolve the inventory-versus-water-intake coordinate discrepancy; do not infer identical structures"),
"WA26-184":("P1_CLOSE_DIGITIZED_BARRIER_WITHOUT_INDEPENDENT_PROOF",
"Obtain dated high-resolution images or engineering/field records showing a constructed wall with independently located position and uncertainty"),
"WA26-185":("P1_CLOSE_DIGITIZED_BARRIER_WITHOUT_INDEPENDENT_PROOF",
"Obtain dated high-resolution images or engineering/field records showing a constructed wall with independently located position and uncertainty"),
"WA26-186":("P1_CLOSE_DIGITIZED_BARRIER_WITHOUT_INDEPENDENT_PROOF",
"Obtain dated high-resolution images or engineering/field records showing a constructed wall with independently located position and uncertainty"),
"WA26-083":("P2_REPEATED_GUSAU_NAME_NOT_RESOLVED",
"Request a separate authoritative facility-identity and dam-wall survey record; do not inherit WA26-003 government references")}
FIXED={"schema_version":"BN_STAGE3D_AA_AD_REVIEW_ONLY_V1",
"status":"HUMAN_EVIDENCE_REQUIRED_NO_DAM_ADMISSIONS",
"source_doi":"10.60507/FK2/YLDK1Y","source_preview_sha256":SHA,
"source_license":"CC BY 4.0","osm_license":"ODbL","review_subjects":5,
"confirmed_dams":0,"published_facility_points_created":0,
"published_private_evidence_created":0,
"digital_evidence_context_does_not_prove_source_independence":True,
"pending_human_observations":60}

def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,
      separators=(",",":")).encode("utf-8")).hexdigest()

def validate_source(data):
    if not isinstance(data,dict):raise ValueError("Expected review-only source object")
    for k,v in FIXED.items():
        if data.get(k)!=v or type(data.get(k))!=type(v):
            raise ValueError("Source schema, publisher lineage or zero-admission contract changed: "+k)
    rows=data.get("review_cases")
    if not isinstance(rows,list) or len(rows)!=5:raise ValueError("Exactly five review cases expected")
    indexed={}
    for row in rows:
        ref=row.get("research_reference_id")
        if ref not in IDS or ref in indexed:raise ValueError("Unknown/duplicated research reference")
        position=row.get("original_compiled_point_WGS84_NOT_WALL")
        if (not isinstance(position,list) or len(position)!=2
            or any(type(q) not in (int,float) or not math.isfinite(q) for q in position)
            or not 2<=position[0]<=16 or not 4<=position[1]<=15):
            raise ValueError("Invalid source-only coordinate")
        if (row.get("editorial_status")!="HOLD_REVIEW_ONLY"
            or row.get("exists_as_constructed_dam_independently_verified") is not False
            or row.get("wall_position_independently_verified") is not False
            or row.get("source_lineage_independent") is not False
            or row.get("human_public_release_authorized") is not False):
            raise ValueError("Input reference is not unverified")
        receipts=row.get("human_release_receipts")
        if not isinstance(receipts,dict) or set(receipts)!=set(RECEIPTS) or any(v is not None for v in receipts.values()):
            raise ValueError("Human evidence receipts must remain empty")
        optical=row.get("sentinel_SCL_temporal_descriptive_QA")
        if (not isinstance(optical,dict)
            or optical.get("interpretation_status")!="UNINTERPRETED_PIXEL_CLASSIFICATION_NOT_A_DAM"
            or optical.get("is_not_dam_construction_evidence") is not True
            or optical.get("is_not_reservoir_area_change") is not True
            or not isinstance(optical.get("periods"),dict)
            or set(optical["periods"])!={"historical_2019","recent_2026"}):
            raise ValueError("Optical classification not evidence of dam construction")
        osm=row.get("OSM_polyline_review_metrics")
        if osm is not None and (not isinstance(osm,dict) or
            osm.get("distance_is_not_position_accuracy") is not True or
            osm.get("wall_position_independently_confirmed") is not False):
            raise ValueError("Crowdsourced line cannot be a surveyed dam wall")
        leads=row.get("independent_public_documentary_context_NOT_FACILITY_RECEIPTS")
        if not isinstance(leads,list):raise ValueError("Missing documentary source contexts")
        if ref=="WA26-003":
            if len(leads)!=2 or {v.get("reported_coordinate_kind") for v in leads}!={
              "DAM_INVENTORY_REPORTED_COORDINATE_NOT_SURVEYED_BY_THIS_PROJECT",
              "WATER_ABSTRACTION_INTAKE_POINT_NOT_DAM_WALL"}:
                raise ValueError("Gusau government inventory versus water intake conflated")
            for lead in leads:
                if (lead.get("facility_identity_matched_independently") is not False
                  or lead.get("wall_position_surveyed_independently") is not False
                  or lead.get("source_lineage_independence_verified") is not False
                  or lead.get("release_authorized") is not False):
                    raise ValueError("Official source lead misrepresented as independently verified")
        elif leads:raise ValueError("Gusau source cannot be assigned to different reference")
        indexed[ref]=row
    if set(indexed)!=set(IDS):raise ValueError("Incomplete review queue")
    return indexed

def build(data):
    indexed=validate_source(data)
    cases=[]
    for ref in IDS:
        r=indexed[ref]
        documents=[]
        for x in r["independent_public_documentary_context_NOT_FACILITY_RECEIPTS"]:
            url=x["document_url"]
            if urlparse(url).scheme!="https":raise ValueError("Unsafe documentary URL")
            documents.append({"url":url,"original_record_label":x["record_label"],
              "original_coordinate_kind_NOT_WALL_SURVEY":x["reported_coordinate_kind"],
              "source_to_reported_position_m_NOT_ACCURACY":x["source_point_to_reported_position_m"],
              "independent_facility_identity_match":False})
        optical=r["sentinel_SCL_temporal_descriptive_QA"]
        metric=r.get("OSM_polyline_review_metrics") or {}
        priority,action=ACTIONS[ref]
        cases.append({"reference_id":ref,"priority":priority,"immediate_action":action,
          "source_label_NOT_CONFIRMED":r["source_name_NOT_VERIFIED"],
          "original_compiled_WGS84_NOT_A_WALL":r["original_compiled_point_WGS84_NOT_WALL"],
          "osm_way_NOT_SURVEYED":r["osm_way"],
          "source_to_digitized_osm_line_m_NOT_SURVEY_ACCURACY":metric.get("source_to_osm_polyline_nearest_m"),
          "independent_documentary_LEADS_NOT_MATCHES":documents,
          "optical_review_dates":{epoch:optical["periods"][epoch]["acquired_utc"]
                                  for epoch in ("historical_2019","recent_2026")},
          "optical_SCL_water_diff_percentage_points_NOT_DAM_CHANGE":
                optical["center_SCL_water_fraction_difference_percentage_points_DESCRIPTIVE_ONLY"],
          "human_evidence_requirements_NOT_FULFILLED":list(RECEIPTS),
          "review_status":"HOLD_NOT_ASSESSED_BY_ACCOUNTABLE_REVIEWER",
          "identity_verified":False,"existence_verified":False,"wall_position_verified":False,
          "source_independence_verified":False,"public_release_authorized":False})
    return {"schema_version":"BN_STAGE3D_AE_AH_REVIEW_DESK_V1",
      "status":"RESEARCH_ONLY_ZERO_CONFIRMED_ZERO_RELEASED",
      "upstream_case_document_sha256":digest(data),
      "original_compiled_preview_sha256":SHA,"publisher_doi":FIXED["source_doi"],
      "original_source_license":"CC BY 4.0","osm_license":"ODbL",
      "review_case_count":5,"unfilled_human_evidence_receipts":60,
      "independently_confirmed_dams":0,"public_map_changes":False,
      "no_automatic_public_approval":True,"cases":cases}

def blank_routing_form(desk):
    if desk.get("schema_version")!="BN_STAGE3D_AE_AH_REVIEW_DESK_V1":
        raise ValueError("Unknown desk")
    return {"schema_version":"BN_STAGE3D_AF_ROUTING_FORM_V1",
      "upstream_case_document_sha256":desk["upstream_case_document_sha256"],
      "allows_approval_or_publication":False,
      "cases":[{"reference_id":x["reference_id"],"routing_decision":"HOLD",
         "human_evidence_receipts":{k:None for k in RECEIPTS},
         "second_review_required":True,"approved_for_publication":False}
          for x in desk["cases"]]}

def validate_routing_form(desk,form):
    if (not isinstance(form,dict)
        or set(form)!={"schema_version","upstream_case_document_sha256","allows_approval_or_publication","cases"}
        or form["schema_version"]!="BN_STAGE3D_AF_ROUTING_FORM_V1"
        or form["upstream_case_document_sha256"]!=desk["upstream_case_document_sha256"]
        or form["allows_approval_or_publication"] is not False):
        raise ValueError("Tampered source digest or publication controls")
    cases=form["cases"]
    if not isinstance(cases,list) or len(cases)!=5:raise ValueError("Five source cases required")
    seen=set()
    for row in cases:
        if (not isinstance(row,dict) or set(row)!={"reference_id","routing_decision",
           "human_evidence_receipts","second_review_required","approved_for_publication"}):
            raise ValueError("Unknown or private routing fields")
        ref=row["reference_id"]
        if ref not in IDS or ref in seen:raise ValueError("Duplicate or unknown case")
        seen.add(ref)
        if (row["routing_decision"] not in ("HOLD","NEEDS_INDEPENDENT_REVIEW")
            or row["second_review_required"] is not True
            or row["approved_for_publication"] is not False):
            raise ValueError("This route cannot approve a dam")
        receipt=row["human_evidence_receipts"]
        if not isinstance(receipt,dict) or set(receipt)!=set(RECEIPTS) or any(v is not None for v in receipt.values()):
            raise ValueError("Actual receipts belong in independently authorized secure human review")
    if seen!=set(IDS):raise ValueError("Missing case")
    return {"review_routing_valid":True,"outstanding_receipts":60,"releasable":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    args=p.parse_args()
    if args.output_dir.exists():raise SystemExit("Refusing overwrite")
    desk=build(json.loads(args.source.read_text("utf-8")))
    form=blank_routing_form(desk)
    validate_routing_form(desk,form)
    args.output_dir.mkdir(parents=True)
    (args.output_dir/"STAGE3D_AE_AH_REVIEW_CASES_NOT_CONFIRMED.json").write_text(json.dumps(desk,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (args.output_dir/"STAGE3D_AF_BLANK_ROUTING_FORM.json").write_text(json.dumps(form,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# Surgical Stage 3D-AE–AH next-action review queue","",
      "**Five independent-review cases, zero confirmed dams, no public data changes.**","",
      "| Rank | Reference | Review priority | Specific next evidence request |","|---:|---|---|---|"]
    for i,c in enumerate(desk["cases"],1):
        lines.append(f"| {i} | {c['reference_id']} | {c['priority']} | {c['immediate_action']} |")
    lines.extend(["","Do not equate government water-intake positions with surveyed wall positions. "
      "Do not count crowdsourced OSM and a matching compiled source as independent facility proof.",
      "Actual physical construction, independently checked coordinates and uncertainty, source lineage, "
      "rights, accountable review and separate public authorization are still required.",
      "This form is a routing template only. Do not upload restricted stakeholder evidence into this repo."])
    (args.output_dir/"STAGE3D_AG_REVIEW_QUEUE.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("Stage AE–AH: five source-only cases, 60 blank receipts, zero confirmed or published dams")

if __name__=="__main__":main()
