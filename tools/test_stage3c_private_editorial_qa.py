#!/usr/bin/env python3
"""Synthetic-only Stage 3C adversarial QA; no real stakeholder content."""
import unittest
from stage3c_private_editorial_qa import audit, parse_pilot

def sample(**updates):
    x = dict(
        internal_review_id='BN-PILOT-001',
        principal_candidate_id='SYN-CANDIDATE-001',
        catchment_id='SCMP-C02', theme='natural_resources',
        source_internal_id='SYN-SOURCE-1', source_section='NATURAL RESOURCES',
        source_locator='Synthetic line 12', raw_statement_internal='Fictional testing statement with no real-world content.',
        engagement_period='2025', engagement_city='Lokoja', editorial_summary_candidate='',
        editorial_review='PENDING', independent_verification='NOT_PERFORMED',
        location=None, release_authorization='', publication_decision='HOLD',
        privacy_status='REVIEW', source_rights='NOT_ASSESSED'
    )
    x.update(updates)
    return x

class Stage3CReviewTests(unittest.TestCase):
    def test_default_requires_review_and_never_approves(self):
        x = audit([sample()])
        self.assertEqual(x['public_records_authorized_by_this_tool'],0)
        self.assertEqual(x['review_flags']['paraphrase_required'],1)
        self.assertEqual(x['review_flags']['source_rights_pending'],1)
    def test_approved_claim_still_not_authorized_by_tool(self):
        x = audit([sample(publication_decision='APPROVED',release_authorization='SYNTHETIC')])
        self.assertEqual(x['review_flags']['release_state_requires_manual_investigation'],1)
        self.assertEqual(x['public_records_authorized_by_this_tool'],0)
    def test_private_text_and_ids_never_enter_output(self):
        record = sample(raw_statement_internal='SECRET-SYNTHETIC-SENTINEL sentence for private QA.')
        result = str(audit([record]))
        self.assertNotIn('SECRET-SYNTHETIC-SENTINEL',result)
        self.assertNotIn('SYN-CANDIDATE-001',result)
        self.assertNotIn('BN-PILOT-001',result)
    def test_duplicate_ids_and_source_candidates_flagged(self):
        x = audit([sample(),sample()])
        self.assertEqual(x['review_flags']['invalid_or_duplicate_review_id'],1)
        self.assertEqual(x['review_flags']['duplicate_or_missing_source_candidate'],1)
    def test_context_fragments_flagged(self):
        x = audit([sample(raw_statement_internal='Specific examples include:')])
        self.assertEqual(x['review_flags']['context_or_fragment_review'],1)
    def test_missing_source_anchor_flagged(self):
        x = audit([sample(source_locator='')])
        self.assertEqual(x['review_flags']['missing_source_or_identity_anchor'],1)
    def test_invalid_catchment_and_theme(self):
        x = audit([sample(catchment_id='SCMP-C21',theme='speculation')])
        self.assertEqual(x['review_flags']['invalid_catchment_id'],1)
        self.assertEqual(x['review_flags']['unclassified_theme'],1)
    def test_coordinate_does_not_imply_release(self):
        x = audit([sample(location={'latitude':9,'longitude':8})])
        self.assertEqual(x['review_flags']['location_present_requires_independent_spatial_review'],1)
        self.assertEqual(x['public_records_authorized_by_this_tool'],0)
    def test_json_array_and_document_lines(self):
        import json
        source = sample()
        self.assertEqual(parse_pilot(json.dumps([source])),[source])
        self.assertEqual(parse_pilot('PRIVATE INTERNAL PILOT\n'+json.dumps(source)+'\n'),[source])
    def test_empty_document_rejected(self):
        with self.assertRaises(ValueError): parse_pilot('No records here')
    def test_invalid_record_types_rejected(self):
        with self.assertRaises(ValueError): audit(['not an object'])

if __name__=='__main__':
    unittest.main()
