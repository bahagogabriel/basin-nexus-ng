#!/usr/bin/env python3
"""Build map-display ADM1/ADM2 geometry, not analytical boundary measurements.

Pinned geoBoundaries Nigeria GRID3 2022 via gbOpen (CC BY 4.0).
The 2022 source ADM2 sample is restricted to LGAs actually intersecting one
of the 20 catchments; all 37 ADM1 states/FCT are included for orientation.
No data from confidential stakeholder documents is accessed here.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import requests
from shapely.geometry import mapping, shape
from shapely import make_valid
from shapely.ops import transform
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site" / "data"
OUT = ROOT / "review" / "admin-map-layers"
PIN = "9469f09"
BASE = f"https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/{PIN}/releaseData/gbOpen/NGA"
FORWARD = Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True).transform
BACK = Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True).transform

def get_layer(level: str, expected_count: int):
    url = f"{BASE}/{level}/geoBoundaries-NGA-{level}_simplified.geojson"
    r = requests.get(url, timeout=180, headers={"User-Agent":"BasinNexusNG/0.8"})
    r.raise_for_status()
    b=r.content
    if b.startswith(b"version https://git-lfs.github.com"):
        raise RuntimeError("Git LFS pointer returned; no actual geometry")
    data=json.loads(b)
    assert data["type"]=="FeatureCollection"
    assert len(data["features"])==expected_count,(level,len(data["features"]))
    return data,{"url":url,"sha256":hashlib.sha256(b).hexdigest(),"source_count":expected_count}

def polygon_only(g):
    g=make_valid(g)
    if g.geom_type in ("Polygon","MultiPolygon"): return g
    polys=[x for x in getattr(g,"geoms",[]) if x.geom_type in ("Polygon","MultiPolygon")]
    if not polys: raise ValueError("Polygon repairs produced no polygon component")
    from shapely.ops import unary_union
    return unary_union(polys)

def output_features(data, allowed_ids, tolerance_m, expected_count, level, parent_lookup=None):
    found=set(); result=[]; max_delta=0.
    for f in data["features"]:
        p=f["properties"]; fid=str(p.get("shapeID",""));name=str(p.get("shapeName","")).strip()
        if not fid or not name: raise ValueError(f"Missing id/name in {level}")
        if fid not in allowed_ids:continue
        if fid in found: raise ValueError(f"Duplicate ID: {fid}")
        found.add(fid)
        raw=polygon_only(transform(FORWARD,shape(f["geometry"])))
        simp=polygon_only(raw.simplify(tolerance_m,preserve_topology=True))
        delta=100*abs(simp.area-raw.area)/raw.area
        max_delta=max(max_delta,delta)
        assert simp.is_valid and not simp.is_empty, (level,fid)
        assert delta<5, (level,fid,"area_delta_pct",round(delta,3))
        props={"id":fid,"name":name}
        if parent_lookup is not None:
            props["state_id"]=parent_lookup[fid]
        result.append({"type":"Feature","properties":props,"geometry":mapping(transform(BACK,simp))})
    assert found==allowed_ids,(level,"missing IDs",list(allowed_ids-found)[:10])
    assert len(result)==expected_count,(level,len(result),expected_count)
    result.sort(key=lambda f:(f["properties"]["name"],f["properties"]["id"]))
    return {"type":"FeatureCollection","name":f"basin_nexus_ng_{level}_provisional_web","features":result},max_delta

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cross=json.loads((SITE/"admin_crosswalk_provisional.json").read_text("utf-8"))
    assert cross["status"]=="PROVISIONAL_GEOMETRIC_OVERLAY" and cross["totalCatchments"]==20
    state_ids={s["id"] for c in cross["byCatchment"].values() for s in c["states"]}
    parent={}
    for c in cross["byCatchment"].values():
        for l in c["lgas"]:
            if l["id"] in parent and parent[l["id"]]!=l["stateId"]:
                raise ValueError("LGA assigned conflicting states: "+l["id"])
            parent[l["id"]]=l["stateId"]
    st,sm=get_layer("ADM1",37)
    lg,lm=get_layer("ADM2",774)
    if sm["sha256"]!=cross["sourceHashADM1"] or lm["sha256"]!=cross["sourceHashADM2"]:
        raise ValueError("Pinned source hash differs from Stage2C administrative crosswalk source")
    all_state_ids={str(f["properties"].get("shapeID","")) for f in st["features"]}
    assert len(all_state_ids)==37 and state_ids.issubset(all_state_ids)
    assert set(parent.values()).issubset(all_state_ids)
    states,delta_s=output_features(st,all_state_ids,250,37,"ADM1")
    lgas,delta_l=output_features(lg,set(parent),175,len(parent),"ADM2",parent)
    # QA: LGA parent IDs must match one of the source states; IDs must be unique.
    assert all(f["properties"]["state_id"] in all_state_ids for f in lgas["features"])
    report={"status":"PROVISIONAL_MAP_GEOMETRY","source":"GRID3 Nigeria boundaries via geoBoundaries gbOpen (2022), CC BY 4.0",
      "release_pin":PIN,"adm1":sm,"adm2":lm,"adm1_features":37,
      "study_intersecting_adm2_features":len(parent),"full_source_adm2_features":774,
      "state_simplify_tolerance_m":250,"lga_simplify_tolerance_m":175,
      "max_state_area_delta_pct":round(delta_s,5),
      "max_lga_area_delta_pct":round(delta_l,5),
      "area_method":"EPSG:6933; display only",
      "warning":"Display boundaries only: source derived from 2022 GRID3, not official 2026 legal or cadastral boundaries. Percentages in profiles calculated independently from original source overlap, NOT these simplified paths."}
    for file,obj in [("adm1_states_provisional.geojson",states),("adm2_lgas_study_provisional.geojson",lgas),("admin_map_layer_QA.json",report)]:
        (OUT/file).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    for path in sorted(OUT.iterdir()):
        print("OUTPUT",path.name,path.stat().st_size,"bytes")
if __name__=="__main__":main()
