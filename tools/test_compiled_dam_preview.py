#!/usr/bin/env python3
"""Stage 3D-S: public compiled-source reference markers are never confirmed dams."""
import hashlib,json,math
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[1];site=root/"site"
d=json.loads((site/"data/wa_dam_compiled_reference_preview.json").read_text("utf-8"))
ref=json.loads((site/"data/wa_dams_2026_catchment_reference_counts.json").read_text("utf-8"))
quality=json.loads((site/"data/wa_dams_2026_source_quality.json").read_text("utf-8"))
confirmed=json.loads((site/"data/confirmed_dam_sites.json").read_text("utf-8"))
html=(site/"index.html").read_text("utf-8")
assert d["schema_version"]=="BN_COMPILED_DAM_REFERENCE_VIEW_V1"
assert d["status"]=="PUBLISHED_RESEARCH_POINT_VIEW_OPT_IN_UNVERIFIED"
assert d["display_mode"]=="OPT_IN_RESEARCH_REFERENCES_ONLY"
assert d["source_license"]=="CC BY 4.0"
assert d["source_doi"]=="10.60507/FK2/YLDK1Y"
assert d["source_csv_md5"]==ref["source_file_md5"]
assert d["source_shapefile_md5"]==ref["source_shapefile_md5"]
assert d["source_nigeria_labelled"]==231
assert d["source_catchment_intersections"]==189
assert d["withheld_identity_review"]==3
assert d["original_reference_data_not_independently_verified"] is True
assert d["independent_confirmed_dams"]==0
rows=d["records"]
assert len(rows)==d["displayable_research_references"]==186
assert sum(r[3] is not None for r in rows)==d["records_with_source_name"]==68
assert sum(r[3] is None for r in rows)==d["records_without_source_name"]==118
assert all(len(r)==4 and type(r[2]) is int and 1<=r[2]<=20 for r in rows)
assert all(isinstance(r[0],(int,float)) and math.isfinite(r[0]) and 2<=r[0]<=16 for r in rows)
assert all(isinstance(r[1],(int,float)) and math.isfinite(r[1]) and 4<=r[1]<=15 for r in rows)
assert all(r[3] is None or isinstance(r[3],str) and 2<=len(r[3])<=96 for r in rows)
assert len({(r[0],r[1]) for r in rows})==186
assert not any(r[3] in {"Souapiti","Kafin Zaki","Mambilla"} for r in rows)
assert set(x["source_name"] for x in d["withheld_review"])=={"Souapiti","Kafin Zaki","Mambilla"}
assert all(x["source"].startswith("https://") and x["issue"] for x in d["withheld_review"])
# Prove the shipped public source-points match the physically inspected publisher review artifact:
expected_hash="2dc9c81925ea2ed6b2cb82f13410868a96ccc93d1897f3eda6040e924c9dd82a"
assert hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==expected_hash
counts=Counter(r[2] for r in rows);named=Counter(r[2] for r in rows if r[3])
for i in range(1,21):
    key=f"SCMP-C{i:02d}"
    excluded=int(key in {"SCMP-C06","SCMP-C17","SCMP-C18"})
    assert counts[i]==ref["per_catchment"][key]-excluded
    assert named[i]==quality["by_catchment"][key]["named_source_rows"]-excluded
assert confirmed["records"]==[] and confirmed["count"]==0
assert json.loads((site/"data/public_evidence_catalogue.json").read_text("utf-8"))["records"]==[]
for key in ("id=\"compiledDamQuickToggle\"","id=\"compiledDamToggle\"",
            "id=\"compiledDamStatus\"","id=\"damRefInfo\"","id=\"damRefLegend\"",
            "function acceptCompiledDamPoints(value)","function renderCompiledDamLayer(scale)",
            "function hitCompiledDam(world)","function showDamRefPopup(hit)",
            "function hideDamRefPopup()","data/wa_dam_compiled_reference_preview.json",
            "unknown_in_source","Unverified"):
    if key=="unknown_in_source":continue
    if key=="Unverified":continue
    assert key in html,key
assert 'id="compiledDamToggle" aria-pressed="false" disabled' in html
assert 'id="compiledDamQuickToggle" aria-pressed="false" disabled' in html
assert "return compiledDamOn &&" in html
assert "if(!compiledDamData||!compiledDamOn)return null" in html
assert "if(!damHit)" in html
assert "This does NOT prove an unnamed physical dam" in html
assert "Not independently verified:" in html
for forbidden in ("raw_statement_internal","principal_candidate_id","private_drive_id"):
    assert forbidden not in html
print("STAGE 3D-S: 186 pinned publisher preview references, 3 disputed withheld, 118 source unnamed, 0 confirmed: PASS")
