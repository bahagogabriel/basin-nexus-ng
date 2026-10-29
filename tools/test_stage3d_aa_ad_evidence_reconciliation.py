#!/usr/bin/env python3
"""Fictional test points and mocked external XML; never published facility claims."""
import copy,json,unittest
from build_stage3d_aa_ad_evidence_reconciliation import (
  GUSAU_DOCUMENT_LEADS,HUMAN_RECEIPTS,build_packet,local_line_distance_m,
  parse_osm_way,validate_all,_documentary_crosswalk,_scl_comparison)
from test_stage3d_w_lineage_eo_discovery import cases,fake_history,fake_stac
from build_stage3d_w_lineage_eo_discovery import assemble,REFERENCES
from test_stage3d_xy_sentinel_pixel_review import stage_w

def sources():
    u,v=cases()
    w=assemble(u,v,
      fetch_history=lambda url,**k:fake_history(url.split("/api/0.6/")[1].replace("/history","")),
      fetch_scene=lambda url,body=None,**k:fake_stac(body))
    rows=[]
    for wrow in w["records"]:
        z={}
        for epoch in ("historical_2019","recent_2026"):
            z[epoch]={"pixel_state":"RGB_SCL_PIXELS_SAMPLED_REVIEW_ONLY",
               "acquired_utc":"2019-08-01T10:00:00Z" if epoch=="historical_2019" else "2026-08-01T10:00:00Z",
               "structure_visually_verified":False,"site_coordinate_verified":False,
               "image_interpretation_performed":False,
               "pixel_qa":{"pixels_total":9216,"valid_coverage_fraction":1.0,
                   "center_clear_fraction_of_valid":1.0,
                   "center_scl_water_fraction_of_clear":0.2 if epoch=="historical_2019" else 0.1,
                   "scl_water_is_not_evidence_of_a_dam":True}}
        rows.append({"reference_id":wrow["source_reference_id"],
            "source_published_name":wrow["source_published_name"],
            "original_reference_WGS84_UNVERIFIED":wrow["source_position_WGS84_UNVERIFIED"],
            "epochs":z,"pixel_coverage_not_construction_date":True,
            "actual_dam_wall_position_verified":False,
            "independent_structure_confirmation":False,
            "human_interpretation_receipt":None,
            "public_release_authorized":False})
    z={"schema_version":"BN_STAGE3D_XY_SENTINEL_RGB_SCL_REVIEW_V1",
      "status":"PIXEL_SAMPLE_REVIEW_ONLY_NOT_A_DAM_SURVEY",
      "source_doi":"10.60507/FK2/YLDK1Y","source_preview_sha256":w["source_preview_sha256"],
      "source_license":"CC BY 4.0","osm_license":"ODbL",
      "sentinel_collection":"sentinel-2-c1-l2a",
      "SCL_not_independent_engineering_evidence":True,
      "historical_comparison_not_construction_or_operational_proof":True,
      "none_of_the_pixel_metrics_estimate_dam_position_accuracy":True,
      "independently_confirmed_dams":0,"public_map_changes":False,
      "source_names_not_verified":True,"RGB_SCL_samples_attempted":10,"records":rows}
    return u,v,w,z

def full_xml(way):
    id=way.split("/")[1]
    return (f'<osm version="0.6">'
       '<node id="10" lat="9.429" lon="8.780"/>'
       '<node id="11" lat="9.431" lon="8.782"/>'
       f'<way id="{id}" version="1" user="Synthetic Editor" uid="999" changeset="23">'
       '<nd ref="10"/><nd ref="11"/><tag k="waterway" v="dam"/></way></osm>').encode()

