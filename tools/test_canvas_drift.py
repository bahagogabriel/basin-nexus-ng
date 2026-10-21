#!/usr/bin/env python3
"""Canvas layout-drift prevention contract for desktop and tablet browsers."""
from pathlib import Path
html=(Path(__file__).resolve().parents[1]/'site/index.html').read_text('utf-8')
assert '.mapbody canvas{position:absolute;inset:0;display:block;' in html
assert 'max-width:100%;max-height:100%' in html
assert 'new ResizeObserver(entries=>' in html
assert 'if(w===lastWidth&&h===lastHeight)return' in html
assert "canvas.setPointerCapture(e.pointerId)" in html
assert "canvas.addEventListener('pointerup',e=>pointerEnd(e))" in html
assert "canvas.addEventListener('pointercancel',e=>pointerEnd(e,true))" in html
assert "requestAnimationFrame(" in html
assert "overscroll-behavior:contain" in html
print('CANVAS LAYOUT STABILITY STATIC GATE: PASS')
