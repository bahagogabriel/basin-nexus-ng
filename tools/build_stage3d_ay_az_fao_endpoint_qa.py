#!/usr/bin/env python3
"""Stages 3D-AY–BB: FAO 2026 *modeled geometry* endpoint-separation QA.

Original HydroRIVERS-derived NEXT_DOWN IDs describe source associations. For
each linked source pair, this finds the MINIMUM great-circle distance between
endpoints of AVAILABLE CLIPPED geometry parts, across the 20 study catchments.

Endpoint proximity is NOT topological validation, directed hydraulic flow,
a surveyed meeting point, positional accuracy or a proof of physical contact.
Clipping can manufacture endpoints or obscure original reach continuations.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path
from build_stage3d_au_av_fao_topology import build as source_build

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"site/data"
SCHEMA="BN_STAGE3D_AY_FAO_CLIPPED_ENDPOINT_GAP_QA_V1"
INDEX_SCHEMA="BN_STAGE3D_AZ_FAO_ENDPOINT_GAPS_LOOKUP_V1"
SOURCE_STATUS="MODELLED_CLIPPED_GEOMETRY_DIAGNOSTIC_NOT_PHYSICAL_CONNECTIVITY"
BANDS=("endpoint_le_50m","endpoint_50_to_500m","endpoint_gt_500m",
       "next_id_not_in_index","source_terminal_or_unlinked")
MAX_COORDS_PER_PART=15000
MAX_ENDPOINTS_PER_ID=120
MAX_LOOKUP_BYTES=1_950_000

def haversine_m(a,b):
    """WGS84 spherical screening approximation; do not report survey accuracy."""
    lon1,lat1=a;lon2,lat2=b
    dlat=math.radians(lat2-lat1);dlon=math.radians(lon2-lon1)
    x=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 6371008.8*2*math.asin(min(1,math.sqrt(max(0,x))))

def endpoints(geometry):
    if not isinstance(geometry,dict):raise ValueError("Missing source line geometry")
    t=geometry.get("type")
    if t=="LineString": parts=[geometry.get("coordinates")]
    elif t=="MultiLineString":parts=geometry.get("coordinates")
    else:raise ValueError("Unsupported publisher clipped river geometry: "+str(t))
    if not isinstance(parts,list) or not parts or len(parts)>60:
        raise ValueError("Unbounded clipped lineparts")
    out=[]
    for part in parts:
        if not isinstance(part,list) or not 2<=len(part)<=MAX_COORDS_PER_PART:
            raise ValueError("Invalid clipped river segment")
        ends=[]
        for item in (part[0],part[-1]):
            if not isinstance(item,(list,tuple)) or len(item)<2:raise ValueError("Bad source coordinate")
            a,b=item[:2]
            if (type(a) not in (int,float) or type(b) not in (int,float)
                or not math.isfinite(a) or not math.isfinite(b) or not -180<=a<=180 or not -90<=b<=90):
                raise ValueError("Bad clipped source coordinate")
            ends.append((float(a),float(b)))
        out+=ends
    return out

def separation_m(a,b):
    if not a or not b:raise ValueError("No clipped source endpoints to compare")
    return min(haversine_m(p,q) for p in a for q in b)

def band(gap_m):
    if gap_m is None:return "next_id_not_in_index"
    if gap_m<=50:return "endpoint_le_50m"
    if gap_m<=500:return "endpoint_50_to_500m"
    return "endpoint_gt_500m"

def build(folder=DATA):
    folder=Path(folder)
    source_summary,source_index,_=source_build(folder)
    original_source_index=(folder/"fao_downstream_index.json").read_bytes()
    original_summary=json.loads((folder/"fao_downstream_summary.json").read_text("utf-8"))
    if (source_summary!=original_summary
        or json.loads(original_source_index)!=source_index):
        raise ValueError("Original source-linked index has not passed prior scientific gate")
    registry=json.loads((folder/"registry.json").read_text("utf-8"))
    manifest=json.loads((folder/"detailed_river_manifest.json").read_text("utf-8"))
    ids=[x["id"] for x in registry]
    positions=defaultdict(list)
    per_catchment={}
    for cid in ids:
        meta=manifest["files"][cid]
        fc=json.loads((folder/meta["file"]).read_bytes())
        pairs={}
        for f in fc["features"]:
            prop=f["properties"]
            fid=int(prop["hyriv_id"]);dn=prop.get("next_down")
            down=int(dn) if dn not in (None,0,"0") else None
            if fid in pairs:raise ValueError("Repeated clipped original source ID inside catchment")
            pairs[fid]=down
            pts=endpoints(f["geometry"])
            if len(positions[fid])+len(pts)>MAX_ENDPOINTS_PER_ID:
                raise ValueError("Source ID has excessive clipped endpoints")
            positions[fid].extend(pts)
        if len(pairs)!=meta["count"]:raise ValueError("Endpoint source count drift")
        per_catchment[cid]=pairs
    graph={fid:next_id for fid,next_id,mask in source_index["rows"]}
    if len(positions)!=len(graph) or set(positions)!=set(graph):
        raise ValueError("Missing original source geometries")
    gap={}
    for fid,next_id in graph.items():
        gap[fid]=(separation_m(positions[fid],positions[next_id])
                  if next_id in positions else None)
    tally={cid:Counter() for cid in ids}
    for cid,pairs in per_catchment.items():
        for fid,next_id in pairs.items():
            category=("source_terminal_or_unlinked" if next_id is None else band(gap[fid]))
            tally[cid][category]+=1
        if sum(tally[cid].values())!=source_summary["counts_by_catchment"][cid]["clipped_reaches"]:
            raise ValueError("One or more modeled reach copies missing from geometry QA")
    pair_metrics=defaultdict(lambda:Counter())
    source_rows={fid:(n,mask) for fid,n,mask in source_index["rows"]}
    for slot,cid in enumerate(ids):
        for fid,dn in per_catchment[cid].items():
            if dn is None or dn not in source_rows:continue
            mask=source_rows[dn][1]
            if mask&(1<<slot):continue
            for j,dest in enumerate(ids):
                if mask&(1<<j):pair_metrics[(cid,dest)][band(gap[fid])]+=1
    pair_summary=[]
    for row in source_summary["cross_catchment_source_link_pairs"]:
        src,dst,n=row["from"],row["to"],row["source_next_down_links"]
        metrics=pair_metrics[(src,dst)]
        if sum(metrics.values())!=n:
            raise ValueError("Cross-catchment original NEXT_DOWN count drift")
        pair_summary.append({"from":src,"to":dst,"source_link_copies":n,
          "endpoint_le_50m":metrics["endpoint_le_50m"],
          "endpoint_50_to_500m":metrics["endpoint_50_to_500m"],
          "endpoint_gt_500m":metrics["endpoint_gt_500m"]})
    allcounts=Counter()
    for stats in tally.values():allcounts.update(stats)
    if sum(allcounts.values())!=52012 or len(pair_summary)!=33:
        raise ValueError("Modelled source geometry coverage failed")
    summary={"schema_version":SCHEMA,"status":SOURCE_STATUS,
       "source":"FAO AQUASTAT 2026 HydroRIVERS-derived clipped 15-arcsecond modeled river geometry",
       "license":"CC BY 4.0",
       "source_manifest_sha256":source_summary["source_manifest_sha256"],
       "source_index_sha256":hashlib.sha256(original_source_index).hexdigest(),
       "unique_source_ids":len(graph),"clipped_reach_copies":52012,
       "geometry_screening_method":"MINIMUM_ENDPOINT_TO_ENDPOINT_GREAT_CIRCLE_METERS_OVER_CLIPPED_SEGMENTS_NOT_FLOW_DIRECTION",
       "distance_rounding_m":1,
       "classification_bands_m":[50,500],
       "total_clipped_source_link_classification":dict(allcounts),
       "by_catchment":{cid:{"name":source_summary["counts_by_catchment"][cid]["name"],
                          "clipped_reaches":source_summary["counts_by_catchment"][cid]["clipped_reaches"],
                          **{key:tally[cid][key] for key in BANDS}}
                       for cid in ids},
       "cross_catchment_source_link_pair_geometry_screen":pair_summary,
       "limitations":[
           "Close clipped endpoints are not independently verified river topology or proof of hydraulic continuity.",
           "A large endpoint gap is not proof that model source IDs are incorrect: source features are clipped, truncated or coarse.",
           "Minimum distance across clipped endpoints is a SCREENING statistic only; it is not field uncertainty or positional accuracy.",
           "Near, far and close thresholds are transparent descriptive bins, not accuracy tolerances or confidence ratings.",
           "Direction of geometry vertices and NEXT_DOWN flow direction are not independently reconciled.",
           "No upstream basin delineation, travel time, flood risk, water availability or dam-site confirmation is inferred.",
       ]}
    index={"schema_version":INDEX_SCHEMA,"status":SOURCE_STATUS,
           "source_manifest_sha256":summary["source_manifest_sha256"],
           "source_index_sha256":summary["source_index_sha256"],
           "license":"CC BY 4.0",
           "row_fields":["source_hyriv_id","endpoint_min_gap_m_or_null"],
           "rows":[[fid,round(gap[fid],1) if gap[fid] is not None else None] for fid in sorted(gap)]}
    compact=json.dumps(index,separators=(",",":"),ensure_ascii=True).encode("utf-8")
    if len(compact)>MAX_LOOKUP_BYTES:
        raise ValueError("Geometry gap lookup exceeds safe browser budget")
    return summary,index,compact

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    summary,index,compact=build()
    s=a.output/"fao_endpoint_gap_summary.json"
    g=a.output/"fao_endpoint_gap_index.json"
    if a.check:
        if json.loads(s.read_text("utf-8"))!=summary or g.read_bytes()!=compact:
            raise ValueError("Existing publisher-geometry QA is stale or changed")
    else:
        if a.output.exists():raise SystemExit("Refuse overwriting existing geometry QA data")
        a.output.mkdir(parents=True)
        s.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
        g.write_bytes(compact)
    print("Stage AY–AZ modeled endpoint screening:",summary["total_clipped_source_link_classification"],
          "cross-catchment pair types",len(summary["cross_catchment_source_link_pair_geometry_screen"]),
          "index bytes",len(compact))
if __name__=="__main__":main()
