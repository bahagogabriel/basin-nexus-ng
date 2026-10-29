#!/usr/bin/env python3
"""Stages 3D-AA–AD: source-only OSM-way geometry, documentary crosswalk, temporal SCL QA
and human release-receipt template. NEVER confirms a physical dam.

Consumes previous independently generated source review artifacts. Outputs remain
under review/ and GitHub Actions; no path to site/data or publication.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import json
import math
import re
import urllib.request
import xml.etree.ElementTree as ET
from pyproj import CRS, Geod, Transformer
from shapely.geometry import LineString, Point
from shapely.ops import transform as shape_transform
from build_stage3d_w_lineage_eo_discovery import REFERENCES, EXPECTED_SHA, validate_inputs
from build_stage3d_xy_sentinel_pixel_review import validate_source as validate_pixel_source

OSM_API="https://api.openstreetmap.org/api/0.6"
REVIEW_IDS=tuple(REFERENCES)
GEOD=Geod(ellps="WGS84")
MAX_XML_BYTES=650_000
MAX_NODES=750
# Public documentary CONTEXT from original national/federal documents.
# IMPORTANT: first document's online publication date not independently verified;
# second table explicitly identifies an abstraction POINT, not a surveyed wall.
GUSAU_DOCUMENT_LEADS=(
  {"lead_id":"GOV-NG-GUSAU-BARRAGE-INV","title":"Gusau Barrage — National Dam Inventory",
   "publisher":"Federal Ministry of Water Resources (dams.ng)",
   "document_url":"https://dams.ng/permanent_assets/dams.pdf",
   "record_label":"Gusau Barrage",
   "record_statement":"Earthfill barrage; inventory lists status Completed, completion 1991",
   "reported_coordinate_kind":"DAM_INVENTORY_REPORTED_COORDINATE_NOT_SURVEYED_BY_THIS_PROJECT",
   "reported_coordinate_WGS84":[6.66952,12.14638],
   "document_published_date":"NOT_INDEPENDENTLY_CONFIRMED",
   "document_page_reference":"Inventory listing Gusau Barrage, visible pagination p.24",
   "independent_source_lineage_assessed":False},
  {"lead_id":"GOV-NG-GUSAU-WATER-INTAKE-2020","title":"Development of Sustainable Water Footprint in Nigeria — Final Report",
   "publisher":"Nigeria Integrated Water Resources Management Commission / JIL Engineering Associates",
   "document_url":"https://niwrmc.gov.ng/wp-content/uploads/2026/01/Final-Water-Footprint-Report-for-IWRM.pdf",
   "record_label":"Gusau Dam",
   "record_statement":"Gusau Dam surface-water abstraction entry (NOT an identified dam-wall survey)",
   "reported_coordinate_kind":"WATER_ABSTRACTION_INTAKE_POINT_NOT_DAM_WALL",
   "reported_coordinate_WGS84":[6+40/60+21.1/3600,12+8/60+48.5/3600],
   "document_published_date":"2020-08",
   "document_page_reference":"Abstraction points, surface water, PDF page 33 (0-based 32)",
   "independent_source_lineage_assessed":False}
)
HUMAN_RECEIPTS=("structure_exists_independent_evidence_url","facility_status_evidence_date",
   "reviewed_dam_wall_position_WGS84","wall_position_method","wall_position_uncertainty_m",
   "independent_source_lineage_assessment","image_interpretation_notes_with_dates",
   "independent_engineering_or_field_source","reviewer_identity_and_organization",
   "human_review_date","rights_privacy_release_receipt","specific_publication_approval")


def _finite_point(point):
    return (isinstance(point,list) and len(point)==2 and
            all(type(x) in (int,float) and math.isfinite(x) for x in point)
            and -180<=point[0]<=180 and -90<=point[1]<=90)


def validate_all(stage_u,stage_v,stage_w,stage_z):
    orig,v=validate_inputs(stage_u,stage_v)
    zp=validate_pixel_source(stage_w)
    if (stage_z.get("schema_version")!="BN_STAGE3D_XY_SENTINEL_RGB_SCL_REVIEW_V1"
        or stage_z.get("status")!="PIXEL_SAMPLE_REVIEW_ONLY_NOT_A_DAM_SURVEY"
        or stage_z.get("source_preview_sha256")!=EXPECTED_SHA
        or stage_z.get("source_doi")!="10.60507/FK2/YLDK1Y"
        or stage_z.get("source_license")!="CC BY 4.0"
        or stage_z.get("osm_license")!="ODbL"
        or stage_z.get("sentinel_collection")!="sentinel-2-c1-l2a"
        or stage_z.get("SCL_not_independent_engineering_evidence") is not True
        or stage_z.get("historical_comparison_not_construction_or_operational_proof") is not True
        or stage_z.get("none_of_the_pixel_metrics_estimate_dam_position_accuracy") is not True
        or stage_z.get("independently_confirmed_dams")!=0
        or stage_z.get("public_map_changes") is not False
        or stage_z.get("source_names_not_verified") is not True
        or stage_z.get("RGB_SCL_samples_attempted")!=10):
        raise ValueError("Stage Z image lineage or no-confirmation release gate drift")
    rows=stage_z.get("records")
    if not isinstance(rows,list) or len(rows)!=5:
        raise ValueError("Stage Z requires exactly five research-only cases")
    maps={}
    for r in rows:
        ref=r.get("reference_id")
        if ref not in REFERENCES or ref in maps:
            raise ValueError("Unknown/duplicate pixel QA research reference")
        if (r.get("actual_dam_wall_position_verified") is not False
            or r.get("independent_structure_confirmation") is not False
            or r.get("human_interpretation_receipt") is not None
            or r.get("public_release_authorized") is not False
            or r.get("pixel_coverage_not_construction_date") is not True
            or r.get("original_reference_WGS84_UNVERIFIED")!=orig[ref]["compiled_reference_position_WGS84"]):
            raise ValueError("Source ID/point or verification status changed")
        epochs=r.get("epochs")
        if not isinstance(epochs,dict) or set(epochs)!={"historical_2019","recent_2026"}:
            raise ValueError("Two fixed optical periods are required")
        for entry in epochs.values():
            if (entry.get("structure_visually_verified") is not False
                or entry.get("site_coordinate_verified") is not False
                or entry.get("image_interpretation_performed") is not False):
                raise ValueError("No image observation may auto-confirm a structure")
            if entry.get("pixel_state") not in (
                "PIXELS_UNAVAILABLE_NOT_NO_IMAGERY",
                "RGB_SCL_PIXELS_SAMPLED_REVIEW_ONLY"):
                raise ValueError("Unrecognized pixel state")
            if entry.get("pixel_state")=="RGB_SCL_PIXELS_SAMPLED_REVIEW_ONLY":
                q=entry.get("pixel_qa")
                if not isinstance(q,dict) or q.get("pixels_total")!=9216:
                    raise ValueError("Pixel QA grid drift")
                for key in ("center_scl_water_fraction_of_clear",
                            "center_clear_fraction_of_valid","valid_coverage_fraction"):
                    value=q.get(key)
                    if value is not None and (type(value) not in (int,float) or not 0<=value<=1):
                        raise ValueError("Invalid SCL fraction")
                if q.get("scl_water_is_not_evidence_of_a_dam") is not True:
                    raise ValueError("Cloud QA became a structure confirmation")
        maps[ref]=r
    if set(maps)!=set(REFERENCES):raise ValueError("All five source references required")
    return orig,maps


def fetch_osm_way(osm_way):
    if osm_way not in REFERENCES.values():raise ValueError("OSM way not within pinned five")
    url=OSM_API+"/"+osm_way+"/full"
    req=urllib.request.Request(url,headers={
      "Accept":"application/xml",
      "User-Agent":"BasinNexusNG-SourceReview/1.0 (https://github.com/bahagogabriel/basin-nexus-ng)"})
    with urllib.request.urlopen(req,timeout=18) as response:
        raw=response.read(MAX_XML_BYTES+1)
    if len(raw)>MAX_XML_BYTES:raise ValueError("OSM geometry body exceeds cap")
    return raw


def parse_osm_way(xml,osm_way):
    if osm_way not in REFERENCES.values():raise ValueError("Unpinned OSM identity")
    if len(xml)>MAX_XML_BYTES:raise ValueError("OSM geometry body exceeds cap")
    root=ET.fromstring(xml)
    if root.tag!="osm":raise ValueError("Unexpected OSM response root")
    wanted=osm_way.split("/")[1]
    ways=[w for w in root.findall("way") if w.get("id")==wanted]
    if len(ways)!=1:raise ValueError("OSM target way absent or repeated")
    way=ways[0]
    tags={t.get("k"):t.get("v") for t in way.findall("tag")}
    if tags.get("waterway")!="dam":
        raise ValueError("OSM current way no longer has dam-barrier tag; reassessment necessary")
    nodes={}
    for node in root.findall("node"):
        nid=node.get("id")
        if nid in nodes:raise ValueError("Duplicate OSM node")
        lon=float(node.get("lon","NaN"));lat=float(node.get("lat","NaN"))
        point=[lon,lat]
        if not _finite_point(point):raise ValueError("Invalid OSM node coordinate")
        nodes[nid]=point
        if len(nodes)>MAX_NODES:raise ValueError("Excessive OSM geometry")
    ref_ids=[n.get("ref") for n in way.findall("nd")]
    if not 2<=len(ref_ids)<=MAX_NODES:raise ValueError("OSM way cannot be represented by a simple line")
    if any(n not in nodes for n in ref_ids):
        raise ValueError("OSM way geometry incomplete")
    coords=[nodes[n] for n in ref_ids]
    if len({tuple(v) for v in coords})<2:raise ValueError("Degenerate way")
    return {"osm_way":osm_way,"osm_url":"https://www.openstreetmap.org/"+osm_way,
      "geometry_type":"LineString","coordinates":coords,
      "osm_node_count":len(coords),
      "dam_tag_currently_present":True,
      "source_lineage_independently_verified":False,
      "site_wall_surveyed":False}


def local_line_distance_m(source_point,coords):
    if not _finite_point(source_point):raise ValueError("Source point is invalid")
    if len(coords)<2 or len(coords)>MAX_NODES or not all(_finite_point(x) for x in coords):
        raise ValueError("Invalid OSM source geometry")
    crs=CRS.from_proj4(f"+proj=aeqd +lat_0={source_point[1]} +lon_0={source_point[0]} +datum=WGS84 +units=m +no_defs")
    transform=Transformer.from_crs("EPSG:4326",crs,always_xy=True)
    line=LineString([transform.transform(*c) for c in coords])
    if not line.is_valid or line.length==0:raise ValueError("Invalid polyline")
    # A local azimuthal equidistant projection is sufficient for short ways here.
    minimum=line.distance(Point(0,0))
    return {"source_to_osm_polyline_nearest_m":round(minimum,1),
      "osm_way_polyline_length_m_approx":round(line.length,1),
      "method":"AEQD_METRIC_NEAREST_ON_OSM_DIGITIZED_LINE_NOT_A_STRUCTURE_SURVEY",
      "distance_is_not_position_accuracy":True,
      "wall_position_independently_confirmed":False}


def _documentary_crosswalk(source_point,ref):
    if ref!="WA26-003":return []
    leads=[]
    for record in GUSAU_DOCUMENT_LEADS:
        candidate=dict(record)
        lon,lat=record["reported_coordinate_WGS84"]
        _,_,distance=GEOD.inv(source_point[0],source_point[1],lon,lat)
        candidate["source_point_to_reported_position_m"]=round(distance,1)
        candidate["facility_identity_matched_independently"]=False
        candidate["wall_position_surveyed_independently"]=False
        candidate["source_lineage_independence_verified"]=False
        candidate["release_authorized"]=False
        leads.append(candidate)
    return leads


def _scl_comparison(pixel_row):
    dates={}; qa={}
    for epoch in ("historical_2019","recent_2026"):
        item=pixel_row["epochs"][epoch]
        dates[epoch]=item.get("acquired_utc")
        q=item.get("pixel_qa") or {}
        qa[epoch]={"center_scl_water_fraction_of_clear":q.get("center_scl_water_fraction_of_clear"),
                   "center_clear_fraction_of_valid":q.get("center_clear_fraction_of_valid"),
                   "valid_coverage_fraction":q.get("valid_coverage_fraction"),
                   "acquired_utc":dates[epoch],
                   "optical_pixel_state":item["pixel_state"]}
    a=qa["historical_2019"]["center_scl_water_fraction_of_clear"]
    b=qa["recent_2026"]["center_scl_water_fraction_of_clear"]
    delta=round((b-a)*100,2) if a is not None and b is not None else None
    return {"periods":qa,
       "center_SCL_water_fraction_difference_percentage_points_DESCRIPTIVE_ONLY":delta,
       "interpretation_status":"UNINTERPRETED_PIXEL_CLASSIFICATION_NOT_A_DAM",
       "seasonal_and_classification_and_processing_confounders":True,
       "is_not_reservoir_area_change":True,
       "is_not_dam_construction_evidence":True}


def build_packet(stage_u,stage_v,stage_w,stage_z,fetch_way=fetch_osm_way):
    originals,zrows=validate_all(stage_u,stage_v,stage_w,stage_z)
    lines=[];cases=[]
    for ref,osm_way in REFERENCES.items():
        source=originals[ref]["compiled_reference_position_WGS84"]
        state="UNAVAILABLE_NOT_NO_DAM"
        geom=None
        try:
            raw=fetch_way(osm_way)
            geom=parse_osm_way(raw,osm_way)
            geo_qa=local_line_distance_m(source,geom["coordinates"])
            state="OSM_DIGITIZED_POLYLINE_AVAILABLE_NOT_SURVEY"
            lines.append({"type":"Feature","id":ref,
                "geometry":{"type":"LineString","coordinates":geom["coordinates"]},
                "properties":{"research_reference_id":ref,"osm_way":osm_way,
                 "record_kind":"OSM_CROWDSOURCED_CONTEXT_NOT_CONFIRMED_DAM",
                 "source_license":"ODbL","source_url":geom["osm_url"],
                 "geometry_source_independent_survey":False,
                 "verified_dam_wall":False}})
        except (OSError,TimeoutError,ValueError,ET.ParseError,KeyError,TypeError):
            geo_qa=None
        cases.append({"research_reference_id":ref,
          "source_name_NOT_VERIFIED":originals[ref]["source_published_name"],
          "original_compiled_point_WGS84_NOT_WALL":source,
          "osm_way":osm_way,
          "OSM_geometry_state":state,
          "OSM_polyline_review_metrics":geo_qa,
          "independent_public_documentary_context_NOT_FACILITY_RECEIPTS":_documentary_crosswalk(source,ref),
          "sentinel_SCL_temporal_descriptive_QA":_scl_comparison(zrows[ref]),
          "human_release_receipts":{key:None for key in HUMAN_RECEIPTS},
          "exists_as_constructed_dam_independently_verified":False,
          "wall_position_independently_verified":False,
          "source_lineage_independent":False,
          "human_public_release_authorized":False,
          "editorial_status":"HOLD_REVIEW_ONLY"})
    return {"schema_version":"BN_STAGE3D_AA_AD_REVIEW_ONLY_V1",
      "status":"HUMAN_EVIDENCE_REQUIRED_NO_DAM_ADMISSIONS",
      "source_doi":stage_w["source_doi"],"source_preview_sha256":EXPECTED_SHA,
      "source_license":"CC BY 4.0",
      "osm_attribution":"© OpenStreetMap contributors","osm_license":"ODbL",
      "copernicus_attribution":"Contains modified Copernicus Sentinel data",
      "review_subjects":5,"review_cases":cases,
      "confirmed_dams":0,"published_facility_points_created":0,
      "published_private_evidence_created":0,
      "digital_evidence_context_does_not_prove_source_independence":True,
      "explanation":"The documentary, OSM geometry and Sentinel class descriptions are separate review leads, not independent existence, position or commissioning receipts.",
      "review_only_osm_way_lines":{"type":"FeatureCollection","features":lines,
        "metadata":{"status":"OSM_CROWDSOURCED_REVIEW_ONLY_NO_DAM_CONFIRMATION",
         "license":"ODbL","attribution":"© OpenStreetMap contributors"}},
      "pending_human_observations":len(HUMAN_RECEIPTS)*5}


def main():
    ap=argparse.ArgumentParser()
    for flag in ("stage-u","stage-v","stage-w","stage-z","output"):
        ap.add_argument("--"+flag,required=True,type=Path)
    args=ap.parse_args()
    if args.output.exists():raise SystemExit("Refuse existing review folder overwrite")
    inputs=[json.loads(getattr(args,f"stage_{x}").read_text("utf-8")) for x in ("u","v","w","z")]
    output=build_packet(*inputs)
    args.output.mkdir(parents=True)
    (args.output/"stage3d_aa_ad_research_receipts_NOT_CONFIRMED.json").write_text(json.dumps(
        {k:v for k,v in output.items() if k!="review_only_osm_way_lines"},
        indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (args.output/"stage3d_aa_osm_digitized_lines_ODbL_NOT_SURVEYED.geojson").write_text(
        json.dumps(output["review_only_osm_way_lines"],indent=2)+"\n",encoding="utf-8")
    table=["# Stages AA–AD: five source references — review-only priority matrix",
           "Source points CC BY 4.0; OSM linework ODbL; Copernicus optical classes separately attributed.",
           "**No engineering position verified. No new constructed dams confirmed.**",
           "| Source reference | OSM geometry | Closest point to digitized line (m) | SCL water fraction difference (percentage points) | Independent documentary lead | Decision |",
           "|---|---|---:|---:|---|---|"]
    for case in output["review_cases"]:
        m=case["OSM_polyline_review_metrics"] or {}
        difference=case["sentinel_SCL_temporal_descriptive_QA"]["center_SCL_water_fraction_difference_percentage_points_DESCRIPTIVE_ONLY"]
        table.append("| "+case["research_reference_id"]+" | "+case["OSM_geometry_state"]+
          " | "+str(m.get("source_to_osm_polyline_nearest_m","N/A"))+
          " | "+str(difference if difference is not None else "N/A")+
          " | "+("Two separate Gusau government listings (NOT a point match)" if case["independent_public_documentary_context_NOT_FACILITY_RECEIPTS"] else "None matched to point")+
          " | HOLD — UNVERIFIED |")
    table.extend(["","Differences in SCL water-class fractions reflect scene-classifier pixels in a tiny sampled window, with differing months and potential processing/seasonal effects.",
      "Even an OSM line 0m from a compiled point does NOT provide surveyed wall position or independent confirmation.",
      "Two Gusau official coordinate values are different types of features and must be reconciled by a professional reviewer.",
      "This document is an editable evidence checklist; all human receipt fields remain null."])
    (args.output/"STAGE3D_AA_AD_REVIEW_MATRIX.md").write_text("\n".join(table)+"\n",encoding="utf-8")
    print("STAGES AA–AD:",len(output["review_cases"]),"review-only cases; OSM digitized lines:",
          len(output["review_only_osm_way_lines"]["features"]),"; confirmed dams=0")


if __name__=="__main__":main()
