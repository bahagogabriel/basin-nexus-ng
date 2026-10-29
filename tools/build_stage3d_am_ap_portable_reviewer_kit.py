#!/usr/bin/env python3
"""Stages 3D-AM/AP: reproducible, portable, source-only offline reviewer ZIP.

No filled evidence or confidential sources are read. All original records and
approval gates remain unchanged; produces NO confirmed facility or release.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from build_stage3d_ae_ah_review_desk import IDS,sha,validate_desk
from build_stage3d_al_evidence_request_kit import build_requests
from stage3d_ai_ak_private_evidence_intake import blank_record

SCHEMA="BN_STAGE3D_AO_PORTABLE_KIT_MANIFEST_V1"
SCRIPTS=(
 "stage3d_ai_ak_private_evidence_intake.py",
 "stage3d_an_offline_batch_audit.py",
 "stage3d_ao_verify_portable_kit.py",
 "build_stage3d_ae_ah_review_desk.py",
 "validate_confirmed_dam_sites.py")
ROOT="BasinNexusNG_OfflineReviewer_2026-10-29/"


def readme(desk):
    return """# Basin Nexus NG: standalone offline five-case facility evidence reviewer kit

**Important:** None of these compiled research references is an independently confirmed dam.
**No engineering evidence was received, no records requests were sent, and no public release was approved.**
This ZIP contains ONLY source-safe research context, blank private intake forms, unsent records-request drafts
and Python standard-library scripts. It contains no SCMP restricted records, field evidence or reviewer identities.

Original compiled dam-reference source: Kouassi et al. (2026), West Africa Dams and Reservoirs Dataset,
DOI https://doi.org/10.60507/FK2/YLDK1Y, CC BY 4.0. OSM observations are separately © OSM contributors, ODbL.
Original compiled-reference coordinates are unverified, not surveyed dam-wall locations.

## 1. Verify the extracted kit before use

Prerequisite: Python 3.11+ (no additional pip dependencies); runs offline on Windows, Linux or macOS.

  python tools/stage3d_ao_verify_portable_kit.py

Integrity verifies the original distributed files, **not source authenticity**, document contents or reviewer approval.
Do not edit original files in the kit. COPY a blank form into your separate secure working folder.

## 2. Create a new private folder OUTSIDE this extracted kit

For Windows, use an access-controlled folder such as C:\\Users\\<your-account>\\Documents\\BasinNexusPrivateEvidence .
For Linux/macOS, a private directory with user-only permissions is recommended.
Do not use a public repo, shared public cloud folder, issue comment, or this extracted kit directory.
Operating-system ACLs on Windows must be managed separately.

From the extracted kit root, initialize one blank private case:

  python tools/stage3d_ai_ak_private_evidence_intake.py --desk SOURCE_DESK_UNVERIFIED.json --case WA26-003 --init --out "C:\\path\\to\\PrivateEvidence\\WA26-003.json"

This creates a local PRIVATE record. A corresponding blank preview form exists under blank_forms/.

## 3. Review actual engineering or field evidence LOCALLY

Review source origin, actual physical dam-wall evidence, position method, uncertainty,
observed-on date, whether sources have genuine separate lineages, facility name and rights.
The presence of two self-declared source families cannot establish independence.
NEVER upload filled forms to GitHub Actions or put them in the public repository.

To produce a local REDACTED structural completeness report:

  python tools/stage3d_ai_ak_private_evidence_intake.py --desk SOURCE_DESK_UNVERIFIED.json --case WA26-003 --review-input "C:\\path\\to\\PrivateEvidence\\WA26-003.json" --out "C:\\path\\to\\PrivateEvidence\\WA26-003-status.json"

## 4. Audit all five cases together, without printing confidential contents

Any absent case remains NOT_SUBMITTED. Put case forms in a private folder using exact
case IDs as filenames (WA26-003.json, WA26-083.json, WA26-184.json, WA26-185.json, WA26-186.json).

  python tools/stage3d_an_offline_batch_audit.py --desk SOURCE_DESK_UNVERIFIED.json --private-dir "C:\\path\\to\\PrivateEvidence" --out "C:\\path\\to\\PrivateEvidence\\batch-status.json"

Reports contain ONLY research-reference IDs, count fields and generic missing-evidence codes.
They do not contain evidence locators, reviewer names, raw documentation or coordinates.
If forms are invalid, the tool reports only INVALID_PRIVATE_FORM, never exception details.

## Scientific and release boundary

Passing any local check means formal documentation may be *ready for second human review*.
It does **not** independently verify dam existence, official name, source independence,
wall positions or rights; it never creates a publication authorization.
The public confirmed-dam collection remains locked to zero until a separate accountable,
source-authenticated release review and authorized GitHub PR.

The first priority is WA26-003 (Gusau Barrage inventory lead), then WA26-184, WA26-185,
WA26-186 (source-unnamed barrier references), and finally WA26-083 (distinct repeated Gusau label).

Source review desk fingerprint SHA-256:
""" + sha(desk) + "\n"


def bundle(desk, scripts_root):
    validate_desk(desk)
    source_root=Path(scripts_root).resolve()
    files={}
    for name in SCRIPTS:
        p=source_root/name
        if p.is_symlink() or not p.is_file():raise ValueError("Required offline tool missing")
        files["tools/"+name]=p.read_bytes()
    files["SOURCE_DESK_UNVERIFIED.json"]=(json.dumps(desk,indent=2,
       ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8")
    files["README_FIRST.md"]=readme(desk).encode("utf-8")
    requests=dict(build_requests(desk))
    if set(requests)!=set(IDS):raise ValueError("Source-bound request identities drift")
    for ref in IDS:
        files[f"requests/REQUEST_{ref}_NOT_SENT.md"]=requests[ref].encode("utf-8")
        files[f"blank_forms/{ref}_BLANK.json"]=(json.dumps(
           blank_record(desk,ref),indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8")
    manifest={"schema_version":SCHEMA,"scope":"BLANK_SOURCE_ONLY_OFFLINE_REVIEW_NOT_A_DAM_CONFIRMATION",
      "files":{name:hashlib.sha256(data).hexdigest() for name,data in sorted(files.items())}}
    files["FILE_MANIFEST.json"]=(json.dumps(manifest,indent=2)+"\n").encode("utf-8")
    return files


def write_archive(desk, scripts_root, target):
    target=Path(target)
    if target.exists():raise ValueError("Refuse to overwrite a review kit")
    target.parent.mkdir(parents=True,exist_ok=True)
    files=bundle(desk,scripts_root)
    with ZipFile(target,"x",compression=ZIP_DEFLATED,compresslevel=7) as z:
        for path,data in sorted(files.items()):
            # Fixed, safely relative paths enable deterministic offline integrity auditing.
            info=ZipInfo(ROOT+path,date_time=(2026,10,29,7,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=0o644<<16
            z.writestr(info,data)
    with ZipFile(target) as z:
        if z.testzip() is not None:raise ValueError("ZIP CRC failed")
        if len(z.namelist())!=len(files):raise ValueError("Incomplete ZIP")
    return {"source_safe_files":len(files),"review_case_count":5,
        "blank_private_forms":5,"unsent_drafts":5,"confirmed_dams":0}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--desk",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    desk=json.loads(args.desk.read_text("utf-8"))
    result=write_archive(desk,Path(__file__).resolve().parent,args.output)
    print("Portable, offline, NO-CONFIRMATION reviewer kit:",result)

if __name__=="__main__":main()
