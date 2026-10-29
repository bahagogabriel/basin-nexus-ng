#!/usr/bin/env python3
"""Synthetic geometry QA and strict original-source 89-row publication checks."""
from __future__ import annotations
import copy
import csv
import io
import json
import unittest
from pathlib import Path
from shapely.geometry import Polygon, LineString
from build_stage3d_bg_bh_89_boundary_qa import (
    build, to_csv, _relation, _nearest_model_gap, STATUS, SCHEMA, DATA
)

class CrossCatchmentTests(unittest.TestCase):
    def test_synthetic_study_area_relationships_are_not_hydraulic_flow(self):
        a=Polygon([(0,0),(2,0),(2,2),(0,2)])
        overlap=Polygon([(1,1),(3,1),(3,3),(1,3)])
        touch=Polygon([(2,0),(3,0),(3,2),(2,2)])
        apart=Polygon([(4,0),(5,0),(5,1),(4,1)])
        self.assertEqual(_relation(a,overlap),"overlapping_study_polygons")
        self.assertEqual(_relation(a,touch),"boundaries_touch_or_intersect")
        self.assertEqual(_relation(a,apart),"spatially_separate_study_polygons")

    def test_synthetic_clipped_line_closest_gap(self):
        a=LineString([(6,10),(6.01,10)])
        b=LineString([(6.01,10),(6.03,10)])
        other=LineString([(6.05,10),(6.08,10)])
        self.assertEqual(_nearest_model_gap(a,b),0)
        self.assertGreater(_nearest_model_gap(a,other),1000)

    def test_real_source_89_link_integrity(self):
        doc=build()
        self.assertEqual(doc["schema_version"],SCHEMA)
        self.assertEqual(doc["status"],STATUS)
        self.assertEqual(doc["source_reach_copies_crossing_selected_catchment_index"],89)
        self.assertEqual(doc["unique_cross_catchment_source_association_pairs"],33)
        self.assertEqual(len(doc["source_references"]),89)
        self.assertEqual(len(doc["pair_aggregates"]),33)
        self.assertEqual(sum(d["source_links_to_other_study_catchments"] for d in doc["per_catchment"].values()),89)
        self.assertEqual(sum(d["source_reference_count"] for d in doc["pair_aggregates"]),doc["reference_memberships_across_target_catchments"])
        self.assertGreaterEqual(doc["reference_memberships_across_target_catchments"],89)
        self.assertEqual(sum(doc["polygon_relationship_reference_counts"].values()),doc["reference_memberships_across_target_catchments"])
        self.assertTrue(all(not p["not_independent_flow_confirmation"] is False for p in doc["pair_aggregates"]))

    def test_every_cross_link_reconciles_both_publisher_ids_and_clips(self):
        doc=build()
        graph=json.loads((DATA/"fao_downstream_index.json").read_text("utf-8"))
        original={fid:(dn,mask) for fid,dn,mask in graph["rows"]}
        ids=graph["catchment_ids"]
        for rec in doc["source_references"]:
            src,dst=rec["source_hyriv_id"],rec["original_next_down_id"]
            dn,mask=original[src]
            self.assertEqual(dn,dst)
            self.assertIn(rec["from_catchment_id"],[ids[i] for i in range(20) if mask&(1<<i)])
            self.assertNotIn(rec["from_catchment_id"],rec["next_id_catchments"])
            self.assertEqual(rec["next_id_catchments"],[ids[i] for i in range(20) if original[dst][1]&(1<<i)])
            self.assertGreaterEqual(rec["closest_clipped_line_gap_m"],0)
            self.assertEqual(rec["review_status"],"SOURCE_RECORD_AND_CLIPPED_GEOMETRY_SCREEN_ONLY")

    def test_csv_is_safe_public_source_only_and_exact_rows(self):
        doc=build()
        parsed=list(csv.DictReader(io.StringIO(to_csv(doc))))
        self.assertEqual(len(parsed),89)
        self.assertEqual(len({(x["from_catchment_id"],x["source_hyriv_id"]) for x in parsed}),89)
        self.assertFalse(any(k for k in parsed[0] if "person" in k or "private" in k or "stakeholder" in k))

    def test_narrative_cannot_claim_flow_or_field_confirmation(self):
        doc=build()
        alltext=" ".join(doc["scientific_limitations"]).lower()
        self.assertIn("not whole-catchment downstream order",alltext)
        self.assertIn("not observed hydraulic flow",alltext)
        self.assertIn("not for all these 89 references",alltext)

if __name__=="__main__":
    unittest.main()
