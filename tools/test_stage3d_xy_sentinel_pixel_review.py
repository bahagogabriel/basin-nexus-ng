#!/usr/bin/env python3
"""Synthetic-only Stage 3D-X/Y: source lineage, cloud QA, no dam promotion."""
import copy
import unittest
from build_stage3d_xy_sentinel_pixel_review import (
    EXPECTED,SCL_CLEAR,SCL_OBSCURED,validate_source,parse_assets,center_cloud_qa,rank_by_local_clarity,run)
from test_stage3d_w_lineage_eo_discovery import cases,fake_history,fake_stac
from build_stage3d_w_lineage_eo_discovery import assemble


def stage_w():
    u,v=cases()
    return assemble(u,v,fetch_history=lambda url,**k:fake_history(
            url.split("/api/0.6/")[1].replace("/history","")),
        fetch_scene=lambda url,body=None,**k:fake_stac(body))


def scene(item):
    return {"type":"Feature","id":item,"collection":"sentinel-2-c1-l2a",
      "assets":{"visual":{"href":"https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/fiction/TCI.tif"},
                "scl":{"href":"https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/fiction/SCL.tif"}}}


class PixelQATests(unittest.TestCase):
    def test_stage_w_source_lineage(self):
        w=stage_w();rows=validate_source(w)
        self.assertEqual([x["source_reference_id"] for x in rows],EXPECTED)
        self.assertTrue(all(x["confirmation_decision"]=="HOLD_REVIEW_ONLY" for x in rows))
    def test_wrong_baseline_or_artifact_confirmation_blocked(self):
        for key,val in [("independently_confirmed_dams",1),("source_preview_sha256","corrupt"),
                        ("public_map_changes",True),("reviewed_site_count",3)]:
            w=stage_w();w[key]=val
            with self.subTest(field=key),self.assertRaises(ValueError):validate_source(w)
        w=stage_w();w["records"][0]["dam_wall_independently_located"]=True
        with self.assertRaises(ValueError):validate_source(w)
    def test_no_unexpected_scene_changes_or_false_pixel_claim(self):
        for key,val in [("structure_visually_confirmed",True),("image_pixels_downloaded",True),
                        ("scene_cloud_not_point_cloud",False)]:
            w=stage_w();w["records"][0]["sentinel2_scene_metadata"]["historical_2019"]["shortlist"][0][key]=val
            with self.subTest(field=key),self.assertRaises(ValueError):validate_source(w)
    def test_stac_visual_and_scl_assets_exact(self):
        k="TEST_S2_SCENE_2019"
        output=parse_assets(scene(k),k)
        self.assertEqual(set(output),{"visual","scl"})
    def test_unsafe_cog_hosts_and_missing_scl_rejected(self):
        k="TEST_S2_SCENE_2019"
        for url in ["http://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/test.tif",
                    "https://evil.example/test.tif",
                    "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/test.jpg",
                    "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/test.tif?token=1"]:
            item=scene(k);item["assets"]["visual"]["href"]=url
            with self.subTest(url=url),self.assertRaises(ValueError):parse_assets(item,k)
        item=scene(k);del item["assets"]["scl"]
        with self.assertRaises(ValueError):parse_assets(item,k)
    def test_cloud_scene_classification_with_masks(self):
        scl=[[4,8,6],[5,3,9],[0,10,11]]
        valid=[[True]*3 for i in range(3)]
        q=center_cloud_qa(scl,valid)
        self.assertEqual(q["pixels_total"],9)
        self.assertEqual(q["valid_pixels"],8)
        self.assertEqual(q["clear_fraction_of_valid"],0.375)
        self.assertEqual(q["obscured_fraction_of_valid"],0.625)
        self.assertEqual(q["scl_water_fraction_of_clear"],round(1/3,4))
        self.assertTrue(q["scl_water_is_not_evidence_of_a_dam"])
    def test_no_valid_pixels_is_null_not_zero_confidence(self):
        q=center_cloud_qa([[0,0],[0,0]],[[False]*2 for i in range(2)])
        self.assertIsNone(q["center_clear_fraction_of_valid"])
        self.assertIsNone(q["scl_water_fraction_of_clear"])
        self.assertEqual(q["valid_coverage_fraction"],0)
    def test_invalid_scl_rejected(self):
        for bad in [12,-1,6.5]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                center_cloud_qa([[4,bad],[6,4]],[[True]*2 for _ in range(2)])
    def test_alignment_rejected(self):
        with self.assertRaises(ValueError):
            center_cloud_qa([[4,5],[6]],[[True,True],[True,True]])
    def test_stage_z_local_clear_scene_priority_over_tile_cloud(self):
        low={"center_clear_fraction_of_valid":0.056,"center_valid_pixels":625,
             "valid_coverage_fraction":1.0}
        high={"center_clear_fraction_of_valid":0.92,"center_valid_pixels":625,
              "valid_coverage_fraction":1.0}
        self.assertGreater(rank_by_local_clarity(high,30),
                           rank_by_local_clarity(low,1))
    def test_stage_z_no_usable_local_scene_ranks_last(self):
        absent={"center_clear_fraction_of_valid":None,"center_valid_pixels":0,
                "valid_coverage_fraction":0}
        present={"center_clear_fraction_of_valid":0.1,"center_valid_pixels":600,
                 "valid_coverage_fraction":1.0}
        self.assertLess(rank_by_local_clarity(absent,0),
                        rank_by_local_clarity(present,50))
    def test_stage_z_invalid_cloud_metrics_cannot_be_selected(self):
        for m in [
            {"center_clear_fraction_of_valid":1.5,"center_valid_pixels":625,"valid_coverage_fraction":1},
            {"center_clear_fraction_of_valid":0.8,"center_valid_pixels":626,"valid_coverage_fraction":1},
            {"center_clear_fraction_of_valid":0.5,"center_valid_pixels":100,"valid_coverage_fraction":-0.1}
        ]:
            with self.assertRaises(ValueError):rank_by_local_clarity(m,0)

    def test_all_references_have_two_bounded_epochs(self):
        w=stage_w()
        for r in validate_source(w):
            self.assertEqual(set(r["sentinel2_scene_metadata"]),{"historical_2019","recent_2026"})
            for epoch,data in r["sentinel2_scene_metadata"].items():
                self.assertLessEqual(len(data["shortlist"]),3)

if __name__=="__main__":unittest.main()
