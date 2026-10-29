#!/usr/bin/env python3
"""Stage 3D-AL: source-bound, PUBLIC-SOURCE-ONLY evidence request drafts.

Do not send emails or claim field checks. Produces blank request templates
and non-filled local-only evidence forms for a future accountable reviewer.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from build_stage3d_ae_ah_review_desk import IDS
from stage3d_ai_ak_private_evidence_intake import blank_record,validate_desk,sha

def build_requests(desk):
    cases=validate_desk(desk)
    refs=[]
    for ref in IDS:
        x=cases[ref]
        coords=x["original_compiled_WGS84_NOT_A_WALL"]
        if not isinstance(coords,list) or len(coords)!=2:
            raise ValueError("Original source reference position absent")
        references=f"{ref}; compiled-source research coordinate (longitude, latitude) {coords[0]:.6f}, {coords[1]:.6f} EPSG:4326 (NOT a surveyed dam-wall coordinate)"
        if ref=="WA26-003":
            topic="Gusau Barrage: as-built record, surveyed barrier and identity reconciliation"
            request=("Please provide a dated government/engineering source identifying the constructed Gusau Barrage, "
                     "an as-built drawing or inspection showing the physical barrier/crest, and a defensible "
                     "dam-wall location with its coordinate reference system, positional uncertainty, survey "
                     "method and survey date. Please identify whether the reported dam-inventory point "
                     "and the separately reported water-abstraction/intake coordinate refer to the barrier "
                     "or different infrastructure. Provide the record's originating organization and "
                     "permission for citation/public reuse, if permitted. Do not treat the water-intake "
                     "coordinate as a dam-wall survey.")
        elif ref=="WA26-083":
            topic="Gusau-area second reference: independent facility identity and location"
            request=("Please identify whether any separate constructed dam corresponds to this other compiled "
                     "research reference, with a date, engineering/as-built inspection, independently surveyed "
                     "barrier coordinates and uncertainty. Do not transfer the Gusau Barrage name, completion "
                     "status or location from a different reference without explicit documented linkage. "
                     "If the reference instead describes the same facility or a proposed/misplaced feature, "
                     "provide specific supporting records. State reproduction rights.")
        else:
            topic="Unnamed research reference: constructed barrier status and independent wall survey"
            request=("Please determine whether a completed physical dam barrier exists at or near this "
                     "UNVERIFIED compiled reference. Provide dated high-resolution field/engineering or "
                     "independently assessed Earth-observation evidence showing the actual wall, with "
                     "an as-built or GNSS dam-wall survey, coordinate CRS, observation date and uncertainty. "
                     "Record whether the barrier has an established official name; if unavailable, document "
                     "the authoritative sources searched. Note source lineage and permissions. OSM digitized "
                     "barriers and Sentinel-2 pixel-class labels alone are not sufficient.")
        body=("# Draft records request — "+topic+"\n\n"
          "**Status:** DRAFT FOR APPROPRIATE OFFICIAL/TECHNICAL RECIPIENT — NOT SENT.\n\n"
          "**Reference (research only):** "+references+"\n\n"
          "Dear Records or Engineering Officer,\n\n"+request+"\n\n"
          "Please provide the original document title, issuer, record date, direct source link or a "
          "legally shareable record, plus any applicable confidentiality limitations. We will not "
          "publish restricted stakeholder information or imply that this reference is verified "
          "before independent evidence assessment and editorial clearance.\n\n"
          "Thank you.\n\n"
          "**Data distinction:** Kouassi et al. (2026) compiled source, CC BY 4.0; OSM context "
          "ODbL where referenced. Neither source alone proves a constructed dam.\n")
        refs.append((ref,body))
    return refs

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--desk",type=Path,required=True)
    a.add_argument("--outdir",type=Path,required=True)
    args=a.parse_args()
    if args.outdir.exists():raise SystemExit("Refusing overwrite")
    desk=json.loads(args.desk.read_text("utf-8"))
    requests=build_requests(desk)
    args.outdir.mkdir(parents=True)
    for ref,body in requests:
        (args.outdir/f"REQUEST_{ref}_NOT_SENT.md").write_text(body,encoding="utf-8")
        (args.outdir/f"{ref}_BLANK_PRIVATE_INTAKE_TEMPLATE.json").write_text(
            json.dumps(blank_record(desk,ref),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    code_fence=chr(96)*3
    guide=("# Reviewer-only evidence request and intake kit\n\n"
      "Generated from Stage AE–AH review desk SHA256: "+sha(desk)+"\n\n"
      "**Everything here is a draft and every source reference is unverified. None of the requests was sent.**\n\n"
      "Review the five source-bound requests, choose appropriate records officers independently, "
      "and do not give them private stakeholder texts or files. The ready-to-fill JSON templates "
      "contain NO reviewed data. Make a secure private working directory OUTSIDE the public GitHub repo "
      "before entering any names, evidence files or rights information.\n\n"
      "Example (from the public repo root, after downloading this review kit):\n\n"
      +code_fence+"\n"
      "python tools/stage3d_ai_ak_private_evidence_intake.py --desk /path/to/STAGE3D_AE_AH_REVIEW_CASES_NOT_CONFIRMED.json "
      "--case WA26-003 --init --out /private/path/WA26-003.json\n"
      "python tools/stage3d_ai_ak_private_evidence_intake.py --desk /path/to/STAGE3D_AE_AH_REVIEW_CASES_NOT_CONFIRMED.json "
      "--case WA26-003 --review-input /private/path/WA26-003.json "
      "--out /private/path/WA26-003-redacted-completeness.json\n"
      +code_fence+"\n\n"
      "The offline CLI uses no network, writes new 0600-permission files, rejects any private output "
      "inside the public repo, and NEVER emits an approved dam or publication receipt. "
      "A status of documentation-complete means only that formal fields and declared source families "
      "are present. A separate, accountable independent reviewer must authenticate and interpret the "
      "real documents, resolve facility identity, verify wall coordinates and uncertainty, check source "
      "independence and clear specific publication rights before any later separate reviewed release PR.\n"
    )
    (args.outdir/"README_PRIVATE_OFFLINE_REVIEW_FIRST.md").write_text(guide,encoding="utf-8")
    print("Stage AL: five NOT SENT source request drafts + five BLANK review forms; zero confirmations")

if __name__=="__main__":main()
