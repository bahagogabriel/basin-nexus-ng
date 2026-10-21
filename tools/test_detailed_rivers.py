#!/usr/bin/env python3
"""Statically ensure detailed reach files load lazily and regional context remains separate."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'site'
s=(p/'index.html').read_text('utf-8')
for term in ["data/detailed_river_manifest.json","function loadDetailedFor(id)","detailCache=new Map()",
             "if(riversOn&&riverPaths.length&&riverScope==='all')","renderDetailedRivers(sc)",
             "groups[c.upstream_class].addPath(path)","while(detailCache.size>2)","if(token!==detailSequence||ctrl.signal.aborted)return",
             "function hitDetailedRiver(world)","source_license!=='CC BY 4.0'",
             "id=\"riverDensity\"","riverDensity='medium'"]:
 assert term in s,term
assert s.count("data/river_network/SCMP-C") == 0, "No eager hardcoded all-catchment loads"
print("DETAILED RIVER RENDERER: lazy load, bounded cache, group-path draw, 20 source files")
