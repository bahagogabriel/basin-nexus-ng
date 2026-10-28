#!/usr/bin/env python3
"""Extra synthetic safety checks: public schema and redaction hard stops."""
import copy
import unittest
from evidence_publication_gate import SCHEMA_VERSION,validate

IDS={'SCMP-C01','SCMP-C02'}
BASE={'type':'PublicEvidenceCollection','schema_version':SCHEMA_VERSION,
      'publication_status':'APPROVED_PUBLIC_ONLY','records':[{
      'record_id':'BN-SYNTH-443','catchment_ids':['SCMP-C01'],
      'theme':'natural_resources','record_type':'resource_report',
      'statement':'This is an invented record used only in a security test.',
      'evidence_status':'stakeholder_reported',
      'source_reference':'Fictional public citation',
      'source_locator':'Invented section one',
      'release_authorization':'PUBLIC-SYNTH-CLEAR-01','location':None
      }]}

class HardenedSchemaTests(unittest.TestCase):
 def setUp(self):self.d=copy.deepcopy(BASE)
 def reject(self):
  with self.assertRaises(ValueError):validate(self.d,IDS)
 def test_valid_synthetic_schema(self):
  self.assertEqual(validate(self.d,IDS)['mapped_locations'],0)
 def test_extra_top_field(self):
  self.d['private_records']=[1];self.reject()
 def test_unsupported_version(self):
  self.d['schema_version']='UNKNOWN';self.reject()
 def test_duplicate_record_id(self):
  self.d['records'].append(copy.deepcopy(self.d['records'][0]));self.reject()
 def test_email_address(self):
  self.d['records'][0]['statement']='Contact fake.contact@example.org for fictional detail'
  self.reject()
 def test_google_private_docs_reference(self):
  self.d['records'][0]['source_reference']='https://docs.google.com/document/d/private-doc'
  self.reject()
 def test_private_source_keyword_in_text(self):
  self.d['records'][0]['statement']='Synthetic raw_statement_internal source leak test'
  self.reject()
 def test_unknown_record_field(self):
  self.d['records'][0]['private_note']='SYNTHETIC-NO-REAL-INFO';self.reject()
 def test_unverified_location(self):
  self.d['records'][0]['location']={
    'latitude':9,'longitude':8,'method':'invented map centroid',
    'verification':'candidate','uncertainty_m':30}
  self.reject()
 def test_empty_valid_catalogue(self):
  self.d['records']=[]
  self.assertEqual(validate(self.d,IDS)['validated_public_records'],0)
 def test_invalid_unknown_catchment(self):
  self.d['records'][0]['catchment_ids']=['SCMP-C99'];self.reject()

if __name__=='__main__':unittest.main()
