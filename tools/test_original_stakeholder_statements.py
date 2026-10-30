#!/usr/bin/env python3
"""S18 contract: all primary communiqués and linked Shared Vision statements."""
import json,re
from collections import Counter
from pathlib import Path
base=Path(__file__).resolve().parents[1]/"site"
d=json.loads((base/"data/stakeholder_source_detail.json").read_text(encoding="utf-8"))
registry=json.loads((base/"data/registry.json").read_text(encoding="utf-8"))
assert d["schema_version"]=="BN_ORIGINAL_STAKEHOLDER_STATEMENTS_V1"
assert len(d["documents"])==37 and len(d["catchments"])==len(registry)==20
assert len(d["entries"])==3277
assert {c["id"] for c in d["catchments"]}=={c["id"] for c in registry}
assert sum(c["total"] for c in d["catchments"])==3277
assert sum(c["communique"] for c in d["catchments"])==1654
assert sum(c["vision"] for c in d["catchments"])==1623
assert sum(x["s"]=="vision_resources" for x in d["entries"])>=300
assert sum(x["s"]=="vision_challenges" for x in d["entries"])>=150
assert sum(x["s"]=="vision_priorities" for x in d["entries"])>=50
assert all(isinstance(x["p"],int) and x["p"]>0 and 0<=x["d"]<37 and x["t"] for x in d["entries"])
assert all(not re.search(r"(?i)signature\s*(?:&|and|/)\s*date|\b\w+@\w+\.\w+\b|\+234\d{10}",x["t"]) for x in d["entries"])
counts=Counter(x["c"] for x in d["entries"])
assert all(counts[c["id"]]==c["total"] for c in d["catchments"])
def text_for(cid):
 return " ".join(x["t"] for x in d["entries"] if x["c"]==cid).lower()
assert "soya beans in danko lga" in text_for("SCMP-C04")
assert "ngaski lga has lithium" in text_for("SCMP-C04")
assert "monazite" in text_for("SCMP-C03") and "kanam lga" in text_for("SCMP-C03")
assert "tin & columbite" in text_for("SCMP-C02")
assert "maize" in text_for("SCMP-C20")
html=(base/"index.html").read_text(encoding="utf-8")
assert "renderOriginalStatementsPanel(c)" in html and "updateOriginalStatementList()" in html
assert 'function renderOccurrenceList(c)' in html and 'allOccurrenceRecords()' in html
assert "sourceResourcesFor(c.id,'all')" in html
assert "originalStakeholderStatements" in html and "data-profile-target=\"originalStakeholderStatements\"" in html
assert json.loads((base/"data/public_evidence_catalogue.json").read_text())["records"]==[]
print("S18 PASS: 20 catchments, 1,654 communiqué + 1,623 Shared Vision statements, no false zero-resource labels")
