#!/usr/bin/env python3
"""Source-only 20 SCMP area overlaps and 125 original FAO reach screen records."""
from __future__ import annotations
import csv,io,json,unittest
from pathlib import Path
from shapely.geometry import Polygon
from build_stage3d_bk_bl_overlap_outlet_screen import (
 DATA,SCHEMA,STATUS,BAND_M,equal_area_overlaps,build,to_csv
)
class ScreenTests(unittest.TestCase):
 def test_synthetic_area_overlap_cannot_establish_outlets(self):
  ids=[{"id":"A","name":"A"},{"id":"B","name":"B"}]
  a=Polygon([(6,9),(8,9),(8,11),(6,11)])
  b=Polygon([(7,10),(9,10),(9,12),(7,12)])
  # Full screen requires exact 20 original study areas: refuse to fabricate a 2-catchment comparison.
  with self.assertRaises(ValueError):
   equal_area_overlaps(ids,{"A":a,"B":b})
 def test_model_screen_pins_original_125_source_records_and_zero_verified(self):
  data=build()
  self.assertEqual(data["schema_version"],SCHEMA)
  self.assertEqual(data["status"],STATUS)
  self.assertEqual(data["source_screen_record_count"],125)
  self.assertEqual(data["source_89_research_count"],89)
  self.assertEqual(data["out_of_index_next_id_count"],32)
  self.assertEqual(data["null_source_terminal_count"],4)
  self.assertEqual(data["actual_verified_outlet_count"],0)
  self.assertEqual(len(data["boundary_exit_lead_records"]),125)
  self.assertEqual(len(data["screen_overlap"]["overlap_pairs"]),190)
  self.assertEqual(data["screen_threshold_m"],250)
 def test_overlap_reference_screen_is_area_reproducible_and_nonexclusive(self):
  v=build()["screen_overlap"]
  self.assertEqual(v["study_pair_count"],190)
  self.assertGreaterEqual(v["screen_sum_catchment_polygon_area_km2"],v["screen_area_unique_union_km2"])
  self.assertGreater(v["screen_area_double_counted_km2"],0)
  self.assertGreater(v["screen_overlap_pair_count"],0)
  self.assertEqual(len(v["per_catchment"]),20)
  self.assertFalse(any(x.get("verified_outlet") for x in v["per_catchment"].values()))
 def test_reconcile_boundary_screen_with_earlier_source_89_qa(self):
  report=build()
  baseline=json.loads((DATA/"fao_89_catchment_source_boundary_audit.json").read_text("utf-8"))
  original={(x["from_catchment_id"],x["source_hyriv_id"]) for x in baseline["source_references"]}
  candidates={(x["catchment_id"],x["source_hyriv_id"]) for x in report["boundary_exit_lead_records"]
              if x["source_link_class"]=="NEXT_ID_ONLY_IN_OTHER_STUDY_AREAS"}
  self.assertEqual(candidates,original)
  self.assertEqual(len(candidates),89)
  self.assertEqual(sum(x["next_id_only_in_other_study_areas"] for x in report["screen_overlap"]["per_catchment"].values()),89)
  self.assertEqual(sum(x["next_id_outside_index"] for x in report["screen_overlap"]["per_catchment"].values()),32)
  self.assertEqual(sum(x["source_terminal_or_unlinked"] for x in report["screen_overlap"]["per_catchment"].values()),4)
 def test_csv_and_claims_are_source_research_only(self):
  v=build();parsed=list(csv.DictReader(io.StringIO(to_csv(v))))
  self.assertEqual(len(parsed),125)
  self.assertTrue(all(not x["hydraulic_outlet_verified"] for x in v["boundary_exit_lead_records"]))
  self.assertTrue(all(x["within_250m_screening_band"]==(x["distance_nearest_clipped_endpoint_to_study_boundary_m"]<=BAND_M) for x in v["boundary_exit_lead_records"]))
  narrative=" ".join(v["source_method_limits"]).lower()
  for snippet in ("not a validated mutually exclusive","not proof","not necessarily a river outlet",
                  "not an independently surveyed catchment outlet","not a confirmed channel crossing"):
   self.assertIn(snippet,narrative)
if __name__=="__main__":unittest.main()
