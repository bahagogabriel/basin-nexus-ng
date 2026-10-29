#!/usr/bin/env python3
"""Stage 3D-AO: verify extracted offline review-kit SHA256 hashes.

Audit the *original distributed* desk, scripts and blank forms before moving
a copy of a blank form to a private directory. Never read submitted evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

SCHEMA="BN_STAGE3D_AO_PORTABLE_KIT_MANIFEST_V1"

def verify(root):
    root=Path(root)
    if not root.is_dir() or root.is_symlink():raise ValueError("Expected extracted kit directory")
    manifest=root/"FILE_MANIFEST.json"
    if manifest.is_symlink() or not manifest.is_file():raise ValueError("No authentic kit manifest")
    data=json.loads(manifest.read_text("utf-8"))
    if (not isinstance(data,dict) or set(data)!={"schema_version","files","scope"}
        or data["schema_version"]!=SCHEMA
        or data["scope"]!="BLANK_SOURCE_ONLY_OFFLINE_REVIEW_NOT_A_DAM_CONFIRMATION"
        or not isinstance(data["files"],dict) or len(data["files"])<15 or len(data["files"])>30):
        raise ValueError("Manifest structure changed")
    seen=set()
    for rel, digest in data["files"].items():
        if not isinstance(rel,str) or not rel or rel in seen:
            raise ValueError("Invalid or repeated manifest entry")
        seen.add(rel)
        p=Path(rel)
        if p.is_absolute() or ".." in p.parts or len(p.parts)>4 or "\\" in rel:
            raise ValueError("Unsafe manifest path")
        target=root/p
        if (not target.is_file() or target.is_symlink()
            or not target.resolve().is_relative_to(root.resolve())
            or not isinstance(digest,str) or len(digest)!=64):
            raise ValueError("Missing or unsafe original kit file")
        h=hashlib.sha256(target.read_bytes()).hexdigest()
        if h!=digest:raise ValueError("A kit source, request or blank form has changed")
    required={"SOURCE_DESK_UNVERIFIED.json","README_FIRST.md",
      "tools/stage3d_ai_ak_private_evidence_intake.py",
      "tools/stage3d_an_offline_batch_audit.py",
      "tools/stage3d_ao_verify_portable_kit.py",
      "tools/build_stage3d_ae_ah_review_desk.py",
      "tools/validate_confirmed_dam_sites.py"}
    if not required<=seen:raise ValueError("Missing required standalone offline components")
    for case in ("WA26-003","WA26-083","WA26-184","WA26-185","WA26-186"):
        for s in (f"blank_forms/{case}_BLANK.json",f"requests/REQUEST_{case}_NOT_SENT.md"):
            if s not in seen:raise ValueError("Incomplete case set")
    return {"checked_source_only_files":len(seen),"all_digests_match":True,
      "human_review_performed":False,"publication_authorized":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=Path(__file__).resolve().parents[1],type=Path)
    args=p.parse_args()
    report=verify(args.root)
    print("OFFLINE KIT INTEGRITY:",report["checked_source_only_files"],
          "original source-only files verified. Evidence verification/approval NOT performed.")

if __name__=="__main__":main()
