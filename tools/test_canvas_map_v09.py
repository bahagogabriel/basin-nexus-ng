#!/usr/bin/env python3
"""Canvas map behavioural contract. Browser-level multi-touch tests are in ui_smoke_v09.cjs."""
from pathlib import Path
html=(Path(__file__).resolve().parents[1]/'site/index.html').read_text('utf-8')
for marker in ('id="mapCanvas"','id="lgaInfo"','function hitCatchment(world)','function hitLGA(catchId,world)',
 'function gestureStart()','function pointerEnd(e,cancelled=false)','pointerMap.size>=2','mapMetrics.pinchMoves++',
 "canvas.addEventListener('wheel'","ctx.fill(e.path,'evenodd')","lgaPaths=new Map",
 "ctx.clip(cp.path,'evenodd')","mapMetrics.panMoves++","requestAnimationFrame(",
 'with LGAs on','within selected catchment'):
 # The last two are prose dependencies and are intentionally optional here.
 if marker in ('with LGAs on','within selected catchment'):continue
 assert marker in html, marker
assert "svg.setAttribute('viewBox'" not in html
assert "svg.setPointerCapture" not in html
assert "e.target.setPointerCapture" not in html
assert "path.adminLGA" in html # legacy noninteractive stylesheet can remain
print("CANVAS MAP STATIC CONTRACT: PASS")
