#!/usr/bin/env python3
"""Stages 3D-BG–BJ: source-locked 89 NEXT_DOWN cross-catchment references.

Audit *clipped modeled geometry* and existing study-polygon intersections.
Neither the FAO source reach direction nor proximity of clipped segments
independently demonstrates catchment-wide upstream/downstream hydraulic flow.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import nearest_points

from build_stage3d_au_av_fao_topology import build as source_build
from build_stage3d_ay_az_fao_endpoint_qa import haversine_m

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site/data"
SCHEMA = "BN_STAGE3D_BG_FAO_89_SOURCE_BOUNDARY_GEOMETRY_QA_V1"
STATUS = "MODELED_SOURCE_ASSOCIATION_AND_CLIPPED_POLYGON_SCREEN_NOT_VERIFIED_FLOW"
CSV_FIELDS = (
    "from_catchment_id","source_hyriv_id","original_next_down_id",
    "next_id_catchments","destination_memberships","source_id_memberships",
    "closest_destination_catchment_id","closest_clipped_line_gap_m",
    "closest_study_polygon_relationship","original_source_endpoint_gap_m",
    "review_status",
)
STATUS_LABEL = "SOURCE_RECORD_AND_CLIPPED_GEOMETRY_SCREEN_ONLY"

def _relation(a, b):
    """An area overlap is not necessarily a hydrological catchment transfer."""
    if a.intersection(b).area > 1e-10:
        return "overlapping_study_polygons"
    if a.intersects(b):
        return "boundaries_touch_or_intersect"
    return "spatially_separate_study_polygons"

def _nearest_model_gap(a, b):
    """Screening: closest pair in lon-lat plane, distance via spherical haversine."""
    u, v = nearest_points(a, b)
    m = haversine_m((u.x,u.y),(v.x,v.y))
    if not math.isfinite(m) or not 0 <= m < 2_000_000:
        raise ValueError("Unexpected modeled clip-to-clip separation")
    return round(m,1)

def build(folder=DATA):
    folder=Path(folder)
    existing, graph, _ = source_build(folder)
    if existing["source_cycle_members"]!=0 or existing["unique_source_reach_ids"]!=51906:
        raise ValueError("Prior source graph changed")
    source_summary=json.loads((folder/"fao_downstream_summary.json").read_text("utf-8"))
    source_index=json.loads((folder/"fao_downstream_index.json").read_text("utf-8"))
    if existing!=source_summary or graph!=source_index:
        raise ValueError("Original source graph is not current")
    manifest=json.loads((folder/"detailed_river_manifest.json").read_text("utf-8"))
    original_polygons=(folder/"catchments.geojson").read_bytes()
    if hashlib.sha256(original_polygons).hexdigest()!=manifest["source_catchment_sha256"]:
        raise ValueError("The 20 original study-area polygons changed")
    boundaries=json.loads(original_polygons)
    registry=json.loads((folder/"registry.json").read_text("utf-8"))
    ids=[r["id"] for r in registry]
    if len(ids)!=20 or len(set(ids))!=20:
        raise ValueError("Expected the original 20 SCMP identities")
    polygons={f["properties"]["id"]:shape(f["geometry"]) for f in boundaries["features"]}
    if set(polygons)!=set(ids) or any(
       p.is_empty or not p.is_valid or p.area<=0 for p in polygons.values()
    ):
        raise ValueError("Unvalidated source catchment polygons")
    source={id:(nxt,mask) for id,nxt,mask in source_index["rows"]}
    if len(source)!=51906:raise ValueError("Source index deduplication changed")
    transition=[]
    needed=defaultdict(set)
    for i,cid in enumerate(ids):
        for fid,(nxt,mask) in source.items():
            if not mask & (1<<i) or nxt is None or nxt not in source:
                continue
            dst_mask=source[nxt][1]
            if dst_mask & (1<<i):continue
            targets=[ids[j] for j in range(20) if dst_mask & (1<<j)]
            if not targets:raise ValueError("Unindexed target incorrectly treated as cross-catchment")
            transition.append((cid,fid,nxt,targets,mask,dst_mask))
            needed[cid].add(fid)
            for target in targets:needed[target].add(nxt)
    transition.sort(key=lambda x:(x[0],x[1],x[2]))
    if len(transition)!=89:
        raise ValueError("The expected 89 source-clip associations changed")
    reach_parts={}
    by_catch=Counter()
    for cid in ids:
        info=manifest["files"][cid]
        content=(folder/info["file"]).read_bytes()
        if len(content)!=info["bytes"] or hashlib.sha256(content).hexdigest()!=info["sha256"]:
            raise ValueError("Original pinned clipped FAO source geometry changed")
        fc=json.loads(content)
        if len(fc["features"])!=info["count"]:
            raise ValueError("Clipped feature count changed")
        found=set()
        for f in fc["features"]:
            fid=int(f["properties"]["hyriv_id"])
            if fid not in needed[cid]:continue
            if fid in found:raise ValueError("Duplicate source ID in one catchment")
            found.add(fid)
            if f["geometry"]["type"] not in ("LineString","MultiLineString"):
                raise ValueError("Unexpected clipped modeled reach type")
            geom=shape(f["geometry"])
            if geom.is_empty or not geom.is_valid or geom.length<=0:
                raise ValueError("Invalid clipped modeled river fragment")
            reach_parts[(cid,fid)]=geom
        if found!=needed[cid]:
            raise ValueError("Needed source ID fragment missing in "+cid)
    old_gap=dict(json.loads((folder/"fao_endpoint_gap_index.json").read_text("utf-8"))["rows"])
    report=[]
    pair_count=Counter()
    relation_count=Counter()
    target_multiplicity=0
    for cid,fid,nxt,targets,src_mask,dst_mask in transition:
        from_geom=reach_parts[(cid,fid)]
        options=[]
        for target in targets:
            geom=reach_parts[(target,nxt)]
            relation=_relation(polygons[cid],polygons[target])
            gap=_nearest_model_gap(from_geom,geom)
            options.append({"target_catchment_id":target,
               "study_polygon_relationship":relation,
               "min_clipped_line_to_line_gap_m":gap})
            relation_count[relation]+=1
            pair_count[(cid,target)]+=1
        options.sort(key=lambda o:(o["min_clipped_line_to_line_gap_m"],o["target_catchment_id"]))
        closest=options[0]
        if len(options)>1:target_multiplicity+=1
        src_members=sum(bool(src_mask & (1<<i)) for i in range(20))
        published_gap=old_gap.get(fid)
        if published_gap is None or not math.isfinite(published_gap):
            raise ValueError("Source geometry gap index lacks original linked ID")
        row={"from_catchment_id":cid,
             "from_catchment_name":next(x["name"] for x in registry if x["id"]==cid),
             "source_hyriv_id":fid,"original_next_down_id":nxt,
             "source_id_memberships":src_members,
             "destination_memberships":len(targets),
             "next_id_catchments":targets,
             "closest_destination_catchment_id":closest["target_catchment_id"],
             "closest_clipped_line_gap_m":closest["min_clipped_line_to_line_gap_m"],
             "closest_study_polygon_relationship":closest["study_polygon_relationship"],
             "all_target_study_polygon_screens":options,
             "original_source_endpoint_gap_m":published_gap,
             "review_status":STATUS_LABEL}
        report.append(row);by_catch[cid]+=1
    expected={(x["from"],x["to"]):x["source_next_down_links"]
              for x in source_summary["cross_catchment_source_link_pairs"]}
    if pair_count!=expected:
        raise ValueError("Expected 33 source-association pair counts did not reconcile")
    if sum(by_catch.values())!=89 or len(pair_count)!=33:
        raise ValueError("Source/geometry cross-catchment review totals invalid")
    pairs=[{"from":cid,"to":dest,
            "source_reference_count":count,
            "from_name":next(x["name"] for x in registry if x["id"]==cid),
            "to_name":next(x["name"] for x in registry if x["id"]==dest),
            "study_polygon_relationship":_relation(polygons[cid],polygons[dest]),
            "not_independent_flow_confirmation":True}
           for (cid,dest),count in sorted(pair_count.items())]
    summary={
        "schema_version":SCHEMA,"status":STATUS,
        "source":"FAO AQUASTAT 2026 HydroRIVERS-derived modeled river network",
        "source_license":"CC BY 4.0",
        "source_catalogue_url":"https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87",
        "source_manifest_sha256":existing["source_manifest_sha256"],
        "source_graph_sha256":hashlib.sha256((folder/"fao_downstream_index.json").read_bytes()).hexdigest(),
        "catchment_polygon_source_sha256":manifest["source_catchment_sha256"],
        "source_reach_copies_crossing_selected_catchment_index":89,
        "unique_cross_catchment_source_association_pairs":33,
        "reference_memberships_across_target_catchments":sum(pair_count.values()),
        "target_ids_in_multiple_other_catchments":target_multiplicity,
        "geometry_method":"Shapely closest points on existing clipped model lines in WGS84, screening great-circle distance; polygons may overlap",
        "distance_units":"metres, rounded 0.1; modeled geometry screening only",
        "polygon_relationship_reference_counts":dict(sorted(relation_count.items())),
        "per_catchment":{cid:{"name":next(x["name"] for x in registry if x["id"]==cid),
            "source_links_to_other_study_catchments":by_catch[cid]}
            for cid in ids},
        "pair_aggregates":pairs,"source_references":report,
        "scientific_limitations":[
            "This is a study-area membership analysis of the original FAO NEXT_DOWN graph; it is not whole-catchment downstream order.",
            "The 89 rows are source-reach copies; source IDs may occur in several study catchments and 33 directed pair types may include reciprocal associations.",
            "Source IDs pointing to multiple study catchments count once per originating catchment, but contribute multiple target membership records.",
            "Study polygons may overlap and are simplified; mapped proximity or polygon intersection is not observed hydraulic flow.",
            "The nearest distance is a screening distance between clipped modeled LINE fragments, not a directed, geodesically optimized travel path or survey uncertainty.",
            "Uncut publisher geometry was authenticated earlier ONLY for three specific clipped gap pairs, not for all these 89 references.",
            "No field-verified channel crossings, flood travel time, flow rate, dam site or private stakeholder information is inferred."
        ]}
    return summary

def to_csv(summary):
    out=io.StringIO(newline="")
    writer=csv.DictWriter(out,fieldnames=CSV_FIELDS,lineterminator="\n")
    writer.writeheader()
    for row in summary["source_references"]:
        writer.writerow({k:(";".join(row[k]) if k=="next_id_catchments" else row[k]) for k in CSV_FIELDS})
    return out.getvalue()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    expected=build()
    j=a.out/"fao_89_catchment_source_boundary_audit.json"
    c=a.out/"fao_89_catchment_source_boundary_audit.csv"
    if a.check:
        if json.loads(j.read_text("utf-8"))!=expected or c.read_text("utf-8")!=to_csv(expected):
            raise ValueError("Published modeled source boundary QA is stale or corrupted")
    else:
        if a.out.exists():raise SystemExit("Refuse to replace previous independent source QA")
        a.out.mkdir(parents=True)
        j.write_text(json.dumps(expected,ensure_ascii=False,indent=2)+"\n","utf-8")
        c.write_text(to_csv(expected),"utf-8")
    print("FAO modeled cross-catchment source membership QA:",
          "source rows",len(expected["source_references"]),
          "33 directed catchment-pair types; total target memberships",
          expected["reference_memberships_across_target_catchments"],
          "relationship screens",expected["polygon_relationship_reference_counts"])
if __name__=="__main__":
    main()
