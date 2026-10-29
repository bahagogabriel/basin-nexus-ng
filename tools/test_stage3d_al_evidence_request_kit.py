#!/usr/bin/env python3
"""Entirely synthetic-only request copy and safe blank template tests."""
import copy, unittest
from build_stage3d_ae_ah_review_desk import build
from test_stage3d_ae_ah_review_desk import fixture
from build_stage3d_al_evidence_request_kit import build_requests
from stage3d_ai_ak_private_evidence_intake import blank_record

class RequestKitTests(unittest.TestCase):
    def test_exactly_five_unsent_drafts(self):
        requests=build_requests(build(fixture()))
        self.assertEqual(len(requests),5)
        for ref,text in requests:
            self.assertIn(ref,text)
            self.assertIn("NOT SENT",text)
            self.assertIn("NOT a surveyed dam-wall coordinate",text)
            self.assertNotIn("private stakeholder evidence:",text)
    def test_gusau_distinguishes_intake_and_barrage(self):
        requests=dict(build_requests(build(fixture())))
        self.assertIn("water-abstraction/intake",requests["WA26-003"])
        self.assertIn("dam-wall survey",requests["WA26-003"])
        self.assertNotIn("reported dam-inventory point",requests["WA26-083"])
    def test_unnamed_drafts_do_not_guess_identity(self):
        requests=dict(build_requests(build(fixture())))
        for ref in ("WA26-184","WA26-185","WA26-186"):
            self.assertIn("UNVERIFIED",requests[ref])
            self.assertNotIn("Gusau Barrage",requests[ref])
            self.assertIn("independently assessed",requests[ref])
    def test_source_digest_failure_blocks_request(self):
        d=build(fixture());d["independently_confirmed_dams"]=1
        with self.assertRaises(ValueError):build_requests(d)
    def test_all_blank_intake_records_remain_unreviewed(self):
        d=build(fixture())
        for ref,_ in build_requests(d):
            x=blank_record(d,ref)
            self.assertEqual(x["documents"],[])
            self.assertEqual(x["human_review"]["status"],"HOLD")
            self.assertIsNone(x["human_review"]["release_authorization"])

if __name__=="__main__":unittest.main()
