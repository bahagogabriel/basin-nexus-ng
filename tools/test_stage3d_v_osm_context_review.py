#!/usr/bin/env python3
"""All test coordinates and facility names are fictional. No API calls on PR."""
import copy
import unittest
from build_stage3d_v_osm_context_review import compare, make_query, normalize, parse_snapshot, validate_workbench, SEARCH_M
from build_stage3d_u_evidence_workbench import FIELDS

WITHHELD={"WA26-027":"Kafin Zaki","WA26-062":"Mambilla","WA26-095":"Souapiti"}

def fixture():
    rows=[]
    for i in range(19):
        ref=list(WITHHELD)[i] if i<3 else f"WA26-{i+200:03d}"
        priority="P0_WITHHELD_IDENTITY" if i<3 else "P1_NEARBY_OR_REPEATED_NAME"
        point=[6.5+i*.01,9.0+i*.01] # entirely fictional test positions
        rows.append({"source_reference_id":ref,
            "source_published_name":WITHHELD.get(ref) if i<3 else ("Fictional Test Dam" if i==3 else None),
            "catchment_id":"SCMP-C01","compiled_reference_position_WGS84":point,
            "triage_priority":priority,"triage_flags":[],
            "source_context_leads_NOT_SITE_RECEIPTS":[],
            **{k:None for k in FIELDS},
            "confirmation_status":"HOLD_UNVERIFIED","public_layer_status":"NO_CHANGE",
            "point_validation_performed":False,"eligible_for_public_confirmation":False})
    return {"schema_version":"BN_STAGE3D_U_HIGH_PRIORITY_REVIEW_WORKSHEET_V2",
        "status":"REVIEW_ONLY_ZERO_CONFIRMED_NOT_PUBLIC_SITE_DATA",
        "source_doi":"10.60507/FK2/YLDK1Y","source_license":"CC BY 4.0",
        "source_publisher_csv_md5":"046b106da1e3a57ec2f1c461fe411b26",
        "source_publisher_shapefile_md5":"a87f9b4ef2e96625b737ffac8595c138",
        "source_pinned_public_preview_sha256":"2dc9c81925ea2ed6b2cb82f13410868a96ccc93d1897f3eda6040e924c9dd82a",
        "source_records_total":189,"high_priority_cases":19,
        "withheld_source_identifications":3,"research_identity_or_proximity_flags":16,
        "reviewed_and_confirmed":0,"automated_evidence_confirmation_performed":False,
        "records":rows}

def osm(items):
    return {"version":0.6,"osm3s":{"timestamp_osm_base":"2026-10-28T18:00:00Z"},
            "elements":items}


