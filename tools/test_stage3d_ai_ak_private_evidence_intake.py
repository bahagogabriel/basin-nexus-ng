#!/usr/bin/env python3
"""Entirely fictional documents/reviewers. No live or real facility is confirmed."""
import copy, json, os, stat, tempfile, unittest
from pathlib import Path
from build_stage3d_ae_ah_review_desk import build
from test_stage3d_ae_ah_review_desk import fixture
from stage3d_ai_ak_private_evidence_intake import (
  SCHEMA, blank_record, check_record, sha, validate_desk,
  _private_destination, _write_private)

def desk():
    return build(fixture())

def completed():
    d=desk()
    x=blank_record(d,"WA26-003")
    x["documents"]=[
      {"source_id":"DOC-EXIST-01","source_family":"independent_engineering_agency",
       "evidence_kind":"engineering_agency_as_built_or_inspection",
       "evidence_locator":"/secure/reviewer-only/fictional-as-built.pdf",
       "observed_on":"2020-01-09","provenance_note":"Fictional distinct producing organization",
       "rights_state":"PRIVATE_REVIEW_ONLY"},
      {"source_id":"DOC-POS-02","source_family":"independent_field_survey",
       "evidence_kind":"surveyed_gnss_with_documented_accuracy",
       "evidence_locator":"/secure/reviewer-only/fictional-wall-gnss.pdf",
       "observed_on":"2020-01-10","provenance_note":"Fictional second source family",
       "rights_state":"PRIVATE_REVIEW_ONLY"}]
    x["name_review"]["status"]="NAME_UNAVAILABLE_AFTER_REVIEW"
    x["name_review"]["search_notes"]="Synthetic reviewer could not find a supported name"
    x["existence_review"]={"status":"DOCUMENTS_SUBMITTED_FOR_REVIEW",
      "existence_evidence_kind":"engineering_agency_as_built_or_inspection",
      "source_ids":["DOC-EXIST-01"],"observed_on":"2020-01-09"}
    x["position_review"]={"status":"POSITION_SUBMITTED_FOR_REVIEW",
      "lon":6.5,"lat":9.5,"method":"surveyed_gnss_with_documented_accuracy",
      "source_ids":["DOC-POS-02"],"uncertainty_m":3.5,"observed_on":"2020-01-10"}
    x["independence_review"]={"status":"FAMILY_INDEPENDENCE_ASSERTED_FOR_REVIEW",
      "lineage_notes":"Fictional source lineage: separate owner, methods, and producing agencies",
      "independent_source_families":["independent_engineering_agency","independent_field_survey"]}
    x["human_review"]={"status":"REQUEST_SECOND_INDEPENDENT_REVIEW",
      "reviewer_name":"Fictional Reviewer","reviewer_organization":"Fictional Bureau",
      "reviewed_on":"2026-10-20","rights_clearance":"REVIEWER_ASSERTS_CLEARED",
      "privacy_clearance":"REVIEWER_ASSERTS_CLEARED",
      "release_authorization":None}
    return d,x


class SecureIntakeTests(unittest.TestCase):
    def test_blank_binding_and_no_admission(self):
        d=desk();r=blank_record(d,"WA26-003")
        self.assertEqual(r["desk_sha256"],sha(d))
        self.assertEqual(r["schema_version"],SCHEMA)
        self.assertEqual(r["documents"],[])
        self.assertFalse(check_record(d,r)["public_layer_update_allowed"])
        self.assertGreater(len(check_record(d,r)["redacted_blocker_codes"]),4)
    def test_complete_synthetic_receipts_are_only_second_review_ready(self):
        d,r=completed()
        status=check_record(d,r)
        self.assertTrue(status["documentation_complete_for_second_human_review"])
        for key in ("independent_facility_existence_verified","wall_position_independently_verified",
                    "public_release_authorized","public_layer_update_allowed"):
            self.assertIs(status[key],False)
        self.assertNotIn("Fictional Reviewer",json.dumps(status))
        self.assertNotIn("/secure/reviewer-only/",json.dumps(status))
    def test_approval_and_release_authorization_are_banned(self):
        d,r=completed()
        r["human_review"]["status"]="APPROVED"
        with self.assertRaises(ValueError):check_record(d,r)
        d,r=completed();r["human_review"]["release_authorization"]="BN-PUBLIC-FAKE123"
        with self.assertRaises(ValueError):check_record(d,r)
    def test_fake_independence_or_one_family_blocks(self):
        d,r=completed()
        r["independence_review"]["independent_source_families"]=["independent_field_survey"]
        a=check_record(d,r)
        self.assertIn("NEED_DOCUMENTED_DISTINCT_LINEAGES",a["redacted_blocker_codes"])
        self.assertFalse(a["documentation_complete_for_second_human_review"])
    def test_forged_source_reference_rejected(self):
        d,r=completed()
        r["existence_review"]["source_ids"]=["DOC-NOT-SUBMITTED"]
        with self.assertRaises(ValueError):check_record(d,r)
    def test_position_uncertainty_and_dates_must_be_explicit(self):
        for bad in (0,False,5001,None):
            d,r=completed();r["position_review"]["uncertainty_m"]=bad
            with self.subTest(bad=bad):
                self.assertIn("NEED_DATED_MEASURED_WALL_POSITION_AND_UNCERTAINTY",
                  check_record(d,r)["redacted_blocker_codes"])
        d,r=completed();r["position_review"]["observed_on"]="2039-01-01"
        self.assertIn("NEED_DATED_MEASURED_WALL_POSITION_AND_UNCERTAINTY",
          check_record(d,r)["redacted_blocker_codes"])
    def test_source_desk_digest_change_rejected(self):
        d,r=completed()
        r["desk_sha256"]="0"*64
        with self.assertRaises(ValueError):check_record(d,r)
        d,r=completed();d["independently_confirmed_dams"]=1
        with self.assertRaises(ValueError):check_record(d,r)
    def test_unsafe_extra_private_fields_fail_closed(self):
        d,r=completed()
        r["private_stakeholder_notes"]="sensitive"
        with self.assertRaises(ValueError):check_record(d,r)
        d,r=completed();r["documents"][0]["participant_address"]="private"
        with self.assertRaises(ValueError):check_record(d,r)
    def test_outside_repository_write_is_private_and_exclusive(self):
        repo=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"review.json"
            d=desk();x=blank_record(d,"WA26-003")
            self.assertEqual(_private_destination(p,repo),p.resolve())
            _write_private(p,x)
            self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
            with self.assertRaises(FileExistsError):_write_private(p,x)
            self.assertEqual(json.loads(p.read_text()),x)
    def test_no_private_output_inside_repo(self):
        repo=Path(__file__).resolve().parents[1]
        with self.assertRaises(ValueError):
            _private_destination(repo/"review"/"must-not-write-private.json",repo)
    def test_different_cases_must_not_inherit_gusau_name(self):
        d=desk()
        x=blank_record(d,"WA26-184")
        self.assertEqual(x["name_review"]["status"],"UNRESOLVED")
        self.assertIsNone(x["name_review"]["supported_name"])
        self.assertEqual(x["documents"],[])

if __name__=="__main__":unittest.main()
