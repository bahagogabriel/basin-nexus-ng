#!/usr/bin/env python3
"""Basin Nexus NG prospective public evidence gate (no source/private records).

Usage: python tools/evidence_publication_gate.py public_records.json
This checks *policy eligibility* only; never substitutes for genuine approval.
No candidate file, personal record or private document belongs in the public repo.
"""
from __future__ import annotations
import json
import math
import re
import sys
from pathlib import Path

SCHEMA_VERSION="BN_PUBLIC_EVIDENCE_V1"
ALLOWED_THEMES={"water_infrastructure","natural_resources","ecosystems","threats_challenges","socioeconomics","policies","interventions"}
ALLOWED_EVIDENCE={"stakeholder_reported","cross_checked","independently_verified"}
ALLOWED_TYPES={"resource_report","facility_report","risk_report","policy_report","intervention_report"}
ALLOWED_FIELDS={"record_id","catchment_ids","theme","record_type","statement","evidence_status","source_reference",
                "source_locator","release_authorization","location","public_source_url","notes"}
BLOCKED_FIELDS={"contact","phone","email","signature","participant","attendance","source_file_id",
                "private_drive_id","private_note","raw_document","raw_text","person_name","source_quote_raw"}

def _fail(message):
    raise ValueError(message)

def _read_ids():
    root=Path(__file__).resolve().parents[1]
    d=json.loads((root/"site/data/registry.json").read_text(encoding="utf-8"))
    return {x["id"] for x in d}

def validate(doc:dict, allowed_catchments:set[str]|None=None)->dict:
    if not isinstance(doc,dict) or doc.get("type")!="PublicEvidenceCollection":
        _fail("Expected PublicEvidenceCollection")
    if doc.get("publication_status")!="APPROVED_PUBLIC_ONLY":
        _fail("Only approved public records are allowed")
    # Accept legacy synthetic test objects, but require versioning for all published site assets.
    if set(doc)-{"type","publication_status","records","schema_version"}:
        _fail("Collection contains unknown top-level fields")
    if "schema_version" in doc and doc["schema_version"]!=SCHEMA_VERSION:
        _fail("Unsupported public evidence schema")
    records=doc.get("records")
    if not isinstance(records,list) or len(records)>500:
        _fail("Expected bounded records list")
    allowed_catchments=allowed_catchments or _read_ids()
    seen=set()
    for idx,rec in enumerate(records):
        if not isinstance(rec,dict):
            _fail(f"record {idx}: expected object")
        extra=set(rec)-ALLOWED_FIELDS
        if extra or any(k.lower() in BLOCKED_FIELDS for k in rec):
            _fail(f"record {idx}: disallowed/private fields {sorted(extra)}")
        uid=rec.get("record_id")
        if not isinstance(uid,str) or not re.fullmatch(r"BN-[A-Z0-9-]{5,50}",uid) or uid in seen:
            _fail(f"record {idx}: invalid or duplicate public ID")
        seen.add(uid)
        ids=rec.get("catchment_ids")
        if not isinstance(ids,list) or not ids or set(ids)-allowed_catchments:
            _fail(f"record {idx}: unknown or missing catchment relationship")
        if any(not isinstance(x,str) for x in ids):
            _fail(f"record {idx}: invalid catchment relationship type")
        if len(ids)!=len(set(ids)):
            _fail(f"record {idx}: repeated catchment ID")
        if rec.get("theme") not in ALLOWED_THEMES or rec.get("record_type") not in ALLOWED_TYPES:
            _fail(f"record {idx}: invalid record classification")
        if rec.get("evidence_status") not in ALLOWED_EVIDENCE:
            _fail(f"record {idx}: evidence status missing or invalid")
        if not isinstance(rec.get("release_authorization"),str) or not re.fullmatch(r"PUBLIC-[A-Z0-9-]{5,60}",rec["release_authorization"]):
            _fail(f"record {idx}: explicit source/publication authorization missing")
        for key in ("statement","source_reference","source_locator"):
            v=rec.get(key)
            if not isinstance(v,str) or len(v.strip())<5 or len(v)>2400:
                _fail(f"record {idx}: invalid {key}")
            if "drive.google.com" in v.lower() or "docs.google.com" in v.lower():
                _fail(f"record {idx}: private source reference")
            if re.search(r"[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}",v,re.I):
                _fail(f"record {idx}: email address in published evidence")
            if re.search(r"(?i)(?:\\bprivate_drive_id\\b|\\bsource_internal_id\\b|\\brelease_authorization\\b|\\braw_statement_internal\\b)",v):
                _fail(f"record {idx}: internal review marker in public text")
        url=rec.get("public_source_url")
        if url is not None:
            if not isinstance(url,str) or not url.startswith("https://") or any(host in url.lower() for host in ("drive.google.com","docs.google.com","localhost","127.0.0.1")):
                _fail(f"record {idx}: public source URL requires a reviewed public HTTPS endpoint")
        position=rec.get("location")
        if position is not None:
            if not isinstance(position,dict):
                _fail(f"record {idx}: location must be an object")
            if set(position)!={"latitude","longitude","verification","method","uncertainty_m"}:
                _fail(f"record {idx}: location lacks required verification metadata")
            if position["verification"]!="independently_validated":
                _fail(f"record {idx}: unvalidated coordinates cannot be published")
            if not isinstance(position["method"],str) or len(position["method"])<8:
                _fail(f"record {idx}: location method missing")
            for field,minval,maxval in [("latitude",-90,90),("longitude",-180,180),("uncertainty_m",0,1e7)]:
                v=position[field]
                if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not minval<=v<=maxval:
                    _fail(f"record {idx}: invalid {field}")
        notes=rec.get("notes")
        if notes is not None and (not isinstance(notes,str) or len(notes)>1200
                or "drive.google.com" in notes.lower() or "docs.google.com" in notes.lower()
                or re.search(r"[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}",notes,re.I)):
            _fail(f"record {idx}: invalid or private notes")
    return {"validated_public_records":len(records),"mapped_locations":sum(x.get("location") is not None for x in records)}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("Usage: evidence_publication_gate.py <approved_public_collection.json>")
    data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    result=validate(data)
    print("BASIN NEXUS PUBLIC EVIDENCE GATE: PASS",result)
if __name__=="__main__":
    main()
