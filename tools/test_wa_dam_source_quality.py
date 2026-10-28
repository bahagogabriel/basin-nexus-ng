#!/usr/bin/env python3
"""Stage 3D-Q: published source metadata completeness, no point or private claim."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
site=root/"site"
q=json.loads((site/"data/wa_dams_2026_source_quality.json").read_text("utf-8"))
refs=json.loads((site/"data/wa_dams_2026_catchment_reference_counts.json").read_text("utf-8"))
pub=json.loads((site/"data/public_evidence_catalogue.json").read_text("utf-8"))
registry=json.loads((site/"data/registry.json").read_text("utf-8"))
html=(site/"index.html").read_text("utf-8")
assert q["schema_version"]=="BN_WA_DAM_SOURCE_QUALITY_V1"
assert q["status"]=="ORIGINAL_PUBLISHER_COMPILED_REFERENCE_METADATA_REVIEW_ONLY"
assert q["source_dataset_doi"]==refs["dataset_doi"]
assert q["source_csv_md5"]==refs["source_file_md5"]
assert q["source_shapefile_md5"]==refs["source_shapefile_md5"]
assert q["source_crs_epsg"]==4326 and q["license"]=="CC BY 4.0"
assert q["publication_decision"]=="AGGREGATE_METADATA_ONLY_NO_POINT_LAYER"
n=q["national_source_summary"]
w=q["within_study_catchment_summary"]
assert n["nigeria_labelled_source_rows"]==231
assert n["rows_with_usable_source_name"]==84
assert n["rows_without_usable_source_name"]==147
assert n["rows_with_main_source_label"]==231
assert n["rows_with_recognizable_dam_year"]==76
assert n["rows_without_recognizable_dam_year"]==155
assert n["repeated_normalized_name_groups"]==5
assert n["source_rows_in_repeated_name_groups"]==11
assert n["pairs_of_source_points_within_250_metres"]==1
assert n["pairs_of_source_points_within_1_km"]==10
assert n["source_rows_with_neighbor_within_1_km"]==15
assert n["same_normalized_name_pairs_within_1_km"]==1
assert n["same_normalized_name_pairs_within_5_km"]==2
assert w["intersecting_compiled_source_points"]==189
assert w["source_points_with_usable_name"]==71
assert w["source_points_with_main_source_label"]==189
assert w["source_points_with_recognizable_dam_year"]==62
by=q["by_catchment"]
assert len(by)==20 and set(by)=={c["id"] for c in registry}
for cid,entry in by.items():
    assert set(entry)=={"source_positions","named_source_rows","rows_with_source_label","rows_with_recognizable_year"}
    assert entry["source_positions"]==refs["per_catchment"][cid]
    assert all(isinstance(v,int) and 0<=v<=entry["source_positions"] for v in entry.values())
assert sum(v["source_positions"] for v in by.values())==189
assert sum(v["named_source_rows"] for v in by.values())==71
assert sum(v["rows_with_recognizable_year"] for v in by.values())==62
assert sum(v["rows_with_source_label"] for v in by.values())==189
assert q["individually_verified_facilities"]==0
assert q["individual_dam_source_records_published"]==0
assert q["individual_coordinates_published"]==0
assert q["stakeholder_records_authorized"]==0
assert pub["records"]==[]
assert set(q)-{"by_catchment"}=={
 "schema_version","status","reviewed_on","source_dataset_doi","source_csv_md5",
 "source_shapefile_md5","source_crs_epsg","license","verification_workflow",
 "national_source_summary","within_study_catchment_summary","publication_decision",
 "individually_verified_facilities","individual_dam_source_records_published",
 "individual_coordinates_published","stakeholder_records_authorized","note"
}
for prohibited in ('"longitude"','"latitude"','"dam_name"','"source_internal_id"','"raw_statement_internal"'):
    assert prohibited not in json.dumps(q).lower()
for token in ('function acceptPublicDamSourceQuality(value)','data/wa_dams_2026_source_quality.json',
              'function renderKnowledgeLens(rows)','compiled_2026_dam_reference_source_points',
              'compiled_2026_source_rows_with_dam_names','compiled_2026_source_rows_with_recognizable_year',
              'Most compiled dam-reference points','Most named dam-source records',
              "individual_coordinates_published!==0","damQuality.by_catchment[row.id].source_positions"):
    assert token in html,token
for private in ("source_internal_id","raw_statement_internal","private_drive_id"):
    assert private not in html
print("STAGE 3D-Q PUBLISHED 231/84/76 SOURCE COMPLETENESS, 189/71/62 STUDY LENS, 0 POINTS: PASS")
