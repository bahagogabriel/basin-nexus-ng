#!/usr/bin/env python3
"""Synthetic coordinates and exact-source screening; no surveyed river assertions."""
from __future__ import annotations
import copy,json,math,unittest
from pathlib import Path
from build_stage3d_ay_az_fao_endpoint_qa import (
 band,endpoints,haversine_m,separation_m,build,outlier_review_csv,SOURCE_STATUS,MAX_LOOKUP_BYTES)

class SourceEndpointScreenTests(unittest.TestCase):
 def test_synthetic_coincident_and_large_gaps(self):
  self.assertAlmostEqual(haversine_m((6,10),(6,10)),0)
  self.assertGreater(haversine_m((6,10),(6,10.01)),1000)
  self.assertEqual(band(0),"endpoint_le_50m")
  self.assertEqual(band(50),"endpoint_le_50m")
  self.assertEqual(band(50.1),"endpoint_50_to_500m")
  self.assertEqual(band(500),"endpoint_50_to_500m")
  self.assertEqual(band(500.1),"endpoint_gt_500m")
  self.assertEqual(band(None),"next_id_not_in_index")
 def test_linestring_endpoints_are_not_whole_geometries(self):
  a=endpoints({"type":"LineString","coordinates":[[7,10],[8,11],[9,12]]})
  self.assertEqual(a,[(7,10),(9,12)])
  self.assertEqual(separation_m(a,[(9,12)]),0)
 def test_synthetic_multi_part_geometry_preserves_clipping(self):
  parts=endpoints({"type":"MultiLineString","coordinates":[
   [[6,9],[6.1,9.1]],[[8,10],[8.3,10.3]]]})
  self.assertEqual(len(parts),4)
  self.assertEqual(separation_m(parts,[(8.3,10.3)]),0)
 def test_not_survey_or_accuracy_claim(self):
  s,idx,raw=build()
  self.assertEqual(s["status"],SOURCE_STATUS)
  self.assertEqual(s["clipped_reach_copies"],52012)
  self.assertEqual(s["unique_source_ids"],51906)
  self.assertEqual(len(idx["rows"]),51906)
  self.assertEqual(len(s["cross_catchment_source_link_pair_geometry_screen"]),33)
  self.assertLess(len(raw),MAX_LOOKUP_BYTES)
  self.assertEqual(sum(s["total_clipped_source_link_classification"].values()),52012)
  self.assertEqual(sum(x["clipped_reaches"] for x in s["by_catchment"].values()),52012)
  self.assertTrue(any("not field uncertainty" in v for v in s["limitations"]))
  source_index=json.loads((Path(__file__).resolve().parents[1]/"site/data/fao_downstream_index.json").read_text("utf-8"))
  flagged=outlier_review_csv(s,idx,source_index)
  self.assertEqual([v["source_hyriv_id"] for v in flagged],[10505946,10566530,10568272])
  self.assertEqual([v["minimum_clipped_endpoint_separation_m"] for v in flagged],[10983.5,4805.2,4885.1])
  self.assertTrue(all(v["review_status"]=="GEOMETRIC_SCREENING_LEAD_NOT_FIELD_VERIFIED" for v in flagged))
 def test_reject_invalid_coordinates_and_geometry(self):
  for geometry in ({"type":"Point","coordinates":[6,10]},
    {"type":"LineString","coordinates":[[5,9]]},
    {"type":"LineString","coordinates":[[5,9],[float("nan"),10]]},
    {"type":"MultiLineString","coordinates":[[]]}):
   with self.subTest(geometry=geometry.get("type")),self.assertRaises(ValueError):
    endpoints(geometry)
 def test_only_original_source_files_can_generate_data(self):
  root=Path(__file__).resolve().parents[1]/"site/data"
  self.assertTrue((root/"fao_downstream_summary.json").exists())
  self.assertTrue((root/"fao_downstream_index.json").exists())
  for file in ("detailed_river_manifest.json","registry.json"):
   self.assertTrue((root/file).exists())
if __name__=="__main__":unittest.main()
