#!/usr/bin/env python3
"""Stage 3D-AN: offline private five-case batch completeness check.

Never copies evidence, reviewer names, coordinates, comments or locators to the
report. Never makes an HTTP request; does not approve facilities.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from build_stage3d_ae_ah_review_desk import IDS
from stage3d_ai_ak_private_evidence_intake import (
    _private_destination,_write_private,check_record,validate_desk,sha
)

SCHEMA="BN_STAGE3D_AN_REDACTED_FIVE_CASE_BATCH_V1"


def batch_audit(desk, private_dir):
    validate_desk(desk)
    private_dir=Path(private_dir)
    kit_root=Path(__file__).resolve().parents[1]
    if (not private_dir.is_dir() or private_dir.is_symlink()
        or private_dir.resolve().is_relative_to(kit_root)):
        raise ValueError("Private source folder must be an ordinary directory outside the public tool/kit")
    items=[]
    for ref in IDS:
        candidate=private_dir/(ref+".json")
        if candidate.is_symlink():
            # Do not follow links that could point to private unrelated records.
            state={"case_id":ref,"submission_state":"INVALID_PRIVATE_FORM",
                   "submitted_document_count":None,"declared_document_families_count":None,
                   "blocker_codes":["INVALID_PRIVATE_FORM"],"documentation_complete_for_second_review":False}
        elif not candidate.exists():
            state={"case_id":ref,"submission_state":"NOT_SUBMITTED",
                   "submitted_document_count":0,"declared_document_families_count":0,
                   "blocker_codes":["NO_PRIVATE_EVIDENCE_SUBMISSION"],"documentation_complete_for_second_review":False}
        else:
            try:
                if not candidate.is_file() or candidate.stat().st_size>800_000:
                    raise ValueError("Unbounded or invalid evidence form")
                with candidate.open("r",encoding="utf-8") as f:
                    record=json.load(f)
                if record.get("case_id")!=ref:
                    raise ValueError("Evidence reference changed")
                report=check_record(desk,record)
                state={"case_id":ref,"submission_state":"DECLARED_EVIDENCE_CHECKED_FOR_COMPLETENESS_ONLY",
                   "submitted_document_count":report["submitted_document_count"],
                   "declared_document_families_count":report["declared_document_families_count"],
                   "blocker_codes":report["redacted_blocker_codes"],
                   "documentation_complete_for_second_review":
                        report["documentation_complete_for_second_human_review"]}
            except (OSError,TypeError,ValueError,UnicodeError,KeyError,OverflowError,
                    json.JSONDecodeError):
                state={"case_id":ref,"submission_state":"INVALID_PRIVATE_FORM",
                   "submitted_document_count":None,"declared_document_families_count":None,
                   "blocker_codes":["INVALID_PRIVATE_FORM"],"documentation_complete_for_second_review":False}
        items.append(state)
    return {"schema_version":SCHEMA,
      "source_desk_sha256":sha(desk),
      "review_cases":len(items),
      "source_case_ids":list(IDS),
      "not_submitted_count":sum(c["submission_state"]=="NOT_SUBMITTED" for c in items),
      "invalid_form_count":sum(c["submission_state"]=="INVALID_PRIVATE_FORM" for c in items),
      "structurally_complete_second_review_candidates":sum(c["documentation_complete_for_second_review"] for c in items),
      "approval_is_technically_possible_from_this_tool":False,
      "independently_confirmed_dams":0,"public_map_updated":False,
      "data_leakage_controls":"No evidence paths, person names, notes, raw documents or coordinates in this report",
      "cases":items}


def main():
    p=argparse.ArgumentParser(description="Offline private five-case completeness audit; not an approval")
    p.add_argument("--desk",required=True,type=Path)
    p.add_argument("--private-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    kit=Path(__file__).resolve().parents[1]
    private=args.private_dir
    out=_private_destination(args.out,kit)
    if out.parent.resolve()!=private.resolve():
        raise SystemExit("Batch audit output must stay in the same PRIVATE directory as submitted forms")
    desk=json.loads(args.desk.read_text("utf-8"))
    report=batch_audit(desk,private)
    _write_private(out,report)
    print("Offline batch completeness:",report["review_cases"],"cases;",
        report["structurally_complete_second_review_candidates"],"formal submissions suitable for human inspection;",
        "0 independently confirmed dams; NO publication authorization.")

if __name__=="__main__":main()
