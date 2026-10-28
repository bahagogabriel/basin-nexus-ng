#!/usr/bin/env python3
"""PRIVATE Stage 3D-G reviewer queue from existing 3B flagged IDs.

Reads restricted source registers and a restricted heuristic flag list.
No original stakeholder material is uploaded, committed, published or logged by CI.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from stage3c_source_context_qa import parse_register
from stage3d_f_editorial_workbench import tidy

FLAG_CODES=frozenset({
    "QUANTITY_UNIT_REVIEW","SECURITY_OR_SENSITIVITY_REVIEW",
    "INTERVENTION_STATUS_CONTEXT","REPORTED_ADMIN_GEOGRAPHY_ONLY",
    "INFRASTRUCTURE_IDENTITY_STATUS","MINERAL_CLAIM_INDEPENDENT_CHECK"
})
ROW=re.compile(r"^(BN-3B-\d{3}-L\d{4})\s*\|\s*(SCMP-C(?:0[1-9]|1\d|20))"
               r"\s*\|\s*([^|]+)\s*\|\s*(HIGH|MEDIUM)\s*\|\s*(.+?)\s*$")


def parse_flags(text):
    result=[]
    ids=set()
    for line in text.strip().lstrip("\ufeff").splitlines():
        item=line.strip()
        if not item.startswith("BN-3B-"):
            continue
        m=ROW.fullmatch(item)
        if not m:
            raise ValueError("Malformed private triage row")
        uid,cid,city,priority,codes=m.groups()
        if uid in ids:
            raise ValueError("Duplicate source-line ID in triage queue")
        ids.add(uid)
        flags=[flag.strip() for flag in codes.split(";")]
        if not flags or len(flags)!=len(set(flags)) or not set(flags)<=FLAG_CODES:
            raise ValueError("Unknown or duplicated triage flags")
        result.append({"source_line_id":uid,"catchment_id":cid,
                       "engagement_batch":city.strip(),"priority":priority,"flags":flags})
    if not result:
        raise ValueError("No flagged source lines found")
    return result


def build_queue(flags,source_lines):
    if not isinstance(flags,list) or not isinstance(source_lines,list):
        raise ValueError("Expected private flag and source lists")
    index={}
    sequence={}
    for x in source_lines:
        if not isinstance(x,dict) or not isinstance(x.get("internal_claim_id"),str):
            raise ValueError("Malformed source record")
        uid=x["internal_claim_id"]
        if uid in index:
            raise ValueError("Duplicate source register key")
        index[uid]=x
        sequence.setdefault(x.get("source_id"),[]).append(x)
    records=[]
    counts=Counter()
    categories=Counter()
    cross=Counter()
    flagged_ids=set()
    for flag in flags:
        if not isinstance(flag,dict):
            raise ValueError("Malformed flagged row")
        uid=flag.get("source_line_id")
        if uid in flagged_ids:
            raise ValueError("Duplicate flagged source ID")
        flagged_ids.add(uid)
        if flag.get("priority") not in ("HIGH","MEDIUM"):
            raise ValueError("Unexpected review priority")
        if set(flag.get("flags",[])) - FLAG_CODES or not flag.get("flags"):
            raise ValueError("Unknown review flag")
        src=index.get(uid)
        if src is None or flag.get("catchment_id") not in (src.get("catchment_ids") or []):
            raise ValueError("Source and flag catchment identity mismatch")
        if src.get("coordinates") is not None or src.get("release_decision")!="HOLD" or src.get("release_authorization"):
            raise ValueError("Input is not a held, unmapped private source")
        arr=sequence[src.get("source_id")]
        i=next(i for i,record in enumerate(arr) if record["internal_claim_id"]==uid)
        previous=arr[i-1] if i>0 and arr[i-1].get("source_section")==src.get("source_section") else None
        following=arr[i+1] if i+1<len(arr) and arr[i+1].get("source_section")==src.get("source_section") else None
        context=[]
        if previous:
            context.append({"role":"PRECEDING","locator":previous.get("source_locator"),
                            "excerpt":tidy(previous.get("raw_statement_internal"))})
        context.append({"role":"SELECTED","locator":src.get("source_locator"),
                        "excerpt":tidy(src.get("raw_statement_internal"))})
        if following:
            context.append({"role":"FOLLOWING","locator":following.get("source_locator"),
                            "excerpt":tidy(following.get("raw_statement_internal"))})
        records.append({
            "priority":flag["priority"],"review_flags":list(flag["flags"]),
            "source_line_id":uid,"source_id":src.get("source_id"),
            "catchment_id":flag["catchment_id"],"source_section":src.get("source_section"),
            "source_locator":src.get("source_locator"),
            "source_version":src.get("source_version"),"reported_name":src.get("reported_name"),
            "reported_geography":{k:src.get(k) for k in
                ("state_reported","lga_reported","community_reported")},
            "original_context":context,
            "verified_original_anchor":None,
            "independent_quantity_check":None,
            "verified_action_status":None,
            "editorial_paraphrase":None,
            "source_rights":"NOT_CLEARED","privacy_review":"PENDING",
            "release_decision":"HOLD","public_authorization":None,
        })
        counts[flag["priority"]]+=1
        cross[flag["catchment_id"]]+=1
        categories.update(flag["flags"])
    records.sort(key=lambda r:(0 if r["priority"]=="HIGH" else 1,r["catchment_id"],r["source_line_id"]))
    return {
        "metadata":{
            "kind":"PRIVATE_STAGE3D_G_SOURCE_PRIORITY_QUEUE_NOT_RELEASE",
            "flagged_lines":len(records),
            "source_line_records":len(source_lines),
            "priority_counts":dict(sorted(counts.items())),
            "flag_counts":dict(sorted(categories.items())),
            "catchments_represented":len(cross),
            "publication_status":"HOLD",
            "public_records_authorized":0,
            "verified_asset_points":0,
        },
        "review_packets":records,
    }


def render_text(out):
    m=out["metadata"]
    lines=[
        "PRIVATE — BASIN NEXUS NG STAGE 3D-G PRIORITY SOURCE REVIEW QUEUE",
        "DO NOT PUBLISH: private text and source IDs for owner-only review.",
        f"Flagged lines: {m['flagged_lines']}; source lines: {m['source_line_records']}. "
        f"Priority totals: {m['priority_counts']}.",
        "These are heuristic flags on extracted text lines, not unique assets or verified facts.",
        "Full original document, paragraph/table, signed version and rights checks remain mandatory.",
        "",
    ]
    for rec in out["review_packets"]:
        lines.extend([
            "------------------------",
            f"{rec['priority']} | {rec['source_line_id']} | {rec['catchment_id']}",
            f"Source: {rec['source_id']} | {rec['source_section']} | {rec['source_locator']}",
            "Review flags: " + "; ".join(rec["review_flags"]),
        ])
        for part in rec["original_context"]:
            lines.append(f"{part['role']} ({part['locator']}): {part['excerpt']}")
        lines.extend([
            "VERIFY PRIMARY DOCUMENT/TABLE, ORIGINAL UNIT, ACTUAL PROJECT STATUS, "
            "INSTITUTIONAL RIGHTS AND PRIVACY.",
            "REVIEWED PARAPHRASE: [PENDING] | RELEASE: HOLD | LOCATION: NOT VERIFIED",
            "",
        ])
    return "\n".join(lines)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("private_risk_queue")
    parser.add_argument("--source-register",action="append",required=True)
    parser.add_argument("--out-private-json",required=True)
    parser.add_argument("--out-private-text",required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    inp=[Path(args.private_risk_queue).resolve()]+[Path(x).resolve() for x in args.source_register]
    out=[Path(args.out_private_json).resolve(),Path(args.out_private_text).resolve()]
    if any(x.is_relative_to(root) for x in inp+out):
        raise SystemExit("Restricted source and output paths must stay outside public repository")
    if len(set(inp+out))!=len(inp+out) or any(not x.is_file() for x in inp):
        raise SystemExit("Private source paths must exist and all paths must be different")
    if any(x.exists() or not x.parent.is_dir() for x in out):
        raise SystemExit("Output paths must be new in an existing owner-controlled folder")
    flags=parse_flags(inp[0].read_text(encoding="utf-8"))
    lines=[]
    for src in inp[1:]:
        lines.extend(parse_register(src.read_text(encoding="utf-8")))
    result=build_queue(flags,lines)
    with out[0].open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2,ensure_ascii=False)
        f.write("\n")
    with out[1].open("x",encoding="utf-8") as f:
        f.write(render_text(result))
    print("PRIVATE priority queue created:",result["metadata"]["flagged_lines"],
          "flagged source lines; public approvals: 0. No excerpts printed.")


if __name__=="__main__":
    main()
