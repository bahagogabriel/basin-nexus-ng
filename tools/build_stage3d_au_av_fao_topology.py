#!/usr/bin/env python3
"""Stages 3D-AU–AX: source-locked FAO reach NEXT_DOWN connectivity exploration.

Never infer hydraulic continuity, travel time, surveyed channels, floods or dams.
A downstream link is ONLY an original publisher NEXT_DOWN identifier; reach
geometry is clipped to catchment polygons and may not spatially meet neighbors.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from collections import Counter,defaultdict

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"site/data"
SUMMARY="BN_STAGE3D_AU_FAO_TOPOLOGY_SUMMARY_V1"
INDEX="BN_STAGE3D_AV_FAO_TOPOLOGY_LOOKUP_V1"
PUBLISHER="FAO AQUASTAT 2026 HydroRIVERS-derived modeled network"
CLASSES={"small_upstream_below100","medium_upstream_100plus","large_upstream_1000plus"}
TOTAL_FEATURES=52012
UNIQUE_IDS=51906
MAX_INDEX_BYTES=1_950_000

def _identifier(value,allow_unlinked=False):
    if value is None and allow_unlinked:return None
    if not isinstance(value,(str,int)) or isinstance(value,bool) or not re.fullmatch(r"\d{1,12}",str(value)):
        raise ValueError("Source HYRIV_ID/NEXT_DOWN must be an unsigned decimal ID")
    n=int(value)
    if allow_unlinked and n==0:return None
    if n<1:raise ValueError("Invalid source HYRIV_ID")
    return n

def _cycles(graph):
    """Functional directed graph; return only members of loops (not their ancestors)."""
    status={}
    members=set()
    for start in graph:
        if status.get(start):continue
        path=[];onpath={};cur=start
        while cur in graph and not status.get(cur) and cur not in onpath:
            onpath[cur]=len(path);path.append(cur)
            cur=graph[cur] if graph[cur] is not None else -1
        if cur in onpath:
            members.update(path[onpath[cur]:])
        for node in path:status[node]=1
    return members

def build(folder=SOURCE):
    folder=Path(folder)
    manifest_bytes=(folder/"detailed_river_manifest.json").read_bytes()
    registry=json.loads((folder/"registry.json").read_text("utf-8"))
    manifest=json.loads(manifest_bytes)
    if (manifest.get("status")!="PROVISIONAL_DETAILED_RIVER_NETWORK"
        or manifest.get("source_intersecting_unique_reaches")!=UNIQUE_IDS
        or manifest.get("total_display_reaches")!=TOTAL_FEATURES
        or manifest.get("license")!="CC BY 4.0 (FAO AQUASTAT)"
        or not isinstance(registry,list) or len(registry)!=20
        or not isinstance(manifest.get("files"),dict) or len(manifest["files"])!=20):
        raise ValueError("Publisher-modeled reach manifest or copyright contract drift")
    ordered=[r["id"] for r in registry]
    if set(ordered)!={f"SCMP-C{i:02d}" for i in range(1,21)} or len(set(ordered))!=20:
        raise ValueError("Catchment identities changed")
    if set(manifest["files"])!=set(ordered):raise ValueError("Missing 20 modeled river files")
    known={} # HYRIV_ID -> (int NEXT_DOWN or None, 20-bit catchment mask)
    local=defaultdict(dict)
    counts=Counter()
    for slot,cid in enumerate(ordered):
        row=manifest["files"][cid]
        if row["file"]!=f"river_network/{cid}.geojson" or row["name"]!=registry[slot]["name"]:
            raise ValueError("Named source catchment or file mismatch")
        raw=(folder/row["file"]).read_bytes()
        if len(raw)!=row["bytes"] or hashlib.sha256(raw).hexdigest()!=row["sha256"]:
            raise ValueError("Pinned FAO GeoJSON byte/source hash drift: "+cid)
        fc=json.loads(raw)
        if (fc.get("type")!="FeatureCollection"
            or fc.get("properties",{}).get("catchment_id")!=cid
            or len(fc.get("features",[]))!=row["count"]):
            raise ValueError("Clipped source feature collection modified")
        class_counts=Counter()
        for feature in fc["features"]:
            if not isinstance(feature,dict):raise ValueError("Unexpected feature")
            prop=feature.get("properties") or {}
            fid=_identifier(prop.get("hyriv_id"))
            nxt=_identifier(prop.get("next_down"),allow_unlinked=True)
            if (prop.get("id")!=f"{cid}_{fid}"
                or prop.get("source_license")!="CC BY 4.0"
                or prop.get("is_clipped_to_catchment") is not True
                or prop.get("upstream_class") not in CLASSES):
                raise ValueError("Source-scoped reach ID, license or model class changed")
            if fid in local[cid]:raise ValueError("Duplicate source reach within catchment")
            if fid==nxt:raise ValueError("Self-link in publisher NEXT_DOWN field")
            class_counts[prop["upstream_class"]]+=1
            local[cid][fid]=nxt
            if fid in known:
                prev,mask=known[fid]
                if prev!=nxt:raise ValueError("Publisher downstream ID inconsistent across catchment clips")
                known[fid]=(nxt,mask|(1<<slot))
            else:known[fid]=(nxt,1<<slot)
            counts[cid]+=1
        if counts[cid]!=row["count"] or dict(class_counts)!=row["classes"]:
            raise ValueError("Publisher source class/count totals drift")
    if len(known)!=UNIQUE_IDS or sum(counts.values())!=TOTAL_FEATURES:
        raise ValueError("Unexpected original FAO source graph coverage")
    graph={fid:dn for fid,(dn,mask) in known.items()}
    loops=_cycles(graph)
    source_edges={cid:Counter() for cid in ordered}
    per={}
    missing_examples=[]
    for slot,cid in enumerate(ordered):
        same=outbound=missing=explicit_terminal=multi=0
        for fid,down in local[cid].items():
            if down is None:
                explicit_terminal+=1;continue
            if down not in known:
                missing+=1
                if len(missing_examples)<12:missing_examples.append([cid,fid,down])
                continue
            target=known[down][1]
            if target&(1<<slot):same+=1
            else:
                outbound+=1
                dest=[ordered[k] for k in range(20) if target&(1<<k)]
                if len(dest)>1:multi+=1
                for other in dest:source_edges[cid][other]+=1
        per[cid]={"name":registry[slot]["name"],"clipped_reaches":counts[cid],
            "next_down_within_same_catchment":same,
            "next_down_only_outside_selected_catchment":outbound,
            "next_down_not_in_20_catchment_index":missing,
            "next_down_null_or_source_terminal":explicit_terminal,
            "outbound_targets_with_multiple_catchment_memberships":multi}
        if same+outbound+missing+explicit_terminal!=counts[cid]:
            raise ValueError("Source downstream classification not exhaustive")
    transitions=[{"from":a,"to":b,"source_next_down_links":n}
      for a in ordered for b,n in source_edges[a].most_common() if n>0]
    transitions.sort(key=lambda x:(x["from"],x["to"]))
    index={"schema_version":INDEX,
       "status":"SOURCE_NEXT_DOWN_REFERENCE_ONLY_NOT_TOPOLOGICALLY_VERIFIED",
       "source":"FAO AQUASTAT 2026 modeled 15 arcsecond HydroRIVERS-derived reaches",
       "license":"CC BY 4.0",
       "source_manifest_sha256":hashlib.sha256(manifest_bytes).hexdigest(),
       "catchment_ids":ordered,
       "row_fields":["original_source_hyriv_id","original_next_down_id_or_null","catchment_membership_bitmask"],
       "rows":[[fid,dn,mask] for fid,(dn,mask) in sorted(known.items())]}
    compressed=json.dumps(index,separators=(",",":"),ensure_ascii=True).encode("utf-8")
    if len(compressed)>MAX_INDEX_BYTES:
        raise ValueError(f"Source connectivity index exceeds publication size budget: {len(compressed)}")
    summary={"schema_version":SUMMARY,
      "status":"RESEARCH_ONLY_ORIGINAL_SOURCE_LINKS_NO_INDEPENDENT_CONNECTIVITY_PROOF",
      "source":PUBLISHER,"license":"CC BY 4.0",
      "publisher_source":"https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87",
      "source_manifest_sha256":index["source_manifest_sha256"],
      "unique_source_reach_ids":len(known),"clipped_catchment_reach_copies":TOTAL_FEATURES,
      "source_ids_in_multiple_catchments":sum(mask.bit_count()>1 for _,mask in known.values()),
      "source_cycle_members":len(loops),
      "source_cycle_example_ids":sorted(loops)[:10],
      "counts_by_catchment":per,"cross_catchment_source_link_pairs":transitions,
      "unresolved_next_down_example_ids":missing_examples,
      "important_limitations":[
        "NEXT_DOWN is an original FAO/HydroRIVERS modeled reach identifier, not independently verified channel connectivity.",
        "A downstream identifier outside these 20 catchment clips is unresolved, never assumed to terminate a river.",
        "The same original reach may intersect more than one catchment, and duplicated clipped reach copies are not separate rivers.",
        "Cross-catchment source references are candidate links only; geographic adjacency, network geometry and hydraulic continuity are NOT verified.",
        "Only bounded downstream source-ID walks are supported; no upstream catchment accumulation, reach length, travel time, dam/water quality or flood impact is inferred."
       ]}
    return summary,index,compressed

def _load(folder):
    return (folder/"fao_downstream_summary.json",folder/"fao_downstream_index.json")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    summary,index,compact=build()
    a,b=_load(args.output)
    if args.check:
        if json.loads(a.read_text("utf-8"))!=summary or b.read_bytes()!=compact:
            raise ValueError("Published source graph or summary differs from existing FAO inputs")
    else:
        if args.output.exists():raise SystemExit("Refuse to overwrite existing topology review folder")
        args.output.mkdir(parents=True)
        a.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
        b.write_bytes(compact)
    print("Stage AU–AV source-only graph: unique",summary["unique_source_reach_ids"],
          "clipped",summary["clipped_catchment_reach_copies"],
          "shared",summary["source_ids_in_multiple_catchments"],
          "source cycle members",summary["source_cycle_members"],
          "edges",len(summary["cross_catchment_source_link_pairs"]),
          "index bytes",len(compact))
if __name__=="__main__":main()
