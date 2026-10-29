#!/usr/bin/env python3
"""Stage 3D-V: OSM public-context source crosswalk for 19 unverified dam references.

OpenStreetMap is a crowdsourced *review lead*, never an independent engineering
or location receipt. ODbL data are confined to review-only Actions artifacts.
No combined CC BY + ODbL point database is installed in site/data.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata
import urllib.parse
import urllib.request
from pyproj import Geod

OSM_URL="https://overpass-api.de/api/interpreter"
OSM_ATTRIBUTION="© OpenStreetMap contributors"
OSM_LICENSE_URL="https://www.openstreetmap.org/copyright"
SEARCH_M=3000
MAX_ELEMENTS=6000
MAX_RESPONSE_BYTES=3_000_000
GEOD=Geod(ellps="WGS84")
WITHHELD={"WA26-027":"Kafin Zaki","WA26-062":"Mambilla","WA26-095":"Souapiti"}
RECEIPT_FIELDS=("existence_evidence_receipt","existence_observed_on","completed_structure_confirmed",
                "position_validation_method","position_uncertainty_m",
                "source_lineage_independence_receipt","identity_reconciliation_notes",
                "accountable_reviewer","reviewed_on","rights_privacy_permission_receipt",
                "public_release_authorization_receipt")


def normalize(value):
    if not isinstance(value,str):return None
    a=unicodedata.normalize("NFKD",value).encode("ascii","ignore").decode().lower()
    return " ".join(re.findall(r"[a-z0-9]+",a)) or None


def validate_workbench(workbench):
    if (workbench.get("schema_version")!="BN_STAGE3D_U_HIGH_PRIORITY_REVIEW_WORKSHEET_V2"
        or workbench.get("status")!="REVIEW_ONLY_ZERO_CONFIRMED_NOT_PUBLIC_SITE_DATA"
        or workbench.get("source_doi")!="10.60507/FK2/YLDK1Y"
        or workbench.get("source_license")!="CC BY 4.0"
        or workbench.get("source_publisher_csv_md5")!="046b106da1e3a57ec2f1c461fe411b26"
        or workbench.get("source_publisher_shapefile_md5")!="a87f9b4ef2e96625b737ffac8595c138"
        or workbench.get("source_pinned_public_preview_sha256")!="2dc9c81925ea2ed6b2cb82f13410868a96ccc93d1897f3eda6040e924c9dd82a"
        or workbench.get("source_records_total")!=189
        or workbench.get("high_priority_cases")!=19
        or workbench.get("withheld_source_identifications")!=3
        or workbench.get("research_identity_or_proximity_flags")!=16
        or workbench.get("reviewed_and_confirmed")!=0
        or workbench.get("automated_evidence_confirmation_performed") is not False):
        raise ValueError("Stage U source lineage or zero-confirmation contract altered")
    rows=workbench.get("records")
    if not isinstance(rows,list) or len(rows)!=19:raise ValueError("Expected exactly 19 reviewer cases")
    refs=set()
    withheld={}
    for row in rows:
        ref=row.get("source_reference_id")
        if (not isinstance(ref,str) or not re.fullmatch(r"WA26-\d{3}",ref)
            or ref in refs):raise ValueError("Missing or duplicate source reference")
        refs.add(ref)
        point=row.get("compiled_reference_position_WGS84")
        if (not isinstance(point,list) or len(point)!=2 or
            any(type(p) not in (int,float) or not math.isfinite(p) for p in point)
            or not 2<=point[0]<=16 or not 4<=point[1]<=15):
            raise ValueError("Invalid source-only WGS84 coordinates")
        priority=row.get("triage_priority")
        if priority not in {"P0_WITHHELD_IDENTITY","P1_NEARBY_OR_REPEATED_NAME"}:
            raise ValueError("Unapproved review priority")
        if priority=="P0_WITHHELD_IDENTITY":
            withheld[ref]=row.get("source_published_name")
        if (row.get("confirmation_status")!="HOLD_UNVERIFIED"
            or row.get("public_layer_status")!="NO_CHANGE"
            or row.get("point_validation_performed") is not False
            or row.get("eligible_for_public_confirmation") is not False
            or any(row.get(k) is not None for k in RECEIPT_FIELDS)):
            raise ValueError("No source record may contain verified position, evidence receipt or authorization")
        if not isinstance(row.get("source_context_leads_NOT_SITE_RECEIPTS"),list):
            raise ValueError("Missing source-only lead list")
    if withheld!=WITHHELD:raise ValueError("Withheld identity mismatch")
    return rows


def make_query(rows):
    """Single bounded OSM request, never 19 individual heavy requests."""
    fragments=[]
    for item in rows:
        lon,lat=item["compiled_reference_position_WGS84"]
        at=f"(around:{SEARCH_M},{lat:.7f},{lon:.7f})"
        for selector in ('["waterway"="dam"]','["water"="reservoir"]',
                         '["landuse"="reservoir"]'):
            fragments.append("nwr"+selector+at+";")
    return "[out:json][timeout:40];("+ "".join(fragments) +");out center qt;"


def fetch_osm(query, *, timeout=52):
    request=urllib.request.Request(OSM_URL,data=urllib.parse.urlencode({"data":query}).encode(),
      headers={"User-Agent":"BasinNexusNG-SourceReview/1.0 (research-only; GitHub bahagogabriel/basin-nexus-ng)",
               "Accept":"application/json"},method="POST")
    with urllib.request.urlopen(request,timeout=timeout) as response:
        raw=response.read(MAX_RESPONSE_BYTES+1)
    if len(raw)>MAX_RESPONSE_BYTES:raise ValueError("OSM source output exceeded safe response cap")
    return raw


def parse_snapshot(data):
    if not isinstance(data,dict) or not isinstance(data.get("elements"),list):
        raise ValueError("Invalid OSM Overpass JSON; not evidence of absence")
    if len(data["elements"])>MAX_ELEMENTS:
        raise ValueError("OSM comparison too large for reviewer; needs bounded re-query")
    timestamp=data.get("osm3s",{}).get("timestamp_osm_base")
    if not isinstance(timestamp,str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ",timestamp):
        raise ValueError("OSM snapshot time unavailable: no stale claims allowed")
    features={}
    skipped=0
    for item in data["elements"]:
        if not isinstance(item,dict):
            raise ValueError("Invalid OSM feature")
        kind,number=item.get("type"),item.get("id")
        if kind not in ("node","way","relation") or type(number) is not int or number<=0:
            raise ValueError("Bad OSM feature identity")
        tags=item.get("tags",{})
        if not isinstance(tags,dict):raise ValueError("Bad OSM feature tags")
        if tags.get("waterway")=="dam":
            context_type="OSM_TAGGED_DAM_BARRIER"
        elif tags.get("water")=="reservoir" or tags.get("landuse")=="reservoir":
            context_type="OSM_TAGGED_RESERVOIR"
        else:continue
        rep=item if kind=="node" else item.get("center",{})
        if not isinstance(rep,dict):
            skipped+=1;continue
        lat,lon=rep.get("lat"),rep.get("lon")
        if (type(lat) not in (int,float) or type(lon) not in (int,float)
            or not math.isfinite(lat) or not math.isfinite(lon)
            or not -90<=lat<=90 or not -180<=lon<=180):
            skipped+=1;continue
        url=f"https://www.openstreetmap.org/{kind}/{number}"
        label=tags.get("name")
        if not isinstance(label,str) or len(label)>128:label=None
        features[(kind,number)]={"osm_id":f"{kind}/{number}","osm_url":url,
          "osm_name":label,"osm_context_kind":context_type,
          "osm_position_repr":"NODE_COORDINATE" if kind=="node" else "OSM_CENTER_NOT_DAM_WALL",
          "osm_representative_position_WGS84":[lon,lat]}
    return timestamp,list(features.values()),skipped


def compare(workbench, snapshot=None, *, acquisition_status=None, acquisition_error=None):
    rows=validate_workbench(workbench)
    if snapshot is None and acquisition_status!="UNAVAILABLE":
        raise ValueError("Unavailable source must be explicitly declared; never infer zero matches")
    timestamp=None; features=[]; skipped=0
    if snapshot is not None:
        timestamp,features,skipped=parse_snapshot(snapshot)
        status="QUERY_COMPLETED"
        if acquisition_error:raise ValueError("Successful query cannot also claim unavailable")
    else:
        status="QUERY_UNAVAILABLE"
    records=[]
    for r in rows:
        lon,lat=r["compiled_reference_position_WGS84"]
        nearby=[]
        if status=="QUERY_COMPLETED":
            for f in features:
                x,y=f["osm_representative_position_WGS84"]
                _,_,d=GEOD.inv(lon,lat,x,y)
                if d>SEARCH_M:continue
                osmname=f["osm_name"]
                nearby.append({**{k:v for k,v in f.items() if k!="osm_representative_position_WGS84"},
                  "geodesic_distance_to_representative_m":round(d),
                  "same_normalized_source_name_hint":bool(osmname and r["source_published_name"] and
                          normalize(osmname)==normalize(r["source_published_name"])),
                  "source_lineage_independent":None,
                  "evidence_for_completed_structure":False,
                  "position_verified":False})
            nearby.sort(key=lambda z:(z["geodesic_distance_to_representative_m"],
                                       z["osm_id"]))
        # No negative infrastructure claim from absent, incomplete or unavailable OSM map.
        records.append({"reference_id":r["source_reference_id"],
          "source_published_name":r["source_published_name"],"catchment_id":r["catchment_id"],
          "priority":r["triage_priority"],"display_eligibility":
            "WITHHELD" if r["triage_priority"]=="P0_WITHHELD_IDENTITY" else "UNVERIFIED_REFERENCE_ONLY",
          "osm_review_state":("SEARCH_UNAVAILABLE" if status!="QUERY_COMPLETED"
            else "OSM_TAGGED_FEATURES_TO_REVIEW" if nearby else "NO_OSM_TAGGED_FEATURE_OBSERVED_NOT_ABSENCE"),
          "osm_candidate_count_in_radius":len(nearby) if status=="QUERY_COMPLETED" else None,
          "osm_context_candidates":nearby[:6],
          "candidate_list_truncated":len(nearby)>6,
          "independent_existence_verified":False,
          "position_verified":False,
          "review_decision":"HOLD_UNVERIFIED",
          "eligible_for_public_confirmation":False})
    return {"schema_version":"BN_STAGE3D_V_OSM_CONTEXT_REVIEW_V1",
      "status":"RESEARCH_ONLY_NO_AUTOMATIC_DAM_CONFIRMATION",
      "source_doi":workbench["source_doi"],"compiled_source_license":"CC BY 4.0",
      "source_preview_sha256":workbench["source_pinned_public_preview_sha256"],
      "osm_data_credit":OSM_ATTRIBUTION,"osm_license":"ODbL",
      "osm_license_url":OSM_LICENSE_URL,"osm_endpoint":OSM_URL,
      "osm_timestamp":timestamp,
      "osm_query_state":status,
      "osm_acquisition_error_category":acquisition_error if status=="QUERY_UNAVAILABLE" else None,
      "osm_search_radius_m":SEARCH_M,
      "osm_features_in_snapshot":len(features) if status=="QUERY_COMPLETED" else None,
      "osm_features_skipped_missing_center":skipped if status=="QUERY_COMPLETED" else None,
      "reporting_notes":"OSM crowd mapping is not a dam inspection, surveyed dam-wall position, verified commissioning, independent source-lineage receipt, or proof of absence. Reservoir polygon centers are not dam-wall coordinates. OSM features may copy other sources. Match distances are not positional uncertainty. No live site records created.",
      "queried_source_reference_count":19,
      "confirmed_facility_count":0,
      "automated_facility_admissions":0,
      "original_compiled_references_changed":False,
      "public_map_updated":False,
      "records":records}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--workbench",type=Path,required=True)
    parser.add_argument("--report",type=Path,required=True)
    parser.add_argument("--snapshot",type=Path)
    parser.add_argument("--fetch-osm",action="store_true")
    args=parser.parse_args()
    if args.fetch_osm==bool(args.snapshot):raise SystemExit("Use exactly one of --fetch-osm or --snapshot")
    if args.report.exists():raise SystemExit("Refusing to overwrite existing review report")
    data=json.loads(args.workbench.read_text("utf-8"))
    rows=validate_workbench(data)
    if args.snapshot:
        raw=args.snapshot.read_bytes()
        if len(raw)>MAX_RESPONSE_BYTES:raise SystemExit("OSM snapshot exceeds cap")
        result=compare(data,json.loads(raw.decode("utf-8")))
    else:
        try:
            raw=fetch_osm(make_query(rows))
            result=compare(data,json.loads(raw.decode("utf-8")))
        except (TimeoutError, OSError, ValueError, UnicodeError, json.JSONDecodeError) as error:
            result=compare(data,acquisition_status="UNAVAILABLE",acquisition_error=type(error).__name__)
            # Failure is NOT silently converted into 'none found'.
            print("OSM comparison source unavailable:",type(error).__name__)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    with args.report.open("x",encoding="utf-8") as out:
        json.dump(result,out,ensure_ascii=False,indent=2)
        out.write("\n")
    print("STAGE3D-V",result["osm_query_state"],"cases=19",
          "mapped-context-cases",sum(x["osm_candidate_count_in_radius"]!=0
              for x in result["records"] if x["osm_candidate_count_in_radius"] is not None),
          "confirmed=0; release=HOLD")


if __name__=="__main__":main()
