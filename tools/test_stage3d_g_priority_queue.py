#!/usr/bin/env python3
"""Synthetic only: Stage 3D-G priority flags source identity and publication safety."""
import unittest
from stage3d_g_priority_queue import parse_flags,build_queue,render_text

def line(**overrides):
    d=dict(internal_claim_id='BN-3B-001-L0001',source_id='SRC-SYN-1',
           source_section='INTERVENTIONS',source_locator='test line 1',
           source_version='synthetic-v1',catchment_ids=['SCMP-C01'],
           raw_statement_internal='Fictional infrastructure report: no real scheme.',
           release_decision='HOLD',release_authorization=None,coordinates=None)
    d.update(overrides)
    return d

S='BN-3B-001-L0001 | SCMP-C01 | Invented City | HIGH | QUANTITY_UNIT_REVIEW;INTERVENTION_STATUS_CONTEXT'

class PriorityQueueTests(unittest.TestCase):
    def test_parse_heuristics(self):
        out=parse_flags('PRIVATE DOCUMENT\n'+S)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]['priority'],'HIGH')
        self.assertEqual(len(out[0]['flags']),2)
    def test_source_link(self):
        out=build_queue(parse_flags(S),[line()])
        self.assertEqual(out['metadata']['flagged_lines'],1)
        self.assertEqual(out['metadata']['priority_counts']['HIGH'],1)
        self.assertEqual(out['metadata']['public_records_authorized'],0)
        self.assertEqual(out['review_packets'][0]['release_decision'],'HOLD')
        self.assertEqual(len(out['review_packets'][0]['original_context']),1)
    def test_private_text_never_in_summary(self):
        out=build_queue(parse_flags(S),[line()])
        self.assertNotIn('Fictional infrastructure report',str(out['metadata']))
        self.assertIn('Fictional infrastructure report',render_text(out))
    def test_unknown_flag_fails(self):
        with self.assertRaises(ValueError):parse_flags(S.replace('QUANTITY_UNIT_REVIEW','MADE_UP'))
    def test_duplicate_flag_source_fails(self):
        with self.assertRaises(ValueError):parse_flags(S+'\n'+S)
    def test_duplicate_source_id_fails(self):
        with self.assertRaises(ValueError):build_queue(parse_flags(S),[line(),line()])
    def test_bad_catchment_link_fails(self):
        with self.assertRaises(ValueError):
            build_queue(parse_flags(S),[line(catchment_ids=['SCMP-C20'])])
    def test_unmapped_absent_candidate_fails(self):
        with self.assertRaises(ValueError):build_queue(parse_flags(S),[])
    def test_unverified_coordinates_fail(self):
        with self.assertRaises(ValueError):
            build_queue(parse_flags(S),[line(coordinates={'lat':9,'lon':8})])
    def test_release_status_change_fails(self):
        with self.assertRaises(ValueError):
            build_queue(parse_flags(S),[line(release_decision='APPROVED')])
    def test_one_neighbor_each(self):
        a=line(internal_claim_id='BN-3B-001-L0000',source_locator='test line 0')
        b=line()
        c=line(internal_claim_id='BN-3B-001-L0002',source_locator='test line 2')
        out=build_queue(parse_flags(S),[a,b,c])
        self.assertEqual([z['role'] for z in out['review_packets'][0]['original_context']],
                          ['PRECEDING','SELECTED','FOLLOWING'])
    def test_separator_variations(self):
        self.assertEqual(parse_flags(' \ufeff'+S.replace(' | ','|'))[0]['source_line_id'],
                         'BN-3B-001-L0001')

if __name__=='__main__':unittest.main()
