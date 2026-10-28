#!/usr/bin/env python3
"""Static public link-only source registry contract and privacy safeguard."""
import json,re
from pathlib import Path

root=Path(__file__).resolve().parents[1]
site=root/"site"
data=json.loads((site/"data/external_reference_sources.json").read_text(encoding="utf-8"))
assert set(data)=={"schema_version","status","reviewed_on","source_records_integrated","facility_points_published","sources"}
assert data["schema_version"]=="BN_EXTERNAL_REFERENCE_V1"
assert data["status"]=="PUBLIC_SOURCE_LINKS_ONLY"
assert data["source_records_integrated"]==data["facility_points_published"]==0
sources=data["sources"]
assert len(sources)==4
ids={r["id"] for r in sources}
assert ids=={"WA_DAMS_2026","NGSA_MINERAL_OCCURRENCE","NGSA_NMRDSS","NGSA_MAP_DERIVED_COMPILATION"}
assert len(set(r["url"] for r in sources))==4
for row in sources:
    assert set(row)=={"id","subject","name","producer","url","doi","publication_date","license","status",
     "regional_dam_points_reported","regional_reservoir_polygons_reported","source_file_doi","dam_csv_md5","note"}
    assert row["url"].startswith("https://")
    assert row["status"]!="PUBLISHED_AS_VERIFIED_ASSETS"
    assert 15<len(row["note"])<800
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",str(row))
    assert not re.search("private_drive_id|raw_statement_internal|source_internal_id|attendance",str(row),re.I)
wa=next(x for x in sources if x["id"]=="WA_DAMS_2026")
assert wa["dam_csv_md5"]=="046b106da1e3a57ec2f1c461fe411b26"
assert wa["source_file_doi"]=="10.60507/FK2/YLDK1Y/WKZDRQ"
assert wa["regional_dam_points_reported"]==1429 and wa["regional_reservoir_polygons_reported"]==1258
assert wa["status"]=="ACQUISITION_AND_SPATIAL_QA_PENDING"
assert all(x["regional_dam_points_reported"] is None for x in sources if x["id"]!="WA_DAMS_2026")
html=(site/"index.html").read_text(encoding="utf-8")
for source in sources:
    assert 'data-external-source="'+source["id"]+'"' in html
    assert 'href="'+source["url"]+'"' in html
assert 'id="externalReferenceSources"' in html
assert 'href="data/external_reference_sources.json"' in html
assert 'not yet been checked' in html
public=json.loads((site/"data/public_evidence_catalogue.json").read_text(encoding="utf-8"))
assert public["records"]==[]
for prohibited in ("WA_Dams_2026.geojson","mineral_occurrence_points.geojson","candidate_geolocation.json"):
    assert not (site/"data"/prohibited).exists()
print("STAGE 3D-L PUBLIC SOURCES LINK-ONLY, 2026 REGIONAL COUNT CONTEXT, ZERO PUBLIC POINTS: PASS")
