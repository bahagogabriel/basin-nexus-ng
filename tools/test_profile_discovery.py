#!/usr/bin/env python3
"""UX-C1: map hints, directory sync and profile section navigation."""
from pathlib import Path
s=(Path(__file__).resolve().parents[1]/'site/index.html').read_text(encoding='utf-8')
for marker in (
 'function keepSelectedVisible(){','keepSelectedVisible()','if(previousSelection!==id)',
 "el('catchmentList').scrollTop=0",'id="mapHint"',
 'summary aria-label="Show map instructions"','id="mapNote"',
 'class="profileViews"','data-profile-view="overview"',
 'data-profile-view="resources"','id="statesLGAs"',
 'id="profileRivers"','id="profileAdmin"','id="profileOccurrences"',
 "el('details').addEventListener('click'","el('details').scrollTop=0"
):assert marker in s,marker
assert s.count('id="mapHint"')==1
assert s.count('id="mapNote"')==1
assert s.count('function choose(id,zoom)')==1
print('PROFILE DISCOVERY / MAP OVERLAY QA: PASS')
