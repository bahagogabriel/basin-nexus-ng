#!/usr/bin/env python3
"""Stage 3D-U source-only, non-public evidence receipt worksheet. NO automatic confirmations."""
import argparse, json, re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

EXPECTED={"P0_WITHHELD_IDENTITY":3,"P1_NEARBY_OR_REPEATED_NAME":16,
          "P2_UNNAMED_SOURCE":108,"P3_NAMED_SOURCE":62}
BASE={"source_dataset_doi":"10.60507/FK2/YLDK1Y",
      "source_csv_md5":"046b106da1e3a57ec2f1c461fe411b26",
      "source_shapefile_md5":"a87f9b4ef2e96625b737ffac8595c138",
      "public_source_preview_sha256":"2dc9c81925ea2ed6b2cb82f13410868a96ccc93d1897f3eda6040e924c9dd82a",
      "confirmed_facility_count":0,
      "independent_site_validation_performed":False,
      "automatic_deduplication_performed":False}
SOURCE_KEYS={"reference_id","catchment_id","source_name","coordinates","priority","flags",
             "nearest_compiled_reference","nearest_reference_distance_m_rounded",
             "display_eligibility","independent_existence_verified","position_verified",
             "facility_status","review_outcome"}
FIELDS=("existence_evidence_receipt","existence_observed_on","completed_structure_confirmed",
        "position_validation_method","position_uncertainty_m",
        "source_lineage_independence_receipt","identity_reconciliation_notes",
        "accountable_reviewer","reviewed_on","rights_privacy_permission_receipt",
        "public_release_authorization_receipt")
LEADS={
 "WA26-095":[("Guinea Ministry of Energy","2026-08-13","https://www.energie.gov.gn/%F0%9D%90%95%F0%9D%90%88%F0%9D%90%92%F0%9D%90%88%F0%9D%90%93%F0%9D%90%84-%F0%9D%90%93%F0%9D%90%84%F0%9D%90%82%F0%9D%90%87%F0%9D%90%8D%F0%9D%90%88%F0%9D%90%90%F0%9D%90%94%F0%9D%90%84-%F0%9D%90%83/",
               "Guinean hydroelectric complex identified; Nigeria source point not matched")],
 "WA26-062":[("Nigeria State House","2026-09-18","https://statehouse.gov.ng/icc-case-ab-sunrise-power-and-transmission-company-limited-sunrise-v-federal-government-of-nigeria-nigeria-v-mr-leno-adesanya/",
               "Hydropower development/legal context, not a finished dam at source point"),
              ("Radio Nigeria FRCN","2026-10-03","https://radionigeria.frcn.gov.ng/news/north-east-governors-seek-speedy-completion-of-mambila-hydropower-project",
               "Call for take-off/completion, not confirmation of a built structure")],
 "WA26-027":[("Nigeria Eyemark / Upper Benue RBDA","2026-09-25","https://www.eyemark.ng/project/re-design-and-enviromental-impact-assessment-of-kafin-zaki-dam-ningi-lga-bauchi-state-ergp557112936",
               "Specific redesign/EIA project not started; does NOT establish absence of all physical works")]
}
WITHHELD={"WA26-027":"Kafin Zaki","WA26-062":"Mambilla","WA26-095":"Souapiti"}


