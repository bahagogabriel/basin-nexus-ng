#!/usr/bin/env python3
"""3D-BC–BF: six targeted original FAO 2026 WFS records, no bulk re-download.

Query ONLY 3 exact HYRIV_ID/NEXT_DOWN pairs previously established from 20
SHA-locked FAO clips. This is public-source model topology QA, NOT a surveyed
river, hydraulic continuity proof, or approved dam. Never silently substitute
HydroRIVERS from another year, or reuse simplified clipped geometry as source.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import argparse, hashlib, json, math, time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"site/data"
WFS="https://data.apps.fao.org/map/gsrv/gsrv1/aquamaps/wfs"
DOI="https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87"
EXPECTED=((10505946,10506074,"SCMP-C19",10983.5),
          (10566530,10567236,"SCMP-C04",4805.2),
          (10568272,10568127,"SCMP-C19",4885.1))
SCHEMA="BN_STAGE3D_BC_ORIGINAL_FAO_REACH_PAIR_AUDIT_V1"
INPUTS=tuple(sorted({n for a,b,_,_ in EXPECTED for n in (a,b)}))
MAX_RESPONSE_BYTES=300_000
LIMIT_WFS_FEATURES=3
POINT_CAP=2000

def haversine(a,b):
    la1,lo1=math.radians(a[1]),math.radians(a[0])
    la2,lo2=math.radians(b[1]),math.radians(b[0])
    dlat=la2-la1;dlon=lo2-lo1
    k=math.sin(dlat/2)**2+math.cos(la1)*math.cos(la2)*math.sin(dlon/2)**2
    return 6371008.8*2*math.asin(min(1,math.sqrt(max(0,k))))

def lines(feature):
    if not isinstance(feature,dict):raise ValueError("Expected FAO WFS feature dict")
    geom=feature.get("geometry")
    if not isinstance(geom,dict):raise ValueError("Source has no geometric response")
    if geom.get("type")=="LineString":parts=[geom.get("coordinates")]
    elif geom.get("type")=="MultiLineString":parts=geom.get("coordinates")
    else:raise ValueError("Source is not original LineString/MultiLineString")
    if not isinstance(parts,list) or not parts or len(parts)>20:raise ValueError("Unbounded source geometry parts")
    checked=[]
    total=0
    for seg in parts:
        if not isinstance(seg,list) or not 2<=len(seg)<=POINT_CAP:raise ValueError("Unbounded line geometry")
        coords=[]
        for p in seg:
            if not isinstance(p,(list,tuple)) or len(p)<2:raise ValueError("Invalid WFS point")
            a,b=p[:2]
            if type(a) not in (int,float) or type(b) not in (int,float) or not math.isfinite(a) or not math.isfinite(b) or not -180<=a<=180 or not -90<=b<=90:
                raise ValueError("Source longitude or latitude invalid")
            coords.append((float(a),float(b)))
        total+=len(coords);checked.append(coords)
    if total>POINT_CAP:raise ValueError("WFS record geometry too large for narrow research")
    return checked

def validate_feature(raw, requested):
    props=raw.get("properties")
    if not isinstance(props,dict) or str(props.get("hyriv_id"))!=str(requested):
        raise ValueError("Source WFS HYRIV_ID not the requested original ID")
    parts=lines(raw)
    nxt=props.get("next_down")
    if nxt is not None:
        try:nxt=int(nxt)
        except (ValueError,TypeError):raise ValueError("Unexpected NEXT_DOWN")
    if len(str(requested))>12 or requested not in INPUTS:raise ValueError("Request outside approved review queue")
    return {"id":requested,"next_down":nxt,"parts":parts,
            "source_property_keys":sorted(props),"geometry_type":raw["geometry"]["type"]}

def bounded_get(id, retries=3, opener=urlopen, sleep=time.sleep):
    if id not in INPUTS:raise ValueError("Disallowed unbounded WFS source query")
    params={"service":"WFS","version":"1.1.0","request":"GetFeature",
        "typeName":"aquamaps:river_network","outputFormat":"application/json",
        "srsName":"EPSG:4326","cql_filter":f"hyriv_id={id}",
        "maxFeatures":LIMIT_WFS_FEATURES}
    url=WFS+"?"+urlencode(params)
    for attempt in range(retries):
        try:
            response=opener(Request(url,headers={"User-Agent":"BasinNexusNG-model-source-audit/1.0","Accept":"application/json"}),timeout=55)
            with response:
                b=response.read(MAX_RESPONSE_BYTES+1)
                if len(b)>MAX_RESPONSE_BYTES:raise ValueError("WFS source response exceeds bounded size")
            data=json.loads(b)
            if not isinstance(data,dict) or data.get("type")!="FeatureCollection":
                raise ValueError("Expected publisher GeoJSON FeatureCollection, not WFS exception")
            items=data.get("features")
            if not isinstance(items,list) or len(items)!=1:
                raise ValueError(f"Expected exactly 1 original FAO WFS reach for {id}, found {len(items) if isinstance(items,list) else 'invalid'}")
            return validate_feature(items[0],id),items[0],hashlib.sha256(b).hexdigest()
        except (OSError,ValueError,HTTPError,URLError) as err:
            if attempt==retries-1:raise
            sleep(1+attempt*2)
    raise RuntimeError("WFS retry exhaustion")

def closest_endpoints(parts1,parts2):
    a=[p for seg in parts1 for p in (seg[0],seg[-1])]
    b=[p for seg in parts2 for p in (seg[0],seg[-1])]
    gap,p,q=min((haversine(p,q),p,q) for p in a for q in b)
    return round(gap,1),[list(p),list(q)]

def oriented_distance(parts1,parts2):
    # Vertex ordering might not equal hydraulic flow direction; screening ONLY.
    return round(min(haversine(a[-1],b[0]) for a in parts1 for b in parts2),1)

def source_bbox(parts):
    allpts=[pt for seg in parts for pt in seg]
    return [round(min(x for x,y in allpts),7),round(min(y for x,y in allpts),7),
            round(max(x for x,y in allpts),7),round(max(y for x,y in allpts),7)]

def source_reconciliation(records,clipped_gap,topology):
    require={id for pair in EXPECTED for id in pair[:2]}
    if set(records)!=require:raise ValueError("Original six WFS records incomplete")
    if clipped_gap.get("schema_version")!="BN_STAGE3D_AY_FAO_CLIPPED_ENDPOINT_GAP_QA_V1":
        raise ValueError("Stage AY clipped source provenance changed")
    if topology.get("schema_version")!="BN_STAGE3D_AU_FAO_TOPOLOGY_SUMMARY_V1":
        raise ValueError("Source graph provenance changed")
    if clipped_gap.get("source_manifest_sha256")!=topology.get("source_manifest_sha256"):
        raise ValueError("Source summary digest mismatch")
    report=[]
    for upstream,downstream,cid,prevgap in EXPECTED:
        a,b=records[upstream],records[downstream]
        if a["next_down"]!=downstream:raise ValueError("Original FAO NEXT_DOWN fails source-clip identity: "+str(upstream))
        gap,endpoints=closest_endpoints(a["parts"],b["parts"])
        # Grounded in the old clipped original QA, NOT supposed to be equal to unclipped gap.
        report.append({"catchment_id":cid,"source_hyriv_id":upstream,
         "next_down_hyriv_id":downstream,
         "prior_clipped_min_endpoint_gap_m":prevgap,
         "original_uncut_min_endpoint_gap_m":gap,
         "original_uncut_oriented_end_to_start_m_NOT_FLOW_PROOF":oriented_distance(a["parts"],b["parts"]),
         "uncut_closer_than_prior_clips":gap<prevgap,
         "near_endpoint_pair_lon_lat":endpoints,
         "upstream_source_bbox_wgs84":source_bbox(a["parts"]),
         "next_source_bbox_wgs84":source_bbox(b["parts"]),
         "interpretation":"ORIGINAL_MODEL_GEOMETRY_SCREENING_ONLY_NOT_VERIFIED_HYDRAULIC_CONTINUITY"})
    return {"schema_version":SCHEMA,
       "status":"ORIGINAL_PUBLISHER_MODEL_GEOMETRY_QA_NOT_SURVEYED",
       "publisher_dataset":DOI,"original_source_wfs":WFS,
       "source_model_version":"2026-06-15","source_license":"CC BY 4.0",
       "reference_source_manifest_sha256":topology["source_manifest_sha256"],
       "source_index_sha256":clipped_gap["source_index_sha256"],
       "targeted_original_reaches":len(records),
       "source_pair_count":len(report),
       "source_gap_pairs":report,
       "scope_limits":[
          "Only six exact published FAO source IDs were queried. No unbounded WFS discovery or replacement of approved clipped river files.",
          "WFS can be updated by publisher: response hashes and source property lists retained for traceability, not historical immutability proof.",
          "Uncut source-endpoint separation can reduce clipping artefacts, but close model geometry is not independently verified hydraulic continuity.",
          "Vertex orientation is not independently verified as downstream flow; end-to-start distances are diagnostic only.",
          "Original geographic positions are publisher modeled features, not survey-grade or independently verified positions.",
          "No impact, travel time, new dams, flow simulation or changes to the original 20 catchment boundary files."
       ]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",required=True,type=Path)
    a=ap.parse_args()
    if a.output_dir.exists():raise SystemExit("Refuse overwrite of any existing original-source review")
    a.output_dir.mkdir(parents=True)
    records,features,digests={},{},{}
    for n in INPUTS:
        rec,raw,digest=bounded_get(n)
        records[n]=rec;features[n]=raw;digests[n]=digest
        print("FETCH EXACT PUBLISHER SOURCE",n,"NEXT_DOWN",rec["next_down"],"points",sum(len(seg) for seg in rec["parts"]),flush=True)
    clipped=json.loads((DATA/"fao_endpoint_gap_summary.json").read_text("utf-8"))
    topology=json.loads((DATA/"fao_downstream_summary.json").read_text("utf-8"))
    report=source_reconciliation(records,clipped,topology)
    report["wfs_single_response_sha256_by_id"]={str(n):digests[n] for n in sorted(digests)}
    report["source_field_names_by_id"]={str(n):records[n]["source_property_keys"] for n in sorted(digests)}
    rawout=a.output_dir/"ORIGINAL_FAO_SIX_REACHES_WFS_SOURCE_ONLY.geojson"
    rawout.write_text(json.dumps({"type":"FeatureCollection","name":"SIX_ORIGINAL_FAO_WFS_MODEL_REACHES_NOT_SURVEYED",
                                 "features":[features[n] for n in sorted(features)]},separators=(",",":"))+"\n")
    report["six_feature_collection_sha256"]=hashlib.sha256(rawout.read_bytes()).hexdigest()
    (a.output_dir/"ORIGINAL_UNCLIPPED_THREE_PAIRS_RESEARCH_ONLY.json").write_text(json.dumps(report,indent=2)+"\n")
    for q in report["source_gap_pairs"]:
        print("MODEL QA",q["source_hyriv_id"],q["next_down_hyriv_id"],
              "clipped_m",q["prior_clipped_min_endpoint_gap_m"],"full_model_m",q["original_uncut_min_endpoint_gap_m"],
              "NOT physical continuity",flush=True)

if __name__=="__main__":main()
