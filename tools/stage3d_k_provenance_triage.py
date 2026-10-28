#!/usr/bin/env python3
"""Stage 3D-K: source provenance triage, not factual verification or release.

Use with owner-controlled inputs outside public GitHub. CI uses synthetic sources.
A corroborating page can repeat a submitted table and is not automatically independent.
No precise asset positions or individual statement text should enter public repos.
"""
from __future__ import annotations
from collections import Counter
from datetime import date
import re

DIMENSIONS={
    "mineral_occurrence","mineral_reserve_or_grade","dam_capacity",
    "commissioning_date","construction_status","operational_status",
    "project_procurement","environmental_sampling","asset_position"
}
KINDS={
    "agency_primary_event","agency_technical_record","government_promotion",
    "government_project_tracker","government_procurement","academic_field_study",
    "technical_assessment","submitted_source","secondary_report"
}
SUPPORT={"SUPPORT","CONTRADICT","CONTEXT_ONLY","UNRELATED"}
SCOPE={"EXACT_DIMENSION","PARTIAL_DIMENSION","REGIONAL_CONTEXT","INTENT_ONLY"}
PRIVATE_MARKERS=("drive.google.com","docs.google.com","raw_statement_internal",
                 "private_drive_id","source_internal_id")


def _date(value):
    if not isinstance(value,str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}",value):
        raise ValueError("Every evidence observation requires an exact ISO date")
    try:
        d=date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Invalid observation date") from error
    if d>date.today():
        raise ValueError("Future-dated source")
    return d


