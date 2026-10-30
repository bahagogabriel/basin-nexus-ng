#!/usr/bin/env python3
"""UX-B: regional launch, opt-in detailed rivers and return-to-overview contract."""
from pathlib import Path
s=(Path(__file__).resolve().parents[1]/'site/index.html').read_text(encoding='utf-8')
for value in ("riverScope='all',riverDensity='medium'","selected=null;riverScope='all'",
"function showOverview()","function updateRiverScopeUI()",
"el('overviewBtn').addEventListener('click',showOverview)",
"showOverview()).catch","disabled>All catchments</button>","id=\"riverDensity\"",
"Select a catchment to load its FAO 2026 modeled river network",
"renderList();el('catchmentList').scrollTop=0;refreshThemeControls();renderDetails();el('details').scrollTop=0;setView(full)",
"20 strategic catchments · choose a region to explore its rivers",
"Click any catchment on the map","public geographic data"):
 if value=="showOverview()).catch":continue
 if value=="public geographic data":continue
 assert value in s,value
assert "choose('SCMP-C02',false)" not in s
assert "<details class=\"countryLegend\" id=\"countryLegend\">" in s
assert "riverScope='selected';mapMetrics.selected=id" in s
assert "loadDetailedFor(id)" in s
assert "if(!selected)return" in s
print('REGIONAL DEFAULT AND CATCHMENT NAVIGATION GATE: PASS')
