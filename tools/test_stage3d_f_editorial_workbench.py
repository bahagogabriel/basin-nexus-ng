#!/usr/bin/env python3
"""Synthetic-only tests for source-linked review packet generator."""
import copy
import unittest
from stage3d_f_editorial_workbench import build, render_text

def line(**changes):
    d = dict(
      internal_claim_id='SYN-L001',source_id='SYN-SRC-01',
      source_section='POLICIES',source_locator='Synthetic line 1',
      source_version='training-v1',catchment_ids=['SCMP-C02'],
      raw_statement_internal='Synthetic policy introduction includes:',
      state_reported=None,lga_reported=None,community_reported=None
    )
    d.update(changes)
    return d

def pilot(**changes):
    d=dict(
      internal_review_id='BN-PILOT-001',source_internal_id='SYN-SRC-01',
      principal_candidate_id='SYN-L001',source_section='POLICIES',
      source_locator='Synthetic line 1',catchment_id='SCMP-C02',
      catchment_name='Invented Study Catchment',theme='policies',
      engagement_period='Synthetic workshop',raw_statement_internal='Synthetic policy introduction includes:',
      publication_decision='HOLD',release_authorization='',
      source_rights='NOT_ASSESSED',privacy_status='REVIEW',location=None
    )
    d.update(changes)
    return d

def source():
    return [line(),line(internal_claim_id='SYN-L002',source_locator='Synthetic line 2',
                        raw_statement_internal='A fictional project statement, for tests only.'),
           line(internal_claim_id='SYN-L003',source_locator='Synthetic line 3',
                raw_statement_internal='Another fictional statement for the testing queue.')]

class PrivateEditorialWorkbenchTests(unittest.TestCase):
    def test_matches_and_context(self):
        result=build([pilot()],source())
        self.assertEqual(result['metadata']['queue_counts']['EXACT_SOURCE_PAIRS'],1)
        self.assertEqual(result['metadata']['queue_counts']['P1_CONTEXT_FRAGMENT'],1)
        self.assertEqual(result['metadata']['queue_counts']['HAS_TWO_FOLLOWING_SAME_SECTION_LINES'],1)
        self.assertEqual(len(result['review_packets'][0]['original_context']),3)
    def test_not_automatically_approved(self):
        r=build([pilot()],source())
        self.assertEqual(r['metadata']['public_records_authorized'],0)
        self.assertIsNone(r['review_packets'][0]['editorial_summary_draft'])
        self.assertIsNone(r['review_packets'][0]['independently_verified_location'])
        self.assertEqual(r['review_packets'][0]['publication_decision'],'HOLD')
    def test_numeric_quantity_flags_without_asserting_truth(self):
        a=source();a[0]['raw_statement_internal']='Invented reported dam volume: 12 million m3.'
        p=pilot(raw_statement_internal=a[0]['raw_statement_internal'])
        out=build([p],a)
        self.assertEqual(out['review_packets'][0]['priority'],'P2_NUMERIC_UNIT_CONTEXT')
    def test_duplicate_pilot_id_rejected(self):
        with self.assertRaises(ValueError):build([pilot(),pilot()],source())
    def test_missing_source_line_rejected(self):
        with self.assertRaises(ValueError):build([pilot(principal_candidate_id='MISSING')],source())
    def test_missing_catchment_link_rejected(self):
        with self.assertRaises(ValueError):build([pilot(catchment_id='SCMP-C19')],source())
    def test_exact_quote_required(self):
        with self.assertRaises(ValueError):build([pilot(raw_statement_internal='Rewritten without context')],source())
    def test_wrong_source_locator_rejected(self):
        with self.assertRaises(ValueError):build([pilot(source_locator='Wrong line')],source())
    def test_duplicate_source_ids_rejected(self):
        with self.assertRaises(ValueError):build([pilot()],source()+[line()])
    def test_unexpected_authorization_rejected(self):
        with self.assertRaises(ValueError):build([pilot(release_authorization='PUBLIC-FAKE-TEST')],source())
    def test_unverified_coordinate_rejected(self):
        with self.assertRaises(ValueError):build([pilot(location={'lat':9,'lon':8})],source())
    def test_cleared_rights_cannot_be_inferred(self):
        with self.assertRaises(ValueError):build([pilot(source_rights='CLEARED')],source())
    def test_source_text_never_in_metadata(self):
        result=build([pilot()],source())
        self.assertNotIn('Synthetic policy introduction',str(result['metadata']))
        self.assertIn('Synthetic policy introduction',render_text(result))
    def test_truncated_context_is_marked(self):
        result=build([pilot()],source()[:1])
        self.assertIn('INSUFFICIENT_ADJACENT_SOURCE_CONTEXT',result['review_packets'][0]['flags'])
    def test_summary_order_is_stable(self):
        first=build([pilot()],source())
        second=build([pilot()],source())
        self.assertEqual(render_text(first),render_text(second))

if __name__=='__main__':unittest.main()
