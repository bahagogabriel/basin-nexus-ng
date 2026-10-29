#!/usr/bin/env python3
"""Validate the single inline atlas JavaScript plus allowed external climate module."""
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
root=Path(__file__).resolve().parents[1]
html=(root/'site'/'index.html').read_text('utf-8')
scripts=re.findall(r'(<script\b[^>]*>)(.*?)</script>',html,flags=re.I|re.S)
inline=[body for tag,body in scripts if not re.search(r'\bsrc\s*=',tag,flags=re.I)]
external=[tag for tag,body in scripts if re.search(r'\bsrc\s*=',tag,flags=re.I)]
assert len(inline)==1, f'Expected exactly one inline app script, got {len(inline)}'
assert len(external)==1 and re.search(r'\bsrc\s*=\s*["\']climate\.js["\']',external[0],flags=re.I), 'Unreviewed external app scripts'
with TemporaryDirectory() as folder:
    for name,source in [('page.mjs',inline[0]),('climate.mjs',(root/'site'/'climate.js').read_text('utf-8'))]:
        target=Path(folder)/name
        target.write_text(source,encoding='utf-8')
        result=subprocess.run(['node','--check',str(target)],capture_output=True,text=True)
        assert result.returncode==0, f'{name}: {result.stderr}'
assert 'function adminPanel(c)' in html
assert 'administrative=admin' in html
print('ATLAS INLINE + EXTERNAL CLIMATE SCRIPT SYNTAX GATE: PASS')