class StageVTests(unittest.TestCase):
    def test_osm_dam_node_remains_unverified(self):
        w=fixture()
        p=w["records"][3]["compiled_reference_position_WGS84"]
        x=compare(w,osm([{"type":"node","id":100,
           "lat":p[1],"lon":p[0],"tags":{"waterway":"dam","name":"Fictional Test Dam"}}]))
        hit=x["records"][3]["osm_context_candidates"][0]
        self.assertEqual(hit["osm_context_kind"],"OSM_TAGGED_DAM_BARRIER")
        self.assertTrue(hit["same_normalized_source_name_hint"])
        self.assertFalse(hit["evidence_for_completed_structure"])
        self.assertIsNone(hit["source_lineage_independent"])
        self.assertFalse(x["records"][3]["eligible_for_public_confirmation"])
        self.assertEqual(x["confirmed_facility_count"],0)
        self.assertEqual(x["osm_license"],"ODbL")
    def test_reservoir_polygon_center_is_not_dam_wall(self):
        w=fixture();p=w["records"][3]["compiled_reference_position_WGS84"]
        x=compare(w,osm([{"type":"way","id":105,
          "center":{"lat":p[1],"lon":p[0]},"tags":{"water":"reservoir","name":"Fictional Lake"}}]))
        a=x["records"][3]["osm_context_candidates"][0]
        self.assertEqual(a["osm_position_repr"],"OSM_CENTER_NOT_DAM_WALL")
        self.assertFalse(a["position_verified"])
    def test_unavailable_is_not_negative_finding(self):
        x=compare(fixture(),acquisition_status="UNAVAILABLE",acquisition_error="TimeoutError")
        self.assertEqual(x["osm_query_state"],"QUERY_UNAVAILABLE")
        self.assertTrue(all(r["osm_candidate_count_in_radius"] is None for r in x["records"]))
        self.assertTrue(all(r["osm_review_state"]=="SEARCH_UNAVAILABLE" for r in x["records"]))
        self.assertEqual(x["confirmed_facility_count"],0)
    def test_valid_empty_snapshot_does_not_mean_no_dam(self):
        x=compare(fixture(),osm([]))
        self.assertTrue(all(r["osm_review_state"]=="NO_OSM_TAGGED_FEATURE_OBSERVED_NOT_ABSENCE" for r in x["records"]))
        self.assertTrue(all(r["osm_candidate_count_in_radius"]==0 for r in x["records"]))
    def test_reject_corrupt_snapshot_or_unbounded_elements(self):
        for d in [{},{"elements":[]},{"osm3s":{"timestamp_osm_base":"2026-10-28T18:00:00Z"},"elements":[{}]},
                  osm([{"type":"node","id":-1,"lat":9,"lon":6,"tags":{"waterway":"dam"}}])]:
            with self.subTest(d=d),self.assertRaises(ValueError):parse_snapshot(d)
        with self.assertRaises(ValueError):parse_snapshot(osm([{"type":"node","id":i+1} for i in range(6001)]))
    def test_reject_forged_evidence_or_name_relabel(self):
        for key,value in [("completed_structure_confirmed",True),("position_uncertainty_m",10),
                          ("eligible_for_public_confirmation",True),("point_validation_performed",True),
                          ("confirmation_status","APPROVED")]:
            x=fixture();x["records"][3][key]=value
            with self.subTest(field=key),self.assertRaises(ValueError):validate_workbench(x)
        x=fixture();x["records"][0]["source_published_name"]="Fiction"
        with self.assertRaises(ValueError):validate_workbench(x)
    def test_reject_source_drift(self):
        for key,value in [("source_doi","other"),("source_publisher_csv_md5","0"*32),
                          ("source_records_total",188),("reviewed_and_confirmed",1)]:
            x=fixture();x[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate_workbench(x)
    def test_bounded_single_overpass_query(self):
        q=make_query(validate_workbench(fixture()))
        self.assertEqual(q.count("(around:3000,"),19*3)
        self.assertEqual(q.count(";out center qt;"),1)
        self.assertEqual(q.count('["waterway"="dam"]'),19)
        self.assertNotIn("private",q)
        self.assertEqual(SEARCH_M,3000)
    def test_missing_polygon_center_never_fabricated(self):
        p=fixture()["records"][3]["compiled_reference_position_WGS84"]
        out=compare(fixture(),osm([{"type":"way","id":101,"tags":{"waterway":"dam"}},
                                   {"type":"node","id":102,"lat":p[1],"lon":p[0],"tags":{"natural":"water"}}]))
        self.assertEqual(out["osm_features_skipped_missing_center"],1)
        self.assertEqual(out["records"][3]["osm_candidate_count_in_radius"],0)
    def test_duplicate_osm_identity_deduplicated_not_facility(self):
        x=fixture();p=x["records"][3]["compiled_reference_position_WGS84"]
        item={"type":"node","id":91,"lat":p[1],"lon":p[0],"tags":{"waterway":"dam"}}
        out=compare(x,osm([item,item]))
        self.assertEqual(out["osm_features_in_snapshot"],1)
        self.assertEqual(out["records"][3]["osm_candidate_count_in_radius"],1)
        self.assertFalse(out["public_map_updated"])

if __name__=="__main__":unittest.main()
