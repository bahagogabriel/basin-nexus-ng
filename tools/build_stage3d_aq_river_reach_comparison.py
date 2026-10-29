#!/usr/bin/env python3
"""Stages 3D-AQ/AT: validate/model-only catchment river-reach comparison exports.

Data come ONLY from the pinned, already-published FAO AQUASTAT modeled-reach
manifest and existing catchment registry; this tool does not fetch remote data,
trace upstream/downstream routing, map facilities, or infer surveyed drainage.
"""
from __future__ import annotations
import argparse,csv,io,json,math,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIELDS=("id","name","area_km2","reach_count","small_reaches","medium_reaches",
        "large_reaches","large_share_pct","reaches_per_1000_km2")
CLASSES=("small_upstream_below100","medium_upstream_100plus","large_upstream_1000plus")
SCHEMA="BN_STAGE3D_AQ_CATCHMENT_RIVER_REACH_COMPARISON_V1"

def make(manifest,registry):
    if (not isinstance(manifest,dict) or manifest.get("status")!="PROVISIONAL_DETAILED_RIVER_NETWORK"
        or manifest.get("license")!="CC BY 4.0 (FAO AQUASTAT)"
        or manifest.get("source")!="https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87"
        or manifest.get("layer")!="aquamaps:river_network"
        or manifest.get("version")!="2026-06-15"
        or manifest.get("source_intersecting_unique_reaches")!=51906
        or manifest.get("total_display_reaches")!=52012
        or manifest.get("display_units")!="Individual clipped river reaches, not independently surveyed rivers"
        or not re.fullmatch("[a-f0-9]{64}",manifest.get("source_catchment_sha256",""))):
        raise ValueError("Published FAO river-source baseline changed; no automatic comparison")
    if not isinstance(registry,list) or len(registry)!=20 or not isinstance(manifest.get("files"),dict):
        raise ValueError("Expected exactly 20 existing catchments")
    if set(manifest["files"])!={c.get("id") for c in registry}:
        raise ValueError("River files do not match the original 20 catchments")
    if {c["id"] for c in registry}!={f"SCMP-C{i:02d}" for i in range(1,21)}:
        raise ValueError("A catchment source identity has changed")
    rows=[]
    for c in registry:
        cid=c["id"];meta=manifest["files"][cid];count=meta["count"]
        area=c.get("area_km2")
        if (meta.get("name")!=c.get("name") or meta.get("file")!=f"river_network/{cid}.geojson"
            or not isinstance(count,int) or isinstance(count,bool) or not 0<count<100000
            or type(area) not in (int,float) or not math.isfinite(area) or not 1000<area<200000
            or not re.fullmatch("[a-f0-9]{64}",meta.get("sha256",""))):
            raise ValueError("River count, file or area baseline drift: "+cid)
        classes=meta.get("classes",{})
        if set(classes)!=set(CLASSES) or any(type(classes[k]) is not int or classes[k]<0 for k in CLASSES):
            raise ValueError("Unrecognized source drainage-area classes")
        a,b,d=(classes[k] for k in CLASSES)
        if a+b+d!=count:raise ValueError("Source class sum inconsistent for "+cid)
        rows.append({"id":cid,"name":c["name"],"area_km2":area,"reach_count":count,
            "small_reaches":a,"medium_reaches":b,"large_reaches":d,
            "large_share_pct":round(d/count*100,1),
            "reaches_per_1000_km2":round(count/area*1000,1)})
    if sum(x["reach_count"] for x in rows)!=52012:raise ValueError("Publisher clipped reach total inconsistent")
    return {"schema_version":SCHEMA,
      "status":"MODELLED_SOURCE_REACH_COMPARISON_NOT_A_FIELD_SURVEY",
      "source":"FAO AQUASTAT 2026 modeled river reaches (HydroRIVERS-derived)",
      "source_license":"CC BY 4.0","source_dataset_url":manifest["source"],
      "source_catchment_sha256":manifest["source_catchment_sha256"],
      "underlying_manifest":"detailed_river_manifest.json",
      "total_catchments":20,"clipped_reach_segments":52012,
      "unique_intersecting_source_reaches":51906,
      "metric_notices":[
        "Counts are clipped FAO modeled reach features, not unique named rivers or measured channels.",
        "The density is a count of clipped reaches per 1000 km2 of registered catchment area; not drainage length per area or hydrologic network density.",
        "Large, medium and small are source-upstream-area bands >=1000, 100-999, below 100 km2; not Strahler stream orders.",
        "Catchment size, source segmentation, boundary clipping and missing minor channels affect comparisons; this is not flood, ecological or facility risk ranking.",
        "Some catchments cross national borders. Source points, private engagement claims and dam sites are not included."
      ],
      "rows":rows}

def to_csv(rows):
    out=io.StringIO(newline="")
    writer=csv.DictWriter(out,fieldnames=FIELDS,lineterminator="\n")
    writer.writeheader();writer.writerows(rows)
    return out.getvalue()

def verify(obj,reg,publication,csv_data):
    expected=make(obj,reg)
    if publication!=expected:raise ValueError("Published river comparison does not match original source summary")
    parsed=list(csv.DictReader(io.StringIO(csv_data)))
    if len(parsed)!=20 or any(set(x)!=set(FIELDS) for x in parsed):
        raise ValueError("River comparison CSV rows/columns differ")
    for incoming,expected_row in zip(parsed,expected["rows"]):
        for key in FIELDS:
            if incoming[key]!=str(expected_row[key]):
                raise ValueError("River comparison CSV differs at "+expected_row["id"]+" / "+key)
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--write",action="store_true")
    args=p.parse_args()
    if args.check==args.write:raise SystemExit("Use exactly --write or --check")
    folder=ROOT/"site/data"
    m=json.loads((folder/"detailed_river_manifest.json").read_text("utf-8"))
    r=json.loads((folder/"registry.json").read_text("utf-8"))
    summary=make(m,r)
    json_path=folder/"river_reach_comparison.json"
    csv_path=folder/"river_reach_comparison.csv"
    if args.write:
        if json_path.exists() or csv_path.exists():raise SystemExit("Refuse overwrite; review source changes first")
        json_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        csv_path.write_text(to_csv(summary["rows"]),encoding="utf-8")
    else:
        verify(m,r,json.loads(json_path.read_text("utf-8")),csv_path.read_text("utf-8"))
    print("FAO 2026 modeled river reach comparison: 20 catchments, 52012 clipped reaches, source checks PASS")

if __name__=="__main__":main()
