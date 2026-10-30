#!/usr/bin/env python3
"""S19: verify source-specific LGA resource symbols without fictional site coordinates."""
import json
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parents[1]
site=root/"site"
read=lambda p:json.loads((site/"data"/p).read_text(encoding="utf-8"))
data=read("stakeholder_lga_occurrences.json")
admin=read("admin_crosswalk_provisional.json")
atlas=read("stakeholder_resource_atlas.json")
sources=read("stakeholder_source_detail.json")
assert data["schema_version"]=="BN_STAKEHOLDER_LGA_OCCURRENCES_V1"
assert data["publication_scope"]=="OWNER_AUTHORIZED_ANONYMIZED_SOURCE_STATEMENTS_ALREADY_PUBLIC_IN_S18"
records=data["records"]
assert len(records)==data["records_count"]>=400
assert data["source_documents_count"]==20
assert data["catchments_covered"]==20
assert len({r["id"] for r in records})==len(records)
assert len({(r["resource_id"],r["lga_id"]) for r in records})==len(records)
ids={c["id"] for c in atlas["catchments"]}
assert set(data["counts_by_catchment"])==ids==set(admin["byCatchment"])
assert dict(Counter(r["catchment_id"] for r in records))==data["counts_by_catchment"]
resources={r["id"]:r for r in atlas["resources"]}
source_keys={(e["c"],sources["documents"][e["d"]],e["p"],e["s"]) for e in sources["entries"]}
for r in records:
 assert r["catchment_id"] in ids
 assert r["source_locators"] and all((r["catchment_id"],x["document"],x["paragraph"],x["theme"]) in source_keys for x in r["source_locators"])
 assert all(x["document"].lower().startswith("communiqu") for x in r["source_locators"])
 a=resources[r["resource_id"]]
 assert (r["catchment_id"],r["category"],r["name"])==(a["catchment_id"],a["category"],a["reported_resource"])
 assert r["evidence_status"]=="OWNER_AUTHORIZED_STAKEHOLDER_REPORTED_NOT_INDEPENDENTLY_VERIFIED"
 assert r["spatial_scope"]=="LGA_REPRESENTATIVE_POSITION_NOT_EXACT_ASSET"
 assert all(k not in r for k in ("coordinates","latitude","longitude","geometry","source_file_id","private_drive_url"))
 matches=[x for x in admin["byCatchment"][r["catchment_id"]]["lgas"] if x["id"]==r["lga_id"]]
 assert len(matches)==1
 matched=matches[0]
 assert (matched["name"],matched["state"])==(r["lga_name"],r["state"])
 assert abs(r["intersection_km2"]-matched["km2"])<0.015
 assert r["intersection_km2"]>=.5
assert any(r["catchment_id"]=="SCMP-C04" and r["lga_name"]=="Ngaski" and r["name"]=="Lithium" for r in records)
assert any(r["catchment_id"]=="SCMP-C03" and r["lga_name"]=="Kanam" and r["name"]=="Gold" for r in records)
assert not any(x in (site/"data/stakeholder_lga_occurrences.json").read_text().lower() for x in ("drive.google.com","@gmail.com","signature/date"))
html=(site/"index.html").read_text(encoding="utf-8")
for token in ("stakeholder_lga_occurrences.json","acceptStakeholderLGAEvidence","allOccurrenceRecords","occurrenceRepresentativePoint","drawOccurrenceSymbols","source_locators"):
 assert token in html
print(f"S19 LGA evidence PASS: {len(records)} source-linked LGA resource records in {data['catchments_covered']} catchments; no fictional site coordinates")
