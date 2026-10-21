#!/usr/bin/env python3
"""Provisional catchment × Nigeria state/LGA overlays; QA outputs only.

Source: geoBoundaries Nigeria GRID3 2022 ADM1 (37) and ADM2 (774), CC BY 4.0.
Input: Basin Nexus NG simplified web polygons, *not* full-resolution catchments.
No institutional endorsement; small slivers and international edges are uncertain.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys
import requests
from shapely.geometry import shape
from shapely.ops import transform, unary_union
from shapely import make_valid
from shapely.strtree import STRtree
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data"
OUT = ROOT / "review" / "admin-crosswalk"
PIN = "9469f09"
BASE = "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/" + PIN + "/releaseData/gbOpen/NGA/"
EQUAL_AREA = Transformer.from_crs(4326, 6933, always_xy=True).transform
MIN_AREA_KM2 = 0.25

def get_json(url):
    r = requests.get(url, timeout=120, headers={"User-Agent":"BasinNexusNG-AdminQA/0.1"})
    r.raise_for_status()
    if r.text.lstrip().startswith("version https://git-lfs.github.com"):
        raise RuntimeError("Got git-lfs pointer, not geometry: " + url)
    return r.json(), hashlib.sha256(r.content).hexdigest()

def prepare(features, label, expected):
    assert len(features) == expected, f"{label}: expected {expected}, got {len(features)}"
    out = []
    ids = set()
    for f in features:
        p=f["properties"]
        uid=str(p.get("shapeID") or "")
        name=str(p.get("shapeName") or "").strip()
        assert uid and uid not in ids and name, f"{label}: missing or repeated name/id: {uid}"
        ids.add(uid)
        g=make_valid(shape(f["geometry"]))
        assert not g.is_empty and g.geom_type in ("Polygon","MultiPolygon"), (label,uid,g.geom_type)
        g=make_valid(transform(EQUAL_AREA,g))
        assert g.is_valid and g.area>0
        out.append({"id":uid,"name":name,"geom":g})
    return out

def overlay(catches, states, lgas):
    state_geoms=[x["geom"] for x in states]
    lga_geoms=[x["geom"] for x in lgas]
    state_tree=STRtree(state_geoms)
    lga_tree=STRtree(lga_geoms)
    nigeria=unary_union(state_geoms)
    state_rows=[]; lga_rows=[]; summary=[]; parent_warnings=[]
    parent_of={}
    for li,L in enumerate(lgas):
        neighbors=state_tree.query(L["geom"],predicate="intersects")
        hits=sorted(((L["geom"].intersection(state_geoms[int(i)]).area,int(i)) for i in neighbors),reverse=True)
        if hits and hits[0][0]>0:
            parent_of[li]=hits[0][1]
            fraction=hits[0][0]/L["geom"].area
            if fraction<0.95: parent_warnings.append({"lga_id":L["id"],"name":L["name"],"parent_overlap_pct":round(100*fraction,2)})
        else:
            parent_warnings.append({"lga_id":L["id"],"name":L["name"],"issue":"no containing ADM1"})
    for C in catches:
        cg=C["geom"]; area=cg.area/1e6
        inside=cg.intersection(nigeria).area/1e6
        srow=[]; lrow=[]
        for ix in state_tree.query(cg,predicate="intersects"):
            S=states[int(ix)]
            a=cg.intersection(S["geom"]).area/1e6
            if a>=MIN_AREA_KM2:
                srow.append({"catchment_id":C["id"],"catchment":C["name"],"state_uid":S["id"],"state":S["name"],"intersection_km2":round(a,3),"pct_total_catchment":round(100*a/area,4),"pct_within_nigeria":round(100*a/inside,4) if inside else 0})
        for ix in lga_tree.query(cg,predicate="intersects"):
            i=int(ix);L=lgas[i];a=cg.intersection(L["geom"]).area/1e6
            if a>=MIN_AREA_KM2:
                si=parent_of.get(i)
                S=states[si] if si is not None else None
                lrow.append({"catchment_id":C["id"],"catchment":C["name"],"lga_uid":L["id"],"lga":L["name"],"state_uid":S["id"] if S else "","state":S["name"] if S else "","intersection_km2":round(a,3),"pct_total_catchment":round(100*a/area,4)})
        srow.sort(key=lambda x:(-x["intersection_km2"],x["state"]))
        lrow.sort(key=lambda x:(x["state"],-x["intersection_km2"],x["lga"]))
        state_rows.extend(srow);lga_rows.extend(lrow)
        ssum=sum(v["intersection_km2"] for v in srow)
        lsum=sum(v["intersection_km2"] for v in lrow)
        summary.append({"catchment_id":C["id"],"catchment":C["name"],"catchment_area_km2":round(area,2),"within_nigeria_admin1_km2":round(inside,2),"outside_nigeria_admin1_km2":round(max(0,area-inside),2),"outside_pct_admin1_approx":round(max(0,100*(area-inside)/area),2),"state_count":len(srow),"lga_count":len(lrow),"state_coverage_discrepancy_pct":round(100*(ssum-inside)/area,3),"lga_coverage_discrepancy_pct":round(100*(lsum-inside)/area,3)})
    return state_rows,lga_rows,summary,parent_warnings

def save_csv(path,rows):
    if not rows: raise RuntimeError("Empty overlay table "+str(path))
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    catchments=json.loads((DATA/"catchments.geojson").read_text("utf-8"))["features"]
    assert len(catchments)==20
    C=[]
    for f in catchments:
        g=make_valid(transform(EQUAL_AREA,shape(f["geometry"])))
        assert g.is_valid and not g.is_empty
        C.append({"id":f["properties"]["id"],"name":f["properties"]["name"],"geom":g})
    meta={}
    admins={}
    for lvl,n in [("ADM1",37),("ADM2",774)]:
        url=BASE+lvl+"/geoBoundaries-NGA-"+lvl+"_simplified.geojson"
        obj,sha=get_json(url)
        assert obj["type"]=="FeatureCollection"
        admins[lvl]=prepare(obj["features"],lvl,n)
        meta[lvl]={"url":url,"sha256":sha,"unit_count":len(admins[lvl])}
    s,l,summary,parent_warnings=overlay(C,admins["ADM1"],admins["ADM2"])
    save_csv(OUT/"catchment_states_PROVISIONAL.csv",s)
    save_csv(OUT/"catchment_lgas_PROVISIONAL.csv",l)
    save_csv(OUT/"catchment_administrative_coverage_QA.csv",summary)
    meta["catchment_geojson_sha256"]=hashlib.sha256((DATA/"catchments.geojson").read_bytes()).hexdigest()
    meta.update({"study_scope":"Primarily northern Nigeria, some transboundary portions","source":"geoBoundaries gbOpen, GRID3-derived Nigeria admin boundaries represented as 2022; CC BY 4.0","license":"CC BY 4.0 attribution required","crs_area":"EPSG:6933","minimum_intersection_km2":MIN_AREA_KM2,"publication":"HOLD: provisional pending source and accuracy review","parent_warnings_count":len(parent_warnings),"parent_warnings":parent_warnings[:50],"total_state_intersections":len(s),"total_lga_intersections":len(l)})
    (OUT/"provenance_and_QA.json").write_text(json.dumps(meta,indent=2)+"\n","utf-8")
    assert len(summary)==20 and all(x["state_count"]>=1 and x["lga_count"]>=1 for x in summary),"Some catchments have no admin intersections"
    assert all(abs(x["state_coverage_discrepancy_pct"])<1 for x in summary),"State overlay diverges from union >1%"
    assert all(abs(x["lga_coverage_discrepancy_pct"])<3 for x in summary),"LGA overlay diverges from ADM1 union >3%"
    print("CROSSWALK QA: 20 catchments / 37 states-FCT / 774 LGAs")
    print(f"Provisional crossings: {len(s)} state rows; {len(l)} LGA rows")
    print("ADM2 parent irregularities:",len(parent_warnings))
    for row in summary:
        print(row["catchment_id"],row["catchment"],"states="+str(row["state_count"]),"LGAs="+str(row["lga_count"]),"outside%="+str(row["outside_pct_admin1_approx"]),"state-discrepancy%="+str(row["state_coverage_discrepancy_pct"]),"lga-discrepancy%="+str(row["lga_coverage_discrepancy_pct"]))
    print("NOT PUBLICATION APPROVAL — review attached CSV, source and QA warnings")

if __name__=="__main__":
    main()
