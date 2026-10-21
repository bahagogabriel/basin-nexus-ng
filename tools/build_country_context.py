#!/usr/bin/env python3
"""Recalculate provisional border crossing against public-boundary data.

Dependencies (local development only): shapely, pyproj.
Sources: user-supplied (simplified) catchments + Natural Earth Admin0 1:110m.
NOT a surveyed international border; use results as map-scale QA only.
"""
import json
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
site=Path(__file__).resolve().parents[1]/"site"/"data"
country=json.loads((site/"nigeria_boundary.geojson").read_text())
catchments=json.loads((site/"catchments.geojson").read_text())
project=Transformer.from_crs(4326,6933,always_xy=True).transform
nigeria=transform(project,shape(country["features"][0]["geometry"]))
out=[]
for f in catchments["features"]:
    catchment=transform(project,shape(f["geometry"]))
    outside=100*catchment.difference(nigeria).area/catchment.area
    out.append({"id":f["properties"]["id"],"outside_pct_indicative":round(outside,1),"outside_pct_unrounded":outside,
                "classification":"extends_beyond_nigeria" if outside>0.5 else "within_nigeria_at_map_scale"})
report=json.loads((site/"international_context.json").read_text())
report["coverage"]=out
report["extension_count_indicative"]=sum(r["classification"]=="extends_beyond_nigeria" for r in out)
report["total_catchments"]=len(out)
(site/"international_context.json").write_text(json.dumps(report,indent=2)+"\n")
print("Provisional catchments crossing Nigeria (1:110m):",report["extension_count_indicative"])
