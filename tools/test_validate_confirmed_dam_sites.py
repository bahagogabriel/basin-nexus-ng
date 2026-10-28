#!/usr/bin/env python3
"""Synthetic-only source-policy checks: unverified vs confirmed, named or unnamed."""
import unittest
from validate_confirmed_dam_sites import validate_record,validate_collection
def record(**kw):
 r=dict(record_id="BN-DAM-SYNTHETIC-01",catchment_id="SCMP-C02",
  name=None,name_status="name_unavailable_after_review",
  existence_status="PHYSICAL_DAM_EXISTENCE_INDEPENDENTLY_REVIEWED",
  existence_evidence_kind="engineering_agency_as_built_or_inspection",
  existence_evidence_url="https://example.org/synthetic-dam-inspection",
  existence_observed_on="2025-08-20",
  position={"lon":8.333,"lat":9.111},
  position_method="surveyed_gnss_with_documented_accuracy",
  position_evidence_url="https://example.org/synthetic-dam-gnss",
  position_observed_on="2025-08-20",position_uncertainty_m=15,
  source_independence_review="SEPARATE_LINEAGES_CONFIRMED",
  editorial_reviewer="Synthetic reviewer",editorial_reviewed_on="2026-10-28",
  rights_status="EXPLICIT_PUBLIC_REUSE_CLEARED",
  publication_authorization="BN-PUBLIC-SYNTHETIC-001")
 r.update(kw)
 return r
class ConfirmedAdmissionTests(unittest.TestCase):
 def test_unnamed_can_pass_with_all_evidence_receipts(self):
  self.assertTrue(validate_record(record()))
 def test_named_can_pass_with_source_confirmation(self):
  self.assertTrue(validate_record(record(name="Fictional Valley Dam",name_status="established_name")))
 def test_guessing_name_not_allowed(self):
  with self.assertRaises(ValueError):validate_record(record(name="Maybe Dam"))
 def test_no_unsourced_facility(self):
  with self.assertRaises(ValueError):validate_record(record(existence_status="compiled_source_only"))
 def test_no_unreviewed_compilation(self):
  with self.assertRaises(ValueError):validate_record(record(source_independence_review="ONE_SOURCE_ONLY"))
 def test_bad_coordinate(self):
  with self.assertRaises(ValueError):validate_record(record(position={"lon":201,"lat":10}))
 def test_no_uncertainty(self):
  with self.assertRaises(ValueError):validate_record(record(position_uncertainty_m=0))
 def test_missing_rights(self):
  with self.assertRaises(ValueError):validate_record(record(rights_status="NOT_CLEARED"))
 def test_unapproved_publication(self):
  with self.assertRaises(ValueError):validate_record(record(publication_authorization=None))
 def test_private_google_link_forbidden(self):
  with self.assertRaises(ValueError):validate_record(record(position_evidence_url="https://docs.google.com/document/d/secret"))
 def test_missing_name_alone_not_a_blocker(self):
  x=record()
  self.assertIsNone(x["name"])
  self.assertTrue(validate_record(x))
 def test_entire_collection_remains_empty(self):
  d=dict(schema_version="BN_CONFIRMED_DAM_SITES_V1",
   status="INDEPENDENT_REVIEW_REQUIRED_ZERO_RECORDS",records=[],count=0,
   reviewed_on="2026-10-28",note="none yet")
  self.assertTrue(validate_collection(d))
  d["records"]=[record()]
  d["count"]=1
  with self.assertRaises(ValueError):validate_collection(d)
if __name__=="__main__":unittest.main()
