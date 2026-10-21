#!/usr/bin/env python3
"""Fictional records only: privacy, duplicate, status, rights and spatial regression tests."""
import unittest
from stage3b_private_qa import audit

def claim(**kwargs):
    record={'internal_claim_id':'SYN-001','source_id':'synthetic-source','source_locator':'table 1 row 1','raw_statement_internal':'Synthetic placeholder only','catchment_ids':['SCMP-C02'],'theme':'water_infrastructure','reported_status':'unknown','evidence_status':'stakeholder_reported','redistribution_rights':'NOT_CLEARED','release_decision':'HOLD','release_authorization':'','privacy_flag':'REVIEW','coordinates':None}
    record.update(kwargs)
    return record

class Stage3BPrivateQATest(unittest.TestCase):
    def test_no_public_records(self):
        result=audit([claim()])
        self.assertEqual(result['approved_for_publication'],0)
        self.assertEqual(result['readiness_counts']['no_verified_point'],1)
    def test_duplicates(self):
        result=audit([claim(),claim(source_locator='')])
        self.assertEqual(result['flag_counts']['MISSING_OR_DUPLICATE_INTERNAL_ID'],1)
        self.assertEqual(result['flag_counts']['PROVENANCE_INCOMPLETE'],1)
    def test_invalid_location(self):
        result=audit([claim(coordinates={'latitude':7,'longitude':8,'uncertainty_m':1,'verification':'stakeholder_reported'})])
        self.assertEqual(result['flag_counts']['COORDINATE_NOT_VERIFIED'],1)
    def test_boolean_latitude_rejected(self):
        result=audit([claim(coordinates={'latitude':True,'longitude':8,'uncertainty_m':1,'verification':'independently_validated'})])
        self.assertEqual(result['flag_counts']['COORDINATE_NOT_VERIFIED'],1)
    def test_reconciliation_conflict(self):
        a=claim(reconciliation_group='SYN-A',quantity=2,unit='m3')
        b=claim(internal_claim_id='SYN-002',reconciliation_group='SYN-A',quantity=3,unit='m3')
        self.assertEqual(audit([a,b])['groups_requiring_conflict_review'],1)
    def test_release_gate(self):
        self.assertEqual(audit([claim(release_decision='APPROVED')])['flag_counts']['MISSING_RELEASE_AUTHORIZATION'],1)
    def test_invalid_status(self):
        self.assertEqual(audit([claim(reported_status='operational_by_default')])['flag_counts']['STATUS_REVIEW'],1)
    def test_invalid_catchment(self):
        self.assertEqual(audit([claim(catchment_ids=['SCMP-C21'])])['flag_counts']['CATCHMENT_LINK_UNRESOLVED'],1)
    def test_private_content_not_in_report(self):
        self.assertNotIn('secret-synthetic-token',str(audit([claim(raw_statement_internal='secret-synthetic-token')])))

if __name__=='__main__': unittest.main()
