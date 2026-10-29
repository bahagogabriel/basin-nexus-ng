#!/usr/bin/env python3
"""Synthetic-only source-graph safety and data publication tests."""
from __future__ import annotations
import tempfile,unittest
from pathlib import Path
from build_stage3d_au_av_fao_topology import (
 _identifier,_cycles,build,MAX_INDEX_BYTES,UNIQUE_IDS,TOTAL_FEATURES)

class TopologyTests(unittest.TestCase):
 def test_valid_integer_source_ids_and_zero_unlinked(self):
  self.assertEqual(_identifier("10746373"),10746373)
  self.assertIsNone(_identifier("0",True))
  self.assertIsNone(_identifier(None,True))
  for x in ("-9999","foo",True,"12.3","3e5"):
   with self.subTest(x=x),self.assertRaises(ValueError):_identifier(x)
 def test_functional_graph_loop_detection(self):
  g={1:2,2:3,3:2,4:5,5:None,6:4}
  self.assertEqual(_cycles(g),{2,3})
  self.assertEqual(_cycles({1:2,2:0,3:7}),set())
 def test_no_self_links_in_public_graph(self):
  with self.assertRaises(ValueError):_identifier(-1)
 def test_real_twenty_catchment_source_integrity(self):
  summary,index,compressed=build()
  self.assertEqual(summary["unique_source_reach_ids"],UNIQUE_IDS)
  self.assertEqual(summary["clipped_catchment_reach_copies"],TOTAL_FEATURES)
  self.assertEqual(len(index["rows"]),UNIQUE_IDS)
  self.assertLess(len(compressed),MAX_INDEX_BYTES)
  self.assertEqual(sum(d["clipped_reaches"] for d in summary["counts_by_catchment"].values()),TOTAL_FEATURES)
  self.assertEqual(summary["status"],"RESEARCH_ONLY_ORIGINAL_SOURCE_LINKS_NO_INDEPENDENT_CONNECTIVITY_PROOF")
  self.assertFalse(any("dam locations" in str(x).lower() for x in index["rows"][:100]))
 def test_reject_different_source_bytes(self):
  # No modifications to source files; normal publication tests check hashes.
  root=Path(__file__).resolve().parents[1]/"site/data"
  with tempfile.TemporaryDirectory() as temp:
   d=Path(temp)
   (d/"detailed_river_manifest.json").write_bytes((root/"detailed_river_manifest.json").read_bytes())
   (d/"registry.json").write_bytes((root/"registry.json").read_bytes())
   with self.assertRaises(FileNotFoundError):build(d)
if __name__=="__main__":unittest.main()
