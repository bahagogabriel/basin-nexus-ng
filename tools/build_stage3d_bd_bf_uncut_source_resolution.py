#!/usr/bin/env python3
"""Stages 3D-BD–BF: source-checked uncut vs clipped 3-pair model diagnostic.

Uses a six-feature original 2026 FAO WFS snapshot, NOT any invented geometry.
Published output is scientific QA only: a 0m publisher endpoint match DOES NOT
establish independent in-situ hydraulic continuity or survey accuracy.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from build_stage3d_bc_original_uncut_fao_review import (
 EXPECTED,INPUTS,SCHEMA as WFS_SCHEMA,validate_feature,
 closest_endpoints,haversine,source_reconciliation)
from build_stage3d_ay_az_fao_endpoint_qa import endpoints, separation_m
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"site/data"
SCHEMA="BN_STAGE3D_BD_THREE_UNCUT_SOURCE_PAIRS_V1"
STATUS="PUBLISHER_MODEL_UNCUT_ENDPOINT_MATCH_NOT_SURVEYED_HYDRAULIC_CONFIRMATION"
PUBLIC_FIELDS={"type","name","features"}

def generate(six_source, folder=DATA):
    six_source=Path(six_source)
    root=Path(folder)
    six=six_source.read_bytes()
    document=json.loads(six)
    if (not isinstance(document,dict) or set(document)!=PUBLIC_FIELDS
        or document.get("type")!="FeatureCollection"
        or document.get("name")!="SIX_ORIGINAL_FAO_WFS_MODEL_REACHES_NOT_SURVEYED"
        or not isinstance(document.get("features"),list)
        or len(document["features"])!=6):
        raise ValueError("Not the original six-record publisher QA FeatureCollection")
    records={}
    for f in document["features"]:
        props=f.get("properties") or {}
        if str(props.get("hyriv_id")) not in {str(v) for v in INPUTS}:
            raise ValueError("Unexpected source record identity")
        id=int(props["hyriv_id"])
        if id in records:raise ValueError("Repeated WFS original source feature")
        records[id]=validate_feature(f,id)
    clipped=json.loads((root/"fao_endpoint_gap_summary.json").read_text("utf-8"))
    index=json.loads((root/"fao_endpoint_gap_index.json").read_text("utf-8"))
    topology=json.loads((root/"fao_downstream_summary.json").read_text("utf-8"))
    graph=json.loads((root/"fao_downstream_index.json").read_text("utf-8"))
    source_reconciliation(records,clipped,topology)
    if (index.get("schema_version")!="BN_STAGE3D_AZ_FAO_ENDPOINT_GAPS_LOOKUP_V1"
        or index.get("source_manifest_sha256")!=clipped["source_manifest_sha256"]
        or graph.get("schema_version")!="BN_STAGE3D_AV_FAO_TOPOLOGY_LOOKUP_V1"
        or index.get("source_index_sha256")!=clipped["source_index_sha256"]):
        raise ValueError("Prior scientific lookup/manifest source has changed")
    old_gap=dict(index["rows"])
    files=json.loads((root/"detailed_river_manifest.json").read_text("utf-8"))["files"]
    bycatch={}
    for cid in {q[2] for q in EXPECTED}:
        meta=files[cid];raw=(root/meta["file"]).read_bytes()
        if len(raw)!=meta["bytes"] or hashlib.sha256(raw).hexdigest()!=meta["sha256"]:
            raise ValueError("Published clipped FAO river file has changed")
        features=json.loads(raw)["features"]
        bycatch[cid]={int(f["properties"]["hyriv_id"]):f for f in features}
    published=[]
    for fid,dn,cid,prior in EXPECTED:
        src,dst=records[fid],records[dn]
        original_gap,pair=closest_endpoints(src["parts"],dst["parts"])
        if original_gap!=0.0:
            raise ValueError("Original publisher did not support an exact modeled endpoint match")
        if fid not in bycatch[cid] or dn not in bycatch[cid]:
            raise ValueError("Original clipped source pair is missing from expected study catchment")
        clsrc,cldst=bycatch[cid][fid],bycatch[cid][dn]
        srcpts,dstpts=endpoints(clsrc["geometry"]),endpoints(cldst["geometry"])
        localgap=round(separation_m(srcpts,dstpts),1)
        if abs(localgap-prior)>0.11 or abs(old_gap[fid]-prior)>0.11:
            raise ValueError("Original clipped outlier baseline has drifted")
        point=pair[0]
        if point!=pair[1]:
            raise ValueError("Non-matching original-source modeled junction")
        upstream_cut=round(min(haversine(p,point) for p in srcpts),1)
        downstream_cut=round(min(haversine(p,point) for p in dstpts),1)
        published.append({
            "catchment_id":cid,
            "source_hyriv_id":fid,"next_down_hyriv_id":dn,
            "clipped_display_min_endpoint_gap_m":localgap,
            "original_uncut_model_min_endpoint_gap_m":0.0,
            "publisher_modeled_shared_endpoint_lon_lat":point,
            "clipped_source_nearest_endpoint_to_model_junction_m":upstream_cut,
            "clipped_target_nearest_endpoint_to_model_junction_m":downstream_cut,
            "classification":"CLIPPED_DISPLAY_GEOMETRY_ENDPOINT_GAP_WITH_MATCHING_ORIGINAL_MODEL_SOURCE_ENDPOINT",
            "hydraulic_connection_field_verified":False
        })
    return {
        "schema_version":SCHEMA,"status":STATUS,
        "study_catchments":20,"reviewed_source_pairs":3,"source_reaches_reviewed":6,
        "original_source_collection_sha256":hashlib.sha256(six).hexdigest(),
        "source_index_sha256":clipped["source_index_sha256"],
        "original_source_manifest_sha256":clipped["source_manifest_sha256"],
        "source":"FAO AQUASTAT Rivers (Global edition 2026), modelled HydroRIVERS network",
        "source_url":"https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87",
        "source_layer":"aquamaps:river_network","source_license":"CC BY 4.0",
        "source_observation_basis":"Six exact uncut WFS GeoJSON model records (retrieval snapshot); verified NEXT_DOWN model IDs",
        "all_three_original_model_endpoint_gaps_zero":True,
        "independent_hydraulic_continuity_verified":False,
        "source_snapshot_path":"research/source_qa/FAO_2026_SIX_ORIGINAL_MODELED_REACHES_NOT_SURVEYED.geojson",
        "cases":published,
        "scientific_notices":[
          "Original source endpoint coincidence diagnoses the clipping-induced distance discrepancy; it does not independently prove in-situ river connectivity.",
          "These three large >500m gaps concern modeled reach display fragments, not measured discontinuities in physical channels.",
          "Clipped simplified geometries can remove full source endpoints. Matched original source endpoints must never be spliced into the public catchment map as invented connectors.",
          "FAO publisher WFS records are model-derived at coarse resolution, not survey-grade or field-verified.",
          "Only three predetermined source pairs were tested; other source topology links were not independently verified.",
          "No change to the 20 original catchments, 52,012 clipped features, dam identities or stakeholder data."
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--six-original",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    generated=generate(args.six_original)
    if args.check:
        if json.loads(args.output.read_text("utf-8"))!=generated:
            raise ValueError("Original modeled geometry reconciliation or public QA drift")
    else:
        if args.output.exists():raise SystemExit("Refuse overwriting publisher original-source QA")
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(generated,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("THREE ORIGINAL FAO 2026 MODELLED ENDPOINT MATCHES: 3/3 at 0 m; field-verified channels: 0")
    for z in generated["cases"]:
        print(z["source_hyriv_id"],"->",z["next_down_hyriv_id"],
              "previous clipped gap",z["clipped_display_min_endpoint_gap_m"],
              "model shared endpoint",z["publisher_modeled_shared_endpoint_lon_lat"])
if __name__=="__main__":main()
