#!/usr/bin/env python3
"""Stages 3D-BK–BN: original SCMP study-area overlap and source-exit screening.

Solely derived from immutable original catchment polygons and SHA256-pinned
FAO AQUASTAT 2026 modeled clipped river geometry / original NEXT_DOWN links.
NOT a mapped outlet, hydrological basin partition, official boundary, or
field-verified upstream/downstream connectivity. No new source data fetching.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math
from collections import Counter,defaultdict
from pathlib import Path
from shapely.geometry import Point,shape
from shapely.ops import transform,nearest_points
from pyproj import Transformer
from build_stage3d_au_av_fao_topology import build as build_graph
from build_stage3d_ay_az_fao_endpoint_qa import endpoints,haversine_m

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"site/data"
SCHEMA="BN_STAGE3D_BK_MODEL_STUDY_AREA_OVERLAP_EXIT_SCREEN_V1"
STATUS="SOURCE_CLIPPED_STUDY_AREA_SCREEN_NOT_VERIFIED_HYDROLOGIC_OUTLETS"
CSV_COLUMNS=("catchment_id","study_area_name","source_hyriv_id","original_next_down_id_or_blank",
             "source_link_class","distance_nearest_clipped_endpoint_to_study_boundary_m",
             "within_250m_screening_band","study_boundary_intersects_source_fragment",
             "hydraulic_outlet_verified")
BAND_M=250.0
MODEL_CLASSES=("NEXT_ID_ONLY_IN_OTHER_STUDY_AREAS","NEXT_ID_OUTSIDE_AVAILABLE_SOURCE_INDEX",
               "SOURCE_TERMINAL_OR_UNLINKED")

def get_geometry(folder):
    raw=(folder/"catchments.geojson").read_bytes()
    manifest=json.loads((folder/"detailed_river_manifest.json").read_text("utf-8"))
    if hashlib.sha256(raw).hexdigest()!=manifest["source_catchment_sha256"]:
        raise ValueError("Original polygon bytes have changed")
    fc=json.loads(raw)
    registry=json.loads((folder/"registry.json").read_text("utf-8"))
    if fc.get("type")!="FeatureCollection" or len(fc.get("features",[]))!=20 or len(registry)!=20:
        raise ValueError("20 original polygons required")
    polygons={}
    for feat in fc["features"]:
        cid=feat["properties"]["id"]
        if cid in polygons:raise ValueError("Duplicate source study-area ID")
        geo=shape(feat["geometry"])
        if not geo.is_valid or geo.is_empty or geo.area<=0:
            raise ValueError("Invalid original study-area shape: "+cid)
        polygons[cid]=geo
    if set(polygons)!={r["id"] for r in registry}:
        raise ValueError("Original study-area identities changed")
    return registry,polygons,manifest

def equal_area_overlaps(registry,polygons):
    ids=[r["id"] for r in registry]
    project=Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True).transform
    proj={cid:transform(project,polygons[cid]) for cid in ids}
    from shapely.ops import unary_union
    union=unary_union(list(proj.values()))
    area={cid:proj[cid].area/1_000_000 for cid in ids}
    pair=[]
    for i,origin in enumerate(ids):
        for destination in ids[i+1:]:
            intersect=proj[origin].intersection(proj[destination])
            overlap=intersect.area/1_000_000 if not intersect.is_empty else 0.0
            if overlap<0:raise ValueError("Negative polygon overlap")
            p={"a":origin,"b":destination,
               "screen_overlap_km2":round(overlap,2),
               "overlap_of_smaller_pct":round(100*overlap/min(area[origin],area[destination]),2),
               "source_polygon_relation":("positive_area_overlap" if overlap>0.000001 else
                   "touching_only" if polygons[origin].intersects(polygons[destination]) else
                   "separate")}
            pair.append(p)
    if len(pair)!=190:raise ValueError("Expected all 190 unordered catchment pairs")
    total=sum(area.values());unique=union.area/1_000_000
    if total<unique or unique<=0:raise ValueError("Overlapping study-area screen not valid")
    per={cid:{"name":next(r["name"] for r in registry if r["id"]==cid),
              "equal_area_polygon_screen_km2":round(area[cid],2),
              "positive_area_overlap_with_other_study_areas":sum(
                 bool(p["screen_overlap_km2"]>0)
                 for p in pair if cid in (p["a"],p["b"])),
              "no_independently_validated_outlet":True} for cid in ids}
    return {"projection":"EPSG:6933 global equal-area area-screening; original WGS84 polygons preserved",
            "screen_sum_catchment_polygon_area_km2":round(total,2),
            "screen_area_unique_union_km2":round(unique,2),
            "screen_area_double_counted_km2":round(total-unique,2),
            "screen_overlap_pair_count":sum(p["source_polygon_relation"]=="positive_area_overlap" for p in pair),
            "study_pair_count":190,
            "per_catchment":per,
            "overlap_pairs":pair}

def build(folder=DATA):
    folder=Path(folder)
    registry,polygons,manifest=get_geometry(folder)
    ids=[r["id"] for r in registry]
    source,graph,bytes_index=build_graph(folder)
    if source!=json.loads((folder/"fao_downstream_summary.json").read_text("utf-8")):
        raise ValueError("Pinned source graph publication differs")
    if bytes_index!=(folder/"fao_downstream_index.json").read_bytes():
        raise ValueError("Pinned graph bytewise identity differs")
    prior=json.loads((folder/"fao_89_catchment_source_boundary_audit.json").read_text("utf-8"))
    if (prior.get("schema_version")!="BN_STAGE3D_BG_FAO_89_SOURCE_BOUNDARY_GEOMETRY_QA_V1"
        or prior.get("source_manifest_sha256")!=source["source_manifest_sha256"]
        or prior.get("source_reach_copies_crossing_selected_catchment_index")!=89):
        raise ValueError("Previous 89-source association QA changed")
    computed_overlap=equal_area_overlaps(registry,polygons)
    ref={fid:(dn,mask) for fid,dn,mask in graph["rows"]}
    model_rows=[]
    per=defaultdict(lambda:Counter())
    for slot,cid in enumerate(ids):
        meta=manifest["files"][cid]
        raw=(folder/meta["file"]).read_bytes()
        if len(raw)!=meta["bytes"] or hashlib.sha256(raw).hexdigest()!=meta["sha256"]:
            raise ValueError("Pinned clipped FAO modeled reach features changed")
        collection=json.loads(raw)
        if len(collection["features"])!=meta["count"]:
            raise ValueError("Unexpected clipped source reach count")
        for f in collection["features"]:
            pr=f["properties"];fid=int(pr["hyriv_id"])
            original_nxt,mask=ref[fid]
            if not mask&(1<<slot):raise ValueError("Feature/source catchment membership changed")
            if original_nxt is None:
                kind="SOURCE_TERMINAL_OR_UNLINKED"
            elif original_nxt not in ref:
                kind="NEXT_ID_OUTSIDE_AVAILABLE_SOURCE_INDEX"
            elif not(ref[original_nxt][1]&(1<<slot)):
                kind="NEXT_ID_ONLY_IN_OTHER_STUDY_AREAS"
            else:continue
            # All candidate records are source-reach screen records, NOT outlets.
            from shapely.geometry import shape as geo_shape
            line=geo_shape(f["geometry"])
            border=polygons[cid].boundary
            pts=endpoints(f["geometry"])
            distances=[]
            for pt in pts:
                nearest=nearest_points(Point(pt),border)[1]
                distances.append(haversine_m(pt,(nearest.x,nearest.y)))
            nearest_m=round(min(distances),1)
            if not math.isfinite(nearest_m) or nearest_m<0 or nearest_m>1_500_000:
                raise ValueError("Screen distance outside source-area budget")
            intersects=line.intersects(border)
            row={"catchment_id":cid,
              "study_area_name":next(r["name"] for r in registry if r["id"]==cid),
              "source_hyriv_id":fid,
              "original_next_down_id_or_blank":original_nxt,
              "source_link_class":kind,
              "distance_nearest_clipped_endpoint_to_study_boundary_m":nearest_m,
              "within_250m_screening_band":nearest_m<=BAND_M,
              "study_boundary_intersects_source_fragment":bool(intersects),
              "hydraulic_outlet_verified":False}
            model_rows.append(row);per[cid][kind]+=1
            if row["within_250m_screening_band"]:per[cid]["within_250m"]+=1
    model_rows.sort(key=lambda x:(x["catchment_id"],x["source_hyriv_id"]))
    actual=Counter(x["source_link_class"] for x in model_rows)
    if actual!=Counter({"NEXT_ID_ONLY_IN_OTHER_STUDY_AREAS":89,
                        "NEXT_ID_OUTSIDE_AVAILABLE_SOURCE_INDEX":32,
                        "SOURCE_TERMINAL_OR_UNLINKED":4}):
        raise ValueError("Model boundary review count drift")
    if len(model_rows)!=125 or len({(r["catchment_id"],r["source_hyriv_id"]) for r in model_rows})!=125:
        raise ValueError("Unexpected cross-area candidate coverage")
    earlier={(x["from_catchment_id"],x["source_hyriv_id"]) for x in prior["source_references"]}
    selected={(x["catchment_id"],x["source_hyriv_id"]) for x in model_rows
              if x["source_link_class"]=="NEXT_ID_ONLY_IN_OTHER_STUDY_AREAS"}
    if selected!=earlier:raise ValueError("89 pinned source-origin references do not reconcile")
    for cid in ids:
        d=source["counts_by_catchment"][cid]
        if (per[cid]["NEXT_ID_ONLY_IN_OTHER_STUDY_AREAS"]!=d["next_down_only_outside_selected_catchment"] or
            per[cid]["NEXT_ID_OUTSIDE_AVAILABLE_SOURCE_INDEX"]!=d["next_down_not_in_20_catchment_index"] or
            per[cid]["SOURCE_TERMINAL_OR_UNLINKED"]!=d["next_down_null_or_source_terminal"]):
            raise ValueError("Per-catchment known source conditions do not reconcile")
        computed_overlap["per_catchment"][cid].update({
          "modeled_boundary_screen_records":sum(per[cid][k] for k in MODEL_CLASSES),
          "next_id_only_in_other_study_areas":per[cid][MODEL_CLASSES[0]],
          "next_id_outside_index":per[cid][MODEL_CLASSES[1]],
          "source_terminal_or_unlinked":per[cid][MODEL_CLASSES[2]],
          "within_250m_of_polygon_border":per[cid]["within_250m"]
          })
    return {"schema_version":SCHEMA,"status":STATUS,
      "provenance_source":"FAO AQUASTAT 2026 modeled original source NEXT_DOWN + SHA256-pinned source SCMP polygons",
      "source_license":"CC BY 4.0 (FAO network); original user-supplied study polygons",
      "catchment_source_sha256":manifest["source_catchment_sha256"],
      "fao_source_manifest_sha256":source["source_manifest_sha256"],
      "source_89_research_count":89,
      "out_of_index_next_id_count":32,
      "null_source_terminal_count":4,
      "source_screen_record_count":125,
      "actual_verified_outlet_count":0,
      "screen_threshold_m":250,
      "screen_overlap":computed_overlap,
      "boundary_exit_lead_records":model_rows,
      "source_method_limits":[
         "These are 20 possibly overlapping study-area polygons, not a validated mutually exclusive watershed partition.",
         "An apparent source link to another polygon is not proof of directional water transfer between complete catchments.",
         "A NEXT_DOWN ID missing outside the 20-study-area index is missing coverage, not necessarily a river outlet.",
         "A source terminal/unlinked record is not an independently surveyed catchment outlet.",
         "A clipped model endpoint within 250 m of a polygon border is a screening lead, not a confirmed channel crossing or outlet.",
         "No candidate point is promoted to a field-verified hydraulic outlet; no new named facility is created.",
         "Area screening is from EPSG:6933 equal-area transformation of unmodified polygons; not official basin area or land area outside other catchments.",
         "No inferred upstream hierarchy, flow rates, travel times, dam walls or private stakeholder records were added."
      ]}
def to_csv(report):
    out=io.StringIO(newline="")
    writer=csv.DictWriter(out,fieldnames=CSV_COLUMNS,lineterminator="\n")
    writer.writeheader()
    for x in report["boundary_exit_lead_records"]:
        writer.writerow({k:("" if x[k] is None else x[k]) for k in CSV_COLUMNS})
    return out.getvalue()
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",required=True,type=Path)
    a.add_argument("--check",action="store_true")
    args=a.parse_args()
    x=build()
    j=args.output/"fao_study_area_overlap_outlet_readiness.json"
    csvf=args.output/"fao_model_boundary_exit_screen_records.csv"
    if args.check:
        if json.loads(j.read_text("utf-8"))!=x or csvf.read_text("utf-8")!=to_csv(x):
            raise ValueError("Screened model research records are stale")
    else:
        if args.output.exists():raise SystemExit("Refuse overwriting previously verified geometry")
        args.output.mkdir(parents=True)
        j.write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n","utf-8")
        csvf.write_text(to_csv(x),"utf-8")
    print("STUDY AREA OVERLAP/OUTLET READINESS SCREEN: 20 study polygons, 190 unordered pairs, 125 model link-boundary leads, 0 verified outlets")
    print("Overlap pairs",x["screen_overlap"]["screen_overlap_pair_count"],
          "double counted area screening km2",x["screen_overlap"]["screen_area_double_counted_km2"],
          "model endpoint within 250m",sum(r["within_250m_screening_band"] for r in x["boundary_exit_lead_records"]))
if __name__=="__main__":main()
