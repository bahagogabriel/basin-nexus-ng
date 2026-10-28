#!/usr/bin/env python3
"""Adversarial synthetic examples only. No live stakeholder data included."""
import json
import unittest
from stage3c_source_context_qa import parse_register, verify, is_fragment

def source(**updates):
    row = dict(internal_claim_id='SYN-001',source_id='SYN-SRC',source_section='POLICIES',
               source_locator='line 1',catchment_ids=['SCMP-C01'],
               raw_statement_internal='Fictional public-policy example for testing only, without actual events.')
    row.update(updates)
    return row

def pilot(**updates):
    row = dict(principal_candidate_id='SYN-001',source_internal_id='SYN-SRC',
               source_section='POLICIES',source_locator='line 1',catchment_id='SCMP-C01',
               raw_statement_internal='Fictional public-policy example for testing only, without actual events.',
               publication_decision='HOLD',release_authorization='')
    row.update(updates)
    return row

class SourceContextTests(unittest.TestCase):
    def test_matching_source(self):
        r=verify([pilot()],[source()])
        self.assertEqual(r['exact_source_text_matches'],1)
        self.assertEqual(r['public_records_authorized_by_this_tool'],0)
    def test_missing_source(self):
        r=verify([pilot(principal_candidate_id='SYN-NOTFOUND')],[source()])
        self.assertEqual(r['counts_by_review_flag']['unresolved_or_duplicate_source_candidate'],1)
    def test_source_wording_mismatch(self):
        r=verify([pilot(raw_statement_internal='Fabricated non-matching wording')],[source()])
        self.assertEqual(r['counts_by_review_flag']['source_wording_mismatch'],1)
    def test_section_and_anchor_mismatch(self):
        r=verify([pilot(source_section='OTHER',source_locator='wrong')],[source()])
        self.assertEqual(r['counts_by_review_flag']['source_section_mismatch'],1)
        self.assertEqual(r['counts_by_review_flag']['source_locator_mismatch'],1)
    def test_bad_catchment(self):
        self.assertEqual(verify([pilot(catchment_id='SCMP-C20')],[source()])['counts_by_review_flag']['catchment_link_mismatch'],1)
    def test_duplicate_source_keys(self):
        r=verify([pilot()],[source(),source()])
        self.assertEqual(r['counts_by_review_flag']['duplicate_source_line_keys'],1)
        self.assertEqual(r['counts_by_review_flag']['unresolved_or_duplicate_source_candidate'],1)
    def test_fragment_and_missing_context(self):
        a=source(raw_statement_internal='Relevant regulations include:')
        b=pilot(raw_statement_internal='Relevant regulations include:')
        x=verify([b],[a])
        self.assertEqual(x['counts_by_review_flag']['possible_fragment_or_list_heading'],1)
        self.assertEqual(x['counts_by_review_flag']['fragment_insufficient_adjacent_context'],1)
    def test_fragment_with_same_source_context(self):
        a=source(raw_statement_internal='Relevant regulations include:')
        b=pilot(raw_statement_internal='Relevant regulations include:')
        c=source(internal_claim_id='SYN-002',source_locator='line 2',raw_statement_internal='A fictional item from the invented list.')
        d=source(internal_claim_id='SYN-003',source_locator='line 3',raw_statement_internal='Another fictional item from the invented list.')
        x=verify([b],[a,c,d])
        self.assertEqual(x['counts_by_review_flag'].get('fragment_insufficient_adjacent_context',0),0)
    def test_hold_flags(self):
        x=verify([pilot(publication_decision='APPROVED',release_authorization='SYN-CODE')],[source()])
        self.assertEqual(x['counts_by_review_flag']['release_state_needs_manual_review'],1)
        self.assertEqual(x['public_records_authorized_by_this_tool'],0)
    def test_never_leak_private_text_or_identifiers(self):
        secret='SECRET-SYNTHETIC-CANDIDATE-CONTENT-123'
        x=verify([pilot(raw_statement_internal=secret)],[source(raw_statement_internal=secret)])
        dump=json.dumps(x)
        self.assertNotIn(secret,dump)
        self.assertNotIn('SYN-001',dump)
        self.assertNotIn('SYN-SRC',dump)
    def test_parser_extracts_register_lines_only(self):
        s='PRIVATE HEADER\n'+json.dumps(source(),separators=(',',':'))+'\n'
        self.assertEqual(parse_register(s),[source()])
    def test_parser_rejects_empty(self):
        with self.assertRaises(ValueError):parse_register('No records here')
    def test_fragment_detection(self):
        self.assertTrue(is_fragment('Some laws include:'))
        self.assertFalse(is_fragment('This imaginary sentence is an independent complete testing claim.'))

if __name__ == '__main__':
    unittest.main()
