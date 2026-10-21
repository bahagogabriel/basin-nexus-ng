#!/usr/bin/env python3
"""UX-A: map controls grouping, legend, focus and responsive layout must exist."""
from pathlib import Path
site=Path(__file__).resolve().parents[1]/"site"/"index.html"
s=site.read_text(encoding="utf-8")
for marker in ('class="mapbar"','class="layerManager" id="layerManager"','<summary aria-label="Open map layer settings">',
               'class="layerSection"','id="focusMapBtn"','id="overviewBtn"','id="mapActiveSummary"',
               '<details class="countryLegend" id="countryLegend">',
               'class="legendContent"','riverDensity=\'medium\'',
               "el('focusMapBtn').addEventListener('click',focusSelected)",
               "el('layerManager').addEventListener('keydown'","document.addEventListener('pointerdown'",
               '@media(max-width:980px)','@media(max-width:620px)',
               'Catchment geography and modelled rivers'):
    assert marker in s,marker
assert s.count('id="riverScopeToggle"')==1
assert s.count('id="riverDensity"')==1
assert s.count('id="expandBtn"')==1
assert s.count('id="lgaToggle"')==1
assert s.count('id="countryLegend"')==1
assert 'selected catchment' in s
print('UX-A STRUCTURAL CONTRACT: PASS')
