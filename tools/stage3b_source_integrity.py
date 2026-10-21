#!/usr/bin/env python3
"""Source-family and numeric-conflict QA for PRIVATE Stage 3B manifests.

Pure functions use synthetic or caller-supplied private metadata. Do not put
actual stakeholder data into the public repository, tests or Actions artifacts.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import math
import re

RESTRICTED = {"signed_derivative_restricted", "signatures_restricted",
              "attendance_restricted", "temporary_exclude"}


def classify_source(filename: str, parent_collection: str = "") -> str:
    """Conservative, filename-only triage; never grants release rights."""
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("Source filename is required")
    f = re.sub(r"\s+", " ", filename.casefold()).strip()
    path = parent_collection.casefold() if isinstance(parent_collection, str) else ""
    if f.startswith("~") or f.endswith(".tmp") or f.endswith(".temp"):
        return "temporary_exclude"
    if "signatures" in path or "signature" in f:
        return "signatures_restricted"
    if "attendance" in path or "attendance" in f or "list of stakeholders" in f:
        return "attendance_restricted"
    if "signed" in f and ("stakeholder" in f or "communiqu" in f or
                          "shared vision" in f or "shared vison" in f):
        return "signed_derivative_restricted"
    if "archive" in path:
        return "archival_support"
    if "communiqu" in f:
        return "communique_candidate"
    if "shared vision" in f or "shared vison" in f:
        return "shared_vision"
    if "mineral" in f:
        return "thematic_mineral_submission"
    if "dam" in f or "weir" in f:
        return "thematic_dam_submission"
    return "thematic_or_supporting_input"


def review_manifest(entries: list[dict]) -> dict:
    """Counts only: no filename, source ID, Drive link or raw content returned."""
    if not isinstance(entries, list):
        raise ValueError("Expected private manifest list")
    kinds = Counter()
    mismatches = 0
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Expected manifest entry")
        kind = classify_source(entry.get("filename"), entry.get("parent_collection", ""))
        kinds[kind] += 1
        if "initial_category" in entry and entry["initial_category"] != kind:
            mismatches += 1
    return {
        "publication_status": "PRIVATE_INTERNAL_QA_ONLY",
        "sources": len(entries),
        "category_counts": dict(sorted(kinds.items())),
        "restricted_sources": sum(kinds[k] for k in RESTRICTED),
        "misclassified_source_entries": mismatches,
        "authorized_public_records": 0,
    }


def numeric_conflicts(observations: list[dict]) -> dict:
    """Never fuzzy-merge. Only explicit reviewer-assigned keys may be compared.

    Each observation must retain its own source_locator, quantity and original
    unit. Missing values are not zero; different units are not converted.
    """
    if not isinstance(observations, list):
        raise ValueError("Expected list of private numeric observations")
    grouped: dict[str, list] = defaultdict(list)
    missing = 0
    for obs in observations:
        if not isinstance(obs, dict):
            raise ValueError("Expected private observation object")
        key = obs.get("reviewed_asset_key")
        if not isinstance(key, str) or not key.strip():
            missing += 1
            continue
        if not obs.get("source_locator"):
            raise ValueError("Every compared observation needs a source locator")
        value = obs.get("quantity")
        unit = obs.get("unit")
        if value is not None and (isinstance(value, bool) or
                                  not isinstance(value, (int, float)) or
                                  not math.isfinite(value)):
            raise ValueError("Quantity must be finite numeric or null")
        grouped[key.strip()].append((value, unit))
    codes = Counter()
    comparable_groups = 0
    for values in grouped.values():
        if len(values) < 2:
            continue
        comparable_groups += 1
        units = {u for _, u in values if u is not None}
        nums = {v for v, _ in values if v is not None}
        if len(units) > 1:
            codes["UNIT_CONFLICT_REVIEW"] += 1
        if len(nums) > 1:
            codes["QUANTITY_CONFLICT_REVIEW"] += 1
        if any(v is None or u is None for v, u in values):
            codes["MISSING_VALUE_OR_UNIT"] += 1
    return {
        "publication_status": "PRIVATE_INTERNAL_QA_ONLY",
        "observations": len(observations),
        "ungrouped_missing_review_key": missing,
        "explicitly_comparable_groups": comparable_groups,
        "flag_counts": dict(sorted(codes.items())),
        "quantities_verified": 0,
    }
