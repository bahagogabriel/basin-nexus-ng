#!/usr/bin/env python3
"""Stage 3D-AI–AK: OFFLINE only, private dam evidence-intake completeness audit.

This is NOT a dam confirmer, reviewer approval, source authentication, release
gate bypass or uploader. Filled evidence and even redacted reports are forbidden
in the public Basin Nexus repository. Runtime has no networking.
"""
from __future__ import annotations
import argparse
from datetime import date
import hashlib
import json
import math
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

from build_stage3d_ae_ah_review_desk import IDS, SHA
from validate_confirmed_dam_sites import METHODS, EXISTENCE

SCHEMA="BN_STAGE3D_AI_PRIVATE_FACILITY_EVIDENCE_V1"
REPORT_SCHEMA="BN_STAGE3D_AK_REDACTED_COMPLETENESS_V1"
DOCUMENT_KEYS={"source_id","source_family","evidence_kind","evidence_locator",
               "observed_on","provenance_note","rights_state"}
PHYSICAL_KINDS=set(EXISTENCE)
POSITION_KINDS=set(METHODS)
DOC_KINDS=PHYSICAL_KINDS | POSITION_KINDS | {"facility_identity_authority","context_only"}
SOURCE_ID=re.compile(r"[A-Z0-9][A-Z0-9-]{2,59}$")
SOURCE_FAMILY=re.compile(r"[a-z][a-z0-9_-]{2,59}$")
PRIVATE_LETTER_KEYS={"schema_version","case_id","desk_sha256","documents",
    "name_review","existence_review","position_review","independence_review","human_review"}
NAME_KEYS={"status","supported_name","source_ids","search_notes"}
EXIST_KEYS={"status","existence_evidence_kind","source_ids","observed_on"}
POS_KEYS={"status","lon","lat","method","source_ids","uncertainty_m","observed_on"}
IND_KEYS={"status","lineage_notes","independent_source_families"}
REVIEW_KEYS={"status","reviewer_name","reviewer_organization","reviewed_on",
             "rights_clearance","privacy_clearance","release_authorization"}


def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,
      allow_nan=False,separators=(",",":")).encode("utf-8")).hexdigest()


def day(value):
    if not isinstance(value,str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}",value):
        return False
    try:
        return date.fromisoformat(value)<=date.today()
    except ValueError:
        return False


def _keys(x,keys):
    if not isinstance(x,dict) or set(x)!=keys:
        raise ValueError("Unexpected or missing private review form fields")


def validate_desk(desk):
    if not isinstance(desk,dict) or (
        desk.get("schema_version")!="BN_STAGE3D_AE_AH_REVIEW_DESK_V1"
        or desk.get("status")!="RESEARCH_ONLY_ZERO_CONFIRMED_ZERO_RELEASED"
        or desk.get("original_compiled_preview_sha256")!=SHA
        or desk.get("publisher_doi")!="10.60507/FK2/YLDK1Y"
        or desk.get("original_source_license")!="CC BY 4.0"
        or desk.get("osm_license")!="ODbL"
        or desk.get("review_case_count")!=5
        or desk.get("unfilled_human_evidence_receipts")!=60
        or desk.get("independently_confirmed_dams")!=0
        or desk.get("public_map_changes") is not False
        or desk.get("no_automatic_public_approval") is not True):
        raise ValueError("Review desk provenance/zero-admission contract altered")
    rows=desk.get("cases")
    if not isinstance(rows,list) or len(rows)!=5 or [x.get("reference_id") for x in rows]!=list(IDS):
        raise ValueError("The five priority reference IDs changed")
    for row in rows:
        if (row.get("review_status")!="HOLD_NOT_ASSESSED_BY_ACCOUNTABLE_REVIEWER"
            or any(row.get(k) is not False for k in (
             "identity_verified","existence_verified","wall_position_verified",
             "source_independence_verified","public_release_authorized"))):
            raise ValueError("Desk contains a promoted candidate")
    return {row["reference_id"]:row for row in rows}


def blank_record(desk,case_id):
    cases=validate_desk(desk)
    if case_id not in cases:raise ValueError("Not a queued case")
    return {"schema_version":SCHEMA,"case_id":case_id,"desk_sha256":sha(desk),
        "documents":[],"name_review":{"status":"UNRESOLVED","supported_name":None,
             "source_ids":[],"search_notes":None},
        "existence_review":{"status":"NOT_REVIEWED","existence_evidence_kind":None,
             "source_ids":[],"observed_on":None},
        "position_review":{"status":"NOT_REVIEWED","lon":None,"lat":None,
             "method":None,"source_ids":[],"uncertainty_m":None,"observed_on":None},
        "independence_review":{"status":"NOT_REVIEWED","lineage_notes":None,
             "independent_source_families":[]},
        "human_review":{"status":"HOLD","reviewer_name":None,"reviewer_organization":None,
            "reviewed_on":None,"rights_clearance":"NOT_CLEARED",
            "privacy_clearance":"NOT_CLEARED","release_authorization":None}}


