#!/usr/bin/env python3
"""Stage 3D-N: regional dam reference *candidate* overlay, aggregate QA only.

2026 Kouassi et al. source: DOI 10.60507/FK2/YLDK1Y, CC BY 4.0.
DO NOT use the result as verified dam positions, unique facility counts or
as evidence that a stakeholder-reported location has been confirmed.
No individual source rows, names, coordinates or facility points are emitted.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path
from shapely.geometry import shape,Point
from pyproj import CRS
from preflight_wa_dams_2026 import preflight,fetch_pinned

ZIP_URL=("https://bonndata.uni-bonn.de/api/access/datafile/:persistentId/"
         "?persistentId=doi%3A10.60507%2FFK2%2FYLDK1Y%2FPQBMFO")
ZIP_MD5="a87f9b4ef2e96625b737ffac8595c138"
ZIP_MAX_BYTES=2_000_000
EXPECTED_CRS=4326
SOURCE_FIELDS={"country":"Country","longitude":"Long_X","latitude":"Lat_Y","id":"ID"}
EXPECTED_REGIONAL=1429
EXPECTED_NIGERIA=231 # As established from the exact 2026 publisher CSV on 28 Oct 2026.

def fetch_zip():
    req=urllib.request.Request(ZIP_URL,headers={"User-Agent":"BasinNexusSourceQA/1.0"})
    with urllib.request.urlopen(req,timeout=40) as resp:
        data=resp.read(ZIP_MAX_BYTES+1)
    if len(data)>ZIP_MAX_BYTES or len(data)<1000:
        raise ValueError("Publisher Shapefile ZIP size unexpected")
    return data

def ensure_wgs84_zip(data:bytes, expected_md5=ZIP_MD5)->dict:
    if not isinstance(data,bytes) or hashlib.md5(data).hexdigest()!=expected_md5:
        raise ValueError("Publisher's 2026 dam shapefile ZIP checksum mismatch")
    with zipfile.ZipFile(io.BytesIO(data)) as zipped:
        names=zipped.namelist()
        if len(names)>35 or any(n.startswith("/") or ".." in Path(n).parts for n in names):
            raise ValueError("Unexpected ZIP member naming")
        prjs=[n for n in names if n.lower().endswith(".prj")]
        if len(prjs)!=1:raise ValueError("Exactly one published CRS definition is required")
        wkt=zipped.read(prjs[0]).decode("utf-8-sig")
        crs=CRS.from_wkt(wkt)
        if not crs.is_geographic or crs.to_epsg()!=EXPECTED_CRS:
            raise ValueError("Publisher dam shapefile coordinate reference is not EPSG:4326")
        shp=[n for n in names if n.lower().endswith(".shp")]
        if len(shp)!=1:raise ValueError("Missing or multiple source shapefile geometry files")
    return {"source_shapefile_md5":expected_md5,"source_crs_epsg":EXPECTED_CRS,"source_prj_verified":True}

def validate_features(path:Path):
    geo=json.loads(path.read_text(encoding="utf-8"))
    if geo.get("type")!="FeatureCollection":
        raise ValueError("SCMP catchment geometry is not GeoJSON")
    all_geos=[]
    for feature in geo["features"]:
        id=feature["properties"]["id"]
        geometry=shape(feature["geometry"])
        if not id.startswith("SCMP-C") or geometry.is_empty or not geometry.is_valid:
            raise ValueError("Invalid displayed catchment geometry")
        all_geos.append((id,geometry))
    if len(all_geos)!=20 or len(set(x[0] for x in all_geos))!=20:
        raise ValueError("Expected the original 20 SCMP catchments")
    return all_geos

def inspect(csv_bytes:bytes,zip_bytes:bytes,catchment_geojson:Path,
            expected_count=EXPECTED_REGIONAL,expected_nigeria=EXPECTED_NIGERIA,
            csv_md5="046b106da1e3a57ec2f1c461fe411b26",
            zip_md5=ZIP_MD5):
    source=preflight(csv_bytes,expected_md5=csv_md5,expected_count=expected_count)
    coordinate=ensure_wgs84_zip(zip_bytes,expected_md5=zip_md5)
    if any(k not in source["column_names"] for k in SOURCE_FIELDS.values()):
        raise ValueError("Required source ID, country and WGS84 coordinate fields missing")
    rows=list(csv.DictReader(io.StringIO(csv_bytes.decode(source["source_character_encoding"]),newline="")))
    nigeria_rows=[r for r in rows if (r["Country"] or "").strip().lower() in {"nigeria","nga","ng"}]
    if source["nigeria_source_country_rows"]!=len(nigeria_rows) or len(nigeria_rows)!=expected_nigeria:
        raise ValueError("Country-classification count changed or source version not pinned")
    catchments=validate_features(catchment_geojson)
    matched_by_id=Counter()
    no_coords=0;invalid_coords=0;duplicate_coordinates=0;duplicate_ids=0
    unique_coord=set();known_ids=set()
    multiple=0;inside_any=0;on_boundary=0
    for r in nigeria_rows:
        rid=str(r["ID"]).strip()
        if not rid or rid in known_ids:duplicate_ids+=1
        known_ids.add(rid)
        try:
            x=float(r["Long_X"]);y=float(r["Lat_Y"])
        except (TypeError,ValueError):
            no_coords+=1
            continue
        if not math.isfinite(x) or not math.isfinite(y) or not (-180<=x<=180 and -90<=y<=90):
            invalid_coords+=1
            continue
        pair=(round(x,7),round(y,7))
        if pair in unique_coord:duplicate_coordinates+=1
        unique_coord.add(pair)
        point=Point(x,y)
        matches=[id for id,poly in catchments if poly.covers(point)]
        if matches:
            inside_any+=1
            if len(matches)>1:multiple+=1
            for id in matches:
                matched_by_id[id]+=1
                if next(poly for cid,poly in catchments if cid==id).boundary.intersects(point):
                    on_boundary+=1
    return {
        "qa_status":"GEOGRAPHIC_CANDIDATE_OVERLAY_COMPLETED_NOT_FIELD_VALIDATED",
        "source_dataset_doi":"10.60507/FK2/YLDK1Y",
        "source_csv_md5":source["computed_md5"],
        "source_shapefile_md5":coordinate["source_shapefile_md5"],
        "source_crs_epsg_verified":coordinate["source_crs_epsg"],
        "source_rows_regional":source["source_records"],
        "source_country_nigeria_rows":len(nigeria_rows),
        "country_classification_method":"exact publisher Country text/ISO labels; not political boundary",
        "nigeria_rows_without_numeric_location":no_coords,
        "nigeria_rows_with_invalid_numeric_location":invalid_coords,
        "nigeria_repeated_source_ids":duplicate_ids,
        "nigeria_repeated_coordinate_pairs":duplicate_coordinates,
        "nigeria_source_rows_intersecting_any_study_catchment":inside_any,
        "source_rows_intersecting_multiple_study_catchments":multiple,
        "boundary_intersection_candidate_count":on_boundary,
        "nigeria_rows_outside_all_study_catchments_or_unmapped":len(nigeria_rows)-inside_any,
        "overlap_counts_by_catchment":dict(sorted(matched_by_id.items())),
        "intersections_not_unique_dams":sum(matched_by_id.values()),
        "spatial_interpretation":"Candidate intersections with supplied simplified SCMP display polygons, WGS84; adjacent catchments may share source points. Not a survey, active dam inventory, verified facility count, official jurisdiction or coordinates cleared for publication.",
        "individual_source_names_published":0,
        "individual_coordinates_published":0,
        "stakeholder_source_crossmatches_performed":False,
        "public_evidence_records_authorized":0,
        "review":"HOLD_FOR_SITE_IDENTITY_POSITION_UNCERTAINTY_SOURCE_LINEAGE_AND_REUSE"
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fetch",action="store_true",help="Fetch pinned original CSV and shapefile ZIP")
    parser.add_argument("--csv",type=Path)
    parser.add_argument("--dam-zip",type=Path)
    parser.add_argument("--catchments",type=Path,default=Path("site/data/catchments.geojson"))
    parser.add_argument("--report",type=Path,required=True)
    args=parser.parse_args()
    if args.fetch:
        if args.csv or args.dam_zip:raise SystemExit("Select fetch or existing files, not both")
        csv_bytes=fetch_pinned();zip_bytes=fetch_zip()
    else:
        if not args.csv or not args.dam_zip:raise SystemExit("Both source CSV and publisher ZIP required")
        csv_bytes=args.csv.read_bytes();zip_bytes=args.dam_zip.read_bytes()
    report=inspect(csv_bytes,zip_bytes,args.catchments)
    if args.report.exists():raise SystemExit("Refusing to overwrite existing review report")
    args.report.parent.mkdir(parents=True,exist_ok=True)
    with args.report.open("x",encoding="utf-8") as handle:
        json.dump(report,handle,indent=2);handle.write("\n")
    print("WEST AFRICA DAMS STAGE 3D-N: verified source rows",report["source_rows_regional"],
          "Nigeria-labelled",report["source_country_nigeria_rows"],
          "candidate catchment intersections",report["nigeria_source_rows_intersecting_any_study_catchment"],
          "multiple catchment",report["source_rows_intersecting_multiple_study_catchments"],
          "published positions",report["individual_coordinates_published"])

if __name__=="__main__":main()
