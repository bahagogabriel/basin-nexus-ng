#!/usr/bin/env python3
"""Strict source-only comparison publication contract: no extra river downloads."""
import copy,json,unittest
from pathlib import Path
from build_stage3d_aq_river_reach_comparison import make,verify,SCHEMA

DATA=Path(__file__).resolve().parents[1]/"site/data"
def load():
    return (json.loads((DATA/"detailed_river_manifest.json").read_text("utf-8")),
            json.loads((DATA/"registry.json").read_text("utf-8")))

class ComparisonTests(unittest.TestCase):
    def test_committed_json_and_csv_match_existing_source(self):
        m,reg=load();published=json.loads((DATA/"river_reach_comparison.json").read_text("utf-8"))
        self.assertTrue(verify(m,reg,published,(DATA/"river_reach_comparison.csv").read_text("utf-8")))
        self.assertEqual(published["schema_version"],SCHEMA)
        self.assertEqual(published["clipped_reach_segments"],52012)
        self.assertEqual(published["unique_intersecting_source_reaches"],51906)
        self.assertEqual(len(published["rows"]),20)
    def test_upstream_area_classes_are_not_strahler_order(self):
        r=make(*load())
        self.assertEqual(sum(c["reach_count"] for c in r["rows"]),52012)
        self.assertIn("not Strahler",r["metric_notices"][2])
        self.assertIn("not drainage length",r["metric_notices"][1])
        self.assertIn("not flood",r["metric_notices"][3])
    def test_all_rows_are_area_normalized_correctly(self):
        for c in make(*load())["rows"]:
            self.assertAlmostEqual(c["reaches_per_1000_km2"],round(c["reach_count"]*1000/c["area_km2"],1))
            self.assertAlmostEqual(c["large_share_pct"],round(100*c["large_reaches"]/c["reach_count"],1))
    def test_source_manifest_drift_fails_closed(self):
        m,reg=load()
        for key,value in [("total_display_reaches",52013),("source_intersecting_unique_reaches",52012),("license","public domain")]:
            x=copy.deepcopy(m);x[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):make(x,reg)
    def test_one_modified_class_count_rejected(self):
        m,reg=load();m=copy.deepcopy(m)
        m["files"]["SCMP-C01"]["classes"]["large_upstream_1000plus"]+=1
        with self.assertRaises(ValueError):make(m,reg)
    def test_source_area_and_name_are_pinned(self):
        m,reg=load();reg=copy.deepcopy(reg)
        reg[0]["name"]="Invented catchment"
        with self.assertRaises(ValueError):make(m,reg)
        m,reg=load();reg=copy.deepcopy(reg);reg[0]["area_km2"]=-1
        with self.assertRaises(ValueError):make(m,reg)
    def test_missing_or_duplicate_stable_catchment_id_rejected(self):
        m,reg=load();reg=copy.deepcopy(reg);reg[0]["id"]=reg[1]["id"]
        with self.assertRaises(ValueError):make(m,reg)
    def test_modified_published_numeric_data_rejected(self):
        m,reg=load()
        p=make(m,reg);p["rows"][0]["reaches_per_1000_km2"]+=50
        with self.assertRaises(ValueError):verify(m,reg,p,(DATA/"river_reach_comparison.csv").read_text("utf-8"))
    def test_modified_csv_data_rejected(self):
        m,reg=load()
        p=make(m,reg);original=(DATA/"river_reach_comparison.csv").read_text("utf-8")
        with self.assertRaises(ValueError):verify(m,reg,p,original.replace("SCMP-C01","SCMP-CXX",1))
    def test_public_ui_cannot_claim_surveyed_rivers(self):
        source=(DATA.parent/"index.html").read_text("utf-8")
        for required in ("id=\"reachComparison\"","id=\"reachCompareRows\"","id=\"reachCompareSort\"",
                         "function acceptRiverComparison(data)","function renderRiverComparison()",
                         "data/river_reach_comparison.json","not drainage length per area" if False else "not</em> drainage length"):
            self.assertIn(required,source)
        self.assertIn("reaches per 1,000 km², not measured drainage density",source)

if __name__=="__main__":unittest.main()
