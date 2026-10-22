#!/usr/bin/env python3
"""Synthetic release-schema adversarial QA: event metadata is not stakeholder evidence."""
from pathlib import Path
from datetime import date
import copy
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "site/data/stakeholder_coverage_index.json"
SAFE_SOURCE_FIELDS = {
    "id","name","source_documents_located","source_section_keys","verification",
    "public_release","source_type","engagement_date_start","engagement_date_end",
    "engagement_period","engagement_city","evidence_status"
}
EVENT_CITIES={"Kano","Sokoto","Ilorin","Lokoja","Gombe"}

def validate_safe_source_index(d):
    if not isinstance(d, dict) or d.get("publication_status")!="PUBLIC_METADATA_ONLY":
        raise ValueError("Event source metadata must not become an approved evidence collection")
    if d.get("engagement_provenance_status")!="SOURCE_EVENT_METADATA_ONLY":
        raise ValueError("Not an engagement event index")
    if d.get("source_records_publicly_cleared") != 0:
        raise ValueError("Real clearance decision required before records")
    if d.get("source_contents_published") is not False or d.get("coordinates_or_observations_published") is not False:
        raise ValueError("Original stakeholder claims and coordinates are not authorized")
    entries=d.get("catchments")
    if not isinstance(entries, list) or len(entries)!=20:
        raise ValueError("Must cover 20 catchments")
    seen=set()
    for c in entries:
        if set(c)!=SAFE_SOURCE_FIELDS: raise ValueError("Sensitive or unknown public source fields")
        if c["id"] in seen or not re.fullmatch(r"SCMP-C(?:0[1-9]|1[0-9]|20)", c["id"]):
            raise ValueError("Unexpected or duplicate catchment ID")
        seen.add(c["id"])
        if c["source_documents_located"]!=1 or c["public_release"]!="Metadata only":
            raise ValueError("Source index is not clearance")
        if c["source_type"]!="SCMP institutional stakeholder engagement communiqué":
            raise ValueError("Source class must remain explicit")
        if c["evidence_status"]!="Source documented; individual claims withheld pending review":
            raise ValueError("Do not imply source statements have been individually validated")
        if c["engagement_city"] not in EVENT_CITIES: raise ValueError("Unexpected workshop host city")
        a=date.fromisoformat(c["engagement_date_start"])
        b=date.fromisoformat(c["engagement_date_end"])
        if a > b or not date(2024,1,1)<=a<=b<=date(2025,12,31):
            raise ValueError("Unexpected engagement date")
        if not c["engagement_period"] or len(c["engagement_period"])>45:
            raise ValueError("Date label missing or too long")
    blob=json.dumps(d,ensure_ascii=False).casefold()
    for forbidden in ("drive.google.com", "private_drive_id", "source_file_id",
                      "raw_statement_internal", "signature_file", "private_note",
                      "release_authorization", "source_quote_raw", "signed stakeholder engagement"):
        if forbidden in blob: raise ValueError("Private source marker in public index")
    return True

class SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(PATH.read_text(encoding="utf-8"))

    def test_real_public_index_stays_metadata_only(self):
        self.assertTrue(validate_safe_source_index(self.data))

    def test_confidential_field_rejected(self):
        x=copy.deepcopy(self.data)
        x["catchments"][0]["private_drive_id"]="fictional-secret"
        with self.assertRaises(ValueError): validate_safe_source_index(x)

    def test_unapproved_observations_rejected(self):
        x=copy.deepcopy(self.data)
        x["coordinates_or_observations_published"]=True
        with self.assertRaises(ValueError): validate_safe_source_index(x)

    def test_fake_clearance_rejected(self):
        x=copy.deepcopy(self.data)
        x["source_records_publicly_cleared"]=1
        with self.assertRaises(ValueError): validate_safe_source_index(x)

    def test_unvalidated_item_rejected(self):
        x=copy.deepcopy(self.data)
        x["catchments"][0]["evidence_status"]="independently_verified"
        with self.assertRaises(ValueError): validate_safe_source_index(x)

    def test_bad_date_rejected(self):
        x=copy.deepcopy(self.data)
        x["catchments"][0]["engagement_date_end"]="2024-01-01"
        with self.assertRaises(ValueError): validate_safe_source_index(x)

if __name__=="__main__":
    unittest.main()