def check_record(desk,record):
    cases=validate_desk(desk)
    _keys(record,PRIVATE_LETTER_KEYS)
    case_id=record["case_id"]
    if case_id not in cases or record["schema_version"]!=SCHEMA or record["desk_sha256"]!=sha(desk):
        raise ValueError("Review-source fingerprint mismatch, unknown or altered case")
    docs=record["documents"]
    if not isinstance(docs,list) or len(docs)>24:raise ValueError("Unbounded private evidence")
    source_ids={}
    for d in docs:
        _keys(d,DOCUMENT_KEYS)
        sid=d["source_id"];fam=d["source_family"]
        if (not isinstance(sid,str) or not SOURCE_ID.fullmatch(sid) or sid in source_ids
            or not isinstance(fam,str) or not SOURCE_FAMILY.fullmatch(fam)
            or d["evidence_kind"] not in DOC_KINDS):
            raise ValueError("Missing/duplicate receipt identity or unsafe source family")
        locator=d["evidence_locator"]
        # Local absolute source paths or authenticated remote locators are private;
        # never export these. No HTTP used, and no URL is independently verified.
        if not isinstance(locator,str) or not 4<=len(locator)<=1500:
            raise ValueError("Missing private evidence locator")
        if d["observed_on"] is not None and not day(d["observed_on"]):
            raise ValueError("Invalid evidence date")
        note=d["provenance_note"]
        if note is not None and (not isinstance(note,str) or len(note)>1500):
            raise ValueError("Invalid source lineage note")
        if d["rights_state"] not in ("UNREVIEWED","PUBLIC_REUSE_CLEARED","PRIVATE_REVIEW_ONLY"):
            raise ValueError("Invalid evidence rights state")
        source_ids[sid]=d
    name=record["name_review"];exist=record["existence_review"]
    pos=record["position_review"];ind=record["independence_review"]
    review=record["human_review"]
    for x,ks in [(name,NAME_KEYS),(exist,EXIST_KEYS),(pos,POS_KEYS),(ind,IND_KEYS),(review,REVIEW_KEYS)]:
        _keys(x,ks)
    if name["status"] not in ("UNRESOLVED","DOCUMENTARILY_NAMED","NAME_UNAVAILABLE_AFTER_REVIEW"):
        raise ValueError("Unsupported name review status")
    if exist["status"] not in ("NOT_REVIEWED","DOCUMENTS_SUBMITTED_FOR_REVIEW"):
        raise ValueError("Only human evaluation may assess existence")
    if pos["status"] not in ("NOT_REVIEWED","POSITION_SUBMITTED_FOR_REVIEW"):
        raise ValueError("Only human evaluation may assess wall position")
    if ind["status"] not in ("NOT_REVIEWED","FAMILY_INDEPENDENCE_ASSERTED_FOR_REVIEW"):
        raise ValueError("Source independence is not established by this tool")
    if review["status"] not in ("HOLD","REQUEST_SECOND_INDEPENDENT_REVIEW"):
        raise ValueError("Local evidence intake cannot approve or publish a dam")
    if review["release_authorization"] is not None:
        raise ValueError("Explicit release authorization must occur outside this intake")
    if review["rights_clearance"] not in ("NOT_CLEARED","REVIEWER_ASSERTS_CLEARED"):
        raise ValueError("Invalid rights review flag")
    if review["privacy_clearance"] not in ("NOT_CLEARED","REVIEWER_ASSERTS_CLEARED"):
        raise ValueError("Invalid privacy review flag")
    blockers=[]
    def block(code,condition):
        if condition:blockers.append(code)
    if name["status"]=="DOCUMENTARILY_NAMED":
        block("NEED_NAMED_AUTHORITY",not isinstance(name["supported_name"],str)
            or len(name["supported_name"].strip())<2)
    elif name["status"]=="NAME_UNAVAILABLE_AFTER_REVIEW":
        block("NEED_NAME_SEARCH_DOCUMENTATION",not isinstance(name["search_notes"],str)
            or len(name["search_notes"].strip())<10)
    else:block("NEED_IDENTITY_REVIEW",True)
    if not isinstance(name["source_ids"],list) or any(s not in source_ids for s in name["source_ids"]):
        raise ValueError("Name evidence citations must point to submitted sources")
    if (name["status"]=="DOCUMENTARILY_NAMED"
        and not any(source_ids[s]["evidence_kind"]=="facility_identity_authority" for s in name["source_ids"])):
        blockers.append("NEED_INDEPENDENT_NAME_SOURCE")
    if not isinstance(exist["source_ids"],list) or any(s not in source_ids for s in exist["source_ids"]):
        raise ValueError("Existence citations must point to submitted sources")
    if exist["status"]!="DOCUMENTS_SUBMITTED_FOR_REVIEW":blockers.append("NEED_PHYSICAL_WALL_EXISTENCE_RECORD")
    elif (exist["existence_evidence_kind"] not in PHYSICAL_KINDS
          or not any(source_ids[s]["evidence_kind"]==exist["existence_evidence_kind"] for s in exist["source_ids"])
          or not day(exist["observed_on"])):
        blockers.append("NEED_DATED_EXISTENCE_EVIDENCE_MATCH")
    if not isinstance(pos["source_ids"],list) or any(s not in source_ids for s in pos["source_ids"]):
        raise ValueError("Position citations must point to submitted sources")
    if pos["status"]!="POSITION_SUBMITTED_FOR_REVIEW":
        blockers.append("NEED_INDEPENDENT_WALL_POSITION")
    elif (pos["method"] not in POSITION_KINDS
          or not any(source_ids[s]["evidence_kind"]==pos["method"] for s in pos["source_ids"])
          or not day(pos["observed_on"])
          or type(pos["lon"]) not in (int,float) or type(pos["lat"]) not in (int,float)
          or not math.isfinite(pos["lon"]) or not math.isfinite(pos["lat"])
          or not -180<=pos["lon"]<=180 or not -90<=pos["lat"]<=90
          or type(pos["uncertainty_m"]) not in (int,float)
          or not math.isfinite(pos["uncertainty_m"]) or not 1<=pos["uncertainty_m"]<=5000):
        blockers.append("NEED_DATED_MEASURED_WALL_POSITION_AND_UNCERTAINTY")
    families=ind["independent_source_families"]
    if not isinstance(families,list) or any(f not in {d["source_family"] for d in docs} for f in families):
        raise ValueError("Independence assertion refers to unavailable source families")
    # Two declared families are a *routing* constraint; not authenticated independence.
    if (ind["status"]!="FAMILY_INDEPENDENCE_ASSERTED_FOR_REVIEW"
        or len(set(families))<2 or not isinstance(ind["lineage_notes"],str)
        or len(ind["lineage_notes"].strip())<15):
        blockers.append("NEED_DOCUMENTED_DISTINCT_LINEAGES")
    if (not isinstance(review["reviewer_name"],str)
        or len(review["reviewer_name"].strip())<3
        or not isinstance(review["reviewer_organization"],str)
        or len(review["reviewer_organization"].strip())<3
        or not day(review["reviewed_on"])):
        blockers.append("NEED_ACCOUNTABLE_HUMAN_REVIEW")
    if review["rights_clearance"]!="REVIEWER_ASSERTS_CLEARED":
        blockers.append("NEED_RIGHTS_REVIEW")
    if review["privacy_clearance"]!="REVIEWER_ASSERTS_CLEARED":
        blockers.append("NEED_PRIVACY_REVIEW")
    if review["status"]!="REQUEST_SECOND_INDEPENDENT_REVIEW":
        blockers.append("NEED_SECOND_REVIEW_ROUTING")
    return {"schema_version":REPORT_SCHEMA,"case_id":case_id,
        "reviewed_against_desk_sha256":sha(desk),
        "submitted_document_count":len(docs),
        "declared_document_families_count":len({d["source_family"] for d in docs}),
        "redacted_blocker_codes":sorted(set(blockers)),
        "documentation_complete_for_second_human_review":not blockers,
        "independent_facility_existence_verified":False,
        "wall_position_independently_verified":False,
        "public_release_authorized":False,
        "public_layer_update_allowed":False,
        "disclaimer":"This checks forms and source-family declarations, not the authenticity, source independence or truth of evidence. Never publish or claim a verified dam from this report."}


