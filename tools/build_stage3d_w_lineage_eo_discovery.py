#!/usr/bin/env python3
"""Stage 3D-W: OSM tag-lineage and Sentinel-2 metadata leads, NEVER dam confirmation.

The only inputs are already reviewed, public-source research artifacts from the
existing Stage 3D-U and V GitHub Actions pipeline. The report goes to review/,
never the public Pages site. No imagery is classified or inspected by this tool.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import math
from pathlib import Path
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

OSM_API = "https://api.openstreetmap.org/api/0.6"
STAC_API = "https://earth-search.aws.element84.com/v1/search"
STAC_COLLECTION = "sentinel-2-c1-l2a"
REFERENCES = {"WA26-003": "way/272558892", "WA26-083": "way/272558893",
              "WA26-184": "way/571289117", "WA26-185": "way/571289118",
              "WA26-186": "way/571289120"}
EPOCHS = {"historical_2019": "2019-01-01T00:00:00Z/2019-12-31T23:59:59Z",
          "recent_2026": "2026-01-01T00:00:00Z/2026-10-29T23:59:59Z"}
EXPECTED_SHA = "2dc9c81925ea2ed6b2cb82f13410868a96ccc93d1897f3eda6040e924c9dd82a"
MAX_OSM_BYTES = 750_000
MAX_STAC_BYTES = 1_500_000
MAX_STAC_ITEMS = 40
MAX_HISTORY_VERSIONS = 250
MAX_CANDIDATES_PER_EPOCH = 3


def _stamp(t):
    if not isinstance(t, str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z", t):
        raise ValueError("Timestamp must be explicit UTC ISO")
    return dt.datetime.fromisoformat(t.replace("Z","+00:00"))


def validate_inputs(workbench, osm):
    if (workbench.get("schema_version") != "BN_STAGE3D_U_HIGH_PRIORITY_REVIEW_WORKSHEET_V2"
        or workbench.get("status") != "REVIEW_ONLY_ZERO_CONFIRMED_NOT_PUBLIC_SITE_DATA"
        or workbench.get("source_doi") != "10.60507/FK2/YLDK1Y"
        or workbench.get("source_publisher_csv_md5") != "046b106da1e3a57ec2f1c461fe411b26"
        or workbench.get("source_publisher_shapefile_md5") != "a87f9b4ef2e96625b737ffac8595c138"
        or workbench.get("source_pinned_public_preview_sha256") != EXPECTED_SHA
        or workbench.get("reviewed_and_confirmed") != 0
        or workbench.get("high_priority_cases") != 19
        or workbench.get("source_records_total") != 189
        or workbench.get("withheld_source_identifications") != 3):
        raise ValueError("Stage U original source integrity or zero-confirmed baseline drift")
    if (osm.get("schema_version") != "BN_STAGE3D_V_OSM_CONTEXT_REVIEW_V1"
        or osm.get("status") != "RESEARCH_ONLY_NO_AUTOMATIC_DAM_CONFIRMATION"
        or osm.get("source_preview_sha256") != EXPECTED_SHA
        or osm.get("osm_license") != "ODbL"
        or osm.get("confirmed_facility_count") != 0
        or osm.get("automated_facility_admissions") != 0
        or osm.get("public_map_updated") is not False
        or osm.get("queried_source_reference_count") != 19):
        raise ValueError("Stage V source crosswalk/OSM attribution or release status drift")
    a = workbench.get("records"); b = osm.get("records")
    if not isinstance(a,list) or not isinstance(b,list) or len(a)!=19 or len(b)!=19:
        raise ValueError("Stage U-V 19 source-case contracts changed")
    originals = {}
    for r in a:
        ref = r["source_reference_id"]
        pt = r["compiled_reference_position_WGS84"]
        if ref in originals or not re.fullmatch(r"WA26-\d{3}",str(ref)):
            raise ValueError("Duplicate or invalid original source reference")
        if not (isinstance(pt,list) and len(pt)==2
                and all(type(q) in (int,float) and math.isfinite(q) for q in pt)
                and 2<=pt[0]<=16 and 4<=pt[1]<=15):
            raise ValueError("Incorrect original source WGS84 point")
        if (r.get("confirmation_status")!="HOLD_UNVERIFIED"
            or r.get("eligible_for_public_confirmation") is not False
            or r.get("public_layer_status")!="NO_CHANGE"
            or r.get("point_validation_performed") is not False):
            raise ValueError("A Stage U original point has been promoted")
        originals[ref]=r
    seen=set(); index={}
    for r in b:
        ref=r["reference_id"]
        if ref in seen or ref not in originals:raise ValueError("Duplicate/unmatched Stage V reference")
        seen.add(ref)
        if (r.get("independent_existence_verified") is not False
            or r.get("position_verified") is not False
            or r.get("eligible_for_public_confirmation") is not False
            or r.get("review_decision")!="HOLD_UNVERIFIED"
            or r["priority"]!=originals[ref]["triage_priority"]
            or r["source_published_name"]!=originals[ref]["source_published_name"]):
            raise ValueError("Stage V review decision or source identity drift")
        if not isinstance(r.get("osm_context_candidates"),list):raise ValueError("Dam reference candidates missing")
        index[ref]=r
    if seen!=set(originals) or not set(REFERENCES)<=seen:
        raise ValueError("Original U-V case alignment failed")
    state=osm.get("osm_query_state")
    if state not in ("QUERY_COMPLETED","QUERY_UNAVAILABLE"):raise ValueError("Unknown OSM fetch state")
    if state=="QUERY_COMPLETED":_stamp(osm.get("osm_timestamp"))
    for ref,way in REFERENCES.items():
        row=index[ref]
        matches=[c for c in row["osm_context_candidates"]
                 if c.get("osm_context_kind")=="OSM_TAGGED_DAM_BARRIER" and c.get("osm_id")==way]
        if len(matches)>1:raise ValueError("Duplicated nearest OSM identity")
        if matches:
            c=matches[0]
            if (c.get("osm_url") != "https://www.openstreetmap.org/"+way
                or c.get("evidence_for_completed_structure") is not False
                or c.get("position_verified") is not False
                or c.get("source_lineage_independent") is not None
                or not isinstance(c.get("geodesic_distance_to_representative_m"),(float,int))
                or c["geodesic_distance_to_representative_m"]<0):
                raise ValueError("OSM barrier source or nonverification fields changed")
        if state=="QUERY_COMPLETED" and not matches:
            raise ValueError("The prior five OSM object matches changed; require new identity review")
    return originals,index


def _fetch(url, *, body=None, limit=MAX_STAC_BYTES, timeout=13):
    req=urllib.request.Request(url,data=body,
        headers={"Accept":"application/json" if body is not None else "application/xml",
                 "Content-Type":"application/json" if body is not None else "application/xml",
                 "User-Agent":"BasinNexusNG-IndependentResearchReview/1.0 (https://github.com/bahagogabriel/basin-nexus-ng)"},
        method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req,timeout=timeout) as resp:raw=resp.read(limit+1)
    if len(raw)>limit:raise ValueError("External metadata response exceeded cap")
    return raw


def parse_osm_history(xml, osm_id):
    if not re.fullmatch(r"way/[1-9]\d{0,16}",osm_id):raise ValueError("Unexpected OSM object identifier")
    if len(xml)>MAX_OSM_BYTES:raise ValueError("OSM history exceeds safety cap")
    root=ET.fromstring(xml)
    if root.tag!="osm":raise ValueError("OSM history root mismatch")
    ways=root.findall("way")
    if not ways or len(ways)>MAX_HISTORY_VERSIONS:raise ValueError("Missing/unbounded OSM history")
    versions=[]; observed=set()
    expected=int(osm_id.split("/")[1])
    for w in ways:
        if w.get("id")!=str(expected):raise ValueError("OSM history contains unrelated way")
        ver=int(w.attrib["version"]);ts=w.attrib["timestamp"]
        _stamp(ts)
        if ver<1 or ver in observed:raise ValueError("Invalid/duplicate OSM version")
        observed.add(ver)
        if w.get("visible","true")!="true":continue
        tags={t.get("k"):t.get("v") for t in w.findall("tag")}
        source_keys=sorted(k for k in tags if k and (k=="source" or k.startswith("source:")))
        # Do NOT expose editor/user IDs, free-text source values, or personal details.
        origin_hint=any("kouassi" in (tags[k] or "").lower() or
                        "bonndata" in (tags[k] or "").lower() for k in source_keys)
        versions.append((ver,ts,source_keys,origin_hint,tags.get("waterway")=="dam"))
    if not versions:raise ValueError("No visible OSM history states")
    versions.sort()
    last=versions[-1]
    return {"history_status":"AVAILABLE_TAG_HISTORY_ONLY","osm_way":osm_id,
            "first_mapped_timestamp":versions[0][1],
            "latest_edit_timestamp":last[1],
            "available_visible_versions":len(versions),
            "source_keys_seen":sorted({k for v in versions for k in v[2]}),
            "possible_compiled_dataset_source_tag":any(v[3] for v in versions),
            "latest_version_dam_tag":last[4],
            "no_declared_source_does_not_prove_independence":True,
            "independent_lineage_verified":False,
            "osm_editor_personal_data_exported":False}


def parse_stac(payload, case_point, start_end):
    if not isinstance(payload,dict) or payload.get("type")!="FeatureCollection":
        raise ValueError("STAC response missing FeatureCollection")
    items=payload.get("features")
    if not isinstance(items,list) or len(items)>MAX_STAC_ITEMS:raise ValueError("Bad bounded STAC result")
    lon,lat=case_point
    allowed=[]
    time_start,time_end=map(_stamp,start_end.split("/"))
    for f in items:
        if not isinstance(f,dict) or f.get("type")!="Feature" or f.get("collection")!=STAC_COLLECTION:
            raise ValueError("Unexpected STAC item/collection")
        item_id=f.get("id")
        if not isinstance(item_id,str) or not 3<=len(item_id)<=180:
            raise ValueError("Invalid STAC item ID")
        p=f.get("properties",{})
        t=p.get("datetime")
        stamp=_stamp(t)
        if not time_start<=stamp<=time_end:continue
        cloud=p.get("eo:cloud_cover")
        if type(cloud) not in (int,float) or not math.isfinite(cloud) or not 0<=cloud<=100:
            continue
        # STAC intersects point was requested; this remains unverified metadata, not pixel QA.
        href=next((l.get("href") for l in f.get("links",[]) if
                   isinstance(l,dict) and l.get("rel")=="self"),None)
        if not isinstance(href,str) or not href.startswith("https://earth-search.aws.element84.com/"):
            continue
        allowed.append({"item_id":item_id,"acquired_utc":t,
          "scene_cloud_pct":round(float(cloud),2),
          "stac_item":href,
          "collection":STAC_COLLECTION,
          "scene_cloud_not_point_cloud":True,
          "image_pixels_downloaded":False,"structure_visually_confirmed":False})
    # Catalog duplicates or different processing item versions cannot count as validation.
    unique={r["item_id"]:r for r in allowed}
    best=sorted(unique.values(),key=lambda x:(x["scene_cloud_pct"],x["acquired_utc"],x["item_id"]))
    return {"catalog_state":"SCENE_METADATA_FOUND" if best else "NO_USABLE_CATALOG_ITEMS_NOT_NO_IMAGERY",
            "searched_item_count":len(items),
            "eligible_item_count":len(best),
            "shortlist":best[:MAX_CANDIDATES_PER_EPOCH]}


def make_search(point, period):
    if not isinstance(point,list) or len(point)!=2 or period not in EPOCHS:
        raise ValueError("Invalid search case")
    return json.dumps({"collections":[STAC_COLLECTION],
      "intersects":{"type":"Point","coordinates":point},
      "datetime":EPOCHS[period],"limit":MAX_STAC_ITEMS},
      separators=(",",":")).encode("utf-8")


def assemble(workbench, osm, *, fetch_history=None, fetch_scene=None):
    originals,lookup=validate_inputs(workbench,osm)
    if fetch_history is None:fetch_history=_fetch
    if fetch_scene is None:fetch_scene=_fetch
    all_cases=[]
    for ref,osm_id in REFERENCES.items():
        orig=originals[ref];v=lookup[ref]
        pt=orig["compiled_reference_position_WGS84"]
        near=next((c for c in v["osm_context_candidates"] if c.get("osm_id")==osm_id
                   and c.get("osm_context_kind")=="OSM_TAGGED_DAM_BARRIER"),None)
        if near is None:
            history={"history_status":"UPSTREAM_CONTEXT_NOT_AVAILABLE","independent_lineage_verified":False}
        else:
            try:
                data=fetch_history(OSM_API+"/"+osm_id+"/history",limit=MAX_OSM_BYTES,timeout=13)
                history=parse_osm_history(data,osm_id)
            except (OSError,TimeoutError,ValueError,ET.ParseError,KeyError,OverflowError):
                history={"history_status":"LOOKUP_UNAVAILABLE_NOT_INDEPENDENT",
                         "independent_lineage_verified":False}
        scene_windows={}
        for epoch in EPOCHS:
            try:
                raw=fetch_scene(STAC_API,body=make_search(pt,epoch),
                                limit=MAX_STAC_BYTES,timeout=13)
                catalog=parse_stac(json.loads(raw.decode("utf-8")),pt,EPOCHS[epoch])
            except (OSError,TimeoutError,ValueError,UnicodeError,KeyError,json.JSONDecodeError):
                catalog={"catalog_state":"CATALOG_UNAVAILABLE_NOT_NO_IMAGERY",
                         "searched_item_count":None,"eligible_item_count":None,"shortlist":[]}
            scene_windows[epoch]=catalog
        all_cases.append({"source_reference_id":ref,"source_published_name":orig["source_published_name"],
           "source_position_WGS84_UNVERIFIED":pt,
           "nearest_osm_barrier_way_research_only":osm_id,
           "stage_v_osm_center_distance_m_NOT_ACCURACY":near["geodesic_distance_to_representative_m"] if near else None,
           "osm_lineage_context":history,"sentinel2_scene_metadata":scene_windows,
           "dam_wall_independently_located":False,
           "constructed_dam_independently_verified":False,
           "historical_earth_observation_interpreted":False,
           "field_survey_performed":False,
           "source_lineage_independent":False,
           "confirmation_decision":"HOLD_REVIEW_ONLY",
           "public_release_authorized":False})
    return {"schema_version":"BN_STAGE3D_W_LINEAGE_EO_DISCOVERY_V1",
      "status":"RESEARCH_ONLY_NO_FACILITY_ADMISSIONS",
      "source_doi":workbench["source_doi"],"source_license":"CC BY 4.0",
      "source_preview_sha256":EXPECTED_SHA,
      "osm_attribution":osm["osm_data_credit"],"osm_license":"ODbL",
      "osm_snapshot_timestamp":osm.get("osm_timestamp"),
      "osm_history_api":OSM_API,
      "eo_catalog":STAC_API,"eo_collection":STAC_COLLECTION,
      "eo_data_notice":"Copernicus Sentinel data legal notice; consult original publisher conditions",
      "scenes_are_metadata_not_checked_pixel_evidence":True,
      "returned_scene_cloud_is_tile_level_not_at_reference_point":True,
      "reviewed_site_count":5,"independently_confirmed_dams":0,
      "human_release_receipts_generated":0,"public_map_changes":False,
      "no_unmatched_osm_inference":True,"records":all_cases}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage-u",type=Path,required=True)
    p.add_argument("--stage-v",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise SystemExit("Refusing review output overwrite")
    x=json.loads(args.stage_u.read_text("utf-8"));y=json.loads(args.stage_v.read_text("utf-8"))
    obj=assemble(x,y)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as fd:
        json.dump(obj,fd,ensure_ascii=False,indent=2);fd.write("\n")
    print("STAGE 3D-W: 5 OSM lineage leads, Sentinel-2 metadata only, ZERO independently confirmed dams")
    for row in obj["records"]:
        print(row["source_reference_id"],row["osm_lineage_context"]["history_status"],
              {k:v["catalog_state"] for k,v in row["sentinel2_scene_metadata"].items()})

if __name__=="__main__":main()
