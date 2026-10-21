#!/usr/bin/env python3
"""Parse and validate all inline website JavaScript using Node on GitHub Actions."""
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
site=Path(__file__).resolve().parents[1]/'site'/'index.html'
html=site.read_text('utf-8')
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',html,flags=re.I|re.S)
assert len(scripts)==1, f'Expected one inline site script, got {len(scripts)}'
with TemporaryDirectory() as folder:
    f=Path(folder)/'page.mjs'
    f.write_text(scripts[0],encoding='utf-8')
    result=subprocess.run(['node','--check',str(f)],capture_output=True,text=True)
    assert result.returncode==0, result.stderr
assert 'function adminPanel(c)' in html
assert 'administrative=admin' in html
print('BROWSER SCRIPT SYNTAX GATE: PASS')
