#!/usr/bin/env python3
"""Stage 3D-X/Y: bounded Sentinel-2 RGB/SCL pixel chips, local cloud QA and reviewer matrix.

No dam/structure verification, historical construction assertion, coordinate
correction, automatic publication or private stakeholder material. This module
is stdlib-importable for synthetic PR tests; rasterio/numpy/Pillow are optional
main-workflow pixel readers only.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit
import urllib.request

SOURCE_SHA="2dc9c81925ea2ed6b2cb82f13410868a96ccc93d1897f3eda6040e924c9dd82a"
EXPECTED=["WA26-003","WA26-083","WA26-184","WA26-185","WA26-186"]
EPOCHS=("historical_2019","recent_2026")
CATALOG_PREFIX="https://earth-search.aws.element84.com/v1/collections/sentinel-2-c1-l2a/items/"
ALLOWED_COG_HOSTS={"e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com",
                   "sentinel-cogs.s3.us-west-2.amazonaws.com"}
SCL_OBSCURED={3,8,9,10,11}
SCL_CLEAR={4,5,6,7}
SCL_NO_DATA={0,1}
SCENE_LIMIT=2
PIXELS=96
HALF_EXTENT_M=360
MAX_ITEM_BYTES=800_000


def validate_source(w):
    if (w.get("schema_version")!="BN_STAGE3D_W_LINEAGE_EO_DISCOVERY_V1"
        or w.get("status")!="RESEARCH_ONLY_NO_FACILITY_ADMISSIONS"
        or w.get("source_doi")!="10.60507/FK2/YLDK1Y"
        or w.get("source_preview_sha256")!=SOURCE_SHA
        or w.get("source_license")!="CC BY 4.0"
        or w.get("osm_license")!="ODbL"
        or w.get("eo_collection")!="sentinel-2-c1-l2a"
        or w.get("independently_confirmed_dams")!=0
        or w.get("human_release_receipts_generated")!=0
        or w.get("public_map_changes") is not False
        or w.get("reviewed_site_count")!=5
        or w.get("scenes_are_metadata_not_checked_pixel_evidence") is not True
        or w.get("returned_scene_cloud_is_tile_level_not_at_reference_point") is not True):
        raise ValueError("Fail-closed: verified Stage W baseline drift")
    rows=w.get("records")
    if not isinstance(rows,list) or len(rows)!=5:raise ValueError("Five research cases required")
    seen=set()
    for r in rows:
        ref=r.get("source_reference_id")
        if ref not in EXPECTED or ref in seen:raise ValueError("Unexpected or duplicate research reference")
        seen.add(ref)
        p=r.get("source_position_WGS84_UNVERIFIED")
        if (not isinstance(p,list) or len(p)!=2
            or any(type(v) not in (float,int) or not math.isfinite(v) for v in p)
            or not 2<=p[0]<=16 or not 4<=p[1]<=15):
            raise ValueError("Untrusted geographic source coordinates")
        if (r.get("confirmation_decision")!="HOLD_REVIEW_ONLY"
            or r.get("dam_wall_independently_located") is not False
            or r.get("constructed_dam_independently_verified") is not False
            or r.get("historical_earth_observation_interpreted") is not False
            or r.get("source_lineage_independent") is not False
            or r.get("public_release_authorized") is not False):
            raise ValueError("Review-only source was incorrectly promoted")
        if not isinstance(r.get("sentinel2_scene_metadata"),dict) or set(r["sentinel2_scene_metadata"])!=set(EPOCHS):
            raise ValueError("Epochs missing")
        for epoch in EPOCHS:
            d=r["sentinel2_scene_metadata"][epoch]
            if d.get("catalog_state") not in ("SCENE_METADATA_FOUND",
                    "CATALOG_UNAVAILABLE_NOT_NO_IMAGERY","NO_USABLE_CATALOG_ITEMS_NOT_NO_IMAGERY"):
                raise ValueError("Unexpected scene metadata status")
            scenes=d.get("shortlist")
            if not isinstance(scenes,list) or len(scenes)>3:raise ValueError("Scene shortlist overflow")
            for s in scenes:
                if (s.get("collection")!="sentinel-2-c1-l2a"
                    or s.get("scene_cloud_not_point_cloud") is not True
                    or s.get("image_pixels_downloaded") is not False
                    or s.get("structure_visually_confirmed") is not False
                    or not isinstance(s.get("item_id"),str)
                    or s.get("stac_item")!=CATALOG_PREFIX+s["item_id"]
                    or type(s.get("scene_cloud_pct")) not in (int,float)
                    or not 0<=s["scene_cloud_pct"]<=100):
                    raise ValueError("Scene metadata or unverified flag mismatch")
    if set(seen)!=set(EXPECTED):raise ValueError("The original five research IDs changed")
    return sorted(rows,key=lambda z:EXPECTED.index(z["source_reference_id"]))


def parse_assets(item, expected_id):
    if (not isinstance(item,dict) or item.get("type")!="Feature"
        or item.get("id")!=expected_id
        or item.get("collection")!="sentinel-2-c1-l2a"):
        raise ValueError("STAC item not identical to pinned metadata lead")
    assets=item.get("assets")
    if not isinstance(assets,dict):raise ValueError("Missing Sentinel COG assets")
    links={}
    for name in ("visual","scl"):
        a=assets.get(name)
        if not isinstance(a,dict):raise ValueError("Missing visual or SCL COG")
        href=a.get("href")
        if not isinstance(href,str):raise ValueError("COG href absent")
        p=urlsplit(href)
        if (p.scheme!="https" or p.hostname not in ALLOWED_COG_HOSTS
            or p.username or p.password or p.query or p.fragment
            or not p.path.endswith(".tif")):
            raise ValueError("COG host or type not in approved public data range")
        links[name]=href
    return links


def center_cloud_qa(scl, visual_valid):
    """Pure classification of SCL pixels; does not identify a dam or waterbarrier."""
    if not scl or not isinstance(scl,list) or len(scl)!=len(visual_valid):
        raise ValueError("SCL and visual pixel dimensions must align")
    n=len(scl);mid=n//2
    valid=obscured=clear=water=center_valid=center_clear=center_obscured=center_water=0
    for y,row in enumerate(scl):
        if not isinstance(row,list) or len(row)!=n or len(visual_valid[y])!=n:
            raise ValueError("Expected square, aligned scene classification grid")
        for x,raw in enumerate(row):
            if type(raw) is not int or not 0<=raw<=11:raise ValueError("Invalid Sentinel-2 SCL class")
            if not visual_valid[y][x] or raw in SCL_NO_DATA:continue
            valid+=1
            if raw in SCL_OBSCURED:obscured+=1
            if raw in SCL_CLEAR:clear+=1
            if raw==6:water+=1
            if abs(x-mid)<=12 and abs(y-mid)<=12:
                center_valid+=1
                if raw in SCL_CLEAR:center_clear+=1
                if raw in SCL_OBSCURED:center_obscured+=1
                if raw==6:center_water+=1
    total=n*n
    return {"pixels_total":total,"valid_pixels":valid,
       "valid_coverage_fraction":round(valid/total,4),
       "obscured_fraction_of_valid":round(obscured/valid,4) if valid else None,
       "clear_fraction_of_valid":round(clear/valid,4) if valid else None,
       "scl_water_fraction_of_clear":round(water/clear,4) if clear else None,
       "center_valid_pixels":center_valid,
       "center_obscured_fraction_of_valid":round(center_obscured/center_valid,4) if center_valid else None,
       "center_clear_fraction_of_valid":round(center_clear/center_valid,4) if center_valid else None,
       "center_scl_water_fraction_of_clear":round(center_water/center_clear,4) if center_clear else None,
       "scl_water_is_not_evidence_of_a_dam":True,
       "center_is_compiled_reference_not_a_verified_wall":True}


def fetch_item(url, expected_id):
    if url!=CATALOG_PREFIX+expected_id:raise ValueError("Unapproved STAC item request")
    with urllib.request.urlopen(urllib.request.Request(url,headers={
            "Accept":"application/json","User-Agent":"BasinNexusNG-EO-Review/1.0"}),timeout=17) as r:
        raw=r.read(MAX_ITEM_BYTES+1)
    if len(raw)>MAX_ITEM_BYTES:raise ValueError("STAC item too large")
    return json.loads(raw)


def _pixel_chip(assets,position):
    """Only called on the main GitHub Actions runner with optional GDAL packages."""
    import numpy as np
    from PIL import Image,ImageDraw
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.transform import from_bounds
    from rasterio.vrt import WarpedVRT
    lon,lat=position
    dy=HALF_EXTENT_M/111_320
    dx=HALF_EXTENT_M/(111_320*math.cos(math.radians(lat)))
    target=from_bounds(lon-dx,lat-dy,lon+dx,lat+dy,PIXELS,PIXELS)
    arrays={}
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="YES",
        GDAL_HTTP_MAX_RETRY="1",GDAL_HTTP_TIMEOUT="15",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",VSI_CACHE="TRUE",VSI_CACHE_SIZE="2000000"):
        for key in ("visual","scl"):
            with rasterio.open(assets[key]) as ds:
                if ds.crs is None:raise ValueError("Unprojected source imagery")
                if key=="visual" and ds.count<3:raise ValueError("Visual COG lacks RGB bands")
                with WarpedVRT(ds,crs="EPSG:4326",transform=target,width=PIXELS,
                               height=PIXELS,resampling=Resampling.bilinear if key=="visual"
                               else Resampling.nearest) as vrt:
                    raw=vrt.read(indexes=[1,2,3] if key=="visual" else [1],masked=True)
                    arrays[key]=raw
    rgb=arrays["visual"]
    scl=arrays["scl"][0]
    rgb_data=np.asarray(rgb.filled(0))
    if rgb_data.dtype!=np.uint8:
        # STAC visual should normally be uint8; refuse implicit radiometric fabrication.
        raise ValueError("Sentinel visual asset unexpectedly not 8-bit RGB")
    rgb_hwc=np.moveaxis(rgb_data[:3],0,2)
    valid_r=np.logical_not(np.any(np.ma.getmaskarray(rgb[:3]),axis=0))
    scl_v=scl.filled(0).astype("uint8")
    valid=valid_r & np.logical_not(np.ma.getmaskarray(scl))
    report=center_cloud_qa(scl_v.tolist(),valid.tolist())
    im=Image.fromarray(rgb_hwc,"RGB")
    # Display only: mark source reference center, never call this a dam wall.
    draw=ImageDraw.Draw(im)
    mid=PIXELS//2
    draw.line([(mid-7,mid),(mid+7,mid)],fill=(255,30,200),width=1)
    draw.line([(mid,mid-7),(mid,mid+7)],fill=(255,30,200),width=1)
    return im,report


def run(w, output, *, pixel_reader=None, item_fetcher=None, attempts=SCENE_LIMIT):
    rows=validate_source(w)
    if attempts not in (1,2,3):raise ValueError("Review fetch attempts must be bounded")
    reader=pixel_reader or _pixel_chip
    fetcher=item_fetcher or fetch_item
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    records=[]
    from PIL import Image,ImageDraw,ImageFont
    img_map={}
    for row in rows:
        ref=row["source_reference_id"]
        period_info={}
        for epoch in EPOCHS:
            shots=row["sentinel2_scene_metadata"][epoch]["shortlist"]
            errors=[];successful=None
            for shot in shots[:attempts]:
                try:
                    item=fetcher(shot["stac_item"],shot["item_id"])
                    links=parse_assets(item,shot["item_id"])
                    picture,metrics=reader(links,row["source_position_WGS84_UNVERIFIED"])
                    if picture.size!=(PIXELS,PIXELS):raise ValueError("Unexpected pixel-chip dimensions")
                    if metrics.get("pixels_total")!=PIXELS*PIXELS:raise ValueError("Pixel audit dimensions wrong")
                    im_file=f"{ref}_{epoch}_RGB_REVIEW_ONLY.png"
                    picture.save(out/im_file)
                    img_map[(ref,epoch)]=picture
                    successful={"pixel_state":"RGB_SCL_PIXELS_SAMPLED_REVIEW_ONLY",
                         "acquired_utc":shot["acquired_utc"],
                         "scene_cloud_pct_metadata":shot["scene_cloud_pct"],
                         "item_id":shot["item_id"],"stac_item":shot["stac_item"],
                         "RGB_chip":im_file,"pixel_qa":metrics,
                         "structure_visually_verified":False,
                         "site_coordinate_verified":False,
                         "image_interpretation_performed":False}
                    break
                except (OSError,TimeoutError,ValueError,RuntimeError,KeyError,IndexError,
                        json.JSONDecodeError) as e:
                    errors.append(type(e).__name__)
            period_info[epoch]=successful if successful else {
                "pixel_state":"PIXELS_UNAVAILABLE_NOT_NO_IMAGERY",
                "attempted_scene_count":min(len(shots),attempts),
                "failure_categories":errors,"RGB_chip":None,"pixel_qa":None,
                "structure_visually_verified":False,
                "site_coordinate_verified":False,
                "image_interpretation_performed":False}
        records.append({"reference_id":ref,"source_published_name":row["source_published_name"],
           "original_reference_WGS84_UNVERIFIED":row["source_position_WGS84_UNVERIFIED"],
           "epochs":period_info,
           "pixel_coverage_not_construction_date":True,
           "actual_dam_wall_position_verified":False,
           "independent_structure_confirmation":False,
           "human_interpretation_receipt":None,
           "public_release_authorized":False})
    # Stage 3D-Y: visual reviewer board, never a verified dam map.
    W,H=330,260
    board=Image.new("RGB",(W*3,H*len(EXPECTED)),"#f4f4f1")
    d=ImageDraw.Draw(board)
    for i,record in enumerate(records):
        ref=record["reference_id"]
        d.text((12,i*H+16),ref,fill="#172630")
        d.text((12,i*H+40),"SOURCE ONLY / UNVERIFIED",fill="#a00030")
        d.text((12,i*H+70),str(record["source_published_name"] or "UNNAMED REFERENCE")[:27],fill="#172630")
        for col,epoch in enumerate(EPOCHS,1):
            entry=record["epochs"][epoch]
            x=(col*W)+13;y=i*H+12
            d.text((x,y),epoch.replace("_"," "),fill="#172630")
            if (ref,epoch) in img_map:
                image=img_map[(ref,epoch)].resize((195,195),Image.Resampling.NEAREST)
                board.paste(image,(x,y+27))
                d.text((x+206,y+62),entry["acquired_utc"][:10],fill="#172630")
                qa=entry["pixel_qa"]
                d.text((x+206,y+90),"valid "+str(qa["valid_coverage_fraction"]),fill="#172630")
                d.text((x+206,y+112),"clear "+str(qa["center_clear_fraction_of_valid"]),fill="#172630")
            else:
                d.text((x,y+80),"PIXELS UNAVAILABLE",fill="#a00030")
    board.save(out/"STAGE3D_Y_REVIEW_BOARD_UNVERIFIED.png")
    review={"schema_version":"BN_STAGE3D_XY_SENTINEL_RGB_SCL_REVIEW_V1",
      "status":"PIXEL_SAMPLE_REVIEW_ONLY_NOT_A_DAM_SURVEY",
      "source_doi":w["source_doi"],"source_license":"CC BY 4.0",
      "source_preview_sha256":SOURCE_SHA,
      "osm_attribution":w["osm_attribution"],"osm_license":"ODbL",
      "sentinel_collection":w["eo_collection"],
      "copernicus_credit":"Contains modified Copernicus Sentinel data; source Element 84 Earth Search",
      "epochs":list(EPOCHS),
      "pixel_grid_size":PIXELS,"half_extent_m_approx":HALF_EXTENT_M,
      "RGB_SCL_samples_attempted":len(records)*len(EPOCHS),
      "RGB_SCL_samples_successful":sum(v["pixel_state"]=="RGB_SCL_PIXELS_SAMPLED_REVIEW_ONLY"
          for r in records for v in r["epochs"].values()),
      "SCL_not_independent_engineering_evidence":True,
      "none_of_the_pixel_metrics_estimate_dam_position_accuracy":True,
      "historical_comparison_not_construction_or_operational_proof":True,
      "independently_confirmed_dams":0,"public_map_changes":False,
      "source_names_not_verified":True,
      "reviewer_board":"STAGE3D_Y_REVIEW_BOARD_UNVERIFIED.png",
      "records":records}
    (out/"stage3d_xy_pixel_qa_NOT_CONFIRMED.json").write_text(
        json.dumps(review,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    text=["# Stage 3D-X/Y | Pixel sampling and reviewer image board",
      "All coordinates are compiled research references, NOT validated dam walls. "
      "This file is a machine-generated research status sheet, NOT a human visual interpretation.",
      "Original compiled point source CC BY 4.0; OSM ODbL separate; contains modified Copernicus Sentinel data.",
      "",
      "| Reference | 2019 imagery | 2026 imagery | Confirmation |","|---|---|---|---|"]
    for r in records:
        v=[]
        for e in EPOCHS:
            info=r["epochs"][e];q=info["pixel_qa"]
            v.append(("RGB/SCL sampled; center clear "+str(q["center_clear_fraction_of_valid"])
                if q else "Pixels unavailable") )
        text.append("| "+r["reference_id"]+" | "+" | ".join(v)+" | **UNVERIFIED** |")
    text.extend(["","SCL clear classes: 4, 5, 6, 7. Obscured: 3, 8, 9, 10, 11. "
                 "Zeros and invalid imagery are excluded. SCL water class 6 does not verify a dam.",
                 "No comparison of spectral reflectance, no automated built-structure detection, "
                 "no cloud-free guarantee and no independently determined positional uncertainty.",
                 "PNG crosshairs mark the *source reference* coordinate only. "
                 "Human reviewers must separately inspect imagery, records and rights/permissions."])
    (out/"STAGE3D_Y_REVIEW_MATRIX.md").write_text("\n".join(text)+"\n",encoding="utf-8")
    return review


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage-w",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    args=p.parse_args()
    if args.output_dir.exists():raise SystemExit("Refusing to overwrite a prior pixel review directory")
    w=json.loads(args.stage_w.read_text(encoding="utf-8"))
    validate_source(w)
    result=run(w,args.output_dir)
    print("STAGE 3D-X/Y: sampled",result["RGB_SCL_samples_successful"],
          "of",result["RGB_SCL_samples_attempted"],"RGB/SCL chips; independently confirmed dams 0")


if __name__=="__main__":main()
