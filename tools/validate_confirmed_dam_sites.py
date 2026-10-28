#!/usr/bin/env python3
"""Confirmed dam gate: names optional; independent existence and position evidence NOT optional.

This checks documented human review receipts, not the truth of independent research.
Site release requires a dedicated human-approved change of this release gate. The
public site's confirmed record collection remains zero by default.
"""
from __future__ import annotations
from datetime import date
from urllib.parse import urlparse
import json,re,math
from pathlib import Path

METHODS={"surveyed_gnss_with_documented_accuracy",
         "authoritative_agency_location_verified",
         "independently_reviewed_multi_date_earth_observation"}
EXISTENCE={"engineering_agency_as_built_or_inspection",
           "independent_field_observation",
           "independently_reviewed_earth_observation_dam_wall"}
CHECK_STATUS="PHYSICAL_DAM_EXISTENCE_INDEPENDENTLY_REVIEWED"
def public_url(url):
    if not isinstance(url,str) or len(url)>1500:return False
    u=urlparse(url)
    return (u.scheme=="https" and bool(u.hostname) and
            u.username is None and u.password is None and
            not any(s in u.hostname.lower() for s in
                    ("docs.google.com","drive.google.com","localhost","127.0.0.1")))
def valid_date(s):
    try:
        d=date.fromisoformat(s)
        return len(s)==10 and d<=date.today()
    except (ValueError,TypeError):
        return False

def validate_record(r):
    expected={"record_id","catchment_id","name","name_status","existence_status",
             "existence_evidence_kind","existence_evidence_url","existence_observed_on",
             "position","position_method","position_evidence_url","position_observed_on",
             "position_uncertainty_m","source_independence_review","editorial_reviewer",
             "editorial_reviewed_on","rights_status","publication_authorization"}
    if not isinstance(r,dict) or set(r)!=expected:raise ValueError("Unknown or missing facility field")
    if not isinstance(r["record_id"],str) or not re.fullmatch(r"BN-DAM-[A-Z0-9-]{5,50}",r["record_id"]):
        raise ValueError("Invalid confirmed site identity")
    if not isinstance(r["catchment_id"],str) or not re.fullmatch(r"SCMP-C(?:0[1-9]|1\d|20)",r["catchment_id"]):
        raise ValueError("Unrecognized catchment")
    named=r["name_status"]=="established_name"
    unnamed=r["name_status"]=="name_unavailable_after_review"
    if not (named or unnamed):
        raise ValueError("Every name requires affirmative review status")
    if named and (not isinstance(r["name"],str) or not 2<=len(r["name"])<=96 or re.search(r"[<>@]",r["name"])):
        raise ValueError("No credible supported dam name")
    if unnamed and r["name"] is not None:
        raise ValueError("Unknown name must be null, not a guessed string")
    if r["existence_status"]!=CHECK_STATUS or r["existence_evidence_kind"] not in EXISTENCE:
        raise ValueError("Unsubstantiated dam wall")
    if r["position_method"] not in METHODS:
        raise ValueError("Position insufficiently reviewed")
    for field in ("existence_evidence_url","position_evidence_url"):
        if not public_url(r[field]):raise ValueError("Source evidence must be publicly resolvable")
    for field in ("existence_observed_on","position_observed_on","editorial_reviewed_on"):
        if not valid_date(r[field]):raise ValueError("Dates must not be future or invalid")
    p=r["position"]
    if not isinstance(p,dict) or set(p)!={"lon","lat"}:
        raise ValueError("No geometrically validated position")
    lon=p["lon"];lat=p["lat"]
    if (not isinstance(lon,(int,float)) or not isinstance(lat,(int,float)) or
        not math.isfinite(lon) or not math.isfinite(lat) or not -180<=lon<=180 or not -90<=lat<=90):
        raise ValueError("Invalid lon/lat")
    if (not isinstance(r["position_uncertainty_m"],(int,float))
        or not math.isfinite(r["position_uncertainty_m"])
        or r["position_uncertainty_m"]<1 or r["position_uncertainty_m"]>5000):
        raise ValueError("Explicit bounded location uncertainty required")
    if r["source_independence_review"]!="SEPARATE_LINEAGES_CONFIRMED":
        raise ValueError("No independent source lineage review")
    if not isinstance(r["editorial_reviewer"],str) or len(r["editorial_reviewer"].strip())<3:
        raise ValueError("Named accountable reviewer required")
    if r["rights_status"]!="EXPLICIT_PUBLIC_REUSE_CLEARED":
        raise ValueError("Source redistribution rights not cleared")
    if not isinstance(r["publication_authorization"],str) or not re.fullmatch(r"BN-PUBLIC-[A-Z0-9-]{6,50}",r["publication_authorization"]):
        raise ValueError("Specific reviewed approval receipt required")
    return True

def validate_collection(collection):
    if not isinstance(collection,dict) or set(collection)!={"schema_version","status","records","count","reviewed_on","note"}:
        raise ValueError("Collection schema mismatch")
    if collection["schema_version"]!="BN_CONFIRMED_DAM_SITES_V1":
        raise ValueError("Unknown contract")
    if collection["status"]!="INDEPENDENT_REVIEW_REQUIRED_ZERO_RECORDS" or collection["records"]!=[] or collection["count"]!=0:
        raise ValueError("Stage R locks zero public confirmed records until separate reviewed release PR")
    if not valid_date(collection["reviewed_on"]):raise ValueError("Missing review date")
    return True

if __name__=="__main__":
    root=Path(__file__).resolve().parents[1]
    collection=json.loads((root/"site/data/confirmed_dam_sites.json").read_text("utf-8"))
    validate_collection(collection)
    print("CONFIRMED DAM RELEASE GATE: 0 named or unnamed confirmed facility points, no auto promotion: PASS")