def assess(candidate:dict, reference_date:str="2026-10-28")->dict:
    """Return aggregate-only decision flags; never source text or release authority.

    A human still must authenticate each source and determine the truth of its claims.
    """
    target=_date(reference_date)
    if not isinstance(candidate,dict) or set(candidate)!={
        "candidate_id","dimension","rights","publication_decision","position",
        "sources","claimed_metric_definition"
    }:
        raise ValueError("Unexpected or missing candidate keys")
    cid=candidate["candidate_id"]
    if not isinstance(cid,str) or not re.fullmatch(r"SYN-[A-Z0-9-]{3,40}",cid):
        raise ValueError("Generic CI ID only; real source IDs must remain private")
    dimension=candidate["dimension"]
    if dimension not in DIMENSIONS or candidate["rights"]!="NOT_CLEARED" or candidate["publication_decision"]!="HOLD":
        raise ValueError("Invalid candidate dimension or publication state")
    if candidate["position"] is not None:
        raise ValueError("No site coordinates in this provenance triage")
    sources=candidate["sources"]
    if not isinstance(sources,list) or len(sources)>60:
        raise ValueError("Expected bounded source record list")
    metric=candidate["claimed_metric_definition"]
    if metric is not None and (not isinstance(metric,str) or metric not in {
        "GROSS_STORAGE","LIVE_STORAGE","DESIGN_STORAGE","UNSPECIFIED_STORAGE",
        "RESERVE_TONNES","GRADE_PERCENT","EVENT_DATE"
    }):
        raise ValueError("Unrecognized measurement definition")
    if dimension=="dam_capacity" and metric is None:
        raise ValueError("Capacity comparison requires an explicit metric definition, even if unspecified")
    if dimension=="mineral_reserve_or_grade" and metric not in {"RESERVE_TONNES","GRADE_PERCENT"}:
        raise ValueError("Reserve/grade dimension must specify its unit class")

    independence={}
    role_count=Counter()
    flags=set()
    source_keys=set()
    for row in sources:
        allowed={"source_key","lineage_key","source_kind","support",
                 "scope","observation_date","metric_definition","independence_review"}
        if not isinstance(row,dict) or set(row)!=allowed:
            raise ValueError("Malformed source comparison")
        sk=row["source_key"];lineage=row["lineage_key"]
        if (not isinstance(sk,str) or not re.fullmatch(r"SRC-[A-Z0-9-]{3,40}",sk)
            or sk in source_keys or not isinstance(lineage,str)
            or not re.fullmatch(r"FAMILY-[A-Z0-9-]{3,40}",lineage)):
            raise ValueError("Invalid or repeated synthetic source reference")
        source_keys.add(sk)
        if row["source_kind"] not in KINDS or row["support"] not in SUPPORT or row["scope"] not in SCOPE:
            raise ValueError("Invalid source classification")
        if row["independence_review"] not in {"UNREVIEWED","INDEPENDENT",
                                               "SAME_ORIGIN","SUSPECTED_SHARED_ORIGIN"}:
            raise ValueError("Source dependence not reviewed")
        d=_date(row["observation_date"])
        if d>target:
            raise ValueError("Reference date precedes source observation")
        if row["metric_definition"] is not None and row["metric_definition"] not in {
            "GROSS_STORAGE","LIVE_STORAGE","DESIGN_STORAGE","UNSPECIFIED_STORAGE",
            "RESERVE_TONNES","GRADE_PERCENT","EVENT_DATE"
        }:
            raise ValueError("Unsupported observed measurement")
        lineage_values=independence.setdefault(lineage,[])
        lineage_values.append(row)
        role_count[row["support"]]+=1

        if row["support"]=="CONTRADICT":
            flags.add("SOURCE_DISAGREEMENT_REQUIRES_RECONCILIATION")
        if row["independence_review"] in {"UNREVIEWED","SUSPECTED_SHARED_ORIGIN"}:
            flags.add("SOURCE_INDEPENDENCE_UNESTABLISHED")
        if row["scope"]!="EXACT_DIMENSION" and row["support"]=="SUPPORT":
            flags.add("SOURCE_SCOPE_BELOW_CLAIM")
        if dimension in {"operational_status","construction_status"} and (target-d).days>365:
            flags.add("HISTORICAL_STATUS_ONLY")
        if dimension=="dam_capacity" and row["support"] in {"SUPPORT","CONTRADICT"}:
            if metric=="UNSPECIFIED_STORAGE" or row["metric_definition"]!=metric:
                flags.add("CAPACITY_DEFINITION_NOT_COMPARABLE")
        if dimension=="mineral_reserve_or_grade" and row["support"]=="SUPPORT":
            if row["source_kind"]=="government_promotion":
                flags.add("PROMOTIONAL_QUANTITY_IS_NOT_RESERVE_ESTIMATE")

    repeated=sum(len(group)-1 for group in independence.values())
    if repeated:
        flags.add("MULTIPLE_REFERENCES_SHARE_LINEAGE")
    if any(any(x["independence_review"]=="SAME_ORIGIN" for x in group)
           for group in independence.values()):
        flags.add("DERIVATIVE_SOURCE_NOT_INDEPENDENT_CONFIRMATION")
    eligible_groups=0
    for group in independence.values():
        independently_scoped=[
          x for x in group
          if x["support"]=="SUPPORT"
          and x["scope"]=="EXACT_DIMENSION"
          and x["independence_review"]=="INDEPENDENT"
          and (dimension not in {"operational_status","construction_status"}
               or (target-_date(x["observation_date"])).days<=365)
          and (dimension!="dam_capacity"
               or metric!="UNSPECIFIED_STORAGE" and x["metric_definition"]==metric)
          and x["source_kind"] not in {"government_promotion","secondary_report",
                                      "submitted_source","government_procurement"}
        ]
        if independently_scoped:
            eligible_groups+=1

    if "SOURCE_DISAGREEMENT_REQUIRES_RECONCILIATION" in flags:
        review="CONFLICT_HOLD"
    elif eligible_groups:
        review="INDEPENDENT_SPECIFIC_SOURCE_PRESENT_REVIEW_REQUIRED"
    elif sources:
        review="PARTIAL_OR_HISTORICAL_CONTEXT_ONLY"
    else:
        review="NO_EXTERNAL_EVIDENCE_LINKED"
    return {
        "status":review,
        "source_count":len(sources),
        "distinct_source_families":len(independence),
        "potentially_independent_specific_families":eligible_groups,
        "support_counts":dict(sorted(role_count.items())),
        "flags":sorted(flags),
        "publication_decision":"HOLD",
        "mapped_positions":0,
        "rights_cleared":0,
        "note":"Method-only triage: URL/source authenticity and scientific validity require external review."
    }
