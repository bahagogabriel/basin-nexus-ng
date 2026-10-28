#!/usr/bin/env python3
"""Synthetic, adversarial publication-receipt tests (never real source material)."""
import copy
import json
import unittest
from stage3d_e_release_pipeline import digest,promote

def base():
    rec={
     'record_id':'BN-SYNTH-301','catchment_ids':['SCMP-C02'],
     'theme':'water_infrastructure','record_type':'facility_report',
     'statement':'Fictional example of an infrastructure claim; no actual facility.',
     'evidence_status':'stakeholder_reported','source_reference':'Invented public training source',
     'source_locator':'Synthetic section 2 item 1','release_authorization':'PUBLIC-SYNTH-TEST-01',
     'location':None
    }
    return {'type':'PublicEvidenceCollection','records':[rec]}, {
        'type':'EvidencePublicationReview','review_version':'1','records':[{
            'record_id':rec['record_id'],'record_sha256':digest(rec),
            'source_rights':'CLEARED','privacy':'CLEARED','editorial':'APPROVED',
            'reviewer':'Synthetic reviewer','decision_date':'2025-01-01',
            'release_authorization':rec['release_authorization'],'spatial_review':'NOT_APPLICABLE'
        }]}
class ReleasePipelineTests(unittest.TestCase):
    def setUp(self):
        self.c,self.m=base()
    def run_good(self):
        return promote(self.c,self.m,{'SCMP-C02'})
    def reject(self):
        with self.assertRaises(ValueError):self.run_good()
    def test_exact_review_passes_synthetic(self):
        released,counts=self.run_good()
        self.assertEqual(released['schema_version'],'BN_PUBLIC_EVIDENCE_V1')
        self.assertEqual(counts,{'validated_public_records':1,'mapped_locations':0})
    def test_modified_record_after_review_rejected(self):
        self.c['records'][0]['statement']+=' EXTRA'
        self.reject()
    def test_missing_rights_rejected(self):
        self.m['records'][0]['source_rights']='UNKNOWN'
        self.reject()
    def test_missing_privacy_rejected(self):
        self.m['records'][0]['privacy']='REVIEW'
        self.reject()
    def test_missing_editorial_rejected(self):
        self.m['records'][0]['editorial']='HOLD'
        self.reject()
    def test_missing_named_reviewer(self):
        self.m['records'][0]['reviewer']=''
        self.reject()
    def test_wrong_authorization_rejected(self):
        self.m['records'][0]['release_authorization']='PUBLIC-SYNTH-TEST-02'
        self.reject()
    def test_unknown_catchment_rejected(self):
        self.c['records'][0]['catchment_ids']=['SCMP-C99']
        self.m['records'][0]['record_sha256']=digest(self.c['records'][0])
        self.reject()
    def test_unreviewed_mapped_location_rejected(self):
        self.c['records'][0]['location']={'latitude':9.2,'longitude':8.5,'verification':'independently_validated',
              'method':'Fictional GPS survey','uncertainty_m':50}
        self.m['records'][0]['record_sha256']=digest(self.c['records'][0])
        self.reject()
    def test_spatially_reviewed_synthetic_location(self):
        self.c['records'][0]['location']={'latitude':9.2,'longitude':8.5,'verification':'independently_validated',
              'method':'Fictional GPS survey','uncertainty_m':50}
        self.m['records'][0]['record_sha256']=digest(self.c['records'][0])
        self.m['records'][0]['spatial_review']='APPROVED'
        self.assertEqual(self.run_good()[1]['mapped_locations'],1)
    def test_unapproved_private_field_rejected(self):
        self.c['records'][0]['private_drive_id']='INVENTED-NONPUBLIC'
        self.m['records'][0]['record_sha256']=digest(self.c['records'][0])
        self.reject()
    def test_duplicate_receipt_rejected(self):
        self.m['records'].append(copy.deepcopy(self.m['records'][0]))
        self.reject()
    def test_future_date_rejected(self):
        self.m['records'][0]['decision_date']='2099-01-01'
        self.reject()
    def test_empty_manifest_and_empty_catalogue(self):
        c={'type':'PublicEvidenceCollection','records':[]}
        m={'type':'EvidencePublicationReview','review_version':'1','records':[]}
        self.assertEqual(promote(c,m,{'SCMP-C02'})[1]['validated_public_records'],0)
    def test_email_exclusion(self):
        self.c['records'][0]['statement']='Synthetic email contact: example@example.com is a fiction.'
        self.m['records'][0]['record_sha256']=digest(self.c['records'][0])
        self.reject()

if __name__=='__main__':unittest.main()
