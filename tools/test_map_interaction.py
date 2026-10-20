#!/usr/bin/env python3
"""Guard the SVG pointer-capture regression that broke polygon selection in v0.5.
This is a static CI safeguard; manual/browser QA still covers real pointer interactions.
"""
from pathlib import Path

html = (Path(__file__).resolve().parents[1] / "site" / "index.html").read_text("utf-8")
assert html.count("e.target.setPointerCapture(e.pointerId)") == 1, "Capture must stay on pressed SVG path"
assert "svg.setPointerCapture(e.pointerId)" not in html, "Capturing on outer SVG redirects polygon clicks"
assert "p.addEventListener('click',()=>{if(!dragged)choose(f.properties.id,true)" in html
assert "p.addEventListener('keydown',e=>{" in html
assert "svg.addEventListener('pointermove',e=>{" in html and "if(dragged){" in html
assert "#mapSvg path.region:focus{outline:none}" in html
assert "#mapSvg path.region:focus-visible{" in html
print("MAP INTERACTION REGRESSION GATE: PASS — polygon click, drag and keyboard controls intact")
