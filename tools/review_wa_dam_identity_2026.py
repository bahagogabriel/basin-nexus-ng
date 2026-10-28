#!/usr/bin/env python3
"""Stage 3D-P: independent-source identity/provenance and position QA.

The published Kouassi et al. (2026) dam point CSV is CC BY 4.0, but compiled
locations are not individually surveyed or approved stakeholder evidence.
This script returns only aggregate diagnostics, never source rows or point positions.

Checks the publisher's exact MD5 AND shapefile .prj before interpreting coordinates.
Names/attributes are read solely for identity flags; duplicate candidates are
NOT collapsed because two nearby points need not describe the same structure.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import math
import re
import unicodedata
from collections import Counter,defaultdict
from pathlib import Path
from pyproj import Geod
from shapely.geometry import Point
from preflight_wa_dams_2026 import fetch_pinned,preflight
from review_wa_dam_catchments_2026 import (fetch_zip,ensure_wgs84_zip,
    validate_features,EXPECTED_REGIONAL,EXPECTED_NIGERIA,ZIP_MD5)

MISSING={"","na","n a","n/a","n.a.","not available","not known",
         "unknown","unnamed","none","null","nil","--","-","0"}
COLS={"Country","ID","Long_X","Lat_Y","Dam_Name","Main_Sourc"}
GEOD=Geod(ellps="WGS84")


def norm(text):
    if text is None:return ""
    raw=unicodedata.normalize("NFKD",str(text))
    return " ".join(re.findall(r"[a-z0-9]+",raw.lower().encode("ascii","ignore").decode()))


def is_known(s):
    return norm(s) not in MISSING and len(norm(s))>=2


def to_year(s):
    if not is_known(s):return None
    try:
        value=float(str(s).strip().replace(",",""))
        if math.isfinite(value) and value.is_integer() and 1700<=value<=2026:return int(value)
    except (ValueError,TypeError):
        pass
    return None


def inspect(csv_bytes:bytes, zip_bytes:bytes,catchment_geojson:Path,
            expected_count=EXPECTED_REGIONAL,expected_nigeria=EXPECTED_NIGERIA,
            expected_csv_md5="046b106da1e3a57ec2f1c461fe411b26",
            expected_zip_md5=ZIP_MD5):
    origin=preflight(csv_bytes,expected_md5=expected_csv_md5,expected_count=expected_count)
    crs=ensure_wgs84_zip(zip_bytes,expected_md5=expected_zip_md5)
    if not COLS.issubset(origin["column_names"]):
        raise ValueError("Original source missing required name, provenance or coordinates column")
    polygons=validate_features(catchment_geojson)
    text=csv_bytes.decode(origin["source_character_encoding"])
    source=list(csv.DictReader(io.StringIO(text,newline="")))
    candidates=[]
    unknown_names=unknown_source=missing_year=unparseable_year=0
    valid_years=0
    year_field="Dam_Year" if "Dam_Year" in origin["column_names"] else None
    suspicious_names=0
    source_coverage=Counter()
    matched_name=Counter()
    by_catchment=defaultdict(lambda:Counter())
    for row in source:
        if norm(row["Country"]) not in {"nigeria","nga","ng"}:continue
        try:
            longitude=float(row["Long_X"]); latitude=float(row["Lat_Y"])
        except (ValueError,TypeError):
            raise ValueError("Nigerian row lacks numeric WGS84 coordinates")
        if not all(math.isfinite(x) for x in (longitude,latitude)) or not (-180<=longitude<=180 and -90<=latitude<=90):
            raise ValueError("Nigerian source coordinate outside geographic WGS84 range")
        if not is_known(row["ID"]):
            raise ValueError("Nigerian source record lacks identifier")
        named=is_known(row["Dam_Name"])
        name=norm(row["Dam_Name"]) if named else ""
        sourced=is_known(row["Main_Sourc"])
        if not named:unknown_names+=1
        if not sourced:unknown_source+=1
        source_coverage["with_named_source" if sourced else "missing_named_source"]+=1
        if named:
            matched_name[name]+=1
            if name in {"dam","water reservoir","reservoir","pond"}:suspicious_names+=1
        year=None
        if year_field:
            year=to_year(row[year_field])
            if year is None:
                if is_known(row[year_field]):unparseable_year+=1
                else:missing_year+=1
            else:valid_years+=1
        matches=[ident for ident,poly in polygons if poly.covers(Point(longitude,latitude))]
        for cid in matches:
            by_catchment[cid]["source_positions"]+=1
            if named:by_catchment[cid]["named_rows"]+=1
            if sourced:by_catchment[cid]["rows_with_source_label"]+=1
            if year is not None:by_catchment[cid]["valid_year_rows"]+=1
        candidates.append(dict(id=row["ID"],name=name,x=longitude,y=latitude,
                               catchments=matches))
    if len(candidates)!=expected_nigeria:
        raise ValueError("Source-country count does not match audited Nigeria baseline")

    pairs_250=pairs_1000=probable_name_1km=probable_name_5km=0
    near_id_250=set()
    near_id_1000=set()
    duplicate_name_groups=set()
    nearest_distances=[]
    for i,r in enumerate(candidates):
        nearest=None
        for j in range(i+1,len(candidates)):
            other=candidates[j]
            _,_,dist=GEOD.inv(r["x"],r["y"],other["x"],other["y"])
            if not math.isfinite(dist):raise ValueError("Distance computation failed")
            if dist<=250:
                pairs_250+=1
                near_id_250.update((i,j))
            if dist<=1000:
                pairs_1000+=1
                near_id_1000.update((i,j))
            if r["name"] and r["name"]==other["name"]:
                if dist<=1000:probable_name_1km+=1
                if dist<=5000:
                    probable_name_5km+=1
                    duplicate_name_groups.add(r["name"])
    exact_repeated_names={name:count for name,count in matched_name.items() if count>1}
    # Source counts are not independently identified dams.
    return {
      "status":"COMPILED_REFERENCE_IDENTITY_AND_POSITION_QA_ONLY",
      "observation_date":"2026-10-28",
      "source_dataset_doi":"10.60507/FK2/YLDK1Y",
      "publisher_csv_md5":origin["computed_md5"],
      "publisher_zip_md5":crs["source_shapefile_md5"],
      "publisher_crs_epsg":crs["source_crs_epsg"],
      "source_country_field":"Country",
      "nigeria_source_rows":len(candidates),
      "country_label_not_a_jurisdiction_check":True,
      "catchment_match_method":"simplified study polygon covers compiled source point",
      "within_20_catchments_source_rows":sum(bool(c["catchments"]) for c in candidates),
      "cross_catchment_candidate_rows":sum(len(c["catchments"])>1 for c in candidates),
      "source_rows_with_a_dam_name":len(candidates)-unknown_names,
      "source_rows_with_missing_name":unknown_names,
      "source_rows_with_generic_name":suspicious_names,
      "source_rows_with_source_label":len(candidates)-unknown_source,
      "source_rows_without_source_label":unknown_source,
      "dam_year_field_present":bool(year_field),
      "rows_with_recognizable_dam_year":valid_years if year_field else None,
      "rows_with_missing_dam_year":missing_year if year_field else None,
      "rows_with_unparseable_dam_year":unparseable_year if year_field else None,
      "repeated_normalized_name_groups_countrywide":len(exact_repeated_names),
      "source_rows_in_repeated_name_groups":sum(exact_repeated_names.values()),
      "distinct_source_point_pairs_within_250m":pairs_250,
      "source_rows_with_neighbor_within_250m":len(near_id_250),
      "distinct_source_point_pairs_within_1km":pairs_1000,
      "source_rows_with_neighbor_within_1km":len(near_id_1000),
      "same_normalized_name_pairs_within_1km":probable_name_1km,
      "same_normalized_name_pairs_within_5km":probable_name_5km,
      "same_normalized_name_groups_within_5km":len(duplicate_name_groups),
      "by_catchment":{
        cid:{
          "source_positions":int(by_catchment[cid]["source_positions"]),
          "named_source_rows":int(by_catchment[cid]["named_rows"]),
          "rows_with_source_label":int(by_catchment[cid]["rows_with_source_label"]),
          "rows_with_recognizable_year":int(by_catchment[cid]["valid_year_rows"])
        } for cid,_ in polygons
      },
      "flags":[
        "GEODESIC_NEARBY_POINTS_MAY_BE_SEPARATE_FACILITIES",
        "REPEATED_NAMES_MAY_DESCRIBE_DIFFERENT_FACILITIES",
        "SOURCE_LABEL_IS_NOT_AN_INDEPENDENCE_CHECK",
        "YEAR_FIELD_IS_NOT_CURRENT_OPERATIONAL_VERIFICATION",
        "GEOREFERENCING_PRECISION_IS_NOT_POSITIONAL_ACCURACY",
        "CATCHMENT_GEOMETRY_SIMPLIFIED_DISPLAY_DERIVATIVE",
        "NO_REVIEWED_SITE_IDS_OR_FIELD_SURVEYS"
      ],
      "independently_verified_facilities":0,
      "individual_dam_points_published":0,
      "stakeholder_records_published":0,
      "review_decision":"HOLD_POINT_LAYER_PENDING_IDENTITY_AND_UNCERTAINTY_REVIEW"
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fetch",action="store_true")
    p.add_argument("--csv",type=Path)
    p.add_argument("--dam-zip",type=Path)
    p.add_argument("--catchments",type=Path,default=Path("site/data/catchments.geojson"))
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    if args.fetch:
        if args.csv or args.dam_zip:raise SystemExit("Choose fetch OR supplied files")
        data,zipbytes=fetch_pinned(),fetch_zip()
    else:
        if not args.csv or not args.dam_zip:raise SystemExit("Require CSV and original ZIP")
        data,zipbytes=args.csv.read_bytes(),args.dam_zip.read_bytes()
    out=inspect(data,zipbytes,args.catchments)
    if args.report.exists():raise SystemExit("Refusing overwrite")
    args.report.parent.mkdir(parents=True,exist_ok=True)
    with args.report.open("x",encoding="utf-8") as handle:
        json.dump(out,handle,ensure_ascii=False,indent=2)
        handle.write("\n")
    print("STAGE3D-P SOURCE QUALITY: Nigeria rows",out["nigeria_source_rows"],
          "named",out["source_rows_with_a_dam_name"],
          "source-described",out["source_rows_with_source_label"],
          "nearby-pairs-250m",out["distinct_source_point_pairs_within_250m"],
          "possible-name-collisions-1km",out["same_normalized_name_pairs_within_1km"],
          "verified-points",out["independently_verified_facilities"],
          "published",out["individual_dam_points_published"])


if __name__=="__main__":main()
