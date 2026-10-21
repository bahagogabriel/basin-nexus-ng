#!/usr/bin/env python3
"""Synthetic regression for future source-report evidence publishing rules."""
import copy
from evidence_publication_gate import validate
BASE={"type":"PublicEvidenceCollection","publication_status":"APPROVED_PUBLIC_ONLY",
      "records":[{"record_id":"BN-SYNTH-001","catchment_ids":["SCMP-C15"],
      "theme":"water_infrastructure","record_type":"facility_report",
      "statement":"Synthetic training example, not a real water facility.",
      "evidence_status":"stakeholder_reported",
      "source_reference":"Synthetic source for validator testing only",
      "source_locator":"Section 1, example paragraph 1",
      "release_authorization":"PUBLIC-SYNTH-TEST-01","location":None}]}
ids={"SCMP-C15","SCMP-C02"}
assert validate(BASE,ids)=={"validated_public_records":1,"mapped_locations":0}
def reject(change):
    c=copy.deepcopy(BASE);change(c["records"][0])
    try:
        validate(c,ids)
    except ValueError:
        return
    raise AssertionError("Public gate accepted an unapproved or unsafe record")
reject(lambda x:x.pop("release_authorization"))
reject(lambda x:x.update({"catchment_ids":["SCMP-C99"]}))
reject(lambda x:x.update({"private_drive_id":"restricted123"}))
reject(lambda x:x.update({"source_reference":"https://drive.google.com/file/d/private/view"}))
reject(lambda x:x.update({"location":{"latitude":9.4,"longitude":8.7,"verification":"candidate",
                                    "method":"Unverified centroid","uncertainty_m":1000}}))
reject(lambda x:x.update({"location":{"latitude":9.4,"longitude":8.7,
                      "verification":"independently_validated","method":"GPS site survey","uncertainty_m":float("nan")}}))
ok=copy.deepcopy(BASE);ok["records"][0]["location"]={"latitude":9.4,"longitude":8.7,
     "verification":"independently_validated","method":"Synthetic GPS site survey","uncertainty_m":30}
assert validate(ok,ids)=={"validated_public_records":1,"mapped_locations":1}
print("PUBLIC EVIDENCE SCHEMA GATE: PASS synthetic no-geometry, validated geometry, and blocked unsafe records")
