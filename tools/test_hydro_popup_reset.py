#!/usr/bin/env python3
"""Selecting a new catchment clears any stale water-feature popup."""
from pathlib import Path
s=(Path(__file__).resolve().parents[1]/'site/index.html').read_text()
assert "function choose(id,zoom){" in s
assert "if(selected!==id){" in s
assert "activeHydro=null;activeLGA=null" in s
assert "el('hydroInfo').classList.add('hidden');el('lgaInfo').classList.add('hidden')" in s
assert "function showOverview(){" in s
assert "selected=null;riverScope='all'" in s
assert "if(water){showHydro(water);return}" in s
print("STALE WATER POPUP: PASS")
