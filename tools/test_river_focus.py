#!/usr/bin/env python3
"""Keep catchment river focus optional and map-scale claims qualified."""
from pathlib import Path
s=(Path(__file__).resolve().parents[1]/"site/index.html").read_text("utf-8")
assert 'id="riverScopeToggle"' in s
assert "riverScope='selected'" in s
assert "clipCatch=riverScope==='selected'?catchPaths.get(selected):null" in s
assert "ctx.clip(clipCatch.path,'evenodd')" in s
assert "function riverAllowedAt(world)" in s
assert "if(riversOn&&riverAllowedAt(world))" in s
assert "mapMetrics.riverScope=riverScope" in s
assert "incomplete network" in s
assert "must not be interpreted as having no streams" in s
assert "canvas.setPointerCapture(e.pointerId)" in s
print("CATCHMENT RIVER FOCUS REGRESSION: PASS")
