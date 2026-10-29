#!/usr/bin/env python3
"""Science-only regression for three original FAO 2026 model source endpoint matches."""
import copy,hashlib,json,unittest
from pathlib import Path
from build_stage3d_bd_bf_uncut_source_resolution import generate,SCHEMA

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"research/source_qa/FAO_2026_SIX_ORIGINAL_MODELED_REACHES_NOT_SURVEYED.geojson"
PUB=ROOT/"site/data/fao_three_original_gap_resolution.json"

class ThreeSourceModelQA(unittest.TestCase):
 def test_six_original_public_model_reaches_pinned(self):
  src=json.loads(SRC.read_text("utf-8"))
  self.assertEqual(src["type"],"FeatureCollection")
  self.assertEqual(len(src["features"]),6)
  self.assertEqual({int(f["properties"]["hyriv_id"]) for f in src["features"]},
      {10505946,10506074,10566530,10567236,10568272,10568127})
  self.assertEqual(hashlib.sha256(SRC.read_bytes()).hexdigest(),
      "90a2864a104b18a475d5e5028da9176d2f948845ea7164c410b08e4c2747895c")
 def test_published_three_model_junctions_are_exactly_rebuilt(self):
  doc=json.loads(PUB.read_text("utf-8"))
  self.assertEqual(generate(SRC),doc)
  self.assertEqual(doc["schema_version"],SCHEMA)
  self.assertEqual(doc["reviewed_source_pairs"],3)
  self.assertEqual([r["original_uncut_model_min_endpoint_gap_m"] for r in doc["cases"]],[0,0,0])
  self.assertEqual([r["clipped_display_min_endpoint_gap_m"] for r in doc["cases"]],[10983.5,4805.2,4885.1])
  self.assertFalse(doc["independent_hydraulic_continuity_verified"])
  self.assertTrue(all(not x["hydraulic_connection_field_verified"] for x in doc["cases"]))
 def test_all_three_removed_junctions_are_far_from_displayed_clips(self):
  doc=generate(SRC)
  self.assertTrue(all(x["clipped_source_nearest_endpoint_to_model_junction_m"]>2000 for x in doc["cases"]))
  self.assertTrue(all(x["clipped_target_nearest_endpoint_to_model_junction_m"]>3000 or x["source_hyriv_id"]==10505946 for x in doc["cases"]))
 def test_cannot_rename_or_transfer_original_model_source_id(self):
  tmp=json.loads(SRC.read_text("utf-8"))
  tmp["features"][0]["properties"]["hyriv_id"]=999999
  import tempfile
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"FAO_SIX.geojson"
   p.write_text(json.dumps(tmp))
   with self.assertRaises(ValueError):generate(p)
 def test_cannot_approve_or_publish_verified_hydrology_from_model_check(self):
  doc=generate(SRC)
  self.assertIn("not independently prove", " ".join(doc["scientific_notices"]))
  self.assertFalse(doc["independent_hydraulic_continuity_verified"])
  html=(ROOT/"site/index.html").read_text("utf-8")
  for phrase in ("Three large clipped-gap cases","Source endpoint status",
                 "not</strong> independently verify","function acceptFaoThreeUncutReview",
                 "function renderFaoThreeUncutReview","data/fao_three_original_gap_resolution.json"):
   self.assertIn(phrase,html)

if __name__=="__main__":unittest.main()
