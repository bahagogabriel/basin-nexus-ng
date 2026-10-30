#!/usr/bin/env python3
"""Keep catchment river focus optional and map-scale claims qualified."""
from pathlib import Path
s=(Path(__file__).resolve().parents[1]/"site/index.html").read_text("utf-8")
assert 'id="riverScopeToggle"' in s
assert "riverScope='all'" in s
assert "riverScope='selected';mapMetrics.selected=id" in s
assert "renderDetailedRivers(sc)" in s
assert "if(riversOn&&riverPaths.length&&riverScope==='all')" in s
assert "function riverAllowedAt(world)" in s
assert "if(riversOn&&riverScope==='all'&&riverAllowedAt(world))" in s
assert "mapMetrics.riverScope=riverScope" in s
assert "FAO AQUASTAT river reaches are modelled" in s
assert "not surveyed channels" in s
assert "not a complete survey" in s
assert "canvas.setPointerCapture(e.pointerId)" in s
print("CATCHMENT RIVER FOCUS REGRESSION: PASS")
