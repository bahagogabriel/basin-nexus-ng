#!/usr/bin/env python3
"""Published 2026 reference-point aggregation: provenance and zero-individual-point gate."""
import json,re
from pathlib import Path

root=Path(__file__).resolve().parents[1]
site=root/"site"
data=json.loads((site/"data/wa_dams_2026_catchment_reference_counts.json").read_text("utf-8"))
registry=json.loads((site/"data/registry.json").read_text("utf-8"))
sources=json.loads((site/"data/external_reference_sources.json").read_text("utf-8"))
assert data["schema_version"]=="BN_WA_DAM_REFERENCE_CATCHMENT_V1"
assert data["status"]=="PROVISIONAL_RESEARCH_SOURCE_POINT_INTERSECTIONS_NOT_A_DAM_INVENTORY"
assert data["license"]=="CC BY 4.0"
assert data["source_file_md5"]=="046b106da1e3a57ec2f1c461fe411b26"
assert data["source_shapefile_md5"]=="a87f9b4ef2e96625b737ffac8595c138"
assert data["source_crs"].startswith("EPSG:4326")
assert data["dataset_doi"]=="10.60507/FK2/YLDK1Y"
assert (data["source_regional_dam_rows"],data["country_nigeria_source_rows"])==(1429,231)
assert data["country_rows_intersecting_any_display_catchment"]==189
assert data["country_rows_not_intersecting_any_display_catchment"]==42
assert data["country_rows_intersecting_multiple_display_catchments"]==0
assert data["repeated_source_ids"]==0 and data["repeated_numeric_coordinate_pairs"]==0
assert data["invalid_or_missing_numeric_coordinates"]==0
counts=data["per_catchment"]
ids={r["id"] for r in registry}
assert len(counts)==len(ids)==20 and set(counts)==ids
assert all(type(c) is int and c>=0 for c in counts.values())
assert sum(counts.values())==189
assert sum(c>0 for c in counts.values())==18
assert [x for x in sorted(counts) if counts[x]==0]==["SCMP-C03","SCMP-C19"]
assert data["catchments_without_source_point_matches"]==2
assert data["catchments_with_source_point_matches"]==18
assert data["individual_dam_records_published"]==0
assert data["individual_dam_coordinates_published"]==0
assert data["stakeholder_records_cleared"]==0
assert "no match" in data["limitations"] or "Zero means no match" in data["limitations"]
wa=next(x for x in sources["sources"] if x["id"]=="WA_DAMS_2026")
assert wa["nigeria_source_country_rows"]==231
assert wa["dam_csv_md5"]==data["source_file_md5"]
html=(site/"index.html").read_text("utf-8")
assert 'id="waDamReferenceSummary"' in html
assert 'id="waDamReferenceCounts"' in html
assert 'href="data/wa_dams_2026_catchment_reference_counts.json"' in html
assert "189 source point positions across 18 of 20 catchments" in html
rows=re.findall(r'<tr data-reference-catchment-id="(SCMP-C\d{2})" data-reference-count="(\d+)">',html)
assert len(rows)==20 and {k:int(v) for k,v in rows}==counts
assert "A zero is a source-data gap" in html
assert "not a field-surveyed dam inventory" in html
for private in ("raw_statement_internal","principal_candidate_id","private_drive_id","source_internal_id"):
    assert private not in html
assert json.loads((site/"data/public_evidence_catalogue.json").read_text("utf-8"))["records"]==[]
assert not any(x.name.endswith(".geojson") and "dam" in x.name.lower() for x in (site/"data").iterdir())
assert not any(k in json.dumps(data).lower() for k in ('"latitude"','"longitude"','"dam_name"','"location"'))
print("STAGE 3D-O PUBLIC AGGREGATE 189 SOURCE POINT INTERSECTIONS, 20 CATCHMENTS, ZERO COORDINATES: PASS")
