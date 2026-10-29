#!/usr/bin/env python3
"""All record coordinates and official leads in these tests are synthetic."""
import copy,unittest
from build_stage3d_ae_ah_review_desk import IDS,RECEIPTS,SHA,build,validate_source,blank_routing_form,validate_routing_form

def fixture():
    rows=[]
    for i,ref in enumerate(IDS):
        leads=[]
        if ref=="WA26-003":
            for kind in ("DAM_INVENTORY_REPORTED_COORDINATE_NOT_SURVEYED_BY_THIS_PROJECT",
                         "WATER_ABSTRACTION_INTAKE_POINT_NOT_DAM_WALL"):
                leads.append({"document_url":"https://fictional.example.test/record",
                  "record_label":"Synthetic record",
                  "reported_coordinate_kind":kind,
                  "source_point_to_reported_position_m":100,
                  "facility_identity_matched_independently":False,
                  "wall_position_surveyed_independently":False,
                  "source_lineage_independence_verified":False,
                  "release_authorized":False})
        rows.append({"research_reference_id":ref,
          "source_name_NOT_VERIFIED":None if ref.startswith("WA26-18") else "Gusau",
          "original_compiled_point_WGS84_NOT_WALL":[6.5+i*.05,9.4],
          "osm_way":f"way/{100+i}",
          "OSM_polyline_review_metrics":{"source_to_osm_polyline_nearest_m":2,
              "distance_is_not_position_accuracy":True,
              "wall_position_independently_confirmed":False},
          "independent_public_documentary_context_NOT_FACILITY_RECEIPTS":leads,
          "sentinel_SCL_temporal_descriptive_QA":{
            "periods":{"historical_2019":{"acquired_utc":"2019-11-01T00:00:00Z"},
                       "recent_2026":{"acquired_utc":"2026-10-10T00:00:00Z"}},
            "interpretation_status":"UNINTERPRETED_PIXEL_CLASSIFICATION_NOT_A_DAM",
            "is_not_dam_construction_evidence":True,"is_not_reservoir_area_change":True,
            "center_SCL_water_fraction_difference_percentage_points_DESCRIPTIVE_ONLY":0.4},
          "human_release_receipts":{k:None for k in RECEIPTS},
          "exists_as_constructed_dam_independently_verified":False,
          "wall_position_independently_verified":False,
          "source_lineage_independent":False,
          "human_public_release_authorized":False,
          "editorial_status":"HOLD_REVIEW_ONLY"})
    return {"schema_version":"BN_STAGE3D_AA_AD_REVIEW_ONLY_V1",
      "status":"HUMAN_EVIDENCE_REQUIRED_NO_DAM_ADMISSIONS",
      "source_doi":"10.60507/FK2/YLDK1Y","source_preview_sha256":SHA,
      "source_license":"CC BY 4.0","osm_license":"ODbL",
      "review_subjects":5,"confirmed_dams":0,
      "published_facility_points_created":0,"published_private_evidence_created":0,
      "digital_evidence_context_does_not_prove_source_independence":True,
      "pending_human_observations":60,"review_cases":rows}

class EvidenceDeskTests(unittest.TestCase):
    def test_priority_queue_is_ordered_and_no_admissions(self):
        d=build(fixture())
        self.assertEqual([r["reference_id"] for r in d["cases"]],list(IDS))
        self.assertEqual(d["unfilled_human_evidence_receipts"],60)
        self.assertEqual(d["independently_confirmed_dams"],0)
        self.assertFalse(d["public_map_changes"])
        self.assertTrue(all(r["review_status"]=="HOLD_NOT_ASSESSED_BY_ACCOUNTABLE_REVIEWER" for r in d["cases"]))
    def test_inventory_and_intake_remain_distinct(self):
        d=build(fixture())
        leads=d["cases"][0]["independent_documentary_LEADS_NOT_MATCHES"]
        self.assertEqual(len(leads),2)
        self.assertNotEqual(leads[0]["original_coordinate_kind_NOT_WALL_SURVEY"],
                            leads[1]["original_coordinate_kind_NOT_WALL_SURVEY"])
        self.assertTrue(all(x["independent_facility_identity_match"] is False for x in leads))
        self.assertTrue(all(not c["independent_documentary_LEADS_NOT_MATCHES"] for c in d["cases"][1:]))
    def test_cannot_forge_source_confirmation(self):
        for key,value in (("confirmed_dams",1),("published_facility_points_created",1),
                          ("pending_human_observations",59),("source_preview_sha256","fake")):
            x=fixture();x[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate_source(x)
    def test_cannot_forge_wall_or_review_receipt(self):
        for key,value in (("wall_position_independently_verified",True),
                          ("human_public_release_authorized",True),
                          ("editorial_status","APPROVED")):
            x=fixture();x["review_cases"][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):build(x)
        x=fixture();x["review_cases"][0]["human_release_receipts"]["wall_position_uncertainty_m"]=5
        with self.assertRaises(ValueError):build(x)
    def test_cannot_reinterpret_osm_or_scl_as_proof(self):
        x=fixture();x["review_cases"][0]["OSM_polyline_review_metrics"]["wall_position_independently_confirmed"]=True
        with self.assertRaises(ValueError):build(x)
        x=fixture();x["review_cases"][0]["sentinel_SCL_temporal_descriptive_QA"]["is_not_dam_construction_evidence"]=False
        with self.assertRaises(ValueError):build(x)
    def test_cannot_rename_source_or_redistribute_gusau_leads(self):
        x=fixture();x["review_cases"][1]["independent_public_documentary_context_NOT_FACILITY_RECEIPTS"]=\
             copy.deepcopy(x["review_cases"][0]["independent_public_documentary_context_NOT_FACILITY_RECEIPTS"])
        with self.assertRaises(ValueError):build(x)
    def test_blank_routing_is_valid_but_never_releasable(self):
        d=build(fixture());form=blank_routing_form(d)
        self.assertEqual(validate_routing_form(d,form)["outstanding_receipts"],60)
        self.assertFalse(validate_routing_form(d,form)["releasable"])
    def test_routing_approval_and_filled_receipts_rejected(self):
        d=build(fixture())
        for field,value in (("approved_for_publication",True),
                            ("second_review_required",False),("routing_decision","APPROVED")):
            form=blank_routing_form(d);form["cases"][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_routing_form(d,form)
        form=blank_routing_form(d);form["cases"][0]["human_evidence_receipts"]["wall_position_uncertainty_m"]=2
        with self.assertRaises(ValueError):validate_routing_form(d,form)
    def test_source_digest_binds_form(self):
        d=build(fixture());form=blank_routing_form(d)
        form["upstream_case_document_sha256"]="fake"
        with self.assertRaises(ValueError):validate_routing_form(d,form)
    def test_identical_input_produces_identical_desk(self):
        self.assertEqual(build(fixture()),build(copy.deepcopy(fixture())))

if __name__=="__main__":unittest.main()
