#!/usr/bin/env python3
"""UX-A2 map-first first-viewport layout guard (without changing scientific data)."""
from pathlib import Path
s=(Path(__file__).resolve().parents[1]/'site/index.html').read_text(encoding='utf-8')
assert 'class="hero" aria-label="Atlas introduction"' in s
assert 'Choose a catchment, explore its rivers and boundaries' in s
assert 'height:clamp(570px,calc(100dvh - 180px),970px)' in s
assert '.mapPanel .mapbody{flex:1;min-height:0;height:auto;' in s
assert '.mapPanel{order:1}' in s and '.directory{order:2}' in s
assert "riverDensity='medium'" in s
assert "canvas.setPointerCapture(e.pointerId)" in s
assert "function loadDetailedFor(id)" in s
assert 'id="layerManager"' in s
print('MAP-FIRST HOMEPAGE STATIC QA: PASS')
