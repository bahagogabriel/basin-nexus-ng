#!/usr/bin/env python3
"""LGA selection must retain precedence while both administrative and water layers are visible."""
from pathlib import Path
s=(Path(__file__).resolve().parents[1]/'site/index.html').read_text('utf-8')
assert 'if(row){activeHydro=null;' in s
assert s.index('if(row){activeHydro=null;')<s.index('if(water){showHydro(water);return}')
assert "if(hydro)name=(hydro.name||'Water feature')" in s
assert "function hitHydro(world)" in s
assert "lakesOn" in s and "riversOn" in s
print('HYDRO/LGA CLICK PRIORITY: PASS')