def build(data, strict=True):
    if data.get("schema_version")!="BN_WA_DAM_REFERENCE_TRIAGE_V1" or data.get("status")!="REVIEW_ONLY_COMPILED_SOURCES_NO_CONFIRMED_DAMS":
        raise ValueError("Wrong review-only triage schema/status")
    for key, value in BASE.items():
        if data.get(key)!=value or type(data.get(key))!=type(value):
            raise ValueError("Source hash, lineage or zero-confirmed status mismatch: "+key)
    rows=data.get("review_queue")
    if not isinstance(rows,list):raise ValueError("Missing compiled-source queue")
    seen=set(); priorities=Counter(); selected=[]
    for q in rows:
        if not isinstance(q,dict) or set(q)!=SOURCE_KEYS:
            raise ValueError("Unexpected input/private source field")
        ref=q["reference_id"]; pr=q["priority"]; point=q["coordinates"]
        if not isinstance(ref,str) or not re.fullmatch(r"WA26-\d{3}",ref) or ref in seen:
            raise ValueError("Missing or duplicated source ID")
        seen.add(ref)
        if pr not in EXPECTED or q["review_outcome"]!="REQUIRES_INDEPENDENT_EVIDENCE":
            raise ValueError("Unapproved review state")
        if (q["independent_existence_verified"] is not False
            or q["position_verified"] is not False
            or q["facility_status"]!="not_assessed"):
            raise ValueError("Cannot promote a compiled reference through worksheet")
        if not re.fullmatch(r"SCMP-C(0[1-9]|1[0-9]|20)",str(q["catchment_id"])):
            raise ValueError("Invalid catchment")
        if (not isinstance(point,list) or len(point)!=2 or
            any(type(n) not in (float,int) for n in point) or
            not (2<=point[0]<=16 and 4<=point[1]<=15)):
            raise ValueError("Invalid WGS84 source reference point")
        name=q["source_name"]
        if name is not None and (not isinstance(name,str) or not 2<=len(name)<=96):
            raise ValueError("Invalid published name")
        if not isinstance(q["flags"],list) or not all(isinstance(flag,str) for flag in q["flags"]):
            raise ValueError("Invalid triage flags")
        if (pr=="P0_WITHHELD_IDENTITY") != (q["display_eligibility"]=="WITHHELD"):
            raise ValueError("Disputed source identity quarantine bypassed")
        priorities[pr]+=1
        if pr not in ("P0_WITHHELD_IDENTITY","P1_NEARBY_OR_REPEATED_NAME"):continue
        leads=[]
        for publisher,date,url,scope in LEADS.get(ref,[]):
            if urlparse(url).scheme!="https" or not urlparse(url).netloc:raise ValueError("Unsafe evidence URL")
            leads.append({"publisher":publisher,"document_date":date,"url":url,
                          "claim_scope":scope,"independent_point_match":False})
        selected.append({"source_reference_id":ref,"source_published_name":name,
                         "catchment_id":q["catchment_id"],
                         "compiled_reference_position_WGS84":point,
                         "triage_priority":pr,"triage_flags":q["flags"],
                         "source_context_leads_NOT_SITE_RECEIPTS":leads,
                         **{key:None for key in FIELDS},
                         "confirmation_status":"HOLD_UNVERIFIED",
                         "public_layer_status":"NO_CHANGE",
                         "point_validation_performed":False,
                         "eligible_for_public_confirmation":False})
    if strict:
        if (len(rows)!=189 or data.get("candidate_count")!=189 or priorities!=EXPECTED
            or data.get("priority_counts")!=EXPECTED
            or data.get("source_named_count")!=71 or data.get("source_unnamed_count")!=118
            or data.get("withheld_identity_count")!=3 or len(selected)!=19):
            raise ValueError("Original 189/71/118 and 3/16/108/62 source audit drift")
        withheld={row["source_reference_id"]:row["source_published_name"] for row in selected
                  if row["triage_priority"]=="P0_WITHHELD_IDENTITY"}
        if withheld!=WITHHELD:raise ValueError("Three withheld names/IDs changed")
    return {"schema_version":"BN_STAGE3D_U_HIGH_PRIORITY_REVIEW_WORKSHEET_V2",
            "status":"REVIEW_ONLY_ZERO_CONFIRMED_NOT_PUBLIC_SITE_DATA",
            "prepared_on":"2026-10-28",
            "source_doi":BASE["source_dataset_doi"],"source_license":"CC BY 4.0",
            "source_publisher_csv_md5":BASE["source_csv_md5"],
            "source_publisher_shapefile_md5":BASE["source_shapefile_md5"],
            "source_pinned_public_preview_sha256":BASE["public_source_preview_sha256"],
            "source_records_total":len(rows),"high_priority_cases":len(selected),
            "withheld_source_identifications":priorities["P0_WITHHELD_IDENTITY"],
            "research_identity_or_proximity_flags":priorities["P1_NEARBY_OR_REPEATED_NAME"],
            "reviewed_and_confirmed":0,"automated_evidence_confirmation_performed":False,
            "authorization_mechanism":"NONE: this worksheet cannot authorize/publicly release a dam",
            "instructions":"Public documentary context is a research lead, NOT an existence/position receipt. Every site requires independent physical existence/position evidence, method, uncertainty, reviewer, dates, rights and authorization. Missing source names are Unnamed reference point, NOT confirmed Unnamed dam.",
            "records":selected}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--triage",required=True,type=Path)
    parser.add_argument("--review-output",required=True,type=Path)
    args=parser.parse_args()
    if args.review_output.exists():raise SystemExit("Refusing to overwrite workbench")
    out=build(json.loads(args.triage.read_text(encoding="utf-8")))
    args.review_output.parent.mkdir(parents=True,exist_ok=True)
    with args.review_output.open("x",encoding="utf-8") as fd:
        json.dump(out,fd,indent=2,ensure_ascii=False);fd.write("\n")
    print("STAGE3D-U: non-public high-priority review workbench",
          out["high_priority_cases"],"cases, confirmed=0")

if __name__=="__main__":main()
