#!/usr/bin/env python3
"""Fictional-only source records; not actual facilities or field observations."""
import copy, unittest
from build_stage3d_u_evidence_workbench import build, BASE, FIELDS

def fake():
    z={"schema_version":"BN_WA_DAM_REFERENCE_TRIAGE_V1",
       "status":"REVIEW_ONLY_COMPILED_SOURCES_NO_CONFIRMED_DAMS",**BASE}
    z["review_queue"]=[]
    for i,(name,priority) in enumerate([(None,"P1_NEARBY_OR_REPEATED_NAME"),
                                           ("Fictional Source A","P3_NAMED_SOURCE")],1):
        z["review_queue"].append({
          "reference_id":f"WA26-{i:03}","catchment_id":"SCMP-C01",
          "source_name":name,"coordinates":[6+i*.001,9+i*.001],
          "priority":priority,"flags":["SOURCE_NAME_MISSING"] if name is None else [],
          "nearest_compiled_reference":None,"nearest_reference_distance_m_rounded":None,
          "display_eligibility":"EXISTING_OPT_IN_UNVERIFIED_REFERENCE",
          "independent_existence_verified":False,"position_verified":False,
          "facility_status":"not_assessed","review_outcome":"REQUIRES_INDEPENDENT_EVIDENCE"})
    return z

class StageUTests(unittest.TestCase):
    def test_only_priority_receipts_unverified(self):
        out=build(fake(),strict=False);self.assertEqual(len(out["records"]),1)
        self.assertEqual(out["reviewed_and_confirmed"],0)
        self.assertEqual(out["records"][0]["confirmation_status"],"HOLD_UNVERIFIED")
        self.assertFalse(out["records"][0]["eligible_for_public_confirmation"])
        self.assertTrue(all(out["records"][0][p] is None for p in FIELDS))
    def test_bogus_admissions_rejected(self):
        for key,value in [("independent_existence_verified",True),
                          ("position_verified",True),("facility_status","operational"),
                          ("review_outcome","CONFIRMED")]:
            v=fake();v["review_queue"][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):build(v,strict=False)
    def test_reject_private_field(self):
        v=fake();v["review_queue"][0]["private_stakeholder_id"]="NO"
        with self.assertRaises(ValueError):build(v,strict=False)
    def test_reject_duplicate_reference_ids(self):
        v=fake();v["review_queue"][1]["reference_id"]="WA26-001"
        with self.assertRaises(ValueError):build(v,strict=False)
    def test_source_md5_and_baseline_guard(self):
        with self.assertRaises(ValueError):build(fake(),strict=True)
        for key,value in [("source_csv_md5","fake"),
                          ("source_shapefile_md5","fake"),
                          ("public_source_preview_sha256","fake"),
                          ("confirmed_facility_count",1)]:
            v=fake();v[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):build(v,strict=False)
    def test_invalid_coordinate(self):
        v=fake();v["review_queue"][0]["coordinates"]=[30,0]
        with self.assertRaises(ValueError):build(v,strict=False)
    def test_no_withheld_without_quarantine(self):
        v=fake();v["review_queue"][0]["priority"]="P0_WITHHELD_IDENTITY"
        with self.assertRaises(ValueError):build(v,strict=False)

if __name__=="__main__":unittest.main()