def _private_destination(path,repo):
    dest=path.resolve()
    if dest.is_relative_to(repo.resolve()):
        raise ValueError("Filled records and private evaluations must stay OUTSIDE this public repository")
    if dest.exists():raise ValueError("Refusing existing private output")
    if not dest.parent.is_dir():raise ValueError("Private output parent directory must exist")
    return dest


def _write_private(path,doc):
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,"w",encoding="utf-8") as f:
        json.dump(doc,f,indent=2,ensure_ascii=False,allow_nan=False)
        f.write("\n")


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--desk",required=True,type=Path)
    a.add_argument("--case",required=True,choices=IDS)
    g=a.add_mutually_exclusive_group(required=True)
    g.add_argument("--init",action="store_true")
    g.add_argument("--review-input",type=Path)
    a.add_argument("--out",required=True,type=Path)
    args=a.parse_args()
    repo=Path(__file__).resolve().parents[1]
    destination=_private_destination(args.out,repo)
    desk=json.loads(args.desk.read_text("utf-8"))
    validate_desk(desk)
    if args.init:
        _write_private(destination,blank_record(desk,args.case))
        print("Created offline-only blank review form; no site admission or publication.")
    else:
        src=args.review_input.resolve()
        if src.is_relative_to(repo):raise SystemExit("Filled/private review input cannot be in public repository")
        record=json.loads(src.read_text("utf-8"))
        if record.get("case_id")!=args.case:raise SystemExit("Review case mismatch")
        status=check_record(desk,record)
        _write_private(destination,status)
        print("Offline redacted evidence completeness review:",status["case_id"],
              "blockers=",len(status["redacted_blocker_codes"]),
              "; facility independently verified = NO; approved for publication = NO")

if __name__=="__main__":main()
