#!/usr/bin/env python3
"""Stage 3D-R: build an inspectable, SOURCE-ONLY candidate GeoJSON for review.

This is NOT independently confirmed infrastructure. Original source: Kouassi et al.
(2026) West Africa dams, CC BY 4.0. The output is a research candidate artifact
and must not be installed in public site/data without a separate reviewed release.
No stakeholder, private or inferred entries. No invented names or capacities.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,unicodedata
from pathlib import Path
from shapely.geometry import Point
from preflight_wa_dams_2026 import preflight,fetch_pinned
from review_wa_dam_catchments_2026 import (
 ensure_wgs84_zip,validate_features,fetch_zip,EXPECTED_REGIONAL,EXPECTED_NIGERIA,ZIP_MD5)
from review_wa_dam_identity_2026 import norm,is_known
CSV_MD5="046b106da1e3a57ec2f1c461fe411b26"
DATASET_DOI="10.60507/FK2/YLDK1Y"
UNSAFE_NAME=re.compile(r"(?:@|https?://|[<>{}\r\n\t])",re.I)

def clean_display_name(value):
    """Published names only, never manufacturing a name or silently fixing locality."""
    if not is_known(value):
        return None
    name=" ".join(str(value).split())
    if not 2<=len(name)<=96 or UNSAFE_NAME.search(name):
        return None
    if norm(name) in {"dam","water reservoir","reservoir","pond","small dam","lake"}:
        return None
    return name

def build(csv_bytes,dam_zip_bytes,catchment_path,expected_csv_md5=CSV_MD5,
          expected_zip_md5=ZIP_MD5,expected_regional=EXPECTED_REGIONAL,
          expected_nigeria=EXPECTED_NIGERIA):
    audit=preflight(csv_bytes,expected_md5=expected_csv_md5,expected_count=expected_regional)
    crs=ensure_wgs84_zip(dam_zip_bytes,expected_md5=expected_zip_md5)
    columns=set(audit["column_names"])
    mandatory={"ID","Country","Long_X","Lat_Y","Dam_Name","Main_Sourc"}
    if not mandatory<=columns:
        raise ValueError("Published source columns no longer match pinned intake")
    polygons=validate_features(Path(catchment_path))
    rows=list(csv.DictReader(io.StringIO(csv_bytes.decode(audit["source_character_encoding"]),newline="")))
    features=[]
    ids=set()
    counts={k:0 for k,_ in polygons}
    with_names=0
    rows_within=0
    source_numeric=0
    for row in rows:
        if norm(row["Country"]) not in {"nigeria","nga","ng"}:continue
        source_numeric+=1
        id=str(row["ID"]).strip()
        if not id or id in ids:raise ValueError("Unknown or duplicate source ID")
        ids.add(id)
        x=float(row["Long_X"]);y=float(row["Lat_Y"])
        if not (-180<=x<=180 and -90<=y<=90):raise ValueError("Invalid source point")
        from math import isfinite
        if not isfinite(x) or not isfinite(y):raise ValueError("Non-finite coordinate")
        covers=[cid for cid,poly in polygons if poly.covers(Point(x,y))]
        if len(covers)>1:
            raise ValueError("Source point belongs to multiple display catchments; manual review")
        if not covers:continue
        rows_within+=1
        cid=covers[0];counts[cid]+=1
        name=clean_display_name(row["Dam_Name"])
        if name:with_names+=1
        features.append({"type":"Feature",
          "id":"WA26-"+str(rows_within).zfill(3),
          "geometry":{"type":"Point","coordinates":[round(x,7),round(y,7)]},
          "properties":{
            "reference_id":"WA26-"+str(rows_within).zfill(3),
            "catchment_id":cid,
            "published_name":name,
            "name_status":"named_in_source" if name else "unknown_in_source",
            "record_kind":"compiled_research_reference",
            "independent_existence_verified":False,
            "position_verified":False,
            "facility_operational_status":"unknown",
            "source_lineage":"Kouassi et al. 2026 compiled dataset",
            "source_doi":DATASET_DOI,
            "source_license":"CC BY 4.0"
          }})
    if source_numeric!=expected_nigeria or rows_within!=189 or with_names!=71 or sum(counts.values())!=189:
        raise ValueError("Candidate point counts do not match verified Stage 3D-Q source QA; abort")
    if len({f["id"] for f in features})!=len(features):
        raise ValueError("Duplicate public candidate ID")
    out={"type":"FeatureCollection","metadata":{
        "schema_version":"BN_COMPILED_DAM_REFERENCE_PREVIEW_V1",
        "status":"RESEARCH_COMPILED_SOURCE_UNVERIFIED_NOT_CONFIRMED_FACILITIES",
        "source_doi":DATASET_DOI,
        "source_csv_md5":audit["computed_md5"],
        "source_shapefile_md5":crs["source_shapefile_md5"],
        "source_crs_epsg":4326,"source_license":"CC BY 4.0",
        "country_source_rows":source_numeric,"source_rows_intersecting_catchments":rows_within,
        "named_source_rows_intersecting_catchments":with_names,
        "verified_facility_count":0,
        "unknown_name_does_not_imply_verified_existence":True,
        "publication_decision":"REVIEW_CANDIDATES_ONLY",
        "caveat":"Coordinates are compiled source reference points; neither survey-verified nor proof of physical dam existence, facility name, current operation or engineering capacity. Use only in separately labelled opt-in research view, never in verified asset layer."
      },"features":features}
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fetch",action="store_true")
    p.add_argument("--csv",type=Path);p.add_argument("--dam-zip",type=Path)
    p.add_argument("--catchments",type=Path,default=Path("site/data/catchments.geojson"))
    p.add_argument("--review-output",type=Path,required=True)
    args=p.parse_args()
    if args.fetch:
        if args.csv or args.dam_zip:raise SystemExit("Choose fetch OR files")
        c,z=fetch_pinned(),fetch_zip()
    else:
        if not args.csv or not args.dam_zip:raise SystemExit("Require both source files")
        c,z=args.csv.read_bytes(),args.dam_zip.read_bytes()
    out=build(c,z,args.catchments)
    if args.review_output.exists():raise SystemExit("Refusing review overwrite")
    args.review_output.parent.mkdir(parents=True,exist_ok=True)
    with args.review_output.open("x",encoding="utf-8") as f:
        json.dump(out,f,ensure_ascii=False,indent=2);f.write("\n")
    print("COMPILED REFERENCE REVIEW CANDIDATES:",
          len(out["features"]),"name-present",out["metadata"]["named_source_rows_intersecting_catchments"],
          "confirmed-facilities",out["metadata"]["verified_facility_count"],
          "stage","REVIEW_ONLY")
if __name__=="__main__":main()
