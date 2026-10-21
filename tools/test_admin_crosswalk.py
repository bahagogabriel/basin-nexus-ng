#!/usr/bin/env python3
"""Synthetic overlay regression, including repeated LGA names in different states."""
import importlib.util
from pathlib import Path
from shapely.geometry import box
p=Path(__file__).with_name("stage_admin_crosswalk.py")
spec=importlib.util.spec_from_file_location("admin",p)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
# Synthetic geometries in projected metres.
C=[{"id":"A","name":"A Catchment","geom":box(0,0,2000,1000)},
   {"id":"B","name":"B Catchment","geom":box(2000,0,4000,1000)}]
S=[{"id":"S1","name":"West","geom":box(0,0,2000,1000)},
   {"id":"S2","name":"East","geom":box(2000,0,4000,1000)}]
L=[{"id":"L1","name":"Central","geom":box(0,0,2000,1000)},
   {"id":"L2","name":"Central","geom":box(2000,0,4000,1000)}]
s,l,a,w=mod.overlay(C,S,L)
assert len(s)==2 and len(l)==2
assert len({x["lga_uid"] for x in l})==2
assert {(r["lga_uid"],r["state"]) for r in l}=={("L1","West"),("L2","East")}
assert all(abs(r["outside_nigeria_admin1_km2"])<1e-9 for r in a)
assert all(abs(r["state_coverage_discrepancy_pct"])<1e-9 for r in a)
assert not w
print("SYNTHETIC CROSSWALK: PASS")
