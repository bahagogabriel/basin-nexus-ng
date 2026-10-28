#!/usr/bin/env python3
"""PRIVATE 3D-F/G editorial workbench: source-grounded context packets; never grants release.

This tool only reads owner-supplied PRIVATE extracts located outside the public repo.
All generated excerpts and review IDs are PRIVATE. CI runs synthetic tests exclusively.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from stage3c_private_editorial_qa import parse_pilot
from stage3c_source_context_qa import parse_register, is_fragment

FRAGMENT_PRIORITY = "P1_CONTEXT_FRAGMENT"
NUMERIC_PRIORITY = "P2_NUMERIC_UNIT_CONTEXT"
STANDARD_PRIORITY = "P3_SOURCE_CONTEXT"
HOLD_STATE = {"publication_decision": "HOLD", "rights": "NOT_CLEARED",
              "privacy": "REVIEW", "spatial": "NOT_VERIFIED"}
NUMERIC = re.compile(
    r"(?:\b\d[\d,.]*\s*(?:km2|km²|ha|hectares?|metres?|meters?|"
    r"m3|m³|mw|kw|million|billion|tonnes?|litres?|liters?|percent|%)\b)", re.I)


def tidy(value):
    return " ".join(str(value or "").split())


def build(pilot, registers):
    """Return private review packets and an aggregate-only progress summary.

    Fail completely if any source pair, quote, section, locator or catchment link
    does not match. This avoids presenting mismatched text as source-supported.
    """
    if not isinstance(pilot, list) or not isinstance(registers, list):
        raise ValueError("Expected candidate and source lists")
    by_source = defaultdict(list)
    registered = set()
    for row in registers:
        if not isinstance(row, dict):
            raise ValueError("Invalid source record")
        key = (row.get("source_id"), row.get("internal_claim_id"))
        if not all(isinstance(v, str) and v for v in key) or key in registered:
            raise ValueError("Duplicate/missing source line identity")
        registered.add(key)
        by_source[key[0]].append(row)
    if not by_source:
        raise ValueError("Source-line register is empty")

    queue = []
    ids = set()
    counts = Counter()
    themes = Counter()
    catchments = Counter()
    for candidate in pilot:
        if not isinstance(candidate, dict):
            raise ValueError("Invalid editorial candidate")
        pid = candidate.get("internal_review_id")
        if not isinstance(pid, str) or not re.fullmatch(r"BN-PILOT-\d{3,}", pid) or pid in ids:
            raise ValueError("Duplicate or invalid editorial ID")
        ids.add(pid)
        src = candidate.get("source_internal_id")
        original_id = candidate.get("principal_candidate_id")
        seq = by_source.get(src, [])
        found = [(i, row) for i, row in enumerate(seq)
                 if row.get("internal_claim_id") == original_id]
        if len(found) != 1:
            raise ValueError("Missing or multiply matched source candidate")
        index, selected = found[0]
        if (tidy(selected.get("raw_statement_internal")) !=
            tidy(candidate.get("raw_statement_internal")) or
            selected.get("source_section") != candidate.get("source_section") or
            selected.get("source_locator") != candidate.get("source_locator") or
            candidate.get("catchment_id") not in (selected.get("catchment_ids") or [])):
            raise ValueError("Source line and editorial candidate differ")
        if (candidate.get("publication_decision") != "HOLD" or
            candidate.get("release_authorization") or
            candidate.get("source_rights") == "CLEARED" or
            candidate.get("privacy_status") == "CLEARED"):
            raise ValueError("Unexpected release/rights state: manual review required")
        if candidate.get("location") is not None:
            raise ValueError("This private workbench does not accept mapped positions")

        txt = tidy(selected["raw_statement_internal"])
        fragment = is_fragment(txt)
        has_numeric = bool(NUMERIC.search(txt))
        priority = (FRAGMENT_PRIORITY if fragment else
                    NUMERIC_PRIORITY if has_numeric else STANDARD_PRIORITY)
        before = seq[index-1] if index > 0 and seq[index-1].get("source_section")==selected["source_section"] else None
        next_two = [x for x in seq[index+1:index+3]
                    if x.get("source_section")==selected["source_section"]]
        context = [
            {"role": "PRECEDING", "source_locator": before["source_locator"],
             "original_excerpt": tidy(before["raw_statement_internal"])}
        ] if before else []
        context.append({"role": "SELECTED", "source_locator": selected["source_locator"],
                        "original_excerpt": txt})
        context.extend({"role": "FOLLOWING", "source_locator": x["source_locator"],
                        "original_excerpt": tidy(x["raw_statement_internal"])} for x in next_two)
        checks = ["CONFIRM_ORIGINAL_PAGE_PARAGRAPH_OR_TABLE",
                  "CONFIRM_CLAIM_BOUNDARIES_AND_REPORTED_STATUS",
                  "REVIEW_SOURCE_RIGHTS_AND_PRIVACY",
                  "DO_NOT_INFER_ASSET_COORDINATES"]
        if fragment:
            checks.append("RECONSTRUCT_LIST_OR_INCOMPLETE_CLAUSE_FROM_FULL_SOURCE")
        if has_numeric:
            checks.append("CHECK_ORIGINAL_NUMBER_UNIT_AND_DATE")
        if len(next_two)<2 and fragment:
            checks.append("INSUFFICIENT_ADJACENT_SOURCE_CONTEXT")
        item = {
            "internal_review_id": pid,
            "source_internal_id": src,
            "source_candidate_id": original_id,
            "catchment_id": candidate["catchment_id"],
            "catchment_name": candidate.get("catchment_name"),
            "theme": candidate.get("theme"),
            "engagement_period": candidate.get("engagement_period"),
            "source_section": selected["source_section"],
            "source_version": selected.get("source_version"),
            "source_locator": selected["source_locator"],
            "reported_geography": {
                "state": selected.get("state_reported"),
                "lga": selected.get("lga_reported"),
                "community": selected.get("community_reported"),
            },
            "priority": priority,
            "flags": checks,
            "original_context": context,
            "editorial_summary_draft": None,
            "original_page_or_table_anchor_verified": None,
            "project_state_verified": None,
            "numeric_version_conflicts_resolved": None,
            "source_rights": "NOT_ASSESSED",
            "privacy_status": "REVIEW",
            "publication_decision": "HOLD",
            "release_authorization": None,
            "independently_verified_location": None,
            "reviewer": None,
            "review_date": None,
        }
        queue.append(item)
        themes[item["theme"]] += 1
        catchments[item["catchment_id"]] += 1
        counts[priority] += 1
        counts["EXACT_SOURCE_PAIRS"] += 1
        counts["HAS_PRECEDING_SAME_SECTION_LINE"] += int(before is not None)
        counts["HAS_TWO_FOLLOWING_SAME_SECTION_LINES"] += int(len(next_two)==2)
    queue.sort(key=lambda i: (i["priority"], i["catchment_id"], i["internal_review_id"]))
    report = {
        "kind": "PRIVATE_3D_F_EDITORIAL_PACKETS_NOT_RELEASE_APPROVAL",
        "publication_status": "HOLD",
        "source_line_records": len(registers),
        "source_collections": len(by_source),
        "pilot_records": len(pilot),
        "catchments_represented": len(catchments),
        "theme_counts": dict(sorted(themes.items())),
        "queue_counts": dict(sorted(counts.items())),
        "source_rights_cleared": 0,
        "public_records_authorized": 0,
        "verified_asset_locations": 0,
    }
    return {"metadata": report, "review_packets": queue}


def render_text(result):
    report = result["metadata"]
    lines = [
        "PRIVATE — BASIN NEXUS NG STAGE 3D-F EDITORIAL REVIEW WORKBENCH",
        "DO NOT PUBLISH. All excerpts, source IDs and review notes remain owner-restricted.",
        "",
        f"Pilot records: {report['pilot_records']}; principal source lines: {report['source_line_records']}; "
        f"source collections: {report['source_collections']}. Exact source pairs: "
        f"{report['queue_counts'].get('EXACT_SOURCE_PAIRS', 0)}.",
        "Potential fragments are triage prompts, not source conclusions. "
        "Extracted neighboring lines are NOT verified complete original paragraphs/tables.",
        "ALL publication decisions: HOLD. All source rights: NOT_ASSESSED. "
        "No editorial summaries or authorizations are manufactured.",
        "",
    ]
    for item in result["review_packets"]:
        lines.extend([
            "------------------------",
            f"REVIEW {item['internal_review_id']} | {item['catchment_id']} | "
            f"{item['theme']} | {item['priority']}",
            f"Source: {item['source_internal_id']}, {item['source_candidate_id']}; "
            f"{item['source_section']} | {item['source_locator']}",
        ])
        for context in item["original_context"]:
            lines.append(f"{context['role']} ({context['source_locator']}): "
                         f"{context['original_excerpt']}")
        lines.extend([
            f"REQUIRED CHECKS: {', '.join(item['flags'])}",
            "FAITHFUL PRIVATE PARAPHRASE: [PENDING HUMAN EDITORIAL REVIEW]",
            "VERIFIED ORIGINAL PARAGRAPH/TABLE ANCHOR: [PENDING]",
            "STATUS, UNIT AND SOURCE-VERSION RECONCILIATION: [PENDING]",
            "SOURCE RIGHTS: NOT_ASSESSED | PRIVACY: REVIEW | RELEASE: HOLD",
            "",
        ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("private_pilot")
    parser.add_argument("--source-register", action="append", required=True)
    parser.add_argument("--out-private-json", required=True)
    parser.add_argument("--out-private-text", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = [Path(args.private_pilot).resolve()] + [
        Path(p).resolve() for p in args.source_register]
    output = [Path(args.out_private_json).resolve(), Path(args.out_private_text).resolve()]
    if any(p.is_relative_to(root) for p in sources + output):
        raise SystemExit("Private documents/outputs must stay outside the public repository")
    if len(set(sources + output)) != len(sources + output):
        raise SystemExit("Input and output paths must be distinct")
    if any(not p.is_file() for p in sources) or any(p.exists() or not p.parent.is_dir() for p in output):
        raise SystemExit("Private inputs must exist; outputs must be in existing private folders and must be new")
    pilot = parse_pilot(sources[0].read_text(encoding="utf-8"))
    lines = []
    for path in sources[1:]:
        lines.extend(parse_register(path.read_text(encoding="utf-8")))
    result = build(pilot, lines)
    with output[0].open("x", encoding="utf-8") as dest:
        json.dump(result, dest, ensure_ascii=False, indent=2)
        dest.write("\n")
    with output[1].open("x", encoding="utf-8") as dest:
        dest.write(render_text(result))
    print("PRIVATE review packets produced:",
          result["metadata"]["pilot_records"],
          "source matches. Public authorizations: 0. No source excerpts printed.")


if __name__ == "__main__":
    main()
