#!/usr/bin/env python3
"""Synthetic-only regression: evidence breadth is not permission or site verification."""
import copy
import unittest
from stage3d_k_provenance_triage import assess

def example(dimension="commissioning_date", metric="EVENT_DATE"):
    return {
      "candidate_id":"SYN-CLAIM-101","dimension":dimension,"rights":"NOT_CLEARED",
      "publication_decision":"HOLD","position":None,
      "claimed_metric_definition":metric,"sources":[]
    }
def source(key="SRC-SYN-101",group="FAMILY-SYN-101",
           kind="agency_primary_event",scope="EXACT_DIMENSION",support="SUPPORT",
           on="2024-02-28",independence="INDEPENDENT",metric="EVENT_DATE"):
    return dict(source_key=key,lineage_key=group,source_kind=kind,
       support=support,scope=scope,observation_date=on,
       metric_definition=metric,independence_review=independence)

class TriageTests(unittest.TestCase):
    def test_empty_is_hold(self):
        x=assess(example())
        self.assertEqual(x["status"],"NO_EXTERNAL_EVIDENCE_LINKED")
        self.assertEqual(x["publication_decision"],"HOLD")
    def test_primary_event_has_specific_source_not_verified_claim(self):
        c=example();c["sources"]=[source()]
        x=assess(c)
        self.assertEqual(x["status"],"INDEPENDENT_SPECIFIC_SOURCE_PRESENT_REVIEW_REQUIRED")
        self.assertEqual(x["potentially_independent_specific_families"],1)
        self.assertEqual(x["rights_cleared"],0)
    def test_repeated_detailed_sheets_not_independent(self):
        c=example()
        c["sources"]=[
            source(key="SRC-SYN-101",independence="SAME_ORIGIN"),
            source(key="SRC-SYN-102",independence="SAME_ORIGIN")]
        x=assess(c)
        self.assertEqual(x["distinct_source_families"],1)
        self.assertEqual(x["potentially_independent_specific_families"],0)
        self.assertIn("MULTIPLE_REFERENCES_SHARE_LINEAGE",x["flags"])
    def test_repeated_independent_labels_count_one_family(self):
        c=example()
        c["sources"]=[source(key="SRC-SYN-101"),source(key="SRC-SYN-102")]
        self.assertEqual(assess(c)["potentially_independent_specific_families"],1)
    def test_promotional_reserve_does_not_verify_quantity(self):
        c=example("mineral_reserve_or_grade","RESERVE_TONNES")
        c["sources"]=[source(kind="government_promotion",metric="RESERVE_TONNES")]
        x=assess(c)
        self.assertEqual(x["potentially_independent_specific_families"],0)
        self.assertIn("PROMOTIONAL_QUANTITY_IS_NOT_RESERVE_ESTIMATE",x["flags"])
    def test_regional_geology_not_proof_of_specific_site(self):
        c=example("mineral_occurrence",None)
        c["sources"]=[source(kind="academic_field_study",scope="REGIONAL_CONTEXT",metric=None)]
        self.assertEqual(assess(c)["status"],"PARTIAL_OR_HISTORICAL_CONTEXT_ONLY")
    def test_incompatible_capacity_definitions(self):
        c=example("dam_capacity","DESIGN_STORAGE")
        c["sources"]=[source(kind="agency_technical_record",metric="LIVE_STORAGE")]
        x=assess(c)
        self.assertIn("CAPACITY_DEFINITION_NOT_COMPARABLE",x["flags"])
        self.assertEqual(x["potentially_independent_specific_families"],0)
    def test_unspecified_capacity_definition(self):
        c=example("dam_capacity","UNSPECIFIED_STORAGE")
        c["sources"]=[source(kind="agency_technical_record",metric="UNSPECIFIED_STORAGE")]
        self.assertEqual(assess(c)["potentially_independent_specific_families"],0)
    def test_incompatible_capacity_conflict_still_review(self):
        c=example("dam_capacity","DESIGN_STORAGE")
        c["sources"]=[source(kind="agency_technical_record",metric="LIVE_STORAGE",support="CONTRADICT")]
        self.assertEqual(assess(c)["status"],"CONFLICT_HOLD")
    def test_2019_rehabilitation_not_current_operation(self):
        c=example("operational_status",None)
        c["sources"]=[source(kind="government_procurement",scope="INTENT_ONLY",on="2019-04-01",metric=None)]
        x=assess(c)
        self.assertIn("HISTORICAL_STATUS_ONLY",x["flags"])
        self.assertEqual(x["potentially_independent_specific_families"],0)
    def test_2024_not_started_not_2026_status(self):
        c=example("construction_status",None)
        c["sources"]=[source(kind="government_project_tracker",on="2024-06-16",metric=None)]
        x=assess(c)
        self.assertIn("HISTORICAL_STATUS_ONLY",x["flags"])
        self.assertEqual(x["status"],"PARTIAL_OR_HISTORICAL_CONTEXT_ONLY")
    def test_more_recent_exact_status_can_support_timed_review(self):
        c=example("construction_status",None)
        c["sources"]=[source(kind="government_project_tracker",on="2026-06-16",metric=None)]
        self.assertEqual(assess(c)["potentially_independent_specific_families"],1)
    def test_unreviewed_source_independence_does_not_count(self):
        c=example();c["sources"]=[source(independence="UNREVIEWED")]
        x=assess(c)
        self.assertIn("SOURCE_INDEPENDENCE_UNESTABLISHED",x["flags"])
        self.assertEqual(x["potentially_independent_specific_families"],0)
    def test_suspected_shared_origin_not_counted(self):
        c=example();c["sources"]=[source(independence="SUSPECTED_SHARED_ORIGIN")]
        self.assertEqual(assess(c)["potentially_independent_specific_families"],0)
    def test_conflicting_exact_document(self):
        c=example();c["sources"]=[source(support="CONTRADICT")]
        self.assertEqual(assess(c)["status"],"CONFLICT_HOLD")
    def test_input_cannot_be_released(self):
        c=example();c["publication_decision"]="APPROVED"
        with self.assertRaises(ValueError):assess(c)
    def test_input_cannot_have_positions(self):
        c=example();c["position"]={"lat":8,"long":9}
        with self.assertRaises(ValueError):assess(c)
    def test_input_cannot_embed_private_review_fields(self):
        c=example();c["private_source_text"]="SYNTHETIC"
        with self.assertRaises(ValueError):assess(c)
    def test_future_2026_reference_not_allowed(self):
        c=example();c["sources"]=[source(on="2026-12-01")]
        with self.assertRaises(ValueError):assess(c)
    def test_nonexistent_date_rejected(self):
        c=example();c["sources"]=[source(on="2026-02-30")]
        with self.assertRaises(ValueError):assess(c)
    def test_out_of_scope_not_equated_to_asset_status(self):
        c=example("operational_status",None)
        c["sources"]=[source(kind="technical_assessment",scope="PARTIAL_DIMENSION",on="2026-09-01",metric=None)]
        x=assess(c)
        self.assertIn("SOURCE_SCOPE_BELOW_CLAIM",x["flags"])
        self.assertEqual(x["status"],"PARTIAL_OR_HISTORICAL_CONTEXT_ONLY")
    def test_no_plaintext_claim_leaves_function(self):
        c=example();c["sources"]=[source()]
        self.assertNotIn("source_key",str(assess(c)))
        self.assertNotIn("SYN-CLAIM-101",str(assess(c)))

if __name__=="__main__":
    unittest.main()