class StageAAADTests(unittest.TestCase):
    def test_five_case_pipeline_no_confirmation(self):
        inputs=sources()
        packet=build_packet(*inputs,fetch_way=lambda way:full_xml(way))
        self.assertEqual(len(packet["review_cases"]),5)
        self.assertEqual(len(packet["review_only_osm_way_lines"]["features"]),5)
        self.assertEqual(packet["confirmed_dams"],0)
        self.assertEqual(packet["pending_human_observations"],5*len(HUMAN_RECEIPTS))
        self.assertTrue(all(case["editorial_status"]=="HOLD_REVIEW_ONLY" for case in packet["review_cases"]))
        self.assertTrue(all(v is None for case in packet["review_cases"]
                        for v in case["human_release_receipts"].values()))
        self.assertFalse(any(case["wall_position_independently_verified"] for case in packet["review_cases"]))
        self.assertNotIn("Synthetic Editor",json.dumps(packet))
        self.assertNotIn("changeset",json.dumps(packet))
    def test_gusau_government_crosswalk_never_changes_identity(self):
        a=[6.6703,12.1464]
        leads=_documentary_crosswalk(a,"WA26-003")
        self.assertEqual(len(leads),2)
        self.assertAlmostEqual(leads[0]["source_point_to_reported_position_m"],84.9,delta=1)
        self.assertAlmostEqual(leads[1]["source_point_to_reported_position_m"],246.6,delta=1)
        self.assertTrue(all(not r["facility_identity_matched_independently"] for r in leads))
        self.assertEqual(_documentary_crosswalk(a,"WA26-083"),[])
        self.assertIn("INTAKE",leads[1]["reported_coordinate_kind"])
    def test_osm_line_geometry_not_survey_and_near_point(self):
        data=parse_osm_way(full_xml("way/571289118"),"way/571289118")
        self.assertEqual(data["osm_node_count"],2)
        self.assertFalse(data["site_wall_surveyed"])
        metrics=local_line_distance_m([8.781,9.430],data["coordinates"])
        self.assertLess(metrics["source_to_osm_polyline_nearest_m"],2)
        self.assertFalse(metrics["wall_position_independently_confirmed"])
    def test_geometry_missing_nodes_or_tag_is_unavailable(self):
        w="way/571289118"
        for xml in [b"<foo/>",
           b'<osm><way id="571289118"><nd ref="10"/><nd ref="11"/><tag k="waterway" v="dam"/></way></osm>',
           b'<osm><way id="571289118"><nd ref="10"/><nd ref="11"/><tag k="waterway" v="weir"/></way></osm>',
           b'<osm><node id="10" lat="9" lon="8"/><node id="11" lat="9" lon="8"/><way id="571289118"><nd ref="10"/><nd ref="11"/><tag k="waterway" v="dam"/></way></osm>']:
            with self.subTest(xml=xml),self.assertRaises(ValueError):parse_osm_way(xml,w)
    def test_upstream_unavailable_is_not_no_dam(self):
        x=build_packet(*sources(),fetch_way=lambda osm:(_ for _ in ()).throw(TimeoutError()))
        self.assertEqual(len(x["review_only_osm_way_lines"]["features"]),0)
        self.assertTrue(all(r["OSM_geometry_state"]=="UNAVAILABLE_NOT_NO_DAM" for r in x["review_cases"]))
        self.assertEqual(x["confirmed_dams"],0)
    def test_source_verification_tampering_fails(self):
        for idx,key,value in [(3,"independently_confirmed_dams",1),
                              (3,"public_map_changes",True),
                              (2,"independently_confirmed_dams",1),
                              (2,"source_preview_sha256","wrong")]:
            inputs=list(sources());obj=copy.deepcopy(inputs[idx]);obj[key]=value;inputs[idx]=obj
            with self.subTest(key=key),self.assertRaises(ValueError):validate_all(*inputs)
    def test_scl_difference_is_description_not_reservoir_area(self):
        row=sources()[3]["records"][0]
        result=_scl_comparison(row)
        self.assertAlmostEqual(result["center_SCL_water_fraction_difference_percentage_points_DESCRIPTIVE_ONLY"],-10)
        self.assertTrue(result["is_not_dam_construction_evidence"])
        self.assertTrue(result["is_not_reservoir_area_change"])
        self.assertEqual(result["interpretation_status"],"UNINTERPRETED_PIXEL_CLASSIFICATION_NOT_A_DAM")
    def test_no_water_data_results_null_difference(self):
        row=copy.deepcopy(sources()[3]["records"][0])
        row["epochs"]["recent_2026"]["pixel_qa"]["center_scl_water_fraction_of_clear"]=None
        self.assertIsNone(_scl_comparison(row)["center_SCL_water_fraction_difference_percentage_points_DESCRIPTIVE_ONLY"])
    def test_no_human_approval_possible_from_original_inputs(self):
        inputs=list(sources());z=copy.deepcopy(inputs[3])
        z["records"][0]["human_interpretation_receipt"]="fabricated"
        inputs[3]=z
        with self.assertRaises(ValueError):validate_all(*inputs)
    def test_distinct_research_points_not_auto_merged(self):
        packet=build_packet(*sources(),fetch_way=lambda way:full_xml(way))
        self.assertEqual({v["research_reference_id"] for v in packet["review_cases"]},set(REFERENCES))
        self.assertEqual(len(packet["review_cases"]),5)
        self.assertEqual(packet["published_facility_points_created"],0)

if __name__=="__main__":unittest.main()
